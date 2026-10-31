---
name: today
description: Daily triage of CJ's private Obsidian inbox. Moves new half-baked ideas, links and tools from `~/cjbackman/Inbox/` daily notes into `~/cjbackman/Personal/Backlog.md`, then suggests what to do, read and try today, steered by `Personal/Now.md` and the goal notes. Triggers on `/today`, "what should I do today", "triage my inbox", "process my inbox". Private stuff only — do not invoke for work planning.
---

# Today

Turn raw captures into a short, goal-steered list for today. Three steps: **read context → triage inbox into backlog → suggest**. Keep everything short; CJ reads this in a terminal.

## Paths

All relative to the vault `~/cjbackman/`:

| What | Path | Who writes |
|---|---|---|
| Inbox (daily notes, `YYYY-MM-DD.md`, free-form bullets) | `Inbox/` | CJ; skill only adds a `processed` property |
| Current focus | `Personal/Now.md` | CJ (skill never edits) |
| Goals | `Personal/Growth/Goals/*.md` (props: `GoalID`, `Objective`, `Key Result`, `Status`, `Date`) | CJ (skill never edits) |
| Backlog | `Personal/Backlog.md` | Skill + CJ |

## 1. Read context

1. Read `Personal/Now.md`. Its **Focus** sections define priority order. **Background** = never create tasks. **Not now** = park items, never suggest them.
2. Read frontmatter of goal notes linked from `Now.md` (for GoalID + Key Result wording). Skip the rest.
3. Read `Personal/Backlog.md`.

## 2. Triage inbox → backlog

1. List `Inbox/*.md`. Process every note **without** a `processed` property, plus today's note (it may still be growing).
2. For each bullet / line / link:
   - **Dedupe** against the backlog (same URL, or clearly the same idea). Already there → skip.
   - **URLs:** fetch with WebFetch to get a real title + one-line summary. Fetch fails or login-walled (LinkedIn often is) → use the URL slug + CJ's own words, mark `(unread)`.
   - **Classify** into one section:
     - `Read` — article, post, paper, video
     - `Try` — tool, skill, plugin, library, model, workflow to test
     - `Build` — project or prototype idea
     - `Do` — plain errand / task
   - **Tag goal:** `G26.5` etc. if it clearly serves a Focus goal; `job-prep` for new-job items; `—` if none. Don't stretch to force a match.
   - **Size:** S (<30 min), M (an evening), L (a weekend+).
   - **Due date:** if CJ wrote one, add `due YYYY-MM-DD`. If the item is time-sensitive (booking, travel, gift, event, deadline, anything that gets worse or impossible later) and has no date → don't guess one; list it under "Needs a date" in the output.
   - Line format: `- [ ] Title — summary · goal · size · due YYYY-MM-DD (optional) · added YYYY-MM-DD · from [[YYYY-MM-DD]]`
   - Work-only items → don't add; list them under "Skipped" in the output.
   - Ambiguous fragment you can't interpret → add to `Do` as-is with `(unclear)`; don't guess.
3. Append new items to the right sections of `Backlog.md`. Never delete or rewrite CJ's existing lines. Move checked `[x]` items from other sections into `## Done` (keep them as they are).
4. Add `processed: <today>` to the frontmatter of every processed inbox note **except today's**. Never edit the bullets themselves.

## 3. Suggest today

Pick from the whole backlog (not just new items). Output in chat, nothing written to the vault except due dates CJ gives in reply (see below):

```
## Today — <weekday YYYY-MM-DD>

**Due soon** (only if any)
- [ ] <item> — due <date> (<n> days)

**Do** (max 3)
- [ ] <item> — <why: goal / unblocks / quick win>

**Read** (1)
- <item> — <why>

**Try** (0–1, only if there's time)
- <item>

**French** — one small concrete action (while French is a Focus)

---
Inbox: N new → Read a · Try b · Build c · Do d · Skipped s
Stale: <items >4 weeks old, untouched — keep or drop?> (only if any)
Needs a date: <time-sensitive items without `due` — when should this be done by?> (only if any)
```

If CJ answers with dates, write `due YYYY-MM-DD` into those backlog lines (only edit to an existing line the skill makes).

Selection rules:
- **Due dates override Focus order.** Surface an item under "Due soon" once it's within its lead time: S → 3 days, M → 7 days, L → 14 days before `due`. Overdue items always show, marked **overdue**. Due-soon items don't count toward the 3 Do slots.
- Order by `Now.md` Focus order, then size: prefer S/M on weekdays, allow L on Fri–Sun.
- Prefer items carried over from earlier days over shiny new ones; say "carried over" when so.
- Job-prep: until `Now.md` defines it, only suggest captured job-prep items, plus a one-time nudge to schedule the scoping session if none exists.
- Never suggest Background or Not-now items.
- Empty backlog and inbox → say so in one line and suggest the top Focus's next step.
- Every suggestion gets a one-clause *why*. No item without a why.

## Don'ts

- Don't edit `Now.md`, goal notes, or inbox bullets.
- Don't add structure to inbox notes (no headings, no templates) — the `processed` property is the only thing written there.
- Don't touch `Personal/TODO.md` or anything under `Work/`.
