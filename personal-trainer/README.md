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
