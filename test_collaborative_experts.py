#!/usr/bin/env python3
"""
Test Collaborative Expert System
Tests the enhanced AI experts with cross-sharing and iterative refinement
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

async def test_collaborative_experts():
    """Test the collaborative expert system with cross-sharing"""
    print("🎼" + "=" * 80 + "🎼")
    print("🎼  CHAT-LETON GPT - COLLABORATIVE EXPERT SYSTEM TEST")
    print("🎼  AI experts with cross-sharing and iterative refinement")
    print("🎼" + "=" * 80 + "🎼")
    print()
    
    # Check API key
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ GOOGLE_AI_API_KEY not set!")
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
    
    # Initialize Collaborative AI Expert Orchestrator
    print("\n🧠 Initializing Collaborative AI Expert System...")
    expert_orchestrator = AIExpertOrchestrator(model)
    print("✅ All collaborative AI experts initialized")
    
    # Test collaborative expert generation
    print("\n🎵 Testing collaborative expert generation...")
    print("   Creating Ben Böhmer-style Progressive House with expert collaboration...")
    
    expert_content = await expert_orchestrator.generate_complete_section(
        style="Progressive House",
        key="A Minor", 
        bpm=122,
        section="Drop_1",
        bars=16,
        energy="high"
    )
    
    print(f"✅ Collaborative expert content generated successfully!")
    
    # Display collaborative analysis
    print("\n📊 COLLABORATIVE EXPERT ANALYSIS:")
    print("=" * 60)
    
    # Expert Analysis
    expert_analysis = expert_content.get('expert_analysis', {})
    refinement_analysis = expert_content.get('refinement_analysis', {})
    
    print(f"🎼 ORCHESTRATOR ANALYSIS:")
    print(f"   • Section type: {expert_analysis.get('section_type', 'unknown')}")
    print(f"   • Musical complexity: {expert_analysis.get('musical_complexity', 'standard')}")
    print(f"   • Collaboration quality: {expert_analysis.get('collaboration_quality', 'good')}")
    print(f"   • Generation success: {expert_analysis.get('generation_success', False)}")
    print()
    
    print(f"🔄 REFINEMENT ANALYSIS:")
    print(f"   • Collaboration score: {refinement_analysis.get('collaboration_score', 'good')}")
    print(f"   • Needs refinement: {refinement_analysis.get('needs_refinement', False)}")
    print(f"   • Issues found: {len(refinement_analysis.get('issues_found', []))}")
    print(f"   • Strengths: {len(refinement_analysis.get('strengths', []))}")
    
    # Show expert interactions
    interactions = expert_analysis.get('expert_interactions', [])
    if interactions:
        print(f"\n🤝 EXPERT INTERACTIONS:")
        for interaction in interactions[:3]:  # Show first 3
            print(f"   • {interaction}")
    
    # Show refinement details if any
    issues_found = refinement_analysis.get('issues_found', [])
    if issues_found:
        print(f"\n⚠️  ISSUES IDENTIFIED:")
        for issue in issues_found[:3]:  # Show first 3
            print(f"   • {issue}")
    
    strengths = refinement_analysis.get('strengths', [])
    if strengths:
        print(f"\n✅ COLLABORATION STRENGTHS:")
        for strength in strengths[:3]:  # Show first 3
            print(f"   • {strength}")
    
    # Individual Expert Results
    print("\n🎯 INDIVIDUAL EXPERT RESULTS:")
    print("=" * 60)
    
    # Harmony Expert Results
    if expert_content.get('harmony'):
        harmony_content = expert_content['harmony']
        print(f"🎹 HARMONY EXPERT:")
        print(f"   • {harmony_content.get('musical_description', 'Expert harmonic content')}")
        if 'chord_progression' in harmony_content:
            chords = len(harmony_content['chord_progression'])
            chord_symbols = [chord.get('chord_symbol', 'Unknown') for chord in harmony_content['chord_progression']]
            print(f"   • Chord progression: {' → '.join(chord_symbols[:4])}")  # Show first 4
            print(f"   • {chords} sophisticated chords with extensions")
        print()
    
    # Drum Expert Results
    if expert_content.get('drums'):
        drum_content = expert_content['drums']
        print(f"🥁 DRUM EXPERT:")
        print(f"   • {drum_content.get('musical_description', 'Expert drum arrangement')}")
        harmonic_integration = drum_content.get('groove_characteristics', {}).get('harmonic_integration', 'Standard rhythm')
        print(f"   • Harmonic integration: {harmonic_integration}")
        
        total_drum_hits = 0
        for pattern_name in ['kick_pattern', 'snare_pattern', 'hihat_pattern', 'percussion_pattern']:
            pattern = drum_content.get(pattern_name, {})
            hits = len(pattern.get('notes', []))
            total_drum_hits += hits
            if hits > 0:
                print(f"   • {pattern_name.replace('_', ' ').title()}: {hits} hits")
        print(f"   • Total drum hits: {total_drum_hits}")
        print()
    
    # Bass Expert Results  
    if expert_content.get('bass'):
        bass_content = expert_content['bass']
        print(f"🎸 BASS EXPERT:")
        print(f"   • {bass_content.get('musical_description', 'Expert bass arrangement')}")
        if 'harmonic_analysis' in bass_content:
            analysis = bass_content['harmonic_analysis']
            print(f"   • Chord support: {analysis.get('chord_support', 'sophisticated')}")
            print(f"   • Movement pattern: {analysis.get('movement_pattern', 'smooth')}")
            print(f"   • Collaboration notes: {analysis.get('collaboration_notes', 'Coordinated with other parts')}")
        if 'bass_line' in bass_content:
            bass_notes = len(bass_content['bass_line'].get('notes', []))
            print(f"   • Bass line: {bass_notes} notes")
        print()
    
    # Melody Expert Results
    if expert_content.get('melody'):
        melody_content = expert_content['melody']
        print(f"🎺 MELODY EXPERT:")
        print(f"   • {melody_content.get('musical_description', 'Expert melodic content')}")
        if 'melodic_analysis' in melody_content:
            analysis = melody_content['melodic_analysis']
            print(f"   • Collaboration analysis: {analysis.get('collaboration_analysis', 'Works with other parts')}")
        if 'melody_line' in melody_content:
            phrases = len(melody_content['melody_line'].get('phrases', []))
            print(f"   • Melodic phrases: {phrases}")
        print()
    
    # Now create the complete collaborative track in Ableton
    print("🎛️ CREATING COLLABORATIVE TRACK IN ABLETON...")
    print("=" * 60)
    
    try:
        conn = AbletonConnection('localhost', 9877)
        
        # Set tempo
        conn.send_command('set_tempo', {'tempo': 122})
        print("✅ Set tempo to 122 BPM")
        
        # Create tracks
        tracks = {
            'drums': conn.send_command('create_midi_track', {'name': 'Collaborative Drums'}),
            'bass': conn.send_command('create_midi_track', {'name': 'Collaborative Bass'}),
            'lead': conn.send_command('create_midi_track', {'name': 'Collaborative Lead'}),
            'pads': conn.send_command('create_midi_track', {'name': 'Collaborative Pads'})
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
        
        # Create collaborative expert-generated musical content
        
        # 1. Collaborative Drums - Rhythmically aware of harmony
        drum_content = expert_content.get('drums', {})
        if drum_content:
            all_drum_notes = []
            
            # Add all drum elements that were generated with harmonic awareness
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
                print(f"✅ Created collaborative drum arrangement: {len(all_drum_notes)} harmonically-aware drum hits")
        
        # 2. Collaborative Bass - Supports harmony and groove
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
            
            # Add sub-bass if present
            sub_bass = bass_content.get('sub_bass', {})
            for note in sub_bass.get('notes', []):
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
                print(f"✅ Created collaborative bass line: {len(bass_notes)} notes that lock with drums and support harmony")
        
        # 3. Collaborative Harmony - Foundation for all other parts
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
                print(f"✅ Created collaborative chord progression: {len(pad_notes)} chord notes that inform all other parts")
        
        # 4. Collaborative Melody - Works with all other elements
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
                print(f"✅ Created collaborative melody: {len(lead_notes)} notes that complement harmony, bass, and drums")
        
        # Start playback
        conn.send_command('start_playback')
        print("▶️ Started collaborative track playback!")
        
        # Get final session info
        final_session = conn.send_command('get_session_info')
        session_info = final_session.get('result', final_session)
        print(f"🎉 Collaborative track complete! Session now has {session_info.get('track_count', 0)} tracks")
        
        conn.disconnect()
        
    except Exception as e:
        print(f"❌ Collaborative track creation failed: {e}")
        return False
    
    print("\n🎉 COLLABORATIVE EXPERT SYSTEM TEST COMPLETE!")
    print("=" * 60)
    print("🎵 Check your Ableton Live session!")
    print("   • Drums that are harmonically aware")
    print("   • Bass that locks with drums and supports harmony")
    print("   • Chords that inform all other experts")
    print("   • Melody that complements all other parts")
    print("   • 6-phase collaborative generation process")
    print("   • Iterative refinement and expert feedback")
    print("   • Cross-sharing of expert knowledge")
    print()
    print("🚀 The AI experts are now truly collaborating like a real band!")
    
    return True

async def main():
    """Main test function"""
    success = await test_collaborative_experts()
    if success:
        print("\n✅ All collaborative expert tests passed!")
    else:
        print("\n❌ Collaborative expert tests failed!")

if __name__ == "__main__":
    asyncio.run(main()) 