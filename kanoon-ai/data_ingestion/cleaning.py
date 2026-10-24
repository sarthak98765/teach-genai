import json
import re
import sys
import unicodedata
from typing import Dict, List
from config import ACTS, CLEAN_DIR
from data_extraction import extract
from logger import custom_logger

QUOTES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-"})
INVISIBLE_RE = re.compile(r"[​‌‍­﻿\x00-\x08\x0b\x0c\x0e-\x1f]")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")              # OCR image placeholders
PAGE_NUMBER_RE = re.compile(r"^\s*(\d+|Page \d+( of \d+)?)\s*$", re.M)
HYPHEN_RE = re.compile(r"(\w)-\n(\w)")                     # "pun-\nishment" -> "punishment"

def clean(text: str) -> str:
    """Day 9 cleaning, in order: characters first, then lines, then whitespace."""
    text = unicodedata.normalize("NFKC", text)  # ligatures, odd spaces
    text = text.translate(QUOTES)               # curly quotes and dashes
    text = INVISIBLE_RE.sub("", text)           # zero-width, soft hyphen
    text = IMAGE_RE.sub("", text)
    text = PAGE_NUMBER_RE.sub("", text)
    text = HYPHEN_RE.sub(r"\1\2", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def clean_act(act_id: str) -> List[Dict]:
    """OCR pages -> cleaned pages, saved to data/cleaned/<act>.json."""
    pages = [{**p, "markdown": clean(p["markdown"])} for p in extract(act_id)]
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    (CLEAN_DIR / f"{act_id}.json").write_text(json.dumps(pages, indent=1, ensure_ascii=False))
    custom_logger.info(f"clean | {act_id}: {len(pages)} pages")
    return pages

if __name__ == "__main__":
    for act_id in sys.argv[1:] or ACTS:
        clean_act(act_id)