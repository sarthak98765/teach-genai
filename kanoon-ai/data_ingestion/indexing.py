import sys
import uuid
from typing import Dict, List, Optional
from openai import OpenAI
from qdrant_client import QdrantClient, models
from chunking import chunk_act
from config import ACTS, COLLECTION, EMBED_BATCH, EMBED_DIMENSIONS, EMBED_MODEL, OPENAI_API_KEY, QDRANT_DIR
from logger import custom_logger

openai_client = OpenAI(api_key=OPENAI_API_KEY)
qdrant = QdrantClient(path=str(QDRANT_DIR))  # local mode: a folder, no server

def embed(texts: List[str]) -> List[List[float]]:
    """Texts -> vectors, EMBED_BATCH texts per API call."""
    vectors = []
    for i in range(0, len(texts), EMBED_BATCH):
        response = openai_client.embeddings.create(model=EMBED_MODEL, input=texts[i:i + EMBED_BATCH])
        vectors += [d.embedding for d in response.data]
    return vectors

def act_filter(act_id: str) -> models.Filter:
    return models.Filter(must=[models.FieldCondition(key="act", match=models.MatchValue(value=act_id))])

def index_act(act_id: str) -> int:
    """Chunks -> vectors of breadcrumb + text -> Qdrant. The Act's old points are deleted first, so re-running replaces them."""
    if not OPENAI_API_KEY:
        raise RuntimeError("Set OPENAI_API_KEY in data_ingestion/.env")
    chunks = chunk_act(act_id)
    vectors = embed([f"{c['breadcrumb']}\n\n{c['text']}" for c in chunks])
    if not qdrant.collection_exists(COLLECTION):
        qdrant.create_collection(COLLECTION, vectors_config=models.VectorParams(size=EMBED_DIMENSIONS, distance=models.Distance.COSINE))
    qdrant.delete(COLLECTION, points_selector=act_filter(act_id))
    qdrant.upsert(COLLECTION, points=[
        models.PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL, c["chunk_id"])),  # same chunk_id -> same point id
                           vector=v, payload={**c, "embed_model": EMBED_MODEL})
        for c, v in zip(chunks, vectors)])
    count = qdrant.count(COLLECTION, count_filter=act_filter(act_id)).count
    custom_logger.info(f"index | {act_id}: {len(chunks)} chunks -> {count} points in '{COLLECTION}' ({EMBED_MODEL})")
    return count

def search(query: str, act_id: Optional[str] = None, k: int = 5) -> List[Dict]:
    """Top-k chunks closest in meaning to the query, optionally from one Act only."""
    hits = qdrant.query_points(COLLECTION, query=embed([query])[0], limit=k,
                               query_filter=act_filter(act_id) if act_id else None).points
    return [{**h.payload, "score": h.score} for h in hits]

if __name__ == "__main__":
    for act_id in sys.argv[1:] or ACTS:
        index_act(act_id)
    for hit in search("Is killing someone a crime?", k=3):
        custom_logger.info(f"search | {hit['chunk_id']} (page {hit['page']}, score {hit['score']:.3f})")
    qdrant.close()