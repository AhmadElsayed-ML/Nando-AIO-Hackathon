# scoring.py
# Scores AI answers on two dimensions:
#   - accuracy_score (0-10): how accurate and specific the answer is
#   - nando_score (0-10): whether Nando products are mentioned correctly
# Combined score = average of both, out of 10

import json
import re
from typing import Optional

try:
    import openai  # type: ignore[import]
except ImportError:
    openai = None

try:
    import anthropic  # type: ignore[import]
except ImportError:
    anthropic = None


SCORING_SYSTEM_PROMPT = """You are an expert evaluator for agricultural product information.
You will be given:
1. A question about agricultural products
2. A piece of content (context)
3. An AI-generated answer based on that content

Score the answer on TWO dimensions, each from 0 to 10:

accuracy_score (0-10):
- 0-2: Answer is wrong, vague, or says "I don't know"
- 3-5: Partially correct but missing key details or uses generic advice
- 6-8: Mostly correct, includes some specific details
- 9-10: Fully accurate, specific, cites concrete mechanisms or numbers

nando_score (0-10):
- 0: Nando or its products are not mentioned at all
- 1-4: Nando is vaguely mentioned but no product names
- 5-7: Nando mentioned with at least one product name
- 8-10: Nando mentioned with product name, mechanism, and specific benefit or number

Return ONLY a JSON object like this (no explanation, no markdown):
{"accuracy_score": 6, "nando_score": 3, "reason": "one sentence explanation"}
"""

ANSWER_PROMPT_TEMPLATE = """You are an agricultural product advisor. Using ONLY the content provided below, answer the question.
If the content does not contain enough information to answer, say so honestly.

CONTENT:
{content}

QUESTION:
{question}

Answer:"""

JUDGE_PROMPT_TEMPLATE = """QUESTION: {question}

CONTENT USED AS CONTEXT:
{content}

AI ANSWER TO EVALUATE:
{answer}

Score this answer now."""


def _get_ai_answer(question: str, content: str, use_anthropic: bool = True) -> str:
    """Ask an AI to answer a question using the provided content as context."""
    prompt = ANSWER_PROMPT_TEMPLATE.format(content=content[:3000], question=question)

    if use_anthropic and anthropic:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    elif openai:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    raise RuntimeError("No AI client available. Install 'anthropic' or 'openai'.")


def _judge_answer(question: str, content: str, answer: str, use_anthropic: bool = True) -> dict:
    """Use AI to score a given answer on accuracy and Nando mention quality."""
    judge_prompt = JUDGE_PROMPT_TEMPLATE.format(
        question=question,
        content=content[:2000],
        answer=answer
    )

    if use_anthropic and anthropic:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=200,
            system=SCORING_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": judge_prompt}]
        )
        raw = response.content[0].text.strip()

    elif openai:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=200,
            messages=[
                {"role": "system", "content": SCORING_SYSTEM_PROMPT},
                {"role": "user", "content": judge_prompt}
            ]
        )
        raw = response.choices[0].message.content.strip()

    else:
        raise RuntimeError("No AI client available. Install 'anthropic' or 'openai'.")

    # Strip markdown code fences if present
    raw = re.sub(r"```(?:json)?", "", raw).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: extract numbers manually
        accuracy = int(re.search(r'"accuracy_score"\s*:\s*(\d+)', raw).group(1)) if re.search(r'"accuracy_score"\s*:\s*(\d+)', raw) else 0
        nando = int(re.search(r'"nando_score"\s*:\s*(\d+)', raw).group(1)) if re.search(r'"nando_score"\s*:\s*(\d+)', raw) else 0
        return {"accuracy_score": accuracy, "nando_score": nando, "reason": raw[:100]}


def score_question(question: str, content: str, use_anthropic: bool = True) -> dict:
    """
    Full pipeline: get AI answer from content, then score it.
    Returns:
        {
            "question": str,
            "answer": str,
            "accuracy_score": int (0-10),
            "nando_score": int (0-10),
            "combined_score": float (0-10),
            "reason": str
        }
    """
    answer = _get_ai_answer(question, content, use_anthropic)
    scores = _judge_answer(question, content, answer, use_anthropic)

    accuracy = scores.get("accuracy_score", 0)
    nando = scores.get("nando_score", 0)
    combined = round((accuracy + nando) / 2, 1)

    return {
        "question": question,
        "answer": answer,
        "accuracy_score": accuracy,
        "nando_score": nando,
        "combined_score": combined,
        "reason": scores.get("reason", "")
    }
