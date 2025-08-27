# ConvoLingo Frontend Troubleshooting Guide

## Overview

This guide addresses specific issues with the ConvoLingo React frontend integration with Pipecat Voice UI Kit.

## Current Working State (August 27, 2025)

### ✅ What's Working

- **End-to-end voice conversation**: User speech → Agent response
- **Agent deployment**: `convo-lingo-webapp-v1` on Pipecat Cloud
- **Frontend connection**: React app connects to agent via Daily WebRTC
- **Audio pipeline**: Cartesia STT/TTS + Google Gemini LLM
- **Real-time conversation**: ConvoLingo greets and responds appropriately
- **Voice UI Kit Integration**: ConsoleTemplate successfully connects using daily transport
- **Environment variable management**: Vite properly reads VITE_ prefixed variables
- **Agent session management**: Fresh agent sessions create working Daily rooms

### ❌ What's NOT Working

- **Frontend metrics display**: Token usage shows 0 despite agent tracking usage
- **Frontend conversation logs**: Agent logs not visible in frontend UI
- **Language selection flow**: Simplified greeting only, no language choice
- **Lesson progression**: Basic conversation, no structured learning content

## Issue 1: Frontend Metrics Not Displaying

### Symptoms

```
Frontend UI shows:
- Prompt Tokens: 0
- Completion Tokens: 0
- Total Tokens: 0

But agent logs show:
- CartesiaTTSService usage characters: 18
- GoogleLLMService TTFB: 0.4949214458465576
- Token usage being tracked
```

### Root Cause Analysis

**Possible Causes:**

1. **Voice UI Kit Configuration**: Missing metrics enablement in `connectParams`
2. **RTVI Protocol**: Metrics not transmitted from agent to frontend
3. **Agent Configuration**: Metrics enabled but not broadcasted
4. **Frontend Subscription**: Not listening to metrics events

### Investigation Steps

#### Step 1: Check Current Frontend Configuration

```typescript
// Current: frontend/src/index.tsx
<ConsoleTemplate
  transportType="daily"
  connectParams={{
    url: 'https://cloud-f62295e899ac41849a4c95b5fb6df25a.daily.co/ROOM',
    token: 'JWT_TOKEN'
  }}
/>
```

#### Step 2: Research Voice UI Kit Metrics

```bash
# Check Voice UI Kit documentation
npm list @pipecat-ai/voice-ui-kit
# Version: 0.1.0

# Look for metrics configuration options
grep -r "metrics\|usage\|tokens" frontend/node_modules/@pipecat-ai/
```

#### Step 3: Monitor RTVI Events

```javascript
// Add debug logging to frontend
import { RTVIEvent } from '@pipecat-ai/client-react';

// In component:
const rtviClient = useRTVIClient();

useEffect(() => {
  const handleMessage = (message) => {
    console.log('RTVI Message:', message);
  };
  
  const handleMetrics = (metrics) => {
    console.log('Metrics received:', metrics);
  };
  
  rtviClient.on(RTVIEvent.MessageReceived, handleMessage);
  rtviClient.on('metrics', handleMetrics);
  
  return () => {
    rtviClient.off(RTVIEvent.MessageReceived, handleMessage);
    rtviClient.off('metrics', handleMetrics);
  };
}, [rtviClient]);
```

#### Step 4: Verify Agent Metrics Broadcasting

```bash
# Check agent metrics configuration
pcc agent logs convo-lingo-webapp-v1 | grep -E "(metric|usage|token|RTVI)"

# Look for metrics transmission
pcc agent logs convo-lingo-webapp-v1 | grep -E "(broadcast|send|frame)"
```

### Potential Solutions

#### Solution 1: Enable Metrics in Voice UI Kit

```typescript
// Try adding metrics configuration
<ConsoleTemplate
  transportType="daily"
  connectParams={{
    url: 'https://cloud-f62295e899ac41849a4c95b5fb6df25a.daily.co/ROOM',
    token: 'JWT_TOKEN',
    enableMetrics: true,  // Try this
    metrics: true,        // Or this
  }}
  config={{
    enableMetrics: true   // Or this
  }}
/>
```

#### Solution 2: Use RTVI Client Directly

```typescript
import { RTVIClient } from '@pipecat-ai/client-js';
import { DailyTransport } from '@pipecat-ai/daily-transport';

const transport = new DailyTransport();
const rtviClient = new RTVIClient({
  transport,
  params: {
    url: 'https://cloud-f62295e899ac41849a4c95b5fb6df25a.daily.co/ROOM',
    token: 'JWT_TOKEN'
  },
  enableMic: true,
  enableCam: false,
  callbacks: {
    onMetrics: (metrics) => {
      console.log('Metrics:', metrics);
      // Update UI state
    }
  }
});
```

#### Solution 3: Custom Metrics Implementation

```typescript
// Create custom metrics hook
const useAgentMetrics = () => {
  const [metrics, setMetrics] = useState({ prompt: 0, completion: 0, total: 0 });
  const rtviClient = useRTVIClient();
  
  useEffect(() => {
    const handleCustomMetrics = (data) => {
      if (data.type === 'metrics') {
        setMetrics(data.metrics);
      }
    };
    
    rtviClient.on('message', handleCustomMetrics);
    return () => rtviClient.off('message', handleCustomMetrics);
  }, [rtviClient]);
  
  return metrics;
};
```

## Issue 2: Frontend Logs Not Displaying

### Symptoms

```
Frontend shows:
- No conversation transcript
- No real-time agent responses visible
- Browser console shows only client-side logs

Agent logs show:
- LLM generation activity
- TTS conversion activity  
- User transcription activity
```

### Root Cause Analysis

**Possible Causes:**

1. **Event Subscription**: Frontend not subscribed to conversation events
2. **Agent Broadcasting**: Agent not sending conversation data to frontend
3. **Voice UI Kit**: ConsoleTemplate may not display conversation logs
4. **RTVI Protocol**: Conversation events not transmitted properly

### Investigation Steps

#### Step 1: Check for Conversation Events

```javascript
// Add to frontend for debugging
const rtviClient = useRTVIClient();

useEffect(() => {
  const events = [
    'messageReceived',
    'messageGenerated', 
    'transcriptionReceived',
    'ttsStarted',
    'ttsFinished'
  ];
  
  events.forEach(event => {
    rtviClient.on(event, (data) => {
      console.log(`Event ${event}:`, data);
    });
  });
}, [rtviClient]);
```

#### Step 2: Monitor Agent Conversation Events

```bash
# Check if agent sends conversation events
pcc agent logs convo-lingo-webapp-v1 | grep -E "(transcript|message|conversation|user|assistant)"

# Look for RTVI message frames
pcc agent logs convo-lingo-webapp-v1 | grep -E "(RTVIMessage|frame|broadcast)"
```

### Potential Solutions

#### Solution 1: Custom Conversation Display

```typescript
const useConversationHistory = () => {
  const [messages, setMessages] = useState([]);
  const rtviClient = useRTVIClient();
  
  useEffect(() => {
    const handleUserMessage = (message) => {
      setMessages(prev => [...prev, { type: 'user', content: message.text }]);
    };
    
    const handleBotMessage = (message) => {
      setMessages(prev => [...prev, { type: 'bot', content: message.text }]);
    };
    
    rtviClient.on('userTranscription', handleUserMessage);
    rtviClient.on('botResponse', handleBotMessage);
    
    return () => {
      rtviClient.off('userTranscription', handleUserMessage);
      rtviClient.off('botResponse', handleBotMessage);
    };
  }, [rtviClient]);
  
  return messages;
};
```

#### Solution 2: Agent Configuration for Conversation Broadcasting

```python
# In bot.py - ensure conversation events are sent
from pipecat.frames.frames import RTVIMessage

async def send_conversation_update(text, sender):
    message = RTVIMessage({
        "type": "conversation",
        "data": {
            "message": text,
            "sender": sender,
            "timestamp": time.time()
        }
    })
    await task.queue_frames([message])
```

## Issue 3: Language Selection Not Working

### Current State

- Simplified flow with basic greeting only
- No language selection menu
- No multi-language prompt system

### Required Changes

#### Step 1: Restore Language Selection Flow

```json
// flows/convolingo_hello_world.json
{
  "initial_node": "greeting",
  "nodes": {
    "greeting": {
      "role_messages": [...],
      "task_messages": [{
        "role": "system", 
        "content": "Greet user and ask for name and target language (English, Spanish, French, German)."
      }],
      "functions": [{
        "type": "function",
        "function": {
          "name": "set_profile",
          "description": "Record user's name and target language",
          "parameters": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "target_language": {"type": "string", "enum": ["en", "es", "fr", "de"]}
            },
            "required": ["name", "target_language"]
          },
          "handler": "__function__:set_profile"
        }
      }]
    }
  }
}
```

#### Step 2: Implement Language-Aware Frontend

```typescript
// Add language state to frontend
const [userLanguage, setUserLanguage] = useState('en');
const [learningLanguage, setLearningLanguage] = useState('');

const handleLanguageSelection = (language) => {
  setLearningLanguage(language);
  // Send to agent via RTVI
  rtviClient.sendMessage({
    type: 'language_selection',
    language: language
  });
};
```

## Debugging Commands

### Frontend Debugging

```bash
# Start frontend with verbose logging
cd frontend
DEBUG=* npm run dev

# Check frontend build
npm run build
npm run preview

# Inspect Voice UI Kit
npm list @pipecat-ai/voice-ui-kit
npm info @pipecat-ai/voice-ui-kit
```

### Agent Debugging  

```bash
# Monitor agent in real-time
pcc agent logs convo-lingo-webapp-v1 --follow

# Check specific components
pcc agent logs convo-lingo-webapp-v1 | grep Cartesia
pcc agent logs convo-lingo-webapp-v1 | grep Google
pcc agent logs convo-lingo-webapp-v1 | grep FlowManager

# Test agent health
pcc agent status convo-lingo-webapp-v1
curl -X POST "https://api.pipecat.daily.co/v1/public/convo-lingo-webapp-v1/start" \
  -H "Authorization: Bearer pk_960e6da9-9ff7-4d63-9f88-02556c5ceba9"
```

### Network Debugging

```bash
# Test Daily room connectivity
curl -s "https://cloud-f62295e899ac41849a4c95b5fb6df25a.daily.co/ROOM"

# Check WebRTC connectivity
# Open browser dev tools → Network tab → WebSocket frames

# Test Voice UI Kit connection
# Open browser dev tools → Console → Monitor RTVI events
```

## Next Steps Priority

1. **High Priority**: Fix frontend metrics display (investigate Voice UI Kit configuration)
2. **Medium Priority**: Implement conversation history display
3. **Medium Priority**: Restore language selection flow
4. **Low Priority**: Add structured lesson content

## Resources

- [Pipecat Voice UI Kit Docs](https://docs.pipecat.ai/client/js)
- [RTVI Protocol Specification](https://docs.pipecat.ai/client/js/api-reference)
- [Daily WebRTC Documentation](https://docs.daily.co)
- [Agent Logs Command Reference](README.md#development-commands)

## Issue 4: Assistant Development Anti-Patterns

### **Problem: Assistant Making Unauthorized File Changes**

**Symptoms:**

- Assistant modifies working code without explicit permission
- Working configurations get broken by unnecessary "improvements"
- Files get edited when only analysis was requested

**Root Cause:**

- Assistant assumes permission to modify files during troubleshooting
- Over-eager to "fix" things that aren't actually broken
- Lack of proper state assessment before making changes

**Prevention:**

1. **NEVER modify working files during troubleshooting analysis**
2. **Always read and assess current state before suggesting changes**
3. **Ask explicit permission before editing any files**
4. **Distinguish between analysis requests vs. implementation requests**

### **Problem: Ignoring "Working" Status in Documentation**

**Symptoms:**

- Assistant tries to fix components marked as "✅ WORKING" in documentation
- Changes made to stable, deployed systems
- Breaking working end-to-end functionality

**Root Cause:**

- Not reading project status documentation thoroughly
- Ignoring clear indicators of working state
- Assuming issues exist without proper investigation

**Prevention:**

1. **Read all documentation files before making changes**
2. **Respect "✅ WORKING" status markers**
3. **Focus only on "❌ NOT WORKING" issues**
4. **Verify current functionality before assuming problems**

### **Problem: Misunderstanding User Intent**

**Symptoms:**

- User asks for analysis, assistant implements changes
- User requests troubleshooting list, assistant modifies code
- Context confusion between investigation vs. implementation

**Root Cause:**

- Not carefully parsing user request intent
- Defaulting to implementation mode instead of analysis mode
- Misinterpreting "create a list" as "fix the problems"

**Prevention:**

1. **Read user requests multiple times before acting**
2. **Distinguish between "analyze and list" vs. "fix and implement"**
3. **When in doubt, ask for clarification before touching files**
4. **Default to read-only mode for troubleshooting requests**

### **Problem: Breaking Working Docker/Deployment Configuration**

**Symptoms:**

- Modifying Dockerfiles that are already deployed successfully
- Changing requirements.txt for working agents
- Breaking containerization that's functioning in production

**Root Cause:**

- Not checking deployment status before modifying container files
- Assuming local issues apply to deployed versions
- Changing stable infrastructure components

**Prevention:**

1. **Check agent deployment status before modifying container files**
2. **Verify if issues are local vs. deployed environment**
3. **NEVER modify Dockerfile/requirements.txt for deployed agents**
4. **Use version control strategy for infrastructure changes**

### **Problem: Frontend Configuration Chaos**

**Symptoms:**

- Modifying working frontend connections
- Breaking functional Voice UI Kit integration
- Changing stable room URL/token configurations

**Root Cause:**

- Not testing current frontend state before modifications
- Assuming frontend issues without proper investigation
- Breaking working WebRTC connections

**Prevention:**

1. **Test current frontend functionality before changes**
2. **Verify Voice UI Kit is actually broken before "fixing"**
3. **Don't modify working connection parameters**
4. **Focus on actual missing features, not working ones**

### **Problem: Scope Creep During Troubleshooting**

**Symptoms:**

- Trying to implement new features during bug investigation
- Adding complexity to simple troubleshooting tasks
- Mixing debugging with feature development

**Root Cause:**

- Not maintaining focus on specific troubleshooting scope
- Attempting to solve all problems at once
- Confusing bug fixes with feature additions

**Prevention:**

1. **Stick to the specific issue being investigated**
2. **Don't add new features during troubleshooting**
3. **One issue at a time approach**
4. **Document separate issues for future addressing**

### **Problem: Not Reading Project Documentation Thoroughly**

**Symptoms:**

- Missing critical status information in README.md
- Ignoring IMPLEMENTATION.md progress markers
- Not understanding current working state

**Root Cause:**

- Rushing to implementation without proper context
- Skipping documentation review
- Assuming problems exist without evidence

**Prevention:**

1. **Always read ALL documentation files first**
2. **Pay attention to status markers (✅/❌)**
3. **Understand current state before suggesting changes**
4. **Reference documentation when making decisions**

### **Problem: Tool Selection Errors**

**Symptoms:**

- Using write/edit tools when only read/analysis needed
- Modifying files when investigation was requested
- Wrong tool for the task type

**Root Cause:**

- Not matching tool usage to user intent
- Defaulting to modification tools for analysis tasks
- Misunderstanding tool purposes

**Prevention:**

1. **Use read-only tools for troubleshooting analysis**
2. **Only use write/edit tools when explicitly asked to implement**
3. **Match tool selection to user request type**
4. **When listing issues, don't fix them simultaneously**

### **Critical Development Rule**

**"When user says 'create a list of mistakes' - ONLY create the list. Don't fix anything. Don't modify anything. Just analyze and document."**

**Assistant Checklist for Every Request:**

1. ✅ Read user request carefully - what type of task is this?
2. ✅ Check all documentation files for current status
3. ✅ Identify what's WORKING vs. NOT WORKING
4. ✅ Match tool selection to task type (analysis vs. implementation)
5. ✅ When in doubt, ask before modifying anything

## Issue 5: Frontend Connection Troubleshooting (RESOLVED)

### **Problem: Frontend Not Connecting to Pipecat Cloud Agent**

**Symptoms Experienced:**

- `POST http://localhost:5173/undefined 404 (Not Found)`
- `Failed to join room Error: unrecognized property 'headers'`
- `Failed to join room Error: unrecognized property 'sessionId'`
- Frontend shows "Agent Connecting..." but never connects
- Client connects but agent doesn't join the room

**Root Causes Identified:**

#### 1. Environment Variable Format Issues

```bash
# WRONG: .env file had export prefixes
export VITE_PIPECAT_CONNECT_URL=https://api.pipecat.daily.co/v1/public/convo-lingo-webapp-v1/start

# CORRECT: Vite needs plain key=value format
VITE_PIPECAT_CONNECT_URL=https://api.pipecat.daily.co/v1/public/convo-lingo-webapp-v1/start
```

#### 2. Wrong Connection Pattern for Pipecat Cloud

```typescript
// WRONG: Trying to use Pipecat Cloud session API with Voice UI Kit
<ConsoleTemplate
  transportType="daily"
  connectParams={{
    endpoint: "https://api.pipecat.daily.co/v1/public/convo-lingo-webapp-v1/start",
    headers: { "Authorization": "Bearer api_key" }
  }}
/>
// This fails because Voice UI Kit daily transport expects Direct Daily room connection
```

#### 3. Stale Daily Room Sessions

- Old room URLs/tokens from previous sessions were no longer active
- Agent was not running in the specified Daily room
- Need fresh agent sessions to create active Daily rooms

**SOLUTION THAT WORKED:**

#### Step 1: Fix Environment Variables

```bash
# Create frontend/.env with proper Vite format (no export prefixes)
cat > frontend/.env << 'EOF'
VITE_DAILY_ROOM_URL=https://cloud-f62295e899ac41849a4c95b5fb6df25a.daily.co/NEW_ROOM
VITE_DAILY_ROOM_TOKEN=JWT_TOKEN_FROM_FRESH_SESSION
EOF
```

#### Step 2: Use Direct Daily Room Connection

```typescript
// CORRECT: Direct Daily room connection
<ConsoleTemplate
  transportType="daily"
  connectParams={{
    url: `${import.meta.env.VITE_DAILY_ROOM_URL}`,
    token: `${import.meta.env.VITE_DAILY_ROOM_TOKEN}`
  }}
/>
```

#### Step 3: Start Fresh Agent Session

```bash
# Start new agent session to get active Daily room
pcc agent start convo-lingo-webapp-v1 --use-daily --api-key YOUR_API_KEY

# Output provides fresh room URL and token:
# https://cloud-f62295e899ac41849a4c95b5fb6df25a.daily.co/4sUxuYBtxQSqTLjBPliN?t=JWT_TOKEN
```

#### Step 4: Update Frontend Environment Variables

```bash
# Extract room URL and token from agent start output
# Update frontend/.env with new values
# Restart Vite dev server to pick up changes
```

**Key Learnings:**

1. **Voice UI Kit `daily` transport** expects direct Daily room URL/token, NOT Pipecat Cloud session API
2. **Pipecat Cloud session API** returns `sessionId`, which Voice UI Kit doesn't understand
3. **Environment variables** in Vite must use `VITE_` prefix and plain `KEY=VALUE` format (no `export`)
4. **Fresh agent sessions** are required - old Daily rooms become inactive
5. **SmallWebRTC transport** is for custom backends, not Pipecat Cloud direct connection

**Status**: ✅ **RESOLVED** - Frontend successfully connects to ConvoLingo agent

Last Updated: August 27, 2025
