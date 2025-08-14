# run_convolingo.py
import os, json, asyncio
from loguru import logger
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.google.llm import GoogleLLMService
from pipecat.services.cartesia.stt import CartesiaSTTService
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat_flows import FlowManager

# Example handler referenced in JSON as "__function__:set_profile"
async def set_profile(args):
    # e.g. args = {"name": "...", "target_language": "en"|"es"}
    return args, "end"

async def main():
    # 1) Load FlowConfig JSON (exported from the editor)
    with open("flows/convolingo_hello_world.json", "r") as f:
        flow_config = json.load(f)

    # 2) Services (use your keys)
    llm = GoogleLLMService(api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
                           model="gemini-2.0-flash")
    stt = CartesiaSTTService(api_key=os.getenv("CARTESIA_API_KEY"))
    tts = CartesiaTTSService(api_key=os.getenv("CARTESIA_API_KEY"),
                             voice_id=os.getenv("CARTESIA_VOICE_ID","32b3f3c5-7171-46aa-abe7-b598964aa793"))

    context = OpenAILLMContext()
    context_aggregator = llm.create_context_aggregator(context)

    # 3) Daily transport (easiest for browser testing)
    transport = DailyTransport(
        os.getenv("YOUR_DAILY_ROOM_URL"),
        os.getenv("DAILY_MEETING_TOKEN"), # TODO: figure out a better way to get the meeting token than adding it to the .env file
        "ConvoLingo",
        DailyParams(audio_in_enabled=True, audio_out_enabled=True, vad_analyzer=SileroVADAnalyzer()),
    )

    # 4) Pipeline
    pipeline = Pipeline([
        transport.input(),
        stt,
        context_aggregator.user(),
        llm,
        tts,
        transport.output(),
        context_aggregator.assistant(),
    ])
    task = PipelineTask(pipeline, params=PipelineParams(allow_interruptions=True))

    # 5) FlowManager with static flow_config
    flow_manager = FlowManager(
        task=task,
        llm=llm,
        context_aggregator=context_aggregator,
        flow_config=flow_config,
    )

    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant):
        await transport.capture_participant_transcription(participant["id"])
        logger.debug("Initializing flow")
        await flow_manager.initialize()

    # 6) Run
    await PipelineRunner().run(task)

if __name__ == "__main__":
    asyncio.run(main())