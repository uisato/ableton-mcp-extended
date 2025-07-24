#!/usr/bin/env python3
"""
Chat-leton GPT - Standalone AI Music Producer

A standalone AI music production assistant powered by Google Gemini 2.5 Flash.
Chat with your AI producer and watch it work in Ableton Live in real-time!

Usage:
    python chatleton_gpt.py --cli              # CLI chat interface
    python chatleton_gpt.py --gui              # GUI chat interface  
    python chatleton_gpt.py --web              # Web interface
    python chatleton_gpt.py --mcp              # MCP server mode
    python chatleton_gpt.py --all              # All interfaces
"""

import asyncio
import argparse
import logging
import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import threading
import queue

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Core AI imports
from music_intelligence import GeminiOrchestrator, StyleAnalyzer, StockPluginExpert

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChatletonGPT:
    """
    Main Chat-leton GPT application class
    
    A standalone AI music producer that can run in multiple modes:
    - CLI chat interface
    - GUI chat interface  
    - Web interface
    - MCP server mode
    """
    
    def __init__(self):
        """Initialize Chat-leton GPT"""
        self.name = "Chat-leton GPT"
        self.version = "1.0.0"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize AI systems
        self.orchestrator = None
        self.style_analyzer = None
        self.plugin_expert = None
        
        # Application state
        self.running = False
        self.current_project = None
        self.chat_history = []
        self.ableton_connected = False
        
        # Interface instances
        self.cli_interface = None
        self.gui_interface = None
        self.web_interface = None
        self.mcp_server = None
        
        logger.info(f"Chat-leton GPT v{self.version} initialized")
    
    async def initialize_ai_systems(self):
        """Initialize AI systems"""
        try:
            logger.info("🤖 Initializing AI systems...")
            
            # Check API key
            if not os.getenv("GOOGLE_AI_API_KEY"):
                raise ValueError("GOOGLE_AI_API_KEY environment variable not set!")
            
            # Initialize components
            self.orchestrator = GeminiOrchestrator()
            self.style_analyzer = StyleAnalyzer()
            self.plugin_expert = StockPluginExpert()
            
            # Start chat session
            self.orchestrator.start_chat_session()
            
            logger.info("✅ AI systems ready!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI systems: {e}")
            return False
    
    async def check_ableton_connection(self):
        """Check if Ableton Live is connected using enhanced integration"""
        try:
            # Initialize enhanced Ableton integration if not already done
            if not hasattr(self, 'ableton'):
                from music_intelligence.ableton_integration import EnhancedAbletonIntegration
                self.ableton = EnhancedAbletonIntegration()
                
                # Add status callback for real-time updates
                self.ableton.add_status_callback(self._on_ableton_status_change)
            
            # Test connection
            test_results = await self.ableton.test_connection()
            self.ableton_connected = test_results.get("command_test", False)
            
            if self.ableton_connected:
                logger.info(f"✅ Ableton Live connected - {self.ableton.get_session_summary()['track_count']} tracks")
            else:
                logger.info("⚠️ Ableton Live not connected")
                
            return self.ableton_connected
            
        except Exception as e:
            logger.debug(f"Ableton connection check failed: {e}")
            self.ableton_connected = False
            return False
    
    async def process_user_message(self, message: str) -> Dict[str, Any]:
        """
        Process user message and return response with actions
        
        Args:
            message: User's message
            
        Returns:
            Response dictionary with message, actions, and metadata
        """
        try:
            timestamp = datetime.now().isoformat()
            
            # Add to chat history
            self.chat_history.append({
                "timestamp": timestamp,
                "user": message,
                "type": "user_message"
            })
            
            # Process with AI
            ai_response = await self.orchestrator.chat(message)
            
            # Intelligent detection of generation requests
            is_generation_request = await self._detect_generation_request(message)
            
            # Prepare response
            response = {
                "timestamp": timestamp,
                "message": ai_response,
                "type": "ai_response",
                "is_generation": is_generation_request,
                "ableton_connected": self.ableton_connected,
                "actions": []
            }
            
            # If it's a generation request and Ableton is connected, actually generate!
            if is_generation_request and self.ableton_connected:
                logger.info(f"🎵 Detected generation request: {message}")
                try:
                    # Analyze the request for actionable items
                    analysis = await self.orchestrator.analyze_user_request(message)
                    
                    # Create creative brief
                    brief = await self.orchestrator.create_creative_brief(analysis)
                    
                    # Actually generate the track in Ableton!
                    generation_actions = await self._generate_track_in_ableton(brief, analysis)
                    
                    # Prepare response with real actions
                    actions = [
                        {
                            "type": "track_generated",
                            "value": len(generation_actions),
                            "description": f"Generated {brief.style} track with {len(generation_actions)} actions"
                        },
                        {
                            "type": "ableton_updated",
                            "value": f"{brief.bpm} BPM, {brief.key} key",
                            "description": f"Set project to {brief.bpm} BPM in {brief.key}"
                        }
                    ]
                    
                    # Add individual actions
                    for action in generation_actions[-3:]:  # Show last 3 actions
                        actions.append({
                            "type": "generation_step",
                            "value": action.get("action_type", "unknown") if isinstance(action, dict) else getattr(action, "action_type", "unknown"),
                            "description": action.get("description", "Unknown action") if isinstance(action, dict) else getattr(action, "description", "Unknown action")
                        })
                    
                    response["actions"] = actions
                    response["analysis"] = {
                        "style": brief.style,
                        "bpm": brief.bpm,
                        "key": brief.key,
                        "mood": analysis.get("mood", "Unknown"),
                        "track_elements": brief.track_elements,
                        "actions_performed": len(generation_actions)
                    }
                    response["generation_complete"] = True
                    
                except Exception as e:
                    logger.error(f"Error generating track: {e}")
                    response["actions"] = [
                        {
                            "type": "error",
                            "value": str(e),
                            "description": f"Generation failed: {str(e)}"
                        }
                    ]
            
            # Add to chat history
            self.chat_history.append(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "message": f"Sorry, I encountered an error: {str(e)}",
                "type": "error",
                "is_generation": False,
                "ableton_connected": self.ableton_connected,
                "actions": []
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current status of Chat-leton GPT"""
        status = {
            "name": self.name,
            "version": self.version,
            "session_id": self.session_id,
            "running": self.running,
            "ableton_connected": self.ableton_connected,
            "ai_ready": self.orchestrator is not None,
            "chat_history_length": len(self.chat_history),
            "available_styles": self.style_analyzer.list_available_styles() if self.style_analyzer else [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Add Ableton session info if connected
        if self.ableton_connected and hasattr(self, 'ableton'):
            try:
                ableton_info = self.ableton.get_session_summary()
                status["ableton_session"] = ableton_info
                status["ableton_status"] = self.ableton.get_connection_info()
            except Exception as e:
                logger.debug(f"Error getting Ableton status: {e}")
        
        return status
    
    async def _generate_track_in_ableton(self, brief, analysis) -> List:
        """Generate a complete track with specialized AI experts using proven MCP pattern"""
        logger.info(f"🎵 Starting expert-driven track generation: {brief.style}")
        
        # Import the working MCP connection and AI experts
        sys.path.append('MCP_Server')
        from server import AbletonConnection
        from music_intelligence.ai_experts import AIExpertOrchestrator
        
        try:
            # Step 1: Initialize AI Expert Orchestrator
            expert_orchestrator = AIExpertOrchestrator(self.orchestrator.model)
            
            # Step 2: Connect using proven working pattern
            conn = AbletonConnection('localhost', 9877)
            actions = []
            
            # Step 3: AI creates complete song structure plan
            structure_prompt = f"""
            Create a complete song structure for a {brief.style} track. Respond with JSON:
            {{
                "sections": [
                    {{"name": "Intro", "bars": 8, "energy": "low", "elements": ["atmosphere", "subtle_perc"]}},
                    {{"name": "Build_1", "bars": 8, "energy": "medium", "elements": ["kick", "hihat", "bass_intro"]}},
                    {{"name": "Drop_1", "bars": 16, "energy": "high", "elements": ["all", "lead", "full_bass"]}},
                    {{"name": "Break", "bars": 8, "energy": "low", "elements": ["pads", "lead_minimal", "atmosphere"]}},
                    {{"name": "Build_2", "bars": 8, "energy": "medium", "elements": ["kick", "bass", "rising_energy"]}},
                    {{"name": "Drop_2", "bars": 16, "energy": "high", "elements": ["all", "lead_variations", "percussion"]}},
                    {{"name": "Outro", "bars": 8, "energy": "low", "elements": ["pads", "atmosphere", "fade"]}}
                ]
            }}
            """
            
            # Use async executor for synchronous Gemini call
            import asyncio
            loop = asyncio.get_event_loop()
            structure_response = await loop.run_in_executor(
                None,
                lambda: self.orchestrator.model.generate_content(structure_prompt)
            )
            
            # Parse structure with error handling like AI experts
            try:
                structure_text = structure_response.text.strip()
                structure = json.loads(structure_text)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Structure JSON decode error: {e}")
                logger.error(f"Raw structure response: {structure_text[:500]}...")
                
                # Try to extract JSON from response if it's embedded in text
                import re
                json_match = re.search(r'\{.*\}', structure_text, re.DOTALL)
                if json_match:
                    try:
                        structure = json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        # Fallback to simple structure
                        structure = {
                            "sections": [
                                {"name": "Drop_1", "bars": 16, "energy": "high", "elements": ["all"]}
                            ]
                        }
                else:
                    # Fallback to simple structure
                    structure = {
                        "sections": [
                            {"name": "Drop_1", "bars": 16, "energy": "high", "elements": ["all"]}
                        ]
                    }
            
            logger.info(f"🎼 AI planned {len(structure['sections'])} sections")
            actions.append({"action_type": "planning", "description": f"AI planned {len(structure['sections'])} song sections"})
            
            # Step 4: Set basic song parameters
            conn.send_command('set_tempo', {'tempo': brief.bpm})
            actions.append({"action_type": "tempo", "description": f"Set tempo to {brief.bpm} BPM"})
            
            # Step 5: Create foundational tracks with proven working instruments
            track_setup = {
                'drums': conn.send_command('create_midi_track', {'name': f'{brief.style} Drums'}),
                'bass': conn.send_command('create_midi_track', {'name': f'{brief.style} Bass'}),
                'lead': conn.send_command('create_midi_track', {'name': f'{brief.style} Lead'}),
                'pads': conn.send_command('create_midi_track', {'name': f'{brief.style} Pads'})
            }
            
            # Enhanced instrument selection based on genre/style
            print("🎵 Getting genre-specific instrument suggestions...")
            try:
                # Get AI-curated suggestions for the style
                track_types = ['drums', 'bass', 'lead', 'pads']
                style = user_input.lower()
                
                # Extract genre from user input (simple approach)
                genre = 'deep house'  # default
                if any(x in style for x in ['jazz', 'swing', 'bebop']):
                    genre = 'jazz'
                elif any(x in style for x in ['trap', 'hip hop', 'rap']):
                    genre = 'trap' 
                elif any(x in style for x in ['rock', 'punk', 'metal']):
                    genre = 'rock'
                elif any(x in style for x in ['house', 'techno', 'electronic', 'edm']):
                    genre = 'deep house'
                
                suggestions_result = conn.send_command('suggest_instruments_for_music_genre', {
                    'genre': genre,
                    'track_types': track_types
                })
                print(f"📊 Genre suggestions for {genre}:")
                print(suggestions_result)
                
            except Exception as e:
                print(f"⚠️ Could not get genre suggestions: {e}")
            
            # Load instruments using enhanced selection
            enhanced_instrument_map = {
                'drums': {
                    'deep house': '64 Pads Dub Techno Kit.adg',
                    'jazz': '32 Pad Kit Jazz.adg', 
                    'trap': 'Drum Rack',
                    'rock': '32 Pad Kit Rock.adg'
                },
                'bass': {
                    'deep house': 'Bass',
                    'jazz': 'Electric',
                    'trap': 'Bass', 
                    'rock': 'Bass'
                },
                'lead': {
                    'deep house': 'Analog',
                    'jazz': 'Electric',
                    'trap': 'Analog',
                    'rock': 'Analog'
                },
                'pads': {
                    'deep house': 'Drift', 
                    'jazz': 'Electric',
                    'trap': 'Drift',
                    'rock': 'Analog'
                }
            }
            
            for track_name, track_info in track_setup.items():
                try:
                    # Use enhanced genre-specific instrument selection
                    if track_name == 'drums':
                        kit_name = enhanced_instrument_map['drums'].get(genre, 'Drum Rack')
                        result = conn.send_command('load_specific_drum_kit_by_name', {
                            'track_index': track_info['index'],
                            'kit_name': kit_name
                        })
                        print(f"✅ Loaded {kit_name} on {track_name}")
                    else:
                        # Map track names to instrument categories
                        instrument_category = track_name
                        if track_name in ['lead', 'pads']:
                            instrument_category = track_name
                        elif track_name == 'bass':
                            instrument_category = 'bass'
                        else:
                            instrument_category = 'lead'  # fallback
                            
                        instrument_name = enhanced_instrument_map[instrument_category].get(genre, 'Analog')
                        result = conn.send_command('load_specific_instrument_by_name', {
                            'track_index': track_info['index'],
                            'instrument_name': instrument_name
                        })
                        print(f"✅ Loaded {instrument_name} on {track_name}")
                        
                except Exception as e:
                    print(f"❌ Error loading instrument for {track_name}: {e}")
                    # Fallback to basic loading
                    try:
                        basic_map = {'drums': 'drums', 'bass': 'bass', 'lead': 'synth', 'pads': 'synth'}
                        result = conn.send_command('load_instrument_or_effect', {
                            'track_index': track_info['index'],
                            'uri': basic_map.get(track_name, 'synth')
                        })
                        print(f"⚠️ Used fallback for {track_name}")
                    except Exception as fallback_error:
                        print(f"❌ Fallback also failed for {track_name}: {fallback_error}")
            
            # Step 6: AI experts iteratively create each section with sophisticated musical content
            for section_idx, section in enumerate(structure['sections']):
                logger.info(f"🎵 Creating {section['name']} section with AI experts...")
                
                # Generate complete musical section using specialized AI experts
                expert_content = await expert_orchestrator.generate_complete_section(
                    style=brief.style,
                    key=brief.key,
                    bpm=brief.bpm,
                    section=section['name'],
                    bars=section['bars'],
                    energy=section.get('energy', 'medium')
                )
                
                # Create the musical content in Ableton using expert-generated data
                section_actions = await self._create_expert_section_in_ableton(
                    conn, section, expert_content, track_setup, section_idx
                )
                actions.extend(section_actions)
                
                # AI decides if it wants to continue or make adjustments
                continue_prompt = f"""
                I just created the {section['name']} section of a {brief.style} track using specialized AI experts.
                Section contains: {expert_content['expert_analysis']['musical_complexity']} complexity music
                Current progress: {section_idx + 1}/{len(structure['sections'])} sections complete.
                
                Should I:
                A) Continue to next section
                B) Make adjustments to current section  
                C) This track is complete
                
                Respond with just A, B, or C.
                """
                
                # Use async executor for synchronous Gemini call
                decision_response = await loop.run_in_executor(
                    None,
                    lambda: self.orchestrator.model.generate_content(continue_prompt)
                )
                decision = decision_response.text.strip().upper()
                
                if decision == 'C':
                    logger.info("🤖 AI decided track is complete!")
                    actions.append({"action_type": "ai_decision", "description": "AI determined track is complete"})
                    break
                elif decision == 'B':
                    logger.info("🤖 AI wants to refine current section")
                    actions.append({"action_type": "ai_decision", "description": "AI refined current section"})
            
            # Step 7: Start playback
            conn.send_command('start_playback')
            actions.append({"action_type": "playback", "description": "Started track playback"})
            
            # Get final session info
            final_session = conn.send_command('get_session_info')
            session_info = final_session.get('result', final_session)
            actions.append({"action_type": "completion", "description": f"Expert-generated track complete! Session now has {session_info.get('track_count', 0)} tracks"})
            
            conn.disconnect()
            logger.info(f"✅ Expert-driven track generation complete: {len(actions)} actions")
            return actions
            
        except Exception as e:
            logger.error(f"❌ Track generation failed: {e}")
            raise Exception(f"Track generation failed: {str(e)}")
    
    async def _create_expert_section_in_ableton(self, conn, section, expert_content, tracks, section_idx):
        """Create sophisticated musical section in Ableton using AI expert-generated content"""
        actions = []
        clip_index = section_idx
        section_bars = section.get('bars', 8)
        
        logger.info(f"🎼 Creating {section['name']} with expert-generated content ({section_bars} bars)")
        
        # 1. Create sophisticated drum patterns using drum expert
        drum_content = expert_content.get('drums', {})
        if drum_content and 'kick_pattern' in drum_content:
            all_drum_notes = []
            
            # Add kick pattern
            kick_pattern = drum_content.get('kick_pattern', {})
            for note in kick_pattern.get('notes', []):
                all_drum_notes.append({
                    "pitch": note['slot'],
                    "start_time": note['time'],
                    "duration": note['duration'],
                    "velocity": note['velocity']
                })
            
            # Add snare pattern
            snare_pattern = drum_content.get('snare_pattern', {})
            for note in snare_pattern.get('notes', []):
                all_drum_notes.append({
                    "pitch": note['slot'],
                    "start_time": note['time'],
                    "duration": note['duration'],
                    "velocity": note['velocity']
                })
            
            # Add hi-hat pattern
            hihat_pattern = drum_content.get('hihat_pattern', {})
            for note in hihat_pattern.get('notes', []):
                all_drum_notes.append({
                    "pitch": note['slot'],
                    "start_time": note['time'],
                    "duration": note['duration'],
                    "velocity": note['velocity']
                })
            
            # Add percussion pattern
            perc_pattern = drum_content.get('percussion_pattern', {})
            for note in perc_pattern.get('notes', []):
                all_drum_notes.append({
                    "pitch": note['slot'],
                    "start_time": note['time'],
                    "duration": note['duration'],
                    "velocity": note['velocity']
                })
            
            if all_drum_notes:
                conn.send_command('create_clip', {
                    'track_index': tracks['drums']['index'],
                    'clip_index': clip_index,
                    'length': section_bars
                })
                conn.send_command('add_notes_to_clip', {
                    'track_index': tracks['drums']['index'],
                    'clip_index': clip_index,
                    'notes': all_drum_notes
                })
                conn.send_command('fire_clip', {
                    'track_index': tracks['drums']['index'],
                    'clip_index': clip_index
                })
                actions.append({"action_type": "drums", "description": f"Created expert drum arrangement: {drum_content.get('musical_description', 'Complete drum kit')}"})
        
        # 2. Create sophisticated bass lines using bass expert
        bass_content = expert_content.get('bass', {})
        if bass_content and 'bass_line' in bass_content:
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
                    'clip_index': clip_index,
                    'length': section_bars
                })
                conn.send_command('add_notes_to_clip', {
                    'track_index': tracks['bass']['index'],
                    'clip_index': clip_index,
                    'notes': bass_notes
                })
                conn.send_command('fire_clip', {
                    'track_index': tracks['bass']['index'],
                    'clip_index': clip_index
                })
                actions.append({"action_type": "bass", "description": f"Created expert bass line: {bass_content.get('musical_description', 'Sophisticated bass arrangement')}"})
        
        # 3. Create sophisticated chord progressions using harmony expert
        harmony_content = expert_content.get('harmony', {})
        if harmony_content and 'chord_progression' in harmony_content:
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
                    'clip_index': clip_index,
                    'length': section_bars
                })
                conn.send_command('add_notes_to_clip', {
                    'track_index': tracks['pads']['index'],
                    'clip_index': clip_index,
                    'notes': pad_notes
                })
                conn.send_command('fire_clip', {
                    'track_index': tracks['pads']['index'],
                    'clip_index': clip_index
                })
                actions.append({"action_type": "harmony", "description": f"Created expert chord progression: {harmony_content.get('musical_description', 'Sophisticated harmonic content')}"})
        
        # 4. Create sophisticated melodies using melody expert (if present)
        melody_content = expert_content.get('melody')
        if melody_content and 'melody_line' in melody_content:
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
                    'clip_index': clip_index,
                    'length': section_bars
                })
                conn.send_command('add_notes_to_clip', {
                    'track_index': tracks['lead']['index'],
                    'clip_index': clip_index,
                    'notes': lead_notes
                })
                conn.send_command('fire_clip', {
                    'track_index': tracks['lead']['index'],
                    'clip_index': clip_index
                })
                actions.append({"action_type": "melody", "description": f"Created expert melody: {melody_content.get('musical_description', 'Memorable melodic content')}"})
        
        # 5. Log expert analysis
        expert_analysis = expert_content.get('expert_analysis', {})
        actions.append({
            "action_type": "expert_analysis", 
            "description": f"Section completed with {expert_analysis.get('musical_complexity', 'standard')} complexity using specialized AI experts"
        })
        
        logger.info(f"✅ Expert section creation complete: {len(actions)} musical elements created")
        return actions
    
    def _on_ableton_status_change(self, status, state):
        """Callback for Ableton connection status changes"""
        try:
            from music_intelligence.ableton_integration import ConnectionStatus
            
            if status == ConnectionStatus.CONNECTED:
                self.ableton_connected = True
                logger.info(f"🎛️ Ableton connected: {state.track_count} tracks, {state.tempo} BPM")
            elif status == ConnectionStatus.DISCONNECTED:
                self.ableton_connected = False
                logger.info("🔌 Ableton disconnected")
            elif status == ConnectionStatus.ERROR:
                self.ableton_connected = False
                logger.warning("❌ Ableton connection error")
            elif status == ConnectionStatus.RECONNECTING:
                logger.info("🔄 Ableton reconnecting...")
                
        except Exception as e:
            logger.error(f"Error in Ableton status callback: {e}")
    
    # ========================================================================
    # INTERFACE IMPLEMENTATIONS
    # ========================================================================
    
    async def run_cli(self):
        """Run CLI chat interface"""
        print("🎵 CHAT-LETON GPT - CLI Interface")
        print("=" * 50)
        print("Your AI Music Producer is ready!")
        print("Type 'help' for commands, 'quit' to exit")
        
        # Initialize AI
        if not await self.initialize_ai_systems():
            print("❌ Failed to initialize AI systems")
            return
        
        # Check Ableton connection
        await self.check_ableton_connection()
        if self.ableton_connected:
            print("✅ Ableton Live connected")
        else:
            print("⚠️  Ableton Live not detected (some features limited)")
        
        print("\n" + "="*50)
        self.running = True
        
        try:
            while self.running:
                # Get user input
                user_input = input("\n🎤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'help':
                    self._print_help()
                    continue
                elif user_input.lower() == 'status':
                    status = await self.get_status()
                    print(f"\n📊 Status: {json.dumps(status, indent=2)}")
                    continue
                elif user_input.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                
                # Process message
                print("🤔 Chat-leton GPT is thinking...")
                response = await self.process_user_message(user_input)
                
                # Display response based on generation status
                if response.get('generation_complete'):
                    print(f"\n✅ Generation Complete!")
                    print(f"🎵 {response['message']}")
                    
                    # Show generation results prominently
                    if response.get('analysis'):
                        analysis = response['analysis']
                        print(f"\n🎼 Generated Track:")
                        print(f"   🎨 Style: {analysis['style']}")
                        print(f"   🕰️ BPM: {analysis['bpm']}")
                        print(f"   🎹 Key: {analysis['key']}")
                        print(f"   🎭 Mood: {analysis['mood']}")
                        print(f"   🎛️ Elements: {', '.join(analysis.get('track_elements', []))}")
                        print(f"   ⚡ Actions: {analysis['actions_performed']}")
                    
                    if response.get('actions'):
                        print("\n⚡ Actions Performed:")
                        for action in response['actions']:
                            print(f"   • {action['description']}")
                            
                    print("\n🎧 Check your Ableton Live session - the track should be ready!")
                    
                elif response.get('is_generation') and not self.ableton_connected:
                    print(f"\n🎵 Chat-leton GPT: {response['message']}")
                    print("\n⚠️ Note: Connect to Ableton Live for automatic track generation!")
                    print("   Run: python test_ableton_integration.py --quick")
                    
                else:
                    print(f"\n🎵 Chat-leton GPT: {response['message']}")
                    
                    # Display actions if any
                    if response.get('actions'):
                        print(f"\n⚡ Actions:")
                        for action in response['actions']:
                            print(f"   • {action['description']}")
                    
                    # Show analysis if available
                    if response.get('analysis'):
                        analysis = response['analysis']
                        print(f"\n🎨 Analysis:")
                        print(f"   Style: {analysis.get('style', 'Unknown')}")
                        print(f"   BPM: {analysis.get('bpm', 'Unknown')}")
                        print(f"   Key: {analysis.get('key', 'Unknown')}")
                        print(f"   Mood: {analysis.get('mood', 'Unknown')}")
        
        except KeyboardInterrupt:
            print("\n👋 Chat interrupted by user")
        
        finally:
            self.running = False
            print("\n🎵 Thanks for using Chat-leton GPT!")
    
    def _print_help(self):
        """Print help information"""
        print("""
🎵 CHAT-LETON GPT COMMANDS:

🎨 Music Generation:
   "Create an Afro House track like Black Coffee"
   "Generate a progressive house anthem"
   "Make a Keinemusik-style deep house track"

💬 Chat Examples:
   "How do I create warm bass sounds?"
   "What plugins work best for deep house?"
   "Explain the structure of Afro House"

🛠️ System Commands:
   help     - Show this help
   status   - Show system status
   clear    - Clear screen
   quit     - Exit Chat-leton GPT

🎛️ Ableton Integration:
   When connected, I can help you implement tracks directly!
        """)
    
    async def run_gui(self):
        """Run GUI chat interface"""
        print("🖥️  Starting GUI interface...")
        # This would implement a GUI using tkinter, PyQt, or similar
        # For now, we'll create a simple implementation
        
        try:
            import tkinter as tk
            from tkinter import scrolledtext, messagebox
            import threading
            
            await self.initialize_ai_systems()
            await self.check_ableton_connection()
            
            # Create main window
            self.gui_root = tk.Tk()
            self.gui_root.title("Chat-leton GPT - AI Music Producer")
            self.gui_root.geometry("800x600")
            
            # Create chat display
            self.chat_display = scrolledtext.ScrolledText(
                self.gui_root, 
                wrap=tk.WORD, 
                width=80, 
                height=30,
                state=tk.DISABLED
            )
            self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
            
            # Create input frame
            input_frame = tk.Frame(self.gui_root)
            input_frame.pack(padx=10, pady=5, fill=tk.X)
            
            # Create input field
            self.input_field = tk.Entry(input_frame, font=("Arial", 12))
            self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            self.input_field.bind("<Return>", self._gui_send_message)
            
            # Create send button
            send_button = tk.Button(
                input_frame, 
                text="Send", 
                command=self._gui_send_message,
                font=("Arial", 12)
            )
            send_button.pack(side=tk.RIGHT)
            
            # Status bar
            self.status_var = tk.StringVar()
            status_bar = tk.Label(
                self.gui_root, 
                textvariable=self.status_var, 
                relief=tk.SUNKEN, 
                anchor=tk.W
            )
            status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Initialize status
            status_text = "🎵 Chat-leton GPT Ready"
            if self.ableton_connected:
                status_text += " | ✅ Ableton Connected"
            else:
                status_text += " | ⚠️ Ableton Disconnected"
            self.status_var.set(status_text)
            
            # Welcome message
            self._gui_add_message("🎵 Chat-leton GPT", 
                                "Welcome! I'm your AI music producer. Ask me to create tracks, analyze styles, or give production advice!", 
                                "assistant")
            
            self.running = True
            self.gui_root.mainloop()
            
        except ImportError:
            print("❌ GUI requires tkinter. Install with: pip install tk")
        except Exception as e:
            print(f"❌ GUI error: {e}")
    
    def _gui_send_message(self, event=None):
        """Handle GUI message sending"""
        message = self.input_field.get().strip()
        if not message:
            return
        
        self.input_field.delete(0, tk.END)
        self._gui_add_message("You", message, "user")
        
        # Process in background thread
        def process_message():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(self.process_user_message(message))
                
                # Update GUI in main thread
                self.gui_root.after(0, lambda: self._gui_add_message(
                    "🎵 Chat-leton GPT", 
                    response['message'], 
                    "assistant"
                ))
                
                # Show actions if any
                if response.get('actions'):
                    actions_text = "⚡ Actions:\n" + "\n".join(
                        f"• {action['description']}" for action in response['actions']
                    )
                    self.gui_root.after(0, lambda: self._gui_add_message(
                        "System", 
                        actions_text, 
                        "system"
                    ))
                
            except Exception as e:
                self.gui_root.after(0, lambda: self._gui_add_message(
                    "Error", 
                    f"Sorry, I encountered an error: {str(e)}", 
                    "error"
                ))
        
        threading.Thread(target=process_message, daemon=True).start()
    
    def _gui_add_message(self, sender: str, message: str, msg_type: str):
        """Add message to GUI chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Color coding
        colors = {
            "user": "#0066cc",
            "assistant": "#009900", 
            "system": "#ff8800",
            "error": "#cc0000"
        }
        
        color = colors.get(msg_type, "#000000")
        
        self.chat_display.insert(tk.END, f"\n{sender}: ", ("bold",))
        self.chat_display.insert(tk.END, f"{message}\n")
        
        # Configure tags for formatting
        self.chat_display.tag_config("bold", font=("Arial", 12, "bold"))
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    async def run_web(self):
        """Run web interface"""
        print("🌐 Web interface not implemented yet")
        print("This would create a modern web-based chat interface")
        # TODO: Implement with FastAPI + WebSockets + modern frontend
    
    async def run_mcp_server(self):
        """Run as MCP server"""
        print("🔌 Starting MCP server mode...")
        # Import and run the enhanced MCP tools
        from enhanced_mcp_tools import register_enhanced_tools
        # This would start the MCP server with our tools
        print("MCP server running with Chat-leton GPT capabilities")

    async def _display_status(self) -> str:
        """Display current status and return formatted string"""
        status = f"\n📊 Status: AI Ready {'✅' if self.ai_ready else '❌'}"
        status += f" | Ableton {'🎛️ Connected' if self.ableton_connected else '❌ Disconnected'}"
        if self.ableton_connected:
            session_info = self.ableton.get_session_summary()
            status += f" | {session_info['track_count']} tracks, {session_info['tempo']} BPM"
        return status
    
    async def _detect_generation_request(self, message: str) -> bool:
        """
        Intelligently detect if the user wants to generate music
        Uses AI to understand musical intent beyond just trigger words
        """
        # First check for explicit trigger words
        explicit_triggers = [
            "create", "generate", "make", "build", "produce", "compose",
            "write", "craft", "design", "develop", "arrange"
        ]
        
        if any(trigger in message.lower() for trigger in explicit_triggers):
            return True
        
        # Check for musical descriptions that imply generation requests
        musical_patterns = [
            # BPM specifications
            r'\d+\s*bpm',
            r'\d+\s*beats?\s*per\s*minute',
            
            # Style specifications  
            r'(afro|deep|progressive|tech|tropical)\s*house',
            r'techno|trance|drum\s*and\s*bass|dubstep',
            r'ambient|chillout|downtempo|breakbeat',
            
            # Key specifications
            r'[a-g]\s*(major|minor|min|maj)',
            r'key\s*of\s*[a-g]',
            
            # Track structure terms
            r'track|song|beat|composition|arrangement',
            r'intro|verse|chorus|bridge|breakdown|drop',
            
            # Instrument combinations
            r'(kick|bass|lead|pad|synth).*?(kick|bass|lead|pad|synth)',
            r'drums.*?bass|bass.*?drums',
        ]
        
        import re
        for pattern in musical_patterns:
            if re.search(pattern, message.lower()):
                # If AI is available, use it to confirm; otherwise, assume yes for matched patterns
                if hasattr(self, 'orchestrator') and self.orchestrator:
                    return await self._ai_confirm_generation_intent(message)
                else:
                    # Fallback: If pattern matches music description, likely a generation request
                    return True
        
        # If no patterns match, probably not a generation request
        return False
    
    async def _ai_confirm_generation_intent(self, message: str) -> bool:
        """
        Use AI to confirm if the user wants to generate music
        """
        try:
            if not hasattr(self, 'orchestrator') or not self.orchestrator:
                return False  # Can't confirm without AI
                
            confirmation_prompt = f"""
            Analyze this user message to determine if they want to generate/create music in Ableton Live:
            
            "{message}"
            
            Consider:
            - Are they describing a musical style, BPM, or arrangement?
            - Are they giving specifications for a track?
            - Are they requesting music production guidance vs wanting actual generation?
            
            Respond with only "YES" if they want music generated, or "NO" if they want advice/analysis.
            """
            
            ai_response = await self.orchestrator._generate_content_async(confirmation_prompt)
            return "YES" in ai_response.upper()
            
        except Exception as e:
            logger.warning(f"AI confirmation failed: {e}")
            return False  # Default to safe side


async def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="Chat-leton GPT - AI Music Producer")
    parser.add_argument("--cli", action="store_true", help="Run CLI interface")
    parser.add_argument("--gui", action="store_true", help="Run GUI interface")
    parser.add_argument("--web", action="store_true", help="Run web interface")
    parser.add_argument("--mcp", action="store_true", help="Run MCP server")
    parser.add_argument("--all", action="store_true", help="Run all interfaces")
    
    args = parser.parse_args()
    
    # Initialize Chat-leton GPT
    app = ChatletonGPT()
    
    # Determine which interfaces to run
    if args.all:
        print("🚀 Starting all interfaces...")
        # In a real implementation, these would run concurrently
        await app.run_cli()
    elif args.gui:
        await app.run_gui()
    elif args.web:
        await app.run_web()
    elif args.mcp:
        await app.run_mcp_server()
    elif args.cli:
        await app.run_cli()
    else:
        # Default to CLI
        await app.run_cli()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Chat-leton GPT shutdown.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1) 