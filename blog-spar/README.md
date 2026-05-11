# blog-spar

An intellectual sparring partner for CJ's blog drafts. Stress-tests the argument before any rewrite happens, then revises against CJ's voice.

## What it does

**Phase 1 — Critique**

1. Reads the draft and the AI Writing Style Guide.
2. Names the thesis in one sentence (or refuses to, if there isn't one).
3. Calls out the single strongest move and the single weakest move in the argument.
4. Asks 5–8 high-leverage questions **one at a time**, pushing back on thin answers.
5. Does not rewrite anything during this phase.

**Phase 2 — Revision** (only after CJ approves)

1. Fetches recent posts from `https://www.cjbackman.com/on/` to calibrate voice.
2. Integrates CJ's answers into a revised draft against the style guide.
3. Leaves `[needs: ...]` markers instead of inventing claims CJ has not endorsed.
4. Reports what changed structurally, what's still missing, and what was deliberately kept.

## Assumptions

| Path / URL | Purpose |
|---|---|
| Argument or message-mentioned path | The draft to spar over. |
| `~/cjbackman/Zettelkasten/Permanent/AI Writing Style Guide.md` | Voice and anti-pattern rules. |
| `https://www.cjbackman.com/on/` | Public blog used to mirror tone, abstraction level, and structure. |

The vault is assumed to live at `~/cjbackman`. Move the vault and you'll need to update the path in `SKILL.md`.

## Install

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/blog-spar" ~/.claude/skills/blog-spar
```

## Usage

In Claude Code:

- "spar with my draft at <path>" / "stress-test this post" / "challenge this draft" — natural-language trigger.
- `/blog-spar <path>` — slash command with explicit path.
- `/blog-spar` — slash command, will ask for the path if not supplied.

The skill will not auto-trigger on generic editing requests — invocation is explicit.

## Files

```
blog-spar/
├── SKILL.md                 # critique-then-revise protocol
├── README.md                # this file
└── commands/
    └── blog-spar.md         # slash command wrapper
```
