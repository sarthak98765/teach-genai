# Kanoon.ai

Ask questions about Indian law and get answers that cite the exact Section or Article.

> **Not legal advice.** Kanoon.ai is a course project. It shows what the text of the law says; it does not replace a lawyer.

The project grows one class at a time (plan: `../rag-days-09-14.md`).

| Day | Adds |
|---|---|
| **09** | `download → parse → chunk`: PDF → Markdown with chapters and sections → one chunk per section |
| 10 | embeddings + vector database |
| 11–12 | hybrid search, reranking, answers with citations, `/ask` API |
| 13–14 | evals and observability |

## Run

```bash
cd kanoon-ai
uv venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
python ingest.py bns               # or just: python ingest.py  (every Act in sources.py)
```

```
download | bns: 1350 KB
chunk | bns: 358 sections -> 377 chunks
ingest | bns: done
```

Output (git-ignored, re-created by `ingest.py`):
- `data/raw/bns.pdf`: the Act, downloaded once
- `data/parsed/bns.md`: the Act as Markdown, so you can open it and check the parser
- `data/chunks/bns.jsonl`: one JSON chunk per line

## Files

| File | Job |
|---|---|
| `sources.py` | the Acts: title, download URL, official page, date of the text |
| `config.py` | paths, page layout numbers, chunk limits |
| `logger.py` | `custom_logger` |
| `download.py` | fetch the PDF into `data/raw/` (reused if it's already there) |
| `parse.py` | PDF → Markdown. Keeps the body column, drops the Gazette masthead and running headers, reads section titles from the margin |
| `chunk.py` | Markdown → chunks. One per section; a section over 800 tokens is split again with 100 tokens of overlap |
| `ingest.py` | runs the three steps for each Act |

## How the parser reads a Gazette PDF

Every Act in the Gazette of India has the same layout (in PDF points, on a 595 × 842 page):

- **Running header** above `y = 80` → dropped
- **Body** between `x = 110` and `x = 485` → kept, line by line
- **Margin notes** outside that column → section titles, matched to the section line at the same height
- **`CHAPTER VI`** + the upper-case line(s) under it → `# CHAPTER VI — OF OFFENCES AFFECTING THE HUMAN BODY`
- **Centred "Of …" lines** → group headings (`### Of offences affecting life`)
- **A line starting `103.`** → a new section, but only if 103 is the *next* number. Sections are numbered in order, so a wrapped line that happens to start with a number can't start a fake one.

## A chunk

```json
{
  "chunk_id": "bns::s103::0",
  "act": "bns",
  "breadcrumb": "Bharatiya Nyaya Sanhita, 2023 > CHAPTER VI — OF OFFENCES AFFECTING THE HUMAN BODY > Of offences affecting life > Section 103: Punishment for murder",
  "unit": "Section 103",
  "title": "Punishment for murder",
  "page": 34,
  "text": "103. (1) Whoever commits murder shall be punished with death or imprisonment for\nlife, and shall also be liable to fine. ...",
  "tokens": 98,
  "source_url": "https://www.indiacode.nic.in/handle/123456789/20062",
  "as_of": "2023-12-25"
}
```

- `chunk_id` is deterministic, so running ingestion again overwrites chunks instead of duplicating them.
- `breadcrumb` is the free version of contextual retrieval: on Day 10 we embed `breadcrumb + text`.
- `page` is the PDF page where the section starts, for citations.

## Sources (checked 2026-10-23)

- **BNS:** Gazette of India copy, Act No. 45 of 2023, 25 December 2023, in force from 1 July 2024. It's downloaded from PRS India because India Code blocks scripted downloads. Official page: https://www.indiacode.nic.in/handle/123456789/20062
- **Raw PDFs are not committed.** `download.py` fetches them, and `data/` is git-ignored.
