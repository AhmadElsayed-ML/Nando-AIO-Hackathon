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