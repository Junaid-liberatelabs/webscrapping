import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.glassdoor.com/Reviews/Microsoft-Reviews-E1651.htm",
        )
        print(result.markdown)  # Show the first 300 characters of extracted text

if __name__ == "__main__":
    asyncio.run(main())