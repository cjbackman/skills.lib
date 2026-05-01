# Flashcards skill — design spec

**Date:** 2026-05-01
**Status:** Approved, pending implementation plan
**Skill name:** `flashcards`
**Repo location:** `flashcards/` at repo root

## Purpose

A skill for turning arbitrary text — Obsidian vault notes or pasted snippets — into high-quality Anki flashcards. The skill encodes the principles from Andy Matuschak's prompt-writing notes, Borretti's "Effective Spaced Repetition", and SuperMemo's twenty rules: atomic prompts, minimum information, multiple angles per concept, no enumerations, low interference. Output is a single TSV file in `~/Downloads/` formatted for direct import into Anki using **stock Basic and Cloze note types** (no custom note type required).

The skill is interactive and two-pass: it extracts candidate atoms from the source, has the user confirm which to make cards from, drafts cards, audits them silently against a rule checklist, and only then writes the file.

## Sources of truth

| Resource | Role in skill |
|---|---|
| <https://andymatuschak.org/prompts/> | Multiple prompts per concept, no leak, test understanding not trivia |
| <https://borretti.me/article/effective-spaced-repetition> | Personal context, source attribution, atomicity |
| <https://www.supermemo.com/en/blog/twenty-rules-of-formulating-knowledge> | Minimum information, no enumeration, closed answers, low interference |
| <https://docs.ankiweb.net/importing/intro.html> | TSV import format, header lines, mixed note types |

## Vault and host conventions

Vault root: `~/cjbackman` (convention only; no hardcoded absolute paths beyond this).
Output directory: `~/Downloads/` (with `/tmp/` fallback if unwritable).

## Architecture

Approach: short engine prompt, dense rule reference, small writer script.

```
flashcards/
├── SKILL.md                       # workflow: two-pass loop, decision points
├── README.md                      # install + usage
├── commands/
│   └── flashcards.md              # /flashcards slash command wrapper
├── references/
│   ├── principles.md              # 20 rules + Borretti + Andy condensed; audit checklist
│   ├── atom-extraction.md         # tier definitions + extraction prompt template
│   └── card-drafting.md           # cards-per-atom heuristics + drafting prompt template
├── scripts/
│   └── write_anki_tsv.py          # JSON intermediate → Anki TSV
└── tests/
    └── fixtures/
        ├── sample-cards.json      # writer script input fixture
        └── sample-cards.expected.txt  # expected output
```

`SKILL.md` stays short and procedural. `references/` hold the dense reading the engine consults during each pass. `scripts/write_anki_tsv.py` handles TSV escaping and header generation.

## Anki output model

**Note types:** stock Anki `Basic` and `Cloze`. No custom note types. No one-time Anki setup required beyond having Anki installed.

**Source attribution:** native types have no Source field, so source is appended as an HTML footer inside the existing `Back` (Basic) or `Back Extra` (Cloze) field:

```
<hr><small><i>Source: ~/cjbackman/Reading/foo.md</i></small>
```

For pasted text, the source string is `pasted YYYY-MM-DD`.

**TSV format:**

```
#separator:tab
#html:true
#notetype column:1
#deck column:2
#tags column:5
```

5 columns:

| Column | Basic row | Cloze row |
|---|---|---|
| 1 — notetype | `Basic` | `Cloze` |
| 2 — deck | user-supplied (e.g. `Reading`) | same |
| 3 — field 1 | Front | Text (with `{{c1::…}}` markers) |
| 4 — field 2 | Back + source footer | Back Extra + source footer |
| 5 — tags | space-separated | space-separated |

**Filename:** `~/Downloads/flashcards-<source-stem-or-paste>-YYYYMMDD-HHMMSS.txt`. Timestamp avoids re-run collisions; `-2`, `-3` suffix appended on the rare exact-second collision.

**Escaping (handled by `write_anki_tsv.py`):**
- Literal tabs in field bodies → 4 spaces.
- Literal newlines inside a field → `<br>` (valid because `#html:true`).
- Tags with embedded spaces → split into multiple tags (Anki tags cannot contain spaces).

## Invocation

User runs `/flashcards [arg]`. Resolution rules:

| Arg shape | Behavior |
|---|---|
| (no arg) | Skill prompts: "Paste text or give a path." Waits for next message. |
| Absolute path or `~/...` | Read file directly. |
| Vault-relative (no leading `/` or `~`), e.g. `Reading/foo.md` | Resolve under `~/cjbackman/`. |
| Multiple spaces / lines / no resolvable path | Treat as inline pasted text. |
| Vault path resolves to missing file | Show resolved path; ask user to confirm or correct. |
| Vault shorthand matches multiple files | Show candidates; user picks. |

## Two-pass workflow

### Pass 1 — atom extraction

1. Skill loads source text into context.
2. Loads `references/atom-extraction.md` and `references/principles.md`.
3. Drafts atoms, each tagged `core` / `supporting` / `detail`. An atom is one to two sentences capturing one testable claim, definition, or mechanism.
4. Prints atoms in chat as a numbered list, grouped by tier:
   ```
   CORE
   1. [claim]
   2. [claim]
   SUPPORTING
   3. [claim]
   DETAIL
   4. [claim]
   ```
5. Skill says: *"Default approves CORE only. Reply with adjustments — for example: 'add 5, 7; drop 2; promote 9 to core'. Or 'looks good'."*
6. User replies. Skill confirms the final atom set + tier assignments.

**Tier definitions (in `references/atom-extraction.md`):**
- **core** — load-bearing claims, the central thesis, mechanisms named in headings or topic sentences.
- **supporting** — definitions, examples, and counterexamples that illuminate core atoms.
- **detail** — specifics (numbers, names, dates) that may be worth memorizing only if the user opts in.

### Pass 2 — card drafting

1. Loads `references/card-drafting.md`.
2. For each approved atom, decides card count:
   - Atomic definition → 1 card.
   - Multi-part mechanism → 2-5 cards covering different angles (forward, backward, key-term cloze, application/example).
3. Prints a **count plan** before drafting:
   ```
   Atom 1 → 1 cloze
   Atom 2 → 3 cards (1 basic, 2 cloze)
   …
   Total: 14 cards. OK or adjust?
   ```
4. After user approves the count plan (or supplies adjustments like "atom 2 → 1 card; atom 5 → skip"), drafts the cards.
5. Runs **silent audit** (see Audit checklist) against each draft. Failed cards are revised once. Cards that fail twice are dropped and logged.
6. Prints the final card set in chat, grouped by atom, numbered globally:
   ```
   Atom 1 (core): "Effective spaced repetition requires atomic prompts."
     1. [Basic] Q: What does effective SR require? | A: Atomic prompts.
   Atom 2 (core): …
     2. [Cloze] {{c1::Spacing effect}} … | Extra: …
   ```
7. Skill says: *"Reply with edits ('drop 4; rewrite 7 as: …'; or 'looks good')."*

### Output stage

1. Skill prompts: *"Deck name?"* (no default — user supplies per run).
2. Skill suggests 3-6 tags inferred from content (e.g. `spaced-repetition memory borretti`). User accepts or edits.
3. Skill builds a JSON intermediate containing all approved cards plus deck and tags.
4. Skill calls `scripts/write_anki_tsv.py <json>` which writes the TSV to `~/Downloads/`.
5. Skill prints the final path and a one-line import instruction:
   *"Anki → File → Import → select file."*

## Audit checklist (`references/principles.md`)

Each draft card is checked silently against these rules. Cards that fail are revised once; if the second draft still fails, the card is dropped and logged.

1. **Atomic.** One fact per card. *(SuperMemo #4, Borretti)*
2. **Minimum information.** Shortest form that still tests the concept. *(SuperMemo #3)*
3. **No enumeration.** Lists/sets become individual cards or cloze deletions; never "list the 5 X". *(SuperMemo #5-6, Andy)*
4. **No leak.** Question doesn't contain or strongly hint the answer. *(Andy, Borretti)*
5. **Closed answer.** Answer is unambiguous, single-valued. *(SuperMemo #2)*
6. **Personal context.** Card mentions the source-specific framing if needed for disambiguation. *(Borretti)*
7. **Low interference.** Cards in the same batch don't share near-identical fronts that produce wrong-but-plausible answers. *(SuperMemo #11, Andy)*
8. **Test understanding, not trivia.** Prefer "why does X?" over "in year Y" unless the date is the point. *(Andy)*

After Pass 2, the skill prints a short drop log if anything was dropped:

```
Dropped 2 cards (audit failures):
- Atom 4 draft 1: enumeration (5-item list, couldn't atomize cleanly)
- Atom 7 draft 1: ambiguous answer
```

User can override drops by asking the skill to re-include them.

## Edge cases & error handling

**Input:**
- File not found → show resolved path, ask user to confirm or correct.
- Vault shorthand ambiguous → show candidates, user picks.
- Empty input → tell user, exit cleanly.
- Very long input (~30k+ tokens) → skill warns: *"Input large. Process whole or split by section?"* If split, user picks sections; runs Pass 1 per section, then merges atom lists before Pass 2.

**Pass 1:**
- User rejects all atoms → skill exits cleanly. No file written.
- Atom approval ambiguous ("drop a few") → skill asks which.

**Pass 2:**
- All cards for an atom fail audit twice → atom is dropped, logged. Skill notes which atoms produced zero cards.
- Cloze draft has no `{{c1::…}}` markers → audit catches; skill revises to add markers, or downgrades the card to Basic.

**Output:**
- `~/Downloads/` missing or unwritable → skill writes to `/tmp/` and prints the actual path.
- Filename collision (timestamp matches) → append `-2`, `-3`.
- Empty card set after all reviews/audits → don't write file; tell user.

**Re-run behavior:** stateless. Each run is fresh; no memory of previously generated cards. User responsible for de-duping at Anki side. Anki dedupes by first field on import by default.

**Tag/deck validation:**
- Deck name with `::` (Anki sub-deck separator) → preserved as-is, valid.
- Tag with spaces → split into multiple tags.

## Verification plan

Skill is mostly prompt + small script. Verification = manual smoke tests + a script unit check.

**Manual smoke tests (run after build):**
1. **File input, vault shorthand.** `/flashcards Reading/<some-existing-note>.md` → completes Pass 1 + 2 → file appears in `~/Downloads`.
2. **Absolute path.** `/flashcards ~/cjbackman/Reading/<file>.md` → same.
3. **No arg + paste.** `/flashcards` → paste a 3-paragraph snippet → completes.
4. **Missing file.** `/flashcards Reading/nope.md` → graceful error, asks for clarification.
5. **Reject all atoms.** Skill exits cleanly, no file written.
6. **Anki import.** Import the produced `.txt` into a test deck → verify Basic + Cloze rows render correctly, tags appear, source footer shows.

**Script unit check (`scripts/write_anki_tsv.py`):**
- `tests/fixtures/sample-cards.json` contains mixed Basic + Cloze + tags + source.
- Run script → assert output matches `tests/fixtures/sample-cards.expected.txt` (header lines, column order, escaping).
- Edge cases in fixture: card body with literal tab, with newline, with HTML, empty tag list, Cloze without `{{c1::}}` (must fail validation in the script).

**Audit rule check (manual):**
- Construct a deliberate violation card per rule (enumeration, leak, ambiguity, etc.) and run skill → verify audit catches and revises or drops.

No CI hookup; tests run locally when changes are made.

## Out of scope

- `.apkg` generation via `genanki` (deferred; current TSV approach has zero Python dependencies beyond stdlib).
- Custom Anki note types or styling.
- Card scheduling, FSRS tuning, deck management — Anki handles after import.
- Re-run de-duplication.
- Multi-language deck conventions.
- Image/audio/cloze-with-image support (TSV format supports it; first version is text-only).
