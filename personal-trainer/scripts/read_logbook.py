#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["openpyxl>=3.1"]
# ///
"""Read the training logbook and emit JSON on stdout."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

RESISTANCE_SHEET = "Resistance - 2026"
RUNNING_SHEET = "Running - 2026"
DATA_ROWS = list(range(3, 9)) + list(range(10, 16)) + list(range(17, 23))


def _read_resistance(workbook_path: Path) -> dict[str, Any]:
    wb = load_workbook(workbook_path, read_only=True, data_only=True)
    ws = wb[RESISTANCE_SHEET]

    template = []
    for row in DATA_ROWS:
        day = ws.cell(row=row, column=1).value
        if day is None:
            continue
        template.append({
            "row": row,
            "day": day,
            "description": ws.cell(row=row, column=2).value,
            "muscle_group": ws.cell(row=row, column=3).value,
            "exercise": ws.cell(row=row, column=4).value,
        })

    next_empty_week = 1
    week = 1
    while True:
        reps_col = 4 + (2 * week) - 1
        any_filled = False
        for r in DATA_ROWS:
            if ws.cell(row=r, column=reps_col).value is not None:
                any_filled = True
                break
        if not any_filled:
            next_empty_week = week
            break
        week += 1
        if week > 60:  # safety bound
            next_empty_week = week
            break

    wb.close()
    return {"template": template, "next_empty_week": next_empty_week}


def _read_running(workbook_path: Path) -> dict[str, Any]:
    wb = load_workbook(workbook_path, read_only=True, data_only=True)
    ws = wb[RUNNING_SHEET]

    filled = []
    next_empty_row = 2
    row = 2
    while True:
        week_num = ws.cell(row=row, column=1).value
        day1 = ws.cell(row=row, column=2).value
        if week_num is None and day1 is None:
            break
        filled.append({
            "row": row,
            "week": week_num,
            "day1": day1,
            "day2": ws.cell(row=row, column=3).value,
            "day3": ws.cell(row=row, column=4).value,
            "status": ws.cell(row=row, column=5).value,
            "comment": ws.cell(row=row, column=6).value,
        })
        row += 1
        if row > 200:
            break
    next_empty_row = row

    wb.close()
    return {"filled_weeks": filled, "next_empty_row": next_empty_row}


def main() -> int:
    parser = argparse.ArgumentParser(description="Read training logbook")
    parser.add_argument("--logbook", required=True, type=Path)
    parser.add_argument("--sheet", required=True, choices=["resistance", "running"])
    args = parser.parse_args()

    path = args.logbook.expanduser()
    if not path.exists():
        print(f"Logbook not found: {path}", file=sys.stderr)
        return 2

    if args.sheet == "resistance":
        result = _read_resistance(path)
    else:
        result = _read_running(path)

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
