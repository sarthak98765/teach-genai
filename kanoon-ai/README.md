# Kanoon.ai

Ask questions about Indian law and get answers that cite the exact Section or Article.

> **Not legal advice.** Kanoon.ai is a course project. It shows what the text of the law says; it does not replace a lawyer.

The project grows one class at a time (plan: `../rag-days-09-14.md`).

| Day | Adds |
|---|---|
| **09** | `data_ingestion/`: PDF → Mistral OCR → cleaning → one chunk per section |
| 10 | embeddings + vector database |
| 11–12 | hybrid search, reranking, answers with citations, `/ask` API |
| 13–14 | evals and observability |

## Run

From the repo root (one `.venv` for the whole course):

```bash
uv pip install -r kanoon-ai/requirements.txt
cp kanoon-ai/data_ingestion/.env.example kanoon-ai/data_ingestion/.env   # then add your MISTRAL_API_KEY
cd kanoon-ai/data_ingestion
python chunking.py bns          # runs extraction -> cleaning -> chunking; or: python chunking.py (every Act)
```

Each step can also run alone (`python data_extraction.py bns`, `python cleaning.py bns`) and reads the step before it.
OCR costs money, so its result is cached: delete `data/ocr/bns.json` to OCR again.

## `data_ingestion/`

| File | Job |
|---|---|
| `config.py` | the Acts (title, download URL, page we cite, date of the text), `.env`, paths, OCR model, chunk limits |
| `data_extraction.py` | download the PDF once, OCR it with Mistral (running headers and footers removed) → `data/ocr/<act>.json` |
| `cleaning.py` | Day 9 cleaning: NFKC, quotes, invisible characters, image tags, page numbers, hyphenation, whitespace → `data/cleaned/<act>.json` |
| `chunking.py` | one chunk per section, a section over 800 tokens is split again with 100 tokens of overlap → `data/chunks/<act>.jsonl` |
| `logger.py` | `custom_logger` |

`data/` is git-ignored and re-created by the scripts.

## How sections are found

- Everything before `CHAPTER I` (the Gazette masthead) is skipped.
- `CHAPTER VI` + the upper-case line(s) under it → the chapter, e.g. `CHAPTER VI - OF OFFENCES AFFECTING THE HUMAN BODY`.
- **A line starting `103.`** → a new section, but only if 103 is the *next* number. Sections are numbered in order, so a wrapped line that happens to start with a number can't start a fake one.

## A chunk

```json
{
  "chunk_id": "bns::s103::0",
  "act": "bns",
  "breadcrumb": "Bharatiya Nyaya Sanhita, 2023 > CHAPTER VI - OF OFFENCES AFFECTING THE HUMAN BODY > Section 103",
  "unit": "Section 103",
  "page": 34,
  "text": "103. (1) Whoever commits murder shall be punished with death or imprisonment for life, ...",
  "tokens": 98,
  "source_url": "https://www.indiacode.nic.in/handle/123456789/20062",
  "as_of": "2023-12-25"
}
```

- `chunk_id` is stable, so running ingestion again overwrites chunks instead of duplicating them.
- `breadcrumb` is the free version of contextual retrieval: on Day 10 we embed `breadcrumb + text`.
- `page` is the PDF page where the section starts, for citations.
