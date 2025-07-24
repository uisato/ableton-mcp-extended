#!/usr/bin/env python3
"""
Simple Chat-leton GPT Test - Direct MCP Integration
Uses the proven working MCP pattern to create tracks in Ableton Live
"""

import sys
import json
import os
from pathlib import Path

# Add MCP server to path
sys.path.append('MCP_Server')

try:
    from server import AbletonConnection
    import google.generativeai as genai
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Run: pip install google-generativeai")
    sys.exit(1)

def test_ableton_connection():
    """Test direct Ableton connection"""
    try:
        conn = AbletonConnection('localhost', 9877)
        response = conn.send_command('get_session_info')
        session = response.get('result', response)  # Handle different response formats
        print(f"✅ Ableton connected - {session['track_count']} tracks at {session['tempo']} BPM")
        conn.disconnect()
        return True
    except Exception as e:
        print(f"❌ Ableton connection failed: {e}")
        return False

def create_simple_track(style="Afro House", bpm=122):
    """Create a simple track using working MCP pattern"""
    try:
        conn = AbletonConnection('localhost', 9877)
        
        print(f"🎵 Creating {style} track at {bpm} BPM...")
        
        # 1. Create tracks
        kick_track = conn.send_command('create_midi_track', {'name': f'{style} Kick'})
        bass_track = conn.send_command('create_midi_track', {'name': f'{style} Bass'})
        pad_track = conn.send_command('create_midi_track', {'name': f'{style} Pads'})
        
        print(f"✅ Created tracks: {kick_track['index']}, {bass_track['index']}, {pad_track['index']}")
        
        # 2. Load instruments on tracks
        print("🎛️ Loading instruments...")
        
        # Load Impulse drum rack on kick track
        try:
            drum_result = conn.send_command('load_instrument_or_effect', {
                'track_index': kick_track['index'],
                'uri': 'drums'
            })
            print(f"✅ Loaded drum rack on kick track")
        except Exception as e:
            print(f"⚠️ Could not load drum rack: {e}")
        
        # Load bass instrument
        try:
            bass_result = conn.send_command('load_instrument_or_effect', {
                'track_index': bass_track['index'], 
                'uri': 'bass'
            })
            print(f"✅ Loaded bass instrument")
        except Exception as e:
            print(f"⚠️ Could not load bass: {e}")
            
        # Load pad/synth instrument
        try:
            pad_result = conn.send_command('load_instrument_or_effect', {
                'track_index': pad_track['index'],
                'uri': 'synth'
            })
            print(f"✅ Loaded Wavetable synth for pads")
        except Exception as e:
            print(f"⚠️ Could not load Wavetable: {e}")
        
        # 3. Set tempo
        tempo_result = conn.send_command('set_tempo', {'tempo': bpm})
        print(f"✅ Set tempo to {bpm} BPM")
        
        # 4. Create simple MIDI patterns
        # Kick pattern - 4 on the floor
        kick_notes = [
            {"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 100},
            {"pitch": 36, "start_time": 1.0, "duration": 0.25, "velocity": 100},
            {"pitch": 36, "start_time": 2.0, "duration": 0.25, "velocity": 100},
            {"pitch": 36, "start_time": 3.0, "duration": 0.25, "velocity": 100}
        ]
        
        kick_clip = conn.send_command('create_clip', {
            'track_index': kick_track['index'],
            'clip_index': 0,
            'length': 4.0
        })
        
        conn.send_command('add_notes_to_clip', {
            'track_index': kick_track['index'],
            'clip_index': 0,
            'notes': kick_notes
        })
        
        print(f"✅ Added kick pattern")
        
        # Bass pattern - simple root notes
        bass_notes = [
            {"pitch": 40, "start_time": 0.0, "duration": 1.0, "velocity": 80},
            {"pitch": 38, "start_time": 1.0, "duration": 1.0, "velocity": 80},
            {"pitch": 43, "start_time": 2.0, "duration": 1.0, "velocity": 80},
            {"pitch": 41, "start_time": 3.0, "duration": 1.0, "velocity": 80}
        ]
        
        bass_clip = conn.send_command('create_clip', {
            'track_index': bass_track['index'],
            'clip_index': 0,
            'length': 4.0
        })
        
        conn.send_command('add_notes_to_clip', {
            'track_index': bass_track['index'],
            'clip_index': 0,
            'notes': bass_notes
        })
        
        print(f"✅ Added bass pattern")
        
        # Pad pattern - simple chords
        pad_notes = [
            # Am chord
            {"pitch": 57, "start_time": 0.0, "duration": 2.0, "velocity": 60},  # A
            {"pitch": 60, "start_time": 0.0, "duration": 2.0, "velocity": 60},  # C
            {"pitch": 64, "start_time": 0.0, "duration": 2.0, "velocity": 60},  # E
            # F chord  
            {"pitch": 53, "start_time": 2.0, "duration": 2.0, "velocity": 60},  # F
            {"pitch": 57, "start_time": 2.0, "duration": 2.0, "velocity": 60},  # A
            {"pitch": 60, "start_time": 2.0, "duration": 2.0, "velocity": 60},  # C
        ]
        
        pad_clip = conn.send_command('create_clip', {
            'track_index': pad_track['index'],
            'clip_index': 0,
            'length': 4.0
        })
        
        conn.send_command('add_notes_to_clip', {
            'track_index': pad_track['index'],
            'clip_index': 0,
            'notes': pad_notes
        })
        
        print(f"✅ Added pad chord progression")
        
        # 5. Fire clips to start playing
        print("🎵 Starting playback...")
        conn.send_command('fire_clip', {'track_index': kick_track['index'], 'clip_index': 0})
        conn.send_command('fire_clip', {'track_index': bass_track['index'], 'clip_index': 0})
        conn.send_command('fire_clip', {'track_index': pad_track['index'], 'clip_index': 0})
        
        conn.send_command('start_playback')
        
        # Get final session info
        final_response = conn.send_command('get_session_info')
        final_session = final_response.get('result', final_response)
        print(f"🎉 SUCCESS! Track created with {final_session['track_count']} tracks")
        
        conn.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Track creation failed: {e}")
        return False

def main():
    """Main test function"""
    print("🎵 Simple Chat-leton GPT Test - WITH INSTRUMENTS!")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("⚠️  GOOGLE_AI_API_KEY not set (AI features disabled)")
    else:
        print("✅ Google AI API key found")
    
    # Test Ableton connection
    print("\n🔍 Testing Ableton connection...")
    if not test_ableton_connection():
        print("💡 Make sure Ableton Live is running with AbletonMCP Remote Script")
        return
    
    # Create simple track
    print("\n🎵 Testing track creation with instruments...")
    if create_simple_track():
        print("\n🎉 SUCCESS! Check your Ableton Live session!")
        print("   - New tracks with INSTRUMENTS should be created")
        print("   - Kick, bass, and pad patterns should be playing")
        print("   - Tempo should be set to 122 BPM")
        print("   - Music should be playing automatically!")
    else:
        print("\n❌ Track creation failed")

if __name__ == "__main__":
    main() 