"""The full pipeline: web search → crawl the top 3 pages → LLM with a prompt → strict structured output.
Outputs: outputs/cutoffs.json (the structured data) and outputs/pipeline.md (URLs, table, full pages).
"""
import asyncio
from datetime import date
from pathlib import Path
from openai import OpenAI
from crawl import crawl
from prompts import CUTOFF_EXTRACTION_PROMPT
from pydantic_models import CutoffReport
from web_search import web_search

client = OpenAI()  # the key was loaded from ../.env by web_search.py
OUTPUTS = Path(__file__).parent / "outputs"

def pipeline(query: str, top: int = 3) -> CutoffReport:
    """Search exactly `query`, crawl the top `top` URLs, and extract a CutoffReport from those pages."""
    # 1. Web search: the top 3 URLs for the query, as it is
    urls = [r["url"] for r in web_search(query)[:top]]

    # 2. Crawl: each full page as Markdown
    pages = []
    for url in urls:
        try:
            pages.append(asyncio.run(crawl(url)))
        except Exception as e:  # one bad page shouldn't stop the others
            pages.append(f"(could not crawl: {e})")

    # 3. LLM: the prompt + the pages in, a CutoffReport out (strict structured output)
    sources = "\n\n".join(f"### SOURCE {i}\nURL: {u}\n\n{p[:50_000]}" for i, (u, p) in enumerate(zip(urls, pages), 1))
    response = client.responses.parse(
        model="gpt-5-mini", reasoning={"effort": "low"},
        instructions=CUTOFF_EXTRACTION_PROMPT.format(date=date.today()),
        input=f"Query: {query}\n\n{sources}",
        text_format=CutoffReport,
    )
    report = response.output_parsed

    # 4. Save: the JSON, and a readable Markdown file
    OUTPUTS.mkdir(exist_ok=True)
    (OUTPUTS / "cutoffs.json").write_text(report.model_dump_json(indent=2))
    table = ["| Program | Quota | Opening | Closing |", "|---|---|---|---|"]
    table += [f"| {c.program} | {c.quota} | {c.opening_rank} | {c.closing_rank} |" for c in report.cutoffs]
    out = [f"# Query\n\n{query}\n\n# Top {top} URLs\n"] + [f"{i}. {u}" for i, u in enumerate(urls, 1)]
    out += [f"\n# Structured output\n\n**{report.college}** · {report.exam} {report.year} · {report.round} · {report.category}\n",
            *table, f"\nNotes: {report.notes}\n\nFull JSON: `outputs/cutoffs.json`"]
    out += [f"\n---\n\n# Page {i}: {u}\n\n{len(p.split()):,} words, crawled as it is:\n\n{p}" for i, (u, p) in enumerate(zip(urls, pages), 1)]
    (OUTPUTS / "pipeline.md").write_text("\n".join(out))
    return report


if __name__ == "__main__":
    print(pipeline("NIT Trichy cutoff 2026").model_dump_json(indent=2))