"""Unit tests for write_resistance_swap.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from openpyxl import load_workbook

SCRIPT = Path(__file__).parent.parent / "scripts" / "write_resistance_swap.py"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def test_overwrites_exercise_cell(logbook: Path) -> None:
    result = _run(["--logbook", str(logbook), "--row", "3", "--exercise", "Bench press"])
    assert result.returncode == 0, result.stderr

    wb = load_workbook(logbook)
    ws = wb["Resistance - 2026"]
    assert ws.cell(row=3, column=4).value == "Bench press"


def test_preserves_other_cells(logbook: Path) -> None:
    _run(["--logbook", str(logbook), "--row", "3", "--exercise", "Bench press"])

    wb = load_workbook(logbook)
    ws = wb["Resistance - 2026"]
    # Other rows unchanged
    assert ws.cell(row=4, column=4).value == "Machine fly"
    assert ws.cell(row=10, column=4).value == "Cable curl"
    # Row 3's reps/weight unchanged
    assert ws.cell(row=3, column=5).value == 12
    assert ws.cell(row=3, column=6).value == 30


def test_rejects_separator_row(logbook: Path) -> None:
    result = _run(["--logbook", str(logbook), "--row", "9", "--exercise", "Anything"])
    assert result.returncode != 0
    assert "separator" in result.stderr.lower() or "blank" in result.stderr.lower()


def test_rejects_header_row(logbook: Path) -> None:
    result = _run(["--logbook", str(logbook), "--row", "2", "--exercise", "Anything"])
    assert result.returncode != 0


def test_rejects_out_of_range_row(logbook: Path) -> None:
    result = _run(["--logbook", str(logbook), "--row", "999", "--exercise", "Anything"])
    assert result.returncode != 0


def test_missing_logbook_exits_nonzero(tmp_path: Path) -> None:
    bogus = tmp_path / "nope.xlsx"
    result = _run(["--logbook", str(bogus), "--row", "3", "--exercise", "X"])
    assert result.returncode != 0
    assert "not found" in result.stderr.lower()
