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
