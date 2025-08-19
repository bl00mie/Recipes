#!/usr/bin/env python3
"""
normalize_serving_size.py
- Scans all .md files recursively from the repo root.
- Finds YAML frontmatter blocks and looks for a `serving_size:` field.
- Parses values like "1/4 cup", "1 1/2 tbsp", "2 tablespoons", "0.5 cup".
- Replaces the single `serving_size: ...` line with a numeric field whose key is
  `serving_size_<unit>` and value is a decimal (e.g. `serving_size_cup: 0.25`).
- Dry-run by default; use --apply to modify files.

Assumptions / notes:
- If the unit cannot be determined, uses `serving_size_unitless`.
- Preserves the rest of the frontmatter and body unchanged.
- Backups are not created; use dry-run first.
"""
import argparse
import re
from pathlib import Path
from typing import Optional, Tuple

UNIT_MAP = {
    'cups': 'cup', 'cup': 'cup', 'c': 'cup',
    'tablespoons': 'tbsp', 'tablespoon': 'tbsp', 'tbsp': 'tbsp', 'tbs': 'tbsp', 'tbsp.': 'tbsp',
    'teaspoons': 'tsp', 'teaspoon': 'tsp', 'tsp': 'tsp',
    'grams': 'g', 'gram': 'g', 'g': 'g', 'gr': 'g',
    'kilograms': 'kg', 'kg': 'kg',
    'ounces': 'oz', 'ounce': 'oz', 'oz': 'oz',
    'milliliters': 'ml', 'milliliter': 'ml', 'ml': 'ml', 'l': 'l', 'liters': 'l', 'liter': 'l',
    'piece': 'piece', 'pieces': 'piece', 'slice': 'slice', 'slices': 'slice',
    'serving': 'serving', 'servings': 'serving'
}

# frontmatter matcher: capture the leading '---\n', the body, and the trailing '---\n'
FIND_FRONT = re.compile(r'^(---\s*\n)(.*?)(---\s*\n)', re.DOTALL)
# capture serving_size line: prefix, optional quote, value, matching quote
SERVING_RE = re.compile(r'^(?P<prefix>\s*serving_size\s*:\s*)(?P<quote>["\']?)(?P<value>.+?)(?P=quote)\s*$', re.IGNORECASE | re.MULTILINE)

FRAC_RE = re.compile(r'(?:(?P<int>\d+)\s+)?(?P<num>\d+)\/(?P<den>\d+)')
DEC_RE = re.compile(r'(?P<dec>\d+(?:\.\d+)?)')


def parse_quantity_unit(s: str) -> Tuple[float, str]:
    """Return (quantity, unit_string) where unit_string may be 'unitless'."""
    original = s.strip()
    # remove parenthetical notes
    s = re.sub(r"\(.*?\)", "", original)
    s = s.replace(',', ' ').strip()
    # find fraction or decimal at start
    m = FRAC_RE.search(s)
    if m:
        whole = int(m.group('int')) if m.group('int') else 0
        num = int(m.group('num'))
        den = int(m.group('den'))
        value = whole + (num / den)
        after = s[m.end():].strip()
    else:
        m2 = DEC_RE.search(s)
        if m2:
            value = float(m2.group('dec'))
            after = s[m2.end():].strip()
        else:
            # maybe it's like 'cup' without numeric — assume 1
            value = 1.0
            after = s

    # unit detection: take first word of 'after'
    if not after:
        unit = 'unitless'
    else:
        # unit may be multiple words (e.g., 'tablespoons', 'tbsp')
        first = after.split()[0].lower().strip('.,')
        # normalize common forms
        unit = UNIT_MAP.get(first, first)

    return float(value), unit


def transform_frontmatter(front: str) -> Tuple[str, Optional[str]]:
    """Return (new_front, message) where new_front is modified frontmatter (or same)
    and message describes the change or None if nothing changed."""
    # Find serving_size line
    m = SERVING_RE.search(front)
    if not m:
        return front, None

    raw_value = m.group('value').strip()

    qty, unit = parse_quantity_unit(raw_value)

    # format numeric: use decimal with up to 4 decimals, but drop trailing zeros
    val_str = (f"{qty:.4f}").rstrip('0').rstrip('.')

    # if unitless, prefer the original `serving_size` key (no suffix)
    if unit == 'unitless':
        new_key = "serving_size"
    else:
        new_key = f"serving_size_{unit}"
    new_line = f"{new_key}: {val_str}\n"

    # replace the serving_size line with the new one
    new_front = SERVING_RE.sub(new_line, front, count=1)
    return new_front, f"serving_size -> {new_key}: {val_str} (was: {raw_value})"


def process_file(path: Path, apply: bool) -> Optional[str]:
    text = path.read_text(encoding='utf-8')
    m = FIND_FRONT.search(text)
    if not m:
        return None
    start, front_body, end = m.group(1), m.group(2), m.group(3)
    front = front_body
    new_front, msg = transform_frontmatter(front)
    if not msg:
        return None
    # rebuild file content
    new_text = start + new_front + end + text[m.end():]
    if apply:
        path.write_text(new_text, encoding='utf-8')
        return f"UPDATED: {path} -> {msg}"
    else:
        return f"WILL UPDATE: {path} -> {msg}"


def main(argv=None):
    p = argparse.ArgumentParser(description='Convert serving_size to numeric keyed field')
    p.add_argument('--apply', action='store_true', help='Apply changes')
    p.add_argument('--root', default='.', help='Root folder to scan')
    args = p.parse_args(argv)

    root = Path(args.root)
    md_files = sorted(root.rglob('*.md'))
    if not md_files:
        print('No markdown files found')
        return 0

    print(('APPLY' if args.apply else 'DRY RUN') + ' - scanning files...')
    for md in md_files:
        res = process_file(md, args.apply)
        if res:
            print(res)

    print('\nDone.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
