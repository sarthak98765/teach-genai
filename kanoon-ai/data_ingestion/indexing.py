import csv
import json
import sys
import uuid
from typing import Dict, List, Optional
import numpy as np
from openai import OpenAI
from qdrant_client import QdrantClient, models
from chunking import chunk_act
from config import ACTS, COLLECTION, EMBED_BATCH, EMBED_DIMENSIONS, EMBED_MODEL, EMBEDDINGS_DIR, OPENAI_API_KEY, QDRANT_API_KEY, QDRANT_DIR, QDRANT_URL
from logger import custom_logger

openai_client = OpenAI(api_key=OPENAI_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY or None) if QDRANT_URL else QdrantClient(path=str(QDRANT_DIR))  # Qdrant Cloud/Docker server, or local mode: a folder

def embed(texts: List[str]) -> List[List[float]]:
    """Texts -> vectors, EMBED_BATCH texts per API call."""
    vectors = []
    for i in range(0, len(texts), EMBED_BATCH):
        response = openai_client.embeddings.create(model=EMBED_MODEL, input=texts[i:i + EMBED_BATCH])
        vectors += [d.embedding for d in response.data]
    return vectors

def save_vectors(act_id: str, chunks: List[Dict], vectors: List[List[float]]) -> None:
    """Save the vectors next to the chunks: .npy (matrix, row i = chunk i), .jsonl (one vector per chunk) and a small CSV preview to open in a spreadsheet."""
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
    matrix = np.array(vectors, dtype=np.float32)
    np.save(EMBEDDINGS_DIR / f"{act_id}_vectors.npy", matrix)
    with open(EMBEDDINGS_DIR / f"{act_id}_vectors.jsonl", "w") as f:
        f.writelines(json.dumps({"chunk_id": c["chunk_id"], "page": c["page"], "model": EMBED_MODEL, "dims": len(v),
                                 "text": c["text"][:150], "vector": [round(x, 6) for x in v]}, ensure_ascii=False) + "\n"
                     for c, v in zip(chunks, vectors))
    with open(EMBEDDINGS_DIR / f"{act_id}_vectors_preview.csv", "w", newline="") as f:
        writer = csv.writer(f)  # first 8 dims + the last one, and the length (OpenAI vectors are normalised, so ~1.000)
        writer.writerow(["chunk_id", "page", "text_start"] + [f"d{i}" for i in range(8)] + ["...", f"d{matrix.shape[1] - 1}", "length"])
        for c, row in zip(chunks, matrix):
            writer.writerow([c["chunk_id"], c["page"], c["text"][:60].replace("\n", " ")]
                            + [f"{x:.4f}" for x in row[:8]] + ["...", f"{row[-1]:.4f}", f"{np.linalg.norm(row):.3f}"])
    custom_logger.info(f"save | {act_id}: {matrix.shape[0]} x {matrix.shape[1]} vectors -> {EMBEDDINGS_DIR}")

def act_filter(act_id: str) -> models.Filter:
    return models.Filter(must=[models.FieldCondition(key="act", match=models.MatchValue(value=act_id))])

def index_act(act_id: str) -> int:
    """Chunks -> vectors of breadcrumb + text -> Qdrant. The Act's old points are deleted first, so re-running replaces them."""
    if not OPENAI_API_KEY:
        raise RuntimeError("Set OPENAI_API_KEY in data_ingestion/.env")
    chunks = chunk_act(act_id)
    vectors = embed([f"{c['breadcrumb']}\n\n{c['text']}" for c in chunks])
    save_vectors(act_id, chunks, vectors)
    if not qdrant.collection_exists(COLLECTION):
        qdrant.create_collection(COLLECTION, vectors_config=models.VectorParams(size=EMBED_DIMENSIONS, distance=models.Distance.COSINE))
    if QDRANT_URL:  # a server only filters on indexed fields (local mode doesn't need it)
        qdrant.create_payload_index(COLLECTION, "act", models.PayloadSchemaType.KEYWORD)
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