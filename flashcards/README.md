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

Vault root: `~/cjbackman`. If yours lives elsewhere, edit `~/cjbackman` references in `SKILL.md` and `references/atom-extraction.md`.

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
