import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
url = [
    "https://www.comparably.com/companies/google/reviews",
    "https://www.teamblind.com/company/Google/reviews"
]
async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.comparably.com/companies/google/reviews",
        )
        print(result.markdown)  # Show the first 300 characters of extracted text

if __name__ == "__main__":
    asyncio.run(main())