import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig,CacheMode
urls = [
    "https://www.comparably.com/companies/google/reviews",
    "https://www.teamblind.com/company/Google/reviews",
    "https://socialblade.com/youtube/handle/jamunatvbd"
],

async def main():
    browser_conf = BrowserConfig(headless=True) 
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(
            url="https://socialblade.com/youtube/handle/jamunatvbd",
            config=run_conf
        )
        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())