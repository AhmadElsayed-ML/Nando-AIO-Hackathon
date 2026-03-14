import re
from typing import Dict, Any

from .web_scraper import scrape_url
from Utils.text_cleaner import clean_text


URL_REGEX = re.compile(
    r"^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(:\d+)?(/.*)?$"
)


def is_url(user_input: str) -> bool:
    """
    Heuristic check: does the string look like a URL?
    """
    if not user_input:
        return False
    candidate = user_input.strip()
    return bool(URL_REGEX.match(candidate))


def normalize_url(url: str) -> str:
    """
    Ensure the URL has a scheme (http/https).
    """
    url = url.strip()
    if not url.lower().startswith(("http://", "https://")):
        return "https://" + url
    return url


def process_input(user_input: str) -> Dict[str, Any]:
    """
    Main entry point for your part of the system.

    - If user_input is a URL: scrape + clean.
    - If user_input is raw text: clean directly.

    Returns a dict that later modules can use.
    """
    if not user_input or not user_input.strip():
        raise ValueError("Input is empty.")

    raw_input = user_input.strip()

    if is_url(raw_input):
        url = normalize_url(raw_input)
        scraped = scrape_url(url)
        raw_content = scraped.get("text", "")
        cleaned = clean_text(raw_content)
        return {
            "source_type": "url",
            "original_input": raw_input,
            "url": url,
            "raw_content": raw_content,
            "clean_content": cleaned,
            "metadata": {
                "page_title": scraped.get("title"),
                "content_length": len(cleaned),
            },
        }

    # Treat as raw text
    raw_content = raw_input
    cleaned = clean_text(raw_content)
    return {
        "source_type": "text",
        "original_input": raw_input,
        "url": None,
        "raw_content": raw_content,
        "clean_content": cleaned,
        "metadata": {
            "content_length": len(cleaned),
        }
    }