import os
import json
import asyncio
from typing import Dict, List
from pydantic import BaseModel, Field

# --- Corrected Imports ---
from crawl4ai import (
    AsyncWebCrawler,
    CrawlerRunConfig,
    LLMConfig,
    CacheMode,
    BrowserConfig
)
# Import ONLY CrawlResult from the 'model' submodule
try:
    # Try the most likely location first
    from crawl4ai.model import CrawlResult
except ImportError:
    try:
        # Try models as a fallback (less likely based on previous error)
         from crawl4ai.models import CrawlResult
    except ImportError:
        # If it's neither, maybe it's directly available? (Least likely)
        try:
            from crawl4ai import CrawlResult
        except ImportError:
            print("ERROR: Could not find CrawlResult class. Please check crawl4ai installation/version.")
            CrawlResult = None # Define as None to prevent further NameErrors later in the script
# --------------------------

from crawl4ai.extraction_strategy import LLMExtractionStrategy
import traceback

# Define the schema for a single review
class CompanyReview(BaseModel):
    title: str = Field(..., description="Title of the review.")
    review_tags: str = Field(..., description="Comma-separated tags associated with the review.")
    review_text: list[str] = Field(..., description="List of paragraphs or distinct parts of the review text.")

# Define a schema for a list of reviews
class ReviewList(BaseModel):
    reviews: List[CompanyReview] = Field(..., description="A list of company reviews extracted from the page.")


async def extract_structured_data_using_llm(
    provider: str, api_token: str = None, extra_headers: Dict[str, str] = None
):
    # Exit if CrawlResult couldn't be imported
    if CrawlResult is None:
        return

    print(f"\n--- Extracting Structured Data with {provider} ---")

    if api_token is None and provider != "ollama":
        print(f"API token is required for {provider}. Skipping this example.")
        return

    browser_config = BrowserConfig(
        headless=True, # Keep True for automation, False for visual debugging
        chrome_channel="chrome"
    )

    extra_args = {"temperature": 0, "top_p": 0.9, "max_tokens": 4000}
    if extra_headers:
        # Typo fixed here: should be extra_args, not extra_argss
        extra_args["extra_headers"] = extra_headers

    crawler_config = CrawlerRunConfig(
        css_selector="div.reviewCard",
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=1,
        page_timeout=80000,
        extraction_strategy=LLMExtractionStrategy(
            llm_config=LLMConfig(
                provider=provider,
                api_token=api_token,
            ),
            schema=ReviewList.model_json_schema(),
            extraction_type="schema",
            instruction=f"""From the provided HTML snippets (each corresponding to a review card), extract the review details. For each review, provide the title, a single string containing all associated tags (comma-separated if multiple), and the review text (as a list of strings, where each string is a paragraph or distinct part of the review). Structure the output as a JSON object containing a list named 'reviews', where each item in the list follows the CompanyReview schema: {CompanyReview.model_json_schema()}""",
            extra_args=extra_args,
        ),
    )

    print(f"Attempting crawl for: https://www.comparably.com/companies/google/reviews")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = None # This will hold the CrawlResult object
        try:
            # Directly assign the result of arun
            result = await crawler.arun(
                url="https://www.comparably.com/companies/google/reviews", config=crawler_config
            )

            # --- Simplified Check: Proceed only if we got a CrawlResult object ---
            if isinstance(result, CrawlResult):
                print("\n--- Raw Crawl Result ---")
                print(f"URL: {result.url}")
                print(f"Success Flag: {result.success}")
                print(f"Status Code: {result.status_code}")
                print(f"Redirected URL: {result.redirected_url}")
                print(f"Error Message: {result.error_message}")
                # Only print headers if they exist
                print(f"Response Headers: {result.response_headers if result.response_headers else 'N/A'}")
                print(f"HTML (first 500 chars): {result.html[:500] if result.html else 'None'}...")
                print(f"Extracted Content (raw): {result.extracted_content}")

                if result.status_code != 200:
                    print(f"\n--- ERROR: Received HTTP Status Code {result.status_code} ---")
                    print("This indicates the request was likely BLOCKED by anti-scraping measures (e.g., Cloudflare).")
                    # ... (rest of the error message for non-200 status) ...

                elif not result.html or "<div class='crawl4ai-result'>\n\n</div>" in result.html:
                     print("\n--- WARNING: Received HTTP 200 but HTML seems empty or minimal ---")
                     # ... (rest of the warning message) ...

                print("\n--- Parsed Extracted Content ---")
                if result.status_code == 200 and result.extracted_content and result.extracted_content.strip() not in ('[]', ''):
                    try:
                        # Handle potential string vs dict/list type for extracted_content
                        if isinstance(result.extracted_content, str):
                           extracted_data = json.loads(result.extracted_content)
                        else:
                           extracted_data = result.extracted_content # Assume already parsed if not string

                        # Check if crawl4ai might have already parsed it into the pydantic model
                        if isinstance(extracted_data, ReviewList):
                             print("Content already parsed as ReviewList:")
                             print(extracted_data.model_dump_json(indent=2))
                        # Check if it's the expected dictionary structure
                        elif isinstance(extracted_data, dict) and 'reviews' in extracted_data:
                            print("Parsing dictionary into ReviewList:")
                            parsed_data = ReviewList(**extracted_data)
                            print(parsed_data.model_dump_json(indent=2))
                        # Check if it's just a list (maybe LLM didn't wrap in 'reviews' key)
                        elif isinstance(extracted_data, list):
                            print("WARNING: Extracted data is a list, not the expected ReviewList structure.")
                            print("Attempting to parse as list of CompanyReview (might fail if format differs):")
                            try:
                                parsed_reviews = [CompanyReview(**item) for item in extracted_data]
                                temp_list = ReviewList(reviews=parsed_reviews)
                                print(temp_list.model_dump_json(indent=2))
                            except Exception as list_parse_e:
                                print(f"Failed to parse list items as CompanyReview: {list_parse_e}")
                                print("Raw list data:")
                                print(json.dumps(extracted_data, indent=2))
                        else:
                             print("Unexpected extracted content format (JSON parsed):")
                             print(json.dumps(extracted_data, indent=2))
                    except (json.JSONDecodeError, TypeError, Exception) as e:
                        print(f"Error processing extracted content: {e}")
                        print("Raw extracted content was:")
                        print(result.extracted_content)

                elif result.extracted_content and result.extracted_content.strip() in ('[]', ''):
                    print("Extraction resulted in an empty list '[]' or empty string.")
                    if result.status_code != 200:
                        print("This is expected due to the non-200 status code (request blocked).")
                    else:
                        print("This might mean no elements matched the CSS selector OR the page content was blocked/empty despite HTTP 200.")
                else:
                    print("No content extracted or content was None.")
            # --- End of processing block for valid CrawlResult ---
            elif result is None:
                 print("Crawler.arun() returned None.")
            else:
                 print(f"Crawler.arun() returned an unexpected type: {type(result)}")

        except Exception as e:
            print(f"\n--- An unexpected error occurred during crawling/extraction ---")
            traceback.print_exc()

if __name__ == "__main__":
    # Add check for CrawlResult import success
    if CrawlResult is None:
        print("Exiting because CrawlResult class could not be imported.")
    else:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("Error: OPENAI_API_KEY environment variable not set.")
        else:
            asyncio.run(
                extract_structured_data_using_llm(
                    provider="openai/gpt-4o-mini", api_token=openai_key
                )
            )