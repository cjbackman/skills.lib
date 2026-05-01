---
name: flashcards
description: Generate high-quality Anki flashcards from any text source — Obsidian vault notes or pasted snippets. Two-pass workflow extracts atoms (tiered core/supporting/detail), user confirms, drafts Basic + Cloze cards, runs a silent audit against principles, then writes a TSV to ~/Downloads. Triggers on /flashcards, "make flashcards from this", "generate Anki cards from this text", or "/flashcards <path>". Do not invoke for general writing tasks, summarization, or non-flashcard work.
---

# Flashcards

Turn source text into high-quality Anki flashcards. The skill is interactive and two-pass: extract atoms, confirm, draft cards, audit, write a TSV file the user imports into Anki.

Read this entire file before responding. The reference files in `references/` are loaded only when the relevant pass runs.

## Invocation

This skill is explicit-only. Triggers:

- `/flashcards [arg]` (slash command in `commands/flashcards.md`)
- Explicit asks: "make flashcards from this", "generate Anki cards from this text"

Do not auto-trigger on casual phrasing.

## Input resolution

| Arg shape | Behavior |
|---|---|
| (no arg) | Prompt: "Paste text or give a path." Wait for next message. |
| Absolute path or `~/...` | Read file directly. |
| Vault-relative (no leading `/` or `~`), e.g. `Reading/foo.md` | Resolve under `~/cjbackman/`. |
| Multiple spaces / lines / no resolvable path | Treat as inline pasted text. |

Edge cases:
- Path resolves to missing file → show resolved path, ask user to confirm or correct.
- Vault shorthand matches multiple files → show candidates, user picks.
- Empty input → tell user, exit cleanly. No file written.

For source attribution: file input uses the resolved path; pasted text uses `pasted YYYY-MM-DD` (today).

## Workflow

### Pass 1 — atom extraction

1. Read source into context. If size > ~30k tokens (~120k chars), ask user: "Process whole or split by section?" Apply `references/atom-extraction.md` long-input handling.
2. Load `references/atom-extraction.md` and `references/principles.md`.
3. Extract atoms tagged `core` / `supporting` / `detail` per the rules in `atom-extraction.md`.
4. Print numbered list grouped by tier (numbering global across tiers).
5. Prompt:

   > Default approves CORE only. Reply with adjustments — for example: "add 5, 7; drop 2; promote 9 to core". Or "looks good".

6. Apply adjustments. Confirm final atom set + tier assignments.
7. If no atoms approved: tell user, exit cleanly. No file written.

### Pass 2 — card drafting

1. Load `references/card-drafting.md`.
2. For each approved atom, decide card count + types per the heuristics. Print **count plan**:
   ```
   Atom 1 → 1 cloze
   Atom 2 → 3 cards (1 basic, 2 cloze)
   Total: <N> cards. OK or adjust?
   ```
3. Apply user adjustments to count plan (e.g. "atom 2 → 1 card; atom 5 → skip"), then draft cards.
4. Run silent audit per `references/principles.md`. Revise failures once; drop on second failure.
5. Print final cards in chat (without source footer for readability), grouped by atom, numbered globally.
6. Print drop log if anything was dropped:
   ```
   Dropped <N> cards (audit failures):
   - Atom <N> draft 1: <rule> (<reason>)
   ```
7. Prompt: "Reply with edits ('drop 4; rewrite 7 as: …'; or 'looks good')."
8. Apply user edits.

### Output stage

1. Prompt: "Deck name?" (no default — user supplies per run).
2. Suggest 3-6 tags inferred from content. Show: "Suggested tags: <list>. Accept, edit, or replace."
3. Build the JSON intermediate per the schema in `references/card-drafting.md`.
4. Write the JSON to a temp file (e.g. `/tmp/flashcards-<unix-ts>.json`).
5. Determine the skill directory (the absolute path to the directory containing this `SKILL.md`). Run:
   ```
   python3 <skill-dir>/scripts/write_anki_tsv.py ~/Downloads/flashcards-<source-stem>-YYYYMMDD-HHMMSS.txt < /tmp/flashcards-<unix-ts>.json
   ```
6. If `~/Downloads/` is unwritable, fall back to `/tmp/` and print the actual path.
7. Print:
   > Wrote <N> cards to <path>. Anki → File → Import → select file.

### Filename construction

`<source-stem>` is:
- File input: input filename without directory or extension; spaces replaced with `-`.
- Pasted text: `pasted`.

Timestamp format: `YYYYMMDD-HHMMSS`. On exact-second collision (rare), append `-2`, `-3`.

## Edge cases

- **All cards for an atom fail audit twice** → atom dropped, logged. Note in the drop log which atoms produced zero cards.
- **Cloze draft has no `{{c1::...}}` markers** → audit catches; revise to add markers, or downgrade card to Basic.
- **`~/Downloads/` missing or unwritable** → write to `/tmp/`, print actual path.
- **Empty card set after edits** → don't write file; tell user.
- **User rejects all atoms in Pass 1** → exit cleanly.
- **Re-runs are stateless** — no memory of prior generations. User dedupes at Anki side (Anki dedupes by first field on import by default).
- **Tag with spaces** — passed through; the writer script splits into multiple tags.
- **Deck name with `::`** — preserved (Anki sub-deck separator, valid).

## Files in this skill

- `SKILL.md` (this file) — engine
- `references/principles.md` — 8 audit rules, source footer format, audit procedure
- `references/atom-extraction.md` — Pass 1: tiers, extraction prompt, output format, long-input handling
- `references/card-drafting.md` — Pass 2: cards-per-atom heuristics, type selection, JSON intermediate schema
- `scripts/write_anki_tsv.py` — JSON → Anki TSV writer
- `tests/fixtures/sample-cards.json`, `sample-cards.expected.txt` — writer script test fixtures
- `commands/flashcards.md` — slash command wrapper
- `README.md` — install + usage
