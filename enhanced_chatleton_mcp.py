#!/usr/bin/env python3
"""
Enhanced Chat-leton MCP Server
Combines proven MCP communication with Google Gemini 2.5 Flash intelligence
"""

import sys
import json
import os
import logging
import asyncio
from typing import Dict, List, Any, Optional
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedChatletonMCP:
    """Enhanced Chat-leton MCP Server with Gemini AI integration"""
    
    def __init__(self, host: str = "localhost", port: int = 9877):
        self.host = host
        self.port = port
        self.ableton_conn = None
        self.gemini_model = None
        self._setup_gemini()
    
    def _setup_gemini(self):
        """Initialize Google Gemini 2.5 Flash"""
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        if not api_key:
            logger.warning("⚠️ GOOGLE_AI_API_KEY not set - AI features disabled")
            return
        
        try:
            genai.configure(api_key=api_key)
            
            # Use the latest Gemini 2.5 Flash-Lite model for cost efficiency
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 4096,
                "response_mime_type": "text/plain",
            }
            
            self.gemini_model = genai.GenerativeModel(
                model_name="gemini-2.5-flash-lite",
                generation_config=generation_config,
                system_instruction="""You are Chat-leton GPT, an expert AI music producer specialized in creating complete tracks in Ableton Live.
                
Your expertise includes:
- Deep understanding of musical styles (Afro House, Deep House, Progressive House, Techno, etc.)
- Professional arrangement and song structure
- Sound design using Ableton Live stock plugins
- MIDI programming and rhythm patterns
- Harmonic progressions and chord voicings

When generating tracks, provide specific, actionable instructions that can be implemented in Ableton Live using only stock plugins and samples."""
            )
            
            logger.info("✅ Gemini 2.5 Flash-Lite initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
            self.gemini_model = None
    
    def connect_ableton(self) -> bool:
        """Connect to Ableton Live via MCP"""
        try:
            self.ableton_conn = AbletonConnection(self.host, self.port)
            response = self.ableton_conn.send_command('get_session_info')
            session = response.get('result', response)
            logger.info(f"✅ Connected to Ableton - {session['track_count']} tracks at {session['tempo']} BPM")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Ableton: {e}")
            return False
    
    def disconnect_ableton(self):
        """Disconnect from Ableton"""
        if self.ableton_conn:
            try:
                self.ableton_conn.disconnect()
                logger.info("✅ Disconnected from Ableton")
            except Exception as e:
                logger.error(f"❌ Error disconnecting: {e}")
            finally:
                self.ableton_conn = None
    
    def load_drum_kit_into_rack(self, track_index: int, drum_samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Load specific drum samples into drum rack slots"""
        try:
            # First load a drum rack
            drum_result = self.ableton_conn.send_command('load_browser_item', {
                'track_index': track_index,
                'item_uri': 'query:Drums#Drum Rack'
            })
            
            logger.info(f"✅ Loaded Drum Rack on track {track_index}")
            
            # TODO: When MCP server supports it, load specific samples into slots
            # For now, the drum rack is loaded and ready for manual sample loading
            # Future enhancement: implement slot-specific sample loading
            
            slot_info = []
            for i, sample in enumerate(drum_samples[:16]):  # Drum rack has 16 slots
                slot_info.append({
                    'slot': i,
                    'sample_name': sample.get('name', f'Sample_{i}'),
                    'note': sample.get('note', 36 + i),  # C1 = 36, standard drum mapping
                    'description': sample.get('description', 'Drum sample')
                })
            
            return {
                'status': 'success',
                'drum_rack_loaded': True,
                'track_index': track_index,
                'available_slots': slot_info,
                'message': 'Drum rack loaded. Samples can be manually dragged to slots.'
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to load drum kit: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def create_intelligent_track(self, style: str, user_request: str) -> Dict[str, Any]:
        """Use Gemini AI to create an intelligent track based on style and user request"""
        if not self.gemini_model:
            return {'status': 'error', 'message': 'Gemini AI not available'}
        
        if not self.ableton_conn:
            if not self.connect_ableton():
                return {'status': 'error', 'message': 'Cannot connect to Ableton Live'}
        
        try:
            # Create AI prompt for track generation
            prompt = f"""Create a complete {style} track based on this request: "{user_request}"

Please provide a detailed production plan including:

1. TRACK STRUCTURE:
   - Track list with instruments needed
   - Arrangement timeline (intro, buildup, drop, breakdown, outro)
   - BPM and key signature

2. DRUM PROGRAMMING:
   - Kick pattern (specify timing and velocity)
   - Hi-hat patterns 
   - Percussion elements
   - Specific drum samples to use

3. BASS & LEAD PROGRAMMING:
   - Bassline pattern and rhythm
   - Lead synth patterns
   - Chord progressions

4. SOUND DESIGN:
   - Ableton Live stock plugins to use
   - Specific preset recommendations
   - Effect chain suggestions

5. MIDI PATTERNS:
   - Specific note sequences for each instrument
   - Rhythm patterns in musical notation
   - Velocity and timing details

Format your response as actionable production steps that can be implemented in Ableton Live."""
            
            # Get AI analysis
            ai_response = self.gemini_model.generate_content(prompt)
            ai_plan = ai_response.text
            
            logger.info(f"🧠 Generated AI production plan for {style}")
            
            # Now implement the basic track structure using our working MCP commands
            actions_taken = []
            
            # 1. Set tempo and key (extract from AI response or use style defaults)
            style_bpm = self._get_style_bpm(style)
            tempo_result = self.ableton_conn.send_command('set_tempo', {'tempo': style_bpm})
            actions_taken.append(f"Set tempo to {style_bpm} BPM")
            
            # 2. Create tracks for the style
            track_names = self._get_style_tracks(style)
            created_tracks = []
            
            for track_name in track_names:
                track_result = self.ableton_conn.send_command('create_midi_track', {'name': track_name})
                created_tracks.append(track_result)
                actions_taken.append(f"Created {track_name} track")
            
            # 3. Load instruments based on style
            for i, track in enumerate(created_tracks):
                track_index = track['index']
                instrument = self._get_style_instrument(style, i)
                
                if instrument:
                    try:
                        if 'Drum' in track_names[i]:
                            # Load drum rack with intelligent samples
                            drum_samples = self._get_style_drum_samples(style)
                            drum_result = self.load_drum_kit_into_rack(track_index, drum_samples)
                            actions_taken.append(f"Loaded drum kit for {style}")
                        else:
                            # Load regular instrument
                            inst_result = self.ableton_conn.send_command('load_browser_item', {
                                'track_index': track_index,
                                'item_uri': instrument
                            })
                            actions_taken.append(f"Loaded {instrument.split('#')[-1]} on {track_names[i]}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not load instrument for {track_names[i]}: {e}")
            
            # 4. Create basic MIDI patterns for the style
            patterns_created = self._create_style_patterns(style, created_tracks, track_names)
            actions_taken.extend(patterns_created)
            
            # 5. Start playback
            self.ableton_conn.send_command('start_playback')
            actions_taken.append("Started playback")
            
            return {
                'status': 'success',
                'style': style,
                'ai_plan': ai_plan,
                'actions_taken': actions_taken,
                'created_tracks': len(created_tracks),
                'bpm': style_bpm,
                'message': f'Successfully created {style} track with AI guidance!'
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create intelligent track: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _get_style_bpm(self, style: str) -> int:
        """Get appropriate BPM for musical style"""
        style_bpms = {
            'Afro House': 122,
            'Deep House': 124,
            'Progressive House': 128,
            'Techno': 130,
            'Tropical House': 120,
            'Tech House': 126
        }
        return style_bpms.get(style, 124)
    
    def _get_style_tracks(self, style: str) -> List[str]:
        """Get track list for musical style"""
        if 'House' in style or 'Techno' in style:
            return [
                f"{style} Kick",
                f"{style} Bass", 
                f"{style} Lead",
                f"{style} Pads",
                f"{style} Percussion"
            ]
        else:
            return [
                f"{style} Drums",
                f"{style} Bass",
                f"{style} Lead",
                f"{style} Harmony"
            ]
    
    def _get_style_instrument(self, style: str, track_index: int) -> Optional[str]:
        """Get appropriate instrument URI for style and track"""
        instruments = {
            0: 'query:Synths#Drum%20Rack',  # Drums/Kick (URL encoded)
            1: 'query:Synths#Bass',          # Bass ✅ Working
            2: 'query:Synths#Wavetable',     # Lead (Wavetable for modern sounds)
            3: 'query:Synths#Poli',          # Pads/Harmony (Poli for rich pads)
            4: 'query:Synths#Drum%20Rack'    # Percussion (URL encoded)
        }
        return instruments.get(track_index)
    
    def _get_style_drum_samples(self, style: str) -> List[Dict[str, Any]]:
        """Get drum samples appropriate for the style"""
        if 'Afro' in style:
            return [
                {'name': 'Afro Kick', 'note': 36, 'description': 'Deep sub kick'},
                {'name': 'Afro Snare', 'note': 38, 'description': 'Crisp snare'},
                {'name': 'Closed Hat', 'note': 42, 'description': 'Tight hi-hat'},
                {'name': 'Open Hat', 'note': 46, 'description': 'Open hi-hat'},
                {'name': 'Conga High', 'note': 48, 'description': 'High conga'},
                {'name': 'Conga Low', 'note': 50, 'description': 'Low conga'},
                {'name': 'Shaker', 'note': 52, 'description': 'Percussion shaker'},
                {'name': 'Clap', 'note': 54, 'description': 'Hand clap'}
            ]
        elif 'Deep' in style:
            return [
                {'name': 'Deep Kick', 'note': 36, 'description': 'Deep house kick'},
                {'name': 'Snare', 'note': 38, 'description': 'Classic snare'},
                {'name': 'Hi-Hat', 'note': 42, 'description': 'Clean hi-hat'},
                {'name': 'Ride', 'note': 44, 'description': 'Ride cymbal'},
                {'name': 'Rim', 'note': 46, 'description': 'Rim shot'},
                {'name': 'Perc', 'note': 48, 'description': 'Percussion'},
            ]
        else:
            return [
                {'name': 'Kick', 'note': 36, 'description': 'Main kick'},
                {'name': 'Snare', 'note': 38, 'description': 'Snare drum'},
                {'name': 'Hi-Hat', 'note': 42, 'description': 'Hi-hat'},
                {'name': 'Perc', 'note': 48, 'description': 'Percussion'},
            ]
    
    def _create_style_patterns(self, style: str, created_tracks: List[Dict], track_names: List[str]) -> List[str]:
        """Create appropriate MIDI patterns for the style"""
        actions = []
        
        try:
            for i, track in enumerate(created_tracks):
                track_index = track['index']
                track_name = track_names[i]
                
                # Create MIDI clip
                clip_result = self.ableton_conn.send_command('create_clip', {
                    'track_index': track_index,
                    'clip_index': 0,
                    'length': 4.0
                })
                
                # Add notes based on track type and style
                notes = self._get_style_notes(style, track_name, i)
                
                if notes:
                    notes_result = self.ableton_conn.send_command('add_notes_to_clip', {
                        'track_index': track_index,
                        'clip_index': 0,
                        'notes': notes
                    })
                    actions.append(f"Added {style} pattern to {track_name}")
                
                # Fire the clip to start playing
                self.ableton_conn.send_command('fire_clip', {
                    'track_index': track_index,
                    'clip_index': 0
                })
                actions.append(f"Started {track_name} playback")
            
        except Exception as e:
            logger.error(f"❌ Error creating patterns: {e}")
            actions.append(f"Pattern creation error: {str(e)}")
        
        return actions
    
    def _get_style_notes(self, style: str, track_name: str, track_index: int) -> List[Dict[str, Any]]:
        """Get MIDI notes appropriate for style and track"""
        
        if 'Kick' in track_name or 'Drum' in track_name:
            # 4-on-the-floor kick pattern
            return [
                {"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 100},
                {"pitch": 36, "start_time": 1.0, "duration": 0.25, "velocity": 100},
                {"pitch": 36, "start_time": 2.0, "duration": 0.25, "velocity": 100},
                {"pitch": 36, "start_time": 3.0, "duration": 0.25, "velocity": 100}
            ]
        
        elif 'Bass' in track_name:
            if 'Afro' in style:
                # Afro house bass pattern - deeper, more syncopated
                return [
                    {"pitch": 40, "start_time": 0.0, "duration": 0.75, "velocity": 90},
                    {"pitch": 38, "start_time": 1.5, "duration": 0.5, "velocity": 85},
                    {"pitch": 43, "start_time": 2.25, "duration": 0.75, "velocity": 88},
                    {"pitch": 41, "start_time": 3.5, "duration": 0.5, "velocity": 92}
                ]
            else:
                # Standard house bass
                return [
                    {"pitch": 40, "start_time": 0.0, "duration": 1.0, "velocity": 80},
                    {"pitch": 38, "start_time": 1.0, "duration": 1.0, "velocity": 80},
                    {"pitch": 43, "start_time": 2.0, "duration": 1.0, "velocity": 80},
                    {"pitch": 41, "start_time": 3.0, "duration": 1.0, "velocity": 80}
                ]
        
        elif 'Lead' in track_name:
            # Simple lead melody
            return [
                {"pitch": 64, "start_time": 0.5, "duration": 0.5, "velocity": 70},
                {"pitch": 67, "start_time": 1.5, "duration": 0.5, "velocity": 75},
                {"pitch": 69, "start_time": 2.5, "duration": 0.5, "velocity": 72},
                {"pitch": 64, "start_time": 3.5, "duration": 0.5, "velocity": 68}
            ]
        
        elif 'Pad' in track_name or 'Harmony' in track_name:
            # Chord progression (Am - F - C - G in MIDI notes)
            return [
                # Am chord (A-C-E)
                {"pitch": 57, "start_time": 0.0, "duration": 1.0, "velocity": 60},
                {"pitch": 60, "start_time": 0.0, "duration": 1.0, "velocity": 60},
                {"pitch": 64, "start_time": 0.0, "duration": 1.0, "velocity": 60},
                # F chord (F-A-C)  
                {"pitch": 53, "start_time": 1.0, "duration": 1.0, "velocity": 60},
                {"pitch": 57, "start_time": 1.0, "duration": 1.0, "velocity": 60},
                {"pitch": 60, "start_time": 1.0, "duration": 1.0, "velocity": 60},
                # C chord (C-E-G)
                {"pitch": 60, "start_time": 2.0, "duration": 1.0, "velocity": 60},
                {"pitch": 64, "start_time": 2.0, "duration": 1.0, "velocity": 60},
                {"pitch": 67, "start_time": 2.0, "duration": 1.0, "velocity": 60},
                # G chord (G-B-D)
                {"pitch": 55, "start_time": 3.0, "duration": 1.0, "velocity": 60},
                {"pitch": 59, "start_time": 3.0, "duration": 1.0, "velocity": 60},
                {"pitch": 62, "start_time": 3.0, "duration": 1.0, "velocity": 60}
            ]
        
        elif 'Percussion' in track_name:
            # Percussion pattern with hi-hats and shakers
            return [
                {"pitch": 42, "start_time": 0.25, "duration": 0.1, "velocity": 60},  # Hi-hat
                {"pitch": 42, "start_time": 0.75, "duration": 0.1, "velocity": 55},
                {"pitch": 42, "start_time": 1.25, "duration": 0.1, "velocity": 65},
                {"pitch": 42, "start_time": 1.75, "duration": 0.1, "velocity": 58},
                {"pitch": 52, "start_time": 2.0, "duration": 0.1, "velocity": 50},   # Shaker
                {"pitch": 42, "start_time": 2.25, "duration": 0.1, "velocity": 62},
                {"pitch": 42, "start_time": 2.75, "duration": 0.1, "velocity": 57},
                {"pitch": 52, "start_time": 3.0, "duration": 0.1, "velocity": 48},
                {"pitch": 42, "start_time": 3.25, "duration": 0.1, "velocity": 64},
                {"pitch": 42, "start_time": 3.75, "duration": 0.1, "velocity": 59}
            ]
        
        return []
    
    def generate_ai_response(self, user_message: str) -> str:
        """Generate AI response using Gemini"""
        if not self.gemini_model:
            return "AI not available. Please set GOOGLE_AI_API_KEY environment variable."
        
        try:
            response = self.gemini_model.generate_content(user_message)
            return response.text
        except Exception as e:
            logger.error(f"❌ Gemini error: {e}")
            return f"AI Error: {str(e)}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        status = {
            'gemini_available': self.gemini_model is not None,
            'ableton_connected': self.ableton_conn is not None
        }
        
        if self.ableton_conn:
            try:
                response = self.ableton_conn.send_command('get_session_info')
                session = response.get('result', response)
                status.update({
                    'ableton_session': session,
                    'track_count': session.get('track_count', 0),
                    'tempo': session.get('tempo', 120)
                })
            except Exception as e:
                status['ableton_error'] = str(e)
        
        return status

def main():
    """Main function to test the enhanced system"""
    print("🎵 Enhanced Chat-leton MCP Server")
    print("=" * 50)
    
    # Initialize system
    chatleton = EnhancedChatletonMCP()
    
    # Check status
    status = chatleton.get_status()
    print(f"🧠 Gemini AI: {'✅ Available' if status['gemini_available'] else '❌ Not available'}")
    
    # Test Ableton connection
    if chatleton.connect_ableton():
        print(f"🎛️ Ableton: ✅ Connected ({status.get('track_count', 0)} tracks)")
        
        # Test intelligent track creation
        print("\n🎵 Testing intelligent track creation...")
        
        result = chatleton.create_intelligent_track(
            style="Afro House",
            user_request="Create an uplifting Afro House track with deep bass, percussion, and atmospheric pads"
        )
        
        if result['status'] == 'success':
            print(f"🎉 SUCCESS! Created {result['style']} track:")
            print(f"   • Created {result['created_tracks']} tracks")
            print(f"   • Set tempo to {result['bpm']} BPM")
            print(f"   • Actions: {len(result['actions_taken'])}")
            
            print("\n🧠 AI Production Plan:")
            ai_plan = result.get('ai_plan', '')
            if len(ai_plan) > 500:
                print(ai_plan[:500] + "...")
            else:
                print(ai_plan)
                
            print(f"\n✅ {result['message']}")
        else:
            print(f"❌ Failed: {result['message']}")
    
    else:
        print("🎛️ Ableton: ❌ Not connected")
        print("💡 Make sure Ableton Live is running with AbletonMCP Remote Script")
    
    # Cleanup
    chatleton.disconnect_ableton()

if __name__ == "__main__":
    main() 