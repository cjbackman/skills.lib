---
name: inbox
description: Review CJ's private Obsidian inbox together with him. Collects every unprocessed note in `~/cjbackman/Inbox/` (except today's), walks the captures one item or theme at a time with a proposed classification, and writes agreed items to `~/cjbackman/Personal/Backlog.md`. Marks notes `processed` when done. Triggers on `/inbox`, "triage my inbox", "process my inbox", "review my inbox".
---

# Inbox

Review new captures with CJ and decide on each one together. This is a conversation, not batch processing: propose, let CJ decide, then write. Keep turns short because CJ reads them in a terminal.

## Paths

All relative to the vault `~/cjbackman/`:

| What | Path | Who writes |
|---|---|---|
| Inbox (daily notes, `YYYY-MM-DD.md`, free-form bullets) | `Inbox/` | CJ; skill only adds a `processed` property |
| Current focus | `Personal/Now.md` | CJ (skill never edits) |
| Goals | `Personal/Growth/Goals/*.md` (props: `GoalID`, `Objective`, `Key Result`, `Status`, `Date`) | CJ (skill never edits) |
| Backlog | `Personal/Backlog.md` | Skill + CJ |

## 1. Gather

1. Read `Personal/Now.md` (Focus sections = priority order; Background / Not now = never tag toward them) and the frontmatter of goal notes linked from it, for tagging.
2. Read `Personal/Backlog.md` for dedupe.
3. List `Inbox/*.md`. Collect every note **without** a `processed` property, **excluding today's note** (it may still be growing; it gets picked up on a later run).
4. Nothing to review → say "Inbox clear" in one line and stop.
5. Fetch URLs up front with WebFetch to get a real title and a one-line summary. If the fetch fails or the page is behind a login (LinkedIn often is), use the URL slug and CJ's own words, and mark the item `(unread)`.

## 2. Overview

One short block: how many notes (date range), how many items, and the themes you spotted (e.g. "3 items on agent tooling, 2 on running"). Then start the walk-through.

## 3. Walk through, one at a time

Go item by item in date order. When several items clearly share a theme, group them and handle them as one unit.

Each turn shows:

```
[n/M] <item text or theme> — from [[YYYY-MM-DD]]
Proposal: <section> · <goal tag> · <size> — <one-line why>
```

- **Section:** `Read` (article, post, paper, video) · `Try` (tool, skill, plugin, library, model, workflow) · `Build` (project or prototype idea) · `Do` (errand / task).
- **Goal tag:** `G26.5` etc. if it clearly serves a Focus goal; `job-prep` for new-job items; `—` if none. Don't force a match.
- **Size:** S (<30 min), M (an evening), L (a weekend or more).
- **Dupe of a backlog line** → propose `skip (dupe of: <line>)` or `merge`.
- **Work item** → raise it like any other, flagged `work`, and discuss with CJ how to handle it. Never write it to the personal backlog unless CJ says to.
- **Ambiguous fragment** → say you can't read it and ask; don't guess.
- **Time-sensitive item** (booking, gift, event, deadline) with no date → ask for a due date as part of the proposal.

CJ replies with one of these:
- **ok**: add as proposed
- **edit**: change the section, tag, size or wording, then add
- **drop**: don't add
- **discuss**: talk it through, then decide
- **merge**: fold into an existing backlog line (CJ confirms the new wording)

Accept loose answers ("yes", "nah", "make it a Try") and infer the decision. Ask only if a reply is genuinely unclear.

## 4. Write as you go

After each decision, not at the end, so stopping halfway loses nothing:

- Append to the right section of `Backlog.md`:
  `- [ ] Title — summary · goal · size · due YYYY-MM-DD (optional) · added YYYY-MM-DD · from [[YYYY-MM-DD]]`
- Never delete or rewrite CJ's existing lines. The exception is a `merge` CJ approved.
- Once **every** item in an inbox note is decided, add `processed: <today>` to that note's frontmatter. Never edit the bullets themselves.

## 5. Close

One line: `Added a (Read x · Try y · Build z · Do w) · dropped d · work items: <how handled> · notes marked: n`.

## Don'ts

- Don't plan the day or suggest what to do next. This skill is triage only.
- Don't edit `Now.md`, goal notes, or inbox bullets. Don't add structure to inbox notes; the `processed` property is the only thing written there.
- Don't touch `Personal/TODO.md` or anything under `Work/` unless CJ explicitly says so while discussing a work item.
