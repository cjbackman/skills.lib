# coach

Personal coaching skill for explicit goal/reflection sessions against an Obsidian vault at `~/cjbackman`.

## What it does

Three modes:

- **Reflect** — radical self-inquiry on whatever the user is wrestling with. Colonna register.
- **Review** — annual or quarterly walkthrough using the user's existing template plus Life Changing Questions for depth.
- **Check-in** — goal-by-goal progress review with concrete next actions written to `Goals/*.md`.

Always logs the session to `~/cjbackman/Personal/Growth/Sessions/`.

## Vault assumptions

| Path | Purpose |
|---|---|
| `~/cjbackman/Personal/Growth/<year>.md` | Annual review |
| `~/cjbackman/Personal/Growth/Goals/*.md` | One file per goal |
| `~/cjbackman/Personal/Growth/Sessions/` | Session logs (auto-created) |
| `~/cjbackman/Templates/Annual Review.md` | Review mode spine |
| `~/cjbackman/Zettelkasten/Permanent/Life Changing Questions.md` | Review mode depth bank |

If the vault lives elsewhere, edit `~/cjbackman` references in `SKILL.md` and `references/vault-conventions.md` to match.

## Install

The skill itself:

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/coach" ~/.claude/skills/coach
```

The slash command (optional, lets you type `/coach`):

```bash
mkdir -p ~/.claude/commands
ln -s "$(pwd)/coach/commands/coach.md" ~/.claude/commands/coach.md
```

## Usage

In Claude Code, either:

- Type `/coach` (with optional mode: `/coach reflect`, `/coach review`, `/coach checkin`).
- Or ask explicitly: "let's do a coaching session", "I want to reflect on something", "let's check in on my goals", "annual review time".

The skill won't auto-trigger on casual phrasing — invocation is always explicit.

## Files

```
coach/
├── SKILL.md                       # engine: voice, discipline, dispatch
├── README.md                      # this file
├── references/
│   ├── vault-conventions.md       # paths, frontmatter, session log format
│   ├── frameworks.md              # GROW, solution-focused, SBI, decision matrix
│   ├── mode-reflect.md            # reflect playbook
│   ├── mode-review.md             # review playbook
│   └── mode-checkin.md            # check-in playbook
└── commands/
    └── coach.md                   # slash command wrapper
```
