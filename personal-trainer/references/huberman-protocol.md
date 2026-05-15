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
