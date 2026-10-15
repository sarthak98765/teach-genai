"""Tool 1: web search. Ask Google (through the Serper API) and get the top results back."""
import os
from pathlib import Path
import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

def web_search(query: str, num: int = 10) -> list[dict]:
    """Top Google results for `query`: title, url and snippet for each."""
    response = httpx.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": os.environ["SERPER_API_KEY"]},
        json={"q": query, "num": num, "gl": "in"},  # gl = country: search like Google in India
        timeout=15,
    )
    response.raise_for_status()
    return [{"title": r["title"], "url": r["link"], "snippet": r.get("snippet", "")}
            for r in response.json().get("organic", [])]

if __name__ == "__main__":
    query = "Next.js 16.4 release notes"
    results = web_search(query)[:3]  # show the top 3
    lines = [f"# Web search: `{query}`\n"] + [f"{i}. [{r['title']}]({r['url']})  \n   {r['snippet']}" for i, r in enumerate(results, 1)]
    Path(__file__).parent.joinpath("outputs/web_search.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))