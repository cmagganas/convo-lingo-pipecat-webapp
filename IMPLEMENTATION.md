# ConvoLingo Implementation Plan

## Project Overview

AI Language Learning WebApp using Pipecat Flows and Daily WebRTC

## Implementation Steps

- [x] Step 0: Repository setup and migration
- [x] Step 1: Minimal Pipecat Flows setup
- [x] Step 2: Fix provider configuration and deploy to Pipecat Cloud
- [x] Step 3: Build React frontend with Voice UI Kit
- [x] Step 4: Establish end-to-end voice conversation
- [ ] Step 5: Add language selection to flow
- [ ] Step 6: Implement prompt versioning (en/es)
- [ ] Step 7: Add lesson nodes
- [ ] Step 8: Implement parallel pipeline for languages
- [ ] Step 9: Add progress tracking
- [ ] Step 10: Fix frontend metrics and logging display

## Current Status

✅ **WORKING END-TO-END VOICE APPLICATION** - Frontend connects to deployed agent, voice conversation functional

### What's Working Right Now:
- ✅ **Agent Deployment**: `convo-lingo-webapp-v1` on Pipecat Cloud
- ✅ **Voice Pipeline**: Cartesia STT/TTS + Google Gemini LLM
- ✅ **Frontend**: React app with Pipecat Voice UI Kit
- ✅ **Connection**: Frontend → Agent via Daily WebRTC
- ✅ **Conversation**: ConvoLingo greets and responds to user
- ✅ **Audio Processing**: Real-time speech recognition and synthesis

### What's NOT Working:
- ❌ **Frontend Metrics**: Token usage/metrics not displayed in UI
- ❌ **Frontend Logs**: Agent logs not visible in frontend console
- ❌ **Language Selection**: Currently uses simplified flow without language choice
- ❌ **Lesson Structure**: Basic greeting only, no structured lessons

## Completed Steps

### Step 0: Repository Setup (2024-08-14)

- Created new repo: `convo-lingo-pipecat-webapp`
- Migrated from `pipecat-flows-convolingo`
- Renamed old repo to `convo-lingo-pipecat-twilio`
- Set up Python 3.13.3 environment with uv

### Step 1: Minimal Pipecat Flows Setup ✅ COMPLETE
### Step 2: Provider Configuration & Deployment ✅ COMPLETE 
### Step 3: React Frontend Development ✅ COMPLETE
### Step 4: End-to-End Connection ✅ COMPLETE

**Current Working Configuration**:

**Agent Side** (`convo-lingo-webapp-v1:0.3`):
- **Docker Image**: `cmagganas/convo-lingo-webapp-v1:0.3`
- **STT**: Cartesia Speech-to-Text (working)
- **LLM**: Google Gemini 2.0 Flash (working)
- **TTS**: Cartesia Text-to-Speech (working)
- **Flow**: Simplified greeting flow (no complex functions)
- **Transport**: Daily WebRTC transport

**Frontend Side** (`frontend/`):
- **Framework**: React + TypeScript + Vite
- **UI Kit**: `@pipecat-ai/voice-ui-kit`
- **Transport**: Daily WebRTC via Voice UI Kit
- **Connection**: Direct room URL + token authentication

**Working Pipeline**: User Speech → Cartesia STT → Google LLM → Cartesia TTS → User Audio

**Deployment**:
- **Agent**: Deployed on Pipecat Cloud
- **Frontend**: Running locally (`npm run dev`)
- **Connection**: Via Daily WebRTC rooms

**Files Structure**:
```
convo-lingo-pipecat-webapp/
├── bot.py                    # Working agent code
├── requirements.txt          # Python dependencies
├── flows/
│   └── convolingo_hello_world.json  # Simplified flow
├── frontend/                 # React frontend
│   ├── src/index.tsx        # Main app with Voice UI Kit
│   ├── package.json         # Frontend dependencies
│   └── ...
└── .env                     # API keys and config
```

## Next Priority Steps

### Step 5: Debug Frontend Metrics Display

**Problem**: Agent tracks metrics (token usage, processing time) but frontend doesn't display them

**Investigation Needed**:
1. Check Voice UI Kit documentation for metrics configuration
2. Verify if metrics need to be explicitly enabled in `connectParams`
3. Investigate if custom metrics implementation is required

### Step 6: Add Language Selection Flow

**Goal**: Restore language selection functionality
- Modify flow to include language choice
- Update prompt system for multi-language support
- Test language switching during conversation

### Step 7: Structured Learning Content

**Goal**: Replace simple greeting with actual language lessons
- Implement lesson progression
- Add vocabulary and grammar content
- Create assessment and feedback system

## Environment Setup

### Prerequisites

- Python 3.13.3
- uv package manager
- Daily account with room created

### Installation

```bash
# Clone repository
git clone https://github.com/cmagganas/convo-lingo-pipecat-webapp.git
cd convo-lingo-pipecat-webapp

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
uv pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Running the Application

```bash
# Test mode (no transport)
python app.py

# Full mode with Daily WebRTC
python run_convolingo.py

# Access Daily room at:
# https://cmagganas.daily.co/pipecat-flow-convolingo
```

## Known Issues

1. Cartesia Payment Required: Need to add credits or switch providers
2. FakeTask in Test Mode: Expected behavior, use run_convolingo.py for full pipeline
3. Provider Selection: Need to configure available providers in .env

## Architecture Notes

Current Structure

```bash
convo-lingo-pipecat-webapp/
├── app.py                    # Main application entry
├── run_convolingo.py         # Full pipeline with Daily
├── config/
│   ├── settings.py          # Configuration management
│   └── transport.py         # Transport setup
├── flows/
│   └── convolingo_hello_world.json
├── functions/
│   └── favorite_color.py
├── prompts/
│   ├── en/v1/              # English prompts
│   └── es/v1/              # Spanish prompts
└── utils/
    └── prompt_loader.py     # Prompt loading utility
```

## Design Decisions

Using Dynamic Flows for flexibility
Daily WebRTC for browser-based voice
Modular prompt system for multi-language support
Provider-agnostic design for STT/LLM/TTS

## References

[Pipecat Flows Documentation](https://docs.pipecat.ai/guides/features/pipecat-flows)
[Pipecat Flows GitHub](https://github.com/pipecat-ai/pipecat-flows)
[Daily WebRTC](https://daily.co)
[Project Repository](https://github.com/cmagganas/convo-lingo-pipecat-webapp)

Last Updated: 2024-08-14
