#!/usr/bin/env python3
"""
AI Music Producer Demo

This script demonstrates the AI Music Producer extension using Google Gemini 2.5 Flash
to generate complete music tracks in Ableton Live.

Usage:
    python demo_ai_music_producer.py

Requirements:
    - Set GOOGLE_AI_API_KEY environment variable
    - Install requirements: pip install -r requirements.txt
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from music_intelligence import GeminiOrchestrator, StyleAnalyzer, StockPluginExpert

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIProducerDemo:
    """Demo class for the AI Music Producer"""
    
    def __init__(self):
        """Initialize the demo"""
        logger.info("🎵 Initializing AI Music Producer Demo...")
        
        # Check for API key
        if not os.getenv("GOOGLE_AI_API_KEY"):
            logger.error("❌ GOOGLE_AI_API_KEY environment variable not set!")
            logger.info("Please set your Google AI API key:")
            logger.info("export GOOGLE_AI_API_KEY='your-api-key-here'")
            sys.exit(1)
        
        try:
            # Initialize AI systems
            self.orchestrator = GeminiOrchestrator()
            self.style_analyzer = StyleAnalyzer()
            self.plugin_expert = StockPluginExpert()
            
            logger.info("✅ AI Music Producer initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI systems: {e}")
            sys.exit(1)
    
    async def demo_style_analysis(self):
        """Demonstrate style analysis capabilities"""
        print("\n" + "="*60)
        print("🎨 STYLE ANALYSIS DEMO")
        print("="*60)
        
        # Test different artists and styles
        test_artists = ["Black Coffee", "Keinemusik", "Dixon", "Eric Prydz"]
        
        for artist in test_artists:
            print(f"\n🎤 Analyzing style for: {artist}")
            style_chars = self.style_analyzer.analyze_artist_style(artist)
            
            print(f"   📊 BPM Range: {style_chars.bpm_range[0]}-{style_chars.bpm_range[1]}")
            print(f"   🎹 Key Preferences: {', '.join(style_chars.key_preferences[:3])}")
            print(f"   🎵 Signature Techniques: {', '.join(style_chars.signature_techniques[:2])}")
            print(f"   ⚡ Energy Curve: {style_chars.energy_curve}")
    
    async def demo_user_request_analysis(self):
        """Demonstrate user request analysis"""
        print("\n" + "="*60)
        print("🎯 USER REQUEST ANALYSIS DEMO")
        print("="*60)
        
        test_requests = [
            "Create an afro house track in the style of Black Coffee at 122 BPM",
            "I want a deep house track with sophisticated chords like Keinemusik",
            "Make me a progressive house anthem with epic builds and emotional breakdowns",
            "Generate a tech house banger with punchy kicks and rolling bassline"
        ]
        
        for i, request in enumerate(test_requests, 1):
            print(f"\n🎵 Request {i}: {request}")
            
            try:
                analysis = await self.orchestrator.analyze_user_request(request)
                
                print(f"   🎨 Style: {analysis['style']}")
                print(f"   🎤 Artist Reference: {analysis['artist_reference']}")
                print(f"   ⚡ BPM: {analysis['bpm']}")
                print(f"   🎹 Key: {analysis['key']}")
                print(f"   😊 Mood: {analysis['mood']}")
                print(f"   ⏱️ Length: {analysis['length_minutes']} minutes")
                
            except Exception as e:
                logger.error(f"Error analyzing request: {e}")
    
    async def demo_creative_brief_generation(self):
        """Demonstrate creative brief generation"""
        print("\n" + "="*60)
        print("📋 CREATIVE BRIEF GENERATION DEMO")
        print("="*60)
        
        # Use a sample analysis
        sample_analysis = {
            "style": "afro_house",
            "artist_reference": "Black Coffee",
            "bpm": 122,
            "key": "Am", 
            "mood": "emotional and uplifting",
            "complexity": "professional",
            "length_minutes": 6.0,
            "specific_elements": ["organic percussion", "vocal chops", "warm bass"],
            "creative_direction": "Create an emotional journey with African influences"
        }
        
        print(f"🎨 Generating creative brief for: {sample_analysis['style']} track")
        
        try:
            brief = await self.orchestrator.create_creative_brief(sample_analysis)
            
            print(f"\n📊 CREATIVE BRIEF:")
            print(f"   🎵 Style: {brief.style}")
            print(f"   🎤 Artist Reference: {brief.artist_reference}")
            print(f"   ⚡ BPM: {brief.bpm}")
            print(f"   🎹 Key: {brief.key}")
            print(f"   😊 Mood: {brief.mood}")
            print(f"   ⏱️ Length: {brief.arrangement_length} minutes")
            print(f"   🎛️ Track Elements: {', '.join(brief.track_elements)}")
            print(f"   🎼 Chord Progression: {' - '.join(brief.harmonic_progression)}")
            
            print(f"\n🥁 RHYTHMIC PATTERNS:")
            for element, pattern in brief.rhythmic_pattern.items():
                print(f"   {element.title()}: {pattern}")
            
            print(f"\n🎨 SOUND PALETTE:")
            for sound_type, characteristics in brief.sound_palette.items():
                print(f"   {sound_type.title()}: {characteristics}")
                
        except Exception as e:
            logger.error(f"Error generating creative brief: {e}")
    
    async def demo_plugin_recommendations(self):
        """Demonstrate plugin recommendations"""
        print("\n" + "="*60)
        print("🎛️ PLUGIN RECOMMENDATIONS DEMO")
        print("="*60)
        
        test_cases = [
            ("bass", "afro_house"),
            ("lead", "keinemusik"),
            ("kick", "deep_house"),
            ("pad", "progressive_house")
        ]
        
        for sound_type, style in test_cases:
            print(f"\n🎵 Getting recommendation for: {sound_type} in {style}")
            
            try:
                recommendation = self.plugin_expert.get_plugin_recommendation(sound_type, style)
                
                print(f"   🎛️ Plugin: {recommendation['plugin']}")
                if 'preset' in recommendation:
                    print(f"   🎨 Preset: {recommendation['preset']}")
                if 'additional_effects' in recommendation:
                    print(f"   ⚡ Effects: {', '.join(recommendation['additional_effects'])}")
                print(f"   💡 Notes: {recommendation['notes']}")
                
            except Exception as e:
                logger.error(f"Error getting plugin recommendation: {e}")
    
    async def demo_arrangement_planning(self):
        """Demonstrate arrangement planning"""
        print("\n" + "="*60)
        print("🎼 ARRANGEMENT PLANNING DEMO")
        print("="*60)
        
        # Create a sample creative brief
        from music_intelligence.gemini_orchestrator import CreativeBrief
        
        sample_brief = CreativeBrief(
            style="afro_house",
            artist_reference="Black Coffee",
            bpm=122,
            key="Am",
            mood="emotional",
            arrangement_length=6.0,
            track_elements=["kick", "bass", "hi_hats", "percussion", "vocal_chops", "pad"],
            harmonic_progression=["Am", "F", "C", "G"],
            rhythmic_pattern={
                "kick": "four_on_floor_with_accents",
                "percussion": "african_polyrhythm"
            },
            sound_palette={
                "bass": "warm_melodic",
                "pad": "atmospheric"
            }
        )
        
        print(f"🎨 Creating arrangement plan for {sample_brief.style} track...")
        
        try:
            arrangement = await self.orchestrator.generate_arrangement_plan(sample_brief)
            
            print(f"\n📊 ARRANGEMENT PLAN:")
            print(f"   📏 Total Bars: {arrangement['total_bars']}")
            
            print(f"\n🎵 SECTIONS:")
            for section in arrangement['sections']:
                print(f"   {section['name'].title()}: Bars {section['start_bar']}-{section['end_bar']}")
                print(f"      Elements: {', '.join(section['active_elements'])}")
                print(f"      Energy: {section['energy_level']}/10")
                if 'description' in section:
                    print(f"      Description: {section['description']}")
                print()
            
            if 'arrangement_notes' in arrangement:
                print(f"💡 Notes: {arrangement['arrangement_notes']}")
                
        except Exception as e:
            logger.error(f"Error generating arrangement plan: {e}")
    
    async def demo_interactive_chat(self):
        """Demonstrate interactive chat with Gemini"""
        print("\n" + "="*60)
        print("💬 INTERACTIVE CHAT DEMO")
        print("="*60)
        
        print("🎵 Starting chat session with AI Music Producer...")
        print("💡 Try asking: 'How do I create a warm Afro House bassline?'")
        print("💡 Or: 'What Ableton plugins work best for deep house pads?'")
        print("💡 Type 'quit' to exit chat")
        
        try:
            self.orchestrator.start_chat_session()
            
            while True:
                user_input = input("\n🎤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Thanks for using AI Music Producer!")
                    break
                
                if not user_input:
                    continue
                
                print("🤔 AI Producer is thinking...")
                response = await self.orchestrator.chat(user_input)
                print(f"🎵 AI Producer: {response}")
                
        except KeyboardInterrupt:
            print("\n👋 Chat session ended.")
        except Exception as e:
            logger.error(f"Error in chat: {e}")
    
    async def run_full_demo(self):
        """Run the complete demo"""
        print("🎵 AI MUSIC PRODUCER DEMO")
        print("=" * 60)
        print("Welcome to the AI Music Producer powered by Google Gemini 2.5 Flash!")
        print("This demo showcases AI-powered music production capabilities.")
        
        try:
            # Run all demos
            await self.demo_style_analysis()
            await self.demo_user_request_analysis() 
            await self.demo_creative_brief_generation()
            await self.demo_plugin_recommendations()
            await self.demo_arrangement_planning()
            
            # Interactive chat
            print("\n" + "="*60)
            print("🎉 Demo completed! Want to try interactive chat?")
            response = input("Start chat session? (y/n): ").strip().lower()
            
            if response == 'y':
                await self.demo_interactive_chat()
            
        except Exception as e:
            logger.error(f"Demo error: {e}")
            print(f"❌ Demo encountered an error: {e}")
        
        print("\n🎵 Thanks for trying the AI Music Producer!")
        print("🚀 This is just the beginning - imagine the possibilities!")


async def main():
    """Main demo function"""
    demo = AIProducerDemo()
    await demo.run_full_demo()


if __name__ == "__main__":
    # Run the demo
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1) 