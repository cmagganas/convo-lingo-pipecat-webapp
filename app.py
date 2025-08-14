from __future__ import annotations

"""
Step 1: Minimal Dynamic Flow adapted from Pipecat Flows README
Collects `name` and `target_language` via a single function call.

No real providers or transports are wired yet. This script should run and log
initialization without starting any audio transport.

Reference: https://github.com/pipecat-ai/pipecat-flows/blob/main/README.md
"""

from typing import Any, Tuple
import os
from loguru import logger

try:
    # Real classes if installed and available.
    from pipecat_flows import FlowManager, FlowsFunctionSchema
except Exception:  # pragma: no cover - allow running without installed deps
    class FlowManager:  # type: ignore
        def __init__(self, **_: Any) -> None:
            self.state: dict[str, Any] = {}

        async def initialize(self, *_: Any, **__: Any) -> None:
            logger.info("FlowManager.initialize called (placeholder)")

    class FlowsFunctionSchema:  # type: ignore
        def __init__(self, **_: Any) -> None:
            ...


class FakeTask:
    """Minimal stub to satisfy FlowManager/ActionManager expectations at init time."""

    def set_reached_downstream_filter(self, *_: Any, **__: Any) -> None:  # noqa: D401
        return None

    def event_handler(self, _event_name: str):
        """Return a no-op decorator to register event handlers."""
        def decorator(func):
            return func
        return decorator

async def record_profile_and_set_next_node(
    args: Any, flow_manager: FlowManager
) -> Tuple[str, dict]:
    """Capture user's name and target language, then transition to end.

    Returns (result_str, next_node_config) per Flows pattern.
    """
    name = (args.get("name") or "Friend").strip()
    language = (args.get("target_language") or "English").strip()
    flow_manager.state["name"] = name
    flow_manager.state["target_language"] = language
    logger.info("Captured profile: name='{}', target_language='{}'", name, language)

    return f"{name}:{language}", create_end_node()


collect_profile_func = FlowsFunctionSchema(
    name="collect_profile_func",
    description="Record user's name and target language.",
    required=["name", "target_language"],
    handler=record_profile_and_set_next_node,
    properties={
        "name": {"type": "string"},
        "target_language": {"type": "string"},
    },
)


def create_initial_node() -> dict:
    return {
        "name": "initial",
        "role_messages": [
            {
                "role": "system",
                "content": (
                    "You are ConvoLingo, a patient language teacher. Speak clearly, "
                    "use simple language, and avoid special characters."
                ),
            }
        ],
        "task_messages": [
            {
                "role": "system",
                "content": (
                    "Greet the user. Ask their name and which language they want to practice. "
                    "You must call the function 'collect_profile_func' with both values."
                ),
            }
        ],
        "functions": [collect_profile_func],
        "respond_immediately": False,
    }


def create_end_node() -> dict:
    return {
        "name": "end",
        "task_messages": [
            {
                "role": "system",
                "content": (
                    "Thank the user for the info. Confirm their name and target language, then end."
                ),
            }
        ],
        "respond_immediately": True,
    }


async def main() -> None:
    logger.info("Setting up minimal flow (Step 1)")
    # Placeholders for FlowManager deps; replaced in later steps
    task = FakeTask()
    # Configure Google Gemini LLM; accept common env var names
    gemini_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("GOOGLE_GENAI_API_KEY")
    )
    if not gemini_key:
        raise RuntimeError(
            "GEMINI_API_KEY (or GOOGLE_API_KEY/GOOGLE_GENAI_API_KEY) is required for Step 1"
        )

    # Use the GoogleLLMService which Flows adapter supports
    from pipecat.services.google.llm import GoogleLLMService

    llm = GoogleLLMService(
        api_key=gemini_key,
        model="gemini-2.0-flash",
        system_instruction=None,
    )
    context_aggregator = object()
    transport = object()

    flow_manager = FlowManager(
        task=task,
        llm=llm,
        context_aggregator=context_aggregator,
        transport=transport,
    )
    await flow_manager.initialize(create_initial_node())
    logger.info("Initialized flow with initial node")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())


