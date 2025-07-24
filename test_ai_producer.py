#!/usr/bin/env python3
"""
AI Music Producer Test Script

Quick test to verify your AI Music Producer installation is working correctly.

Usage:
    python test_ai_producer.py

Requirements:
    - Set GOOGLE_AI_API_KEY environment variable
    - Install requirements: pip install -r requirements.txt
"""

import os
import sys
import asyncio
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check API key
    if not os.getenv("GOOGLE_AI_API_KEY"):
        print("❌ GOOGLE_AI_API_KEY environment variable not set!")
        print("   Set it with: export GOOGLE_AI_API_KEY='your-api-key-here'")
        return False
    
    # Check Python packages
    required_packages = [
        ("google.generativeai", "google-generativeai"),
        ("music_intelligence", "local module")
    ]
    
    missing_packages = []
    for package, pip_name in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (install with: pip install {pip_name})")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n📦 Missing packages. Install with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True


async def test_basic_functionality():
    """Test basic AI Music Producer functionality"""
    print("\n🎵 Testing AI Music Producer functionality...")
    
    try:
        # Import after checking requirements
        from music_intelligence import GeminiOrchestrator, StyleAnalyzer, StockPluginExpert
        
        # Test 1: Initialize systems
        print("   🔧 Initializing AI systems...")
        orchestrator = GeminiOrchestrator()
        style_analyzer = StyleAnalyzer()
        plugin_expert = StockPluginExpert()
        print("   ✅ AI systems initialized")
        
        # Test 2: Style analysis
        print("   🎨 Testing style analysis...")
        style_chars = style_analyzer.analyze_artist_style("Black Coffee")
        print(f"   ✅ Style analysis: {style_chars.energy_curve}")
        
        # Test 3: Plugin recommendations
        print("   🎛️ Testing plugin recommendations...")
        recommendation = plugin_expert.get_plugin_recommendation("bass", "afro_house")
        print(f"   ✅ Plugin recommendation: {recommendation['plugin']}")
        
        # Test 4: User request analysis (quick test)
        print("   🎯 Testing user request analysis...")
        analysis = await orchestrator.analyze_user_request("Create a simple house track")
        print(f"   ✅ Request analysis: {analysis['style']} at {analysis['bpm']} BPM")
        
        print("\n🎉 All tests passed! Your AI Music Producer is ready to use.")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🚀 NEXT STEPS")
    print("="*60)
    
    print("\n1. 🎭 Try the full demo:")
    print("   python demo_ai_music_producer.py")
    
    print("\n2. 🎵 Test with your AI assistant:")
    print("   Add this to your mcp_config.json and ask:")
    print("   'Generate a complete Afro House track inspired by Black Coffee'")
    
    print("\n3. 💬 Interactive chat:")
    print("   Ask the AI Producer: 'How do I create warm Afro House bass?'")
    
    print("\n4. 🎛️ Explore available tools:")
    print("   - generate_complete_track")
    print("   - create_afro_house_track") 
    print("   - analyze_and_replicate_style")
    print("   - chat_with_ai_producer")
    
    print("\n🎵 Happy music making!")


async def main():
    """Main test function"""
    print("🎵 AI MUSIC PRODUCER - INSTALLATION TEST")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Test functionality
    success = await test_basic_functionality()
    
    if success:
        print_next_steps()
    else:
        print("\n❌ Tests failed. Please check your installation.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user.")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1) 