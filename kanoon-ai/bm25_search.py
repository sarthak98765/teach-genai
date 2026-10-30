import json
import pickle
import re
import sys
from typing import Dict, List, Optional
from rank_bm25 import BM25Okapi
from config import ACTS, BM25_DIR, CHUNKS_DIR
from data_ingestion.logger import custom_logger

BM25_PATH = BM25_DIR / "kanoon_bm25.pkl"
TOKEN = re.compile(r"[\w-]+")                  # words and numbers; a hyphen stays inside a word ("sub-section")
SECTION_START = re.compile(r"\*\*(\d+)\.\*\*")  # "**103.**" = Section 103 starts here

def tokenize(text: str) -> List[str]:
    return TOKEN.findall(text.lower())

def bm25_text(chunk: Dict) -> str:
    """The text BM25 indexes: 'Section 102 Section 103 ...' for every section that starts in the chunk, then the chunk."""
    sections = " ".join(f"Section {n}" for n in SECTION_START.findall(chunk["text"]))
    return f"{sections}\n{chunk['text']}"

def build_bm25_index(act_ids: List[str]) -> Dict:
    """Chunks of every Act -> one BM25 index. Row i of the index = chunk i."""
    chunks = []
    for act_id in act_ids:
        with open(CHUNKS_DIR / f"{act_id}.jsonl") as f:
            chunks += [json.loads(line) for line in f]
    return {"bm25": BM25Okapi([tokenize(bm25_text(c)) for c in chunks]), "chunks": chunks}

def save_bm25_index(index: Dict) -> None:
    BM25_DIR.mkdir(parents=True, exist_ok=True)
    with open(BM25_PATH, "wb") as f:
        pickle.dump(index, f)
    custom_logger.info(f"bm25 | {len(index['chunks'])} chunks -> {BM25_PATH}")

def load_bm25_index() -> Dict:
    """Our own file, written by save_bm25_index (pickle runs code on load: never load one from someone else)."""
    if not BM25_PATH.exists():
        raise RuntimeError(f"No BM25 index at {BM25_PATH}: run `python bm25_search.py` first")
    with open(BM25_PATH, "rb") as f:
        return pickle.load(f)

def bm25_search(index: Dict, query: str, act_id: Optional[str] = None, k: int = 2) -> List[Dict]:
    """Top-k chunks that share the most (rare) words with the query, optionally from one Act only. Score 0 = no shared word: not a hit."""
    scores = index["bm25"].get_scores(tokenize(query))
    ranked = sorted(range(len(scores)), key=lambda i: -scores[i])
    hits = [{**index["chunks"][i], "score": float(scores[i])} for i in ranked
            if scores[i] > 0 and (act_id is None or index["chunks"][i]["act"] == act_id)]
    return hits[:k]

if __name__ == "__main__":
    save_bm25_index(build_bm25_index(sys.argv[1:] or list(ACTS)))
    index = load_bm25_index()
    for hit in bm25_search(index, "What does Section 103 say?", k=3):
        custom_logger.info(f"bm25 | {hit['chunk_id']} (page {hit['page']}, score {hit['score']:.2f})")
