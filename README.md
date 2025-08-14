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

Environment Setup (uv)

1) Create and activate virtual environment

    ```cd /Users/christos/cmagganas/pipecat-ai/pipecat-flows-convolingo
    uv venv
    . .venv/bin/activate
    ```

2) Install dependencies

    ```uv pip install -r requirements.txt
    ```

3) Configure environment (.env or export)

Required for this quickstart:

- GOOGLE_API_KEY (or GEMINI_API_KEY): your Google AI Studio (Gemini) key
- CARTESIA_API_KEY: for STT and TTS
- YOUR_DAILY_ROOM_URL: full Daily room URL (not just a name)

Optional (for other transports/providers later):

- DAILY_API_KEY, DEEPGRAM_API_KEY, etc.

Example .env

```GOOGLE_API_KEY=your_google_ai_studio_key
# or GEMINI_API_KEY=...
CARTESIA_API_KEY=your_cartesia_key
YOUR_DAILY_ROOM_URL=https://your-subdomain.daily.co/pipecat-flow-convolingo
```

Verify in shell

```echo ${#GOOGLE_API_KEY}  # should be > 0 (or GEMINI_API_KEY)
echo ${#CARTESIA_API_KEY}
echo $YOUR_DAILY_ROOM_URL
```

Run Option A: Load JSON (static flow)

Use this path when you create or edit a flow in the Editor (local at <http://localhost:5173> or online):

1) Export your flow from the Editor to a JSON file
2) Copy it into this repo at `flows/convolingo_hello_world.json` to match the default path used by `run_convolingo.py`:

    ```mkdir -p editor/examples
    cp /path/to/your/exported.json editor/examples/convolingo_hello_world.json
    ```

3) Run the app (Daily transport)

```python run_convolingo.py
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
    ```
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

Progress so far

- uv environment and dependencies installed
- Editor-driven FlowConfig supported: `flows/convolingo_hello_world.json`
- Static flow runner: `python run_convolingo.py` (Daily + Cartesia STT/TTS + Gemini LLM)
- Function handler resolution via `__function__:` supported (see `set_profile` in `run_convolingo.py`)
- Editor usage validated (import/export JSON), local dev server available at <http://localhost:5173>

Next steps

- Convert to dynamic flow (recommended pattern) and expand nodes (e.g., placement)
- Replace deprecated `transition_to` usage in JSON with consolidated Python handlers returning `(result, next_node)`
- Add language state and prompt selection; introduce prompt versioning helper
- Add optional `DAILY_MEETING_TOKEN` support in `run_convolingo.py` for private rooms
- Add basic tests and a minimal FastAPI runner if needed for local signaling flows
