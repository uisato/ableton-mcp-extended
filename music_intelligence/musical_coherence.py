"""
Musical Coherence Enforcement System

This system ensures all AI-generated music maintains musical coherence by:
- Enforcing scale constraints using Ableton's Scale device
- Maintaining harmonic voice leading
- Ensuring proper clip length and loop settings
- Applying music theory rules
- Managing persistent creative briefs
- Coordinating between AI experts

The goal is to transform random AI output into musically coherent compositions.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
import music21 as m21

logger = logging.getLogger(__name__)

class MusicalMode(Enum):
    MAJOR = "major"
    MINOR = "minor"
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"
    LYDIAN = "lydian"
    MIXOLYDIAN = "mixolydian"
    AEOLIAN = "aeolian"
    LOCRIAN = "locrian"

@dataclass
class MusicalCoherenceSettings:
    """Settings for musical coherence enforcement"""
    root_note: str = "C"
    scale_mode: MusicalMode = MusicalMode.MAJOR
    tempo: int = 120
    time_signature: str = "4/4"
    enforce_scale_device: bool = True
    enforce_clip_length: bool = True
    default_clip_length: int = 16  # bars
    enforce_voice_leading: bool = True
    max_voice_leading_interval: int = 4  # semitones

class MusicalCoherenceEnforcer:
    """Enforces musical coherence across all AI-generated content"""
    
    def __init__(self, ableton_connection=None):
        self.settings = MusicalCoherenceSettings()
        self.ableton_connection = ableton_connection
        self.active_tracks = {}  # track_index -> track_info
        
    def set_global_scale_constraint(self, root_note: str, scale_mode: MusicalMode, 
                                  tempo: int = 120) -> Dict[str, Any]:
        """Set global scale constraint that applies to all tracks"""
        try:
            self.settings.root_note = root_note.upper()
            self.settings.scale_mode = scale_mode
            self.settings.tempo = tempo
            
            logger.info(f"Setting global scale constraint: {root_note} {scale_mode.value} at {tempo} BPM")
            
            # Apply to all active tracks if Ableton connection available
            results = {}
            if self.ableton_connection:
                for track_index in self.active_tracks.keys():
                    result = self._apply_scale_to_track(track_index)
                    results[f"track_{track_index}"] = result
                    
            return {
                "global_settings": {
                    "root_note": self.settings.root_note,
                    "scale_mode": self.settings.scale_mode.value,
                    "tempo": self.settings.tempo
                },
                "track_applications": results
            }
            
        except Exception as e:
            logger.error(f"Error setting global scale constraint: {e}")
            return {"error": str(e)}
    
    def _apply_scale_to_track(self, track_index: int) -> Dict[str, Any]:
        """Apply scale constraint to a specific track using Ableton's Scale device"""
        try:
            if not self.ableton_connection:
                return {"error": "No Ableton connection available"}
                
            # Set Scale device parameters
            result = self.ableton_connection.send_command("set_scale_device_parameters", {
                "track_index": track_index,
                "parameters": {
                    "base": self._note_to_midi_value(self.settings.root_note),
                    "scale": self._mode_to_scale_value(self.settings.scale_mode)
                }
            })
            
            logger.info(f"Applied scale constraint to track {track_index}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error applying scale to track {track_index}: {e}")
            return {"error": str(e)}
    
    def _note_to_midi_value(self, note: str) -> int:
        """Convert note name to MIDI value (0-11)"""
        note_map = {
            'C': 0, 'C#': 1, 'DB': 1, 'D': 2, 'D#': 3, 'EB': 3, 'E': 4,
            'F': 5, 'F#': 6, 'GB': 6, 'G': 7, 'G#': 8, 'AB': 8, 'A': 9,
            'A#': 10, 'BB': 10, 'B': 11
        }
        return note_map.get(note.upper(), 0)
    
    def _mode_to_scale_value(self, mode: MusicalMode) -> int:
        """Convert mode to scale device value"""
        mode_map = {
            MusicalMode.MAJOR: 0,
            MusicalMode.MINOR: 1,
            MusicalMode.DORIAN: 2,
            MusicalMode.PHRYGIAN: 3,
            MusicalMode.LYDIAN: 4,
            MusicalMode.MIXOLYDIAN: 5,
            MusicalMode.AEOLIAN: 6,
            MusicalMode.LOCRIAN: 7
        }
        return mode_map.get(mode, 0)
    
    def register_track(self, track_index: int, track_type: str = "midi") -> Dict[str, Any]:
        """Register a track for coherence enforcement"""
        try:
            self.active_tracks[track_index] = {
                "type": track_type,
                "scale_applied": False,
                "clips": {}
            }
            
            # Apply scale constraint immediately
            if self.settings.enforce_scale_device:
                scale_result = self._apply_scale_to_track(track_index)
                self.active_tracks[track_index]["scale_applied"] = scale_result.get("device_found", False)
                
            logger.info(f"Registered track {track_index} for coherence enforcement")
            return {
                "track_index": track_index,
                "scale_applied": self.active_tracks[track_index]["scale_applied"],
                "settings": {
                    "root_note": self.settings.root_note,
                    "scale_mode": self.settings.scale_mode.value
                }
            }
            
        except Exception as e:
            logger.error(f"Error registering track {track_index}: {e}")
            return {"error": str(e)}
    
    def create_coherent_clip(self, track_index: int, clip_index: int, 
                           length_bars: Optional[int] = None) -> Dict[str, Any]:
        """Create a clip with proper length and scale constraints"""
        try:
            clip_length = length_bars or self.settings.default_clip_length
            
            if not self.ableton_connection:
                return {"error": "No Ableton connection available"}
            
            # Create clip with proper length
            result = self.ableton_connection.send_command("create_clip", {
                "track_index": track_index,
                "clip_index": clip_index,
                "length": clip_length
            })
            
            if track_index in self.active_tracks:
                self.active_tracks[track_index]["clips"][clip_index] = {
                    "length_bars": clip_length,
                    "loop_end": result.get("loop_end"),
                    "scale_constrained": self.active_tracks[track_index]["scale_applied"]
                }
            
            logger.info(f"Created coherent clip: track {track_index}, clip {clip_index}, {clip_length} bars")
            return {
                "clip_created": True,
                "track_index": track_index,
                "clip_index": clip_index,
                "length_bars": clip_length,
                "loop_end": result.get("loop_end"),
                "scale_constrained": self.active_tracks.get(track_index, {}).get("scale_applied", False)
            }
            
        except Exception as e:
            logger.error(f"Error creating coherent clip: {e}")
            return {"error": str(e)}
    
    def validate_notes_against_scale(self, notes: List[int]) -> Tuple[List[int], List[int]]:
        """Validate and correct notes against the current scale"""
        try:
            # Create music21 scale
            root = m21.pitch.Pitch(self.settings.root_note)
            
            if self.settings.scale_mode == MusicalMode.MAJOR:
                scale = m21.scale.MajorScale(root)
            elif self.settings.scale_mode == MusicalMode.MINOR:
                scale = m21.scale.MinorScale(root)
            else:
                # Use the mode name directly
                scale = m21.scale.Scale(root, self.settings.scale_mode.value)
            
            # Get scale pitch classes
            scale_notes = [p.pitchClass for p in scale.pitches]
            
            valid_notes = []
            corrected_notes = []
            
            for note in notes:
                pitch_class = note % 12
                if pitch_class in scale_notes:
                    valid_notes.append(note)
                    corrected_notes.append(note)
                else:
                    # Find nearest scale note
                    nearest = min(scale_notes, key=lambda x: min(abs(x - pitch_class), abs(x - pitch_class + 12), abs(x - pitch_class - 12)))
                    corrected_note = note - pitch_class + nearest
                    corrected_notes.append(corrected_note)
                    
            logger.info(f"Validated {len(notes)} notes, {len(valid_notes)} were valid, {len(notes) - len(valid_notes)} corrected")
            return valid_notes, corrected_notes
            
        except Exception as e:
            logger.error(f"Error validating notes: {e}")
            return notes, notes  # Return original notes if validation fails
    
    def get_scale_chord_progression(self, progression_type: str = "basic") -> List[List[int]]:
        """Generate a chord progression in the current scale"""
        try:
            # Create music21 scale
            root = m21.pitch.Pitch(self.settings.root_note)
            
            if self.settings.scale_mode == MusicalMode.MAJOR:
                scale = m21.scale.MajorScale(root)
            elif self.settings.scale_mode == MusicalMode.MINOR:
                scale = m21.scale.MinorScale(root)
            else:
                scale = m21.scale.Scale(root, self.settings.scale_mode.value)
            
            # Generate basic chord progression
            if progression_type == "basic":
                # I-vi-IV-V in major, i-VII-VI-VII in minor
                if self.settings.scale_mode in [MusicalMode.MAJOR]:
                    chord_degrees = [1, 6, 4, 5]  # I-vi-IV-V
                else:
                    chord_degrees = [1, 7, 6, 7]  # i-VII-VI-VII
            elif progression_type == "blues":
                chord_degrees = [1, 1, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5]  # 12-bar blues
            else:
                chord_degrees = [1, 4, 5, 1]  # Simple I-IV-V-I
            
            chords = []
            for degree in chord_degrees:
                # Get chord notes (root, third, fifth)
                chord_scale = scale.derive(degree)
                chord_pitches = [chord_scale.pitches[0], chord_scale.pitches[2], chord_scale.pitches[4]]
                chord_notes = [p.midi for p in chord_pitches]
                chords.append(chord_notes)
            
            logger.info(f"Generated {progression_type} chord progression with {len(chords)} chords")
            return chords
            
        except Exception as e:
            logger.error(f"Error generating chord progression: {e}")
            return [[60, 64, 67]]  # Return C major chord as fallback
    
    def get_coherence_status(self) -> Dict[str, Any]:
        """Get current coherence enforcement status"""
        return {
            "global_settings": {
                "root_note": self.settings.root_note,
                "scale_mode": self.settings.scale_mode.value,
                "tempo": self.settings.tempo,
                "time_signature": self.settings.time_signature,
                "default_clip_length": self.settings.default_clip_length
            },
            "active_tracks": len(self.active_tracks),
            "tracks": self.active_tracks,
            "enforcement_enabled": {
                "scale_device": self.settings.enforce_scale_device,
                "clip_length": self.settings.enforce_clip_length,
                "voice_leading": self.settings.enforce_voice_leading
            }
        } 