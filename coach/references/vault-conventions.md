# Vault conventions

The coach skill assumes the user's Obsidian vault is at `~/cjbackman`. All paths in this skill use `~/cjbackman/...`. If the vault is missing, fail loudly — do not invent fallback paths.

## Paths

| Path | Purpose |
|---|---|
| `~/cjbackman/Personal/Growth/<year>.md` | Annual review for that year |
| `~/cjbackman/Personal/Growth/Goals/*.md` | One file per goal, with frontmatter |
| `~/cjbackman/Personal/Growth/Goals/Goals.base` | Obsidian Bases config for goal queries |
| `~/cjbackman/Personal/Growth/Sessions/` | Session logs (created on first use) |
| `~/cjbackman/Templates/Annual Review.md` | Canonical structure for review mode |
| `~/cjbackman/Zettelkasten/Permanent/Life Changing Questions.md` | Depth-question bank for review mode |

## Goal file frontmatter

Existing convention to preserve. Do not change field names or casing.

```yaml
---
base: Goals.base
Date: 2026-09-30        # target date (ISO)
GoalID: G26.3           # G<YY>.<n>, scanned from existing goal files
Objective: Improve my French
Key Result: French A2 certificate acquired
Dimensions:             # subset of Wheel of Life dimensions
  - Growth
Status:
  - In Progress
---
```

**Wheel of Life dimensions (fixed set):** Health, Wealth, Play, Relationships, Work, Growth.

**Status taxonomy:** only `In Progress` has been observed in existing goals. The full taxonomy is unknown. On first review or check-in session, ask the user for the full set (e.g., `Done`, `Abandoned`, `On Hold`) and use those values for the rest of that session. If the user wants the taxonomy persisted, propose updating this file as a normal vault edit.

## Goal filenames

Title Case with spaces, e.g., `Learn French.md`, `AI acumen.md`. Match the user's existing convention; do NOT kebab-case.

## Auto-incrementing GoalID

When creating a new goal, scan `~/cjbackman/Personal/Growth/Goals/*.md` for `GoalID: G<YY>.<n>` values where `<YY>` matches the current year's last two digits. The new goal's ID is `G<YY>.<max+1>`. If no goals exist for that year, start at `G<YY>.1`.

## Session log format

Path: `~/cjbackman/Personal/Growth/Sessions/YYYY-MM-DD-<mode>.md` (e.g., `2026-04-26-checkin.md`). If multiple sessions same day, append `-2`, `-3`, etc. before the extension (e.g., `2026-04-26-checkin-2.md`).

Example session log structure (the coach reproduces these sections in every session log):

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

The coach drafts this at session wrap, shows it to the user, and writes after approval (or with edits if requested).

## Vault edit protocol

For every proposed edit to a non-`Sessions/` file:

1. State **what** and **where**: file path + section.
2. Show the **exact diff** — surrounding context + new lines. Don't dump whole files.
3. User responds `yes` / `no` / `edit: …`.
4. Only `yes` writes. `edit:` loops back to step 2.

Batch edits at session wrap, not per-line. The user approves a slate at once.
