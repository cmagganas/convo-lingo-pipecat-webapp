# Copyright (c) 2024, Daily
# SPDX-License-Identifier: BSD 2-Clause License

"""A 'Hello-World' introduction to Pipecat Flows.

Requirements:
- CARTESIA_API_KEY
- GOOGLE_API_KEY (can reuse GEMINI_API_KEY)
"""

import argparse
import os

from loguru import logger
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.cartesia.stt import CartesiaSTTService
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.google.llm import GoogleLLMService
from pipecat.transports.base_transport import BaseTransport
from pipecat.utils.text.markdown_text_filter import MarkdownTextFilter

from pipecat_flows import FlowArgs, FlowManager, FlowsFunctionSchema, NodeConfig
from functions.favorite_color import get_record_favorite_color_func

from config.settings import load_config

from config.transport import transport_params


def create_initial_node() -> NodeConfig:
    """Initial node: greet and ask favorite color (per README)."""
    record_favorite_color_func = get_record_favorite_color_func()

    # Load task messages from prompts/en/v1/initial.json
    import json
    from pathlib import Path

    prompts_path = Path(__file__).parent / "prompts" / "en" / "v1" / "initial.json"
    with prompts_path.open("r", encoding="utf-8") as fp:
        initial_task_messages = json.load(fp)

    # Load role and task messages via PromptLoader
    from pathlib import Path
    from utils.prompt_loader import PromptLoader

    language = os.getenv("TARGET_LANGUAGE") or os.getenv("LANGUAGE") or "en"
    if language not in ("en", "es"):
        language = "en"
    loader = PromptLoader(Path(__file__).parent / "prompts")
    role_messages = loader.load(language, "v1", "role")
    initial_task_messages = loader.load(language, "v1", "initial")

    return {
        "name": "initial",
        "role_messages": role_messages,
        "task_messages": initial_task_messages,
        "functions": [record_favorite_color_func],
    }


# Handler and end-node are moved to functions/favorite_color.py


async def run_example(transport: BaseTransport, _: argparse.Namespace, handle_sigint: bool):
    # Allow GOOGLE_API_KEY to come from GEMINI_API_KEY for convenience
    cfg = load_config()
    stt = CartesiaSTTService(api_key=cfg.cartesia_api_key)
    tts = CartesiaTTSService(
        api_key=cfg.cartesia_api_key,
        voice_id=cfg.voice_id,
        text_filters=cfg.text_filters,
    )
    llm = GoogleLLMService(api_key=cfg.google_api_key, model="gemini-2.0-flash")

    context = OpenAILLMContext()
    context_aggregator = llm.create_context_aggregator(context)

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            context_aggregator.user(),
            llm,
            tts,
            transport.output(),
            context_aggregator.assistant(),
        ]
    )

    task = PipelineTask(pipeline, params=PipelineParams(allow_interruptions=True))

    flow_manager = FlowManager(
        task=task,
        llm=llm,
        context_aggregator=context_aggregator,
        transport=transport,
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info(f"Client connected")
        await flow_manager.initialize(create_initial_node())

    runner = PipelineRunner(handle_sigint=handle_sigint)
    await runner.run(task)


if __name__ == "__main__":
    try:
        from pipecat.examples.run import main  # type: ignore

        main(run_example, transport_params=transport_params)
    except ModuleNotFoundError:
        # Fallback: minimal dry-run initializer without a live transport server
        import asyncio

        async def _dry_run() -> None:
            logger.warning("pipecat.examples.run not found; performing dry-run initialization")
            cfg = load_config()
            if not cfg.google_api_key:
                raise RuntimeError("Set GOOGLE_API_KEY or GEMINI_API_KEY in environment")

            llm = GoogleLLMService(api_key=cfg.google_api_key, model="gemini-2.0-flash")
            context = OpenAILLMContext()
            context_aggregator = llm.create_context_aggregator(context)

            # Minimal pipeline to back a PipelineTask for FlowManager
            pipeline = Pipeline([])
            task = PipelineTask(pipeline, params=PipelineParams(allow_interruptions=True))

            class _DummyTransport:
                def event_handler(self, _event_name: str):
                    def _decorator(func):
                        return func
                    return _decorator

            transport = _DummyTransport()

            flow_manager = FlowManager(
                task=task,
                llm=llm,
                context_aggregator=context_aggregator,
                transport=transport,  # type: ignore[arg-type]
            )
            await flow_manager.initialize(create_initial_node())
            logger.info("Dry-run: Flow initialized successfully")

        asyncio.run(_dry_run())


