from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from pipecat.utils.text.markdown_text_filter import MarkdownTextFilter


@dataclass
class AppConfig:
    google_api_key: str | None
    cartesia_api_key: str | None
    voice_id: str
    text_filters: List[object]


def load_config() -> AppConfig:
    """Load app configuration from environment variables.

    - GOOGLE_API_KEY or GEMINI_API_KEY for Google LLM
    - CARTESIA_API_KEY for STT/TTS
    - CARTESIA_VOICE_ID optional; defaults to a known voice
    - text_filters preconfigured with MarkdownTextFilter
    """
    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    cartesia_key = os.getenv("CARTESIA_API_KEY")
    voice_id = os.getenv("CARTESIA_VOICE_ID") or "32b3f3c5-7171-46aa-abe7-b598964aa793"
    text_filters = [MarkdownTextFilter()]
    return AppConfig(
        google_api_key=google_key,
        cartesia_api_key=cartesia_key,
        voice_id=voice_id,
        text_filters=text_filters,
    )


