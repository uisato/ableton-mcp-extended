#!/usr/bin/env python3
"""
Chat-leton GPT Launcher

Simple launcher script to run Chat-leton GPT in any interface mode.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print the Chat-leton GPT banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║    🎵  CHAT-LETON GPT - AI MUSIC PRODUCER  🎵            ║
    ║                                                           ║
    ║         Your personal AI music production assistant       ║
    ║         Powered by Google Gemini 2.5 Flash              ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_requirements():
    """Check basic requirements"""
    print("🔍 Checking requirements...")
    
    # Check API key
    if not os.getenv("GOOGLE_AI_API_KEY"):
        print("❌ GOOGLE_AI_API_KEY not set!")
        print("\n📝 Quick Setup:")
        print("1. Get your API key from: https://aistudio.google.com/app/apikey")
        print("2. Set it: export GOOGLE_AI_API_KEY='your-api-key-here'")
        print("3. Run this script again")
        return False
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    print("✅ Requirements check passed")
    return True

def show_menu():
    """Show interface selection menu"""
    print("\n🎛️ Choose your interface:")
    print("1. 💬 CLI Chat Interface (Terminal-based)")
    print("2. 🖥️  GUI Chat Interface (Desktop app)")
    print("3. 🌐 Web Chat Interface (Browser-based)")
    print("4. 🔌 MCP Server Mode (For Claude/Cursor)")
    print("5. 🧪 Run Demo")
    print("6. 🔧 Test Installation")
    print("7. 🎛️ Test Ableton Integration")
    print("0. ❌ Exit")
    
    while True:
        choice = input("\n🎤 Your choice (0-7): ").strip()
        if choice in ['0', '1', '2', '3', '4', '5', '6', '7']:
            return choice
        print("❌ Invalid choice. Please enter 0-7.")

def launch_interface(choice):
    """Launch the selected interface"""
    project_root = Path(__file__).parent
    
    if choice == '1':
        print("🚀 Launching CLI interface...")
        subprocess.run([sys.executable, str(project_root / "chatleton_gpt.py"), "--cli"])
    
    elif choice == '2':
        print("🚀 Launching GUI interface...")
        try:
            subprocess.run([sys.executable, str(project_root / "chatleton_gpt.py"), "--gui"])
        except Exception as e:
            print(f"❌ GUI error: {e}")
            print("💡 Try: pip install tk")
    
    elif choice == '3':
        print("🚀 Launching web interface...")
        print("🌐 Opening browser to: http://localhost:8000")
        try:
            subprocess.run([sys.executable, str(project_root / "chatleton_web.py")])
        except Exception as e:
            print(f"❌ Web interface error: {e}")
            print("💡 Try: pip install fastapi uvicorn jinja2")
    
    elif choice == '4':
        print("🚀 Starting MCP server...")
        subprocess.run([sys.executable, str(project_root / "chatleton_gpt.py"), "--mcp"])
    
    elif choice == '5':
        print("🚀 Running demo...")
        subprocess.run([sys.executable, str(project_root / "demo_ai_music_producer.py")])
    
    elif choice == '6':
        print("🚀 Testing installation...")
        subprocess.run([sys.executable, str(project_root / "test_ai_producer.py")])
    
    elif choice == '7':
        print("🚀 Testing Ableton integration...")
        # Ask for test type
        print("\n🎛️ Ableton Integration Test Options:")
        print("a. 🚀 Quick connection test")
        print("b. 🔧 Full test suite")
        print("c. 💬 Interactive test with setup checks")
        
        test_choice = input("\nChoose test type (a/b/c): ").strip().lower()
        
        if test_choice == 'a':
            subprocess.run([sys.executable, str(project_root / "test_ableton_integration.py"), "--quick"])
        elif test_choice == 'b':
            subprocess.run([sys.executable, str(project_root / "test_ableton_integration.py")])
        elif test_choice == 'c':
            subprocess.run([sys.executable, str(project_root / "test_ableton_integration.py"), "--interactive"])
        else:
            print("❌ Invalid test choice")
    
    elif choice == '0':
        print("👋 Goodbye!")
        sys.exit(0)

def main():
    """Main launcher function"""
    print_banner()
    
    if not check_requirements():
        sys.exit(1)
    
    while True:
        choice = show_menu()
        
        if choice == '0':
            print("👋 Thanks for using Chat-leton GPT!")
            break
        
        try:
            launch_interface(choice)
        except KeyboardInterrupt:
            print("\n⏹️  Interrupted by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Ask if they want to continue
        if choice != '0':
            continue_choice = input("\n🔄 Launch another interface? (y/n): ").strip().lower()
            if continue_choice != 'y':
                print("👋 Thanks for using Chat-leton GPT!")
                break

if __name__ == "__main__":
    main() 