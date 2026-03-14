from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any, Dict, List

from Modules.content_analyzer import AnalysisResult, analyze_content_rule_based
from Modules.ai_optimizer import optimize_content_rule_based


def _analysis_result_to_dict(result: AnalysisResult) -> Dict[str, Any]:
    """Convert AnalysisResult (and nested Issues) into plain dicts for the UI."""
    data = asdict(result)
    # Ensure type names are strings (Literal can be non-serializable in some tools)
    for issue in data.get("issues", []):
        issue["type"] = str(issue.get("type", "vague_language"))
    return data


def get_mock_analysis(_: str | None = None) -> Dict[str, Any]:
    """
    Hand-crafted mock result for the 'Jumping Fish Cat Toy' example.

    This ignores the user's text on purpose, so the demo always shows
    the same, polished before/after story with fixed scores.
    """
    original_content = (
        "Our jumping fish cat toy is kinda like this fun thing that moves around when "
        "you plug some USB stuff in or sometimes you can maybe use a battery if you "
        "want but it depends. It kind of flops and jumps in a random way and it should "
        "keep your cat busy for a while, unless it doesn't feel like it. The cable is "
        "sort of long enough and you can charge it somehow through a USB port on "
        "something."
    )

    improved_content = (
        "Product Overview\n"
        "----------------\n"
        "The Jumping Fish Cat Toy is an interactive, motion-activated toy designed to "
        "keep indoor cats engaged and active. When triggered, the fabric fish flops and "
        "jumps in short bursts, simulating the movement of real prey.\n\n"
        "Target Audience (Pet Owners)\n"
        "----------------------------\n"
        "- Indoor cat owners who want to reduce boredom and encourage exercise.\n"
        "- Pet parents looking for a USB-rechargeable toy instead of single-use batteries.\n"
        "- People who need a safe, low-noise toy suitable for apartments or shared spaces.\n\n"
        "Technical Specs\n"
        "--------------\n"
        "- Power: USB-rechargeable lithium battery (included).\n"
        "- Charging: Standard USB-A cable; full charge in approximately 1.5 hours.\n"
        "- Play time: Up to 60 minutes of intermittent play per full charge.\n"
        "- Materials: Soft fabric fish cover with removable electronic core.\n"
        "- Safety: Auto-shutoff after periods of inactivity to prevent overheating.\n"
        "- Usage: Place on the floor, switch on, and allow your cat to interact under supervision.\n"
    )

    analysis_before = {
        "clarity_score": 75,
        "issues": [
            {
                "type": "vague_language",
                "message": "Uses vague phrases like 'kinda like this fun thing' and 'maybe use a battery'.",
                "excerpt": "kinda like this fun thing",
                "suggestion": "Describe the toy and its power options in specific, concrete terms.",
            },
            {
                "type": "structure",
                "message": "Key details (product type, audience, power source) are mixed together in one long paragraph.",
                "excerpt": None,
                "suggestion": "Group information into clear sections such as overview, audience, and technical specs.",
            },
        ],
        "notes": "Mock analysis for Jumping Fish Cat Toy – messy, unstructured copy.",
    }

    analysis_after = {
        "clarity_score": 90,
        "issues": [],
        "notes": "Mock analysis for Jumping Fish Cat Toy – structured, AI-ready copy.",
    }

    metrics = {
        "clarity_before": 75,
        "clarity_after": 90,
        "clarity_improvement": 15,
        "misunderstandings_before": [
            "AI may not clearly identify that this is a USB-rechargeable cat toy.",
            "Power options (USB vs battery) are described in an uncertain, conditional way.",
            "Intended audience (indoor cat owners) is not explicitly stated.",
        ],
        "understanding_after": [
            "AI can confidently recognize the product as a USB-rechargeable, motion-activated cat toy.",
            "AI can infer the target audience as indoor cat owners and pet parents.",
            "AI can list concrete technical specs such as power type, charge time, and safety features.",
        ],
        "explanation": (
            "The AI-ready version removes vague phrases, separates information into clear sections, "
            "and adds explicit technical specs and audience details. This makes it easier for AI tools "
            "to classify the product and answer questions about how it works."
        ),
    }

    summary = (
        "This example shows how messy, informal copy about a USB-powered cat toy can be turned into a "
        "clear, structured description. The optimized version makes it obvious what the product is, who "
        "it is for, and how it works, which significantly improves AI understanding."
    )

    faq: List[Dict[str, str]] = [
        {
            "question": "What is the Jumping Fish Cat Toy?",
            "answer": "An interactive, motion-activated fish toy that flops and jumps to keep indoor cats engaged.",
        },
        {
            "question": "How is the toy powered?",
            "answer": "It uses a built-in, USB-rechargeable lithium battery and comes with a standard USB-A cable.",
        },
        {
            "question": "Who is this toy designed for?",
            "answer": "Indoor cat owners and pet parents who want a safe, rechargeable toy that encourages exercise.",
        },
    ]

    structured_profile = {
        "product_name": "Jumping Fish Cat Toy",
        "category": "Pet accessories / interactive cat toys",
        "target_audience": ["indoor_cat_owners", "pet_parents", "apartment_residents"],
        "key_benefits": [
            "Encourages physical activity and mental stimulation for indoor cats",
            "Rechargeable via USB, reducing battery waste",
            "Clear technical specs that AI systems can parse",
        ],
        "technical_specs": {
            "power": "USB-rechargeable lithium battery",
            "charge_time_minutes": 90,
            "play_time_minutes": 60,
            "auto_shutoff": True,
        },
    }

    return {
        "original": original_content,
        "optimized": improved_content,
        "analysis_before": analysis_before,
        "analysis_after": analysis_after,
        "summary": summary,
        "faq": faq,
        "structured_profile": structured_profile,
        "metrics": metrics,
    }


def run_pipeline(brand_text: str) -> Dict[str, Any]:
    """
    Mock end‑to‑end pipeline for the UI.

    It simulates:
    - Initial analysis of the raw content
    - Optimized "AI‑ready" version
    - Re‑analysis after optimization
    - Brand summary
    - FAQ‑style answers
    - Structured representation for AI agents
    - A scoreboard comparing before vs after
    """
    raw_text = (brand_text or "").strip()
    if not raw_text:
        raw_text = (
            "We do all kinds of stuff for your business. "
            "It's kind of great and helps with things."
        )

    # Use rule‑based components to get realistic‑looking behaviour
    analysis_before = analyze_content_rule_based(raw_text)
    improved_text = optimize_content_rule_based(raw_text, analysis_before.issues)

    # Ensure the optimized text is visibly different and more structured,
    # even when the rule‑based optimizer makes only small changes.
    improved_text = _wrap_as_structured_ai_ready_text(raw_text, improved_text)

    # Re‑analyze after optimization, then gently boost the score so the
    # demo always shows a clear improvement.
    analysis_after_raw = analyze_content_rule_based(improved_text)
    boosted_score = min(100, max(analysis_after_raw.clarity_score, analysis_before.clarity_score + 15))
    analysis_after = replace(analysis_after_raw, clarity_score=boosted_score)

    summary = _build_summary(raw_text, analysis_before, improved_text, analysis_after)
    faq = _build_faq(raw_text, improved_text)
    structured_profile = _build_structured_profile(raw_text, improved_text, analysis_after)
    metrics = _build_metrics(analysis_before, analysis_after)

    return {
        "original": raw_text,
        "analysis_before": _analysis_result_to_dict(analysis_before),
        "optimized": improved_text,
        "analysis_after": _analysis_result_to_dict(analysis_after),
        "summary": summary,
        "faq": faq,
        "structured_profile": structured_profile,
        "metrics": metrics,
    }


def _build_summary(
    original: str,
    before: AnalysisResult,
    improved: str,
    after: AnalysisResult,
) -> str:
    return (
        "This brand offers a business‑focused solution and the content has been rewritten "
        "to be more concrete, structured, and explicit about what it does, for whom, and "
        "what outcomes it delivers. The optimized version reduces vague phrases and adds "
        "clearer signals that AI agents can reliably interpret."
    )


def _build_faq(original: str, improved: str) -> List[Dict[str, str]]:
    return [
        {
            "question": "What does this company do?",
            "answer": (
                "It provides a clearly scoped product or service that helps businesses "
                "improve specific outcomes, rather than a vague 'do everything' offering."
            ),
        },
        {
            "question": "Who is the target audience?",
            "answer": (
                "Primarily business decision‑makers and teams who need a reliable, "
                "data‑driven way to improve their performance."
            ),
        },
        {
            "question": "What benefits does the brand promise?",
            "answer": (
                "Measurable improvements such as better efficiency, more consistent results, "
                "and clearer visibility into performance."
            ),
        },
    ]


def _build_structured_profile(
    original: str,
    improved: str,
    after: AnalysisResult,
) -> Dict[str, Any]:
    """
    A deliberately simple, AI‑friendly schema you can hand to agents.
    """
    return {
        "brand_core": {
            "category": "B2B SaaS or services",
            "primary_audience": ["business owners", "teams", "decision_makers"],
            "primary_benefits": [
                "greater clarity",
                "more specific positioning",
                "clearer outcomes for customers",
            ],
        },
        "messaging_quality": {
            "ai_readiness_score": after.clarity_score,
            "notes": after.notes,
        },
        "content_samples": {
            "optimized_snippet": improved[:400],
        },
    }


def _wrap_as_structured_ai_ready_text(original: str, improved: str) -> str:
    """
    Wrap the improved text in a clearly structured, AI‑friendly template
    so the difference is obvious in the demo.
    """
    base = improved.strip() or original.strip()

    return (
        "AI‑ready brand description (mock)\n"
        "---------------------------------\n\n"
        "What we do:\n"
        "We provide a focused solution that helps businesses achieve clear, measurable outcomes.\n\n"
        "Who we serve:\n"
        "Teams and decision‑makers who need a reliable way to improve performance.\n\n"
        "Key benefits:\n"
        "- Greater clarity in how the offer is described\n"
        "- Easier mapping to product/category for AI systems\n"
        "- More explicit outcomes for customers\n\n"
        "Rewritten message based on your original content:\n"
        f"{base}\n"
    )


def _build_metrics(before: AnalysisResult, after: AnalysisResult) -> Dict[str, Any]:
    improvement = max(1, after.clarity_score - before.clarity_score)

    misunderstandings_before = [
        "AI may not know what the actual product or service is.",
        "AI can confuse the target audience because it is not explicitly stated.",
        "Vague terms like 'stuff' and 'things' make intent ambiguous.",
    ]
    understanding_after = [
        "AI can more reliably infer the product category (e.g., analytics tool, service).",
        "AI can identify the target audience as business users or teams.",
        "AI can describe concrete benefits such as improved performance or efficiency.",
    ]

    return {
        "clarity_before": before.clarity_score,
        "clarity_after": after.clarity_score,
        "clarity_improvement": improvement,
        "misunderstandings_before": misunderstandings_before,
        "understanding_after": understanding_after,
        "explanation": (
            "The optimized version replaces vague language, fills in missing context, "
            "and presents information in a more structured way. This makes it easier "
            "for AI tools to map the brand to the right category, audience, and benefits."
        ),
    }

