# Personal trainer skill — design spec

**Date:** 2026-05-15
**Status:** Approved, pending implementation plan
**Skill name:** `personal-trainer`
**Repo location:** `personal-trainer/` at repo root

## Purpose

Update CJ's training plan in `~/Downloads/Training Logbook.xlsx`. Two sub-flows:

1. **Gym (resistance)** — swap individual exercises while respecting Andrew Huberman's foundational fitness protocol principles. Iterative; no progressive-overload automation (CJ tracks reps/weights manually).
2. **Run** — generate a race-specific running plan given race date, distance, goal time, current pace, runs/week, and allowed run types.

## Invocation

Explicit only. Slash command:

- `/personal-trainer gym` → gym swap flow
- `/personal-trainer run` → race plan flow
- `/personal-trainer` → ask which

Natural-language triggers: "update my workout plan", "swap an exercise", "build my running plan", "plan my next race", "personal trainer".

Do NOT auto-trigger on casual training talk. Explicit ask only.

## Inputs

### Logbook

Path: `~/Downloads/Training Logbook.xlsx` (fixed).

Relevant sheets:

| Sheet | Purpose |
|---|---|
| `Resistance - 2026` | Current resistance plan. 3 gym days/week. Columns: `Day`, `Description`, `Muscle Group`, `Exercise`, then paired (`Reps`, `Weight`) per week up to ~20 weeks. |
| `Running - 2026` | Current running plan. Columns: `Week`, `Day 1`, `Day 2`, `Day 3`, `Status`, `Comment`. |
| `Metadata` | HR zones, Huberman links, A/B schedule legend, big-six list, alt 6-day split. |

Resistance week template (current):

| Day | Description | Muscle group | Exercises (2 per group) |
|---|---|---|---|
| Monday | Torso | Chest / Back / Shoulders | 6 exercises |
| Wednesday | Arms, Neck & Core | Biceps / Triceps / Core / Neck | 6 exercises |
| Thursday | Legs | Quadriceps / Hamstrings / Calves | 6 exercises |

If logbook missing → fail loudly. No fallback path.

### Huberman protocol

Principles enforced when proposing swaps (full text in `references/huberman-protocol.md`):

- **A/B alternation:** Schedule A = heavy (4–8 reps, 3–4 sets, 2–4 min rest). Schedule B = moderate/light (8–15 reps, 2–3 sets, ~90 s rest). Compound lifts gravitate to A; isolation/machine work fits B.
- **Big six bias:** Squats, Bench press, Deadlift, Military press, Chin-up, Hip thrust — prefer these for compound slots when applicable.
- **Compound before isolation** within a day.
- **Muscle group balance** preserved on swap (chest swap stays chest, etc.).
- **2 exercises per muscle group** (matches current sheet).
- **3-day split** is current default. Detect 6-day if user moved to alt split listed in Metadata.

## Architecture

Single skill. Shared engine in `SKILL.md`. Sub-flow logic loaded from references on demand. Scripts handle xlsx I/O.

```
personal-trainer/
├── SKILL.md
├── commands/personal-trainer.md
├── README.md
├── references/
│   ├── huberman-protocol.md       # A/B alternation, big-six, principles
│   ├── exercise-library.md        # seeded from current sheet, tagged
│   ├── running-periodization.md   # phases, 80/20, pace zones, taper
│   └── logbook-schema.md          # xlsx sheet structure + write locations
└── scripts/
    ├── read_logbook.py            # parse current resistance template + last running week
    ├── write_resistance_swap.py   # write swapped exercise name to next-week column
    └── write_running_plan.py      # write full periodized plan to Running sheet
```

## Gym flow (swap-only, iterative)

### 1. Load context

- Read `Resistance - 2026` via `read_logbook.py`. Extract current weekly template: `(day, description, muscle_group, exercise)` rows.
- Load `references/huberman-protocol.md` and `references/exercise-library.md`.

### 2. Identify swap target

Prompt format depends on user phrasing:

- "swap incline press" → target = that single exercise
- "rotate chest day" → target = both chest exercises
- "lost cable access" → target = all cable-tagged exercises
- "refresh the whole week" → target = entire template

If ambiguous, ask one clarifying question.

### 3. Propose alternatives

For each target exercise, return 2–3 candidates from `exercise-library.md` filtered by:

1. Same `muscle_group`
2. Compound/isolation parity (if target is compound, candidates are compound)
3. Equipment available (default: full gym; user can constrain in prompt)
4. Big-six preference when compound slot
5. Not already in the same day's plan (avoid duplication)

Output format:

```
Day:    Monday (Torso)
Group:  Chest
Swap:   Incline press → ?

  1. Bench press         [compound, barbell, big-six]
  2. Dumbbell press      [compound, dumbbell]
  3. Push-ups (weighted) [compound, bodyweight]
```

### 4. Approval + write

User picks number, custom exercise name, or "skip". On approval:

- Write chosen exercise name into next empty week column's `Exercise` cell at the matching row.
- Leave `Reps` / `Weight` blank (CJ fills as he trains).
- Confirm: "Wrote <exercise> to Week <N> column."

### 5. Loop

After write, prompt: "Another swap, or done?" Exit cleanly on done.

## Run flow

### 1. Gather inputs

Single numbered prompt:

1. Race date (ISO)
2. Race distance (5k / 10k / HM / M / other)
3. Goal time
4. Current best pace at reference distance (specify distance)
5. Runs per week (default 3)
6. Allowed run types (default: intervals, tempo, easy, long, strides)

Validate: race date in future, goal pace plausible vs current (warn if >10 % faster than current, ask to confirm).

### 2. Compute plan structure

- Weeks-to-race = (race_date − today) / 7, floored.
- If < 4 weeks → warn ("not enough runway for full periodization; generate taper-only plan?").
- Phase split (proportional to weeks available):
  - Base ~40 % — easy mileage + strides
  - Build ~35 % — intervals + tempo introduced
  - Peak ~15 % — race-pace workouts, peak long run
  - Taper ~10 % — volume cut, intensity preserved

### 3. Compute training paces

Daniels-style derivation from current pace + goal pace:

| Zone | Formula |
|---|---|
| Easy | goal_pace + 60–90 s/km |
| Long | goal_pace + 45–75 s/km |
| Tempo | goal_pace + 20–30 s/km |
| Threshold | goal_pace + 10–15 s/km |
| Interval | goal_pace − 5–10 s/km |
| Strides | ~5k pace, short bursts |

Round to 5 s/km granularity.

### 4. Generate week plan

Rules:

- 80/20 easy/hard split across week
- Hard sessions: 1 quality day (intervals or tempo) + 1 long run with optional embedded quality
- Long run progression ~10 %/week, cutback every 4th week to ~70 % of prior peak
- Long run ceiling: race distance (HM=21 km, M=race-distance taper rules)
- Taper: weeks W−2 = 80 % volume, W−1 = 60 % volume, race week = race-day shakeout only

### 5. Present + approve

Output as table:

```
Week | Day 1                       | Day 2          | Day 3
1    | 6x800m @ 4:05/km, 90s jog   | 7 km Easy      | 16 km Easy
...
```

User approves whole plan or requests edits ("week 6 long run too long", "swap day 2 with day 3 in week 8"). Apply edits, re-show, re-approve.

### 6. Write

Destination decision:

- If `Running - 2026` is empty/unstarted → write into it directly.
- If `Running - 2026` already has filled weeks → ask: "Append after week N, replace, or new sheet `Running - <year>-<race-name>`?"

Write via `write_running_plan.py`. Preserve existing formatting.

## Approval gates

| Action | Approval |
|---|---|
| Exercise swap | One approval per swap |
| Running plan | One approval for full plan (with iterative edit loop) |
| Logbook write | Always shown as diff before write |

Never write xlsx without explicit user approval.

## Edge cases

- **Logbook missing or unwritable** → fail loud, surface path.
- **Logbook open in Excel** → openpyxl write may fail; surface error and ask user to close.
- **No empty week column left in Resistance sheet** → ask whether to overwrite week 1 (year wrap) or extend sheet.
- **6-day Huberman alt schedule detected** → respect it; don't collapse to 3-day.
- **User requests exercise not in library** → accept verbatim, append to library with default tags after confirming muscle group.
- **Race < 4 weeks away** → offer taper-only plan.
- **Goal pace > 10 % faster than current** → warn + confirm before generating.
- **`Running - 2026` already has race plan in it** → never silently overwrite. Force decision.
- **Year boundary** → user may need `Resistance - 2027` sheet next year; out of scope for v1, ask user to create manually.

## Out of scope

- Tracking completed workouts (CJ fills xlsx manually).
- Cardio other than running.
- Recovery / sleep / nutrition advice.
- Multi-block periodization (one block per invocation).
- Mobile / on-the-go workouts.
- Auto-progressive-overload for resistance (explicitly removed per CJ's feedback).

## Files in this skill

- `SKILL.md` — engine
- `references/huberman-protocol.md` — A/B alternation, big-six, principles
- `references/exercise-library.md` — seeded from `Resistance - 2026` exercises, tagged compound/isolation/equipment/big-six
- `references/running-periodization.md` — phases, 80/20, pace zones, taper rules, run-type definitions
- `references/logbook-schema.md` — xlsx sheet/column layout, write locations
- `scripts/read_logbook.py` — parse current state
- `scripts/write_resistance_swap.py` — write swapped exercise to next-week column
- `scripts/write_running_plan.py` — write generated plan to Running sheet
- `commands/personal-trainer.md` — slash command wrapper
- `README.md` — install + usage
