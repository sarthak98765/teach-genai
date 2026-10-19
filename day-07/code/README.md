# Day 07 code

| File | What it shows | Needs a key? |
|---|---|---|
| `day-07-vision-evals-observability.ipynb` | One invoice extractor, start to finish: image input and `detail` (264 vs 1,267 tokens), digital vs scanned PDF (169 vs 6,027 tokens), a table and a chart read into data, Pydantic extraction from an image, schema validation vs business rules (a wrong vendor total that only a rule catches), a golden dataset, per-field metrics and failure analysis (day-first dates came back as the years 1409 and 3009), a regression gate (prompt v2 passes, `gpt-4.1-nano` fails), a small JSONL tracer, monitoring (error rate, P50/P95, cost) and debugging failed traces | Yes, `OPENAI_API_KEY` |
| `samples/` | 6 invoices (clean, different layout, blurry phone photo, wrong total, digital PDF, 8 line items), a revenue chart, and a scanned PDF | - |
| `golden.json` | The answer key for the 6 invoices, plus the business rule each one should trigger | - |
| `make_samples.py` | Draws `samples/` and writes `golden.json` from the same data, so the answers are exact. Already run; only needed if you change an invoice | - |
| `eval_baseline.json` | The saved metrics the regression gate compares against (written by the notebook) | - |
| `logs/traces.jsonl` | One JSON line per span, written by the notebook's tracer | - |

Diagrams are in `../diagrams/` (open in https://excalidraw.com, File → Open): `vision-extraction-pipeline`, `schema-vs-business-rules`, `eval-regression-loop`, `observability-trace`.

## Setup

```bash
cd day-07/code
uv venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
cp .env.example .env             # then paste your OpenAI key into .env
```

Open the notebook in VS Code (pick the `.venv` kernel) or run `jupyter notebook`. A full run makes about 45 API calls and costs about $0.01.

## Notes (checked 2026-10-17)

- Model: `gpt-6-luna` with `reasoning={"effort": "none"}`, via the Responses API, `openai` 3.33, `pydantic` 2.14, Python 3.13. Prices per 1M tokens: `gpt-6-luna` $0.10 in / $0.50 out, `gpt-4.1-nano` $0.10 / $0.40 (https://developers.openai.com/api/docs/models/gpt-6-luna, /gpt-4.1-nano).
- Images: `{"type": "input_image", "image_url": "data:image/png;base64,...", "detail": "low" | "high" | "auto"}`. PNG, JPEG, WEBP, non-animated GIF. Image token counts differ per model: https://developers.openai.com/api/docs/guides/images-vision
- PDFs: `{"type": "input_file", "filename": ..., "file_data": "data:application/pdf;base64,..."}`, under 50 MB. The API sends the extracted text and page images: https://developers.openai.com/api/docs/guides/pdf-files. Measured: the digital PDF cost 169 input tokens, a scanned one 6,027.
- `gpt-4.1-nano` has the same input price per token as `gpt-6-luna` but cost more per invoice ($0.000262 vs $0.000193), because it turns the image into more tokens. Compare cost per document, not per token.
- Without a date hint, `gpt-6-luna` wrote day-first dates as nonsense years (`14/09/2026` → `1409-09-14`, `30/09/2026` → `3009-…`). Prompt v2 says the dates are day first, and that fixed every date except the blurry photo's.
- A cut-off reply (`max_output_tokens=60`) makes `responses.parse()` raise a pydantic `ValidationError` ("Invalid JSON: EOF while parsing"), the same as on Day 05.
- Sending the revenue chart as an invoice: in one run the schema rejected it (date `0000-01-01`). In another it "passed" with made-up fields and only a business rule caught it.
- Observability tools: Langfuse (https://langfuse.com/docs/observability/overview), LangSmith (https://docs.langchain.com/langsmith/observability), OpenTelemetry GenAI semantic conventions, status "Development" (https://github.com/open-telemetry/semantic-conventions-genai).
- LLM output varies between runs, so your scores and timings will differ slightly from the saved output. With only 6 documents, one flaky answer moves a metric a lot.
