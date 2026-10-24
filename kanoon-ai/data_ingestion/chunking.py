import json
import re
import sys
from typing import Dict, List
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from cleaning import clean_act
from config import ACTS, CHUNK_OVERLAP_TOKENS, CHUNKS_DIR, MAX_CHUNK_TOKENS, TOKENIZER
from logger import custom_logger

MARKUP_RE = re.compile(r"[#*]")                            # "**103.** (1)" -> "103. (1)"
CHAPTER_RE = re.compile(r"^CHAPTER ([IVXLC]+)\b")
# "103. (1) Whoever...", "192.Whoever...", and "Punishments. 4. The..." (margin title glued on by OCR)
SECTION_RE = re.compile(r"^(?:[A-Z][^.]{1,120}\.\s+)?(\d+)\.\s*(?=[A-Z(\"])")

encoder = tiktoken.get_encoding(TOKENIZER)
splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(encoding_name=TOKENIZER, chunk_size=MAX_CHUNK_TOKENS, chunk_overlap=CHUNK_OVERLAP_TOKENS)

def sections(pages: List[Dict]) -> List[Dict]:
    """Split the Act into sections. A line starting "103." opens a section only if 103 is the next number, so a wrapped line that happens to start with a number can't start a fake one.Everything before CHAPTER I (the Gazette masthead) is skipped."""
    out, chapter, expected, title_next = [], None, 1, False
    for page in pages:
        for line in page["markdown"].splitlines():
            plain = MARKUP_RE.sub("", line).strip()
            if match := CHAPTER_RE.match(plain):
                chapter, title_next = f"CHAPTER {match[1]}", True
            elif chapter is None or not plain:
                continue
            elif title_next:  # the line after "CHAPTER VI" is its title
                chapter, title_next = f"{chapter} - {plain}", False
            elif (match := SECTION_RE.match(plain)) and int(match[1]) == expected:
                out.append({"number": expected, "chapter": chapter, "page": page["page"], "lines": [plain[match.start(1):]]})
                expected += 1
            elif out:
                out[-1]["lines"].append(line)
    return out


def chunk_act(act_id: str) -> List[Dict]:
    """One chunk per section. A section over MAX_CHUNK_TOKENS is split again, and every piece keeps the same breadcrumb (the free version of contextual retrieval)."""
    act, chunks = ACTS[act_id], []
    found = sections(clean_act(act_id))
    for section in found:
        unit = f"{act['unit']} {section['number']}"
        breadcrumb = f"{act['title']} > {section['chapter']} > {unit}"
        text = "\n".join(section["lines"]).strip()
        pieces = [text] if len(encoder.encode(text)) <= MAX_CHUNK_TOKENS else splitter.split_text(text)
        for i, piece in enumerate(pieces):
            chunks.append({
                "chunk_id": f"{act_id}::s{section['number']}::{i}",  # stable: re-running overwrites
                "act": act_id,
                "breadcrumb": breadcrumb,
                "unit": unit,
                "page": section["page"],
                "text": piece,
                "tokens": len(encoder.encode(piece)),
                "source_url": act["official"],
                "as_of": act["as_of"],
            })
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CHUNKS_DIR / f"{act_id}.jsonl", "w") as f:
        f.writelines(json.dumps(c, ensure_ascii=False) + "\n" for c in chunks)
    custom_logger.info(f"chunk | {act_id}: {len(found)} sections -> {len(chunks)} chunks")
    return chunks

if __name__ == "__main__":
    for act_id in sys.argv[1:] or ACTS:
        chunk_act(act_id)