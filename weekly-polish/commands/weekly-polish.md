---
description: Polish the latest weekly update in ~/cjbackman/Work/<company>/Weekly/<year>.md against the AI Writing Style Guide.
---

The user has invoked the weekly-polish skill. Use the `weekly-polish` skill in this repo to run it.

The first argument is the company (e.g. `/weekly-polish Acme`); it selects `~/cjbackman/Work/<company>/Weekly/<year>.md`. If it's missing, ask for it. An optional second argument (e.g. `/weekly-polish Acme 19`) is a target week number: and scope edits to that `### Week N` section instead of the topmost one. Otherwise scope to the entry at the top of the file.

Do not improvise the editing protocol — follow `weekly-polish/SKILL.md` exactly. Spelling and grammar errors get fixed immediately; clarity and voice changes are listed for approval before any edit is applied.
