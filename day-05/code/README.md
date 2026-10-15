# Day 05 code

| File | What it shows | Needs a key? |
|---|---|---|
| `day-05-structured-outputs.ipynb` | Invoice extraction (a shop tax invoice + a freelancer's email) done 3 ways: prompt only (`json.loads` fails), JSON mode (parses, but a different shape per invoice), strict structured outputs with a nested Pydantic schema (typed object, totals add up). Then: a required field with no way out makes the model invent an invoice number, and a cut-off reply makes `parse()` raise | Yes, `OPENAI_API_KEY` |
| `tool_calling/web_search.py` | Tool 1: `web_search(query)` → top Google results via the Serper API (the demo prints the top 3 for "Next.js 16.4 release notes"). Output: `outputs/web_search.md` | Yes, `SERPER_API_KEY` |
| `tool_calling/crawl.py` | Tool 2: `crawl(url)` → the entire page as Markdown via crawl4ai (headless browser), nothing filtered out. Output: `outputs/crawl.md` | No |
| `tool_calling/pydantic_models.py` | The strict output schema: `CutoffReport` with a list of `BranchCutoff` rows (program, quota, opening/closing rank, source URL) | - |
| `tool_calling/prompts.py` | `CUTOFF_EXTRACTION_PROMPT`: role, today's date, context, guardrails, instructions, workflow, response format | - |
| `tool_calling/pipeline.py` | The full pipeline: `pipeline(query)` → web search → crawl the top 3 pages → LLM with the prompt → strict structured output. Outputs: `outputs/cutoffs.json` and `outputs/pipeline.md` (URLs, table, full pages) | Yes, both keys |

## Setup

```bash
cd day-05/code
uv venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
crawl4ai-setup                   # one time: downloads the headless browser crawl4ai uses
cp .env.example .env             # then paste your OpenAI and Serper keys into .env
```

Run the tool scripts from inside `tool_calling/`, e.g. `cd tool_calling && python pipeline.py`. Get a Serper key at https://serper.dev (free tier: 2,500 searches).

Open the notebook in VS Code (pick the `.venv` kernel) or run `jupyter notebook`. A full run makes 10 API calls and costs well under $0.01.

## Notes (checked 2026-10-14)

- Models: `gpt-4o-mini` (notebook) and `gpt-5-mini` with `reasoning={"effort": "low"}` (tool loop), via the Responses API, `openai` 3.30, `pydantic` 2.14, `crawl4ai` 0.9.4.
- Tool calling: https://developers.openai.com/api/docs/guides/function-calling. crawl4ai: https://docs.crawl4ai.com/core/quickstart/. Serper search endpoint: `https://google.serper.dev/search` with an `X-API-KEY` header.
- Two lessons from building the tool loop: without today's date in the instructions the model searched for "2023" and answered about Next.js 14; and `gpt-4o-mini` read only the blog index and padded the answer, while `gpt-5-mini` opened the actual release post and cited it.
- Structured outputs and JSON mode: https://developers.openai.com/api/docs/guides/structured-outputs. JSON mode needs the word "JSON" in the input, or the API returns a 400 error.
- If a strict reply is cut off by `max_output_tokens`, `responses.parse()` raises a pydantic `ValidationError` (seen in the notebook run).
- LLM output varies between runs, so your scores may differ slightly from the saved output.
