import re
from typing import Dict, List

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP_TOKENS, MAX_CHUNK_TOKENS, TOKENIZER
from logger import custom_logger
from sources import ACTS

HEADING_RE = re.compile(r"^(#{1,3}) (.+)$")
PAGE_RE = re.compile(r"^<!-- page (\d+) -->$")

encoder = tiktoken.get_encoding(TOKENIZER)
splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    encoding_name=TOKENIZER, chunk_size=MAX_CHUNK_TOKENS, chunk_overlap=CHUNK_OVERLAP_TOKENS
)


def sections(markdown: str) -> List[Dict]:
    """Every ## heading starts a section, which remembers its chapter (#), group (###) and first page."""
    out, chapter, group, page = [], "", "", 1
    for line in markdown.splitlines():
        if match := PAGE_RE.match(line):
            page = int(match[1])
        elif match := HEADING_RE.match(line):
            level, text = len(match[1]), match[2]
            if level == 1:
                chapter, group = text, ""
            elif level == 3:
                group = text
            else:
                out.append({"heading": text, "chapter": chapter, "group": group, "page": page, "lines": []})
        elif out:
            out[-1]["lines"].append(line)
    return out


def chunk_act(act_id: str, markdown: str) -> List[Dict]:
    """One chunk per section. A section over MAX_CHUNK_TOKENS is split again, and every piece keeps
    the same breadcrumb so it still says where it lives."""
    act, chunks = ACTS[act_id], []
    found = sections(markdown)
    for section in found:
        unit, title = section["heading"].split(" — ", 1)
        breadcrumb = " > ".join(p for p in [act["title"], section["chapter"], section["group"], f"{unit}: {title}"] if p)
        text = "\n".join(section["lines"]).strip()
        pieces = [text] if len(encoder.encode(text)) <= MAX_CHUNK_TOKENS else splitter.split_text(text)
        for i, piece in enumerate(pieces):
            chunks.append({
                "chunk_id": f"{act_id}::{unit[0].lower()}{unit.split()[-1]}::{i}",
                "act": act_id,
                "breadcrumb": breadcrumb,
                "unit": unit,
                "title": title,
                "page": section["page"],
                "text": piece,
                "tokens": len(encoder.encode(piece)),
                "source_url": act["official"],
                "as_of": act["as_of"],
            })
    custom_logger.info(f"chunk | {act_id}: {len(found)} sections -> {len(chunks)} chunks")
    return chunks
