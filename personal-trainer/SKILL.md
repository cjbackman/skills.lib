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
