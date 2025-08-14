# ConvoLingo Implementation Plan

## Project Overview

AI Language Learning WebApp using Pipecat Flows and Daily WebRTC

## Implementation Steps

- [x] Step 0: Repository setup and migration
- [x] Step 1: Minimal Pipecat Flows setup
- [ ] Step 2: Fix provider configuration
- [ ] Step 3: Add language selection to flow
- [ ] Step 4: Implement prompt versioning (en/es)
- [ ] Step 5: Add lesson nodes
- [ ] Step 6: Implement parallel pipeline for languages
- [ ] Step 7: Add progress tracking

## Current Status

✅ **Working Foundation Established** - Daily connection successful, ready for incremental improvements

## Completed Steps

### Step 0: Repository Setup (2024-08-14)

- Created new repo: `convo-lingo-pipecat-webapp`
- Migrated from `pipecat-flows-convolingo`
- Renamed old repo to `convo-lingo-pipecat-twilio`
- Set up Python 3.13.3 environment with uv

### Step 1: Minimal Pipecat Flows (Dynamic Flow)

**Status**: ✅ Complete with test issues identified

**What's Working**:

- Dynamic flow using Pipecat Flows pattern
- Function `collect_profile_func` for name and language collection
- Nodes: `initial`, `end`
- Daily WebRTC transport connects successfully
- Flow manager initializes properly in full pipeline mode

**Test Results**:

1. `app.py` - FakeTask error in test mode (expected, needs real pipeline)
2. `run_convolingo.py` - Successfully connects to Daily room
3. Cartesia STT/TTS - HTTP 402 (payment required)

**Files Created/Modified**:

- `app.py` - Main application with flow setup
- `run_convolingo.py` - Full pipeline with Daily transport
- `flows/convolingo_hello_world.json` - Flow definition
- `functions/favorite_color.py` - Example function
- `prompts/en/v1/` - English prompts
- `prompts/es/v1/` - Spanish prompts
- `utils/prompt_loader.py` - Prompt loading utility

## Next Steps

### Step 2: Fix Provider Configuration

- [ ] Switch to available STT provider (Deepgram or Google)
- [ ] Switch to available TTS provider (OpenAI or ElevenLabs)
- [ ] Test full audio loop with Daily

### Step 3: Add Language Selection

- [ ] Modify `collect_profile_func` to handle language selection
- [ ] Update flow state with selected language
- [ ] Test language persistence through conversation

### Step 4: Implement Prompt Versioning

- [ ] Load prompts based on selected language
- [ ] Add prompt manager to handle versions
- [ ] Test bilingual conversations

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
