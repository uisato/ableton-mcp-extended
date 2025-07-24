"""
Scale Constraint System - Ableton Scale Instrument Integration

This system integrates with Ableton Live's Scale instrument to provide automatic
scale locking and constraint enforcement across all AI-generated musical content.

Key features:
- Automatic Scale instrument setup and configuration
- Real-time scale constraint validation
- MIDI note filtering and correction
- Scale-aware chord progression generation
- Harmonic consistency enforcement
- Multiple scale and mode support

This ensures all generated content remains musically coherent and in the correct scale.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import music21 as m21

logger = logging.getLogger(__name__)

class ScaleType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"
    LYDIAN = "lydian"
    MIXOLYDIAN = "mixolydian"
    AEOLIAN = "aeolian"
    LOCRIAN = "locrian"
    HARMONIC_MINOR = "harmonic_minor"
    MELODIC_MINOR = "melodic_minor"
    BLUES = "blues"
    PENTATONIC_MAJOR = "pentatonic_major"
    PENTATONIC_MINOR = "pentatonic_minor"

class ChordType(Enum):
    TRIAD = "triad"
    SEVENTH = "seventh"
    NINTH = "ninth"
    ELEVENTH = "eleventh"
    THIRTEENTH = "thirteenth"
    SUS2 = "sus2"
    SUS4 = "sus4"
    ADD9 = "add9"

@dataclass
class ScaleDefinition:
    """Definition of a musical scale"""
    name: str
    intervals: List[int]  # Semitone intervals from root
    characteristic_chords: List[str]
    tensions: List[int]  # Available tension notes
    avoid_notes: List[int]  # Notes to avoid in this scale

@dataclass
class ScaleConstraint:
    """Scale constraint configuration"""
    root_note: str
    scale_type: ScaleType
    allowed_notes: Set[int]  # MIDI note numbers (mod 12)
    allowed_chords: List[str]
    chord_functions: Dict[int, str]  # Scale degree -> function
    voice_leading_rules: Dict[str, Any]

class ScaleConstraintSystem:
    """Manages scale constraints and Ableton Scale instrument integration"""
    
    def __init__(self):
        self.current_constraint: Optional[ScaleConstraint] = None
        self.scale_definitions = self._initialize_scale_definitions()
        self.ableton_scale_device_id: Optional[str] = None
        
    def _initialize_scale_definitions(self) -> Dict[ScaleType, ScaleDefinition]:
        """Initialize comprehensive scale definitions"""
        return {
            ScaleType.MAJOR: ScaleDefinition(
                name="Major",
                intervals=[0, 2, 4, 5, 7, 9, 11],
                characteristic_chords=["I", "ii", "iii", "IV", "V", "vi", "vii°"],
                tensions=[9, 11, 13],
                avoid_notes=[4]  # Avoid 4th in major scale contexts
            ),
            ScaleType.MINOR: ScaleDefinition(
                name="Natural Minor",
                intervals=[0, 2, 3, 5, 7, 8, 10],
                characteristic_chords=["i", "ii°", "♭III", "iv", "v", "♭VI", "♭VII"],
                tensions=[9, 11],
                avoid_notes=[2]  # Avoid 2nd in minor contexts
            ),
            ScaleType.DORIAN: ScaleDefinition(
                name="Dorian",
                intervals=[0, 2, 3, 5, 7, 9, 10],
                characteristic_chords=["i", "ii", "♭III", "IV", "v", "vi°", "♭VII"],
                tensions=[9, 11, 13],
                avoid_notes=[]
            ),
            ScaleType.HARMONIC_MINOR: ScaleDefinition(
                name="Harmonic Minor",
                intervals=[0, 2, 3, 5, 7, 8, 11],
                characteristic_chords=["i", "ii°", "♭III+", "iv", "V", "♭VI", "vii°"],
                tensions=[9, 11],
                avoid_notes=[2, 6]
            ),
            ScaleType.BLUES: ScaleDefinition(
                name="Blues",
                intervals=[0, 3, 5, 6, 7, 10],
                characteristic_chords=["I7", "♭III", "IV7", "♭V", "V7", "♭VII"],
                tensions=[9, 11, 13],
                avoid_notes=[]
            ),
            ScaleType.PENTATONIC_MAJOR: ScaleDefinition(
                name="Major Pentatonic",
                intervals=[0, 2, 4, 7, 9],
                characteristic_chords=["I", "ii", "iii", "V", "vi"],
                tensions=[9],
                avoid_notes=[4, 11]  # Avoid 4th and 7th
            ),
            ScaleType.PENTATONIC_MINOR: ScaleDefinition(
                name="Minor Pentatonic",
                intervals=[0, 3, 5, 7, 10],
                characteristic_chords=["i", "♭III", "iv", "v", "♭VII"],
                tensions=[11],
                avoid_notes=[2, 6]  # Avoid 2nd and 6th
            )
        }
        
    def setup_scale_constraint(self, root_note: str, scale_type: ScaleType) -> ScaleConstraint:
        """Setup scale constraint for the session"""
        logger.info(f"Setting up scale constraint: {root_note} {scale_type.value}")
        
        # Get scale definition
        scale_def = self.scale_definitions[scale_type]
        
        # Calculate root note MIDI number
        root_midi = self._note_name_to_midi(root_note) % 12
        
        # Calculate allowed notes
        allowed_notes = {(root_midi + interval) % 12 for interval in scale_def.intervals}
        
        # Generate chord functions
        chord_functions = self._generate_chord_functions(scale_type, root_note)
        
        # Create scale constraint
        constraint = ScaleConstraint(
            root_note=root_note,
            scale_type=scale_type,
            allowed_notes=allowed_notes,
            allowed_chords=self._generate_allowed_chords(root_note, scale_def),
            chord_functions=chord_functions,
            voice_leading_rules=self._get_voice_leading_rules(scale_type)
        )
        
        self.current_constraint = constraint
        return constraint
        
    def _note_name_to_midi(self, note_name: str) -> int:
        """Convert note name to MIDI number"""
        note_map = {
            'C': 60, 'C#': 61, 'Db': 61, 'D': 62, 'D#': 63, 'Eb': 63,
            'E': 64, 'F': 65, 'F#': 66, 'Gb': 66, 'G': 67, 'G#': 68,
            'Ab': 68, 'A': 69, 'A#': 70, 'Bb': 70, 'B': 71
        }
        
        # Handle different octaves and formats
        base_note = note_name.replace('♭', 'b').replace('♯', '#')
        
        # Extract octave if present
        octave = 4  # Default to middle C octave
        if base_note[-1].isdigit():
            octave = int(base_note[-1])
            base_note = base_note[:-1]
            
        base_midi = note_map.get(base_note, 60)
        return base_midi + (octave - 4) * 12
        
    def _generate_chord_functions(self, scale_type: ScaleType, root_note: str) -> Dict[int, str]:
        """Generate chord functions for scale degrees"""
        if scale_type == ScaleType.MAJOR:
            return {
                0: "I",    # Tonic
                1: "ii",   # Supertonic
                2: "iii",  # Mediant
                3: "IV",   # Subdominant
                4: "V",    # Dominant
                5: "vi",   # Submediant
                6: "vii°"  # Leading tone
            }
        elif scale_type in [ScaleType.MINOR, ScaleType.AEOLIAN]:
            return {
                0: "i",    # Tonic
                1: "ii°",  # Supertonic
                2: "♭III", # Mediant
                3: "iv",   # Subdominant
                4: "v",    # Dominant
                5: "♭VI",  # Submediant
                6: "♭VII"  # Subtonic
            }
        elif scale_type == ScaleType.DORIAN:
            return {
                0: "i",    # Tonic
                1: "ii",   # Supertonic
                2: "♭III", # Mediant
                3: "IV",   # Subdominant
                4: "v",    # Dominant
                5: "vi°",  # Submediant
                6: "♭VII"  # Subtonic
            }
        else:
            # Default chord functions
            return {i: f"chord_{i}" for i in range(7)}
            
    def _generate_allowed_chords(self, root_note: str, scale_def: ScaleDefinition) -> List[str]:
        """Generate list of allowed chords in the scale"""
        root_midi = self._note_name_to_midi(root_note) % 12
        allowed_chords = []
        
        # Generate triads for each scale degree
        for i, interval in enumerate(scale_def.intervals):
            chord_root = (root_midi + interval) % 12
            chord_root_name = self._midi_to_note_name(chord_root)
            
            # Determine chord quality based on scale intervals
            third_interval = scale_def.intervals[(i + 2) % len(scale_def.intervals)]
            fifth_interval = scale_def.intervals[(i + 4) % len(scale_def.intervals)]
            
            third_semitones = (third_interval - interval) % 12
            fifth_semitones = (fifth_interval - interval) % 12
            
            # Determine chord type
            if third_semitones == 4 and fifth_semitones == 7:
                chord_type = ""  # Major
            elif third_semitones == 3 and fifth_semitones == 7:
                chord_type = "m"  # Minor
            elif third_semitones == 3 and fifth_semitones == 6:
                chord_type = "dim"  # Diminished
            elif third_semitones == 4 and fifth_semitones == 8:
                chord_type = "aug"  # Augmented
            else:
                chord_type = ""  # Default to major
                
            allowed_chords.append(f"{chord_root_name}{chord_type}")
            
        return allowed_chords
        
    def _midi_to_note_name(self, midi_note: int) -> str:
        """Convert MIDI note number to note name"""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return note_names[midi_note % 12]
        
    def _get_voice_leading_rules(self, scale_type: ScaleType) -> Dict[str, Any]:
        """Get voice leading rules for the scale type"""
        return {
            "max_leap": 7,  # Maximum interval leap in semitones
            "prefer_stepwise": True,
            "avoid_parallel_fifths": True,
            "avoid_parallel_octaves": True,
            "leading_tone_resolution": scale_type in [ScaleType.MAJOR, ScaleType.HARMONIC_MINOR],
            "chord_tone_emphasis": True
        }
        
    def validate_notes(self, notes: List[int]) -> Dict[str, Any]:
        """Validate a list of MIDI notes against current scale constraint"""
        if not self.current_constraint:
            return {"valid": True, "violations": [], "corrections": []}
            
        violations = []
        corrections = []
        
        for note in notes:
            note_class = note % 12
            if note_class not in self.current_constraint.allowed_notes:
                violations.append({
                    "note": note,
                    "note_class": note_class,
                    "reason": f"Note {self._midi_to_note_name(note_class)} not in {self.current_constraint.scale_type.value} scale"
                })
                
                # Find closest allowed note
                closest_note = self._find_closest_allowed_note(note_class)
                corrections.append({
                    "original": note,
                    "corrected": (note // 12) * 12 + closest_note,
                    "reason": f"Corrected to {self._midi_to_note_name(closest_note)}"
                })
                
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "corrections": corrections,
            "scale_info": {
                "root": self.current_constraint.root_note,
                "scale": self.current_constraint.scale_type.value,
                "allowed_notes": [self._midi_to_note_name(n) for n in sorted(self.current_constraint.allowed_notes)]
            }
        }
        
    def _find_closest_allowed_note(self, note_class: int) -> int:
        """Find the closest allowed note to the given note class"""
        if not self.current_constraint:
            return note_class
            
        allowed = list(self.current_constraint.allowed_notes)
        distances = [(abs(note_class - allowed_note), allowed_note) for allowed_note in allowed]
        distances.extend([(abs(note_class - (allowed_note + 12)), allowed_note) for allowed_note in allowed])
        distances.extend([(abs(note_class - (allowed_note - 12)), allowed_note) for allowed_note in allowed])
        
        distances.sort()
        return distances[0][1] % 12
        
    def correct_melody(self, melody: List[int]) -> List[int]:
        """Correct a melody to fit the current scale constraint"""
        if not self.current_constraint:
            return melody
            
        corrected = []
        for note in melody:
            note_class = note % 12
            if note_class in self.current_constraint.allowed_notes:
                corrected.append(note)
            else:
                closest = self._find_closest_allowed_note(note_class)
                corrected_note = (note // 12) * 12 + closest
                corrected.append(corrected_note)
                
        return corrected
        
    def generate_chord_progression(self, progression_pattern: List[int], length_bars: int = 4) -> List[Dict[str, Any]]:
        """Generate a chord progression following scale constraints"""
        if not self.current_constraint:
            return []
            
        progression = []
        scale_def = self.scale_definitions[self.current_constraint.scale_type]
        
        for i, degree in enumerate(progression_pattern):
            # Get chord root from scale degree
            degree_index = degree % len(scale_def.intervals)
            chord_interval = scale_def.intervals[degree_index]
            root_midi = self._note_name_to_midi(self.current_constraint.root_note)
            chord_root = (root_midi + chord_interval) % 12
            chord_root_name = self._midi_to_note_name(chord_root)
            
            # Get chord function
            chord_function = self.current_constraint.chord_functions.get(degree_index, "unknown")
            
            # Generate chord
            chord = {
                "root": chord_root_name,
                "function": chord_function,
                "degree": degree + 1,
                "notes": self._generate_chord_notes(chord_root, degree_index),
                "bar": (i % length_bars) + 1,
                "beat": 1  # Simplified - place on beat 1
            }
            
            progression.append(chord)
            
        return progression
        
    def _generate_chord_notes(self, root: int, degree_index: int) -> List[int]:
        """Generate notes for a chord based on scale degree"""
        if not self.current_constraint:
            return [root, root + 4, root + 7]  # Default major triad
            
        scale_def = self.scale_definitions[self.current_constraint.scale_type]
        intervals = scale_def.intervals
        
        # Get third and fifth from scale
        third_index = (degree_index + 2) % len(intervals)
        fifth_index = (degree_index + 4) % len(intervals)
        
        third = (root + intervals[third_index]) % 12
        fifth = (root + intervals[fifth_index]) % 12
        
        # Convert to actual MIDI notes (middle octave)
        base_octave = 60  # Middle C
        chord_notes = [
            base_octave + root,
            base_octave + third,
            base_octave + fifth
        ]
        
        return chord_notes
        
    def get_scale_instrument_config(self) -> Dict[str, Any]:
        """Get configuration for Ableton's Scale instrument"""
        if not self.current_constraint:
            return {}
            
        # Map our scale types to Ableton Scale instrument parameters
        scale_map = {
            ScaleType.MAJOR: {"scale": 0, "base": 0},  # Major scale
            ScaleType.MINOR: {"scale": 5, "base": 0},  # Natural Minor
            ScaleType.DORIAN: {"scale": 1, "base": 0}, # Dorian
            ScaleType.PHRYGIAN: {"scale": 2, "base": 0}, # Phrygian
            ScaleType.LYDIAN: {"scale": 3, "base": 0}, # Lydian
            ScaleType.MIXOLYDIAN: {"scale": 4, "base": 0}, # Mixolydian
            ScaleType.HARMONIC_MINOR: {"scale": 8, "base": 0}, # Harmonic Minor
            ScaleType.BLUES: {"scale": 16, "base": 0}, # Blues
            ScaleType.PENTATONIC_MAJOR: {"scale": 17, "base": 0}, # Major Pentatonic
            ScaleType.PENTATONIC_MINOR: {"scale": 18, "base": 0}  # Minor Pentatonic
        }
        
        root_midi = self._note_name_to_midi(self.current_constraint.root_note) % 12
        scale_config = scale_map.get(self.current_constraint.scale_type, {"scale": 0, "base": 0})
        
        return {
            "device_name": "Scale",
            "parameters": {
                "Base": root_midi,  # Root note
                "Scale": scale_config["scale"],  # Scale type
                "Range": 127,  # Full range
                "Lowest": 0,   # Lowest note
                "Highest": 127, # Highest note
                "Fold": 1,     # Enable note folding
                "Layout": 0    # Chromatic layout
            }
        }
        
    def create_ableton_scale_device_command(self) -> Dict[str, Any]:
        """Create command to set up Scale device in Ableton Live"""
        config = self.get_scale_instrument_config()
        
        return {
            "action": "create_scale_device",
            "track_index": 0,  # Master track or specific track
            "device_config": config,
            "enable_constraint": True,
            "bypass": False
        }
        
    def get_constraint_summary(self) -> Dict[str, Any]:
        """Get summary of current scale constraint"""
        if not self.current_constraint:
            return {"active": False}
            
        return {
            "active": True,
            "root_note": self.current_constraint.root_note,
            "scale_type": self.current_constraint.scale_type.value,
            "allowed_notes": [self._midi_to_note_name(n) for n in sorted(self.current_constraint.allowed_notes)],
            "allowed_chords": self.current_constraint.allowed_chords[:8],  # First 8 chords
            "chord_functions": {str(k): v for k, v in self.current_constraint.chord_functions.items()},
            "scale_definition": {
                "intervals": self.scale_definitions[self.current_constraint.scale_type].intervals,
                "characteristic_chords": self.scale_definitions[self.current_constraint.scale_type].characteristic_chords
            }
        }
        
    def apply_scale_constraint_to_midi(self, midi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply scale constraint to MIDI data before sending to Ableton"""
        if not self.current_constraint:
            return midi_data
            
        corrected_midi = midi_data.copy()
        
        # Process notes in MIDI data
        if "notes" in midi_data:
            corrected_notes = []
            for note in midi_data["notes"]:
                if isinstance(note, dict) and "pitch" in note:
                    original_pitch = note["pitch"]
                    corrected_pitch = self._find_closest_allowed_note(original_pitch % 12)
                    corrected_pitch = (original_pitch // 12) * 12 + corrected_pitch
                    
                    corrected_note = note.copy()
                    corrected_note["pitch"] = corrected_pitch
                    corrected_notes.append(corrected_note)
                else:
                    corrected_notes.append(note)
                    
            corrected_midi["notes"] = corrected_notes
            
        return corrected_midi 