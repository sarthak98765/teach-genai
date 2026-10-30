"""Talk to the running API. Start it first: sh run.sh

python test.py                                  # live chat, streamed (/chat); type 'exit' to stop
python test.py "What is the punishment for murder?"   # one full answer (/answer)
"""
import json
import sys
import httpx

URL = "http://localhost:8000"
TIMEOUT = 120

def print_sources(sources):
    for s in sources:
        print(f"   [{s['source']}] {s['chunk_id']}, page {s['page']} ({s.get('found_by', '')} score {s['score']:.3f})")

def answer(question):
    response = httpx.post(f"{URL}/answer", json={"question": question}, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    print(f"Bot: {data['answer']}\n\nSources:")
    print_sources(data["sources"])

def chat():
    history = []
    print("Ask Kanoon.ai about Indian law. Type 'exit' to stop.\n")
    while True:
        question = input("You: ").strip()
        if question.lower() in ("", "exit", "quit"):
            break
        history.append({"role": "user", "content": question})
        reply, sources = "", []
        print("-" * 60 + "\nBot: ", end="", flush=True)
        with httpx.stream("POST", f"{URL}/chat", json={"chat": history}, timeout=TIMEOUT) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                event = json.loads(line)
                if event["role"] == "sources":
                    sources = event["content"]
                elif event["role"] == "assistant":
                    reply += event["content"]
                    print(event["content"], end="", flush=True)  # print each piece as it arrives
                elif event["role"] == "error":
                    print(f"\nError: {event['content']}")
        print("\n\nSources:")
        print_sources(sources)
        print("-" * 60)
        history.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    try:
        answer(" ".join(sys.argv[1:])) if sys.argv[1:] else chat()
    except httpx.ConnectError:
        print(f"Can't reach {URL}: start the API first with `sh run.sh` in kanoon-ai/")