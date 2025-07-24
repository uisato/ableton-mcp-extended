"""
Stock Plugin Expert - Master of Ableton Live's Stock Plugins

This class contains comprehensive knowledge of Ableton Live's stock plugins
and how to use them to create professional sounds for any genre.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PluginCategory(Enum):
    """Categories of Ableton Live stock plugins"""
    INSTRUMENT = "instrument"
    AUDIO_EFFECT = "audio_effect"
    MIDI_EFFECT = "midi_effect"
    

@dataclass
class PluginPreset:
    """A specific preset configuration for a plugin"""
    name: str
    plugin: str
    category: str
    settings: Dict[str, Any]
    description: str
    use_cases: List[str]


@dataclass
class EffectChain:
    """A complete effect chain for achieving specific sounds"""
    name: str
    description: str
    style_tags: List[str]
    effects: List[Dict[str, Any]]
    usage_notes: str


class StockPluginExpert:
    """
    Master of Ableton Live's stock plugins for professional sound design
    
    This class provides comprehensive knowledge about:
    - All stock instruments and their capabilities
    - Audio effects and their creative applications
    - Style-specific preset configurations
    - Effect chain templates for professional sounds
    - MIDI effects for enhanced creativity
    """
    
    def __init__(self):
        """Initialize the stock plugin expert"""
        self.instruments = self._initialize_instruments()
        self.audio_effects = self._initialize_audio_effects()
        self.midi_effects = self._initialize_midi_effects()
        self.preset_library = self._initialize_preset_library()
        self.effect_chains = self._initialize_effect_chains()
        
        logger.info("StockPluginExpert initialized with comprehensive plugin knowledge")
    
    def _initialize_instruments(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive instrument knowledge"""
        return {
            "Wavetable": {
                "description": "Advanced wavetable synthesizer",
                "strengths": ["leads", "bass", "pads", "arpeggios", "sound_design"],
                "style_suitability": ["progressive_house", "tech_house", "deep_house", "afro_house"],
                "key_features": ["wavetable_scanning", "dual_oscillators", "advanced_modulation"],
                "typical_usage": "Primary synthesizer for leads, bass, and textural elements",
                "preset_categories": {
                    "bass": ["deep_analog_bass", "punchy_tech_bass", "melodic_afro_bass"],
                    "lead": ["soaring_lead", "pluck_lead", "cutting_tech_lead"],
                    "pad": ["warm_strings", "atmospheric_pad", "evolving_texture"],
                    "arp": ["classic_arp", "rhythmic_sequence", "flowing_pattern"]
                }
            },
            
            "Operator": {
                "description": "FM synthesis powerhouse",
                "strengths": ["bass", "leads", "bells", "evolving_textures", "percussive_sounds"],
                "style_suitability": ["deep_house", "tech_house", "progressive_house"],
                "key_features": ["fm_synthesis", "four_operators", "flexible_routing"],
                "typical_usage": "Complex timbres, evolving sounds, and unique textures",
                "preset_categories": {
                    "bass": ["fm_bass", "woody_bass", "analog_bass"],
                    "lead": ["bright_lead", "bell_lead", "cutting_lead"],
                    "texture": ["evolving_pad", "metallic_texture", "organic_sound"],
                    "percussion": ["fm_kick", "metallic_perc", "synthetic_drums"]
                }
            },
            
            "Bass": {
                "description": "Dedicated bass synthesizer",
                "strengths": ["sub_bass", "analog_bass", "punchy_bass"],
                "style_suitability": ["afro_house", "deep_house", "tech_house"],
                "key_features": ["dual_oscillators", "analog_modeling", "bass_optimized"],
                "typical_usage": "Primary bass sounds with analog character",
                "preset_categories": {
                    "sub": ["deep_sub", "rolling_sub", "punchy_sub"],
                    "analog": ["vintage_bass", "warm_bass", "growling_bass"],
                    "modern": ["clean_bass", "punchy_bass", "melodic_bass"]
                }
            },
            
            "Impulse": {
                "description": "Drum sampler and synthesizer",
                "strengths": ["kicks", "snares", "hi_hats", "percussion", "drum_kits"],
                "style_suitability": ["all_electronic_genres"],
                "key_features": ["eight_slots", "synthesis_sampling", "individual_effects"],
                "typical_usage": "Complete drum programming and percussion",
                "preset_categories": {
                    "kicks": ["house_kick", "tech_kick", "deep_kick", "punchy_kick"],
                    "snares": ["analog_snare", "crisp_snare", "wooden_snare"],
                    "hats": ["classic_hats", "crisp_hats", "vintage_hats"],
                    "percussion": ["shaker", "tambourine", "conga", "ethnic_perc"]
                }
            },
            
            "Simpler": {
                "description": "Streamlined sampler",
                "strengths": ["vocal_chops", "one_shots", "simple_sampling"],
                "style_suitability": ["all_genres"],
                "key_features": ["drag_drop_sampling", "simple_interface", "quick_results"],
                "typical_usage": "Quick sampling and simple playback instruments",
                "preset_categories": {
                    "vocal": ["vocal_chop", "vocal_pad", "processed_vocal"],
                    "texture": ["atmospheric_texture", "rhythm_texture"],
                    "oneshot": ["impact", "riser", "downlifter"]
                }
            }
        }
    
    def _initialize_audio_effects(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive audio effects knowledge"""
        return {
            "EQ Eight": {
                "description": "8-band parametric equalizer",
                "primary_uses": ["corrective_eq", "creative_shaping", "frequency_splitting"],
                "style_techniques": {
                    "afro_house": ["warm_low_end", "open_highs", "midrange_clarity"],
                    "deep_house": ["vintage_warmth", "gentle_curves", "analog_character"],
                    "tech_house": ["punchy_lows", "crisp_highs", "midrange_cut"],
                    "progressive_house": ["wide_frequency_response", "surgical_cuts"]
                },
                "common_settings": {
                    "kick_enhancement": {"freq": 60, "gain": 3, "q": 0.7},
                    "vocal_clarity": {"freq": 3000, "gain": 2, "q": 1.2},
                    "hi_hat_sparkle": {"freq": 10000, "gain": 1.5, "q": 0.8}
                }
            },
            
            "Compressor": {
                "description": "Dynamics processor",
                "primary_uses": ["dynamic_control", "punch_enhancement", "glue_compression"],
                "style_techniques": {
                    "afro_house": ["gentle_glue", "percussion_punch", "vocal_control"],
                    "deep_house": ["vintage_compression", "subtle_pumping", "warmth"],
                    "tech_house": ["punchy_compression", "tight_control", "transient_enhancement"],
                    "progressive_house": ["transparent_compression", "peak_control"]
                },
                "common_settings": {
                    "kick_punch": {"ratio": 4, "attack": 1, "release": 50, "threshold": -15},
                    "vocal_smooth": {"ratio": 3, "attack": 10, "release": 100, "threshold": -12},
                    "bus_glue": {"ratio": 2, "attack": 30, "release": 200, "threshold": -8}
                }
            },
            
            "Reverb": {
                "description": "Algorithmic reverb processor",
                "primary_uses": ["spatial_enhancement", "depth_creation", "atmosphere"],
                "style_techniques": {
                    "afro_house": ["warm_halls", "organic_spaces", "vocal_enhancement"],
                    "deep_house": ["vintage_chambers", "smooth_tails", "jazz_club_vibe"],
                    "tech_house": ["tight_rooms", "controlled_reverb", "clarity_maintenance"],
                    "progressive_house": ["epic_halls", "cinematic_spaces", "emotional_depth"]
                },
                "common_settings": {
                    "vocal_hall": {"size": 0.8, "decay": 4.0, "predelay": 20, "dry_wet": 0.3},
                    "snare_room": {"size": 0.4, "decay": 1.5, "predelay": 5, "dry_wet": 0.2},
                    "pad_space": {"size": 0.9, "decay": 6.0, "predelay": 50, "dry_wet": 0.4}
                }
            },
            
            "Auto Filter": {
                "description": "Resonant filter with modulation",
                "primary_uses": ["filter_sweeps", "rhythmic_filtering", "creative_modulation"],
                "style_techniques": {
                    "afro_house": ["organic_filter_movement", "vocal_filtering", "percussion_shaping"],
                    "deep_house": ["smooth_filter_sweeps", "analog_warmth", "subtle_modulation"],
                    "tech_house": ["punchy_filter_hits", "rhythmic_gating", "energy_builds"],
                    "progressive_house": ["epic_filter_sweeps", "dramatic_builds", "tension_creation"]
                },
                "common_settings": {
                    "filter_sweep": {"frequency": 1000, "resonance": 0.3, "drive": 0.1},
                    "rhythmic_gate": {"frequency": 2000, "resonance": 0.5, "lfo_rate": "1/8"},
                    "vocal_filter": {"frequency": 800, "resonance": 0.2, "envelope": True}
                }
            },
            
            "Echo": {
                "description": "Delay processor with filtering",
                "primary_uses": ["rhythmic_delays", "space_enhancement", "creative_effects"],
                "style_techniques": {
                    "afro_house": ["organic_echoes", "polyrhythmic_delays", "vocal_delays"],
                    "deep_house": ["warm_analog_delays", "subtle_echoes", "jazz_influenced"],
                    "tech_house": ["tight_delays", "rhythmic_precision", "clarity_maintenance"],
                    "progressive_house": ["epic_delays", "building_echoes", "emotional_trails"]
                },
                "common_settings": {
                    "vocal_delay": {"time": "1/8d", "feedback": 0.25, "filter": 0.3},
                    "lead_echo": {"time": "1/4", "feedback": 0.15, "filter": 0.2},
                    "dub_delay": {"time": "1/2", "feedback": 0.4, "filter": 0.5}
                }
            },
            
            "Saturator": {
                "description": "Saturation and distortion processor",
                "primary_uses": ["harmonic_enhancement", "warmth_addition", "character_creation"],
                "style_techniques": {
                    "afro_house": ["tube_warmth", "organic_saturation", "vocal_character"],
                    "deep_house": ["vintage_tube_warmth", "analog_character", "subtle_harmonics"],
                    "tech_house": ["digital_punch", "presence_enhancement", "modern_character"],
                    "progressive_house": ["transparent_saturation", "polish_enhancement"]
                },
                "common_settings": {
                    "tube_warmth": {"drive": 0.15, "type": "tube", "color": 0.3},
                    "analog_punch": {"drive": 0.25, "type": "analog", "color": 0.2},
                    "digital_edge": {"drive": 0.2, "type": "digital", "color": 0.1}
                }
            }
        }
    
    def _initialize_midi_effects(self) -> Dict[str, Dict[str, Any]]:
        """Initialize MIDI effects knowledge"""
        return {
            "Arpeggiator": {
                "description": "MIDI arpeggiator for rhythmic patterns",
                "creative_uses": ["chord_arpeggiation", "rhythmic_patterns", "melodic_sequences"],
                "style_applications": {
                    "progressive_house": ["epic_arpeggios", "building_sequences"],
                    "tech_house": ["rhythmic_stabs", "percussive_sequences"],
                    "deep_house": ["flowing_arpeggios", "jazz_influenced_patterns"]
                }
            },
            
            "Chord": {
                "description": "Chord generator and harmonizer",
                "creative_uses": ["instant_chords", "harmonic_enhancement", "voicing_creation"],
                "style_applications": {
                    "afro_house": ["warm_chord_voicings", "gospel_progressions"],
                    "deep_house": ["jazz_chord_extensions", "sophisticated_voicings"],
                    "progressive_house": ["epic_chord_stacks", "emotional_harmonies"]
                }
            },
            
            "Scale": {
                "description": "Scale-based note mapping",
                "creative_uses": ["scale_conformity", "exotic_scales", "harmonic_constraint"],
                "style_applications": {
                    "afro_house": ["african_scale_modes", "pentatonic_patterns"],
                    "deep_house": ["jazz_scales", "sophisticated_harmony"],
                    "tech_house": ["minimal_scales", "precise_harmony"]
                }
            }
        }
    
    def _initialize_preset_library(self) -> Dict[str, List[PluginPreset]]:
        """Initialize comprehensive preset library"""
        presets = {}
        
        # Wavetable Presets
        presets["Wavetable"] = [
            PluginPreset(
                name="Afro House Sub Bass",
                plugin="Wavetable",
                category="bass",
                settings={
                    "wavetable": "Sub",
                    "filter_cutoff": 0.6,
                    "filter_resonance": 0.2,
                    "amp_envelope": {"attack": 0.01, "decay": 0.3, "sustain": 0.7, "release": 0.5},
                    "lfo1_rate": 0.1,
                    "lfo1_amount": 0.15
                },
                description="Warm, melodic sub bass perfect for Afro House",
                use_cases=["afro_house_bassline", "deep_house_foundation", "organic_bass"]
            ),
            
            PluginPreset(
                name="Keinemusik Pluck",
                plugin="Wavetable",
                category="lead",
                settings={
                    "wavetable": "Vintage Electric",
                    "filter_cutoff": 0.7,
                    "filter_resonance": 0.3,
                    "amp_envelope": {"attack": 0.01, "decay": 0.8, "sustain": 0.2, "release": 1.0},
                    "modulation": "subtle_lfo_filter"
                },
                description="Sophisticated pluck sound inspired by Keinemusik",
                use_cases=["sophisticated_leads", "chord_stabs", "melodic_elements"]
            ),
            
            PluginPreset(
                name="Progressive Supersaw",
                plugin="Wavetable",
                category="lead",
                settings={
                    "wavetable": "Supersaw",
                    "filter_cutoff": 0.8,
                    "filter_resonance": 0.4,
                    "amp_envelope": {"attack": 0.1, "decay": 2.0, "sustain": 0.6, "release": 2.0},
                    "unison": True,
                    "unison_voices": 7
                },
                description="Epic supersaw lead for progressive house builds",
                use_cases=["progressive_leads", "epic_builds", "emotional_peaks"]
            )
        ]
        
        # Bass Presets
        presets["Bass"] = [
            PluginPreset(
                name="Deep House Foundation",
                plugin="Bass",
                category="bass",
                settings={
                    "osc_mix": 0.8,
                    "sub": 0.9,
                    "envelope": {"attack": 0.01, "decay": 0.3, "sustain": 0.7, "release": 0.3},
                    "filter_cutoff": 0.6,
                    "saturation": 0.15
                },
                description="Warm, analog-style bass for deep house",
                use_cases=["deep_house_bass", "warm_foundation", "analog_character"]
            )
        ]
        
        return presets
    
    def _initialize_effect_chains(self) -> Dict[str, EffectChain]:
        """Initialize effect chain templates"""
        return {
            "afro_house_kick": EffectChain(
                name="Afro House Kick Chain",
                description="Professional kick drum processing for Afro House",
                style_tags=["afro_house", "organic", "punchy"],
                effects=[
                    {
                        "plugin": "EQ Eight",
                        "settings": {
                            "low_shelf": {"freq": 80, "gain": 3, "q": 0.7},
                            "high_cut": {"freq": 8000, "gain": -2, "q": 0.5}
                        }
                    },
                    {
                        "plugin": "Compressor",
                        "settings": {"ratio": 4, "attack": 1, "release": 50, "threshold": -12}
                    },
                    {
                        "plugin": "Saturator",
                        "settings": {"drive": 0.2, "type": "tube", "color": 0.3}
                    }
                ],
                usage_notes="Apply to kick drum for warm, punchy character"
            ),
            
            "deep_house_pad": EffectChain(
                name="Deep House Pad Chain",
                description="Lush, atmospheric pad processing",
                style_tags=["deep_house", "atmospheric", "warm"],
                effects=[
                    {
                        "plugin": "EQ Eight",
                        "settings": {
                            "high_pass": {"freq": 200, "q": 0.7},
                            "presence": {"freq": 5000, "gain": 1, "q": 1.0}
                        }
                    },
                    {
                        "plugin": "Auto Filter",
                        "settings": {"frequency": "slow_lfo", "resonance": 0.2}
                    },
                    {
                        "plugin": "Echo",
                        "settings": {"time": "1/8d", "feedback": 0.2, "filter": 0.3}
                    },
                    {
                        "plugin": "Reverb",
                        "settings": {"size": 0.8, "decay": 4.0, "predelay": 30}
                    }
                ],
                usage_notes="Creates lush, evolving pad sounds perfect for deep house"
            ),
            
            "progressive_lead": EffectChain(
                name="Progressive House Lead Chain",
                description="Epic lead processing for progressive house",
                style_tags=["progressive_house", "epic", "soaring"],
                effects=[
                    {
                        "plugin": "EQ Eight",
                        "settings": {
                            "presence": {"freq": 3000, "gain": 2, "q": 1.2},
                            "air": {"freq": 12000, "gain": 1.5, "q": 0.8}
                        }
                    },
                    {
                        "plugin": "Compressor",
                        "settings": {"ratio": 3, "attack": 10, "release": 100, "threshold": -8}
                    },
                    {
                        "plugin": "Echo",
                        "settings": {"time": "1/4", "feedback": 0.3, "filter": 0.2}
                    },
                    {
                        "plugin": "Reverb",
                        "settings": {"size": 0.9, "decay": 6.0, "predelay": 50}
                    }
                ],
                usage_notes="Creates soaring, epic leads that cut through the mix"
            )
        }
    
    def get_plugin_recommendation(self, sound_type: str, style: str) -> Dict[str, Any]:
        """
        Get plugin recommendation for specific sound type and style
        
        Args:
            sound_type: Type of sound needed (bass, lead, pad, etc.)
            style: Musical style
            
        Returns:
            Plugin recommendation with settings
        """
        
        recommendations = {
            ("bass", "afro_house"): {
                "plugin": "Bass",
                "preset": "Deep House Foundation",
                "additional_effects": ["EQ Eight", "Compressor"],
                "notes": "Use warm, melodic bass with slight saturation"
            },
            
            ("bass", "deep_house"): {
                "plugin": "Bass",
                "preset": "Deep House Foundation", 
                "additional_effects": ["EQ Eight", "Saturator"],
                "notes": "Focus on analog warmth and vintage character"
            },
            
            ("lead", "progressive_house"): {
                "plugin": "Wavetable",
                "preset": "Progressive Supersaw",
                "additional_effects": ["progressive_lead"],
                "notes": "Use supersaw with unison for epic, wide leads"
            },
            
            ("lead", "keinemusik"): {
                "plugin": "Wavetable", 
                "preset": "Keinemusik Pluck",
                "additional_effects": ["Echo", "Reverb"],
                "notes": "Sophisticated, musical lead with vintage character"
            },
            
            ("kick", "afro_house"): {
                "plugin": "Impulse",
                "preset": "House Kick",
                "additional_effects": ["afro_house_kick"],
                "notes": "Warm, punchy kick with organic character"
            },
            
            ("pad", "deep_house"): {
                "plugin": "Wavetable",
                "preset": "Warm Strings",
                "additional_effects": ["deep_house_pad"],
                "notes": "Lush, evolving pads with vintage warmth"
            }
        }
        
        key = (sound_type.lower(), style.lower().replace(" ", "_"))
        
        if key in recommendations:
            return recommendations[key]
        
        # Default recommendations by sound type
        defaults = {
            "bass": {"plugin": "Bass", "notes": "Use analog-style bass"},
            "lead": {"plugin": "Wavetable", "notes": "Use wavetable synthesis"},
            "pad": {"plugin": "Wavetable", "notes": "Use evolving textures"},
            "kick": {"plugin": "Impulse", "notes": "Use punchy drum sounds"},
            "snare": {"plugin": "Impulse", "notes": "Use crisp snare sounds"},
            "hi_hats": {"plugin": "Impulse", "notes": "Use crisp hi-hat sounds"}
        }
        
        return defaults.get(sound_type.lower(), {"plugin": "Wavetable", "notes": "Versatile synthesis"})
    
    def get_effect_chain(self, chain_name: str) -> Optional[EffectChain]:
        """Get specific effect chain by name"""
        return self.effect_chains.get(chain_name)
    
    def get_style_specific_chains(self, style: str) -> List[EffectChain]:
        """Get all effect chains suitable for a specific style"""
        style_key = style.lower().replace(" ", "_")
        suitable_chains = []
        
        for chain in self.effect_chains.values():
            if style_key in chain.style_tags:
                suitable_chains.append(chain)
        
        return suitable_chains
    
    def create_custom_preset(self, plugin: str, sound_type: str, style: str, characteristics: Dict[str, Any]) -> PluginPreset:
        """
        Create a custom preset based on requirements
        
        Args:
            plugin: Plugin name
            sound_type: Type of sound (bass, lead, etc.)
            style: Musical style
            characteristics: Desired sound characteristics
            
        Returns:
            Custom PluginPreset
        """
        
        # Base settings by plugin type
        base_settings = {
            "Wavetable": {
                "wavetable": "Analog",
                "filter_cutoff": 0.7,
                "filter_resonance": 0.3,
                "amp_envelope": {"attack": 0.01, "decay": 0.5, "sustain": 0.6, "release": 1.0}
            },
            "Bass": {
                "osc_mix": 0.8,
                "sub": 0.7,
                "envelope": {"attack": 0.01, "decay": 0.3, "sustain": 0.7, "release": 0.3}
            },
            "Operator": {
                "algorithm": 1,
                "operator_ratios": [1.0, 2.0, 3.0, 4.0],
                "envelope": {"attack": 0.01, "decay": 0.5, "sustain": 0.6, "release": 1.0}
            }
        }
        
        settings = base_settings.get(plugin, {})
        
        # Customize based on style and characteristics
        if style == "afro_house":
            if sound_type == "bass":
                settings.update({
                    "filter_cutoff": 0.6,
                    "warmth": 0.3,
                    "character": "organic"
                })
        elif style == "deep_house":
            settings.update({
                "vintage_character": True,
                "warmth": 0.4
            })
        elif style == "progressive_house":
            if sound_type == "lead":
                settings.update({
                    "unison": True,
                    "brightness": 0.8
                })
        
        preset = PluginPreset(
            name=f"Custom {style} {sound_type}",
            plugin=plugin,
            category=sound_type,
            settings=settings,
            description=f"Custom {sound_type} for {style}",
            use_cases=[f"{style}_{sound_type}"]
        )
        
        return preset
    
    def get_ableton_technique_guide(self, style: str) -> Dict[str, Any]:
        """
        Get comprehensive Ableton Live technique guide for a specific style
        
        Args:
            style: Musical style
            
        Returns:
            Complete production guide
        """
        
        guides = {
            "afro_house": {
                "primary_instruments": ["Bass", "Wavetable", "Impulse"],
                "essential_effects": ["EQ Eight", "Compressor", "Reverb", "Echo"],
                "production_techniques": [
                    "Use Bass for warm, melodic basslines",
                    "Layer organic percussion with Impulse",
                    "Apply tube saturation for warmth",
                    "Use Auto Filter for organic movement",
                    "Create vocal chops with Simpler"
                ],
                "mixing_approach": "Warm, organic, spacious mix with emphasis on groove",
                "arrangement_tips": [
                    "Start with percussion layers",
                    "Build gradually with harmonic elements", 
                    "Use filter sweeps for transitions",
                    "Create emotional peaks with full arrangements"
                ]
            },
            
            "deep_house": {
                "primary_instruments": ["Bass", "Wavetable", "Operator"],
                "essential_effects": ["EQ Eight", "Compressor", "Reverb", "Saturator"],
                "production_techniques": [
                    "Use analog-style compression",
                    "Apply vintage-style EQ curves",
                    "Create lush pads with Wavetable",
                    "Use FM synthesis for character sounds",
                    "Apply subtle saturation throughout"
                ],
                "mixing_approach": "Warm, vintage character with depth and space",
                "arrangement_tips": [
                    "Focus on groove and feel",
                    "Use subtle builds and breakdowns",
                    "Emphasize the 'deep' low-end",
                    "Create hypnotic, flowing arrangements"
                ]
            },
            
            "progressive_house": {
                "primary_instruments": ["Wavetable", "Operator", "Impulse"],
                "essential_effects": ["EQ Eight", "Compressor", "Reverb", "Echo", "Auto Filter"],
                "production_techniques": [
                    "Use supersaw leads for epic moments",
                    "Create dramatic filter sweeps", 
                    "Build tension with layered elements",
                    "Use sidechaining for pumping effect",
                    "Apply long reverb tails for space"
                ],
                "mixing_approach": "Wide, epic soundscape with emotional impact",
                "arrangement_tips": [
                    "Create long-form musical journeys",
                    "Build to emotional peaks",
                    "Use breakdown/buildup structures",
                    "Focus on cinematic arrangement"
                ]
            }
        }
        
        return guides.get(style.lower().replace(" ", "_"), guides["deep_house"])
    
    def list_available_presets(self, plugin: str = None, category: str = None) -> List[str]:
        """List available presets, optionally filtered by plugin or category"""
        all_presets = []
        
        for plugin_name, presets in self.preset_library.items():
            if plugin and plugin_name != plugin:
                continue
                
            for preset in presets:
                if category and preset.category != category:
                    continue
                all_presets.append(f"{plugin_name}: {preset.name}")
        
        return all_presets 