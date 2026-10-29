# Kanoon.ai

Ask questions about Indian law and get answers that cite the exact Section or Article.

> **Not legal advice.** Kanoon.ai is a course project. It shows what the text of the law says; it does not replace a lawyer.

The project grows one class at a time (plan: `../rag-days-09-14.md`).

| Day | Adds |
|---|---|
| **09** | `data_ingestion/`: PDF → Mistral OCR → cleaning → fixed-size chunks |
| **10** | `indexing.py`: chunks → OpenAI embeddings → Qdrant (local), search with an Act filter |
| **11** | `retrieval.py`: question → top 5 chunks from Qdrant → answer that cites them (`[S1]`); `prompts.py`, `config.py` |
| 12 | hybrid search (BM25 + vectors) |
| 13 | reranker |
| 14 | evals and observability |

## Run

From the repo root (one `.venv` for the whole course):

```bash
uv pip install -r kanoon-ai/requirements.txt
cp kanoon-ai/data_ingestion/.env.example kanoon-ai/data_ingestion/.env   # then add MISTRAL_API_KEY and OPENAI_API_KEY
cd kanoon-ai/data_ingestion
python indexing.py bns          # runs extraction -> cleaning -> chunking -> indexing; or: python indexing.py (every Act)
```

Each step can also run alone (`python data_extraction.py bns`, `python cleaning.py bns`, `python chunking.py bns`) and reads the step before it.
OCR costs money, so its result is cached: delete `data/ocr/bns.json` to OCR again.

Then ask a question (from `kanoon-ai/`, after indexing):

```bash
cd ..                           # back to kanoon-ai/
python retrieval.py "What is the punishment for murder?"
```

## Retrieval (Day 11)

| File | Job |
|---|---|
| `config.py` | chat model, `TOP_K = 5`, the fixed replies; keys, Qdrant and embedding model come from `data_ingestion/config.py` |
| `prompts.py` | `SYSTEM_PROMPT` (role, guardrails, instructions, citations, response format, example) and `USER_PROMPT` (`<sources>` + `<question>`) |
| `retrieval.py` | `retrieve(query, act_id, k)` → top-k chunks; `build_context()` → numbered `<source id="S1">` blocks; `generate_answer()`; `ask()` does all three |

| `app.py` | FastAPI: `POST /chat` streams the answer, `POST /answer` returns it whole, `GET /health` |
| `run.sh` | starts the API: gunicorn, 1 uvicorn worker (local Qdrant allows one process), port 8000; activates `../.venv` if needed |
| `test.py` | talk to the running API from the terminal |

```bash
cd kanoon-ai
sh run.sh                                         # terminal 1: the API on port 8000 (docs at http://localhost:8000/docs)
python test.py                                    # terminal 2: live chat, streamed; or
python test.py "What is the punishment for murder?"   # one full answer from /answer
```

- **`POST /chat`** takes `{"chat": [{"role": "user", "content": "..."}], "act_id": "bns"}` (`act_id` is optional) and streams one JSON object per line: first `{"role": "sources", ...}`, then `{"role": "assistant", "content": "<piece of text>"}` as the model writes, or `{"role": "error", ...}`. The last 6 messages are sent to the model as history.
- **`POST /answer`** takes `{"question": "...", "act_id": "bns"}` and returns `{"answer": "...", "sources": [...]}`.
- Search uses only the **last** message, so a follow-up like "and what is the punishment?" finds the wrong chunks (Day 08's `rewrite_question()` fixes this).

Qdrant local mode allows one process at a time: run either `retrieval.py` or the API, and stop any notebook that has `data/qdrant` open first.

## `data_ingestion/`

| File | Job |
|---|---|
| `config.py` | the Acts (title, download URL, page we cite, date of the text), `.env`, paths, OCR model, chunk limits |
| `data_extraction.py` | download the PDF once, OCR it with Mistral (running headers and footers removed) → `data/ocr/<act>.json` |
| `cleaning.py` | Day 9 cleaning: NFKC, quotes, invisible characters, image tags, page numbers, hyphenation, whitespace → `data/cleaned/<act>.json` |
| `chunking.py` | fixed-size chunks: 500 tokens with 100 tokens of overlap, cut across the whole Act → `data/chunks/<act>.jsonl` |
| `indexing.py` | embed `breadcrumb + text` with `text-embedding-3-small` (1,536 dims), store in Qdrant → `data/qdrant/`; `search(query, act_id)` |
| `logger.py` | `custom_logger` |

`data/` is git-ignored and re-created by the scripts.

## How chunks are cut

- The cleaned pages are joined and turned into tokens (`o200k_base`, via `tiktoken`).
- A window of 500 tokens is cut, then the window moves on by 400, so neighbouring chunks share 100 tokens.
- Chapters and sections are ignored, so a cut can land in the middle of a section. Overlap makes it less likely that a sentence is lost at the edge.

## A chunk

```json
{
  "chunk_id": "bns::60",
  "act": "bns",
  "breadcrumb": "Bharatiya Nyaya Sanhita, 2023",
  "page": 33,
  "text": "right of private defence, lays hold of A to prevent him from doing so. ...",
  "tokens": 500,
  "source_url": "https://www.indiacode.nic.in/handle/123456789/20062",
  "as_of": "2023-12-25"
}
```

- `chunk_id` is stable, so running ingestion again overwrites chunks instead of duplicating them.
- `breadcrumb` is the free version of contextual retrieval: on Day 10 we embed `breadcrumb + text`.
- `page` is the PDF page where the chunk starts, for citations.

## How chunks are stored (Day 10)

- **Qdrant in local mode:** `QdrantClient(path="data/qdrant")`, a folder on disk, no server or account. Moving to a Qdrant server later means changing only that line to `QdrantClient(url=...)`. Local mode allows one process at a time.
- **One collection, `kanoon`,** for every Act. Each point's payload is the chunk above plus `embed_model`, and `search(query, act_id="bns")` filters on `act`.
- **Point id = `uuid5(chunk_id)`**, so the same chunk always gets the same id. Re-indexing an Act deletes its old points first, so a re-run with fewer chunks leaves nothing stale.
- **Cost:** the BNS is about 100,000 tokens, about $0.002 to embed (`text-embedding-3-small`, $0.02 per 1M tokens, checked 2026-10-26).
- **Changing `EMBED_MODEL` means re-indexing every Act:** vectors from two models can't be compared.

`python indexing.py` ends with a test search:

```
index | bns: 198 chunks -> 198 points in 'kanoon' (text-embedding-3-small)
search | bns::58 (page 32, score 0.489)
search | bns::57 (page 31, score 0.478)
search | bns::64 (page 35, score 0.464)
```
