from typing import Dict
import logging

import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0 Safari/537.36"
    )
}


logger = logging.getLogger(__name__)


def fetch_html(url: str, timeout: int = 10) -> str:
    """
    Download the raw HTML for a URL.
    """
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def extract_main_text(html: str) -> str:
    """
    Take raw HTML and return the main visible text content.
    - Removes <script>, <style>, <nav>, <footer>, etc.
    - Joins text with reasonable line breaks.
    """
    soup = BeautifulSoup(html, "lxml")

    # Remove non-content elements
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "form"]):
        tag.decompose()

    # Heuristic: if there's an <article> or <main>, prefer that
    main_candidate = soup.find("main") or soup.find("article")
    if main_candidate:
        root = main_candidate
    else:
        root = soup.body or soup

    # Get visible text
    text_chunks = []
    for element in root.stripped_strings:
        text_chunks.append(element)

    text = "\n".join(text_chunks)

    # Deduplicate excessive blank lines
    cleaned_lines = []
    previous_blank = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if not previous_blank:
                cleaned_lines.append("")
            previous_blank = True
        else:
            cleaned_lines.append(stripped)
            previous_blank = False

    return "\n".join(cleaned_lines).strip()


def scrape_url(url: str) -> Dict[str, str]:
    """
    High-level function:
    - Fetch HTML
    - Extract title + main text
    - Return dictionary for upstream modules
    """
    logger.info("Scraping URL: %s", url)
    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    main_text = extract_main_text(html)

    return {
        "url": url,
        "title": title,
        "text": main_text,
    }