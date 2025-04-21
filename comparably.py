import os
import json
import asyncio
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig,BrowserConfig, CacheMode
from typing import Dict, List, Any
from crawl4ai.extraction_strategy import LLMExtractionStrategy

class CompanyReview(BaseModel): 
    reviewer: str = Field(..., description="Name of the reviewer.") 
    job_title: str = Field(..., description="Reviewer job title or position.") 
    # rating: float = Field(..., description="Overall rating given by the reviewer.") 
    review_title: str = Field(None, description="Title or summary of the review (if available).") 
    review_text: str = Field(..., description="Detailed content of the review.") 
    # review_date: str = Field(None, description="Date when the review was posted.")

async def extract_structured_data_using_llm(
    provider: str, api_token: str = None, extra_headers: Dict[str, str] = None
):
    print(f"\n--- Extracting Structured Data with {provider} ---")

    if api_token is None and provider != "ollama":
        print(f"API token is required for {provider}. Skipping this example.")
        return

    browser_config = BrowserConfig(headless=True)

    extra_args = {"temperature": 0, "top_p": 0.9, "max_tokens": 2000}
    if extra_headers:
        extra_args["extra_headers"] = extra_headers

    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=1,
        page_timeout=80000,
        extraction_strategy=LLMExtractionStrategy(
        llm_config=LLMConfig(provider=provider, api_token=api_token),
        schema=CompanyReview.model_json_schema(),
        extraction_type="schema",
        instruction="""From the crawled content, extract all company reviews with the following details:
        reviewer name, job title or position, overall rating, review title (if available), detailed review text, and review date.
        Do not miss any reviews on the page.""",
        extra_args=extra_args,
    ),
)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://www.comparably.com/companies/google/reviews", config=crawler_config
        )
        print(result.extracted_content)

if __name__ == "__main__":

    asyncio.run(
        extract_structured_data_using_llm(
            provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY")
        )
    )