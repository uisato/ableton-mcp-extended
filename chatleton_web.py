#!/usr/bin/env python3
"""
Chat-leton GPT - Web Interface

Modern web-based chat interface for the AI Music Producer.
Includes real-time chat, Ableton status monitoring, and beautiful UI.

Usage:
    python chatleton_web.py
    
Then open: http://localhost:8000
"""

import asyncio
import logging
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse
    from fastapi.templating import Jinja2Templates
    import uvicorn
except ImportError:
    print("❌ Web interface requires FastAPI. Install with:")
    print("   pip install fastapi uvicorn jinja2 python-multipart")
    sys.exit(1)

# Core AI imports
from music_intelligence import GeminiOrchestrator, StyleAnalyzer, StockPluginExpert
from chatleton_gpt import ChatletonGPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Chat-leton GPT", description="AI Music Producer Web Interface")

# Templates
templates = Jinja2Templates(directory="templates")

# Global Chat-leton GPT instance
chatleton_app = None

# Connected WebSocket clients
connected_clients: List[WebSocket] = []


@app.on_event("startup")
async def startup_event():
    """Initialize Chat-leton GPT on startup"""
    global chatleton_app
    chatleton_app = ChatletonGPT()
    await chatleton_app.initialize_ai_systems()
    await chatleton_app.check_ableton_connection()
    logger.info("Chat-leton GPT web interface started")


@app.get("/", response_class=HTMLResponse)
async def get_homepage(request: Request):
    """Serve the main chat interface"""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/api/status")
async def get_status():
    """Get system status"""
    if chatleton_app:
        return await chatleton_app.get_status()
    return {"error": "System not initialized"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        # Send welcome message
        welcome_msg = {
            "type": "assistant_message",
            "message": "🎵 Welcome to Chat-leton GPT! I'm your AI music producer. What would you like to create today?",
            "timestamp": datetime.now().isoformat(),
            "actions": []
        }
        await websocket.send_text(json.dumps(welcome_msg))
        
        # Send system status
        if chatleton_app:
            status = await chatleton_app.get_status()
            status_msg = {
                "type": "system_status",
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_text(json.dumps(status_msg))
        
        # Main message loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "user_message":
                user_message = message_data.get("message", "").strip()
                
                if user_message and chatleton_app:
                    # Process the message
                    response = await chatleton_app.process_user_message(user_message)
                    
                    # Send response back
                    response_msg = {
                        "type": "assistant_message",
                        "message": response.get("message", ""),
                        "timestamp": response.get("timestamp"),
                        "actions": response.get("actions", []),
                        "analysis": response.get("analysis"),
                        "is_generation": response.get("is_generation", False)
                    }
                    await websocket.send_text(json.dumps(response_msg))
                    
                    # Broadcast to other clients if needed
                    for client in connected_clients:
                        if client != websocket:
                            try:
                                await client.send_text(json.dumps({
                                    "type": "other_user_activity",
                                    "message": f"Another user: {user_message[:50]}...",
                                    "timestamp": datetime.now().isoformat()
                                }))
                            except:
                                pass
            
            elif message_data.get("type") == "status_request":
                # Send updated status
                if chatleton_app:
                    await chatleton_app.check_ableton_connection()
                    status = await chatleton_app.get_status()
                    status_msg = {
                        "type": "system_status",
                        "status": status,
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_text(json.dumps(status_msg))
    
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in connected_clients:
            connected_clients.remove(websocket)


def create_templates_directory():
    """Create templates directory and HTML file"""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    chat_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat-leton GPT - AI Music Producer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: rgba(0, 0, 0, 0.2);
            color: white;
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .header h1 {
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .status {
            display: flex;
            align-items: center;
            gap: 1rem;
            font-size: 0.9rem;
        }
        
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4CAF50;
        }
        
        .status-indicator.disconnected {
            background: #f44336;
        }
        
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
            padding: 0 1rem;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .message {
            max-width: 80%;
            padding: 1rem;
            border-radius: 1rem;
            word-wrap: break-word;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message.user {
            align-self: flex-end;
            background: #2196F3;
            color: white;
        }
        
        .message.assistant {
            align-self: flex-start;
            background: white;
            color: #333;
            border-left: 4px solid #4CAF50;
        }
        
        .message.system {
            align-self: center;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 0.9rem;
            max-width: 60%;
        }
        
        .message-header {
            font-weight: bold;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            opacity: 0.8;
        }
        
        .actions {
            margin-top: 1rem;
            padding: 1rem;
            background: rgba(76, 175, 80, 0.1);
            border-radius: 0.5rem;
            border-left: 3px solid #4CAF50;
        }
        
        .actions h4 {
            margin-bottom: 0.5rem;
            color: #4CAF50;
        }
        
        .actions ul {
            list-style: none;
        }
        
        .actions li {
            padding: 0.25rem 0;
        }
        
        .analysis {
            margin-top: 1rem;
            padding: 1rem;
            background: rgba(33, 150, 243, 0.1);
            border-radius: 0.5rem;
            border-left: 3px solid #2196F3;
        }
        
        .analysis h4 {
            margin-bottom: 0.5rem;
            color: #2196F3;
        }
        
        .input-container {
            padding: 1rem;
            background: rgba(0, 0, 0, 0.1);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .input-form {
            display: flex;
            gap: 0.5rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        #messageInput {
            flex: 1;
            padding: 1rem;
            border: none;
            border-radius: 2rem;
            font-size: 1rem;
            outline: none;
        }
        
        #sendButton {
            padding: 1rem 2rem;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 2rem;
            cursor: pointer;
            font-size: 1rem;
            transition: background 0.2s;
        }
        
        #sendButton:hover {
            background: #45a049;
        }
        
        #sendButton:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .typing-indicator {
            display: none;
            align-self: flex-start;
            padding: 1rem;
            background: white;
            border-radius: 1rem;
            border-left: 4px solid #4CAF50;
            color: #666;
            font-style: italic;
        }
        
        .typing-dots {
            display: inline-flex;
            gap: 3px;
        }
        
        .typing-dots span {
            width: 6px;
            height: 6px;
            background: #666;
            border-radius: 50%;
            animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        .typing-dots span:nth-child(3) { animation-delay: 0s; }
        
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        
        .generation-badge {
            display: inline-block;
            background: #FF9800;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 1rem;
            font-size: 0.8rem;
            margin-left: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎵 Chat-leton GPT</h1>
        <div class="status">
            <div class="status-indicator" id="aiStatus"></div>
            <span id="aiStatusText">AI Ready</span>
            <div class="status-indicator" id="abletonStatus"></div>
            <span id="abletonStatusText">Checking Ableton...</span>
        </div>
    </div>
    
    <div class="chat-container">
        <div class="chat-messages" id="chatMessages">
            <!-- Messages will be added here -->
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            🎵 Chat-leton GPT is thinking
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    </div>
    
    <div class="input-container">
        <form class="input-form" id="messageForm">
            <input type="text" id="messageInput" placeholder="Ask me to create a track, analyze a style, or give production advice..." autocomplete="off">
            <button type="submit" id="sendButton">Send</button>
        </form>
    </div>

    <script>
        class ChatletonGPTClient {
            constructor() {
                this.ws = null;
                this.messageInput = document.getElementById('messageInput');
                this.sendButton = document.getElementById('sendButton');
                this.chatMessages = document.getElementById('chatMessages');
                this.typingIndicator = document.getElementById('typingIndicator');
                this.messageForm = document.getElementById('messageForm');
                
                this.setupEventListeners();
                this.connect();
            }
            
            setupEventListeners() {
                this.messageForm.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.sendMessage();
                });
                
                this.messageInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this.sendMessage();
                    }
                });
            }
            
            connect() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;
                
                this.ws = new WebSocket(wsUrl);
                
                this.ws.onopen = () => {
                    console.log('Connected to Chat-leton GPT');
                    this.updateConnectionStatus(true);
                };
                
                this.ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                };
                
                this.ws.onclose = () => {
                    console.log('Disconnected from Chat-leton GPT');
                    this.updateConnectionStatus(false);
                    // Attempt to reconnect after 3 seconds
                    setTimeout(() => this.connect(), 3000);
                };
                
                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };
            }
            
            sendMessage() {
                const message = this.messageInput.value.trim();
                if (!message || !this.ws || this.ws.readyState !== WebSocket.OPEN) return;
                
                // Add user message to chat
                this.addMessage('user', message);
                
                // Send to server
                this.ws.send(JSON.stringify({
                    type: 'user_message',
                    message: message
                }));
                
                // Clear input and show typing indicator
                this.messageInput.value = '';
                this.showTypingIndicator();
                this.sendButton.disabled = true;
            }
            
            handleMessage(data) {
                switch (data.type) {
                    case 'assistant_message':
                        this.hideTypingIndicator();
                        this.addMessage('assistant', data.message, data.actions, data.analysis, data.is_generation);
                        this.sendButton.disabled = false;
                        break;
                        
                    case 'system_status':
                        this.updateSystemStatus(data.status);
                        break;
                        
                    case 'other_user_activity':
                        this.addMessage('system', data.message);
                        break;
                }
            }
            
            addMessage(type, message, actions = null, analysis = null, isGeneration = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                
                let content = '';
                
                if (type === 'user') {
                    content = `<div class="message-header">You</div>${message}`;
                } else if (type === 'assistant') {
                    const badge = isGeneration ? '<span class="generation-badge">🎵 Generation</span>' : '';
                    content = `<div class="message-header">🎵 Chat-leton GPT${badge}</div>${message}`;
                    
                    if (actions && actions.length > 0) {
                        content += `
                            <div class="actions">
                                <h4>⚡ Actions:</h4>
                                <ul>
                                    ${actions.map(action => `<li>• ${action.description}</li>`).join('')}
                                </ul>
                            </div>
                        `;
                    }
                    
                    if (analysis) {
                        content += `
                            <div class="analysis">
                                <h4>🎨 Analysis:</h4>
                                <p><strong>Style:</strong> ${analysis.style || 'Unknown'}</p>
                                <p><strong>BPM:</strong> ${analysis.bpm || 'Unknown'}</p>
                                <p><strong>Key:</strong> ${analysis.key || 'Unknown'}</p>
                                <p><strong>Mood:</strong> ${analysis.mood || 'Unknown'}</p>
                            </div>
                        `;
                    }
                } else if (type === 'system') {
                    content = message;
                }
                
                messageDiv.innerHTML = content;
                this.chatMessages.appendChild(messageDiv);
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }
            
            showTypingIndicator() {
                this.typingIndicator.style.display = 'flex';
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }
            
            hideTypingIndicator() {
                this.typingIndicator.style.display = 'none';
            }
            
            updateConnectionStatus(connected) {
                const aiStatus = document.getElementById('aiStatus');
                const aiStatusText = document.getElementById('aiStatusText');
                
                if (connected) {
                    aiStatus.classList.remove('disconnected');
                    aiStatusText.textContent = 'AI Ready';
                } else {
                    aiStatus.classList.add('disconnected');
                    aiStatusText.textContent = 'AI Disconnected';
                }
            }
            
            updateSystemStatus(status) {
                const abletonStatus = document.getElementById('abletonStatus');
                const abletonStatusText = document.getElementById('abletonStatusText');
                
                if (status.ableton_connected) {
                    abletonStatus.classList.remove('disconnected');
                    abletonStatusText.textContent = 'Ableton Connected';
                } else {
                    abletonStatus.classList.add('disconnected');
                    abletonStatusText.textContent = 'Ableton Disconnected';
                }
            }
        }
        
        // Initialize the client when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            new ChatletonGPTClient();
        });
    </script>
</body>
</html>"""
    
    with open(templates_dir / "chat.html", "w") as f:
        f.write(chat_html)


def main():
    """Main function to run the web interface"""
    # Create templates
    create_templates_directory()
    
    # Check API key
    if not os.getenv("GOOGLE_AI_API_KEY"):
        print("❌ GOOGLE_AI_API_KEY environment variable not set!")
        print("   Set it with: export GOOGLE_AI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    print("🌐 Starting Chat-leton GPT Web Interface...")
    print("🎵 Open your browser to: http://localhost:8000")
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=False
    )


if __name__ == "__main__":
    main() 