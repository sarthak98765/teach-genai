import re
from pathlib import Path
from typing import Dict, List, Tuple

import pymupdf

from config import BODY_LEFT, BODY_RIGHT, HEADER_HEIGHT, MARGIN_NOTE_GAP
from logger import custom_logger

CHAPTER_RE = re.compile(r"^CHAPTER ([IVXLC]+)$")
SECTION_RE = re.compile(r"^(\d+)\.\s*(?=[A-Z(])")  # "192.Whoever" has no space
ACT_REF_RE = re.compile(r"^\d+ of \d{4}\.?$")  # margin notes like "45 of 1860." cite other Acts
END_RE = re.compile(r"^—{3,}$")                # the rule line above the signature
CENTRE_TOLERANCE = 6


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def page_lines(page: pymupdf.Page) -> Tuple[List[Dict], List[Dict]]:
    """A page as body lines and margin notes, each {x0, x1, y, text}. The running header is dropped."""
    body, notes = [], []
    for block in page.get_text("dict")["blocks"]:
        lines = [{"x0": l["bbox"][0], "x1": l["bbox"][2], "y": l["bbox"][1],
                  "text": clean("".join(s["text"] for s in l["spans"]))} for l in block.get("lines", [])]
        lines = [l for l in lines if l["text"] and l["y"] >= HEADER_HEIGHT]
        if not lines:
            continue
        if BODY_LEFT <= block["bbox"][0] <= BODY_RIGHT:
            body += lines
        else:
            notes += margin_notes(lines)
    body.sort(key=lambda l: (round(l["y"]), l["x0"]))
    return body, notes


def margin_notes(lines: List[Dict]) -> List[Dict]:
    """A note wraps over several lines and ends with a full stop. One block can hold two notes."""
    notes, current = [], []
    for line in lines:
        current.append(line)
        if line["text"].endswith("."):
            notes.append({**current[0], "text": " ".join(l["text"] for l in current)})
            current = []
    if current:
        notes.append({**current[0], "text": " ".join(l["text"] for l in current)})
    return notes


def margin_title(y: float, notes: List[Dict]) -> str:
    """The margin note level with a section's first line is its title."""
    for note in notes:
        if abs(note["y"] - y) <= MARGIN_NOTE_GAP and not ACT_REF_RE.match(note["text"]):
            return note["text"].rstrip(".")
    return ""


def is_group_heading(line: Dict, page_width: float) -> bool:
    """Centred lines like "Of offences affecting life" group sections inside a chapter."""
    centre = (line["x0"] + line["x1"]) / 2
    return line["text"].startswith("Of ") and abs(centre - page_width / 2) < CENTRE_TOLERANCE


def to_markdown(pdf_path: Path) -> str:
    """An Act's PDF as markdown: # chapter, ### group, ## section, plus <!-- page N --> markers.
    Everything before CHAPTER I (the Gazette masthead) and after the closing rule is dropped."""
    out, chapter, expected = [], None, 1
    with pymupdf.open(pdf_path) as doc:
        for number, page in enumerate(doc, 1):
            if not page.get_text().strip():
                custom_logger.warning(f"parse | {pdf_path.name} page {number} has no text layer, it needs OCR")
            body, notes = page_lines(page)
            out.append(f"<!-- page {number} -->")
            for line in body:
                text = line["text"]
                if END_RE.match(text):
                    return "\n".join(out) + "\n"
                if match := CHAPTER_RE.match(text):
                    chapter = [f"CHAPTER {match.group(1)}"]
                    continue
                if chapter is None:
                    continue
                if chapter and text.isupper():  # chapter titles can wrap over lines
                    chapter.append(text)
                    continue
                if chapter:
                    out.append(f"# {chapter[0]} — {' '.join(chapter[1:])}")
                    chapter = []
                if is_group_heading(line, page.rect.width):
                    out.append(f"### {text}")
                elif (match := SECTION_RE.match(text)) and int(match.group(1)) == expected:
                    out.append(f"## Section {expected} — {margin_title(line['y'], notes)}")
                    out.append(text)
                    expected += 1
                else:
                    out.append(text)
    return "\n".join(out) + "\n"
