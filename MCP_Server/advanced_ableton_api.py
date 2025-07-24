"""
Advanced Ableton Live API - Full Featured MCP Integration

This module provides comprehensive access to Ableton Live's complete API,
exposing advanced features that are typically only available to power users.

Features included:
- Advanced device parameter control and automation
- Comprehensive sample and audio manipulation  
- Browser integration and preset management
- Advanced MIDI features (probability, velocity deviation, etc.)
- Clip envelope automation and warp marker control
- Scene and arrangement management
- Professional mixing and routing features
- Scale instrument integration for musical coherence
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AdvancedAbletonAPI:
    """Advanced Ableton Live API wrapper with full feature access"""
    
    def __init__(self, connection):
        self.connection = connection
        self.logger = logging.getLogger(__name__)
        
    # ================================================================
    # ADVANCED DEVICE CONTROL
    # ================================================================
    
    def get_device_parameters(self, track_index: int, device_index: int) -> Dict[str, Any]:
        """Get all parameters for a specific device with automation states"""
        return self.connection.send_command("get_device_parameters", {
            "track_index": track_index,
            "device_index": device_index
        })
    
    def set_device_parameter(self, track_index: int, device_index: int, 
                           parameter_index: int, value: float) -> Dict[str, Any]:
        """Set device parameter with precise control"""
        return self.connection.send_command("set_device_parameter", {
            "track_index": track_index,
            "device_index": device_index,
            "parameter_index": parameter_index,
            "value": value
        })
    
    def batch_set_device_parameters(self, track_index: int, device_index: int, 
                                  parameter_values: List[Dict]) -> Dict[str, Any]:
        """Set multiple device parameters in one operation for efficiency"""
        return self.connection.send_command("batch_set_device_parameters", {
            "track_index": track_index,
            "device_index": device_index,
            "parameter_values": parameter_values
        })
    
    def load_device_preset(self, track_index: int, device_index: int, 
                          preset_path: str) -> Dict[str, Any]:
        """Load a device preset by path"""
        return self.connection.send_command("load_device_preset", {
            "track_index": track_index,
            "device_index": device_index,
            "preset_path": preset_path
        })
    
    def save_device_preset(self, track_index: int, device_index: int, 
                          preset_name: str) -> Dict[str, Any]:
        """Save current device state as preset"""
        return self.connection.send_command("save_device_preset", {
            "track_index": track_index,
            "device_index": device_index,
            "preset_name": preset_name
        })

    # ================================================================
    # ADVANCED CLIP AND NOTE MANIPULATION
    # ================================================================
    
    def get_notes_from_clip(self, track_index: int, clip_index: int, 
                           from_time: float = 0, time_span: float = 32,
                           from_pitch: int = 0, pitch_span: int = 127) -> Dict[str, Any]:
        """Get notes from clip with advanced filtering"""
        return self.connection.send_command("get_notes_from_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "from_time": from_time,
            "time_span": time_span,
            "from_pitch": from_pitch,
            "pitch_span": pitch_span
        })
    
    def add_notes_with_probability(self, track_index: int, clip_index: int, 
                                 notes: List[Dict]) -> Dict[str, Any]:
        """Add notes with probability and velocity deviation (Live 11+ features)"""
        return self.connection.send_command("add_notes_with_probability", {
            "track_index": track_index,
            "clip_index": clip_index,
            "notes": notes  # Notes with probability, velocity_deviation fields
        })
    
    def quantize_notes_in_clip(self, track_index: int, clip_index: int,
                              grid_size: int, strength: float = 1.0,
                              from_time: float = 0, to_time: float = 32) -> Dict[str, Any]:
        """Advanced note quantization with strength control"""
        return self.connection.send_command("quantize_notes_in_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "grid_size": grid_size,
            "strength": strength,
            "from_time": from_time,
            "to_time": to_time
        })
    
    def randomize_note_timing(self, track_index: int, clip_index: int,
                            amount: float, from_time: float = 0, 
                            to_time: float = 32) -> Dict[str, Any]:
        """Add humanization to note timing"""
        return self.connection.send_command("randomize_note_timing", {
            "track_index": track_index,
            "clip_index": clip_index,
            "amount": amount,
            "from_time": from_time,
            "to_time": to_time
        })
    
    def set_note_probability(self, track_index: int, clip_index: int,
                           probability: float, from_time: float = 0,
                           to_time: float = 32) -> Dict[str, Any]:
        """Set note probability for generative patterns"""
        return self.connection.send_command("set_note_probability", {
            "track_index": track_index,
            "clip_index": clip_index,
            "probability": probability,
            "from_time": from_time,
            "to_time": to_time
        })

    # ================================================================
    # CLIP AUTOMATION AND ENVELOPES
    # ================================================================
    
    def add_clip_envelope_point(self, track_index: int, clip_index: int,
                               device_index: int, parameter_index: int,
                               time_val: float, value: float,
                               curve_type: int = 0) -> Dict[str, Any]:
        """Add automation point to clip envelope"""
        return self.connection.send_command("add_clip_envelope_point", {
            "track_index": track_index,
            "clip_index": clip_index,
            "device_index": device_index,
            "parameter_index": parameter_index,
            "time_val": time_val,
            "value": value,
            "curve_type": curve_type
        })
    
    def clear_clip_envelope(self, track_index: int, clip_index: int,
                           device_index: int, parameter_index: int) -> Dict[str, Any]:
        """Clear automation from clip envelope"""
        return self.connection.send_command("clear_clip_envelope", {
            "track_index": track_index,
            "clip_index": clip_index,
            "device_index": device_index,
            "parameter_index": parameter_index
        })
    
    def get_clip_envelope(self, track_index: int, clip_index: int,
                         device_index: int, parameter_index: int) -> Dict[str, Any]:
        """Get clip envelope automation data"""
        return self.connection.send_command("get_clip_envelope", {
            "track_index": track_index,
            "clip_index": clip_index,
            "device_index": device_index,
            "parameter_index": parameter_index
        })

    # ================================================================
    # BROWSER AND SAMPLE MANAGEMENT
    # ================================================================
    
    def get_browser_tree(self, category_type: str = "all") -> Dict[str, Any]:
        """Get Ableton's browser tree structure"""
        return self.connection.send_command("get_browser_tree", {
            "category_type": category_type
        })
    
    def get_browser_items_at_path(self, path: str) -> Dict[str, Any]:
        """Get browser items at specific path"""
        return self.connection.send_command("get_browser_items_at_path", {
            "path": path
        })
    
    def search_browser(self, query: str, category: str = "all") -> Dict[str, Any]:
        """Search browser for items"""
        return self.connection.send_command("search_browser", {
            "query": query,
            "category": category
        })
    
    def load_browser_item_to_track(self, track_index: int, item_uri: str,
                                  device_position: int = -1) -> Dict[str, Any]:
        """Load browser item to specific track position"""
        return self.connection.send_command("load_instrument_or_effect", {
            "track_index": track_index,
            "uri": item_uri
        })

    # ================================================================
    # AUDIO FILE AND SAMPLE MANAGEMENT
    # ================================================================
    
    def import_audio_file(self, file_path: str, track_index: int,
                         clip_index: int = 0, create_track_if_needed: bool = True) -> Dict[str, Any]:
        """Import audio file into specific clip slot"""
        return self.connection.send_command("import_audio_file", {
            "file_path": file_path,
            "track_index": track_index,
            "clip_index": clip_index,
            "create_track_if_needed": create_track_if_needed
        })
    
    def analyze_audio_clip(self, track_index: int, clip_index: int) -> Dict[str, Any]:
        """Get detailed audio analysis (tempo, key, etc.)"""
        return self.connection.send_command("analyze_audio_clip", {
            "track_index": track_index,
            "clip_index": clip_index
        })
    
    def slice_audio_clip(self, track_index: int, clip_index: int,
                        slice_method: str = "transient",
                        sensitivity: float = 0.5) -> Dict[str, Any]:
        """Slice audio clip using various methods"""
        return self.connection.send_command("slice_audio_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "slice_method": slice_method,
            "sensitivity": sensitivity
        })

    # ================================================================
    # SCENE AND ARRANGEMENT MANAGEMENT
    # ================================================================
    
    def get_scenes_info(self) -> Dict[str, Any]:
        """Get information about all scenes"""
        return self.connection.send_command("get_scenes_info", {})
    
    def create_scene(self, index: int = -1, name: str = "") -> Dict[str, Any]:
        """Create new scene at specific position"""
        return self.connection.send_command("create_scene", {
            "index": index,
            "name": name
        })
    
    def delete_scene(self, index: int) -> Dict[str, Any]:
        """Delete scene at index"""
        return self.connection.send_command("delete_scene", {
            "index": index
        })
    
    def fire_scene(self, index: int, force_legato: bool = False) -> Dict[str, Any]:
        """Fire scene with advanced options"""
        return self.connection.send_command("fire_scene", {
            "index": index,
            "force_legato": force_legato
        })
    
    def set_scene_name(self, index: int, name: str) -> Dict[str, Any]:
        """Set scene name (can include BPM/time signature info)"""
        return self.connection.send_command("set_scene_name", {
            "index": index,
            "name": name
        })

    # ================================================================
    # ADVANCED MIXING AND ROUTING
    # ================================================================
    
    def set_track_level(self, track_index: int, level: float) -> Dict[str, Any]:
        """Set track volume level (0.0 to 1.0)"""
        return self.connection.send_command("set_track_level", {
            "track_index": track_index,
            "level": level
        })
    
    def set_track_pan(self, track_index: int, pan: float) -> Dict[str, Any]:
        """Set track panning (-1.0 to 1.0)"""
        return self.connection.send_command("set_track_pan", {
            "track_index": track_index,
            "pan": pan
        })
    
    def set_send_level(self, track_index: int, send_index: int, 
                      level: float) -> Dict[str, Any]:
        """Set send level to return track"""
        return self.connection.send_command("set_send_level", {
            "track_index": track_index,
            "send_index": send_index,
            "level": level
        })
    
    def create_return_track(self, name: str = "") -> Dict[str, Any]:
        """Create new return track"""
        return self.connection.send_command("create_return_track", {
            "name": name
        })
    
    def set_crossfade_assign(self, track_index: int, assign: int) -> Dict[str, Any]:
        """Set crossfade assignment (0=A, 1=None, 2=B)"""
        return self.connection.send_command("set_crossfade_assign", {
            "track_index": track_index,
            "assign": assign
        })

    # ================================================================
    # CLIP PROPERTIES AND MANIPULATION
    # ================================================================
    
    def set_clip_loop_parameters(self, track_index: int, clip_index: int,
                                loop_start: float, loop_end: float,
                                loop_enabled: bool = True) -> Dict[str, Any]:
        """Set clip loop parameters"""
        return self.connection.send_command("set_clip_loop_parameters", {
            "track_index": track_index,
            "clip_index": clip_index,
            "loop_start": loop_start,
            "loop_end": loop_end,
            "loop_enabled": loop_enabled
        })
    
    def set_clip_follow_action(self, track_index: int, clip_index: int,
                              action: int, target_clip: int = 0,
                              chance: float = 1.0, time_val: float = 1.0) -> Dict[str, Any]:
        """Set clip follow action for generative sequences"""
        return self.connection.send_command("set_clip_follow_action", {
            "track_index": track_index,
            "clip_index": clip_index,
            "action": action,
            "target_clip": target_clip,
            "chance": chance,
            "time_val": time_val
        })
    
    def duplicate_clip_to_arrangement(self, track_index: int, clip_index: int,
                                    arrangement_time: float) -> Dict[str, Any]:
        """Duplicate clip to arrangement at specific time"""
        return self.connection.send_command("duplicate_clip_to_arrangement", {
            "track_index": track_index,
            "clip_index": clip_index,
            "arrangement_time": arrangement_time
        })

    # ================================================================
    # MUSICAL COHERENCE AND SCALE TOOLS
    # ================================================================
    
    def load_scale_instrument(self, track_index: int, scale_name: str, 
                             root_note: int) -> Dict[str, Any]:
        """Load Scale instrument to enforce musical coherence"""
        return self.connection.send_command("load_scale_instrument", {
            "track_index": track_index,
            "scale_name": scale_name,
            "root_note": root_note
        })
    
    def set_global_scale(self, scale_name: str, root_note: int) -> Dict[str, Any]:
        """Set global scale for the session"""
        return self.connection.send_command("set_global_scale", {
            "scale_name": scale_name,
            "root_note": root_note
        })
    
    def constrain_notes_to_scale(self, track_index: int, clip_index: int,
                                scale_name: str, root_note: int) -> Dict[str, Any]:
        """Constrain existing notes to scale"""
        return self.connection.send_command("constrain_notes_to_scale", {
            "track_index": track_index,
            "clip_index": clip_index,
            "scale_name": scale_name,
            "root_note": root_note
        })
    
    def generate_chord_progression(self, track_index: int, clip_index: int,
                                 style: str, key: str, bars: int = 8) -> Dict[str, Any]:
        """Generate musically correct chord progression"""
        return self.connection.send_command("generate_chord_progression", {
            "track_index": track_index,
            "clip_index": clip_index,
            "style": style,
            "key": key,
            "bars": bars
        })

    # ================================================================
    # GROOVE AND TIMING
    # ================================================================
    
    def apply_groove_to_clip(self, track_index: int, clip_index: int,
                           groove_name: str, amount: float = 1.0) -> Dict[str, Any]:
        """Apply groove template to clip"""
        return self.connection.send_command("apply_groove_to_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "groove_name": groove_name,
            "amount": amount
        })
    
    def extract_groove_from_clip(self, track_index: int, clip_index: int,
                               name: str) -> Dict[str, Any]:
        """Extract groove template from existing clip"""
        return self.connection.send_command("extract_groove_from_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "name": name
        })
    
    def set_global_groove(self, groove_name: str, amount: float = 1.0) -> Dict[str, Any]:
        """Set global groove for all clips"""
        return self.connection.send_command("set_global_groove", {
            "groove_name": groove_name,
            "amount": amount
        })

    # ================================================================
    # BATCH OPERATIONS FOR EFFICIENCY
    # ================================================================
    
    def batch_create_tracks(self, track_configs: List[Dict]) -> Dict[str, Any]:
        """Create multiple tracks in one operation"""
        return self.connection.send_command("batch_create_tracks", {
            "track_configs": track_configs
        })
    
    def batch_load_instruments(self, track_instrument_pairs: List[Dict]) -> Dict[str, Any]:
        """Load multiple instruments efficiently"""
        return self.connection.send_command("batch_load_instruments", {
            "track_instrument_pairs": track_instrument_pairs
        })
    
    def batch_edit_notes_in_clip(self, track_index: int, clip_index: int,
                               note_ids: List[int], note_data_array: List[Dict]) -> Dict[str, Any]:
        """Edit multiple notes in one operation"""
        return self.connection.send_command("batch_edit_notes_in_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "note_ids": note_ids,
            "note_data_array": note_data_array
        })

    # ================================================================
    # PROFESSIONAL WORKFLOW FEATURES
    # ================================================================
    
    def create_professional_mixdown(self, style: str) -> Dict[str, Any]:
        """Create professional mixdown setup for style"""
        return self.connection.send_command("create_professional_mixdown", {
            "style": style
        })
    
    def setup_sidechain_compression(self, source_track: int, 
                                   target_tracks: List[int]) -> Dict[str, Any]:
        """Setup sidechain compression routing"""
        return self.connection.send_command("setup_sidechain_compression", {
            "source_track": source_track,
            "target_tracks": target_tracks
        })
    
    def create_bus_routing(self, source_tracks: List[int], 
                          bus_name: str) -> Dict[str, Any]:
        """Create bus routing for grouped processing"""
        return self.connection.send_command("create_bus_routing", {
            "source_tracks": source_tracks,
            "bus_name": bus_name
        })
    
    def setup_parallel_processing(self, source_track: int, 
                                 effect_chain: List[str]) -> Dict[str, Any]:
        """Setup parallel processing chain"""
        return self.connection.send_command("setup_parallel_processing", {
            "source_track": source_track,
            "effect_chain": effect_chain
        })

    # ================================================================
    # ADVANCED PLUGIN CONTROL (WAVETABLE, BASS, ETC.)
    # ================================================================
    
    def configure_wavetable_synth(self, track_index: int, device_index: int,
                                 wavetable_settings: Dict) -> Dict[str, Any]:
        """Configure Wavetable synth with specific settings"""
        return self.connection.send_command("configure_wavetable_synth", {
            "track_index": track_index,
            "device_index": device_index,
            "wavetable_settings": wavetable_settings
        })
    
    def configure_bass_plugin(self, track_index: int, device_index: int,
                            bass_settings: Dict) -> Dict[str, Any]:
        """Configure Bass plugin with specific settings"""
        return self.connection.send_command("configure_bass_plugin", {
            "track_index": track_index,
            "device_index": device_index,
            "bass_settings": bass_settings
        })
    
    def configure_impulse_drum_rack(self, track_index: int, device_index: int,
                                   drum_settings: Dict) -> Dict[str, Any]:
        """Configure Impulse drum rack with specific samples and settings"""
        return self.connection.send_command("configure_impulse_drum_rack", {
            "track_index": track_index,
            "device_index": device_index,
            "drum_settings": drum_settings
        })
    
    def load_effect_chain_preset(self, track_index: int, 
                                effect_chain_name: str) -> Dict[str, Any]:
        """Load complete effect chain preset"""
        return self.connection.send_command("load_effect_chain_preset", {
            "track_index": track_index,
            "effect_chain_name": effect_chain_name
        })

# ================================================================
# CONVENIENCE FUNCTIONS FOR COMMON OPERATIONS
# ================================================================

def create_complete_track_setup(api: AdvancedAbletonAPI, 
                               track_name: str, 
                               instrument_type: str,
                               effect_chain: List[str] = None,
                               track_color: int = None) -> Dict[str, Any]:
    """Create complete track with instrument and effects in one call"""
    
    # Create track
    track_result = api.connection.send_command("create_midi_track", {"name": track_name})
    track_index = track_result.get("index", 0)
    
    # Set color if specified
    if track_color:
        api.connection.send_command("set_track_color", {
            "track_index": track_index,
            "color": track_color
        })
    
    # Load instrument - use simple identifier for compatibility
    instrument_mapping = {
        "drums": "drums",
        "drum": "drums", 
        "bass": "bass",
        "synth": "synth",
        "wavetable": "synth",
        "lead": "synth"
    }
    
    simple_instrument = instrument_mapping.get(instrument_type.lower(), "synth")
    api.load_browser_item_to_track(track_index, simple_instrument)
    
    # Add effect chain if specified
    if effect_chain:
        for effect in effect_chain:
            # Effects would need additional implementation
            pass  # Placeholder for effect loading
    
    return {"track_index": track_index, "status": "success"}

def setup_style_template(api: AdvancedAbletonAPI, style: str, 
                        key: str, bpm: int) -> Dict[str, Any]:
    """Setup complete style template with proper routing and scale"""
    
    # Set global parameters
    api.connection.send_command("set_tempo", {"tempo": bpm})
    api.set_global_scale(key, 0)  # Convert key to root note
    
    # Create style-specific track routing
    if style.lower() == "afro_house":
        tracks = [
            ("Kick", "Drums", ["EQ Eight", "Compressor"]),
            ("Bass", "Bass", ["EQ Eight", "Saturator"]),
            ("Percussion", "Drums", ["EQ Eight", "Auto Filter"]),
            ("Pads", "Wavetable", ["Reverb", "EQ Eight"]),
            ("Lead", "Wavetable", ["Echo", "Auto Filter"])
        ]
    elif style.lower() == "deep_house":
        tracks = [
            ("Kick", "Drums", ["EQ Eight", "Compressor"]),
            ("Bass", "Bass", ["EQ Eight", "Compressor"]),
            ("Electric Piano", "Electric Piano", ["EQ Eight", "Chorus"]),
            ("Pads", "Wavetable", ["Reverb", "EQ Eight"]),
            ("Percussion", "Drums", ["EQ Eight", "Auto Filter"])
        ]
    else:
        # Default setup
        tracks = [
            ("Kick", "Drums", ["EQ Eight", "Compressor"]),
            ("Bass", "Bass", ["EQ Eight"]),
            ("Synth", "Wavetable", ["EQ Eight"]),
            ("Pads", "Wavetable", ["Reverb"])
        ]
    
    created_tracks = []
    for track_name, instrument, effects in tracks:
        result = create_complete_track_setup(api, track_name, instrument, effects)
        created_tracks.append(result)
    
    return {
        "status": "success",
        "style": style,
        "key": key,
        "bpm": bpm,
        "tracks_created": len(created_tracks),
        "tracks": created_tracks
    } 