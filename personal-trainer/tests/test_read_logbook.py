"""Unit tests for read_logbook.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "read_logbook.py"


def _run(args: list[str]) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_read_resistance_returns_template_rows(logbook: Path) -> None:
    out = _run(["--logbook", str(logbook), "--sheet", "resistance"])

    # Fixture fills only Week 1, so the next empty week is 2.
    assert out["next_empty_week"] == 2
    assert len(out["template"]) == 18  # 6 + 6 + 6 exercise rows

    first = out["template"][0]
    assert first == {
        "row": 3,
        "day": "Monday",
        "description": "Torso",
        "muscle_group": "Chest",
        "exercise": "Incline press",
    }

    legs_first = out["template"][12]
    assert legs_first["day"] == "Thursday"
    assert legs_first["muscle_group"] == "Quadriceps"
    assert legs_first["exercise"] == "Leg extension"


def test_read_resistance_skips_blank_separator_rows(logbook: Path) -> None:
    out = _run(["--logbook", str(logbook), "--sheet", "resistance"])
    rows = [r["row"] for r in out["template"]]
    assert 9 not in rows
    assert 16 not in rows


def test_read_running_empty_sheet(logbook: Path) -> None:
    out = _run(["--logbook", str(logbook), "--sheet", "running"])
    assert out["filled_weeks"] == []
    assert out["next_empty_row"] == 2


def test_read_running_with_existing_plan(logbook_with_running_plan: Path) -> None:
    out = _run(["--logbook", str(logbook_with_running_plan), "--sheet", "running"])
    assert len(out["filled_weeks"]) == 1
    assert out["filled_weeks"][0] == {
        "row": 2,
        "week": 1,
        "day1": "Old plan day 1",
        "day2": "Old plan day 2",
        "day3": "Old plan day 3",
        "status": None,
        "comment": None,
    }
    assert out["next_empty_row"] == 3


def test_read_missing_logbook_exits_nonzero(tmp_path: Path) -> None:
    bogus = tmp_path / "nope.xlsx"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--logbook", str(bogus), "--sheet", "resistance"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "not found" in result.stderr.lower()
