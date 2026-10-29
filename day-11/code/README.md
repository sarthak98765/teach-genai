# Day 11 code

| File | What it shows | Needs a key? |
|---|---|---|
| `retrieval_pipeline.ipynb` | **The retrieval pipeline**, step by step, on the 198 BNS chunks from `kanoon-ai/`: a **baseline** (Day 10 search fails on Hinglish and everyday words), **query rewriting** (rewrite, multi-query, HyDE), **search** (choosing k, a minimum score after rewriting), **neighbours** (the chunk before and after), **merge** (remove the 100-token overlap), **context** (token budget, best first, numbered sources), **answer** (cite `[S1]`, check citations, "not found"), and the whole pipeline in one `ask()` with two "not found" gates and a trace. Ends with what still fails: `Section 103` (Day 12, hybrid search) | `OPENAI_API_KEY` |

## Setup

```bash
cd day-11/code
uv venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

No new `.env`: the notebook reads `OPENAI_API_KEY` from `../../kanoon-ai/data_ingestion/.env`, the Kanoon.ai project's file.

It also reads the chunks (`data/chunks/bns.jsonl`) and the vectors saved on Day 10 (`data/embeddings/bns_vectors.npy`) from `kanoon-ai/data_ingestion/`, so run it from `day-11/code`. Missing vectors? Run `python indexing.py bns` in `kanoon-ai/data_ingestion` first.

No new embeddings for the chunks: they are loaded into an in-memory Qdrant (`QdrantClient(":memory:")`). A full run makes about 25 small LLM calls and 60 short embedding calls, and costs under $0.01.

## Notes (checked 2026-10-29)

- **Chat model:** `gpt-6-luna`, $0.10 / $0.50 per 1M input / output tokens, supports `reasoning={"effort": "none"}`: https://developers.openai.com/api/docs/models
- **Embeddings:** `text-embedding-3-small`, the model of the saved vectors. The question must be embedded with the same model.
- **HyDE:** Gao, Ma, Lin, Callan, "Precise Zero-Shot Dense Retrieval without Relevance Labels" (2022): https://arxiv.org/abs/2212.10496
- **Lost in the Middle:** Liu et al. (2023), performance is "often highest when relevant information occurs at the beginning or end of the input context": https://arxiv.org/abs/2307.03172
- **Qdrant:** `qdrant-client` 1.20.0, `":memory:"` local mode, `score_threshold` in `query_points`.
- **LLM steps change between runs.** The rewritten queries, the HyDE passage and the answers are different every time, and so are some scores and ranks. The notes in the notebook describe the saved run; a few say what happened in other runs. The baseline (§1), k (§3.1), merge (§4) and budget (§5.1) cells don't use the LLM to search and give the same numbers every run.
- **Results from our run:** Hinglish "hatya ki saza kya hai" → best score 0.27, Section 103 not in the top 5; after rewriting → 1st, score 0.70. `bns::61` (Section 103) is 7th for "Is killing someone a crime?". Rewriting raises the dog question's score from 0.17 to about 0.55, so the minimum score (0.55) is set after rewriting and the prompt is a second gate. Merging neighbours 60 + 61 = 900 tokens instead of 1,000. "Section 103" is not found by plain search.
- **Once in testing** OpenAI rejected a multi-query call with `400 invalid_prompt` ("flagged as potentially violating our usage policy") on a plain question; the same call passed on retry. Criminal-law text can trip the filter. If it happens in class, run the cell again.
- Tested on Python 3.14 (the course `.venv`).
