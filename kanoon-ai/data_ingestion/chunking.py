import json
import sys
from typing import Dict, List
import tiktoken
from cleaning import clean_act
from config import ACTS, CHUNK_OVERLAP_TOKENS, CHUNK_TOKENS, CHUNKS_DIR, TOKENIZER
from logger import custom_logger

encoder = tiktoken.get_encoding(TOKENIZER)

def chunk_act(act_id: str) -> List[Dict]:
    """Fixed-size chunking: cut the whole Act every CHUNK_TOKENS tokens, with CHUNK_OVERLAP_TOKENS of overlap. It knows nothing about chapters or sections, so a cut can land in the middle of one."""
    act, chunks = ACTS[act_id], []
    tokens, token_pages = [], []  # token_pages[i] = PDF page of tokens[i], so every chunk still gets a page to cite
    for page in clean_act(act_id):
        page_tokens = encoder.encode(page["markdown"] + "\n\n")
        tokens += page_tokens
        token_pages += [page["page"]] * len(page_tokens)
    step = CHUNK_TOKENS - CHUNK_OVERLAP_TOKENS
    for i, start in enumerate(range(0, len(tokens), step)):
        window = tokens[start:start + CHUNK_TOKENS]
        chunks.append({
            "chunk_id": f"{act_id}::{i}",  # stable: re-running overwrites
            "act": act_id,
            "breadcrumb": act["title"],
            "page": token_pages[start],
            "text": encoder.decode(window).strip(),
            "tokens": len(window),
            "source_url": act["official"],
            "as_of": act["as_of"],
        })
        if start + CHUNK_TOKENS >= len(tokens):
            break
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CHUNKS_DIR / f"{act_id}.jsonl", "w") as f:
        f.writelines(json.dumps(c, ensure_ascii=False) + "\n" for c in chunks)
    custom_logger.info(f"chunk | {act_id}: {len(tokens)} tokens -> {len(chunks)} chunks of {CHUNK_TOKENS}")
    return chunks

if __name__ == "__main__":
    for act_id in sys.argv[1:] or ACTS:
        chunk_act(act_id)