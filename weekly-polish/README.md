# weekly-polish

Polishes CJ's rough weekly updates to his engineering teams while keeping his voice. Reads the latest entry at the top of `~/cjbackman/Work/<company>/Weekly/<year>.md`, where the company is passed as the first argument, fixes spelling and grammar errors immediately, and proposes clarity improvements as a numbered approval list against the AI Writing Style Guide.

## What it does

1. Loads the style guide at `~/cjbackman/Zettelkasten/Permanent/AI Writing Style Guide.md`.
2. Reads the latest `### Week N` entry from the top of the current-year weekly file.
3. Applies obvious spelling, grammar, punctuation, and markdown fixes directly via `Edit`.
4. Lists every clarity or voice suggestion with before/after and a one-line style-guide rationale, then waits for approval.
5. Applies the approved subset.

## Assumptions

| Path | Purpose |
|---|---|
| `~/cjbackman/Work/<company>/Weekly/<year>.md` | Weekly updates. Latest entry at the top. |
| `~/cjbackman/Zettelkasten/Permanent/AI Writing Style Guide.md` | Voice and anti-pattern rules. |

The vault is assumed to live at `~/cjbackman`. Move the vault and you'll need to update the paths in `SKILL.md`.

## Install

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/weekly-polish" ~/.claude/skills/weekly-polish
```

## Usage

In Claude Code:

- "polish my weekly" / "edit my weekly" / "review my weekly update" — scopes to the topmost `### Week N` entry.
- `/weekly-polish` — slash command, same behavior.
- `/weekly-polish 17` — scope to `### Week 17` instead of the topmost entry.

The skill will not auto-trigger on generic editing requests — invocation is explicit.

## Files

```
weekly-polish/
├── SKILL.md                  # editing protocol and style-guide enforcement rules
├── README.md                 # this file
└── commands/
    └── weekly-polish.md      # slash command wrapper
```
