#!/usr/bin/env python3
"""
Simple test for generation detection and track creation
"""

import os
import sys
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_generation():
    """Test the generation detection and track creation"""
    
    # Add the project root to Python path
    sys.path.append('.')
    
    try:
        # Import the main application
        from chatleton_gpt import ChatletonGPT
        
        # Initialize
        app = ChatletonGPT()
        
        # Initialize AI systems
        await app.initialize_ai_systems()
        
        # Test generation detection
        test_message = "120 bpm chilled melodic house"
        
        print(f"Testing generation detection with: '{test_message}'")
        is_generation = await app._detect_generation_request(test_message)
        print(f"Generation detected: {is_generation}")
        
        if is_generation:
            print("✅ Generation request detected correctly!")
            
            # Test the full flow without Ableton connection
            response = await app.process_user_message(test_message)
            print(f"Response: {response.get('generation_complete', False)}")
            print(f"Actions: {len(response.get('actions', []))}")
            
        else:
            print("❌ Generation request NOT detected")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_generation()) 