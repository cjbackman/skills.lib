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
