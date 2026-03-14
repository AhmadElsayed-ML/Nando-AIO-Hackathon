from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv


# Load environment variables from a .env file if present
load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    title: str = "Brand AI-Readiness Optimizer"
    subtitle: str = (
        "Paste website or social content → get a clearer, AI-ready version with proof "
        "that understanding improved."
    )
    max_input_chars: int = 6000
    default_provider: Literal["rule_based", "openai", "anthropic"] = "rule_based"


# Toggle between mocks and real modules.
# During the hackathon MVP, keep this True.
USE_MOCKS: bool = os.getenv("USE_MOCKS", "true").lower() == "true"


def get_openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY")


def get_anthropic_api_key() -> str | None:
    return os.getenv("ANTHROPIC_API_KEY")


APP_CONFIG = AppConfig()
