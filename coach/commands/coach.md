---
description: Start a coaching session (reflect / review / check-in) against the Obsidian vault.
---

The user has invoked the coach. Use the `coach` skill in this repo to run the session.

If the user provided an argument after `/coach` (e.g., `/coach reflect`, `/coach review`, `/coach checkin`), pass that as the mode and skip the "which mode?" question. Otherwise, ask.

Do not improvise the coaching protocol — follow `coach/SKILL.md` and the relevant `coach/references/mode-*.md` file exactly.
