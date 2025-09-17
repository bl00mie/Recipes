#!/usr/bin/env python3
"""
normalize_vault_properties.py

Recursively walk an Obsidian vault, find markdown files with a YAML properties
block at the top (--- ... ---), and normalize the properties according to:
 - numeric property values become integers (rounded)
 - units belong in the property name (e.g., calories_kcal, carbohydrates_g)
 - tags are a YAML list ( - tag )
 - ensure net_carbohydrates_g exists (computed if possible)
 - create .bak backups before writing

Usage: python normalize_vault_properties.py /path/to/vault
"""

import os
import re
import sys
import shutil
import math
from typing import Any, Dict, Optional

try:
    import yaml
except ImportError:
    print("PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)

# Map base property names to their preferred unit suffix
UNIT_SUFFIXES = {
    "calories": "kcal",
    "protein": "g",
    "fat": "g",
    "saturated_fat": "g",
    "trans_fat": "g",
    "carbohydrates": "g",
    "fiber": "g",
    "total_sugars": "g",
    "added_sugars": "g",
    "sodium": "mg",
    "cholesterol": "mg",
    "potassium": "mg",
    "calcium": "mg",
    "iron": "mg",
    "vitamin_d": "mcg",
    "serving_size": "g",        # fallback if someone used serving_size with units
    "serving_size_g": "g",
    "servings": "",             # dimensionless
}

# A set of known suffixes so we can detect keys that already include units
KNOWN_SUFFIXES = set(UNIT_SUFFIXES.values()) | {"cup", "cups", "g", "mg", "mcg", "kcal"}

# Regex used to find a top YAML block
TOP_YAML_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

NUM_REGEX = re.compile(r"[-+]?\d*\.?\d+")

def parse_numeric(value: Any) -> Optional[float]:
    """Return first numeric value found in value (float). Return None if none."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        m = NUM_REGEX.search(value)
        if m:
            try:
                return float(m.group(0))
            except ValueError:
                return None
    return None

def key_has_known_unit_suffix(key: str) -> bool:
    """Return True if key already ends with a known unit suffix (e.g., '_g', '_mg', '_kcal', '_cup')."""
    # common annotation style: something_unit or something-units ; check parts
    # check after last underscore
    if "_" in key:
        suffix = key.split("_")[-1].lower()
        if suffix in KNOWN_SUFFIXES:
            return True
    # also accept keys that explicitly contain the unit string
    for s in KNOWN_SUFFIXES:
        if key.lower().endswith("_" + s):
            return True
    return False

def normalize_key_name(key: str) -> str:
    """
    If key matches one of the known base names (e.g., 'calories'), convert it to
    'calories_kcal'. If key already has a unit-like suffix, return as-is.
    Otherwise return the original key.
    """
    k = key.strip()
    if key_has_known_unit_suffix(k):
        return k
    # Exact-match keys that we want to append suffixes for
    base = k.lower()
    if base in UNIT_SUFFIXES and UNIT_SUFFIXES[base]:
        return f"{base}_{UNIT_SUFFIXES[base]}"
    # keep original for unknown keys (servings, title, notes, etc.)
    return k

def round_to_int(value: float) -> int:
    """Round float to nearest integer (ties away from zero via round())."""
    return int(round(value))

def fix_properties_block(block_text: str) -> str:
    """
    Parse YAML block text and return a normalized YAML block (string).
    If parsing fails, return the original block_text unchanged.
    """
    try:
        parsed = yaml.safe_load(block_text) or {}
    except Exception as e:
        print("YAML parse error (leaving block unchanged):", e)
        return block_text

    if not isinstance(parsed, dict):
        # Unexpected structure; don't attempt to change
        return block_text

    fixed: Dict[str, Any] = {}

    # Preserve insertion order as much as possible by iterating items()
    for raw_key, raw_val in parsed.items():
        key = str(raw_key).strip()

        # Normalize tags into a list
        if key.lower() == "tags":
            # If tags is a comma-separated string, split
            if raw_val is None:
                fixed["tags"] = []
            elif isinstance(raw_val, str):
                # allow both comma-separated or YAML-style newline lists; split by comma
                tags = [t.strip() for t in raw_val.split(",") if t.strip()]
                fixed["tags"] = tags
            elif isinstance(raw_val, (list, tuple)):
                fixed["tags"] = [str(t).strip() for t in raw_val if t is not None and str(t).strip()]
            else:
                # fallback
                fixed["tags"] = []
            continue

        # Try to parse numeric value
        numeric = parse_numeric(raw_val)
        if numeric is not None:
            # Round and store as integer
            int_val = round_to_int(numeric)
            # Determine output key name
            out_key = normalize_key_name(key)
            fixed[out_key] = int_val
        else:
            # Non-numeric: keep original key name (but still normalize unitless base names if they match)
            out_key = normalize_key_name(key)
            # If value is None, keep None (but callers should handle missing numeric values)
            fixed[out_key] = raw_val

    # Ensure net_carbohydrates_g exists (compute if possible)
    if "net_carbohydrates_g" not in fixed:
        carbs = fixed.get("carbohydrates_g")
        fiber = fixed.get("fiber_g")
        if isinstance(carbs, int) and isinstance(fiber, int):
            net = carbs - fiber
            if net < 0:
                net = 0
            fixed["net_carbohydrates_g"] = net
        else:
            # cannot compute; default to 0
            fixed["net_carbohydrates_g"] = 0

    # Ensure tags exists (even if empty)
    if "tags" not in fixed:
        fixed["tags"] = []

    # Dump YAML with stable key order (insertion order preserved)
    dumped = yaml.safe_dump(fixed, sort_keys=False, allow_unicode=True)
    # safe_dump returns a YAML document without the surrounding --- lines; return inner text
    return dumped.strip()

def process_file(path: str, make_backup: bool = True) -> None:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
    except Exception as e:
        print(f"Failed to read {path}: {e}")
        return

    m = TOP_YAML_RE.search(content)
    if not m:
        # no top YAML block
        return

    old_block = m.group(1)
    new_block = fix_properties_block(old_block)

    # If no change, skip
    # Normalize white-space differences for comparison
    if old_block.strip() == new_block.strip():
        return

    new_full = f"---\n{new_block}\n---\n"
    new_content = content[:m.start()] + new_full + content[m.end():]

    # backup file
    if make_backup:
        bak_path = path + ".bak"
        try:
            shutil.copy2(path, bak_path)
        except Exception as e:
            print(f"Warning: failed to create backup for {path}: {e}")

    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new_content)
        print("Fixed:", path)
    except Exception as e:
        print(f"Failed to write {path}: {e}")

def process_directory(root: str, make_backup: bool = True) -> None:
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if not fn.lower().endswith(".md"):
                continue
            full = os.path.join(dirpath, fn)
            process_file(full, make_backup=make_backup)

def main():
    if len(sys.argv) < 2:
        print("Usage: python normalize_vault_properties.py /path/to/obsidian/vault [--no-backup]")
        sys.exit(1)
    root = sys.argv[1]
    make_backup = True
    if len(sys.argv) > 2 and sys.argv[2] == "--no-backup":
        make_backup = False
    if not os.path.isdir(root):
        print("Provided path is not a directory:", root)
        sys.exit(1)
    process_directory(root, make_backup=make_backup)
    print("Done.")

if __name__ == "__main__":
    main()
