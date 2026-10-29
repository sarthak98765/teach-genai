import json
from contextlib import asynccontextmanager
from typing import Dict, List, Literal, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from data_ingestion.logger import custom_logger
from retrieval import ask, notice_for, qdrant, retrieve, stream_answer

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    chat: List[Message]            # the whole conversation, last message = the new question
    act_id: Optional[str] = None   # e.g. "bns"; None = search every Act

class AnswerRequest(BaseModel):
    question: str
    act_id: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    qdrant.close()  # local mode holds a lock on data/qdrant until closed
    custom_logger.info("shutdown | Qdrant closed")

app = FastAPI(title="Kanoon.ai", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def to_sources(chunks: List[Dict]) -> List[Dict]:
    """What the UI shows under an answer: which [S1] is which page, with the official link."""
    return [{k: c[k] for k in ("source", "chunk_id", "act", "page", "score", "source_url")} for c in chunks]

@app.get("/health")
def health():
    return {"status": "OK"}

@app.post("/answer")
def answer(request: AnswerRequest):
    """One question -> one full answer (JSON)."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")
    result = ask(request.question, request.act_id)
    custom_logger.info(f"answer | {request.question!r} -> {[c['chunk_id'] for c in result['chunks']]}")
    return {"answer": result["answer"], "sources": to_sources(result["chunks"])}

@app.post("/chat")
def chat(request: ChatRequest):
    """Chat -> streamed answer, one JSON object per line: first the sources, then the text as it is written."""
    if not request.chat or request.chat[-1].role != "user" or not request.chat[-1].content.strip():
        raise HTTPException(status_code=400, detail="chat must end with a user message")
    question = request.chat[-1].content
    history = [m.model_dump() for m in request.chat[:-1]]

    def stream():
        try:
            chunks = retrieve(question, request.act_id)
            custom_logger.info(f"chat | {question!r} -> {[c['chunk_id'] for c in chunks]}")
            yield json.dumps({"role": "sources", "content": to_sources(chunks)}) + "\n"
            answer = ""
            for delta in stream_answer(question, chunks, history):
                answer += delta
                yield json.dumps({"role": "assistant", "content": delta}) + "\n"
            if notice := notice_for(answer):
                yield json.dumps({"role": "assistant", "content": notice}) + "\n"
        except Exception as e:
            custom_logger.error(f"chat | {e}", exc_info=True)
            yield json.dumps({"role": "error", "content": str(e)}) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson")