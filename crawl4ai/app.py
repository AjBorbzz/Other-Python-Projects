import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url="https://www.nbcnews.com/business")
        print(f"Basic crawl result: {result.markdown[:500]}")  # Print first 500 characters


if __name__ == "__main__":
    asyncio.run(main())