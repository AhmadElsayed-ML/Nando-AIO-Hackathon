# sample_data.py
from Modules.content_analyzer import Issue, IssueType

BAD_BRAND_CONTENT = """
We do all kinds of stuff for your business. 
It's kind of great and helps with things.
Maybe it will improve your results and etc.
Contact us to learn more.
"""

GOOD_BRAND_CONTENT = """
We provide a cloud-based analytics platform for small and mid-sized e-commerce businesses.
Our product helps marketing and operations teams automatically track performance,
identify underperforming campaigns, and optimize ad spend in real time.
Customers typically increase their return on ad spend by 20–30% within three months.
"""

EXPECTED_ISSUES_FOR_BAD = [
    Issue(
        type="vague_language",
        message='Vague term detected: "stuff"',
        excerpt="stuff",
        suggestion="Replace with a specific, concrete description."
    ),
    Issue(
        type="vague_language",
        message='Vague term detected: "things"',
        excerpt="things",
        suggestion="Replace with a specific, concrete description."
    ),
]

"""
Sample data to help you test the input pipeline
without depending on anyone else's modules.
"""

SAMPLE_URLS = [
    "https://example.com",
    "https://www.python.org",
]

SAMPLE_RAW_MESSY_TEXT = """
<div>
  <h1>Welcome to Nando!!!</h1>
  <p>We help brands stop <b>getting misunderstood</b> by AI agents.</p>
  <p>   Our platform cleans messy copy, normalizes tone,
      and structures information so LLMs don't hallucinate. </p>
  <script>console.log('ignore me');</script>
  <p>   Contact us at hello@nando.ai 💥🚀 </p>
</div>
"""

SAMPLE_EXPECTED_CLEAN_SNIPPET = (
    "Welcome to Nando!!!\n"
    "We help brands stop getting misunderstood by AI agents.\n"
    "Our platform cleans messy copy, normalizes tone, and structures information so "
    "LLMs don't hallucinate.\n"
    "Contact us at hello@nando.ai"
)