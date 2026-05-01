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

Numbering is **global** across tiers — each atom has a unique number from 1 to total. Omit a tier heading entirely if no atoms fall into that tier.

After the list, print this exact prompt:

> Default approves CORE only. Reply with adjustments — for example: "add 5, 7; drop 2; promote 9 to core". Or "looks good".

User-command vocabulary (interpret loosely):
- `add N` — include atom N in the approved set (typical for `supporting` / `detail` atoms not approved by default).
- `drop N` — remove atom N from the approved set, regardless of tier.
- `promote N to <tier>` — move atom N to a higher tier; usually `supporting` → `core` or `detail` → `core`.

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
