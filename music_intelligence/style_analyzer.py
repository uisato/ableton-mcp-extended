"""
Style Analyzer - Deep Music Style Understanding

This class provides comprehensive analysis and understanding of musical styles,
genres, and artist signatures for AI music generation.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class StyleCharacteristics:
    """Structured representation of a musical style"""
    bpm_range: Tuple[int, int]
    key_preferences: List[str]
    chord_progressions: List[List[str]]
    rhythmic_patterns: Dict[str, str]
    sound_palette: Dict[str, str]
    arrangement_style: Dict[str, Any]
    signature_techniques: List[str]
    energy_curve: str
    common_instruments: List[str]


class StyleAnalyzer:
    """
    Deep analysis of musical styles and artist signatures
    
    This class contains comprehensive knowledge about:
    - Genre characteristics
    - Artist-specific production styles
    - Harmonic patterns and preferences
    - Rhythmic signatures
    - Sound design approaches
    """
    
    def __init__(self):
        """Initialize the style analyzer with comprehensive style database"""
        self.style_database = self._initialize_style_database()
        logger.info(f"StyleAnalyzer initialized with {len(self.style_database)} styles")
    
    def _initialize_style_database(self) -> Dict[str, StyleCharacteristics]:
        """Initialize comprehensive style database"""
        
        styles = {
            # AFRO HOUSE
            "afro_house": StyleCharacteristics(
                bpm_range=(120, 126),
                key_preferences=["Am", "Dm", "Gm", "Em", "Cm", "Fm"],
                chord_progressions=[
                    ["Am", "F", "C", "G"],
                    ["Dm", "Am", "F", "C"],
                    ["Em", "C", "G", "D"],
                    ["Cm", "Ab", "Bb", "F"],
                    ["Am", "Dm", "G", "C"]
                ],
                rhythmic_patterns={
                    "kick": "four_on_floor_with_syncopated_accents",
                    "percussion": "african_polyrhythm_layers",
                    "hi_hats": "off_beat_emphasis_with_rolls",
                    "snare": "deep_organic_on_beats_2_and_4"
                },
                sound_palette={
                    "bass": "warm_sub_heavy_melodic",
                    "leads": "organic_plucks_and_mallets",
                    "pads": "atmospheric_warm_strings",
                    "percussion": "ethnic_organic_layers",
                    "vocals": "soulful_chopped_phrases"
                },
                arrangement_style={
                    "intro_length": 32,
                    "breakdown_style": "gradual_filter_sweeps",
                    "build_techniques": ["percussion_layers", "harmonic_tension", "vocal_builds"],
                    "drop_style": "emotional_release_with_full_percussion",
                    "transition_style": "organic_flowing"
                },
                signature_techniques=[
                    "vocal_chops_as_percussion",
                    "long_atmospheric_intros",
                    "organic_percussion_layers",
                    "melodic_bass_movements",
                    "traditional_african_instruments"
                ],
                energy_curve="gradual_build_emotional_peaks",
                common_instruments=["kalimba", "djembe", "shakers", "vocal_chops", "organic_bass"]
            ),
            
            # DEEP HOUSE
            "deep_house": StyleCharacteristics(
                bpm_range=(120, 125),
                key_preferences=["Am", "Fm", "Cm", "Dm", "Gm"],
                chord_progressions=[
                    ["Am", "F", "C", "G"],
                    ["Fm", "Cm", "Ab", "Bb"],
                    ["Dm", "Bb", "F", "C"],
                    ["Cm", "Fm", "Bb", "Eb"]
                ],
                rhythmic_patterns={
                    "kick": "four_on_floor_subtle_swing",
                    "percussion": "minimal_sophisticated",
                    "hi_hats": "subtle_shuffle_groove",
                    "snare": "deep_soft_on_2_and_4"
                },
                sound_palette={
                    "bass": "deep_analog_warm",
                    "leads": "subtle_filtered_sounds",
                    "pads": "lush_vintage_strings",
                    "percussion": "vinyl_warmth",
                    "vocals": "soulful_deep_processing"
                },
                arrangement_style={
                    "intro_length": 24,
                    "breakdown_style": "filter_sweeps_echo",
                    "build_techniques": ["subtle_percussion_adds", "filter_opening"],
                    "drop_style": "smooth_transition",
                    "transition_style": "seamless_dj_friendly"
                },
                signature_techniques=[
                    "vintage_vinyl_warmth",
                    "subtle_swing_groove",
                    "jazz_influenced_chords",
                    "analog_filter_sweeps",
                    "soulful_vocal_samples"
                ],
                energy_curve="steady_hypnotic_groove",
                common_instruments=["analog_bass", "vintage_keys", "vinyl_samples", "jazz_guitars"]
            ),
            
            # KEINEMUSIK STYLE (Sophisticated Deep House)
            "keinemusik": StyleCharacteristics(
                bpm_range=(120, 124),
                key_preferences=["Am", "Dm", "Em", "Fm"],
                chord_progressions=[
                    ["Am", "Em", "F", "G"],
                    ["Dm", "Am", "Bb", "F"],
                    ["Em", "Am", "D", "G"],
                    ["Fm", "Cm", "Ab", "Eb"]
                ],
                rhythmic_patterns={
                    "kick": "four_on_floor_sophisticated",
                    "percussion": "organic_minimal_precise",
                    "hi_hats": "crisp_precise_groove",
                    "snare": "organic_woody_character"
                },
                sound_palette={
                    "bass": "melodic_analog_character",
                    "leads": "vintage_electric_pianos",
                    "pads": "atmospheric_sophisticated",
                    "percussion": "organic_acoustic_blend",
                    "vocals": "processed_emotional_snippets"
                },
                arrangement_style={
                    "intro_length": 32,
                    "breakdown_style": "sophisticated_filter_work",
                    "build_techniques": ["harmonic_layering", "percussion_sophistication"],
                    "drop_style": "sophisticated_release",
                    "transition_style": "musical_narrative"
                },
                signature_techniques=[
                    "vintage_electric_piano_chords",
                    "sophisticated_harmonic_progressions",
                    "organic_percussion_blend",
                    "emotional_musical_storytelling",
                    "analog_warmth_precision"
                ],
                energy_curve="sophisticated_emotional_journey",
                common_instruments=["electric_piano", "analog_bass", "organic_percussion", "vintage_synths"]
            ),
            
            # PROGRESSIVE HOUSE
            "progressive_house": StyleCharacteristics(
                bpm_range=(128, 132),
                key_preferences=["Am", "Em", "Bm", "F#m", "Cm"],
                chord_progressions=[
                    ["Am", "F", "C", "G"],
                    ["Em", "C", "G", "D"],
                    ["Bm", "G", "D", "A"],
                    ["F#m", "D", "A", "E"]
                ],
                rhythmic_patterns={
                    "kick": "four_on_floor_driving",
                    "percussion": "layered_rhythmic_complexity",
                    "hi_hats": "sixteenth_note_drive",
                    "snare": "tight_punchy_layers"
                },
                sound_palette={
                    "bass": "powerful_analog_lead",
                    "leads": "soaring_epic_synths",
                    "pads": "cinematic_sweeping",
                    "percussion": "driving_rhythmic",
                    "vocals": "euphoric_anthemic"
                },
                arrangement_style={
                    "intro_length": 48,
                    "breakdown_style": "epic_filter_breakdowns",
                    "build_techniques": ["layered_percussion", "harmonic_rises", "white_noise_builds"],
                    "drop_style": "euphoric_explosive_release",
                    "transition_style": "epic_cinematic"
                },
                signature_techniques=[
                    "epic_breakdown_builds",
                    "soaring_lead_synths",
                    "cinematic_arrangement",
                    "euphoric_drops",
                    "long_form_musical_journeys"
                ],
                energy_curve="epic_emotional_rollercoaster",
                common_instruments=["analog_lead", "epic_pads", "white_noise", "orchestral_elements"]
            ),
            
            # TECH HOUSE
            "tech_house": StyleCharacteristics(
                bpm_range=(126, 130),
                key_preferences=["Am", "Em", "Dm", "Gm"],
                chord_progressions=[
                    ["Am", "Em", "F", "G"],
                    ["Dm", "Am", "Bb", "F"],
                    ["Em", "Bm", "C", "G"],
                    ["Gm", "Dm", "Eb", "Bb"]
                ],
                rhythmic_patterns={
                    "kick": "punchy_tech_house_groove",
                    "percussion": "tribal_tech_elements",
                    "hi_hats": "crisp_tech_precision",
                    "snare": "tight_tech_snap"
                },
                sound_palette={
                    "bass": "punchy_analog_growl",
                    "leads": "tech_stabs_and_riffs",
                    "pads": "dark_atmospheric",
                    "percussion": "tribal_tech_blend",
                    "vocals": "processed_tech_vocal_chops"
                },
                arrangement_style={
                    "intro_length": 16,
                    "breakdown_style": "filter_sweeps_vocal_chops",
                    "build_techniques": ["percussion_drops", "filter_automation"],
                    "drop_style": "punchy_tech_impact",
                    "transition_style": "dj_tool_friendly"
                },
                signature_techniques=[
                    "tribal_percussion_elements",
                    "analog_bass_growls",
                    "vocal_chop_processing",
                    "filter_automation_sweeps",
                    "tech_house_groove_pocket"
                ],
                energy_curve="steady_dancefloor_energy",
                common_instruments=["analog_bass", "tech_stabs", "tribal_percussion", "vocal_chops"]
            )
        }
        
        return styles
    
    def get_style_characteristics(self, style: str) -> StyleCharacteristics:
        """
        Get comprehensive characteristics for a musical style
        
        Args:
            style: Style name (case insensitive)
            
        Returns:
            StyleCharacteristics object with detailed style information
        """
        # Normalize style name
        style_key = style.lower().replace(" ", "_").replace("-", "_")
        
        # Check exact match first
        if style_key in self.style_database:
            return self.style_database[style_key]
        
        # Check for partial matches
        for key in self.style_database.keys():
            if style_key in key or key in style_key:
                logger.info(f"Found partial match: {style_key} -> {key}")
                return self.style_database[key]
        
        # Default to deep house if no match found
        logger.warning(f"Style '{style}' not found, defaulting to deep_house")
        return self.style_database["deep_house"]
    
    def analyze_artist_style(self, artist_name: str) -> StyleCharacteristics:
        """
        Analyze and return style characteristics based on artist reference
        
        Args:
            artist_name: Name of the artist to analyze
            
        Returns:
            StyleCharacteristics for the artist's style
        """
        # Artist-to-style mapping
        artist_mapping = {
            # Afro House Artists
            "black_coffee": "afro_house",
            "black coffee": "afro_house", 
            "dj black coffee": "afro_house",
            "atjazz": "afro_house",
            "boddhi satva": "afro_house",
            "culoe de song": "afro_house",
            
            # Keinemusik Artists
            "keinemusik": "keinemusik",
            "rampa": "keinemusik",
            "adam port": "keinemusik",
            "&me": "keinemusik",
            "reznik": "keinemusik",
            
            # Deep House Artists
            "dixon": "deep_house",
            "âme": "deep_house",
            "innervisions": "deep_house",
            "solomun": "deep_house",
            "tale of us": "deep_house",
            "maceo plex": "deep_house",
            
            # Progressive House Artists
            "eric prydz": "progressive_house",
            "deadmau5": "progressive_house",
            "above & beyond": "progressive_house",
            "armin van buuren": "progressive_house",
            
            # Tech House Artists
            "jamie jones": "tech_house",
            "hot since 82": "tech_house",
            "carl cox": "tech_house",
            "marco carola": "tech_house"
        }
        
        # Normalize artist name
        artist_key = artist_name.lower().strip()
        
        # Find matching style
        if artist_key in artist_mapping:
            style = artist_mapping[artist_key]
            logger.info(f"Mapped artist '{artist_name}' to style '{style}'")
            return self.get_style_characteristics(style)
        
        # Check for partial artist name matches
        for artist, style in artist_mapping.items():
            if artist in artist_key or artist_key in artist:
                logger.info(f"Found partial artist match: '{artist_name}' -> '{artist}' -> '{style}'")
                return self.get_style_characteristics(style)
        
        # Default to deep house for unknown artists
        logger.warning(f"Artist '{artist_name}' not found in database, defaulting to deep_house")
        return self.get_style_characteristics("deep_house")
    
    def get_compatible_styles(self, base_style: str) -> List[str]:
        """
        Get list of styles that are compatible/similar to the base style
        
        Args:
            base_style: Base style to find compatibles for
            
        Returns:
            List of compatible style names
        """
        compatibility_map = {
            "afro_house": ["deep_house", "tech_house"],
            "deep_house": ["afro_house", "keinemusik", "tech_house"],
            "keinemusik": ["deep_house", "afro_house"],
            "progressive_house": ["tech_house", "deep_house"],
            "tech_house": ["deep_house", "afro_house", "progressive_house"]
        }
        
        base_key = base_style.lower().replace(" ", "_")
        return compatibility_map.get(base_key, ["deep_house"])
    
    def suggest_chord_progression(self, style: str, key: str) -> List[str]:
        """
        Suggest an appropriate chord progression for style and key
        
        Args:
            style: Musical style
            key: Musical key
            
        Returns:
            List of chord names
        """
        characteristics = self.get_style_characteristics(style)
        
        # Find progressions that work with the given key
        suitable_progressions = []
        
        for progression in characteristics.chord_progressions:
            if any(chord.startswith(key[0]) for chord in progression):
                suitable_progressions.append(progression)
        
        if suitable_progressions:
            return suitable_progressions[0]  # Return first suitable
        else:
            return characteristics.chord_progressions[0]  # Return first available
    
    def get_recommended_bpm(self, style: str, energy_level: str = "medium") -> int:
        """
        Get recommended BPM for style and energy level
        
        Args:
            style: Musical style
            energy_level: "low", "medium", "high"
            
        Returns:
            Recommended BPM value
        """
        characteristics = self.get_style_characteristics(style)
        min_bpm, max_bpm = characteristics.bpm_range
        
        energy_multipliers = {
            "low": 0.0,     # Use minimum BPM
            "medium": 0.5,  # Use middle BPM
            "high": 1.0     # Use maximum BPM
        }
        
        multiplier = energy_multipliers.get(energy_level, 0.5)
        recommended_bpm = int(min_bpm + (max_bpm - min_bpm) * multiplier)
        
        return recommended_bpm
    
    def create_style_prompt(self, user_request: str, style: str) -> str:
        """
        Generate a comprehensive Gemini prompt for style-specific decisions
        
        Args:
            user_request: Original user request
            style: Identified musical style
            
        Returns:
            Detailed prompt for Gemini with style context
        """
        characteristics = self.get_style_characteristics(style)
        
        prompt = f"""
        You are an expert {style.replace('_', ' ').title()} producer. The user wants: "{user_request}"
        
        Style Characteristics for {style.replace('_', ' ').title()}:
        - BPM Range: {characteristics.bpm_range[0]}-{characteristics.bpm_range[1]}
        - Preferred Keys: {', '.join(characteristics.key_preferences)}
        - Signature Techniques: {', '.join(characteristics.signature_techniques)}
        - Sound Palette: {', '.join([f"{k}: {v}" for k, v in characteristics.sound_palette.items()])}
        - Energy Curve: {characteristics.energy_curve}
        
        Create a detailed production plan that captures the authentic {style.replace('_', ' ')} sound.
        Focus on the specific techniques and characteristics that define this style.
        Include specific Ableton Live stock plugin recommendations and settings.
        """
        
        return prompt
    
    def export_style_database(self, file_path: str) -> None:
        """Export style database to JSON file"""
        # Convert StyleCharacteristics to dict for JSON serialization
        export_data = {}
        for style_name, characteristics in self.style_database.items():
            export_data[style_name] = {
                "bpm_range": characteristics.bpm_range,
                "key_preferences": characteristics.key_preferences,
                "chord_progressions": characteristics.chord_progressions,
                "rhythmic_patterns": characteristics.rhythmic_patterns,
                "sound_palette": characteristics.sound_palette,
                "arrangement_style": characteristics.arrangement_style,
                "signature_techniques": characteristics.signature_techniques,
                "energy_curve": characteristics.energy_curve,
                "common_instruments": characteristics.common_instruments
            }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Style database exported to {file_path}")
    
    def list_available_styles(self) -> List[str]:
        """Get list of all available styles"""
        return list(self.style_database.keys()) 