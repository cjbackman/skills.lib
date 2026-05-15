"""Shared pytest fixtures for personal-trainer script tests."""

from __future__ import annotations

import pytest
from openpyxl import Workbook
from pathlib import Path


def _build_logbook(path: Path) -> None:
    """Build a minimal logbook matching the real schema."""
    wb = Workbook()
    wb.remove(wb.active)

    # --- Resistance - 2026 ---
    rs = wb.create_sheet("Resistance - 2026")
    rs.cell(row=1, column=5, value="Week 1")
    rs.cell(row=1, column=7, value="Week 2")
    headers = ["Day", "Description", "Muscle Group", "Exercise",
               "Reps", "Weight", "Reps", "Weight"]
    for col, val in enumerate(headers, start=1):
        rs.cell(row=2, column=col, value=val)

    monday = [
        ("Monday", "Torso", "Chest", "Incline press", 12, 30, None, None),
        ("Monday", "Torso", "Chest", "Machine fly", 12, 80, None, None),
        ("Monday", "Torso", "Back", "Pulldown", 12, 75, None, None),
        ("Monday", "Torso", "Back", "Seated row", 12, 61, None, None),
        ("Monday", "Torso", "Shoulders", "Military press", 25, 20, None, None),
        ("Monday", "Torso", "Shoulders", "Reverse flys", 12, 72, None, None),
    ]
    for r_off, row in enumerate(monday):
        for c, val in enumerate(row, start=1):
            rs.cell(row=3 + r_off, column=c, value=val)

    wednesday = [
        ("Wednesday", "Arms, Neck & Core", "Biceps", "Cable curl", 22, 15, None, None),
        ("Wednesday", "Arms, Neck & Core", "Biceps", "Dumbbell curl", 20, 20, None, None),
        ("Wednesday", "Arms, Neck & Core", "Triceps", "Cable extension", 12, 35, None, None),
        ("Wednesday", "Arms, Neck & Core", "Triceps", "Close grip bench", 12, 45, None, None),
        ("Wednesday", "Arms, Neck & Core", "Core", "Core exercise", 40, 15, None, None),
        ("Wednesday", "Arms, Neck & Core", "Neck", "Neck exercises", 20, 20, None, None),
    ]
    for r_off, row in enumerate(wednesday):
        for c, val in enumerate(row, start=1):
            rs.cell(row=10 + r_off, column=c, value=val)

    thursday = [
        ("Thursday", "Legs", "Quadriceps", "Leg extension", 12, 60, None, None),
        ("Thursday", "Legs", "Quadriceps", "Leg press", 10, 270, None, None),
        ("Thursday", "Legs", "Hamstrings", "Leg curls", 12, 55, None, None),
        ("Thursday", "Legs", "Hamstrings", "Glute-ham raises", 12, 140, None, None),
        ("Thursday", "Legs", "Calves", "Standing calf raises", 35, 195, None, None),
        ("Thursday", "Legs", "Calves", "Tibialis raises", 40, 30, None, None),
    ]
    for r_off, row in enumerate(thursday):
        for c, val in enumerate(row, start=1):
            rs.cell(row=17 + r_off, column=c, value=val)

    # --- Running - 2026 ---
    rn = wb.create_sheet("Running - 2026")
    rn_headers = ["Week", "Day 1", "Day 2", "Day 3", "Status", "Comment"]
    for col, val in enumerate(rn_headers, start=1):
        rn.cell(row=1, column=col, value=val)
    # Leave Running sheet empty (no weeks filled) for the empty-sheet test path.

    wb.save(path)


@pytest.fixture
def logbook(tmp_path: Path) -> Path:
    """Return a path to a freshly built minimal logbook in tmp."""
    path = tmp_path / "Training Logbook.xlsx"
    _build_logbook(path)
    return path


@pytest.fixture
def logbook_with_running_plan(tmp_path: Path) -> Path:
    """Same as `logbook` but with Week 1 pre-filled in Running - 2026."""
    path = tmp_path / "Training Logbook.xlsx"
    _build_logbook(path)
    from openpyxl import load_workbook
    wb = load_workbook(path)
    rn = wb["Running - 2026"]
    rn.cell(row=2, column=1, value=1)
    rn.cell(row=2, column=2, value="Old plan day 1")
    rn.cell(row=2, column=3, value="Old plan day 2")
    rn.cell(row=2, column=4, value="Old plan day 3")
    wb.save(path)
    return path
