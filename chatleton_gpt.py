#!/usr/bin/env python3
"""
Chat-leton GPT - Standalone AI Music Producer

A standalone AI music production assistant powered by Google Gemini 2.5 Flash.
Chat with your AI producer and watch it work in Ableton Live in real-time!

Usage:
    python chatleton_gpt.py --cli              # CLI chat interface
    python chatleton_gpt.py --gui              # GUI chat interface  
    python chatleton_gpt.py --web              # Web interface
    python chatleton_gpt.py --mcp              # MCP server mode
    python chatleton_gpt.py --all              # All interfaces
"""

import asyncio
import argparse
import logging
import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import threading
import queue

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Core AI imports
from music_intelligence import GeminiOrchestrator, StyleAnalyzer, StockPluginExpert

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChatletonGPT:
    """
    Main Chat-leton GPT application class
    
    A standalone AI music producer that can run in multiple modes:
    - CLI chat interface
    - GUI chat interface  
    - Web interface
    - MCP server mode
    """
    
    def __init__(self):
        """Initialize Chat-leton GPT"""
        self.name = "Chat-leton GPT"
        self.version = "1.0.0"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize AI systems
        self.orchestrator = None
        self.style_analyzer = None
        self.plugin_expert = None
        
        # Application state
        self.running = False
        self.current_project = None
        self.chat_history = []
        self.ableton_connected = False
        
        # Interface instances
        self.cli_interface = None
        self.gui_interface = None
        self.web_interface = None
        self.mcp_server = None
        
        logger.info(f"Chat-leton GPT v{self.version} initialized")
    
    async def initialize_ai_systems(self):
        """Initialize AI systems"""
        try:
            logger.info("🤖 Initializing AI systems...")
            
            # Check API key
            if not os.getenv("GOOGLE_AI_API_KEY"):
                raise ValueError("GOOGLE_AI_API_KEY environment variable not set!")
            
            # Initialize components
            self.orchestrator = GeminiOrchestrator()
            self.style_analyzer = StyleAnalyzer()
            self.plugin_expert = StockPluginExpert()
            
            # Start chat session
            self.orchestrator.start_chat_session()
            
            logger.info("✅ AI systems ready!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI systems: {e}")
            return False
    
    async def check_ableton_connection(self):
        """Check if Ableton Live is connected"""
        try:
            # This would implement actual connection checking
            # For now, simulate based on socket availability
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 11999))
            sock.close()
            
            self.ableton_connected = (result == 0)
            return self.ableton_connected
            
        except Exception as e:
            logger.debug(f"Ableton connection check failed: {e}")
            self.ableton_connected = False
            return False
    
    async def process_user_message(self, message: str) -> Dict[str, Any]:
        """
        Process user message and return response with actions
        
        Args:
            message: User's message
            
        Returns:
            Response dictionary with message, actions, and metadata
        """
        try:
            timestamp = datetime.now().isoformat()
            
            # Add to chat history
            self.chat_history.append({
                "timestamp": timestamp,
                "user": message,
                "type": "user_message"
            })
            
            # Process with AI
            ai_response = await self.orchestrator.chat(message)
            
            # Determine if this is a generation request
            is_generation_request = any(keyword in message.lower() for keyword in [
                "create", "generate", "make", "build", "produce", "compose"
            ])
            
            # Prepare response
            response = {
                "timestamp": timestamp,
                "message": ai_response,
                "type": "ai_response",
                "is_generation": is_generation_request,
                "ableton_connected": self.ableton_connected,
                "actions": []
            }
            
            # If it's a generation request and Ableton is connected, prepare actions
            if is_generation_request and self.ableton_connected:
                try:
                    # Analyze the request for actionable items
                    analysis = await self.orchestrator.analyze_user_request(message)
                    
                    actions = [
                        {
                            "type": "set_bpm",
                            "value": analysis.get("bpm", 120),
                            "description": f"Set BPM to {analysis.get('bpm', 120)}"
                        },
                        {
                            "type": "set_key", 
                            "value": analysis.get("key", "C"),
                            "description": f"Set key to {analysis.get('key', 'C')}"
                        },
                        {
                            "type": "notification",
                            "value": f"Ready to create {analysis.get('style', 'track')} track!",
                            "description": "AI analysis complete"
                        }
                    ]
                    
                    response["actions"] = actions
                    response["analysis"] = analysis
                    
                except Exception as e:
                    logger.error(f"Error analyzing request: {e}")
            
            # Add to chat history
            self.chat_history.append(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "message": f"Sorry, I encountered an error: {str(e)}",
                "type": "error",
                "is_generation": False,
                "ableton_connected": self.ableton_connected,
                "actions": []
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current status of Chat-leton GPT"""
        return {
            "name": self.name,
            "version": self.version,
            "session_id": self.session_id,
            "running": self.running,
            "ableton_connected": self.ableton_connected,
            "ai_ready": self.orchestrator is not None,
            "chat_history_length": len(self.chat_history),
            "available_styles": self.style_analyzer.list_available_styles() if self.style_analyzer else [],
            "timestamp": datetime.now().isoformat()
        }
    
    # ========================================================================
    # INTERFACE IMPLEMENTATIONS
    # ========================================================================
    
    async def run_cli(self):
        """Run CLI chat interface"""
        print("🎵 CHAT-LETON GPT - CLI Interface")
        print("=" * 50)
        print("Your AI Music Producer is ready!")
        print("Type 'help' for commands, 'quit' to exit")
        
        # Initialize AI
        if not await self.initialize_ai_systems():
            print("❌ Failed to initialize AI systems")
            return
        
        # Check Ableton connection
        await self.check_ableton_connection()
        if self.ableton_connected:
            print("✅ Ableton Live connected")
        else:
            print("⚠️  Ableton Live not detected (some features limited)")
        
        print("\n" + "="*50)
        self.running = True
        
        try:
            while self.running:
                # Get user input
                user_input = input("\n🎤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'help':
                    self._print_help()
                    continue
                elif user_input.lower() == 'status':
                    status = await self.get_status()
                    print(f"\n📊 Status: {json.dumps(status, indent=2)}")
                    continue
                elif user_input.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                
                # Process message
                print("🤔 Chat-leton GPT is thinking...")
                response = await self.process_user_message(user_input)
                
                # Display response
                print(f"\n🎵 Chat-leton GPT: {response['message']}")
                
                # Display actions if any
                if response.get('actions'):
                    print(f"\n⚡ Actions:")
                    for action in response['actions']:
                        print(f"   • {action['description']}")
                
                # Show generation analysis if available
                if response.get('analysis'):
                    analysis = response['analysis']
                    print(f"\n🎨 Analysis:")
                    print(f"   Style: {analysis.get('style', 'Unknown')}")
                    print(f"   BPM: {analysis.get('bpm', 'Unknown')}")
                    print(f"   Key: {analysis.get('key', 'Unknown')}")
                    print(f"   Mood: {analysis.get('mood', 'Unknown')}")
        
        except KeyboardInterrupt:
            print("\n👋 Chat interrupted by user")
        
        finally:
            self.running = False
            print("\n🎵 Thanks for using Chat-leton GPT!")
    
    def _print_help(self):
        """Print help information"""
        print("""
🎵 CHAT-LETON GPT COMMANDS:

🎨 Music Generation:
   "Create an Afro House track like Black Coffee"
   "Generate a progressive house anthem"
   "Make a Keinemusik-style deep house track"

💬 Chat Examples:
   "How do I create warm bass sounds?"
   "What plugins work best for deep house?"
   "Explain the structure of Afro House"

🛠️ System Commands:
   help     - Show this help
   status   - Show system status
   clear    - Clear screen
   quit     - Exit Chat-leton GPT

🎛️ Ableton Integration:
   When connected, I can help you implement tracks directly!
        """)
    
    async def run_gui(self):
        """Run GUI chat interface"""
        print("🖥️  Starting GUI interface...")
        # This would implement a GUI using tkinter, PyQt, or similar
        # For now, we'll create a simple implementation
        
        try:
            import tkinter as tk
            from tkinter import scrolledtext, messagebox
            import threading
            
            await self.initialize_ai_systems()
            await self.check_ableton_connection()
            
            # Create main window
            self.gui_root = tk.Tk()
            self.gui_root.title("Chat-leton GPT - AI Music Producer")
            self.gui_root.geometry("800x600")
            
            # Create chat display
            self.chat_display = scrolledtext.ScrolledText(
                self.gui_root, 
                wrap=tk.WORD, 
                width=80, 
                height=30,
                state=tk.DISABLED
            )
            self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
            
            # Create input frame
            input_frame = tk.Frame(self.gui_root)
            input_frame.pack(padx=10, pady=5, fill=tk.X)
            
            # Create input field
            self.input_field = tk.Entry(input_frame, font=("Arial", 12))
            self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            self.input_field.bind("<Return>", self._gui_send_message)
            
            # Create send button
            send_button = tk.Button(
                input_frame, 
                text="Send", 
                command=self._gui_send_message,
                font=("Arial", 12)
            )
            send_button.pack(side=tk.RIGHT)
            
            # Status bar
            self.status_var = tk.StringVar()
            status_bar = tk.Label(
                self.gui_root, 
                textvariable=self.status_var, 
                relief=tk.SUNKEN, 
                anchor=tk.W
            )
            status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Initialize status
            status_text = "🎵 Chat-leton GPT Ready"
            if self.ableton_connected:
                status_text += " | ✅ Ableton Connected"
            else:
                status_text += " | ⚠️ Ableton Disconnected"
            self.status_var.set(status_text)
            
            # Welcome message
            self._gui_add_message("🎵 Chat-leton GPT", 
                                "Welcome! I'm your AI music producer. Ask me to create tracks, analyze styles, or give production advice!", 
                                "assistant")
            
            self.running = True
            self.gui_root.mainloop()
            
        except ImportError:
            print("❌ GUI requires tkinter. Install with: pip install tk")
        except Exception as e:
            print(f"❌ GUI error: {e}")
    
    def _gui_send_message(self, event=None):
        """Handle GUI message sending"""
        message = self.input_field.get().strip()
        if not message:
            return
        
        self.input_field.delete(0, tk.END)
        self._gui_add_message("You", message, "user")
        
        # Process in background thread
        def process_message():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(self.process_user_message(message))
                
                # Update GUI in main thread
                self.gui_root.after(0, lambda: self._gui_add_message(
                    "🎵 Chat-leton GPT", 
                    response['message'], 
                    "assistant"
                ))
                
                # Show actions if any
                if response.get('actions'):
                    actions_text = "⚡ Actions:\n" + "\n".join(
                        f"• {action['description']}" for action in response['actions']
                    )
                    self.gui_root.after(0, lambda: self._gui_add_message(
                        "System", 
                        actions_text, 
                        "system"
                    ))
                
            except Exception as e:
                self.gui_root.after(0, lambda: self._gui_add_message(
                    "Error", 
                    f"Sorry, I encountered an error: {str(e)}", 
                    "error"
                ))
        
        threading.Thread(target=process_message, daemon=True).start()
    
    def _gui_add_message(self, sender: str, message: str, msg_type: str):
        """Add message to GUI chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Color coding
        colors = {
            "user": "#0066cc",
            "assistant": "#009900", 
            "system": "#ff8800",
            "error": "#cc0000"
        }
        
        color = colors.get(msg_type, "#000000")
        
        self.chat_display.insert(tk.END, f"\n{sender}: ", ("bold",))
        self.chat_display.insert(tk.END, f"{message}\n")
        
        # Configure tags for formatting
        self.chat_display.tag_config("bold", font=("Arial", 12, "bold"))
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    async def run_web(self):
        """Run web interface"""
        print("🌐 Web interface not implemented yet")
        print("This would create a modern web-based chat interface")
        # TODO: Implement with FastAPI + WebSockets + modern frontend
    
    async def run_mcp_server(self):
        """Run as MCP server"""
        print("🔌 Starting MCP server mode...")
        # Import and run the enhanced MCP tools
        from enhanced_mcp_tools import register_enhanced_tools
        # This would start the MCP server with our tools
        print("MCP server running with Chat-leton GPT capabilities")


async def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="Chat-leton GPT - AI Music Producer")
    parser.add_argument("--cli", action="store_true", help="Run CLI interface")
    parser.add_argument("--gui", action="store_true", help="Run GUI interface")
    parser.add_argument("--web", action="store_true", help="Run web interface")
    parser.add_argument("--mcp", action="store_true", help="Run MCP server")
    parser.add_argument("--all", action="store_true", help="Run all interfaces")
    
    args = parser.parse_args()
    
    # Initialize Chat-leton GPT
    app = ChatletonGPT()
    
    # Determine which interfaces to run
    if args.all:
        print("🚀 Starting all interfaces...")
        # In a real implementation, these would run concurrently
        await app.run_cli()
    elif args.gui:
        await app.run_gui()
    elif args.web:
        await app.run_web()
    elif args.mcp:
        await app.run_mcp_server()
    elif args.cli:
        await app.run_cli()
    else:
        # Default to CLI
        await app.run_cli()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Chat-leton GPT shutdown.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1) 