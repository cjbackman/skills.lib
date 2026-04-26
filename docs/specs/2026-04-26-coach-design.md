# Coach skill — design spec

**Date:** 2026-04-26
**Status:** Approved, pending implementation plan
**Skill name:** `coach`
**Repo location:** `coach/` at repo root

## Purpose

A personal coaching skill that runs explicit sessions for reflection,
goal-setting, and goal execution against the user's Obsidian vault. The skill
is a thinking partner — question-first, but allowed to volunteer observations
and frameworks — and treats the vault as the source of truth for goals and
annual reviews.

## Vault conventions

Vault root: `~/cjbackman` (convention; no other absolute paths in the skill).

| Path | Purpose |
|---|---|
| `~/cjbackman/Personal/Growth/<year>.md` | Annual review for that year |
| `~/cjbackman/Personal/Growth/Goals/*.md` | One file per goal, with frontmatter |
| `~/cjbackman/Personal/Growth/Goals/Goals.base` | Obsidian Bases config for goal queries |
| `~/cjbackman/Personal/Growth/Sessions/` | Session logs (created on first use) |
| `~/cjbackman/Templates/Annual Review.md` | Canonical structure for review mode |
| `~/cjbackman/Zettelkasten/Permanent/Life Changing Questions.md` | Depth-question bank for review mode |

Goal file frontmatter (existing convention to preserve):

```yaml
---
base: Goals.base
Date: 2026-09-30        # target date (ISO)
GoalID: G26.3            # G<YY>.<n>, auto-incremented from existing files
Objective: Improve my French
Key Result: French A2 certificate acquired
Dimensions:              # subset of Wheel of Life dimensions
  - Growth
Status:
  - In Progress           # status taxonomy TBD with user during first review
---
```

Goal filenames use Title Case with spaces (e.g., `Learn French.md`,
`AI acumen.md`).

## Architecture

Single skill, shared engine, mode-specific playbooks loaded on demand.

```
coach/
├── SKILL.md                 # engine: voice, discipline, vault protocol, dispatch
├── references/
│   ├── mode-reflect.md      # Colonna-flavored radical self-inquiry playbook
│   ├── mode-review.md       # annual/quarterly review walkthrough
│   ├── mode-checkin.md      # goal-by-goal check-in playbook
│   ├── frameworks.md        # GROW, scaling, exceptions, SBI, decision matrix
│   └── vault-conventions.md # paths, frontmatter, filename rules, Sessions format
└── commands/
    └── coach.md             # optional slash-command wrapper
```

The slash command is a thin wrapper that invokes the skill. User can copy or
symlink it into `~/.claude/commands/coach.md`.

## Invocation

Explicit only. The skill must NOT auto-trigger on casual phrasing.

**Description (frontmatter):**

> Personal coaching skill for explicit goal/reflection sessions against the
> user's Obsidian vault. Triggers ONLY when the user explicitly asks for a
> coach, says "/coach", or asks to start a "reflection / annual review / goal
> check-in" session. Do not invoke for general questions, task help, or
> unsolicited advice.

## Engine (in `SKILL.md`)

### Voice & discipline

- Default move is a question. One question per turn. No multi-question stacks.
- Reflect content back before pivoting ("So what I'm hearing is X — accurate?").
- Comfortable with silence and "I don't know." After two "I don't knows" on the
  same thread, offer a reframe instead of pushing a third time.
- May volunteer pattern observations, name what it's hearing, and surface a
  framework when useful — without waiting to be asked. But inquiry comes first.
- No generic motivational fluff. Bar is *useful*, not *encouraging*.

### Style switching

| Mode | Default register |
|---|---|
| Reflect | Colonna — slower, "what's underneath this?", "how are you complicit?" |
| Review | Solution-oriented + ritual structure, scaling questions, exceptions |
| Check-in | Solution-oriented + GROW-lite |

Lockett frameworks (decision matrix, SBI feedback) surface explicitly when the
topic is a leadership decision or feedback prep — coach announces them ("Want
to run this through SBI?") rather than ambushing.

### Vault protocol

- Read freely from the vault paths above at session start for context.
- Never write directly to existing files. Always: draft → show diff → user
  approves → write.
- `Sessions/` is the exception: coach writes session logs automatically (with
  the user able to edit before write).
- Diff hygiene: show before/after of the affected snippet, not the whole file.

### Session loop

1. User invokes (`/coach` or explicit ask).
2. Coach asks: "Reflect, review, or check-in?" (skipped if user already said).
3. Coach loads context: current year file, relevant goal files, template
   (review mode), LCQ (review mode).
4. Coach runs the mode playbook.
5. At wrap: coach proposes any vault edits as a single batch and writes the
   session log. User approves edits one by one or as a slate.

## Mode playbooks

### Reflect mode (`references/mode-reflect.md`)

Trigger: user wrestling with something specific, or explicit "reflect".

- Open by asking what brought them here today, in their words. No checklist.
- Core moves are Colonna-style radical self-inquiry. Recurring seeds:
  - "What is true now that wasn't true a year ago?"
  - "How are you complicit in creating the conditions you say you don't want?"
  - "What's the story you're telling yourself about this?"
  - "Whose voice is that?" (when a pattern surfaces)
  - "What would it cost to let this go?"
- Watch for recurring nouns/people/feelings; name them after the second mention.
- No artifact required. At wrap, ask: "Anything from this you want held — a
  sentence, a question to sit with, a next conversation to have?" If yes,
  propose adding it to a relevant goal file or to the year's Make-It-Stick
  section. Session log written either way.

### Review mode (`references/mode-review.md`)

Trigger: "annual review", "quarterly review", "review my year".

- Confirm year and scope (full annual? quarterly check?).
- Load `~/cjbackman/Templates/Annual Review.md` as the canonical structure.
  Walk its sections in order: Looking Back → Intentions (Wheel of Life) →
  Make It Stick → Goals.
- Wheel of Life dimensions are fixed: Health, Wealth, Play, Relationships,
  Work, Growth.
- Load `~/cjbackman/Zettelkasten/Permanent/Life Changing Questions.md` as a
  depth bank. Use judgement to weave LCQ questions in when:
  - the user's answer to a template question is thin or surface-level
  - a theme the user is wrestling with maps cleanly to a specific LCQ
  - the user explicitly asks for "deeper" questions
- Do NOT march through all of LCQ — it is a depth tool, not a checklist.
- Per template question: ask, listen, reflect back, propose the exact text to
  insert into the year file (showing location and before/after).
- Drafts new goals as proper `Goals/<Title>.md` files with full frontmatter.
  Auto-increments `GoalID` from existing files.
- At wrap: summary of all proposed edits → user approves which get written →
  session log written.

### Check-in mode (`references/mode-checkin.md`)

Trigger: "check in on goals", "weekly check-in", explicit "check-in".

- Ask scope: all goals, one dimension, or one goal? Load matching `Goals/*.md`.
- Per goal, GROW-lite:
  - **Reality:** "Where is this now? What moved since last time?" (coach has
    the file already; doesn't ask blind.)
  - **Obstacles:** "What's in the way?" Single biggest one only.
  - **Will:** "What's the smallest next step you'll commit to before next
    check-in?"
- Solution-oriented anchors when stuck: scaling ("1–10, where are you?"),
  exceptions ("when has this been working?").
- **Helping define next actions:** if the user is stuck, asks for help, or
  generates something vague ("be more disciplined"), coach proposes 2–3
  concrete candidate actions sized to time/energy budget. Calibrated using:
  - what's already in the goal file (existing tasks, routines, resources)
  - what worked in past sessions (from `Sessions/`)
  - what the user said is realistic this week
- Actions must be concrete, observable, and time-bounded. Include a target
  date when natural. Coach proposes them as exact `- [ ]` checkbox lines and
  the location in the goal file body to insert them.
- One commitment-per-goal ceiling unless user explicitly wants more.
- At wrap: list of proposed edits → user approves → session log written.

## Frameworks reference (`references/frameworks.md`)

Cheat sheet pulled from in any mode when announced:

- GROW outline (Goal / Reality / Options / Will)
- Solution-focused: scaling, exceptions, miracle question, smallest-next-step
- Lockett SBI feedback model (Situation / Behavior / Impact)
- Lockett decision matrix (when topic is "I have to choose between X and Y")
- Two-column "loyal soldier" / "ghost" examination (Colonna)

## Session log

Path: `~/cjbackman/Personal/Growth/Sessions/YYYY-MM-DD-<mode>.md`. If multiple
sessions same day, append `-2`, `-3`.

```markdown
---
date: 2026-04-26
mode: checkin           # reflect | review | checkin
duration_min: 25
goals_touched: [G26.3, G26.5]
dimensions: [Growth]
incomplete: false       # true if session ended abruptly
---

## Context
One paragraph — what brought the user in, what state they were in.

## Conversation highlights
- Bullet of key exchange or insight (paraphrased, not transcript)
- Patterns the coach named and how the user responded
- Reframes that landed

## Decisions & commitments
- Concrete next actions written to which goal files
- Anything held but not written (e.g., "sit with this question")

## Open threads
- Things the user dodged, deferred, or noted to revisit
```

Coach drafts at session wrap, shows it, user can request edits before write.

## Vault edit protocol (non-Sessions edits)

Per proposed edit:

1. Coach states **what** and **where** (file + section).
2. Shows **exact diff** — surrounding context + new lines.
3. User responds `yes` / `no` / `edit: …`.
4. Only `yes` writes. `edit:` loops back to step 2.

Batched at session wrap, not per-line — the user approves a slate at once.

## Edge cases & failure modes

- **No `<current-year>.md`** — review mode offers to create one by copying
  `~/cjbackman/Templates/Annual Review.md` and adapting headings. Reflect and
  check-in modes don't need it.
- **No goals exist** — check-in mode says "you don't have any goals tracked.
  Want to switch to review mode?" instead of stalling.
- **Vault not at `~/cjbackman`** — fail loudly. No fallback magic.
- **`Sessions/` missing** — coach creates it on first session without prompting.
- **User goes off-topic** — coach lets it run a few turns, then names it and
  asks if they want to switch modes or come back.
- **Vault/conversation conflict** — e.g., goal `Status: In Progress` but user
  says they gave up. Coach names the gap and proposes a status flip.
- **Mid-session interruption** — coach writes the session log with what it has,
  marks `incomplete: true`. Pending vault edits go into Open threads, not
  written.
- **Repeated same-day invocation** — coach checks `Sessions/` for today's
  entries and references them.
- **User asks for advice the coach shouldn't give** (medical, legal,
  financial-specifics) — coach declines and points to professional resources.

## Open items deferred to implementation

- Status taxonomy: only `In Progress` observed in current goals. Coach asks
  user during first review/check-in what the full taxonomy is and adds a note
  to `vault-conventions.md`.
- Slash command installation: skill ships `coach/commands/coach.md` but
  installation into `~/.claude/commands/` is the user's call.

## Out of scope

- Proactive triggering (e.g., reminding user it's been N days). User-initiated
  only.
- Cross-vault or cross-machine sync — single vault at `~/cjbackman`.
- Mobile / non-Claude-Code surfaces.
