import re
from typing import List

from bs4 import BeautifulSoup


WHITESPACE_REGEX = re.compile(r"\s+")
CONTROL_CHARS_REGEX = re.compile(r"[\x00-\x08\x0b-\x0c\x0e-\x1f]")


def strip_html(raw: str) -> str:
    """
    Remove HTML tags from a string safely using BeautifulSoup.
    """
    if not raw:
        return ""
    soup = BeautifulSoup(raw, "lxml")
    text = soup.get_text(separator="\n")
    return text


def normalize_whitespace(text: str) -> str:
    """
    Collapse multiple spaces/tabs/newlines into clean line-based text.
    """
    if not text:
        return ""
    # Remove control characters
    text = CONTROL_CHARS_REGEX.sub(" ", text)
    # Normalize within each line, then clean up blank lines
    lines: List[str] = []
    for line in text.splitlines():
        norm = WHITESPACE_REGEX.sub(" ", line).strip()
        lines.append(norm)

    # Remove consecutive blank lines
    cleaned_lines: List[str] = []
    previous_blank = False
    for line in lines:
        if not line:
            if not previous_blank:
                cleaned_lines.append("")
            previous_blank = True
        else:
            cleaned_lines.append(line)
            previous_blank = False

    return "\n".join(cleaned_lines).strip()


def remove_special_characters(text: str) -> str:
    """
    Remove stray non-text symbols while keeping punctuation.
    Adjust the allowed characters as needed.
    """
    if not text:
        return ""
    # Keep letters, numbers, basic punctuation and whitespace.
    # Replace disallowed characters with a space.
    cleaned_chars = []
    for ch in text:
        if ch.isalnum() or ch.isspace() or ch in ".,;:!?\"'()[]{}-_/&%+@#":
            cleaned_chars.append(ch)
        else:
            cleaned_chars.append(" ")
    cleaned = "".join(cleaned_chars)
    return cleaned


def clean_text(raw: str) -> str:
    """
    Full cleaning pipeline:

    1. Strip HTML tags (if any are present).
    2. Normalize whitespace and line breaks.
    3. Remove weird/special characters.
    4. Normalize whitespace again.

    Returns a single clean string ready for analysis.
    """
    if not raw:
        return ""

    text = strip_html(raw)
    text = normalize_whitespace(text)
    text = remove_special_characters(text)
    text = normalize_whitespace(text)
    return text