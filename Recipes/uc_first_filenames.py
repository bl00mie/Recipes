#!/usr/bin/env python3
"""
uc_first_filenames.py
- Dry-run by default. Use --apply to actually rename files.
- Renames all `*.md` files under Ingredients/ to UC-first per-word (e.g. "avocado.md" -> "Avocado.md").
- Handles case-only renames on Windows by using a temporary rename step.
- Avoids overwriting by appending " (1)", " (2)", ... on conflicts.
"""
import argparse
from pathlib import Path
import sys

ING_DIR = Path("Ingredients")


def uc_first_filename(name: str) -> str:
    # Preserve spaces; replace hyphens with spaces, capitalize each word
    return " ".join(w.capitalize() for w in name.replace('-', ' ').split())


def propose_new_name(path: Path) -> Path:
    stem = path.stem
    new_stem = uc_first_filename(stem)
    return path.with_name(new_stem + path.suffix)


def safe_rename(old: Path, new_path: Path, apply: bool) -> str:
    # If names identical -> skip
    if old.name == new_path.name:
        return f"skip (same): {old.name}"

    # If target doesn't exist, just rename (handle case-only on Windows)
    if not new_path.exists():
        if apply:
            # On Windows, renaming only case may be a no-op; handle with temp if needed
            try:
                old.rename(new_path)
                return f"renamed: {old.name} -> {new_path.name}"
            except OSError:
                # try temp rename then final
                temp = old.with_name(old.stem + ".ucstmp" + old.suffix)
                old.rename(temp)
                temp.rename(new_path)
                return f"renamed (via temp): {old.name} -> {new_path.name}"
        else:
            return f"would rename: {old.name} -> {new_path.name}"

    # If target exists
    try:
        # If they point to the same file (case-insensitive FS), attempt case-only rename
        if old.resolve() == new_path.resolve():
            if apply:
                # case-only change: rename via temp
                temp = old.with_name(old.stem + ".ucstmp" + old.suffix)
                old.rename(temp)
                temp.rename(new_path)
                return f"renamed (case-only via temp): {old.name} -> {new_path.name}"
            else:
                return f"would rename (case-only): {old.name} -> {new_path.name}"
    except Exception:
        # ignore resolve errors
        pass

    # Otherwise, conflict: find a safe non-existing name by appending (1), (2), ...
    base = new_path.stem
    suffix = new_path.suffix
    i = 1
    while True:
        candidate = new_path.with_name(f"{base} ({i}){suffix}")
        if not candidate.exists():
            if apply:
                old.rename(candidate)
                return f"renamed (conflict): {old.name} -> {candidate.name}"
            else:
                return f"would rename (conflict): {old.name} -> {candidate.name}"
        i += 1


def main(argv=None):
    p = argparse.ArgumentParser(description="UC-first ingredient filenames in Ingredients/")
    p.add_argument("--apply", action="store_true", help="Apply renames; default is dry-run")
    args = p.parse_args(argv)

    if not ING_DIR.exists() or not ING_DIR.is_dir():
        print(f"Ingredients directory not found at: {ING_DIR}")
        return 1

    md_files = sorted(ING_DIR.glob("*.md"))
    if not md_files:
        print("No .md files found in Ingredients/")
        return 0

    print(("APPLYING CHANGES" if args.apply else "DRY RUN (no changes)"))
    changes = []
    for md in md_files:
        new_path = propose_new_name(md)
        result = safe_rename(md, new_path, args.apply)
        print(result)
        changes.append(result)

    print("\nDone.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
