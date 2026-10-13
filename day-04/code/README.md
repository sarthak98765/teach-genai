# Day 04 code

| File | What it shows | Needs a key? |
|---|---|---|
| `day-04-prompt-engineering.ipynb` | System prompt, roles, few-shot, delimiters + output spec, a bad vs good prompt scored on 10 messy WhatsApp orders (6% → 98% → 100%), chain-of-thought vs a reasoning model, prompt chaining, context engineering, and prompt caching with real cached-token counts | Yes, `OPENAI_API_KEY` |

## Setup

```bash
cd day-04/code
uv venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
cp .env.example .env             # then paste your OpenAI key into .env
```

Open the notebook in VS Code (pick the `.venv` kernel) or run `jupyter notebook`. A full run makes about 70 API calls and costs under $0.02.

## Notes (checked 2026-10-13)

- Models: `gpt-4o-mini` (regular) and `gpt-5-mini` (reasoning), via the Responses API, `openai` 3.29.
- Prices from https://developers.openai.com/api/docs/pricing (standard tier, per 1M tokens): `gpt-4o-mini` $0.15 in / $0.075 cached in / $0.60 out; `gpt-5-mini` $0.25 in / $0.025 cached in / $2.00 out.
- Caching rules from https://developers.openai.com/api/docs/guides/prompt-caching: automatic, matches the exact prefix, about 1,024+ tokens, shown in `usage.input_tokens_details.cached_tokens`.
- Reasoning tokens are billed as output tokens and shown in `usage.output_tokens_details.reasoning_tokens` (https://developers.openai.com/api/docs/guides/reasoning).
- LLM output varies between runs, so your scores and answers may differ slightly from the saved output.
