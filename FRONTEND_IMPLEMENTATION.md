# ConvoLingo Frontend Implementation Plan

## 🎯 Goal
Create a simple frontend to test and develop with our working `convo-lingo-webapp-v1` agent, with live logs for debugging.

## 📋 Implementation Steps

### Option 1: Quick Start with Voice UI Kit (RECOMMENDED)

**Why this approach:**
- ✅ Ready-made interface with debug console
- ✅ Built-in log viewing and real-time monitoring  
- ✅ No custom UI development needed
- ✅ Perfect for iterative development and testing

#### 1. Clone the quickstart template
```bash
cd /Users/christos/cmagganas/pipecat-ai/
git clone https://github.com/pipecat-ai/pipecat-quickstart-client-server.git convo-lingo-frontend
cd convo-lingo-frontend
```

#### 2. Modify the client to connect to our agent
**File: `client/src/main.tsx`**
```tsx
import {
  ConsoleTemplate,
  FullScreenContainer, 
  ThemeProvider,
} from "@pipecat-ai/voice-ui-kit";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <FullScreenContainer>
        <ConsoleTemplate
          transportType="daily" // Use Daily transport for Pipecat Cloud
          connectParams={{
            // Connect directly to our deployed agent
            baseUrl: "https://api.pipecat.daily.co/v1/public/convo-lingo-webapp-v1/start",
            headers: {
              "Authorization": "Bearer YOUR_PUBLIC_API_KEY"  // From: pcc organizations keys create
            }
          }}
        />
      </FullScreenContainer>
    </ThemeProvider>
  </StrictMode>
);
```

#### 3. Set up the frontend
```bash
cd client
npm install
npm run dev
```

#### 4. Get your public API key
```bash
# In your convo-lingo-pipecat-webapp directory
pcc organizations keys create --name "frontend-dev-key"
```

#### 5. Launch with logs in split terminal
```bash
# Terminal 1: Frontend
cd /Users/christos/cmagganas/pipecat-ai/convo-lingo-frontend/client
npm run dev

# Terminal 2: Backend logs (live monitoring)
cd /Users/christos/cmagganas/pipecat-ai/convo-lingo-pipecat-webapp
while true; do 
  echo "=== Latest Agent Activity ==="
  pcc agent logs convo-lingo-webapp-v1 | tail -10
  sleep 3
done
```

### Option 2: Embedded Agent Launcher (Custom but Simple)

If you want a more integrated approach, create a simple HTML page that:
1. Starts your agent session
2. Embeds the Daily room
3. Shows logs in a side panel

**File: `convo-lingo-pipecat-webapp/launcher.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>ConvoLingo Agent Launcher</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; display: flex; height: 100vh; }
        .left-panel { width: 70%; }
        .right-panel { width: 30%; background: #1a1a1a; color: #00ff00; padding: 10px; overflow-y: scroll; }
        #daily-frame { width: 100%; height: 100%; border: none; }
        .logs { font-family: monospace; font-size: 12px; }
        .controls { padding: 10px; background: #f0f0f0; }
        button { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="left-panel">
        <div class="controls">
            <button onclick="startAgent()">🚀 Start New Session</button>
            <button onclick="refreshLogs()">🔄 Refresh Logs</button>
            <span id="status">Ready</span>
        </div>
        <iframe id="daily-frame" src="about:blank"></iframe>
    </div>
    
    <div class="right-panel">
        <h3>🔍 Live Agent Logs</h3>
        <div id="logs" class="logs">Click "Start New Session" to begin...</div>
    </div>

    <script>
        let currentSessionUrl = '';
        
        async function startAgent() {
            document.getElementById('status').textContent = 'Starting agent...';
            
            try {
                // In a real implementation, this would call your backend
                // For now, manually start the agent and get the URL
                const response = await fetch('/api/start-agent', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ agent: 'convo-lingo-webapp-v1' })
                });
                
                const data = await response.json();
                currentSessionUrl = data.roomUrl;
                
                document.getElementById('daily-frame').src = currentSessionUrl;
                document.getElementById('status').textContent = 'Session active';
                
                // Start log polling
                pollLogs();
                
            } catch (error) {
                document.getElementById('status').textContent = 'Error: ' + error.message;
            }
        }
        
        async function pollLogs() {
            try {
                const response = await fetch('/api/agent-logs');
                const logs = await response.text();
                document.getElementById('logs').innerHTML = logs.replace(/\n/g, '<br>');
            } catch (error) {
                console.error('Log fetch error:', error);
            }
            
            // Poll every 2 seconds
            if (currentSessionUrl) {
                setTimeout(pollLogs, 2000);
            }
        }
        
        function refreshLogs() {
            if (currentSessionUrl) pollLogs();
        }
    </script>
</body>
</html>
```

## 🛠️ Backend API for Agent Control

Create a simple Express server to handle agent operations:

**File: `convo-lingo-pipecat-webapp/launcher-server.js`**
```javascript
const express = require('express');
const { exec } = require('child_process');
const app = express();

app.use(express.json());
app.use(express.static('.'));

// Start agent session
app.post('/api/start-agent', async (req, res) => {
    exec('pcc agent start convo-lingo-webapp-v1 --use-daily', (error, stdout, stderr) => {
        if (error) {
            return res.status(500).json({ error: error.message });
        }
        
        // Parse the Daily room URL from stdout
        const urlMatch = stdout.match(/https:\/\/cloud-[^\\s]+/);
        const roomUrl = urlMatch ? urlMatch[0] : null;
        
        res.json({ roomUrl, output: stdout });
    });
});

// Get agent logs
app.get('/api/agent-logs', (req, res) => {
    exec('pcc agent logs convo-lingo-webapp-v1 | tail -20', (error, stdout, stderr) => {
        res.text(stdout || stderr || 'No logs available');
    });
});

app.listen(3000, () => {
    console.log('ConvoLingo launcher server running on http://localhost:3000');
    console.log('Open launcher.html to start testing!');
});
```

## 🚀 **Quick Start Commands**

### Recommended: Voice UI Kit Approach
```bash
# 1. Clone and set up frontend
cd /Users/christos/cmagganas/pipecat-ai/
git clone https://github.com/pipecat-ai/pipecat-quickstart-client-server.git convo-lingo-frontend

# 2. Get API key
cd convo-lingo-pipecat-webapp
pcc organizations keys create --name "frontend-dev-key"

# 3. Configure client (update client/src/main.tsx with your API key)
cd ../convo-lingo-frontend/client
npm install

# 4. Launch with split terminals:
# Terminal 1: Frontend
npm run dev

# Terminal 2: Live logs
cd ../../convo-lingo-pipecat-webapp
watch -n 2 'pcc agent logs convo-lingo-webapp-v1 | tail -10'
```

### Alternative: Custom Launcher
```bash
# 1. Install dependencies
cd convo-lingo-pipecat-webapp
npm init -y
npm install express

# 2. Create launcher files (launcher.html and launcher-server.js)
# 3. Start launcher
node launcher-server.js
# Open http://localhost:3000/launcher.html
```

## 🎯 **Next Development Steps**

1. **Test current flow** with the Voice UI Kit console
2. **Monitor logs** to understand conversation patterns  
3. **Iterate on prompts** and flow configuration
4. **Add custom UI elements** as needed
5. **Deploy frontend** when ready for production

The Voice UI Kit approach gives you immediate debugging capabilities and a professional interface for testing your German language learning conversations!
