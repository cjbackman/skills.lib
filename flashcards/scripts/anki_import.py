#!/usr/bin/env python3
"""Import flashcards JSON intermediate into Anki via AnkiConnect.

Usage:
  python3 anki_import.py < input.json

Reads JSON from stdin (same schema as write_anki_tsv.py).
Posts notes to AnkiConnect at http://localhost:8765.
Auto-creates the deck if missing. Skips duplicates (by first field).

Exit codes:
  0  imported successfully (possibly with duplicates skipped)
  2  AnkiConnect unreachable or version mismatch
  3  malformed payload
  4  partial failure — some notes rejected by Anki
"""
import json
import re
import sys
import urllib.error
import urllib.request

ANKI_URL = "http://localhost:8765"
ANKI_VERSION = 6


def post(action, **params):
    payload = json.dumps({"action": action, "version": ANKI_VERSION, "params": params}).encode()
    req = urllib.request.Request(ANKI_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.loads(resp.read().decode())
    if body.get("error"):
        raise RuntimeError(f"AnkiConnect error on {action}: {body['error']}")
    return body.get("result")


def normalize_tags(tags):
    out = []
    for tag in tags:
        for piece in tag.split():
            if piece:
                out.append(piece)
    return out


def build_source_footer(source):
    return f'<hr><small><i>Source: {source}</i></small>'


def field_html(text):
    return text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")


def validate_card(card, idx):
    ctype = card.get("type")
    if ctype == "Basic":
        if not card.get("front") or not card.get("back"):
            raise ValueError(f"card {idx}: Basic requires non-empty front + back")
    elif ctype == "Cloze":
        text = card.get("text", "")
        if not text:
            raise ValueError(f"card {idx}: Cloze requires non-empty text")
        if not re.search(r"\{\{c\d+::", text):
            raise ValueError(f"card {idx}: Cloze missing {{cN::...}} markers")
    else:
        raise ValueError(f"card {idx}: type must be 'Basic' or 'Cloze'")


def build_note(card, deck, tags, source):
    footer = build_source_footer(source)
    if card["type"] == "Basic":
        front = field_html(card["front"])
        back = field_html(card["back"]) + footer
        return {
            "deckName": deck,
            "modelName": "Basic",
            "fields": {"Front": front, "Back": back},
            "tags": tags,
            "options": {"allowDuplicate": False},
        }
    text = field_html(card["text"])
    extra = field_html(card.get("extra", ""))
    back_extra = (extra + footer) if extra else footer
    return {
        "deckName": deck,
        "modelName": "Cloze",
        "fields": {"Text": text, "Back Extra": back_extra},
        "tags": tags,
        "options": {"allowDuplicate": False},
    }


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"malformed JSON: {e}", file=sys.stderr)
        return 3

    deck = payload.get("deck")
    source = payload.get("source")
    cards = payload.get("cards") or []
    if not deck or not source or not cards:
        print("payload missing deck/source/cards", file=sys.stderr)
        return 3

    tags = normalize_tags(payload.get("tags", []))

    for i, card in enumerate(cards):
        try:
            validate_card(card, i)
        except ValueError as e:
            print(str(e), file=sys.stderr)
            return 3

    try:
        version = post("version")
    except (urllib.error.URLError, ConnectionError, RuntimeError) as e:
        print(f"AnkiConnect unreachable: {e}", file=sys.stderr)
        return 2

    if version != ANKI_VERSION:
        print(f"AnkiConnect version mismatch: got {version}, expected {ANKI_VERSION}", file=sys.stderr)
        return 2

    try:
        post("createDeck", deck=deck)
    except RuntimeError as e:
        print(f"createDeck failed: {e}", file=sys.stderr)
        return 2

    notes = [build_note(c, deck, tags, source) for c in cards]

    try:
        addable = post("canAddNotes", notes=notes)
    except RuntimeError as e:
        print(f"canAddNotes failed: {e}", file=sys.stderr)
        return 2

    to_add = [n for n, ok in zip(notes, addable) if ok]
    skipped = len(notes) - len(to_add)

    if not to_add:
        print(f"deck={deck} added=0 skipped={skipped} (all duplicates)", file=sys.stderr)
        return 0

    try:
        results = post("addNotes", notes=to_add)
    except RuntimeError as e:
        print(f"addNotes failed: {e}", file=sys.stderr)
        return 4

    added = sum(1 for r in results if r is not None)
    rejected = sum(1 for r in results if r is None)
    skipped += rejected

    print(f"deck={deck} added={added} skipped={skipped} (duplicates or rejected)", file=sys.stderr)
    return 0 if rejected == 0 else 4


if __name__ == "__main__":
    sys.exit(main())
