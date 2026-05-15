"""Unit tests for write_running_plan.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from openpyxl import load_workbook

SCRIPT = Path(__file__).parent.parent / "scripts" / "write_running_plan.py"


def _run(args: list[str], stdin_data: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin_data,
        capture_output=True,
        text=True,
    )


def _plan(start_row: int, weeks: list[dict]) -> str:
    return json.dumps({"start_row": start_row, "weeks": weeks})


def test_writes_weeks_to_empty_sheet(logbook: Path) -> None:
    payload = _plan(2, [
        {"week": 1, "day1": "5x800m @ 4:05/km", "day2": "6 km Easy", "day3": "16 km Easy"},
        {"week": 2, "day1": "6x800m @ 4:00/km", "day2": "7 km Strides", "day3": "20 km Easy"},
    ])
    result = _run(["--logbook", str(logbook)], payload)
    assert result.returncode == 0, result.stderr

    wb = load_workbook(logbook)
    ws = wb["Running - 2026"]
    assert ws.cell(row=2, column=1).value == 1
    assert ws.cell(row=2, column=2).value == "5x800m @ 4:05/km"
    assert ws.cell(row=2, column=3).value == "6 km Easy"
    assert ws.cell(row=2, column=4).value == "16 km Easy"
    assert ws.cell(row=3, column=1).value == 2
    assert ws.cell(row=3, column=4).value == "20 km Easy"


def test_refuses_to_overwrite_filled_week_without_force(
    logbook_with_running_plan: Path,
) -> None:
    payload = _plan(2, [
        {"week": 1, "day1": "new", "day2": "new", "day3": "new"},
    ])
    result = _run(["--logbook", str(logbook_with_running_plan)], payload)
    assert result.returncode != 0
    assert "would overwrite" in result.stderr.lower() or "force" in result.stderr.lower()

    wb = load_workbook(logbook_with_running_plan)
    ws = wb["Running - 2026"]
    assert ws.cell(row=2, column=2).value == "Old plan day 1"


def test_overwrites_with_force(logbook_with_running_plan: Path) -> None:
    payload = _plan(2, [
        {"week": 1, "day1": "new1", "day2": "new2", "day3": "new3"},
    ])
    result = _run(["--logbook", str(logbook_with_running_plan), "--force"], payload)
    assert result.returncode == 0, result.stderr

    wb = load_workbook(logbook_with_running_plan)
    ws = wb["Running - 2026"]
    assert ws.cell(row=2, column=2).value == "new1"


def test_appends_after_filled_weeks(logbook_with_running_plan: Path) -> None:
    payload = _plan(3, [
        {"week": 2, "day1": "wk2-d1", "day2": "wk2-d2", "day3": "wk2-d3"},
    ])
    result = _run(["--logbook", str(logbook_with_running_plan)], payload)
    assert result.returncode == 0, result.stderr

    wb = load_workbook(logbook_with_running_plan)
    ws = wb["Running - 2026"]
    assert ws.cell(row=2, column=2).value == "Old plan day 1"  # untouched
    assert ws.cell(row=3, column=1).value == 2
    assert ws.cell(row=3, column=2).value == "wk2-d1"


def test_invalid_json_exits_nonzero(logbook: Path) -> None:
    result = _run(["--logbook", str(logbook)], "{not json")
    assert result.returncode != 0


def test_missing_logbook_exits_nonzero(tmp_path: Path) -> None:
    bogus = tmp_path / "nope.xlsx"
    payload = _plan(2, [{"week": 1, "day1": "a", "day2": "b", "day3": "c"}])
    result = _run(["--logbook", str(bogus)], payload)
    assert result.returncode != 0
    assert "not found" in result.stderr.lower()
