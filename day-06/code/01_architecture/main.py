"""Day 06.1: LLM application architecture.

Client -> Backend -> Model API, as one small FastAPI app.

    GET  /       the client: a one-page chat UI (client.html)
    POST /chat   the backend: validate, build the prompt, call the model, return the reply

Run (from day-06/code/01_architecture):
    uvicorn main:app --reload
Then open http://127.0.0.1:8000

USE_MOCK=1 in .env -> a fake model, no key, no cost (step 1 of the demo)
USE_MOCK=0 in .env -> the real OpenAI model (step 2 of the demo)
"""

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).parent.parent / ".env")

USE_MOCK = os.getenv("USE_MOCK", "1") == "1"
MODEL = "gpt-4o-mini"
# Without "Generative AI course", gpt-4o-mini read "RAG" as Red/Amber/Green.
# Adding context like this is the backend's job, not the user's.
SYSTEM_PROMPT = ("You are a friendly tutor in a Generative AI engineering course. "
                 "Answer in 3 short sentences, in simple words.")

app = FastAPI(title="Day 06.1: Client -> Backend -> Model API")

# The key is read HERE, on the server. The browser never sees it.
openai_client = None if USE_MOCK else OpenAI()  # reads OPENAI_API_KEY from the environment


# ---------- 1. The contract between client and backend ----------
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)  # validation: FastAPI returns 422 if broken


class ChatResponse(BaseModel):
    reply: str
    model: str
    input_tokens: int
    output_tokens: int
    model_ms: int  # time spent waiting on the model API


# ---------- 2. The model API (mock first, then real) ----------
def mock_model_api(instructions: str, user_message: str) -> dict:
    print(f"  [model API] (mock) received: {user_message!r}")
    time.sleep(0.5)  # pretend inference takes time
    return {
        "text": "RAG means the app first looks up relevant documents, then gives them to the model "
        "so it answers from real sources instead of memory. (This is the MOCK model, not a real LLM.)",
        "model": "mock-model",
        "input_tokens": 0,
        "output_tokens": 0,
    }


def openai_model_api(instructions: str, user_message: str) -> dict:
    print(f"  [model API] (OpenAI {MODEL}) received: {user_message!r}")
    response = openai_client.responses.create(
        model=MODEL,
        instructions=instructions,
        input=user_message,
    )
    return {
        "text": response.output_text,
        "model": response.model,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }


def call_model(instructions: str, user_message: str) -> dict:
    if USE_MOCK:
        return mock_model_api(instructions, user_message)
    return openai_model_api(instructions, user_message)


# ---------- 3. The backend endpoint ----------
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    print(f"\n[backend] received from client: {request.message!r}")

    # (auth would go here: who is this user, are they over their budget?)

    # Build the prompt: the backend adds the system instructions, not the client
    instructions = SYSTEM_PROMPT

    start = time.perf_counter()
    try:
        result = call_model(instructions, request.message)
    except Exception as e:
        # Never send provider errors (or keys) to the client as-is
        print(f"[backend] model API failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=502, detail="The AI service failed. Please try again.")
    model_ms = round((time.perf_counter() - start) * 1000)

    print(f"[backend] model replied in {model_ms} ms, "
          f"{result['input_tokens']} in / {result['output_tokens']} out tokens")
    return ChatResponse(reply=result["text"], model=result["model"],
                        input_tokens=result["input_tokens"], output_tokens=result["output_tokens"],
                        model_ms=model_ms)


# ---------- 4. Serve the client ----------
@app.get("/")
def client():
    return FileResponse(Path(__file__).parent / "client.html")
