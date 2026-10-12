# Day 03 code

| File | What it shows | Needs a key? |
|---|---|---|
| `model_cost_comparison.ipynb` | One very basic task (routing 20 support messages) on `gpt-4o` vs `gpt-4o-mini`: accuracy, cost and latency side by side, then scaled to 1M messages a month | Yes, `OPENAI_API_KEY` |

## Setup

```bash
cd day-03/code
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then paste your OpenAI key into .env
```

Open the notebook in VS Code (pick the `.venv` kernel) or run `jupyter notebook`.

## Notes (checked 2026-10-11)

- Prices from https://developers.openai.com/api/docs/pricing (standard tier, per 1M tokens): `gpt-4o` $2.50 in / $10.00 out, `gpt-4o-mini` $0.15 in / $0.60 out.
- `gpt-oss-120b` is not available on the OpenAI API (it returns `model_not_found`). It's an open-weight model, so you run it yourself or use a host such as OpenRouter.
- In our run both models got 20/20, used the same tokens, and `gpt-4o` cost 16.7x more. Latency was close (median 0.94s vs 0.91s) and changes between runs.
