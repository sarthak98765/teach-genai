# Day 10 code

| File | What it shows | Needs a key? |
|---|---|---|
| `embeddings_vector_dbs.ipynb` | **What an embedding is** (GPS coordinates for meaning, a toy 3-number example, a real 1,536-number vector, shape, dimensions, memory, a 2D PCA picture), **why** (keyword search finds nothing for "killing someone"; meaning search finds the murder sections; where embeddings fail: `Section 103`, Hinglish), **how** (cosine vs dot vs Euclidean, OpenAI small vs large vs local MiniLM on BNS questions, `dimensions=256`, cost), **how an index is formed** (flat timing, an IVF index built with k-means, HNSW, quantization), **vector databases**, then **FAISS** (a library: flat and HNSW index, no ids or metadata, adding twice duplicates, filter by passing ids, save to a file), **Qdrant** (local mode, upsert by stable id, filters, `score_threshold`) and **Pinecone** (serverless index, namespaces, metadata filters), and FAISS vs Qdrant vs Pinecone in plain words. Uses the 198 BNS chunks from `kanoon-ai/` | `OPENAI_API_KEY`; `PINECONE_API_KEY` for §8 only |
| `cache/` | Written by the notebook: `bns_small.npy` (198 × 1,536 vectors), `bns.faiss` (the FAISS index) and `qdrant/` (the local Qdrant DB). Git-ignored | - |

## Setup

```bash
cd day-10/code
uv venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
cp .env.example .env               # then paste your OpenAI key (and Pinecone key for §8)
```

The notebook reads `../../kanoon-ai/data_ingestion/data/chunks/bns.jsonl`, so run it from `day-10/code`.

A full run makes about 20 OpenAI calls and costs about $0.02 (most of it is embedding the chunks with `text-embedding-3-large`). The first run downloads `all-MiniLM-L6-v2` (about 90 MB). No Pinecone key? Skip §8; everything else runs.

## Notes (checked 2026-10-26)

- **Embedding models:** `text-embedding-3-small` (1,536 dims, $0.02 per 1M tokens) and `text-embedding-3-large` (3,072 dims, $0.13 per 1M tokens), both up to 8,192 input tokens. Vectors are normalised to length 1, and the `dimensions` parameter shortens them: https://developers.openai.com/api/docs/guides/embeddings, https://developers.openai.com/api/docs/pricing. Their tokenizer is `cl100k_base` (`tiktoken.encoding_for_model`).
- **all-MiniLM-L6-v2:** 384 dims; "input text longer than 256 word pieces is truncated": https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2. Our chunks are ~500 tokens, so it only sees about half of each one.
- **FAISS:** `faiss-cpu` 1.15.1 (PyPI, released 2026-09-16, Python 3.10–3.14). "A library for efficient similarity search and clustering of dense vectors", MIT license, developed at Meta FAIR: https://github.com/facebookresearch/faiss. **Mac:** the notebook calls `faiss.omp_set_num_threads(1)` because FAISS and torch (loaded by sentence-transformers in §3.2) each bring their own OpenMP, and `IndexHNSWFlat.add` crashed the kernel (segfault) without it. Checked 2026-10-28.
- **Qdrant:** `qdrant-client` 1.20.0. Local mode (`":memory:"` or `path=`) is "useful for development, prototyping and testing" (https://github.com/qdrant/qdrant-client, Apache-2.0). Local mode warns that payload indexes have no effect; on a server, create them before uploading (https://qdrant.tech/documentation/manage-data/indexing/). Default HNSW config read from a new collection: `m=16`, `ef_construct=100`. Cloud free tier: 0.5 vCPU, 1 GB RAM, 4 GB disk (https://qdrant.tech/pricing/).
- **Pinecone:** `pinecone` 10.2.0. `create_index(name, dimension, metric, spec=ServerlessSpec(cloud, region))`, `index.upsert(vectors=[{id, values, metadata}], namespace, batch_size)`, `index.query(vector, top_k, filter, include_metadata)`. Upserts: up to 1,000 records or 2 MB per request (https://docs.pinecone.io/guides/index-data/upsert-data). Filter operators: https://docs.pinecone.io/guides/search/filter-by-metadata. Starter plan: 2 GB, 5 indexes, AWS us-east-1 (https://www.pinecone.io/pricing/). Pinecone docs now also show a newer schema/documents API (`pc.indexes.create(schema=...)`); the notebook uses the vector API above, which the 10.2 SDK still has. **§8 was not run** (no Pinecone key when this was written): the calls were checked against the installed SDK only.
- **pgvector** offers HNSW and IVFFlat: https://github.com/pgvector/pgvector
- **Results from our run (2026-10-26, FAISS added and re-run 2026-10-28):** "killing someone" → 0 keyword hits; meaning search → `bns::58` (page 32, 0.489). `Section 103` (in `bns::61`, page 33) is not in the top 3. MiniLM misses most pages that small and large find. IVF compared 1% of 100,000 vectors and found 10/10 of the true top 10. `score_threshold=0.4` returns nothing for "Can I bring my dog to the office?". FAISS flat and Qdrant return the same chunks and scores; FAISS flat and HNSW give the same top 5; adding the chunks twice to FAISS gives 396 vectors.
- Embedding scores and the 2D picture change a little between runs; the groups and rankings stay the same.
- Tested on Python 3.14 (the course `.venv`).
