# Day 06 code

Each topic of the day has its own folder. Diagrams are in `../diagrams/` (open in https://excalidraw.com, File → Open).

## 6.1 LLM application architecture (`01_architecture/`)

| File | What it shows | Needs a key? |
|---|---|---|
| `main.py` | The **backend**: a FastAPI `POST /chat` that validates the message (Pydantic), adds the system prompt, calls the model, catches provider errors (returns a clean 502), and returns the reply with token usage and model time. It also serves the client at `GET /`. The terminal prints each hop: backend → model API → backend | Only with `USE_MOCK=0` |
| `client.html` | The **client**: a one-page chat UI that only calls our `/chat`. Open DevTools → Network: no API key anywhere | - |
| `call_backend.py` | A second client (a Python script) calling the same backend. Shows that the backend doesn't care who the client is, and that an empty message is rejected with a 422 *before* any model call | - |
| `leaky_client.html` | The anti-pattern, for reading only: the browser calls the model provider directly with the key inside the JavaScript | Don't put one in |

Diagram: `../diagrams/llm-app-architecture.excalidraw`

**Demo flow**
1. `USE_MOCK=1`: run the server, open http://127.0.0.1:8000, send "Explain RAG in simple words". Point at the terminal logs to show the request going forward and the response coming back. No key and no cost.
2. Open http://127.0.0.1:8000/docs: FastAPI's auto-generated docs for the same endpoint. Try it out from there too.
3. Run `python call_backend.py` in a second terminal: same backend, different client, plus the 422.
4. `USE_MOCK=0`: restart, ask again. Now a real model answers, and the meta line shows real tokens and time.
5. Ask: *what if the backend didn't add the system prompt?* (See note below.) Then read `leaky_client.html` together.

## 6.2–6.10 Production LLM API engineering

| File | What it shows | Needs a key? |
|---|---|---|
| `day-06-production-llm-apis.ipynb` | Every number in the slides, from real calls: stateless vs stateful (incl. `previous_response_id`), token growth over a 40-turn chat, sliding window forgets vs summary + window remembers, streaming vs non-streaming timing, real 400/401/404 errors and how to classify them, a timeout, a backoff + jitter retry loop, rate-limit headers, a semaphore capping concurrency, a per-user budget, cost per call, hidden reasoning tokens, TTFT vs total with P50/P95, two models compared on a small task, and fallback on a timeout (but not on a 401) | Yes, `OPENAI_API_KEY` |
| `02_streaming_sse/main.py` + `client.html` | The same question asked two ways side by side in the browser: non-streaming JSON vs streaming over Server-Sent Events (`EventSource`). Shows first-words time vs total time, and an `error` event for failures mid-stream | Yes |

Run the SSE demo with `cd 02_streaming_sse && uvicorn main:app --reload`, then open http://127.0.0.1:8000. Open the notebook in VS Code (pick the `.venv` kernel). A full notebook run makes about 60 API calls and costs under $0.01.

## Setup

```bash
cd day-06/code
uv venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
cp .env.example .env             # USE_MOCK=1 works with no key; paste your OpenAI key for USE_MOCK=0

cd 01_architecture
uvicorn main:app --reload
```

A real call costs a tiny fraction of a cent (about 40 input + 40 output tokens on `gpt-4o-mini`).

## Notes (checked 2026-10-16)

- Model: `gpt-4o-mini` via the Responses API (`client.responses.create(model, instructions, input)`, then `response.output_text` and `response.usage.input_tokens` / `output_tokens`), `openai` 3.31, `fastapi` 0.143, `uvicorn` 0.54, Python 3.13.
- Why context matters: without "Generative AI course" in the system prompt, `gpt-4o-mini` answered "RAG stands for Red, Amber, Green…". With it, it answered "Retrieval-Augmented Generation". The user typed the same thing both times; the backend added the context.
- Responses API: https://developers.openai.com/api/docs/guides/text. API keys belong on the server: https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety
- FastAPI request bodies and validation: https://fastapi.tiangolo.com/tutorial/body/
- Prices per 1M tokens (https://developers.openai.com/api/docs/models/gpt-4o-mini and /gpt-5-mini): `gpt-4o-mini` $0.15 in / $0.60 out; `gpt-5-mini` $0.25 in / $2.00 out. Reasoning tokens are billed as output.
- OpenAI Python SDK defaults (from the 3.31 source): timeout 600 s (connect 5 s), `max_retries=2`, backoff starting at 0.5 s capped at 8 s, retries on 408, 409, 429, 5xx and connection errors.
- Streaming: https://developers.openai.com/api/docs/guides/streaming-responses (text arrives as `response.output_text.delta` events). SSE: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
- Errors: https://developers.openai.com/api/docs/guides/error-codes. Rate limits, headers and backoff: https://developers.openai.com/api/docs/guides/rate-limits. Conversation state: https://developers.openai.com/api/docs/guides/conversation-state
- Lesson from building the notebook: passing old turns to the summariser *as chat messages* made the model answer the last question in them instead of summarising. Pass them as one transcript string.
- LLM output and latency vary between runs, so your answers and timings will differ slightly.
