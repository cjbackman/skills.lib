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
