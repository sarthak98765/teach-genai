"""A second client: the same backend, called from a Python script instead of a browser.

The backend doesn't care who the client is (browser, mobile app, script):
it only sees an HTTP request to POST /chat.

Run while `uvicorn main:app --reload` is running in another terminal:
    python call_backend.py
"""

import httpx

BACKEND = "http://127.0.0.1:8000"

# 1. A normal request
r = httpx.post(f"{BACKEND}/chat", json={"message": "Explain RAG in simple words"}, timeout=60)
print(r.status_code, r.json())

# 2. A bad request: empty message. The backend rejects it before any model call (no cost)
r = httpx.post(f"{BACKEND}/chat", json={"message": ""}, timeout=60)
print(r.status_code, r.json()["detail"][0]["msg"])
