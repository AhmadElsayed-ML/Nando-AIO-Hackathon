# content_analyzer.py
from dataclasses import dataclass
from typing import List, Literal, Optional, Dict, Any
import re

try:
    import openai  # type: ignore[import]
except ImportError:  # library not installed – fine for fallback
    openai = None

try:
    import anthropic  # type: ignore[import]
except ImportError:
    anthropic = None

IssueType = Literal[
    "vague_language",
    "missing_information",
    "inconsistency",
    "tone_mismatch",
    "structure"
]

import json
from typing import Tuple
from Utils.prompts import ANALYSIS_PROMPT
    

@dataclass
class Issue:
    type: IssueType
    message: str
    excerpt: Optional[str] = None
    suggestion: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AnalysisResult:
    clarity_score: int  # 0–100
    issues: List[Issue]
    notes: Optional[str] = None

VAGUE_WORDS = [
    "stuff", "things", "maybe", "kind of", "sort of",
    "nice", "good", "great", "really good", "etc", "and so on"
]

PRODUCT_KEYWORDS = ["product", "service", "solution", "platform", "app", "tool"]
AUDIENCE_KEYWORDS = ["customers", "clients", "users", "businesses", "teams", "marketers"]
BENEFIT_KEYWORDS = ["save time", "increase revenue", "boost", "improve", "optimize", "simplify"]


def _call_ai_analysis(text: str, provider: str = "openai") -> Tuple[int, List[Issue], str]:
    """
    Very thin wrapper. Assumes environment variables / clients are configured.
    If anything fails, raise and let caller fall back to rules.
    """
    prompt = ANALYSIS_PROMPT + text

    # NOTE: You MUST adapt this to your actual client versions.
    if provider == "openai":
        if openai is None:
            raise RuntimeError("openai library not available")

        # Example using ChatCompletion-like interface; adjust for your SDK.
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = response.choices[0].message.content
    elif provider == "anthropic":
        if anthropic is None:
            raise RuntimeError("anthropic library not available")

        client = anthropic.Anthropic()
        msg = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=800,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )
        # Claude v3 Python SDK returns a list of content blocks; adjust as needed.
        content = "".join(block.text for block in msg.content if getattr(block, "type", "") == "text")
    else:
        raise ValueError(f"Unknown provider: {provider}")

    data = json.loads(content)
    clarity_score = int(data.get("clarity_score", 0))
    issues_data = data.get("issues", [])

    issues: List[Issue] = []
    for item in issues_data:
        issues.append(
            Issue(
                type=item.get("type", "vague_language"),  # default if missing
                message=item.get("message", ""),
                excerpt=item.get("excerpt"),
                suggestion=item.get("suggestion"),
            )
        )

    return clarity_score, issues, "AI analysis (provider: " + provider + ")"


def analyze_content(text: str, use_ai: bool = True, provider: str = "openai") -> AnalysisResult:
    """
    Public API:
    - If use_ai is True, try AI first; on ANY error, fall back to rule-based.
    - If use_ai is False, use rule-based directly.
    """
    if not use_ai:
        return analyze_content_rule_based(text)

    try:
        clarity, issues, notes = _call_ai_analysis(text, provider=provider)
        # Optionally also run rules to add deterministic checks:
        rule_result = analyze_content_rule_based(text)
        combined_issues = issues + rule_result.issues
        final_score = int((clarity + rule_result.clarity_score) / 2)
        return AnalysisResult(
            clarity_score=final_score,
            issues=combined_issues,
            notes=notes + " + rule-based checks"
        )
    except Exception:
        # Silent fallback – you can log if desired
        return analyze_content_rule_based(text)


def _find_vague_language(text: str) -> List[Issue]:
    issues: List[Issue] = []
    lower = text.lower()
    for term in VAGUE_WORDS:
        if term in lower:
            issues.append(
                Issue(
                    type="vague_language",
                    message=f'Vague term detected: "{term}"',
                    excerpt=term,
                    suggestion="Replace with a specific, concrete description."
                )
            )
    return issues


def _detect_missing_information(text: str) -> List[Issue]:
    issues: List[Issue] = []
    lower = text.lower()

    def has_any(keywords: list[str]) -> bool:
        return any(k in lower for k in keywords)

    if not has_any(PRODUCT_KEYWORDS):
        issues.append(
            Issue(
                type="missing_information",
                message="No clear product or service is described.",
                suggestion="Explicitly state what the company offers."
            )
        )
    if not has_any(AUDIENCE_KEYWORDS):
        issues.append(
            Issue(
                type="missing_information",
                message="No clear target audience is mentioned.",
                suggestion="Specify who the product or service is for."
            )
        )
    if not has_any(BENEFIT_KEYWORDS):
        issues.append(
            Issue(
                type="missing_information",
                message="Benefits or outcomes are not clearly described.",
                suggestion="Explain what results or benefits customers get."
            )
        )
    return issues


INCONSISTENCY_PATTERNS = [
    (r"\b24/7\b.*\bnot always available\b", "Claims 24/7 availability but also says not always available."),
    (r"\bno contracts\b.*\b12-month contract\b", "Says 'no contracts' but also mentions a 12‑month contract."),
]


def _detect_inconsistencies(text: str) -> List[Issue]:
    issues: List[Issue] = []
    lower = text.lower()
    for pattern, description in INCONSISTENCY_PATTERNS:
        if re.search(pattern, lower, flags=re.DOTALL):
            issues.append(
                Issue(
                    type="inconsistency",
                    message=description,
                    suggestion="Align these statements so they don’t conflict."
                )
            )
    return issues


def _compute_clarity_score(issues: List[Issue], base: int = 90) -> int:
    """
    Simple heuristic:
    - Start at 90
    - Subtract 5 for each issue (up to 10 issues)
    - Clamp to [0, 100]
    """
    penalty = min(len(issues), 10) * 5
    score = max(0, min(100, base - penalty))
    return score

def analyze_content_rule_based(text: str) -> AnalysisResult:
    """
    Pure rule-based analysis. No external APIs.
    """
    issues: List[Issue] = []
    issues.extend(_find_vague_language(text))
    issues.extend(_detect_missing_information(text))
    issues.extend(_detect_inconsistencies(text))

    clarity_score = _compute_clarity_score(issues)
    notes = "Rule-based analysis only (no AI API)."

    return AnalysisResult(clarity_score=clarity_score, issues=issues, notes=notes)