# Personal-trainer Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `personal-trainer` skill — an interactive workflow with two sub-flows that update `~/Downloads/Training Logbook.xlsx`. The gym flow performs iterative exercise swaps respecting Huberman principles; the run flow generates a race-specific periodized running plan.

**Architecture:** Single skill at `personal-trainer/` in repo root, matching the convention of `coach/`, `flashcards/`, `weekly-polish/`. Short engine in `SKILL.md`; dense reference content (Huberman protocol, exercise library, running periodization, logbook schema) in `references/`; three small Python scripts in `scripts/` handle xlsx I/O via `openpyxl` (declared inline with `uv` script headers so users don't need to manage a virtualenv).

**Tech Stack:** Markdown skill files + Python 3.11 + `openpyxl` (pinned via `uv run --script` inline metadata). Verification = unit tests against generated xlsx fixtures + manual smoke test against the real logbook.

**Spec reference:** `docs/specs/2026-05-15-personal-trainer-design.md`

---

## File Structure

```
personal-trainer/
├── SKILL.md                              # engine: invocation, flows, edge cases
├── README.md                             # install, usage, file map
├── commands/
│   └── personal-trainer.md               # /personal-trainer slash command wrapper
├── references/
│   ├── huberman-protocol.md              # A/B alternation, big-six, principles
│   ├── exercise-library.md               # seeded from current sheet + Huberman big-six
│   ├── running-periodization.md          # phases, 80/20, pace zones, taper rules
│   └── logbook-schema.md                 # xlsx sheet/column layout, write rules
├── scripts/
│   ├── read_logbook.py                   # parse current state → JSON on stdout
│   ├── write_resistance_swap.py          # overwrite Exercise cell at given row
│   └── write_running_plan.py             # write generated plan to Running sheet
└── tests/
    ├── conftest.py                       # fixture factory for minimal logbook
    ├── test_read_logbook.py
    ├── test_write_resistance_swap.py
    └── test_write_running_plan.py
```

Each file has one responsibility. References are loaded only when relevant; scripts encapsulate all xlsx writes; tests rebuild fixtures from a single factory.

**Build order is bottom-up:** scaffold, then references, then test fixture factory, then each script TDD-style, then engine, then command/README, then real-logbook smoke test.

---

## Conventions used across all scripts

- **Inline dependency declaration** via `uv` so the scripts work without a project virtualenv:

  ```python
  #!/usr/bin/env -S uv run --script
  # /// script
  # requires-python = ">=3.11"
  # dependencies = ["openpyxl>=3.1"]
  # ///
  ```

- **I/O contract:** scripts read JSON input on stdin (when applicable) and write JSON output on stdout. Non-zero exit codes on error with a human-readable message on stderr.
- **Argparse** with explicit `--logbook` flag (default: `~/Downloads/Training Logbook.xlsx`, expanded).
- **No mutation without explicit args.** Each write script takes exact target coordinates from the caller.
- **Resistance row schema** (1-indexed, locked by Resistance - 2026 sheet inspection):
  - Row 1 = week header band (`Week 1` spans columns E:F, `Week 2` spans G:H, etc.)
  - Row 2 = sub-headers (`Day, Description, Muscle Group, Exercise, Reps, Weight, Reps, Weight, ...`)
  - Rows 3–8 = Monday/Torso (Chest, Back, Shoulders; 2 exercises each)
  - Row 9 = blank separator
  - Rows 10–15 = Wednesday/Arms, Neck & Core
  - Row 16 = blank separator
  - Rows 17–22 = Thursday/Legs
  - Column D = `Exercise` (this is the swap target — there is one Exercise cell shared across all weeks; per-week columns hold Reps and Weight only)
  - Week N reps column = column index `4 + (N * 2) - 1` (Week 1 = col E = 5). Week N weight column = `4 + (N * 2)` (Week 1 = col F = 6).
- **Running row schema** (Running - 2026):
  - Row 1 = headers (`Week, Day 1, Day 2, Day 3, Status, Comment`)
  - Row N+1 = Week N data
  - Column A = week number; B/C/D = day descriptions; E = status; F = comment

---

## Task 1: Scaffold skill directory

**Files:**
- Create: `personal-trainer/.gitignore`

This task creates the empty directory tree so subsequent tasks can drop files into the right place. The `.gitignore` keeps Python bytecode out of git.

- [ ] **Step 1: Create directory tree**

```bash
mkdir -p personal-trainer/{commands,references,scripts,tests}
```

- [ ] **Step 2: Create `personal-trainer/.gitignore` with the following content**

```
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 3: Commit**

```bash
git add personal-trainer/.gitignore
git commit -m "personal-trainer: scaffold skill directory"
```

---

## Task 2: `references/logbook-schema.md`

**Files:**
- Create: `personal-trainer/references/logbook-schema.md`

Reference doc the scripts and the engine both consult. Locks the cell layout so future edits stay consistent. Written so a fresh reader (or fresh Claude) can re-derive every script's coordinate math from this file alone.

- [ ] **Step 1: Create `personal-trainer/references/logbook-schema.md` with the following content**

````markdown
# Logbook schema

Path: `~/Downloads/Training Logbook.xlsx` (fixed, expanded at runtime).

Two sheets matter for v1: `Resistance - 2026` and `Running - 2026`. The skill never touches other sheets.

## `Resistance - 2026`

Layout (1-indexed):

| Row | Content |
|---|---|
| 1 | Merged week headers: `Week 1` (E:F), `Week 2` (G:H), … |
| 2 | Sub-headers: `Day, Description, Muscle Group, Exercise, Reps, Weight, Reps, Weight, …` |
| 3–8 | Monday — Torso block (Chest ×2, Back ×2, Shoulders ×2) |
| 9 | Blank separator |
| 10–15 | Wednesday — Arms, Neck & Core block (Biceps ×2, Triceps ×2, Core, Neck) |
| 16 | Blank separator |
| 17–22 | Thursday — Legs block (Quadriceps ×2, Hamstrings ×2, Calves ×2) |

Column map:

| Column | Letter | Purpose |
|---|---|---|
| 1 | A | Day (Monday / Wednesday / Thursday) |
| 2 | B | Description (Torso / Arms, Neck & Core / Legs) |
| 3 | C | Muscle Group |
| 4 | D | Exercise *(swap target)* |
| 5 | E | Week 1 Reps |
| 6 | F | Week 1 Weight |
| 7 | G | Week 2 Reps |
| 8 | H | Week 2 Weight |
| … | … | (Week N Reps = column `4 + 2*N - 1`; Week N Weight = `4 + 2*N`) |

**Important:** there is exactly one Exercise column. A swap is an in-place overwrite of column D at the target row. Previous weeks' Reps/Weight remain in their cells but are historically tied to the old name. The skill must surface this to the user when swapping mid-block.

"Next empty week" detection: scan row 3 (or any data row) starting at column E in steps of 2. The first column whose Reps cell is `None` in every data row is the next empty week column.

## `Running - 2026`

Layout (1-indexed):

| Row | Content |
|---|---|
| 1 | Headers: `Week, Day 1, Day 2, Day 3, Status, Comment` |
| 2 | Week 1 row |
| N+1 | Week N row |

Column map:

| Column | Letter | Purpose |
|---|---|---|
| 1 | A | Week number (int) |
| 2 | B | Day 1 description |
| 3 | C | Day 2 description |
| 4 | D | Day 3 description |
| 5 | E | Status |
| 6 | F | Comment |

"Sheet empty" = no rows past row 1 have any non-null Day 1/2/3. "Already has a plan" = at least one such row exists.

## Write rules

1. Always operate on a workbook opened with `openpyxl.load_workbook(keep_vba=False)`.
2. Save to a temp file alongside the original, then atomically replace. Never write in place — if the user has the file open in Excel, `save()` will fail partway and corrupt the workbook.
3. Preserve existing cell styles by writing only `.value`, never touching `.font`, `.fill`, etc.
4. If the workbook fails to open (PermissionError) → exit non-zero with message "Logbook open in Excel. Close and retry."
````

- [ ] **Step 2: Commit**

```bash
git add personal-trainer/references/logbook-schema.md
git commit -m "personal-trainer: document logbook schema"
```

---

## Task 3: `references/huberman-protocol.md`

**Files:**
- Create: `personal-trainer/references/huberman-protocol.md`

The principles the gym flow enforces when proposing swaps. Distilled from the Foundational Fitness Protocol article + PDF linked in the spec.

- [ ] **Step 1: Create `personal-trainer/references/huberman-protocol.md` with the following content**

````markdown
# Huberman foundational fitness protocol — principles

Sources:
- Article — <https://www.hubermanlab.com/newsletter/foundational-fitness-protocol>
- Protocol PDF — <https://cdn.prod.website-files.com/64416928859cbdd1716d79ce/650e450994ef9ab775e16acf_Neural_Network_Newsletter_Foundational_Fitness_Protocol.pdf>

Apply when proposing exercise swaps in the gym flow. These are the constraints a candidate must satisfy before it can be offered.

## Schedule A vs B (rep-range alternation)

| Schedule | Reps | Sets | Rest | Stimulus |
|---|---|---|---|---|
| A — Heavy | 4–8 | 3–4 | 2–4 min | Strength |
| B — Moderate | 8–15 | 2–3 | ~90 s | Hypertrophy |

A and B alternate week to week. Compound lifts work in both; isolation/machine work fits B better.

Tag every library exercise with `a_friendly`, `b_friendly`, or `both`.

## The big six

Prefer these for compound slots when applicable:

1. Squat (back/front/goblet)
2. Bench press
3. Deadlift (conventional/Romanian)
4. Military press / Overhead press
5. Chin-up / Pull-up
6. Hip thrust

When proposing a compound swap and a big-six exercise satisfies the muscle-group constraint, rank it first.

## Muscle group balance

A swap must preserve the muscle group of the row it replaces. Chest → chest, back → back, etc. Never cross groups (e.g. swap chest exercise for a back exercise) without an explicit user instruction to restructure the day.

## Compound before isolation

Within a day's exercise list, compounds should appear before isolations. When swapping, respect ordering: if the user swaps position 1 (typically a compound), don't propose an isolation as a replacement unless they explicitly accept the demotion.

## 2-exercises-per-muscle-group default

The current sheet uses 2 exercises per muscle group (e.g. Chest = Incline press + Machine fly). Swaps preserve this count. Do not propose collapsing or expanding the per-group count without user instruction.

## Day split

Current default is 3-day:
- Monday — Torso (Chest, Back, Shoulders)
- Wednesday — Arms, Neck & Core
- Thursday — Legs

Alternative 6-day split (listed in Metadata sheet, not currently active) splits torso and adds Norwegian 4×4 cardio on Tue/Fri. Detect 6-day if the user describes their week that way; otherwise stick to 3-day.

## Equipment tags

Tag exercises by equipment so swap candidates can be filtered when the user has constraints:

- `barbell`, `dumbbell`, `cable`, `machine`, `bodyweight`, `bar` (pull-up bar)

If the user says e.g. "no cable today," exclude `cable`-tagged candidates.
````

- [ ] **Step 2: Commit**

```bash
git add personal-trainer/references/huberman-protocol.md
git commit -m "personal-trainer: document Huberman principles"
```

---

## Task 4: `references/exercise-library.md`

**Files:**
- Create: `personal-trainer/references/exercise-library.md`

Seeded from the current `Resistance - 2026` sheet exercises, plus the Huberman big-six. Each entry tagged for muscle group, compound/isolation, equipment, A/B compatibility, and big-six membership.

- [ ] **Step 1: Create `personal-trainer/references/exercise-library.md` with the following content**

````markdown
# Exercise library

Seeded from `Resistance - 2026` + Huberman big-six. Format: one bullet per exercise, with tags.

Tag grammar: `[compound|isolation, equipment, a/b/both, big-six?]`

When proposing swap candidates: filter by muscle_group → equipment availability → compound/isolation parity → schedule compatibility → big-six bias (rank first).

The library is intentionally small. If a user requests an exercise not listed here, accept it verbatim and surface a follow-up suggestion: "Want me to add `<name>` to the library with these tags?"

---

## Chest

- Incline press — `[compound, barbell, both]`
- Bench press — `[compound, barbell, both, big-six]`
- Dumbbell bench press — `[compound, dumbbell, both]`
- Dumbbell incline press — `[compound, dumbbell, both]`
- Push-ups (weighted) — `[compound, bodyweight, b]`
- Machine fly — `[isolation, machine, b]`
- Cable crossover — `[isolation, cable, b]`
- Pec deck — `[isolation, machine, b]`

## Back

- Pulldown — `[compound, machine, both]`
- Chin-up / Pull-up — `[compound, bar, both, big-six]`
- Seated row — `[compound, machine, both]`
- Dumbbell row — `[compound, dumbbell, both]`
- Barbell row — `[compound, barbell, both]`
- T-bar row — `[compound, machine, both]`
- Face pull — `[isolation, cable, b]`

## Shoulders

- Military press / Overhead press — `[compound, barbell, both, big-six]`
- Dumbbell shoulder press — `[compound, dumbbell, both]`
- Arnold press — `[compound, dumbbell, b]`
- Lateral raise — `[isolation, dumbbell, b]`
- Reverse fly / Rear delt fly — `[isolation, dumbbell, b]`
- Cable lateral raise — `[isolation, cable, b]`

## Biceps

- Cable curl — `[isolation, cable, b]`
- Dumbbell curl — `[isolation, dumbbell, b]`
- Hammer curl — `[isolation, dumbbell, b]`
- Incline dumbbell curl — `[isolation, dumbbell, b]`
- Preacher curl — `[isolation, machine, b]`
- Barbell curl — `[isolation, barbell, b]`

## Triceps

- Cable overhead extension — `[isolation, cable, b]`
- Lying tricep extension — `[isolation, barbell, b]`
- Close-grip bench press — `[compound, barbell, both]`
- Dips — `[compound, bodyweight, both]`
- Tricep pushdown — `[isolation, cable, b]`
- Skull crusher — `[isolation, barbell, b]`

## Core

- Plank — `[isolation, bodyweight, b]`
- Hanging leg raise — `[isolation, bar, b]`
- Cable crunch — `[isolation, cable, b]`
- Ab wheel rollout — `[isolation, bodyweight, b]`
- Pallof press — `[isolation, cable, b]`
- Russian twist — `[isolation, bodyweight, b]`

## Neck

- Neck flexion (plate) — `[isolation, bodyweight, b]`
- Neck extension (plate) — `[isolation, bodyweight, b]`
- Neck harness — `[isolation, bodyweight, b]`

## Quadriceps

- Leg extension — `[isolation, machine, b]`
- Leg press — `[compound, machine, both]`
- Back squat — `[compound, barbell, both, big-six]`
- Front squat — `[compound, barbell, both]`
- Goblet squat — `[compound, dumbbell, b]`
- Bulgarian split squat — `[compound, dumbbell, both]`

## Hamstrings

- Leg curl — `[isolation, machine, b]`
- Conventional deadlift — `[compound, barbell, a, big-six]`
- Romanian deadlift — `[compound, barbell, both, big-six]`
- Glute-ham raise — `[compound, bodyweight, both]`
- Good morning — `[compound, barbell, both]`
- Hip thrust — `[compound, barbell, both, big-six]`

## Calves

- Standing calf raise — `[isolation, machine, b]`
- Seated calf raise — `[isolation, machine, b]`
- Tibialis raise — `[isolation, bodyweight, b]`
- Donkey calf raise — `[isolation, machine, b]`
````

- [ ] **Step 2: Commit**

```bash
git add personal-trainer/references/exercise-library.md
git commit -m "personal-trainer: seed exercise library from current sheet"
```

---

## Task 5: `references/running-periodization.md`

**Files:**
- Create: `personal-trainer/references/running-periodization.md`

The rules the run flow uses to generate a periodized plan. Phase split, 80/20, pace zone math, taper rules, and run-type definitions.

- [ ] **Step 1: Create `personal-trainer/references/running-periodization.md` with the following content**

````markdown
# Running periodization

Reference for the run flow. The engine consults this to compute phases, paces, and run distributions.

## Phase split

Given `W` weeks to race, allocate:

- Base — `round(W * 0.40)` weeks. Easy mileage, strides 1×/wk, no hard intervals.
- Build — `round(W * 0.35)` weeks. Intervals + tempo introduced.
- Peak — `round(W * 0.15)` weeks. Race-pace workouts, longest long run.
- Taper — remaining weeks (target ~10%). Volume cuts, intensity preserved.

If rounding leaves a 1-week mismatch, absorb it in Base.

If `W < 4`, the engine prompts the user before generating ("Not enough runway. Taper-only plan, or skip?").

## 80/20 rule

Across the week, ~80% of run time/distance is at easy pace, ~20% is hard (intervals, tempo, race-pace embedded in long runs). The engine ensures the weekly distribution stays in this range by construction.

## Pace zones (Daniels-style)

Derived from current best pace (`P_now`, s/km) at a reference distance AND goal race pace (`P_goal`, s/km). For training, use the closer of the two so paces stay achievable early and ambitious late:

| Zone | Offset from goal pace |
|---|---|
| Easy | +60 to +90 s/km |
| Long | +45 to +75 s/km |
| Marathon pace | +20 to +35 s/km |
| Tempo / Threshold | +10 to +25 s/km |
| Interval (VO2max) | −5 to −15 s/km |
| Repetition / Strides | ~5k pace, very short |

Round all training paces to the nearest 5 s/km.

Phase-specific selection:
- Base: only Easy + Strides
- Build: Easy + Tempo + Interval
- Peak: Easy + Marathon-pace + Interval + race-pace long runs
- Taper: Easy + short Tempo + short Interval tune-ups

## Long run rules

- Progress ~10% in distance per week.
- Cutback every 4th week to ~70% of prior peak.
- Peak long run capped by race distance:
  - 5k → up to 12 km
  - 10k → up to 18 km
  - HM → up to 22 km
  - Marathon → up to 32 km (peak 3 weeks before race)
- Race week: shakeout only (4–6 km easy + race day).

## Weekly structure (3 runs/week default)

- Day 1 — Quality session (intervals or tempo, phase-dependent)
- Day 2 — Easy or recovery (sometimes with strides)
- Day 3 — Long run (often with embedded quality in Build/Peak)

If runs/week > 3, add easy runs between quality days, never back-to-back quality.

## Taper template (HM example, 3-week taper)

| Week | Day 1 | Day 2 | Day 3 |
|---|---|---|---|
| W−2 | 80% of peak interval volume | Easy | 14–16 km easy |
| W−1 | Short tune-up (3×1 km @ tempo) | Easy 6 km | 10 km easy |
| Race wk | 5 km easy | Shakeout 4 km | Race |

For 5k/10k/M, scale proportionally.

## Run-type vocabulary

- **Easy** — Z1/Z2, conversational, +60–90 s over goal pace.
- **Long** — extended easy; embedded quality in Peak.
- **Tempo** — sustained threshold effort, 4–10 km depending on phase.
- **Interval** — VO2max-zone reps (200 m–2 km) with jog recovery.
- **Strides** — 6–10× 20s at near-5k pace, full recovery between.
- **Race-pace** — segments at exact goal pace, embedded in long runs.
````

- [ ] **Step 2: Commit**

```bash
git add personal-trainer/references/running-periodization.md
git commit -m "personal-trainer: document running periodization rules"
```

---

## Task 6: Test fixture factory

**Files:**
- Create: `personal-trainer/tests/conftest.py`

A single `pytest` fixture that builds a minimal in-memory logbook (matching the real schema) and writes it to a temp path. Every script test loads this fixture instead of touching the real logbook.

- [ ] **Step 1: Create `personal-trainer/tests/conftest.py` with the following content**

```python
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
```

- [ ] **Step 2: Verify openpyxl is available locally**

Run: `python3 -c "import openpyxl; print(openpyxl.__version__)"`
Expected: prints a version like `3.1.5`. If it fails: `pip install openpyxl` (or use uv). The scripts will run via `uv run --script`; the test runner needs openpyxl installed in the active Python environment.

- [ ] **Step 3: Smoke-test the fixture**

Run: `cd personal-trainer && python3 -c "
import sys; sys.path.insert(0, 'tests')
from pathlib import Path
import tempfile
from conftest import _build_logbook
p = Path(tempfile.mkdtemp()) / 'test.xlsx'
_build_logbook(p)
from openpyxl import load_workbook
wb = load_workbook(p)
print('sheets:', wb.sheetnames)
print('R3 col D:', wb['Resistance - 2026'].cell(row=3, column=4).value)
print('R10 col D:', wb['Resistance - 2026'].cell(row=10, column=4).value)
print('R17 col D:', wb['Resistance - 2026'].cell(row=17, column=4).value)
"`

Expected:
```
sheets: ['Resistance - 2026', 'Running - 2026']
R3 col D: Incline press
R10 col D: Cable curl
R17 col D: Leg extension
```

- [ ] **Step 4: Commit**

```bash
git add personal-trainer/tests/conftest.py
git commit -m "personal-trainer: test fixture factory for minimal logbook"
```

---

## Task 7: `scripts/read_logbook.py` — TDD

**Files:**
- Create: `personal-trainer/tests/test_read_logbook.py`
- Create: `personal-trainer/scripts/read_logbook.py`

Reads the logbook and prints JSON to stdout. Two modes selected by `--sheet`:
- `--sheet=resistance` → current template + next-empty-week column index
- `--sheet=running` → list of filled weeks + next-empty-week row

- [ ] **Step 1: Write the failing tests**

Create `personal-trainer/tests/test_read_logbook.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd personal-trainer && pytest tests/test_read_logbook.py -v`
Expected: FAIL because `scripts/read_logbook.py` doesn't exist yet.

- [ ] **Step 3: Write the minimal implementation**

Create `personal-trainer/scripts/read_logbook.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd personal-trainer && pytest tests/test_read_logbook.py -v`
Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add personal-trainer/scripts/read_logbook.py personal-trainer/tests/test_read_logbook.py
git commit -m "personal-trainer: add read_logbook script with tests"
```

---

## Task 8: `scripts/write_resistance_swap.py` — TDD

**Files:**
- Create: `personal-trainer/tests/test_write_resistance_swap.py`
- Create: `personal-trainer/scripts/write_resistance_swap.py`

Overwrites the Exercise cell (column D) at a given row with a new exercise name. Atomic write: save to temp file, then replace original.

- [ ] **Step 1: Write the failing tests**

Create `personal-trainer/tests/test_write_resistance_swap.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd personal-trainer && pytest tests/test_write_resistance_swap.py -v`
Expected: FAIL — script does not exist.

- [ ] **Step 3: Write the minimal implementation**

Create `personal-trainer/scripts/write_resistance_swap.py`:

```python
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
    wb.save(tmp_path)
    os.replace(tmp_path, path)

    print(f"Wrote '{args.exercise}' to row {args.row}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd personal-trainer && pytest tests/test_write_resistance_swap.py -v`
Expected: all 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add personal-trainer/scripts/write_resistance_swap.py personal-trainer/tests/test_write_resistance_swap.py
git commit -m "personal-trainer: add write_resistance_swap script with tests"
```

---

## Task 9: `scripts/write_running_plan.py` — TDD

**Files:**
- Create: `personal-trainer/tests/test_write_running_plan.py`
- Create: `personal-trainer/scripts/write_running_plan.py`

Reads JSON plan from stdin, writes rows to the running sheet starting at a specified row. Refuses to overwrite filled weeks unless `--force` is given.

Plan JSON schema:

```json
{
  "start_row": 2,
  "weeks": [
    {"week": 1, "day1": "5x800m @ 4:05/km", "day2": "6 km Easy", "day3": "16 km Easy"},
    {"week": 2, "day1": "...", "day2": "...", "day3": "..."}
  ]
}
```

- [ ] **Step 1: Write the failing tests**

Create `personal-trainer/tests/test_write_running_plan.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd personal-trainer && pytest tests/test_write_running_plan.py -v`
Expected: FAIL — script does not exist.

- [ ] **Step 3: Write the minimal implementation**

Create `personal-trainer/scripts/write_running_plan.py`:

```python
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

    fd, tmp = tempfile.mkstemp(suffix=".xlsx", dir=str(path.parent))
    os.close(fd)
    tmp_path = Path(tmp)
    wb.save(tmp_path)
    os.replace(tmp_path, path)

    print(f"Wrote {len(weeks)} weeks starting at row {start_row}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd personal-trainer && pytest tests/test_write_running_plan.py -v`
Expected: all 6 tests PASS.

- [ ] **Step 5: Run the full test suite to confirm no regressions**

Run: `cd personal-trainer && pytest -v`
Expected: 17 tests pass (5 read + 6 swap + 6 plan).

- [ ] **Step 6: Commit**

```bash
git add personal-trainer/scripts/write_running_plan.py personal-trainer/tests/test_write_running_plan.py
git commit -m "personal-trainer: add write_running_plan script with tests"
```

---

## Task 10: `SKILL.md` — engine

**Files:**
- Create: `personal-trainer/SKILL.md`

The engine. Short and procedural. References do the heavy reading.

- [ ] **Step 1: Create `personal-trainer/SKILL.md` with the following content**

````markdown
---
name: personal-trainer
description: Update CJ's training plan in `~/Downloads/Training Logbook.xlsx`. Two sub-flows — `gym` performs iterative exercise swaps respecting Andrew Huberman's foundational fitness protocol; `run` generates a race-specific periodized running plan. Triggers on `/personal-trainer [gym|run]`, "update my workout plan", "swap an exercise", "build my running plan", "plan my next race". Do not auto-trigger on casual training chat — explicit ask only.
---

# Personal trainer

Update CJ's training plan in `~/Downloads/Training Logbook.xlsx`. Two sub-flows: `gym` (iterative exercise swaps respecting Huberman principles) and `run` (race-specific periodized plan generator).

Read this entire file before responding. Reference files in `references/` are loaded only when the relevant sub-flow runs.

## Invocation

Explicit only. Triggers:

- `/personal-trainer gym` → gym swap flow
- `/personal-trainer run` → run plan flow
- `/personal-trainer` → ask which
- Natural-language asks: "update my workout plan", "swap an exercise", "build my running plan", "plan my next race"

Do not run this skill for casual training questions. If you're not sure whether the user wants the skill, ask.

## Shared boundaries

- Logbook path: `~/Downloads/Training Logbook.xlsx` (fixed). If missing → fail loud with the path.
- Never write xlsx without an explicit user approval.
- All writes go through the scripts in `scripts/`. Never use `openpyxl` directly from the chat.
- Each script accepts `--logbook` and exits non-zero on error; capture stderr and surface it to the user.

## Sub-flow router

1. Determine sub-flow from invocation. If absent, ask: "Gym or run?"
2. Load `references/logbook-schema.md` (always — both flows need it).
3. Run the chosen flow.

## Gym flow

Read `references/huberman-protocol.md` and `references/exercise-library.md` before starting.

### 1. Load current template

```bash
python3 scripts/read_logbook.py --logbook ~/Downloads/Training\ Logbook.xlsx --sheet resistance
```

Parse the JSON. Cache `template` (list of `{row, day, description, muscle_group, exercise}`) and `next_empty_week` (int) in working memory.

### 2. Identify the swap target

Match the user's phrasing against the template:

| User says | Target |
|---|---|
| "swap incline press" / "replace X" | The matching row(s) by exercise name (case-insensitive contains) |
| "rotate chest day" / "refresh shoulders" | All rows in that muscle group |
| "no cable today" / "lost machine access" | All rows whose current exercise is tagged with the missing equipment |
| "refresh the whole week" | Every row in the template |

If no match, list the template back to the user and ask which row(s) to swap.

### 3. Propose alternatives

For each target row, pull 2–3 candidates from `exercise-library.md` filtered by:

1. Same `muscle_group` as the row
2. Same compound/isolation as the current exercise
3. Equipment available (full gym by default; restrict if user specified)
4. Not already used elsewhere in the same day
5. Big-six preferred when the slot is a compound

Output format:

```
Day:    Monday (Torso)
Group:  Chest
Swap:   Incline press → ?

  1. Bench press         [compound, barbell, big-six]
  2. Dumbbell press      [compound, dumbbell]
  3. Cable crossover     [isolation, cable]   (different tier — accepts demotion)
```

Always show the tag block; it tells the user why each candidate qualified.

### 4. Approval

Wait for the user to choose. Accept:

- A number from the list
- A custom exercise name ("actually, Romanian deadlifts" — verify muscle group plausibly matches; if not, ask)
- "skip" → no write, move to next target
- "all the same" during multi-row swaps → apply choice 1 to every remaining row in the batch

### 5. Write

For each approved swap:

```bash
python3 scripts/write_resistance_swap.py \
  --logbook ~/Downloads/Training\ Logbook.xlsx \
  --row <ROW> \
  --exercise "<NAME>"
```

If the script exits non-zero, surface the stderr message and stop. Do not retry silently.

### 6. Surface history caveat (once per session)

Before the first write of a swap session, tell the user:

> "Swapping overwrites the Exercise cell. Past weeks' Reps/Weight stay in their cells but are now historically tied to the old exercise name. Continue?"

Only ask once per session.

### 7. Loop

After each batch of writes, ask: "Another swap, or done?" Exit cleanly on done.

## Run flow

Read `references/running-periodization.md` before starting.

### 1. Gather inputs

Single numbered prompt:

```
To build the plan, I need:

1. Race date (ISO, e.g. 2026-09-13)
2. Race distance (5k / 10k / HM / M / other)
3. Goal time (h:mm:ss)
4. Current best pace (give the distance too, e.g. "21:30 for 5k")
5. Runs per week (default 3)
6. Allowed run types (default: intervals, tempo, easy, long, strides)
```

Validate after receiving:

- Race date strictly future. If past → ask for a real date.
- Compute weeks-to-race. If `< 4` → warn: "Less than 4 weeks. Generate taper-only plan, or abort?"
- Goal pace vs current pace: if goal pace is more than 10% faster (in s/km) than current, surface a warning and ask the user to confirm before continuing.

### 2. Compute paces

Convert current and goal to s/km. Derive training paces per the table in `references/running-periodization.md`. Round to 5 s/km. Cache as a dict the run-plan generator will reference.

### 3. Generate the plan

Apply the phase split, long-run progression, and weekly structure from `references/running-periodization.md`. Build a list of `{week, day1, day2, day3}` entries.

### 4. Present + iterate

Show the full plan as a table:

```
Week | Day 1                       | Day 2          | Day 3
1    | 6x800m @ 4:05/km, 90s jog   | 7 km Easy      | 16 km Easy
2    | ...
```

Ask: "Approve? Or request edits (e.g. 'week 6 long run shorter', 'swap day 2/3 in week 8')."

Apply edits in place, re-show the affected weeks, re-ask. Loop until approval.

### 5. Choose write target

Read the running sheet first:

```bash
python3 scripts/read_logbook.py --logbook ~/Downloads/Training\ Logbook.xlsx --sheet running
```

- If `filled_weeks` is empty → write at `start_row = 2`.
- If `filled_weeks` has entries → ask: "`Running - 2026` already has weeks N–M filled. Append after week M, replace all weeks, or write to a new sheet `Running - <year>-<race-name>` (manual setup required)?"

For v1: only Append (start_row = next_empty_row) and Replace (start_row = 2, with `--force`) are supported in-script. New-sheet path is documented as out of scope for v1; tell the user to create the sheet manually and re-run.

### 6. Write

Build the JSON payload and pipe to the script:

```bash
echo '{"start_row": 2, "weeks": [...]}' | \
  python3 scripts/write_running_plan.py --logbook ~/Downloads/Training\ Logbook.xlsx [--force]
```

Surface success message with the count of weeks written.

## Edge cases

- **Logbook missing or unwritable** → fail loud, surface the path.
- **Logbook open in Excel** → script exits with "Logbook open in Excel. Close and retry." Pass that message back verbatim.
- **No empty week column left in Resistance sheet** → tell the user; ask whether to start over from week 1 (year wrap) or extend the sheet manually. The skill does not create new week columns in v1.
- **6-day Huberman alt schedule detected** (user mentions Tue/Fri intervals) → acknowledge and respect; don't collapse to 3-day.
- **User requests exercise not in library** → accept verbatim; after the write, offer: "Want me to add `<name>` to `exercise-library.md` for next time?" (manual edit, not scripted in v1).
- **Race < 4 weeks away** → confirm taper-only plan before generating.
- **Goal pace > 10% faster than current** → warn + confirm.
- **Running - 2026 sheet already has a plan** → never silently overwrite. Force decision.
- **Year boundary** → the sheets are year-specific (`Resistance - 2026`, `Running - 2026`). The skill does not auto-create sheets for new years; ask the user to create them.

## Files in this skill

- `SKILL.md` (this file) — engine
- `references/logbook-schema.md` — xlsx sheet/column layout, write rules
- `references/huberman-protocol.md` — A/B alternation, big-six, principles
- `references/exercise-library.md` — seeded library of exercises with tags
- `references/running-periodization.md` — phases, 80/20, pace zones, taper rules
- `scripts/read_logbook.py` — parse current state → JSON on stdout
- `scripts/write_resistance_swap.py` — overwrite Exercise cell at given row
- `scripts/write_running_plan.py` — write generated plan to Running sheet
- `commands/personal-trainer.md` — slash command wrapper
- `README.md` — install + usage
````

- [ ] **Step 2: Commit**

```bash
git add personal-trainer/SKILL.md
git commit -m "personal-trainer: add SKILL.md engine"
```

---

## Task 11: `commands/personal-trainer.md`

**Files:**
- Create: `personal-trainer/commands/personal-trainer.md`

Slash command wrapper. Mirrors the convention used by `coach/commands/coach.md` and others.

- [ ] **Step 1: Create `personal-trainer/commands/personal-trainer.md` with the following content**

````markdown
---
description: Update training plan — gym exercise swaps (Huberman) or race-specific running plan
argument-hint: "[gym|run]"
---

Run the `personal-trainer` skill.

Arguments:
- `gym` — iterative exercise swap flow
- `run` — generate a race-specific running plan
- (none) — ask which

Logbook path: `~/Downloads/Training Logbook.xlsx`.

Invocation: $ARGUMENTS
````

- [ ] **Step 2: Commit**

```bash
git add personal-trainer/commands/personal-trainer.md
git commit -m "personal-trainer: add slash command wrapper"
```

---

## Task 12: `README.md`

**Files:**
- Create: `personal-trainer/README.md`

Install + usage doc matching the conventions of other skills in this repo.

- [ ] **Step 1: Create `personal-trainer/README.md` with the following content**

````markdown
# personal-trainer

Update CJ's training plan in `~/Downloads/Training Logbook.xlsx`. Two flows:

- **Gym** — swap individual exercises while keeping Andrew Huberman's foundational fitness principles intact (A/B alternation, big-six bias, muscle-group balance).
- **Run** — generate a race-specific periodized running plan from race date, distance, goal time, current pace, runs/week, and allowed run types.

## Install

Symlink into Claude Code's project skills directory (see repo root README for the global pattern). The skill expects `openpyxl` to be installed in the Python the slash command shells out to:

```bash
pip install openpyxl
# or with uv (recommended)
uv tool install openpyxl
```

The scripts also work via `uv run --script` (inline metadata declares the dep), which means a system `python3` without openpyxl is fine as long as `uv` is on PATH.

## Usage

```text
/personal-trainer gym       # iterative exercise swaps
/personal-trainer run       # generate race plan
/personal-trainer           # ask which
```

Natural-language triggers also work: "swap incline press", "plan my next race", "update my workout plan".

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | engine — invocation, both flows, edge cases |
| `commands/personal-trainer.md` | slash command wrapper |
| `references/logbook-schema.md` | xlsx layout the scripts assume |
| `references/huberman-protocol.md` | gym-flow principles |
| `references/exercise-library.md` | swap candidate catalogue |
| `references/running-periodization.md` | run-flow rules |
| `scripts/read_logbook.py` | read current state → JSON |
| `scripts/write_resistance_swap.py` | swap a single exercise |
| `scripts/write_running_plan.py` | write a generated plan |
| `tests/` | pytest suite against generated fixtures |

## Tests

```bash
cd personal-trainer && pytest -v
```

Tests build a minimal xlsx fixture in `tmp_path`; the real logbook is never touched.

## Out of scope (v1)

- Logging completed workouts (CJ fills xlsx manually).
- Non-running cardio.
- Recovery / sleep / nutrition.
- Auto-progressive-overload for resistance training.
- Multi-block periodization in a single invocation.
- Creating year-specific sheets (`Resistance - 2027`, etc.) automatically.
````

- [ ] **Step 2: Commit**

```bash
git add personal-trainer/README.md
git commit -m "personal-trainer: add README"
```

---

## Task 13: Real-logbook smoke test

**Files:**
- (No new files — verification only.)

Confirm the skill works against the actual logbook. Read-only operations only; never write to the real file as part of this task.

- [ ] **Step 1: Read resistance state**

Run:

```bash
python3 personal-trainer/scripts/read_logbook.py \
  --logbook ~/Downloads/Training\ Logbook.xlsx \
  --sheet resistance | python3 -m json.tool | head -40
```

Expected: valid JSON with `template` list including `Incline press`, `Cable curl`, `Leg extension` etc., and a `next_empty_week` int matching the first unfilled week in the real sheet (use the openpyxl inspection from earlier in this plan as ground truth).

- [ ] **Step 2: Read running state**

Run:

```bash
python3 personal-trainer/scripts/read_logbook.py \
  --logbook ~/Downloads/Training\ Logbook.xlsx \
  --sheet running | python3 -m json.tool | head -40
```

Expected: `filled_weeks` array containing the existing 19-week half-marathon plan, with `next_empty_row` = 21 (week 19 row + 1).

- [ ] **Step 3: Dry-run a swap (do NOT execute the write against the real file)**

Open `SKILL.md` and follow the gym flow conceptually: pick a target ("swap incline press"), propose candidates from the library, confirm the output format and that the candidates pass the filter (chest, compound, equipment plausible).

Document the output in chat and confirm to the user.

- [ ] **Step 4: Commit nothing — just confirm**

This task produces no code or commits. It's a manual verification step.

---

## Self-review

After the plan is executed end-to-end:

1. **Spec coverage:**
   - Two flows (gym swap + run plan) — covered by tasks 10 (engine) + 7–9 (scripts).
   - Slash command + sub-args — covered by task 11.
   - Logbook path fixed + fail-loud — covered in `SKILL.md` (task 10) and scripts (tasks 7–9).
   - Huberman principles documented — task 3.
   - Exercise library seeded from current sheet — task 4.
   - Running periodization rules — task 5.
   - Schema reference — task 2.
   - Tests — tasks 7–9.
   - Smoke test on real logbook — task 13.

2. **Placeholder scan:** No TBD/TODO; every code block contains real code; every command has expected output or a verification step.

3. **Type consistency:** Script flag names (`--logbook`, `--sheet`, `--row`, `--exercise`, `--force`) are identical across the engine, the scripts, and the tests. JSON keys for the running plan (`start_row`, `weeks`, `week`, `day1`, `day2`, `day3`) match between script, tests, and `SKILL.md`.
