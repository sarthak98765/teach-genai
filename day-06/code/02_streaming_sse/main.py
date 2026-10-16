"""Day 06.4: Streaming to the browser with Server-Sent Events (SSE).

    GET /             the client (client.html): two buttons, streaming vs non-streaming
    GET /chat         non-streaming: waits for the whole answer, returns JSON
    GET /chat/stream  streaming: forwards each chunk to the browser as an SSE event

Run (from day-06/code/02_streaming_sse):
    uvicorn main:app --reload
Then open http://127.0.0.1:8000
"""

import json
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent / ".env")

MODEL = "gpt-4o-mini"
INSTRUCTIONS = "You are a tutor in a Generative AI engineering course. Use simple words."

app = FastAPI(title="Day 06.4: streaming with SSE")
client = OpenAI(timeout=30, max_retries=2)


@app.get("/chat")
def chat(message: str):
    start = time.perf_counter()
    r = client.responses.create(model=MODEL, instructions=INSTRUCTIONS, input=message)
    return {"reply": r.output_text, "total_ms": round((time.perf_counter() - start) * 1000)}


def sse(event: str, data: dict) -> str:
    # The whole SSE wire format: an "event:" line, a "data:" line, then a blank line
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.get("/chat/stream")
def chat_stream(message: str):
    def generate():
        start = time.perf_counter()
        try:
            stream = client.responses.create(model=MODEL, instructions=INSTRUCTIONS, input=message, stream=True)
            for event in stream:
                if event.type == "response.output_text.delta":
                    yield sse("delta", {"text": event.delta})          # forward, don't buffer
                elif event.type == "response.completed":
                    u = event.response.usage
                    yield sse("done", {"total_ms": round((time.perf_counter() - start) * 1000),
                                       "input_tokens": u.input_tokens, "output_tokens": u.output_tokens})
        except Exception as e:
            # The 200 status is already sent, so an error mid-stream must be an EVENT, not a status code
            print(f"[backend] stream failed: {type(e).__name__}: {e}")
            yield sse("error", {"message": "The AI service failed. Please try again."})

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/")
def index():
    return FileResponse(Path(__file__).parent / "client.html")
