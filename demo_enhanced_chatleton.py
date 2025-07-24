#!/usr/bin/env python3
"""
Demo Enhanced Chat-leton GPT
Showcases the full "Suno for Ableton" capabilities with AI-powered music generation
"""

import os
import time
import sys
from enhanced_chatleton_mcp import EnhancedChatletonMCP

def print_banner():
    """Print fancy banner"""
    print("🎵" + "=" * 80 + "🎵")
    print("🎵  CHAT-LETON GPT - AI MUSIC PRODUCER FOR ABLETON LIVE  🎵")
    print("🎵         Your personal 'Suno for Ableton' assistant       🎵") 
    print("🎵    Powered by Google Gemini 2.5 Flash & Working MCP     🎵")
    print("🎵" + "=" * 80 + "🎵")
    print()

def demo_style_generation():
    """Demo different musical style generation"""
    
    # Check API key
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ Please set GOOGLE_AI_API_KEY environment variable")
        print("💡 Get your API key from: https://makersuite.google.com/app/apikey")
        return
    
    print("🧠 Initializing Chat-leton GPT...")
    chatleton = EnhancedChatletonMCP()
    
    # Check status
    status = chatleton.get_status()
    print(f"🤖 AI Engine: {'✅ Gemini 2.5 Flash-Lite' if status['gemini_available'] else '❌ Not available'}")
    
    if not chatleton.connect_ableton():
        print("❌ Cannot connect to Ableton Live")
        print("💡 Make sure Ableton Live is running with AbletonMCP Remote Script")
        return
    
    print(f"🎛️ Ableton Live: ✅ Connected ({status.get('track_count', 0)} tracks)")
    print()
    
    # Demo different styles
    styles_to_demo = [
        {
            'style': 'Afro House',
            'request': 'Create an uplifting Afro House track with deep bass, tribal percussion, and atmospheric pads. Make it feel like a sunset on the beach.',
            'description': 'Afro House with tribal vibes and deep emotion'
        },
        {
            'style': 'Deep House', 
            'request': 'Create a smooth Deep House track with soulful chords, warm bass, and subtle percussion. Perfect for late night listening.',
            'description': 'Smooth and soulful Deep House vibes'
        },
        {
            'style': 'Progressive House',
            'request': 'Create an epic Progressive House track with building energy, powerful leads, and emotional breakdowns.',
            'description': 'Epic Progressive House journey'
        }
    ]
    
    for i, demo in enumerate(styles_to_demo, 1):
        print(f"\n🎵 DEMO {i}/3: {demo['description']}")
        print("=" * 60)
        print(f"🎸 Style: {demo['style']}")
        print(f"💬 Request: {demo['request']}")
        print()
        
        # Let user choose
        choice = input(f"Generate {demo['style']} track? (y/n/skip): ").strip().lower()
        
        if choice == 'skip':
            break
        elif choice != 'y':
            continue
            
        print(f"\n🚀 Generating {demo['style']} track with AI...")
        print("⏰ This may take 30-60 seconds...")
        
        # Generate track
        result = chatleton.create_intelligent_track(demo['style'], demo['request'])
        
        if result['status'] == 'success':
            print(f"\n🎉 SUCCESS! Created {result['style']} track:")
            print(f"   🎛️ Created {result['created_tracks']} tracks")
            print(f"   🕰️ Set tempo to {result['bpm']} BPM") 
            print(f"   ⚡ Performed {len(result['actions_taken'])} actions")
            
            # Show AI insights
            print(f"\n🧠 AI Production Insights:")
            ai_plan = result.get('ai_plan', '')
            # Show first 400 characters of AI plan
            if len(ai_plan) > 400:
                print(ai_plan[:400] + "...")
                print(f"   📝 (Full AI plan: {len(ai_plan)} characters)")
            else:
                print(ai_plan)
            
            print(f"\n✅ {result['message']}")
            print("\n🎧 Check your Ableton Live session - the track should be playing!")
            
            # Wait for user
            input("\n⏸️ Press Enter to continue to next demo...")
            
        else:
            print(f"❌ Failed: {result['message']}")
            
        print("\n" + "─" * 60)
    
    # Cleanup
    chatleton.disconnect_ableton()
    
    print("\n🎉 Demo Complete!")
    print("🎵 You now have working AI-powered music generation in Ableton Live!")

def demo_interactive_chat():
    """Demo interactive chat with AI music producer"""
    
    print("\n🎵 INTERACTIVE CHAT WITH CHAT-LETON GPT")
    print("=" * 60)
    print("💬 Ask Chat-leton GPT anything about music production!")
    print("🎛️ Try questions like:")
    print("   • 'How do I make a fat bass sound?'")
    print("   • 'What's the difference between Afro House and Deep House?'")
    print("   • 'Help me arrange a Progressive House track'")
    print("   • 'What Ableton stock plugins should I use for pads?'")
    print("   • Type 'quit' to exit")
    print()
    
    chatleton = EnhancedChatletonMCP()
    
    if not chatleton.gemini_model:
        print("❌ AI not available. Please set GOOGLE_AI_API_KEY")
        return
    
    while True:
        try:
            question = input("🎤 Ask Chat-leton GPT: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye']:
                print("👋 Thanks for chatting with Chat-leton GPT!")
                break
                
            if not question:
                continue
            
            print("🧠 Chat-leton GPT is thinking...")
            response = chatleton.generate_ai_response(question)
            
            print(f"\n🎵 Chat-leton GPT:")
            print("─" * 40)
            print(response)
            print("─" * 40)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

def main():
    """Main demo function"""
    print_banner()
    
    print("🌟 Welcome to Chat-leton GPT Demo!")
    print("🎯 This demo showcases AI-powered music generation for Ableton Live")
    print()
    
    # Check prerequisites
    print("🔍 Checking prerequisites...")
    
    # Check API key
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if api_key:
        print("✅ Google AI API key found")
    else:
        print("❌ GOOGLE_AI_API_KEY not set")
        print("💡 Get your free API key from: https://makersuite.google.com/app/apikey")
        print("💡 Then run: export GOOGLE_AI_API_KEY='your-key-here'")
        
        choice = input("\nContinue with limited demo? (y/n): ").strip().lower()
        if choice != 'y':
            return
    
    print()
    print("🎮 Demo Options:")
    print("1. 🎵 Generate AI music tracks (requires Ableton Live)")
    print("2. 💬 Interactive chat with AI music producer")
    print("3. 🚀 Both demos")
    print()
    
    choice = input("Choose demo (1/2/3): ").strip()
    
    if choice == '1':
        demo_style_generation()
    elif choice == '2':
        demo_interactive_chat()
    elif choice == '3':
        demo_style_generation()
        demo_interactive_chat()
    else:
        print("❌ Invalid choice")
        return
    
    print("\n🎵 Thanks for trying Chat-leton GPT!")
    print("🌟 The future of AI music production is here!")

if __name__ == "__main__":
    main() 