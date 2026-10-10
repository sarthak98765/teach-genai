# Day 02 code

Two small demos for "How LLMs actually work".

| File | What it shows | Needs a key? |
|---|---|---|
| `count_tokens.py` | How text becomes tokens and token IDs; English vs Hindi vs code | No (runs locally with tiktoken) |
| `temperature_demo.py` | Same prompt at temperature 0 vs 1, plus optional top-p | Yes, `OPENAI_API_KEY` |

## Setup

```bash
cd day-02/code
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then paste your OpenAI key into .env
```

## Run

```bash
python count_tokens.py
python count_tokens.py "Namaste duniya"

python temperature_demo.py
python temperature_demo.py --top-p 0.1 --runs 5
python temperature_demo.py --max-tokens 16 --prompt "Explain tokens in 100 words."   # see an answer get cut off
```

## Notes (checked 2026-10-10)

- `count_tokens.py` uses the `o200k_base` encoding (OpenAI's tokenizer). Claude and Gemini use their own tokenizers, so their counts differ.
- `temperature_demo.py` uses `gpt-6-luna` with `reasoning={"effort": "none"}`. With reasoning on, the API rejects `temperature` with a 400 error.
- OpenAI has no `top_k` setting. Claude and Gemini do.
- `max_output_tokens` must be at least 16.
- Temperature 0 is more repeatable, but not guaranteed identical: in our test run, two temperature-0 calls gave different names.
