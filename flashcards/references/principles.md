# Principles

These are the rules the skill checks each draft card against. Drawn from:

- Andy Matuschak — <https://andymatuschak.org/prompts/>
- Borretti — <https://borretti.me/article/effective-spaced-repetition>
- SuperMemo's twenty rules — <https://www.supermemo.com/en/blog/twenty-rules-of-formulating-knowledge>

Apply during the silent audit in Pass 2. Each card is checked against every rule. Failed cards are revised once. Cards that fail twice are dropped and logged.

## The 8 audit rules

### 1. Atomic
One fact per card. *(SuperMemo #4, Borretti)*

- ✓ Q: "What does the spacing effect predict?" A: "Recall improves when reviews are spaced apart vs. massed."
- ✗ Q: "Define spacing effect and testing effect." (two facts)

### 2. Minimum information
Shortest form that still tests the concept. *(SuperMemo #3)*

- ✓ Front: "Spacing effect" / Back: "Recall improves with spaced vs. massed reviews."
- ✗ Front: full paragraph from source. Trim until only the testable pivot remains.

### 3. No enumeration
Lists/sets become individual cards or cloze deletions; never "list the 5 X". *(SuperMemo #5-6, Andy)*

- ✓ Cloze: "Wheel of Life dimensions include {{c1::Health}}, {{c2::Wealth}}, {{c3::Play}}, …"
- ✗ Q: "List the 6 Wheel of Life dimensions." (set recall, brittle)

### 4. No leak
Question doesn't contain or strongly hint the answer. *(Andy, Borretti)*

- ✓ Q: "What error does spaced repetition exploit?" A: "The forgetting curve."
- ✗ Q: "What forgetting curve does spaced repetition exploit?" (answer in question)

### 5. Closed answer
Answer is unambiguous, single-valued. *(SuperMemo #2)*

- ✓ Q: "What's the half-life formula in FSRS?" A: specific formula.
- ✗ Q: "Why is spaced repetition effective?" (open-ended; many valid answers).

### 6. Personal context
Card mentions the source-specific framing if needed for disambiguation. *(Borretti)*

- ✓ Q: "In Borretti's effective-SR essay, what does 'atomic' mean?" A: …
- Necessary when the term has different meanings across sources.

### 7. Low interference
Cards in the same batch don't share near-identical fronts. *(SuperMemo #11, Andy)*

If two cards have fronts that differ only in one word, recall confuses them. Rewrite to make fronts distinct.

### 8. Test understanding, not trivia
Prefer "why does X?" over "in year Y" unless the date is the point. *(Andy)*

- ✓ Q: "Why does cloze deletion work better than open recall for definitions?"
- ✗ Q: "What year did Ebbinghaus publish his memory study?" (unless dates matter to the source)

## Audit procedure

For each draft card:

1. Check against rules 1-8.
2. If any rule fails: revise the card with the failed rule as guidance. Re-check.
3. If second draft still fails: drop the card. Record `Atom <N> draft 1: <rule that failed> — <one-line reason>`.

After Pass 2 final card list, print the drop log if anything was dropped:

```
Dropped <N> cards (audit failures):
- Atom 4 draft 1: enumeration (5-item list, couldn't atomize cleanly)
- Atom 7 draft 1: ambiguous answer
```

The user may override drops by asking the skill to re-include specific dropped cards.

## Source footer

All cards have source attribution as an HTML footer in the `Back` field (Basic) or `Back Extra` field (Cloze). The writer script appends it; do not include in JSON `back` / `extra`.

Format:

```
<hr><small><i>Source: <source-string></i></small>
```

`<source-string>` is:
- File input: the resolved file path (e.g. `~/cjbackman/Reading/foo.md`).
- Pasted text: `pasted YYYY-MM-DD` (today's date).
