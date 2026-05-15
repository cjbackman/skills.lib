#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["openpyxl>=3.1"]
# ///
"""Swap an exercise in the resistance plan by overwriting column D at a given row."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from openpyxl import load_workbook

RESISTANCE_SHEET = "Resistance - 2026"
VALID_ROWS = frozenset(list(range(3, 9)) + list(range(10, 16)) + list(range(17, 23)))


def main() -> int:
    parser = argparse.ArgumentParser(description="Swap a resistance exercise")
    parser.add_argument("--logbook", required=True, type=Path)
    parser.add_argument("--row", required=True, type=int)
    parser.add_argument("--exercise", required=True, type=str)
    args = parser.parse_args()

    path = args.logbook.expanduser()
    if not path.exists():
        print(f"Logbook not found: {path}", file=sys.stderr)
        return 2

    if args.row not in VALID_ROWS:
        if args.row in {9, 16}:
            print(f"Row {args.row} is a blank separator. Pick an exercise row.", file=sys.stderr)
        else:
            print(f"Row {args.row} is not a valid exercise row. Valid rows: 3-8, 10-15, 17-22.", file=sys.stderr)
        return 2

    try:
        wb = load_workbook(path)
    except PermissionError:
        print("Logbook open in Excel. Close and retry.", file=sys.stderr)
        return 3

    ws = wb[RESISTANCE_SHEET]
    ws.cell(row=args.row, column=4, value=args.exercise)

    # Atomic write
    fd, tmp = tempfile.mkstemp(suffix=".xlsx", dir=str(path.parent))
    os.close(fd)
    tmp_path = Path(tmp)
    try:
        wb.save(tmp_path)
        os.replace(tmp_path, path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise

    print(f"Wrote '{args.exercise}' to row {args.row}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
