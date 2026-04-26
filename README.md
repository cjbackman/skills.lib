# skills.lib

Personal library of Claude Code skills.

## Layout

Each top-level directory is a single skill containing a `SKILL.md` with
frontmatter (`name`, `description`) and any supporting files.

```
skills.lib/
├── README.md
├── .gitignore
└── example-skill/
    ├── SKILL.md
    ├── references/   # optional: longer docs the skill links to
    ├── scripts/      # optional: helper scripts the skill invokes
    └── assets/       # optional: templates, images, fixtures
```

## Adding a skill

1. Copy `example-skill/` to a new directory named after the skill (kebab-case).
2. Update the `name` and `description` frontmatter in `SKILL.md` — the
   `description` is what Claude matches against to decide when to invoke it,
   so be specific about triggers.
3. Replace the body with the skill's instructions.

## Installing locally

Symlink or copy a skill directory into `~/.claude/skills/` to make it
available to Claude Code.
