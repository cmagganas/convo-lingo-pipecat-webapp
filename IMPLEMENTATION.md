# ConvoLingo Implementation Plan

## Project Overview

AI Language Learning WebApp using Pipecat Flows and Daily WebRTC

## Implementation Steps

- [ ] Step 1: Minimal Pipecat Flows setup
- [ ] Step 2: Add custom prompts directory
- [ ] Step 3: Add Spanish variant
- [ ] Step 4: Extract Prompt Manager
- [ ] Step 5: Add Daily Transport
- [ ] Step 6: Add second node
- [ ] Step 7: Add parallel pipeline structure

## Current Status

Project initialized - ready for Step 1

## Step 1: Minimal Pipecat Flows (Dynamic Flow) — adapted to collect name and target_language

Scope

- Minimal dynamic flow using the Pipecat Flows README pattern
- One function `collect_profile_func` and two nodes: `initial`, `end`
- No transport/providers yet; script logs initialization

Test Instructions

1) Ensure virtual env is active (uv created .venv already)
2) Install: `uv pip install -r requirements.txt`
3) Run: `python app.py`
4) Expect log output: initialization messages (no transport started)

References

- Pipecat Flows README (Dynamic Flow): <https://github.com/pipecat-ai/pipecat-flows/blob/main/README.md>
