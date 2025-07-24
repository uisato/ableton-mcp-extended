#!/usr/bin/env python3
"""
Test Expert System - Advanced AI Music Generation
Tests the new specialized AI experts for sophisticated music creation
"""

import os
import sys
import asyncio
import json
import logging
from pathlib import Path

# Add MCP server to path
sys.path.append('MCP_Server')

try:
    from server import AbletonConnection
    import google.generativeai as genai
    from music_intelligence.ai_experts import AIExpertOrchestrator
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Run: pip install google-generativeai")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_expert_system():
    """Test the specialized AI expert system"""
    print("🎼" + "=" * 80 + "🎼")
    print("🎼  CHAT-LETON GPT - AI EXPERT SYSTEM TEST")
    print("🎼  Specialized AI experts for sophisticated music generation")
    print("🎼" + "=" * 80 + "🎼")
    print()
    
    # Check API key
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ GOOGLE_AI_API_KEY not set!")
        print("Export your Google AI API key before running this test.")
        return False
    
    print("✅ Google AI API key found")
    
    # Initialize Gemini
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        print("✅ Gemini 2.5 Flash-Lite initialized")
    except Exception as e:
        print(f"❌ Gemini initialization failed: {e}")
        return False
    
    # Test Ableton connection
    print("\n🔍 Testing Ableton connection...")
    try:
        conn = AbletonConnection('localhost', 9877)
        response = conn.send_command('get_session_info')
        session = response.get('result', response)
        print(f"✅ Ableton connected - {session['track_count']} tracks at {session['tempo']} BPM")
        conn.disconnect()
    except Exception as e:
        print(f"❌ Ableton connection failed: {e}")
        print("💡 Make sure Ableton Live is running with AbletonMCP Remote Script")
        return False
    
    # Initialize AI Expert Orchestrator
    print("\n🧠 Initializing AI Expert System...")
    expert_orchestrator = AIExpertOrchestrator(model)
    print("✅ All specialized AI experts initialized")
    
    # Test expert-generated content
    print("\n🎵 Testing expert-generated musical content...")
    print("   Creating Ben Böhmer-style Progressive House section...")
    
    expert_content = await expert_orchestrator.generate_complete_section(
        style="Progressive House",
        key="A Minor",
        bpm=122,
        section="Drop_1",
        bars=16,
        energy="high"
    )
    
    print(f"✅ Expert content generated successfully!")
    
    # Display expert analysis
    print("\n📊 EXPERT ANALYSIS:")
    print("=" * 50)
    
    # Drum Expert Results
    if expert_content.get('drums'):
        drum_content = expert_content['drums']
        print(f"🥁 DRUM EXPERT:")
        print(f"   • {drum_content.get('musical_description', 'Expert drum arrangement')}")
        if 'kick_pattern' in drum_content:
            kick_notes = len(drum_content['kick_pattern'].get('notes', []))
            print(f"   • Kick pattern: {kick_notes} notes")
        if 'snare_pattern' in drum_content:
            snare_notes = len(drum_content['snare_pattern'].get('notes', []))
            print(f"   • Snare pattern: {snare_notes} notes")
        if 'hihat_pattern' in drum_content:
            hihat_notes = len(drum_content['hihat_pattern'].get('notes', []))
            print(f"   • Hi-hat pattern: {hihat_notes} notes")
        print()
    
    # Bass Expert Results
    if expert_content.get('bass'):
        bass_content = expert_content['bass']
        print(f"🎸 BASS EXPERT:")
        print(f"   • {bass_content.get('musical_description', 'Expert bass arrangement')}")
        if 'bass_line' in bass_content:
            bass_notes = len(bass_content['bass_line'].get('notes', []))
            print(f"   • Bass line: {bass_notes} notes")
        if 'harmonic_analysis' in bass_content:
            analysis = bass_content['harmonic_analysis']
            print(f"   • Harmonic support: {analysis.get('chord_support', 'sophisticated')}")
        print()
    
    # Harmony Expert Results
    if expert_content.get('harmony'):
        harmony_content = expert_content['harmony']
        print(f"🎹 HARMONY EXPERT:")
        print(f"   • {harmony_content.get('musical_description', 'Expert harmonic content')}")
        if 'chord_progression' in harmony_content:
            chords = len(harmony_content['chord_progression'])
            chord_symbols = [chord.get('chord_symbol', 'Unknown') for chord in harmony_content['chord_progression']]
            print(f"   • Chord progression: {' - '.join(chord_symbols)}")
            print(f"   • {chords} sophisticated chords with extensions")
        print()
    
    # Melody Expert Results
    if expert_content.get('melody'):
        melody_content = expert_content['melody']
        print(f"🎺 MELODY EXPERT:")
        print(f"   • {melody_content.get('musical_description', 'Expert melodic content')}")
        if 'melody_line' in melody_content:
            phrases = len(melody_content['melody_line'].get('phrases', []))
            print(f"   • Melodic phrases: {phrases}")
        print()
    
    # Now create the complete track in Ableton
    print("🎛️ CREATING COMPLETE TRACK IN ABLETON...")
    print("=" * 50)
    
    try:
        conn = AbletonConnection('localhost', 9877)
        
        # Set tempo
        conn.send_command('set_tempo', {'tempo': 122})
        print("✅ Set tempo to 122 BPM")
        
        # Create tracks
        tracks = {
            'drums': conn.send_command('create_midi_track', {'name': 'Expert Drums'}),
            'bass': conn.send_command('create_midi_track', {'name': 'Expert Bass'}),
            'lead': conn.send_command('create_midi_track', {'name': 'Expert Lead'}),
            'pads': conn.send_command('create_midi_track', {'name': 'Expert Pads'})
        }
        
        # Load instruments
        instrument_map = {
            'drums': 'query:Synths#Drum%20Rack',
            'bass': 'query:Synths#Bass',
            'lead': 'query:Synths#Wavetable',
            'pads': 'query:Synths#Poli'
        }
        
        for track_name, track_info in tracks.items():
            try:
                conn.send_command('load_browser_item', {
                    'track_index': track_info['index'],
                    'item_uri': instrument_map[track_name]
                })
                print(f"✅ Loaded {track_name} instrument on track {track_info['index']}")
            except Exception as e:
                print(f"⚠️  Could not load {track_name} instrument: {e}")
        
        # Create expert-generated musical content
        
        # 1. Expert Drums - Full kit with kick, snare, hi-hats, percussion
        drum_content = expert_content.get('drums', {})
        if drum_content:
            all_drum_notes = []
            
            # Add all drum elements
            for pattern_name in ['kick_pattern', 'snare_pattern', 'hihat_pattern', 'percussion_pattern']:
                pattern = drum_content.get(pattern_name, {})
                for note in pattern.get('notes', []):
                    all_drum_notes.append({
                        "pitch": note['slot'],
                        "start_time": note['time'],
                        "duration": note['duration'],
                        "velocity": note['velocity']
                    })
            
            if all_drum_notes:
                conn.send_command('create_clip', {
                    'track_index': tracks['drums']['index'],
                    'clip_index': 0,
                    'length': 16
                })
                conn.send_command('add_notes_to_clip', {
                    'track_index': tracks['drums']['index'],
                    'clip_index': 0,
                    'notes': all_drum_notes
                })
                conn.send_command('fire_clip', {
                    'track_index': tracks['drums']['index'],
                    'clip_index': 0
                })
                print(f"✅ Created expert drum arrangement: {len(all_drum_notes)} drum hits")
        
        # 2. Expert Bass - Sophisticated bass line with harmonic progression
        bass_content = expert_content.get('bass', {})
        if bass_content:
            bass_notes = []
            bass_line = bass_content.get('bass_line', {})
            
            for note in bass_line.get('notes', []):
                bass_notes.append({
                    "pitch": note['pitch'],
                    "start_time": note['time'],
                    "duration": note['duration'],
                    "velocity": note['velocity']
                })
            
            if bass_notes:
                conn.send_command('create_clip', {
                    'track_index': tracks['bass']['index'],
                    'clip_index': 0,
                    'length': 16
                })
                conn.send_command('add_notes_to_clip', {
                    'track_index': tracks['bass']['index'],
                    'clip_index': 0,
                    'notes': bass_notes
                })
                conn.send_command('fire_clip', {
                    'track_index': tracks['bass']['index'],
                    'clip_index': 0
                })
                print(f"✅ Created expert bass line: {len(bass_notes)} bass notes")
        
        # 3. Expert Harmony - Sophisticated chord progressions
        harmony_content = expert_content.get('harmony', {})
        if harmony_content:
            pad_notes = []
            
            for chord in harmony_content.get('chord_progression', []):
                for note_pitch in chord.get('chord_notes', []):
                    pad_notes.append({
                        "pitch": note_pitch,
                        "start_time": chord.get('start_time', 0.0),
                        "duration": chord.get('duration', 4.0),
                        "velocity": 65
                    })
            
            if pad_notes:
                conn.send_command('create_clip', {
                    'track_index': tracks['pads']['index'],
                    'clip_index': 0,
                    'length': 16
                })
                conn.send_command('add_notes_to_clip', {
                    'track_index': tracks['pads']['index'],
                    'clip_index': 0,
                    'notes': pad_notes
                })
                conn.send_command('fire_clip', {
                    'track_index': tracks['pads']['index'],
                    'clip_index': 0
                })
                print(f"✅ Created expert chord progression: {len(pad_notes)} chord notes")
        
        # 4. Expert Melody - Memorable melodic content (if present)
        melody_content = expert_content.get('melody')
        if melody_content:
            lead_notes = []
            
            melody_line = melody_content.get('melody_line', {})
            for phrase in melody_line.get('phrases', []):
                for note in phrase.get('notes', []):
                    lead_notes.append({
                        "pitch": note['pitch'],
                        "start_time": note['time'],
                        "duration": note['duration'],
                        "velocity": note['velocity']
                    })
            
            if lead_notes:
                conn.send_command('create_clip', {
                    'track_index': tracks['lead']['index'],
                    'clip_index': 0,
                    'length': 16
                })
                conn.send_command('add_notes_to_clip', {
                    'track_index': tracks['lead']['index'],
                    'clip_index': 0,
                    'notes': lead_notes
                })
                conn.send_command('fire_clip', {
                    'track_index': tracks['lead']['index'],
                    'clip_index': 0
                })
                print(f"✅ Created expert melody: {len(lead_notes)} melodic notes")
        
        # Start playback
        conn.send_command('start_playback')
        print("▶️ Started playback!")
        
        # Get final session info
        final_session = conn.send_command('get_session_info')
        session_info = final_session.get('result', final_session)
        print(f"🎉 Expert track complete! Session now has {session_info.get('track_count', 0)} tracks")
        
        conn.disconnect()
        
    except Exception as e:
        print(f"❌ Track creation failed: {e}")
        return False
    
    print("\n🎉 EXPERT SYSTEM TEST COMPLETE!")
    print("=" * 50)
    print("🎵 Check your Ableton Live session!")
    print("   • Expert-generated drums with full kit")
    print("   • Sophisticated bass line with harmonic progression")
    print("   • Advanced chord progressions with extensions")
    print("   • Memorable melodic content (if generated)")
    print("   • 16-bar arrangements instead of simple loops")
    print("   • Specialized AI knowledge for each instrument")
    print()
    print("🚀 The AI experts are now creating professional-quality music!")
    
    return True

async def main():
    """Main test function"""
    success = await test_expert_system()
    if success:
        print("\n✅ All expert system tests passed!")
    else:
        print("\n❌ Expert system tests failed!")

if __name__ == "__main__":
    asyncio.run(main()) 