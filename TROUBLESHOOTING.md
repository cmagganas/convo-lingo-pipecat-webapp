# ConvoLingo Frontend Troubleshooting Guide

## Overview

This guide addresses specific issues with the ConvoLingo React frontend integration with Pipecat Voice UI Kit.

## Current Working State (August 21, 2025)

### ✅ What's Working
- **End-to-end voice conversation**: User speech → Agent response
- **Agent deployment**: `convo-lingo-webapp-v1:0.3` on Pipecat Cloud
- **Frontend connection**: React app connects to agent via Daily WebRTC
- **Audio pipeline**: Cartesia STT/TTS + Google Gemini LLM
- **Real-time conversation**: ConvoLingo greets and responds appropriately

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

Last Updated: August 21, 2025
