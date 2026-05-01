# Flashcards Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `flashcards` skill — a two-pass interactive workflow that turns arbitrary text (Obsidian notes or pasted snippets) into Anki-importable TSV using stock Basic + Cloze note types.

**Architecture:** Single skill at `flashcards/` in repo root, matching the convention of `coach/`, `blog-spar/`. Short engine in `SKILL.md`; dense reading (atom-extraction rules, drafting heuristics, audit rules) in `references/`; small Python script in `scripts/` handles TSV escaping; slash command wrapper + README round it out. The only executable code is `scripts/write_anki_tsv.py` (Python stdlib only).

**Tech Stack:** Markdown skill files + Python 3 (stdlib only). No external dependencies. Verification = manual smoke tests + a script unit test using a fixture pair.

**Spec reference:** `docs/specs/2026-05-01-flashcards-skill-design.md`

---

## File Structure

```
flashcards/
├── SKILL.md                       # engine: workflow, decisions, edge cases
├── README.md                      # install, usage, file map
├── commands/
│   └── flashcards.md              # /flashcards slash command wrapper
├── references/
│   ├── principles.md              # 8 audit rules + source footer format
│   ├── atom-extraction.md         # Pass 1: tiers + extraction prompt
│   └── card-drafting.md           # Pass 2: cards-per-atom + JSON schema
├── scripts/
│   └── write_anki_tsv.py          # JSON intermediate → Anki TSV
└── tests/
    └── fixtures/
        ├── sample-cards.json
        └── sample-cards.expected.txt
```

Each file has one responsibility. `SKILL.md` is short and procedural; references are loaded only when their pass runs; the script encapsulates the only place TSV escaping happens.

**Build order is bottom-up:** references first (the dense reading the engine consults), then writer script with TDD, then engine, then slash command, then README, then smoke test.

---

## Task 1: `references/principles.md`

**Files:**
- Create: `flashcards/references/principles.md`

The audit checklist Pass 2 runs against. 8 rules with examples, plus the audit procedure and the source footer spec.

- [ ] **Step 1: Create `flashcards/references/principles.md` with the following content**

````markdown
# Principles

These are the rules the skill checks each draft card against. Drawn from:

- Andy Matuschak — <https://andymatuschak.org/prompts/>
- Borretti — <https://borretti.me/article/effective-spaced-repetition>
- SuperMemo's twenty rules — <https://www.supermemo.com/en/blog/twenty-rules-of-formulating-knowledge>

Apply during the silent audit in Pass 2. Each card is checked against every rule. Failed cards are revised once. Cards that fail twice are dropped and logged.

## The 8 audit rules

### 1. Atomic
One fact per card. *(SuperMemo #4, Borretti)*

- ✓ Q: "What does the spacing effect predict?" A: "Recall improves when reviews are spaced apart vs. massed."
- ✗ Q: "Define spacing effect and testing effect." (two facts)

### 2. Minimum information
Shortest form that still tests the concept. *(SuperMemo #3)*

- ✓ Front: "Spacing effect" / Back: "Recall improves with spaced vs. massed reviews."
- ✗ Front: full paragraph from source. Trim until only the testable pivot remains.

### 3. No enumeration
Lists/sets become individual cards or cloze deletions; never "list the 5 X". *(SuperMemo #5-6, Andy)*

- ✓ Cloze: "Wheel of Life dimensions include {{c1::Health}}, {{c2::Wealth}}, {{c3::Play}}, …"
- ✗ Q: "List the 6 Wheel of Life dimensions." (set recall, brittle)

### 4. No leak
Question doesn't contain or strongly hint the answer. *(Andy, Borretti)*

- ✓ Q: "What error does spaced repetition exploit?" A: "The forgetting curve."
- ✗ Q: "What forgetting curve does spaced repetition exploit?" (answer in question)

### 5. Closed answer
Answer is unambiguous, single-valued. *(SuperMemo #2)*

- ✓ Q: "What's the half-life formula in FSRS?" A: specific formula.
- ✗ Q: "Why is spaced repetition effective?" (open-ended; many valid answers).

### 6. Personal context
Card mentions the source-specific framing if needed for disambiguation. *(Borretti)*

- ✓ Q: "In Borretti's effective-SR essay, what does 'atomic' mean?" A: …
- Necessary when the term has different meanings across sources.

### 7. Low interference
Cards in the same batch don't share near-identical fronts. *(SuperMemo #11, Andy)*

If two cards have fronts that differ only in one word, recall confuses them. Rewrite to make fronts distinct.

### 8. Test understanding, not trivia
Prefer "why does X?" over "in year Y" unless the date is the point. *(Andy)*

- ✓ Q: "Why does cloze deletion work better than open recall for definitions?"
- ✗ Q: "What year did Ebbinghaus publish his memory study?" (unless dates matter to the source)

## Audit procedure

For each draft card:

1. Check against rules 1-8.
2. If any rule fails: revise the card with the failed rule as guidance. Re-check.
3. If second draft still fails: drop the card. Record `Atom <N> draft 1: <rule that failed> — <one-line reason>`.

After Pass 2 final card list, print the drop log if anything was dropped:

```
Dropped <N> cards (audit failures):
- Atom 4 draft 1: enumeration (5-item list, couldn't atomize cleanly)
- Atom 7 draft 1: ambiguous answer
```

The user may override drops by asking the skill to re-include specific dropped cards.

## Source footer

All cards have source attribution as an HTML footer in the `Back` field (Basic) or `Back Extra` field (Cloze). The writer script appends it; do not include in JSON `back` / `extra`.

Format:

```
<hr><small><i>Source: <source-string></i></small>
```

`<source-string>` is:
- File input: the resolved file path (e.g. `~/cjbackman/Reading/foo.md`).
- Pasted text: `pasted YYYY-MM-DD` (today's date).
````

- [ ] **Step 2: Verify**

Run: `head -5 flashcards/references/principles.md`
Expected: shows `# Principles` heading and the first lines of intro.

- [ ] **Step 3: Commit**

```bash
git add flashcards/references/principles.md
git commit -m "Add flashcards principles + audit checklist reference"
```

---

## Task 2: `references/atom-extraction.md`

**Files:**
- Create: `flashcards/references/atom-extraction.md`

Pass 1 reference — what an atom is, tier definitions, extraction prompt, output format, long-input handling.

- [ ] **Step 1: Create `flashcards/references/atom-extraction.md` with the following content**

````markdown
# Atom extraction (Pass 1)

Extract atoms from the source text. An atom is one to two sentences that capture **one testable claim, definition, or mechanism**. Atoms are the unit of decision: the user approves which become cards in Pass 2.

## What counts as an atom

- A **claim**: "Spaced repetition increases long-term retention vs. massed practice."
- A **definition**: "An atomic prompt tests a single fact."
- A **mechanism**: "FSRS adjusts the next-review interval based on the prior recall difficulty."
- A **counterexample or limit**: "SR fails when prompts test enumerations."

## What is NOT an atom

- Section headings without content
- Filler / connective sentences ("In this article, we'll see…")
- The source's name or URL
- Lists in their unbroken form (decompose into per-item atoms)
- Already-handled atoms paraphrased differently

## Tiers

Tag each atom with one of:

| Tier | What goes here |
|---|---|
| `core` | Load-bearing claims, central thesis, mechanisms named in headings or topic sentences. The user almost certainly wants cards from these. |
| `supporting` | Definitions, examples, counterexamples that illuminate a core atom. Useful but optional. |
| `detail` | Specifics — numbers, names, dates, edge cases — only worth memorizing if the user opts in. |

Default: only `core` atoms become cards. The user opts in to `supporting` / `detail` per run.

## Density targets

- **3-7 core** per ~1000 words.
- **0-15 supporting** per ~1000 words.
- **0-10 detail** per ~1000 words.

Not hard limits — let the source dictate. A dense technical paper exceeds; a casual note may not reach the floor.

## Output format

```
CORE
1. [atom in 1-2 sentences]
2. [atom in 1-2 sentences]
...

SUPPORTING
N. [atom]
N+1. [atom]
...

DETAIL
M. [atom]
...
```

Numbering is **global** across tiers — each atom has a unique number from 1 to total.

After the list, print this exact prompt:

> Default approves CORE only. Reply with adjustments — for example: "add 5, 7; drop 2; promote 9 to core". Or "looks good".

## Long input handling

If the source is larger than ~30k tokens (rough heuristic: ~120k chars), warn:

> Input is large (~<N> tokens). Process whole or split by section?

If the user picks split:

1. Identify section boundaries (headings, blank-line-separated chunks).
2. List sections with index + first-line preview.
3. User picks which sections to extract from.
4. Run atom extraction per selected section.
5. Merge atom lists with continuous numbering before showing the user.

## Path resolution for source attribution

The source string used downstream (in card footers) should be the **resolved** path — e.g. `~/cjbackman/Reading/foo.md`, not the user's vault-relative shorthand `Reading/foo.md`. For pasted text, use `pasted YYYY-MM-DD` (today's date).
````

- [ ] **Step 2: Verify**

Run: `wc -l flashcards/references/atom-extraction.md`
Expected: at least 60 lines.

- [ ] **Step 3: Commit**

```bash
git add flashcards/references/atom-extraction.md
git commit -m "Add atom extraction reference (Pass 1)"
```

---

## Task 3: `references/card-drafting.md`

**Files:**
- Create: `flashcards/references/card-drafting.md`

Pass 2 reference — cards-per-atom heuristics, type selection, cloze marker rules, JSON intermediate schema, chat output format.

- [ ] **Step 1: Create `flashcards/references/card-drafting.md` with the following content**

````markdown
# Card drafting (Pass 2)

For each approved atom, decide how many cards and what type, draft them, and run the silent audit (see `principles.md`).

## Cards per atom

Decide based on atom shape:

| Atom shape | Card count | Why |
|---|---|---|
| Single-fact definition ("X is Y") | 1 | Front: "X" → Back: "Y" or cloze. |
| Causal claim ("X causes Y") | 1-2 | Forward (X → Y); optional backward (Y caused by → X). |
| Mechanism with named parts | 2-5 | One per part + one for the whole. |
| Comparison ("X vs. Y") | 2-3 | One for each direction + one for the distinguishing axis. |
| Counterexample / limit | 1 | "When does X fail?" → counterexample. |

Skill picks the count per atom. Show a **count plan** to the user before drafting:

```
Atom 1 → 1 cloze
Atom 2 → 3 cards (1 basic, 2 cloze)
Atom 3 → 2 cards (1 basic, 1 cloze)
...
Total: <N> cards. OK or adjust?
```

User can override: *"atom 2 → 1 card; atom 5 → skip"*. Apply adjustments before drafting.

## Card type selection

| Use Basic when | Use Cloze when |
|---|---|
| Atom is a clean Q/A pair | Atom has a key term embedded in a sentence |
| Causal links ("why does X?") | Definitions where the surrounding sentence helps recall |
| Comparisons | Multi-part atoms (each part as a separate `{{cN::…}}` deletion) |
| Procedural ("how do you X?") | Lists (each item as `{{cN::…}}`) |

Mixed atoms can produce both card types. Don't force one type if the atom has both shapes.

## Cloze marker rules

- Use `{{c1::…}}`, `{{c2::…}}`, etc. for separate deletions in the same card.
- Each `cN` produces one card (Anki splits cloze cards by index).
- A single card can have multiple deletions with the **same** `cN` if they should be hidden together.
- The cloze body becomes the `Text` field; any extra context goes to `Back Extra`.
- Every Cloze card MUST contain at least one `{{c1::…}}` marker. The writer script rejects cloze cards without markers.

## Drafting steps

For each approved atom:

1. Pick card count and types per the table above.
2. Draft each card:
   - **Basic:** `Front` = question, `Back` = answer (no source footer; the writer script adds it).
   - **Cloze:** `Text` = sentence with `{{cN::…}}` markers, `Extra` = optional extra context.
3. Run audit (see `principles.md`). Revise once on failure; drop on second failure.

## Output format for chat

Group cards by atom, numbered globally:

```
Atom 1 (core): "<atom text>"
  1. [Basic] Q: <front> | A: <back without footer>
Atom 2 (core): "<atom text>"
  2. [Cloze] <text with markers> | Extra: <back-extra>
  3. [Cloze] <text with markers> | Extra: <back-extra>
...
```

The chat display **omits the source footer** for readability — it's still in the data the writer script receives.

After the list:

> Reply with edits ("drop 4; rewrite 7 as: …"; or "looks good").

## JSON intermediate schema

After user approves cards, build this JSON for the writer script. Field names are exact.

```json
{
  "deck": "Reading",
  "tags": ["spaced-repetition", "memory", "borretti"],
  "source": "~/cjbackman/Reading/borretti-sr.md",
  "cards": [
    {
      "type": "Basic",
      "front": "What does the spacing effect predict?",
      "back": "Recall improves when reviews are spaced apart vs. massed."
    },
    {
      "type": "Cloze",
      "text": "An {{c1::atomic}} prompt tests a {{c2::single}} fact.",
      "extra": ""
    }
  ]
}
```

Required fields:
- `deck` — string, deck name as the user supplied.
- `tags` — array of strings. Tags with embedded spaces will be split by the writer script.
- `source` — string, the resolved source path or `pasted YYYY-MM-DD`.
- `cards` — non-empty array.

Per-card required fields:
- `type` — `"Basic"` or `"Cloze"`.
- Basic: `front` and `back`, both non-empty.
- Cloze: `text` (non-empty, must contain at least one `{{cN::…}}` marker), `extra` (may be empty).

The writer script appends the source footer to `back` (Basic) or `extra` (Cloze, even if empty). **Do not include the footer in the JSON.**

## Filename for the writer

The skill calls the writer script with the output path:

```
~/Downloads/flashcards-<source-stem>-YYYYMMDD-HHMMSS.txt
```

`<source-stem>` is:
- File input: input filename without directory or extension; spaces → `-`.
- Pasted text: `pasted`.

On exact-second collision, append `-2`, `-3`. If `~/Downloads/` is unwritable, fall back to `/tmp/`.
````

- [ ] **Step 2: Verify**

Run: `grep -c '^##' flashcards/references/card-drafting.md`
Expected: 7 or more (each `##` heading).

- [ ] **Step 3: Commit**

```bash
git add flashcards/references/card-drafting.md
git commit -m "Add card drafting reference (Pass 2)"
```

---

## Task 4: Writer script + fixtures (TDD)

**Files:**
- Create: `flashcards/tests/fixtures/sample-cards.json`
- Create: `flashcards/tests/fixtures/sample-cards.expected.txt`
- Create: `flashcards/scripts/write_anki_tsv.py`

The only code in the skill. TDD: write the fixture pair first, write a test command that runs the script and diffs output, confirm it fails (script doesn't exist), implement the script, confirm it passes.

- [ ] **Step 1: Create input fixture `flashcards/tests/fixtures/sample-cards.json`**

```json
{
  "deck": "Reading",
  "tags": ["spaced-repetition", "memory test"],
  "source": "~/cjbackman/Reading/sample.md",
  "cards": [
    {
      "type": "Basic",
      "front": "What does the spacing effect predict?",
      "back": "Recall improves when reviews are spaced apart vs. massed."
    },
    {
      "type": "Cloze",
      "text": "An {{c1::atomic}} prompt tests a {{c2::single}} fact.",
      "extra": "Andy Matuschak emphasizes this rule."
    },
    {
      "type": "Basic",
      "front": "Line 1\nLine 2",
      "back": "Tab\there"
    }
  ]
}
```

This fixture exercises:
- Basic + Cloze rows
- Tag normalization (`memory test` → two tags `memory` + `test`)
- Newline escaping (`\n` → `<br>`)
- Tab escaping (`\t` → 4 spaces)
- Source footer appended

- [ ] **Step 2: Create expected fixture using `printf`**

`printf` with `$'...'` ANSI-C quoting is the cleanest way to embed literal tabs.

```bash
mkdir -p flashcards/tests/fixtures
printf '%s\n' \
  '#separator:tab' \
  '#html:true' \
  '#notetype column:1' \
  '#deck column:2' \
  '#tags column:5' \
  '' \
  $'Basic\tReading\tWhat does the spacing effect predict?\tRecall improves when reviews are spaced apart vs. massed.<hr><small><i>Source: ~/cjbackman/Reading/sample.md</i></small>\tspaced-repetition memory test' \
  $'Cloze\tReading\tAn {{c1::atomic}} prompt tests a {{c2::single}} fact.\tAndy Matuschak emphasizes this rule.<hr><small><i>Source: ~/cjbackman/Reading/sample.md</i></small>\tspaced-repetition memory test' \
  $'Basic\tReading\tLine 1<br>Line 2\tTab    here<hr><small><i>Source: ~/cjbackman/Reading/sample.md</i></small>\tspaced-repetition memory test' \
  > flashcards/tests/fixtures/sample-cards.expected.txt
```

- [ ] **Step 3: Verify expected file uses literal tabs**

Run: `grep -P '\t' flashcards/tests/fixtures/sample-cards.expected.txt | head -1 | cat -A`
Expected: shows `^I` markers (cat -A's representation of tab) between fields.

- [ ] **Step 4: Run the test command — verify it fails (script doesn't exist yet)**

```bash
mkdir -p flashcards/scripts
python3 flashcards/scripts/write_anki_tsv.py /tmp/flashcards-test-out.txt < flashcards/tests/fixtures/sample-cards.json
```

Expected: `python3: can't open file ... write_anki_tsv.py: [Errno 2] No such file or directory`. This is the failing test.

- [ ] **Step 5: Implement `flashcards/scripts/write_anki_tsv.py`**

```python
#!/usr/bin/env python3
"""Convert flashcards JSON intermediate to Anki-importable TSV.

Usage:
  python3 write_anki_tsv.py <output.txt> < input.json

Reads JSON from stdin; writes a TSV with Anki header lines to <output.txt>.
"""
import json
import re
import sys
from pathlib import Path


def escape_field(text: str) -> str:
    """Tabs → 4 spaces; literal newlines → <br>."""
    text = text.replace("\t", "    ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\n", "<br>")
    return text


def normalize_tags(tags):
    """Anki tags must not contain spaces. Split tags-with-spaces into multiple."""
    out = []
    for tag in tags:
        for piece in tag.split():
            if piece:
                out.append(piece)
    return out


def validate_card(card, idx):
    """Raise ValueError if card is malformed."""
    ctype = card.get("type")
    if ctype == "Basic":
        if not card.get("front") or not card.get("back"):
            raise ValueError(f"card {idx}: Basic requires non-empty front + back")
    elif ctype == "Cloze":
        text = card.get("text", "")
        if not text:
            raise ValueError(f"card {idx}: Cloze requires non-empty text")
        if not re.search(r"\{\{c\d+::", text):
            raise ValueError(f"card {idx}: Cloze missing {{cN::...}} markers")
    else:
        raise ValueError(f"card {idx}: type must be 'Basic' or 'Cloze'")


def build_source_footer(source):
    return f'<hr><small><i>Source: {source}</i></small>'


def render_row(card, deck, tags, source):
    """Build one TSV row."""
    footer = build_source_footer(source)
    if card["type"] == "Basic":
        front = escape_field(card["front"])
        back = escape_field(card["back"]) + footer
        cols = ["Basic", deck, front, back, " ".join(tags)]
    else:
        text = escape_field(card["text"])
        extra = escape_field(card.get("extra", ""))
        back_extra = (extra + footer) if extra else footer
        cols = ["Cloze", deck, text, back_extra, " ".join(tags)]
    return "\t".join(cols)


def write_tsv(payload, out_path):
    deck = payload["deck"]
    tags = normalize_tags(payload.get("tags", []))
    source = payload["source"]
    cards = payload["cards"]

    if not cards:
        raise ValueError("no cards to write")

    for i, card in enumerate(cards):
        validate_card(card, i)

    lines = [
        "#separator:tab",
        "#html:true",
        "#notetype column:1",
        "#deck column:2",
        "#tags column:5",
        "",
    ]
    for card in cards:
        lines.append(render_row(card, deck, tags, source))

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    if len(sys.argv) != 2:
        print("usage: write_anki_tsv.py <output.txt>", file=sys.stderr)
        return 2
    out_path = Path(sys.argv[1])
    payload = json.load(sys.stdin)
    write_tsv(payload, out_path)
    print(out_path, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Make script executable**

```bash
chmod +x flashcards/scripts/write_anki_tsv.py
```

- [ ] **Step 7: Run script against fixture**

```bash
python3 flashcards/scripts/write_anki_tsv.py /tmp/flashcards-test-out.txt < flashcards/tests/fixtures/sample-cards.json
```

Expected stderr: `/tmp/flashcards-test-out.txt`. Exit code 0.

- [ ] **Step 8: Diff against expected — verify it passes**

```bash
diff /tmp/flashcards-test-out.txt flashcards/tests/fixtures/sample-cards.expected.txt
```

Expected: no output (files identical). If diff prints anything, fix the script and re-run.

- [ ] **Step 9: Sanity-check validation errors**

Test that the script rejects bad cards. Run:

```bash
python3 flashcards/scripts/write_anki_tsv.py /tmp/should-not-exist.txt <<'JSON'
{
  "deck": "X",
  "tags": [],
  "source": "x",
  "cards": [
    {"type": "Cloze", "text": "no markers here", "extra": ""}
  ]
}
JSON
```

Expected: non-zero exit + traceback ending in `ValueError: card 0: Cloze missing {{cN::...}} markers`.

- [ ] **Step 10: Commit**

```bash
git add flashcards/scripts/write_anki_tsv.py flashcards/tests/fixtures/sample-cards.json flashcards/tests/fixtures/sample-cards.expected.txt
git commit -m "Add write_anki_tsv.py + fixture pair (TDD)"
```

---

## Task 5: `SKILL.md` engine

**Files:**
- Create: `flashcards/SKILL.md`

The engine. Short and procedural — references hold the dense rules.

- [ ] **Step 1: Create `flashcards/SKILL.md` with the following content**

````markdown
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
````

- [ ] **Step 2: Verify frontmatter parses**

```bash
head -6 flashcards/SKILL.md
```

Expected: shows `---`, `name: flashcards`, `description: ...`, `---`, blank line, then `# Flashcards` heading.

- [ ] **Step 3: Verify all referenced files exist**

```bash
for f in references/principles.md references/atom-extraction.md references/card-drafting.md scripts/write_anki_tsv.py tests/fixtures/sample-cards.json tests/fixtures/sample-cards.expected.txt; do
  test -f "flashcards/$f" && echo "OK $f" || echo "MISSING $f"
done
```

Expected: all `OK`. (`commands/flashcards.md` and `README.md` are created in later tasks.)

- [ ] **Step 4: Commit**

```bash
git add flashcards/SKILL.md
git commit -m "Add flashcards skill engine (SKILL.md)"
```

---

## Task 6: `commands/flashcards.md`

**Files:**
- Create: `flashcards/commands/flashcards.md`

Thin slash-command wrapper, matching the pattern in `coach/commands/coach.md`.

- [ ] **Step 1: Create `flashcards/commands/flashcards.md` with the following content**

```markdown
---
description: Generate Anki flashcards from a file path, vault shorthand, or pasted text using the flashcards skill.
---

The user has invoked the flashcards skill. Use the `flashcards` skill in this repo to run the two-pass workflow.

If the user provided an argument after `/flashcards` (a path, vault shorthand, or inline text), pass it through as the source. If not, ask whether they want to paste text or supply a path.

Do not improvise the protocol — follow `flashcards/SKILL.md` and the relevant `flashcards/references/*.md` file exactly.
```

- [ ] **Step 2: Verify**

```bash
head -3 flashcards/commands/flashcards.md
```

Expected: `---`, `description: ...`, `---`.

- [ ] **Step 3: Commit**

```bash
git add flashcards/commands/flashcards.md
git commit -m "Add /flashcards slash command wrapper"
```

---

## Task 7: `README.md`

**Files:**
- Create: `flashcards/README.md`

User-facing install + usage doc. Matches the structure of `coach/README.md`.

- [ ] **Step 1: Create `flashcards/README.md` with the following content**

````markdown
# flashcards

Generate high-quality Anki flashcards from any text — Obsidian vault notes or pasted snippets. Two-pass interactive workflow that encodes the principles from Andy Matuschak, Borretti, and SuperMemo's twenty rules.

## What it does

1. **Extract atoms** from a source text, tagged `core` / `supporting` / `detail`.
2. **You confirm** which atoms become cards.
3. **Draft cards** (Basic + Cloze, native Anki types only) with multiple angles per atom.
4. **Silent audit** against an 8-rule checklist (atomic, no leak, low interference, etc.).
5. **Write TSV** to `~/Downloads/` for direct import into Anki.

No custom Anki note types. No external dependencies — Python stdlib only.

## Resources encoded

- Andy Matuschak — <https://andymatuschak.org/prompts/>
- Borretti — <https://borretti.me/article/effective-spaced-repetition>
- SuperMemo — <https://www.supermemo.com/en/blog/twenty-rules-of-formulating-knowledge>
- Anki import format — <https://docs.ankiweb.net/importing/intro.html>

## Install

The skill itself:

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/flashcards" ~/.claude/skills/flashcards
```

The slash command (optional, lets you type `/flashcards`):

```bash
mkdir -p ~/.claude/commands
ln -s "$(pwd)/flashcards/commands/flashcards.md" ~/.claude/commands/flashcards.md
```

## Usage

In Claude Code:

- `/flashcards Reading/foo.md` — vault shorthand under `~/cjbackman/`
- `/flashcards ~/path/to/file.md` — absolute path
- `/flashcards` — then paste text in the next message

Or ask explicitly: "make flashcards from this note", "generate Anki cards from this text".

## Anki import

1. Open Anki: File → Import → select the `.txt` file from `~/Downloads/`.
2. The TSV header lines tell Anki which columns are deck, note type, and tags.
3. Cards land in the deck name you supplied. Use stock `Basic` and `Cloze` note types — no custom note type setup required.

## Vault assumption

Vault root: `~/cjbackman`. If yours lives elsewhere, edit `~/cjbackman` references in `SKILL.md` and `commands/flashcards.md`.

## Files

```
flashcards/
├── SKILL.md                       # engine: workflow, decisions, edge cases
├── README.md                      # this file
├── commands/
│   └── flashcards.md              # slash command wrapper
├── references/
│   ├── principles.md              # 8 audit rules + source footer format
│   ├── atom-extraction.md         # Pass 1: tiers + extraction prompt
│   └── card-drafting.md           # Pass 2: cards-per-atom + JSON schema
├── scripts/
│   └── write_anki_tsv.py          # JSON intermediate → Anki TSV
└── tests/
    └── fixtures/
        ├── sample-cards.json
        └── sample-cards.expected.txt
```
````

- [ ] **Step 2: Verify**

```bash
ls flashcards/
```

Expected: `README.md  SKILL.md  commands  references  scripts  tests`.

- [ ] **Step 3: Commit**

```bash
git add flashcards/README.md
git commit -m "Add flashcards README with install instructions"
```

---

## Task 8: Smoke test the writer script end-to-end

**Files:** none modified. Verification only.

Confirm the script runs cleanly against the fixture from a fresh shell, the fixture diff is clean, and the validation errors fire correctly.

- [ ] **Step 1: Re-run fixture round-trip**

```bash
rm -f /tmp/flashcards-test-out.txt
python3 flashcards/scripts/write_anki_tsv.py /tmp/flashcards-test-out.txt < flashcards/tests/fixtures/sample-cards.json
diff /tmp/flashcards-test-out.txt flashcards/tests/fixtures/sample-cards.expected.txt
echo "exit=$?"
```

Expected: empty diff, `exit=0`.

- [ ] **Step 2: Verify Cloze-without-markers rejection**

```bash
python3 flashcards/scripts/write_anki_tsv.py /tmp/nope.txt <<'JSON' 2>&1 | tail -1
{"deck":"X","tags":[],"source":"x","cards":[{"type":"Cloze","text":"no markers","extra":""}]}
JSON
```

Expected: line ending `ValueError: card 0: Cloze missing {{cN::...}} markers`.

- [ ] **Step 3: Verify Basic-with-empty-field rejection**

```bash
python3 flashcards/scripts/write_anki_tsv.py /tmp/nope.txt <<'JSON' 2>&1 | tail -1
{"deck":"X","tags":[],"source":"x","cards":[{"type":"Basic","front":"","back":"y"}]}
JSON
```

Expected: line ending `ValueError: card 0: Basic requires non-empty front + back`.

- [ ] **Step 4: Verify empty cards array rejection**

```bash
python3 flashcards/scripts/write_anki_tsv.py /tmp/nope.txt <<'JSON' 2>&1 | tail -1
{"deck":"X","tags":[],"source":"x","cards":[]}
JSON
```

Expected: line ending `ValueError: no cards to write`.

No commit for Task 8 — these are verification runs only.

---

## Task 9: Manual end-to-end smoke test (human, post-build)

**Files:** none modified. Tests the live skill once installed.

These tests must be run by the user (require Claude Code session + Anki):

1. **Vault shorthand input.** Run `/flashcards Reading/<some-existing-note>.md`. Verify Pass 1 atoms appear, accept defaults, verify count plan, accept, verify cards appear without source footer in chat. Supply deck name `Test`. Accept suggested tags. Verify file appears in `~/Downloads/flashcards-<stem>-<ts>.txt`.

2. **Absolute path input.** Run `/flashcards ~/cjbackman/Reading/<file>.md` → same expectations.

3. **No arg + paste.** Run `/flashcards`, paste a 3-paragraph snippet on the next turn. Verify same flow; source string in resulting file is `pasted YYYY-MM-DD`.

4. **Missing file.** Run `/flashcards Reading/definitely-not-here.md`. Expected: skill shows resolved path and asks for clarification, doesn't proceed.

5. **Reject all atoms.** During Pass 1, reply with "drop 1, 2, 3, …" (drop every atom). Expected: skill exits cleanly, no file written.

6. **Anki import.** Open Anki → File → Import → select the produced `.txt`. Verify:
   - Basic and Cloze rows render correctly.
   - Source footer (`Source: …`) appears at the bottom of the back/extra side.
   - Tags appear on the cards.
   - Deck name matches what was supplied.

7. **Audit catch (manual stress test).** Paste a paragraph that contains an obvious enumeration ("the 5 stages of grief are denial, anger, bargaining, depression, acceptance"). Verify the skill drafts cloze deletions per item rather than a single "list the 5 stages" card. Verify drop log entries (if any) have one-line reasons.

No commit for Task 9 — it's manual verification.

---

## Self-review

Spec coverage checklist:

| Spec section | Implementing tasks |
|---|---|
| Architecture / file layout | Task 1, 2, 3, 4, 5, 6, 7 (all files) |
| Anki output model (native types, footer, TSV) | Task 4 (writer script) |
| Invocation / input resolution | Task 5 (SKILL.md), Task 6 (slash command) |
| Pass 1 — atom extraction | Task 2 (atom-extraction.md), Task 5 (SKILL.md workflow) |
| Pass 2 — card drafting | Task 3 (card-drafting.md), Task 5 (SKILL.md workflow) |
| Output stage (deck prompt, tag suggest, write) | Task 5 (SKILL.md workflow) |
| Audit checklist (8 rules + procedure) | Task 1 (principles.md) |
| Edge cases (missing file, ambiguous shorthand, etc.) | Task 5 (SKILL.md edge cases section) |
| Verification plan (fixture test + manual smoke) | Task 4, Task 8, Task 9 |

No spec gaps detected. All cross-references use exact file paths. Function signatures in the script (`escape_field`, `normalize_tags`, `validate_card`, `render_row`, `write_tsv`) are consistent across the script, the validation step examples, and the README.

No placeholders or `TBD`/`TODO` markers in any task content.
