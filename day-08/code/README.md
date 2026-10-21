# Day 08 code

| File | What it shows | Needs a key? |
|---|---|---|
| `day-08-rag-basics.ipynb` | A RAG chatbot over a 43-page handbook, from scratch. A plain LLM can't answer (in one run it invented "20 leaves, carry forward 5"; the handbook says 24 and 15). Fine-tuning vs RAG vs long context. Full ingestion: text layer check (page 20 is a scan with no text), Mistral OCR to markdown (Tesseract mentioned as the free option), cleaning and saving one `.md` file, fixed-size chunking (50 lines, 20 lines overlap) with metadata, embeddings, a numpy "vector DB" saved to `index/`. Retrieval, generation that names the chunk it used, a chatbot with memory and query rewriting, whole-PDF vs RAG (about 10,600 vs 3,300 input tokens), the problems of basic RAG shown live, and a streaming chat loop at the end (§10) for live questions. Every step is one small function | Yes, `OPENAI_API_KEY`; `MISTRAL_API_KEY` only if `data/ocr_mistral.json` is deleted |
| `data/nimbus_handbook.pdf` | The demo document: the employee handbook of Nimbus Labs, a made-up startup (Part A policies, Part B HR, Part C finance, an Addendum that changes 4 policies, FAQ). Page 20 is a scanned image | - |
| `data/ocr_mistral.json` | Cached Mistral OCR output (a list with one markdown string per page), so the notebook doesn't OCR again | - |
| `data/nimbus_handbook.md` | Written by the notebook: the cleaned handbook as one markdown file (868 lines). This is the file we chunk | - |
| `index/` | Written by the notebook: `vectors.npy` (one 1,536-number vector per chunk) and `chunks.json` (text + metadata) | - |

The diagram is in `../diagrams/rag-pipeline.excalidraw` (open in https://excalidraw.com, File → Open): plain LLM and its disadvantages, fine-tuning vs RAG vs long context, the ingestion pipeline, and the retrieval pipeline.

## Setup

```bash
cd day-08/code
uv venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
cp .env.example .env             # then paste your OpenAI and Mistral keys into .env
```

Open the notebook in VS Code (pick the `.venv` kernel) or run `jupyter notebook`. A full run makes about 45 OpenAI calls and costs about $0.004. OCR is cached, so Mistral is only called if you delete `data/ocr_mistral.json`.

**No Mistral key?** You don't need one: the OCR output is cached in `data/ocr_mistral.json`. Tesseract is the free alternative (`brew install tesseract`), but it gives plain text and misreads the scanned page (see Notes).

## Notes (checked 2026-10-19)

- Models: `gpt-6-luna` with `reasoning={"effort": "none"}` via the Responses API ($0.10 in / $0.50 out per 1M tokens: https://developers.openai.com/api/docs/models), and `text-embedding-3-small` (1,536 dimensions, 62,500 pages per dollar, i.e. $0.02 per 1M tokens: https://developers.openai.com/api/docs/guides/embeddings). Versions: `openai` 3.35.1, `mistralai` 3.2.0, `pymupdf` 2.0, Python 3.13.
- OpenAI embeddings are normalised to length 1, so cosine similarity is a plain dot product (same page).
- Mistral OCR: `from mistralai.client import Mistral`, `client.ocr.process(model="mistral-ocr-latest", document={"type": "document_url", ...})`, returns `pages[].markdown` (https://docs.mistral.ai/capabilities/document_ai/basic_ocr). It is billed per 1,000 pages; check the current price at https://mistral.ai/pricing (the page didn't show a number when checked). The 43 pages took 5 seconds.
- Tesseract 5.5.3 on the scanned page split the table into separate columns and misread words ("Tuesday" → `-tesneciny`, "Good Friday" → `Good Disasill`). Mistral returned a clean markdown table.
- OpenAI's model optimization guide presents fine-tuning as an addition to prompting, and says OpenAI is winding down its fine-tuning platform for new users: https://developers.openai.com/api/docs/guides/model-optimization
- Results from our run (2026-10-20, 868 lines → 29 chunks), used in §8: for paternity leave, k=1 retrieved only chunk 9 (old rule) and answered 10 days; k=5 also got chunk 27 (Addendum) and answered 15. For `CC-400` (in chunks 23 and 24), chunk 22 ranked first without containing it; all scores were about 0.2.
- Streaming (§10): `client.responses.create(..., stream=True)`, printing `event.delta` for `response.output_text.delta` events (https://developers.openai.com/api/docs/guides/streaming-responses).
- LLM output varies between runs. The plain-LLM answer in §1 is sometimes a made-up number and sometimes "I don't know"; both make the point.
