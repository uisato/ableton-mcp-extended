#!/usr/bin/env python3
"""
Browser Content Diagnostic Tool

This script checks what's actually available in Ableton's browser
to understand why all instruments are loading as wavetable.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from MCP_Server.server import AbletonConnection
import time

def diagnose_browser():
    """Diagnose what's actually in the Ableton browser"""
    
    print("🔍 ABLETON BROWSER DIAGNOSTIC")
    print("=" * 50)
    
    try:
        # Connect to Ableton
        conn = AbletonConnection('localhost', 9877)
        print("✅ Connected to Ableton Live")
        
        # Get browser tree information
        print("\n📁 Getting browser structure...")
        
        try:
            result = conn.send_command('get_browser_tree', {'category_type': 'all'})
            print(f"Browser tree result: {result}")
            
            if result.get('status') == 'success':
                browser_data = result.get('result', {})
                categories = browser_data.get('categories', [])
                available_cats = browser_data.get('available_categories', [])
                
                print(f"\nAvailable browser categories: {available_cats}")
                print(f"Found {len(categories)} category structures")
                
                for i, category in enumerate(categories):
                    print(f"\nCategory {i+1}: {category.get('name', 'Unknown')}")
                    print(f"  - Is folder: {category.get('is_folder', False)}")
                    print(f"  - Is device: {category.get('is_device', False)}")
                    print(f"  - Is loadable: {category.get('is_loadable', False)}")
                    print(f"  - URI: {category.get('uri', 'None')}")
            else:
                print(f"❌ Failed to get browser tree: {result}")
                
        except Exception as e:
            print(f"❌ Error getting browser tree: {e}")
        
        # Try to get items at specific paths
        test_paths = [
            "instruments",
            "drums", 
            "sounds",
            "devices",
            "audio_effects",
            "midi_effects"
        ]
        
        print(f"\n🔍 Testing browser paths:")
        for path in test_paths:
            try:
                result = conn.send_command('get_browser_items_at_path', {'path': path})
                if result.get('status') == 'success':
                    items = result.get('result', {}).get('items', [])
                    print(f"  {path}: {len(items)} items found")
                    if items:
                        print(f"    First few: {[item.get('name', 'Unknown') for item in items[:3]]}")
                else:
                    print(f"  {path}: ❌ {result.get('message', 'Failed')}")
            except Exception as e:
                print(f"  {path}: ❌ Error: {e}")
        
        # Test actual instrument loading to see logs
        print(f"\n🎛️ Testing actual instrument loading (check Ableton Log.txt for details):")
        
        # Create a test track
        test_track = conn.send_command('create_midi_track', {'name': 'Diagnostic Test'})
        track_index = test_track.get('result', {}).get('index', 0)
        print(f"Created test track at index: {track_index}")
        
        # Try loading each instrument type
        test_instruments = ['drums', 'bass', 'synth']
        
        for instrument in test_instruments:
            print(f"\n🔧 Testing {instrument} loading...")
            try:
                result = conn.send_command('load_instrument_or_effect', {
                    'track_index': track_index,
                    'uri': instrument
                })
                
                if result.get('status') == 'success':
                    instrument_data = result.get('result', {})
                    print(f"  Result: {instrument_data}")
                    
                    if instrument_data.get('loaded'):
                        print(f"  ✅ Loaded: {instrument_data.get('type', 'unknown')}")
                    else:
                        print(f"  ⚠️ Not loaded: {instrument_data.get('message', 'Unknown issue')}")
                else:
                    print(f"  ❌ Failed: {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
                
            time.sleep(1)  # Small delay between tests
        
        print(f"\n📋 DIAGNOSTIC COMPLETE")
        print(f"Check the Ableton Live Log.txt file for detailed Remote Script logs")
        print(f"Location: ~/Library/Preferences/Ableton/Live */Log.txt")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("🔍 Ableton Browser & Instrument Loading Diagnostic")
    print("This tool will help identify why instruments are all loading as wavetable")
    print("")
    
    if not diagnose_browser():
        print("\n💡 Troubleshooting:")
        print("   1. Make sure Ableton Live is running")
        print("   2. Ensure AbletonMCP Remote Script is selected")
        print("   3. Restart Ableton Live if you made Remote Script changes")
    
    print("\n🔧 CRITICAL: If you made changes to the Remote Script:")
    print("   RESTART ABLETON LIVE to load the new logging code!")

if __name__ == "__main__":
    main() 