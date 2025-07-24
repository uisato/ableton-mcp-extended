#!/usr/bin/env python3
"""
Test AI Expert JSON parsing
"""

import os
import sys
import asyncio
import logging
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_ai_expert():
    """Test the AI expert system directly"""
    
    sys.path.append('.')
    
    try:
        from music_intelligence.gemini_orchestrator import GeminiOrchestrator
        from music_intelligence.ai_experts import DrumExpert
        
        # Initialize
        orchestrator = GeminiOrchestrator()
        drum_expert = DrumExpert(orchestrator.model)
        
        # Test simple context
        context = {
            'style': 'House',
            'bpm': 120,
            'section': 'main',
            'bars': 8,
            'energy': 'medium'
        }
        
        print("Testing DrumExpert with simple context...")
        
        result = await drum_expert.generate_content(
            "Create an 8-bar drum pattern for house music",
            context
        )
        
        print(f"Result type: {type(result)}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict) and 'kick_pattern' in result:
            print("✅ DrumExpert returned valid structure!")
            print(f"Kick pattern notes: {len(result['kick_pattern'].get('notes', []))}")
        else:
            print("❌ DrumExpert returned invalid structure")
            print(f"Full result: {result}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_expert()) 