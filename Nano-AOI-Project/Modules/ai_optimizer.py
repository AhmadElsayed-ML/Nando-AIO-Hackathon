# ai_optimizer.py
from typing import List
from Modules.content_analyzer import Issue
from Utils.prompts import OPTIMIZATION_PROMPT, ISSUES_SECTION_PREFIX

try:
    import openai  # type: ignore[import]
except ImportError:
    openai = None

try:
    import anthropic  # type: ignore[import]
except ImportError:
    anthropic = None


def _format_issues_for_prompt(issues: List[Issue]) -> str:
    lines = []
    for i, issue in enumerate(issues, start=1):
        line = f"{i}. [{issue.type}] {issue.message}"
        if issue.excerpt:
            line += f' (excerpt: "{issue.excerpt}")'
        if issue.suggestion:
            line += f" Suggestion: {issue.suggestion}"
        lines.append(line)
    return "\n".join(lines)


def optimize_content_rule_based(original: str, issues: List[Issue]) -> str:
    """
    Very simple deterministic "optimizer":
    - Replace vague terms with more specific placeholders.
    - This is enough for tests and as API fallback.
    """
    improved = original

    replacements = {
        "stuff": "features and services",
        "things": "details",
        "maybe": "in some cases",
        "kind of": "somewhat",
        "sort of": "somewhat",
    }

    for vague, concrete in replacements.items():
        improved = improved.replace(vague, concrete)
        improved = improved.replace(vague.capitalize(), concrete.capitalize())

    if not improved.strip():
        improved = "Content could not be optimized. Please provide more details."

    return improved


def _call_ai_optimizer(original: str, issues: List[Issue], provider: str = "openai") -> str:
    issues_str = _format_issues_for_prompt(issues)
    prompt = (
        OPTIMIZATION_PROMPT
        + original
        + ISSUES_SECTION_PREFIX
        + "\n"
        + (issues_str if issues_str else "No issues detected; focus on clarity and structure.")
    )

    if provider == "openai":
        if openai is None:
            raise RuntimeError("openai library not available")

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        content = response.choices[0].message.content
    elif provider == "anthropic":
        if anthropic is None:
            raise RuntimeError("anthropic library not available")

        client = anthropic.Anthropic()
        msg = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1200,
            temperature=0.4,
            messages=[{"role": "user", "content": prompt}],
        )
        content = "".join(block.text for block in msg.content if getattr(block, "type", "") == "text")
    else:
        raise ValueError(f"Unknown provider: {provider}")

    return content.strip()
    

def optimize_content(original: str, issues: List[Issue], use_ai: bool = True, provider: str = "openai") -> str:
    """
    Public API:
    - If use_ai is True, try AI; on ANY error, fall back to rule-based.
    - If use_ai is False, use rule-based directly.
    """
    if not use_ai:
        return optimize_content_rule_based(original, issues)

    try:
        return _call_ai_optimizer(original, issues, provider=provider)
    except Exception:
        return optimize_content_rule_based(original, issues)