"""Tool 2: crawl a web page. Open it in a real (headless) browser and turn the whole page into Markdown."""
import asyncio
from pathlib import Path
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

async def crawl(url: str) -> str:
    """The entire page at `url` as Markdown, as it is (nothing filtered out)."""
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False))
    if not result.success:
        raise RuntimeError(f"could not crawl {url}: {result.error_message}")
    return result.markdown.raw_markdown

if __name__ == "__main__":
    url = "https://nextjs.org/blog/next-16-4"
    markdown = asyncio.run(crawl(url))
    Path(__file__).parent.joinpath("outputs/crawl.md").write_text(f"<!-- crawled from {url} -->\n\n{markdown}")
    print(f"{len(markdown.split())} words from {url}\n\n{markdown[:1500]}")