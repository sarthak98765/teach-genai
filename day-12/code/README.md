# Day 12 code

| File | What it shows | Needs a key? |
|---|---|---|
| `hybrid_search.ipynb` | **Hybrid search**, small and step by step. First on 8 short shop docs: **where vector search fails** (asks for `INV-2023-091`, gets `INV-2023-019`; asks for `E1042`, gets `E1024`), **BM25** (tokens, IDF, exact match, "no match"), **where BM25 fails** ("cheap family car" vs "Budget SUVs"), and **hybrid search with Reciprocal Rank Fusion** (right on all four queries). Then on Kanoon.ai's 198 BNS chunks: BM25 ranks *mentions* of 103 above Section 103, the fix (add each chunk's section numbers to its BM25 text), a vector vs BM25 vs hybrid scoreboard, and what hybrid can't fix (Hinglish → Day 11 rewriting) | `OPENAI_API_KEY` |

## Setup

```bash
cd day-12/code
uv venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

No new `.env`: the notebook reads `OPENAI_API_KEY` from `../../kanoon-ai/data_ingestion/.env`, as on Day 11.

It reads the chunks (`data/chunks/bns.jsonl`) and the vectors saved on Day 10 (`data/embeddings/bns_vectors.npy`) from `kanoon-ai/data_ingestion/`, so run it from `day-12/code`. BM25 runs locally, with no API calls. A full run makes about 25 short embedding calls and costs well under $0.01.

## Notes (checked 2026-10-31)

- **BM25 library:** `rank-bm25` 0.2.2 (PyPI). `BM25Okapi(corpus, k1=1.5, b=0.75, epsilon=0.25)`; words in more than half the docs get a small floor IDF instead of a negative one: https://github.com/dorianbrown/rank_bm25
- **RRF:** Cormack, Clarke, Büttcher, "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods", SIGIR 2009. Score = Σ 1 / (k + rank), k = 60: http://cormack.uwaterloo.ca/cormack/cormacksigir09-rrf.pdf
- **BEIR:** Thakur et al. (2021), "BM25 is a robust baseline" across 18 retrieval datasets: https://arxiv.org/abs/2104.08663
- **Elasticsearch:** BM25 is the default similarity: https://www.elastic.co/docs/reference/elasticsearch/index-settings/similarity
- **Qdrant hybrid:** two `prefetch` queries (sparse + dense) fused with `models.RrfQuery(rrf=models.Rrf(k=60))` in `query_points`: https://qdrant.tech/documentation/search/hybrid-queries/ (not used in the notebook; plain Python shows the idea).
- **Embeddings:** `text-embedding-3-small`, the model of the saved BNS vectors (Day 10).
- **Background reading:** Sarthak's post "Hybrid search explained: BM25 + vectors for real-world AI": https://medium.com/@sarthakagg567/hybrid-search-explained-bm25-vectors-for-real-world-ai-5fe1eb7f68bb
- **Tokenizer:** `[\w-]+` keeps codes like `INV-2023-091` in one piece. With `\w+` the ID splits into `inv`, `2023`, `091`; the other invoices then partly match, and RRF ties the right and the wrong invoice.
- **Results from our run:** vector search ranks `INV-2023-019` (0.420) above `INV-2023-091` (0.414) and `E1024` (0.458) above `E1042` (0.448); the two IDs are 0.93 alike as embeddings. BM25 returns only the right doc for both, and nothing for "cheap family car". Hybrid is right on all 4 toy queries. On the BNS, plain BM25 puts `bns::61` (Section 103) 4th, behind three chunks that list 103 among other sections; with the section numbers added it is 1st. Right chunk in the top 5 for 6 questions: vector 3, BM25 4, hybrid 5. Hybrid drops the Facebook question from 5th (vector) to 9th. "hatya ki saza kya hai": BM25 finds nothing, hybrid = vector, wrong.
- Embedding scores can move a little between runs; the rankings above stayed the same in 3 runs.
- Tested on Python 3.14 (the course `.venv`).
