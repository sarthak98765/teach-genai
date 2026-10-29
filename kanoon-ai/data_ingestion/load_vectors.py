import json
import sys
import uuid
import numpy as np
from qdrant_client import QdrantClient, models
from config import ACTS, CHUNKS_DIR, COLLECTION, EMBED_MODEL, EMBEDDINGS_DIR, QDRANT_API_KEY, QDRANT_DIR, QDRANT_URL
from logger import custom_logger

qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY or None) if QDRANT_URL else QdrantClient(path=str(QDRANT_DIR))

def load_vectors(act_id: str) -> int:
    """Saved vectors (data/embeddings) + chunks (data/chunks) -> Qdrant. No OpenAI call: the vectors are already on disk."""
    with open(CHUNKS_DIR / f"{act_id}.jsonl") as f:
        chunks = [json.loads(line) for line in f]
    matrix = np.load(EMBEDDINGS_DIR / f"{act_id}_vectors.npy")  # row i = vector of chunk i
    if len(chunks) != len(matrix):
        raise RuntimeError(f"{len(chunks)} chunks but {len(matrix)} vectors: run `python indexing.py {act_id}` again")
    if not qdrant.collection_exists(COLLECTION):
        qdrant.create_collection(COLLECTION, vectors_config=models.VectorParams(size=matrix.shape[1], distance=models.Distance.COSINE))
    if QDRANT_URL:  # a server only filters on indexed fields (local mode doesn't need it)
        qdrant.create_payload_index(COLLECTION, "act", models.PayloadSchemaType.KEYWORD)
    act_filter = models.Filter(must=[models.FieldCondition(key="act", match=models.MatchValue(value=act_id))])
    qdrant.delete(COLLECTION, points_selector=act_filter)
    qdrant.upsert(COLLECTION, points=[
        models.PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL, c["chunk_id"])), vector=v.tolist(), payload={**c, "embed_model": EMBED_MODEL})
        for c, v in zip(chunks, matrix)])
    count = qdrant.count(COLLECTION, count_filter=act_filter).count
    custom_logger.info(f"load | {act_id}: {len(matrix)} saved vectors -> {count} points in '{COLLECTION}' ({QDRANT_URL or QDRANT_DIR})")
    return count

if __name__ == "__main__":
    for act_id in sys.argv[1:] or ACTS:
        load_vectors(act_id)
    point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "bns::58"))
    for hit in qdrant.query_points(COLLECTION, query=point_id, limit=4).points:
        custom_logger.info(f"nearest to bns::58 | {hit.payload['chunk_id']} (page {hit.payload['page']}, score {hit.score:.3f})")
    qdrant.close()