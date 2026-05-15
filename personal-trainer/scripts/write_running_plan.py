#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["openpyxl>=3.1"]
# ///
"""Write a generated running plan into the Running sheet."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from openpyxl import load_workbook

RUNNING_SHEET = "Running - 2026"


def main() -> int:
    parser = argparse.ArgumentParser(description="Write running plan to logbook")
    parser.add_argument("--logbook", required=True, type=Path)
    parser.add_argument("--force", action="store_true", help="Overwrite filled weeks")
    args = parser.parse_args()

    path = args.logbook.expanduser()
    if not path.exists():
        print(f"Logbook not found: {path}", file=sys.stderr)
        return 2

    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON on stdin: {exc}", file=sys.stderr)
        return 2

    start_row = payload.get("start_row")
    weeks = payload.get("weeks")
    if not isinstance(start_row, int) or not isinstance(weeks, list):
        print("Payload must include int 'start_row' and list 'weeks'.", file=sys.stderr)
        return 2

    try:
        wb = load_workbook(path)
    except PermissionError:
        print("Logbook open in Excel. Close and retry.", file=sys.stderr)
        return 3

    ws = wb[RUNNING_SHEET]

    if not args.force:
        for offset in range(len(weeks)):
            row = start_row + offset
            if any(ws.cell(row=row, column=c).value is not None for c in (1, 2, 3, 4)):
                print(
                    f"Row {row} is already filled. Pass --force to overwrite.",
                    file=sys.stderr,
                )
                return 4

    for offset, week_data in enumerate(weeks):
        row = start_row + offset
        ws.cell(row=row, column=1, value=week_data.get("week"))
        ws.cell(row=row, column=2, value=week_data.get("day1"))
        ws.cell(row=row, column=3, value=week_data.get("day2"))
        ws.cell(row=row, column=4, value=week_data.get("day3"))

    # Atomic write with temp-file cleanup on failure
    fd, tmp = tempfile.mkstemp(suffix=".xlsx", dir=str(path.parent))
    os.close(fd)
    tmp_path = Path(tmp)
    try:
        wb.save(tmp_path)
        os.replace(tmp_path, path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise

    print(f"Wrote {len(weeks)} weeks starting at row {start_row}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
