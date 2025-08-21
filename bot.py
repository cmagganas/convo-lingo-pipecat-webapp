import os
import json
from loguru import logger
from dotenv import load_dotenv

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMMessagesFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.cartesia.stt import CartesiaSTTService
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.google.llm import GoogleLLMService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecatcloud.agent import DailySessionArguments
from pipecat_flows import FlowManager

load_dotenv(override=True)

async def set_profile(args):
    """Handle user profile collection (name and target language)."""
    logger.info(f"Setting profile: {args}")
    name = args.get("name", "Friend").strip()
    target_language = args.get("target_language", "en").strip()
    logger.info(f"Profile set - Name: {name}, Language: {target_language}")
    return {"name": name, "target_language": target_language}, "end"

async def main(transport: DailyTransport):
    # Load ConvoLingo Flow Configuration
    try:
        flow_config_path = os.path.join(os.path.dirname(__file__), "flows", "convolingo_hello_world.json")
        with open(flow_config_path, "r") as f:
            flow_config = json.load(f)
        logger.info("Loaded ConvoLingo flow configuration")
    except Exception as e:
        logger.error(f"Failed to load flow config: {e}")
        flow_config = None

    # Initialize AI Services
    stt = CartesiaSTTService(api_key=os.getenv("CARTESIA_API_KEY"))
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id=os.getenv("CARTESIA_VOICE_ID", "32b3f3c5-7171-46aa-abe7-b598964aa793")
    )
    llm = GoogleLLMService(
        api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
        model="gemini-2.0-flash"
    )

    # Context Management
    messages = [{
        "role": "system",
        "content": "You are ConvoLingo, a patient language teacher. Use simple language, speak clearly, and avoid special characters."
    }]
    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)

    # Pipeline: STT → LLM → TTS
    pipeline = Pipeline([
        transport.input(),
        stt,
        context_aggregator.user(),
        llm,
        tts,
        transport.output(),
        context_aggregator.assistant(),
    ])

    task = PipelineTask(pipeline, params=PipelineParams(
        allow_interruptions=True,
        enable_metrics=True,
        enable_usage_metrics=True,
        report_only_initial_ttfb=True,
    ))

    # Optional: Pipecat Flows Integration
    flow_manager = None
    if flow_config:
        try:
            flow_manager = FlowManager(
                task=task,
                llm=llm,
                context_aggregator=context_aggregator,
                flow_config=flow_config,
            )
            logger.info("ConvoLingo FlowManager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize FlowManager: {e}")

    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant):
        logger.info("First participant joined: {}", participant["id"])
        await transport.capture_participant_transcription(participant["id"])
        
        if flow_manager:
            logger.info("Starting ConvoLingo flow...")
            await flow_manager.initialize()
        else:
            logger.info("Starting simple ConvoLingo greeting...")
            messages.append({
                "role": "system",
                "content": "Greet the user as ConvoLingo and ask for their name and which language they want to practice."
            })
            await task.queue_frames([LLMMessagesFrame(messages)])

    @transport.event_handler("on_participant_left")
    async def on_participant_left(transport, participant, reason):
        logger.info("Participant left: {}", participant)
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False, force_gc=True)
    await runner.run(task)

async def bot(args: DailySessionArguments):
    """Main bot entry point compatible with Pipecat Cloud."""
    logger.info(f"ConvoLingo bot process initialized {args.room_url} {args.token is not None}")

    transport = DailyTransport(
        args.room_url,
        args.token,
        "ConvoLingo WebApp",
        DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            transcription_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )

    try:
        await main(transport)
        logger.info("ConvoLingo bot process completed")
    except Exception as e:
        logger.exception(f"Error in ConvoLingo bot process: {str(e)}")
        raise