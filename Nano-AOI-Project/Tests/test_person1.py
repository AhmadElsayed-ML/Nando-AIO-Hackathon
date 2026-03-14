import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from Modules.input_handler import is_url, process_input
from Modules.web_scraper import extract_main_text
from Utils.text_cleaner import clean_text, strip_html, normalize_whitespace
from Data.sample_data import (
    SAMPLE_URLS,
    SAMPLE_RAW_MESSY_TEXT,
    SAMPLE_EXPECTED_CLEAN_SNIPPET,
)
def assert_true(condition, message):
    if condition:
        print(f"[OK]   {message}")
    else:
        print(f"[FAIL] {message}")
def test_is_url_basic():
    print("\n--- test_is_url_basic ---")
    cases = [
        ("https://example.com", True),
        ("http://example.com/path", True),
        ("example.com", True),
        ("sub.domain.co.uk/page", True),
        ("not a url", False),
        ("hello world", False),
        ("", False),
    ]
    for value, expected in cases:
        result = is_url(value)
        assert_true(result is expected, f"is_url({value!r}) == {expected}, got {result}")
def test_strip_html_and_whitespace():
    print("\n--- test_strip_html_and_whitespace ---")
    raw = "<p>Hello   <strong>world</strong></p>"
    stripped = strip_html(raw)
    assert_true("Hello world" in stripped, "strip_html removes tags and keeps text")
    raw_ws = "Hello   \t world \n\n This   is   \t neat "
    cleaned_ws = normalize_whitespace(raw_ws)
    assert_true("  " not in cleaned_ws, "normalize_whitespace collapses multiple spaces")
    assert_true("\t" not in cleaned_ws, "normalize_whitespace removes tabs")
    assert_true("Hello world" in cleaned_ws, "normalize_whitespace keeps words")
def test_clean_text_with_sample_data():
    print("\n--- test_clean_text_with_sample_data ---")
    cleaned = clean_text(SAMPLE_RAW_MESSY_TEXT)
    expected_parts = [
        "Welcome to Nando",
        "We help brands stop getting misunderstood by AI agents.",
        "Our platform cleans messy copy, normalizes tone, and structures information so LLMs don't hallucinate.",
        "Contact us at hello@nando.ai",
    ]
    for part in expected_parts:
        assert_true(part in cleaned, f"clean_text output contains: {part!r}")
def test_extract_main_text_from_simple_html():
    print("\n--- test_extract_main_text_from_simple_html ---")
    html = """
    <html>
      <head><title>Test</title></head>
      <body>
        <nav>Navigation here</nav>
        <main>
          <h1>Title</h1>
          <p>First paragraph.</p>
          <p>Second paragraph.</p>
        </main>
        <footer>Footer info</footer>
      </body>
    </html>
    """
    text = extract_main_text(html)
    assert_true("Navigation" not in text, "extract_main_text removes <nav> content")
    assert_true("Footer" not in text, "extract_main_text removes <footer> content")
    assert_true("Title" in text, "extract_main_text keeps main title")
    assert_true("First paragraph." in text, "extract_main_text keeps first paragraph")
    assert_true("Second paragraph." in text, "extract_main_text keeps second paragraph")
def test_process_input_with_text():
    print("\n--- test_process_input_with_text ---")
    result = process_input(SAMPLE_RAW_MESSY_TEXT)
    assert_true(result["source_type"] == "text", "process_input detects raw text")
    assert_true(isinstance(result["clean_content"], str), "clean_content is a string")
    assert_true(
        "We help brands stop getting misunderstood by AI agents."
        in result["clean_content"],
        "clean_content contains key sentence",
    )
def run_all_tests():
    print("Running Person 1 tests (no pytest)...")
    test_is_url_basic()
    test_strip_html_and_whitespace()
    test_clean_text_with_sample_data()
    test_extract_main_text_from_simple_html()
    test_process_input_with_text()
    print("\nAll Person 1 tests finished.")
if __name__ == "__main__":
    run_all_tests()