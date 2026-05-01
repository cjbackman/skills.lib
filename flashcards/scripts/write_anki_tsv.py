#!/usr/bin/env python3
"""Convert flashcards JSON intermediate to Anki-importable TSV.

Usage:
  python3 write_anki_tsv.py <output.txt> < input.json

Reads JSON from stdin; writes a TSV with Anki header lines to <output.txt>.
"""
import json
import re
import sys
from pathlib import Path


def escape_field(text: str) -> str:
    """Tabs → 4 spaces; literal newlines → <br>."""
    text = text.replace("\t", "    ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\n", "<br>")
    return text


def normalize_tags(tags):
    """Anki tags must not contain spaces. Split tags-with-spaces into multiple."""
    out = []
    for tag in tags:
        for piece in tag.split():
            if piece:
                out.append(piece)
    return out


def validate_card(card, idx):
    """Raise ValueError if card is malformed."""
    ctype = card.get("type")
    if ctype == "Basic":
        if not card.get("front") or not card.get("back"):
            raise ValueError(f"card {idx}: Basic requires non-empty front + back")
    elif ctype == "Cloze":
        text = card.get("text", "")
        if not text:
            raise ValueError(f"card {idx}: Cloze requires non-empty text")
        if not re.search(r"\{\{c\d+::", text):
            raise ValueError(f"card {idx}: Cloze missing " + "{{cN::...}} markers")
    else:
        raise ValueError(f"card {idx}: type must be 'Basic' or 'Cloze'")


def build_source_footer(source):
    return f'<hr><small><i>Source: {source}</i></small>'


def render_row(card, deck, tags, source):
    """Build one TSV row."""
    footer = build_source_footer(source)
    if card["type"] == "Basic":
        front = escape_field(card["front"])
        back = escape_field(card["back"]) + footer
        cols = ["Basic", deck, front, back, " ".join(tags)]
    else:
        text = escape_field(card["text"])
        extra = escape_field(card.get("extra", ""))
        back_extra = (extra + footer) if extra else footer
        cols = ["Cloze", deck, text, back_extra, " ".join(tags)]
    return "\t".join(cols)


def write_tsv(payload, out_path):
    deck = payload["deck"]
    tags = normalize_tags(payload.get("tags", []))
    source = payload["source"]
    cards = payload["cards"]

    if not cards:
        raise ValueError("no cards to write")

    for i, card in enumerate(cards):
        validate_card(card, i)

    lines = [
        "#separator:tab",
        "#html:true",
        "#notetype column:1",
        "#deck column:2",
        "#tags column:5",
        "",
    ]
    for card in cards:
        lines.append(render_row(card, deck, tags, source))

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    if len(sys.argv) != 2:
        print("usage: write_anki_tsv.py <output.txt>", file=sys.stderr)
        return 2
    out_path = Path(sys.argv[1])
    payload = json.load(sys.stdin)
    write_tsv(payload, out_path)
    print(out_path, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
