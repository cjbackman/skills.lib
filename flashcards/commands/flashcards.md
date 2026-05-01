---
description: Generate Anki flashcards from a file path, vault shorthand, or pasted text using the flashcards skill.
---

The user has invoked the flashcards skill. Use the `flashcards` skill in this repo to run the two-pass workflow.

If the user provided an argument after `/flashcards` (a path, vault shorthand, or inline text), pass it through as the source. If not, ask whether they want to paste text or supply a path.

Do not improvise the protocol — follow `flashcards/SKILL.md` and the relevant `flashcards/references/*.md` file exactly.
