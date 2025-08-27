# ConvoLingo (Pipecat Flows) – Quickstart with `uv`

Overview

This repo shows two ways to run a Pipecat Flows voice app for ConvoLingo:

- From a FlowConfig JSON exported by the Pipecat Flows Editor (static flow)
- From Python code (dynamic flow pattern is recommended for production)

You’ll set up a Python environment with uv, configure API keys, then either:

- Load a JSON flow with `run_convolingo.py` (Daily WebRTC transport)
- Or use your own Python entry (dynamic) following the same wiring

Prerequisites

- Python 3.11+ (3.12/3.13 fine)
- uv (<https://github.com/astral-sh/uv>)
- Daily room URL (for browser-based audio testing)
  - Example: <https://your-subdomain.daily.co/pipecat-flow-convolingo>
  - You can create rooms in your Daily dashboard

## Environment Setup (uv)

### 1. Create and activate virtual environment

```bash
cd /Users/christos/cmagganas/pipecat-ai/pipecat-flows-convolingo
uv venv
. .venv/bin/activate
```

### 2. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 3. Configure environment (.env or export)

Required for this quickstart:

- GOOGLE_API_KEY (or GEMINI_API_KEY): your Google AI Studio (Gemini) key
- CARTESIA_API_KEY: for STT and TTS
- YOUR_DAILY_ROOM_URL: full Daily room URL (not just a name)

Optional (for other transports/providers later):

- DAILY_API_KEY, DEEPGRAM_API_KEY, etc.

Example .env

```bash
GOOGLE_API_KEY=your_google_ai_studio_key

# or GEMINI_API_KEY=

CARTESIA_API_KEY=your_cartesia_key
YOUR_DAILY_ROOM_URL=<https://your-subdomain.daily.co/pipecat-flow-convolingo>

```

Verify in shell

```bash
echo ${#GOOGLE_API_KEY}  # should be > 0 (or GEMINI_API_KEY)
echo ${#CARTESIA_API_KEY}
echo $YOUR_DAILY_ROOM_URL
```

## Usage

Run Option A: Load JSON (static flow)

Use this path when you create or edit a flow in the Editor (local at <http://localhost:5173> or online):

### 1. Export your flow from the Editor to a JSON file

### 2. Copy it into this repo at `flows/convolingo_hello_world.json` to match the default path used by `run_convolingo.py`

```bash
mkdir -p editor/examples
cp /path/to/your/exported.json editor/examples/convolingo_hello_world.json
```

### 3. Run the app (Daily transport)

```bash
python run_convolingo.py
```

What it does

- Loads your JSON flow into FlowManager (static mode)
- Wires Daily → STT (Cartesia) → LLM (Gemini) → TTS (Cartesia) → Daily
- On first participant join, initializes the flow

Notes on handlers

If your JSON uses `"handler": "__function__:set_profile"`, you must define a Python function named `set_profile(args)` in `run_convolingo.py` (or an imported module). It must return `(result, "next_node_name")`. The FlowManager resolves these handler tokens automatically.

Run Option B: Dynamic flow (recommended pattern)

Dynamic flows let you control nodes/transitions in code while still loading prompts/content from files. The wiring to Daily/LLM/STT/TTS is identical; only how nodes are created differs.

Minimal outline (pseudo):

```python
from pipecat_flows import FlowManager

def create_initial_node():
    return {
        "name": "initial",
        "role_messages": [...],
        "task_messages": [...],
        "functions": [my_func_schema],
    }

flow_manager = FlowManager(task=task, llm=llm, context_aggregator=context_aggregator, transport=transport)

@transport.event_handler("on_client_connected")
async def on_client_connected(transport, client):
    await flow_manager.initialize(create_initial_node())
```

You can adapt the static JSON content into role/task messages per node while keeping the function handlers in Python code. See Pipecat Flows docs for node config fields and function schemas.

Troubleshooting

- Missing key error: ensure `GOOGLE_API_KEY` (or `GEMINI_API_KEY`) and `CARTESIA_API_KEY` are set in the current shell.
- No audio: verify your Daily room URL is correct and you join the same room from a browser tab.
- Handler not found: confirm your JSON references `"__function__:<name>"` and a Python function `<name>` exists and is importable.
- Version mismatches: re-run `uv pip install -r requirements.txt` after pulling updates.

References

- Pipecat Flows guide: <https://docs.pipecat.ai/guides/features/pipecat-flows>
- Pipecat Flows README: <https://github.com/pipecat-ai/pipecat-flows/blob/main/README.md>

Daily room access (dev vs prod)

- Public (dev):
  - Make the room public in Daily Dashboard (anyone with link)
  - Open the room URL directly: e.g. <https://your-subdomain.daily.co/pipecat-flow-convolingo>
- Private (prod):
  - Generate a meeting token via Daily API and append to the URL: `?t=TOKEN`
  - Or embed with daily-js and pass the token programmatically
  - Future enhancement: wire `DAILY_MEETING_TOKEN` in `run_convolingo.py` so the bot and browser both use tokens

## ✅ Working Deployment

**Agent**: `convo-lingo-webapp-v1`  
**Status**: ✅ Deployed and functional on Pipecat Cloud  
**Image**: `cmagganas/convo-lingo-webapp-v1:0.1`  

### Architecture

- **STT**: Cartesia Speech-to-Text  
- **TTS**: Cartesia Text-to-Speech
- **LLM**: Google Gemini 2.0 Flash
- **Framework**: Pipecat Flows + Daily WebRTC

### Deploy Commands

```bash
# Deploy webapp version
pcc deploy convo-lingo-webapp-v1 cmagganas/convo-lingo-webapp-v1:0.1 --secrets convo-lingo-webapp-v1-secrets --force

# Start session (will prompt for confirmation)
pcc agent start convo-lingo-webapp-v1 --use-daily

# Check status
pcc agent status convo-lingo-webapp-v1

# View logs
pcc agent logs convo-lingo-webapp-v1 | tail -20
```

### Working Bot Implementation
<!-- 
Working bot.py implementation (Cartesia STT+TTS + Google LLM + Pipecat Flows):

```python
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
```

Working Dockerfile:
```dockerfile
FROM dailyco/pipecat-base:latest
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY ./bot.py bot.py
COPY ./flows/ flows/
```

Working requirements.txt:
```
pipecatcloud
pipecat-ai[cartesia,daily,google,silero]
pipecat-ai-flows
python-dotenv~=1.0.1
```
-->

## ✅ Current Status: WORKING END-TO-END VOICE APPLICATION

### What's Working (August 21, 2025)

- ✅ **Complete Voice Pipeline**: Speech → AI → Speech working end-to-end
- ✅ **Agent Deployed**: `convo-lingo-webapp-v1:0.3` on Pipecat Cloud
- ✅ **Frontend Running**: React app with Voice UI Kit at <http://localhost:5173>
- ✅ **Real-time Conversation**: User can speak to ConvoLingo and get responses
- ✅ **Audio Quality**: Clear speech recognition and synthesis
- ✅ **Infrastructure**: Docker deployment, secrets management, monitoring

### What's NOT Working

- ❌ **Frontend Metrics**: Token usage/processing metrics not displayed in UI
- ❌ **Frontend Logs**: Agent conversation logs not visible in frontend
- ❌ **Language Selection**: Simplified flow without language choice menu
- ❌ **Structured Lessons**: Basic greeting only, no lesson progression

### Quick Start (Current Working Version)

```bash
# 1. Start the frontend
cd frontend && npm run dev

# 2. Start an agent session (in another terminal)
cd .. && pcc agent start convo-lingo-webapp-v1 --use-daily

# 3. Update frontend with new room URL/token (from pcc output)
# Edit frontend/src/index.tsx with new room details

# 4. Open http://localhost:5173 and click "Connect"
# 5. Start talking to ConvoLingo!
```

### Architecture

**Frontend** (React + Voice UI Kit) → **Daily WebRTC** → **Pipecat Cloud Agent** → **Cartesia STT** → **Google LLM** → **Cartesia TTS** → **Daily WebRTC** → **Frontend**

## Troubleshooting Frontend Metrics & Logs

### Issue: Metrics Not Displayed

**Symptoms**:

- Frontend shows "Prompt Tokens: 0, Completion Tokens: 0"
- Agent logs show actual token usage and metrics
- Conversation works but UI doesn't update metrics

**Investigation Steps**:

1. **Check Voice UI Kit Configuration**:

   ```typescript
   // Current config in frontend/src/index.tsx
   <ConsoleTemplate
     transportType="daily"
     connectParams={{
       url: 'https://cloud-...daily.co/...',
       token: '...'
     }}
   />
   ```

2. **Verify Agent Metrics Broadcasting**:

   ```bash
   # Check if agent is sending metrics to frontend
   pcc agent logs convo-lingo-webapp-v1 | grep -E "(metric|usage|token)"
   ```

3. **Test Direct Connection**:

   ```bash
   # Test direct Daily room (bypasses Voice UI Kit)
   # Open: https://cloud-...daily.co/ROOM_ID?t=TOKEN
   ```

### Recommendations for Metrics Fix

**Option 1: Voice UI Kit Configuration Research**

- Research `@pipecat-ai/voice-ui-kit` documentation for metrics enablement
- Check if `connectParams` needs additional configuration
- Look for `enableMetrics` or similar flags

**Option 2: Custom Metrics Implementation**

- Implement custom metrics display using RTVI client directly
- Subscribe to agent events for token usage updates
- Create custom UI components for metrics display

**Option 3: Agent Metrics Broadcasting**

- Verify agent sends metrics via RTVI protocol
- Check if metrics are enabled in `PipelineParams`
- Ensure metrics frames are transmitted to frontend

### Issue: Logs Not Displayed

**Symptoms**:

- Frontend console shows browser logs only
- Agent conversation logs not visible in frontend
- No real-time conversation transcript in UI

**Investigation Steps**:

1. **Check RTVI Event Subscription**:

   ```javascript
   // Add to frontend for debugging
   rtviClient.on('message', (message) => {
     console.log('Agent message:', message);
   });
   ```

2. **Verify Agent Log Broadcasting**:

   ```bash
   # Check if agent logs are configured for frontend
   pcc agent logs convo-lingo-webapp-v1 | grep -E "(transcript|message|user)"
   ```

### Next Development Priorities

1. **Short-term**: Debug and fix frontend metrics display
2. **Medium-term**: Restore language selection flow with proper UI
3. **Long-term**: Implement structured language lessons and progress tracking

### Development Commands

```bash
# Frontend development
cd frontend && npm run dev

# Agent management  
pcc agent status convo-lingo-webapp-v1
pcc agent start convo-lingo-webapp-v1 --use-daily
pcc agent logs convo-lingo-webapp-v1 | tail -20

# Testing
curl -s http://localhost:5173  # Test frontend
curl -s "https://cloud-...daily.co/ROOM" # Test Daily room
```

Last Updated: August 21, 2025
