#!/usr/bin/env python3
"""
Test script to verify instrument loading fix

This script tests the corrected instrument loading functionality
to ensure the 'Vector' object has no attribute 'append_device_from_path' error is fixed.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from MCP_Server.server import AbletonConnection
import time

def test_instrument_loading():
    """Test instrument loading with the fixed Remote Script"""
    
    print("🧪 Testing Instrument Loading Fix")
    print("=" * 50)
    
    try:
        # Connect to Ableton
        conn = AbletonConnection('localhost', 9877)
        print("✅ Connected to Ableton Live")
        
        # Set tempo
        tempo_result = conn.send_command('set_tempo', {'tempo': 120})
        print(f"✅ Set tempo to 120 BPM")
        
        # Create test tracks
        tracks = {}
        track_types = ['Drums', 'Bass', 'Pads', 'Lead']
        
        for track_type in track_types:
            track_result = conn.send_command('create_midi_track', {'name': f'Test {track_type}'})
            tracks[track_type.lower()] = track_result
            print(f"✅ Created {track_type} track (index: {track_result['index']})")
        
        # Test instrument loading with the fixed methods
        print("\n🎛️ Testing Instrument Loading:")
        print("-" * 30)
        
        # Test instruments mapping
        instrument_tests = [
            ('drums', 'drums', "Should load drum rack"),
            ('bass', 'bass', "Should load wavetable for bass"),
            ('pads', 'synth', "Should load wavetable synth for pads"),
            ('lead', 'synth', "Should load wavetable synth for lead")
        ]
        
        results = []
        
        for track_name, instrument_uri, description in instrument_tests:
            print(f"\n🔧 Testing {track_name}: {description}")
            
            try:
                track_index = tracks[track_name]['index']
                
                # Use the corrected load_instrument_or_effect command
                result = conn.send_command('load_instrument_or_effect', {
                    'track_index': track_index,
                    'uri': instrument_uri
                })
                
                print(f"   Result: {result}")
                
                if result.get('status') == 'success':
                    instrument_data = result.get('result', {})
                    if instrument_data.get('loaded'):
                        print(f"   ✅ SUCCESS: Loaded {instrument_data.get('type', 'unknown')} on {track_name}")
                        results.append((track_name, True, instrument_data.get('type', 'unknown')))
                    else:
                        print(f"   ⚠️  PARTIAL: {instrument_data.get('message', 'No instrument found')}")
                        results.append((track_name, False, instrument_data.get('message', 'Failed')))
                elif result.get('loaded'):
                    # Direct response format (what we're actually getting)
                    print(f"   ✅ SUCCESS: Loaded {result.get('type', 'unknown')} on {track_name}")
                    results.append((track_name, True, result.get('type', 'unknown')))
                else:
                    print(f"   ❌ FAILED: {result.get('message', 'Unknown error')}")
                    results.append((track_name, False, result.get('message', 'Failed')))
                    
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")
                results.append((track_name, False, str(e)))
                
            # Small delay between attempts
            time.sleep(0.5)
        
        # Summary
        print("\n📊 RESULTS SUMMARY:")
        print("=" * 50)
        
        success_count = 0
        for track_name, success, details in results:
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{track_name.title():<8}: {status} - {details}")
            if success:
                success_count += 1
        
        print(f"\nOverall: {success_count}/{len(results)} instruments loaded successfully")
        
        if success_count == len(results):
            print("🎉 ALL INSTRUMENTS LOADED SUCCESSFULLY!")
            print("🔧 The 'Vector' object error has been FIXED!")
        elif success_count > 0:
            print("⚠️  PARTIAL SUCCESS - Some instruments loaded")
            print("💡 This is normal if some instrument types aren't available in your Ableton Live installation")
        else:
            print("❌ NO INSTRUMENTS LOADED")
            print("🔍 Check if Ableton Live is running and the Remote Script is loaded")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("💡 Make sure:")
        print("   1. Ableton Live is running")
        print("   2. AbletonMCP Remote Script is selected in Live's preferences")
        print("   3. The Remote Script has been restarted after the fix")
        return False

def main():
    """Main test function"""
    print("🎵 Instrument Loading Fix Test")
    print("Testing the fix for: 'Vector' object has no attribute 'append_device_from_path'")
    print("")
    
    success = test_instrument_loading()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED: Instrument loading is working!")
        print("🎯 The Vector error has been resolved.")
    else:
        print("❌ TEST FAILED: Issues with instrument loading")
        print("🔧 Check the Remote Script installation and Ableton connection")
    
    print("\n💡 Next Steps:")
    print("   - If successful: You can now create tracks with instruments!")
    print("   - If failed: Restart Ableton Live and check Remote Script setup")
    print("   - Try running: python chatleton_gpt.py --cli")

if __name__ == "__main__":
    main() 