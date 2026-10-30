import sys
from typing import Dict, Iterator, List, Optional
from openai import OpenAI
from qdrant_client import QdrantClient, models
from bm25_search import bm25_search, load_bm25_index
from config import BM25_TOP_K, CHAT_MODEL, COLLECTION, EMBED_MODEL, MAX_HISTORY, NOT_FOUND, NOTICE, OFF_TOPIC, OPENAI_API_KEY, QDRANT_API_KEY, QDRANT_DIR, QDRANT_URL, VECTOR_TOP_K
from data_ingestion.logger import custom_logger
from prompts import SYSTEM_PROMPT, USER_PROMPT

openai_client = OpenAI(api_key=OPENAI_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY or None) if QDRANT_URL else QdrantClient(path=str(QDRANT_DIR))  # same DB as data_ingestion/indexing.py
bm25_index = load_bm25_index()  # written by bm25_search.py

def vector_retrieve(query: str, act_id: Optional[str] = None, k: int = VECTOR_TOP_K) -> List[Dict]:
    """Top-k chunks closest in meaning to the query, optionally from one Act only. Best match first."""
    vector = openai_client.embeddings.create(model=EMBED_MODEL, input=[query]).data[0].embedding
    act_filter = models.Filter(must=[models.FieldCondition(key="act", match=models.MatchValue(value=act_id))]) if act_id else None
    hits = qdrant.query_points(COLLECTION, query=vector, limit=k, query_filter=act_filter).points
    return [{**h.payload, "score": round(h.score, 3), "found_by": "vector"} for h in hits]

def bm25_retrieve(query: str, act_id: Optional[str] = None, k: int = BM25_TOP_K) -> List[Dict]:
    """Top-k chunks by keywords: exact words and section numbers that vectors miss."""
    return [{**h, "score": round(h["score"], 3), "found_by": "bm25"} for h in bm25_search(bm25_index, query, act_id, k)]

def retrieve(query: str, act_id: Optional[str] = None, vector_k: int = VECTOR_TOP_K, bm25_k: int = BM25_TOP_K) -> List[Dict]:
    """Hybrid search: top vector_k by meaning + the top bm25_k by keywords that vector search didn't already find. Numbered S1, S2..."""
    hits = vector_retrieve(query, act_id, vector_k)
    seen = {h["chunk_id"] for h in hits}
    hits += [h for h in bm25_retrieve(query, act_id, vector_k + bm25_k) if h["chunk_id"] not in seen][:bm25_k]
    return [{**h, "source": f"S{n}"} for n, h in enumerate(hits, 1)]

def build_context(chunks: List[Dict]) -> str:
    """Chunks -> numbered <source> blocks for the prompt. The model cites the id: [S1]."""
    return "\n\n".join(f'<source id="{c["source"]}" act="{c["breadcrumb"]}" page="{c["page"]}">\n{c["text"]}\n</source>' for c in chunks)

def build_input(question: str, chunks: List[Dict], history: Optional[List[Dict]] = None) -> List[Dict]:
    """Past turns as they were + the new question with its sources (only the new question gets sources)."""
    return (history or [])[-MAX_HISTORY:] + [{"role": "user", "content": USER_PROMPT.format(sources=build_context(chunks), question=question)}]

def generate_answer(question: str, chunks: List[Dict], history: Optional[List[Dict]] = None) -> str:
    response = openai_client.responses.create(model=CHAT_MODEL, instructions=SYSTEM_PROMPT, reasoning={"effort": "none"},
                                              input=build_input(question, chunks, history))
    return response.output_text.strip()

def stream_answer(question: str, chunks: List[Dict], history: Optional[List[Dict]] = None) -> Iterator[str]:
    """Same as generate_answer, but yields the text as the model writes it."""
    stream = openai_client.responses.create(model=CHAT_MODEL, instructions=SYSTEM_PROMPT, reasoning={"effort": "none"},
                                            input=build_input(question, chunks, history), stream=True)
    for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta

def notice_for(answer: str) -> str:
    """The legal notice goes under real answers, not under the fixed not-found / off-topic replies."""
    return "" if answer.strip() in (NOT_FOUND, OFF_TOPIC) else f"\n\n_{NOTICE}_"

def ask(question: str, act_id: Optional[str] = None) -> Dict:
    """Question -> hybrid search (3 vector + 2 BM25 chunks) -> answer that cites them."""
    chunks = retrieve(question, act_id)
    answer = generate_answer(question, chunks)
    return {"question": question, "answer": answer + notice_for(answer), "chunks": chunks}

if __name__ == "__main__":
    result = ask(" ".join(sys.argv[1:]) or "hatya ki saza kya hai?")
    for c in result["chunks"]:
        custom_logger.info(f"retrieve | {c['source']} {c['chunk_id']} (page {c['page']}, {c['found_by']} score {c['score']:.3f})")
    print(f"\nQ: {result['question']}\n\n{result['answer']}")
    qdrant.close()