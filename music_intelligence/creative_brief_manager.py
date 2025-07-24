"""
Creative Brief Persistence Manager

This system maintains a persistent creative brief that ensures all AI generation
phases adhere to the same musical vision, style, and constraints throughout
the entire music creation process.

Key features:
- Persistent creative brief storage and retrieval
- Cross-session creative vision consistency
- Style template management
- Musical constraint propagation
- Generation history tracking
- Quality consistency enforcement
- Professional arrangement guidelines

This ensures that when a user says "120 bpm deep house in A-minor", 
ALL subsequent generation respects and builds upon that foundation.
"""

import json
import logging
import pickle
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import uuid
import os

logger = logging.getLogger(__name__)

class MusicGenre(Enum):
    DEEP_HOUSE = "deep_house"
    TECH_HOUSE = "tech_house"
    TECHNO = "techno"
    TRANCE = "trance"
    PROGRESSIVE = "progressive"
    AMBIENT = "ambient"
    DRUM_AND_BASS = "drum_and_bass"
    DUBSTEP = "dubstep"
    TRAP = "trap"
    HIP_HOP = "hip_hop"
    POP = "pop"
    ROCK = "rock"
    JAZZ = "jazz"
    BLUES = "blues"
    CLASSICAL = "classical"
    FUNK = "funk"
    DISCO = "disco"
    REGGAE = "reggae"

class EnergyLevel(Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    INTENSE = "intense"
    PEAK = "peak"

class Complexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"

@dataclass
class StyleRequirements:
    """Detailed style requirements for music generation"""
    genre: MusicGenre
    sub_genre: Optional[str] = None
    energy_level: EnergyLevel = EnergyLevel.MODERATE
    complexity: Complexity = Complexity.MODERATE
    mood: List[str] = field(default_factory=list)
    instrumentation: List[str] = field(default_factory=list)
    production_style: Dict[str, Any] = field(default_factory=dict)
    reference_tracks: List[str] = field(default_factory=list)
    avoid_elements: List[str] = field(default_factory=list)

@dataclass
class MusicalParameters:
    """Core musical parameters that must remain consistent"""
    key: str
    scale_type: str
    tempo_bpm: int
    time_signature: str
    song_structure: List[str] = field(default_factory=list)
    harmonic_rhythm: str = "moderate"  # slow, moderate, fast
    melodic_range: str = "medium"      # low, medium, high, wide
    rhythmic_complexity: str = "moderate"  # simple, moderate, complex

@dataclass
class ProductionRequirements:
    """Production and mixing requirements"""
    mix_style: str = "modern"  # vintage, modern, lo-fi, hi-fi
    dynamics: str = "moderate"  # compressed, moderate, dynamic
    spatial_width: str = "wide"  # narrow, medium, wide
    frequency_balance: str = "balanced"  # bass_heavy, mid_focused, bright, balanced
    use_sidechain: bool = True
    use_reverb: bool = True
    use_delay: bool = True
    saturation_level: str = "moderate"  # clean, light, moderate, heavy

@dataclass
class ArrangementGuidelines:
    """Guidelines for song arrangement and structure"""
    intro_length_bars: int = 8
    verse_length_bars: int = 16
    chorus_length_bars: int = 16
    bridge_length_bars: int = 8
    outro_length_bars: int = 8
    breakdown_length_bars: int = 8
    build_up_length_bars: int = 8
    total_length_minutes: float = 4.0
    energy_curve: List[float] = field(default_factory=list)
    section_transitions: Dict[str, str] = field(default_factory=dict)

@dataclass
class CreativeBrief:
    """Complete creative brief for music generation"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Untitled Track"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Core requirements
    style_requirements: StyleRequirements = field(default_factory=StyleRequirements)
    musical_parameters: MusicalParameters = field(default_factory=MusicalParameters)
    production_requirements: ProductionRequirements = field(default_factory=ProductionRequirements)
    arrangement_guidelines: ArrangementGuidelines = field(default_factory=ArrangementGuidelines)
    
    # Generation tracking
    generated_sections: List[str] = field(default_factory=list)
    generation_history: List[Dict[str, Any]] = field(default_factory=list)
    quality_scores: Dict[str, float] = field(default_factory=dict)
    
    # User preferences
    user_feedback: List[str] = field(default_factory=list)
    locked_elements: Set[str] = field(default_factory=set)  # Elements that shouldn't change
    
    def __post_init__(self):
        # Set default energy curve if not provided
        if not self.arrangement_guidelines.energy_curve:
            self.arrangement_guidelines.energy_curve = self._generate_default_energy_curve()
            
    def _generate_default_energy_curve(self) -> List[float]:
        """Generate a default energy curve based on style"""
        genre = self.style_requirements.genre
        
        if genre in [MusicGenre.DEEP_HOUSE, MusicGenre.TECH_HOUSE]:
            # Gradual build, sustained energy, gentle outro
            return [0.2, 0.3, 0.5, 0.7, 0.8, 0.9, 0.8, 0.6, 0.4, 0.2]
        elif genre == MusicGenre.TECHNO:
            # Quick build, high sustained energy
            return [0.3, 0.6, 0.8, 0.9, 0.95, 0.9, 0.85, 0.7, 0.5, 0.2]
        elif genre in [MusicGenre.POP, MusicGenre.ROCK]:
            # Traditional song structure energy curve
            return [0.3, 0.5, 0.7, 0.9, 0.6, 0.8, 0.9, 0.7, 0.5, 0.3]
        else:
            # Default moderate curve
            return [0.3, 0.4, 0.6, 0.7, 0.8, 0.7, 0.6, 0.5, 0.4, 0.2]

class CreativeBriefManager:
    """Manages persistent creative briefs across sessions"""
    
    def __init__(self, storage_path: str = "./creative_briefs"):
        self.storage_path = storage_path
        self.current_brief: Optional[CreativeBrief] = None
        self.brief_templates = self._initialize_style_templates()
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
    def _initialize_style_templates(self) -> Dict[str, CreativeBrief]:
        """Initialize templates for common music styles"""
        templates = {}
        
        # Deep House Template
        deep_house_brief = CreativeBrief(
            title="Deep House Template",
            style_requirements=StyleRequirements(
                genre=MusicGenre.DEEP_HOUSE,
                energy_level=EnergyLevel.MODERATE,
                complexity=Complexity.MODERATE,
                mood=["groovy", "atmospheric", "warm", "hypnotic"],
                instrumentation=["bass", "drums", "pads", "leads", "percussion"],
                production_style={
                    "compression": "moderate",
                    "reverb": "lush",
                    "filtering": "prominent"
                }
            ),
            musical_parameters=MusicalParameters(
                key="Am",
                scale_type="minor",
                tempo_bpm=120,
                time_signature="4/4",
                song_structure=["intro", "breakdown", "buildup", "drop", "breakdown", "buildup", "drop", "outro"],
                harmonic_rhythm="slow",
                melodic_range="medium"
            ),
            production_requirements=ProductionRequirements(
                mix_style="modern",
                use_sidechain=True,
                use_reverb=True,
                use_delay=True,
                frequency_balance="bass_heavy"
            )
        )
        templates["deep_house"] = deep_house_brief
        
        # Tech House Template
        tech_house_brief = CreativeBrief(
            title="Tech House Template",
            style_requirements=StyleRequirements(
                genre=MusicGenre.TECH_HOUSE,
                energy_level=EnergyLevel.HIGH,
                complexity=Complexity.MODERATE,
                mood=["driving", "punchy", "minimal", "rhythmic"],
                instrumentation=["bass", "drums", "percussion", "minimal_leads"],
                production_style={
                    "compression": "tight",
                    "reverb": "minimal",
                    "punch": "prominent"
                }
            ),
            musical_parameters=MusicalParameters(
                key="Em",
                scale_type="minor",
                tempo_bpm=128,
                time_signature="4/4",
                harmonic_rhythm="moderate",
                rhythmic_complexity="complex"
            ),
            production_requirements=ProductionRequirements(
                mix_style="modern",
                dynamics="compressed",
                use_sidechain=True,
                frequency_balance="mid_focused"
            )
        )
        templates["tech_house"] = tech_house_brief
        
        # Pop Template
        pop_brief = CreativeBrief(
            title="Pop Template",
            style_requirements=StyleRequirements(
                genre=MusicGenre.POP,
                energy_level=EnergyLevel.HIGH,
                complexity=Complexity.SIMPLE,
                mood=["catchy", "uplifting", "accessible", "memorable"],
                instrumentation=["vocals", "drums", "bass", "guitar", "synths", "strings"]
            ),
            musical_parameters=MusicalParameters(
                key="C",
                scale_type="major",
                tempo_bpm=120,
                time_signature="4/4",
                song_structure=["intro", "verse", "pre_chorus", "chorus", "verse", "pre_chorus", "chorus", "bridge", "chorus", "outro"],
                harmonic_rhythm="moderate",
                melodic_range="wide"
            ),
            arrangement_guidelines=ArrangementGuidelines(
                intro_length_bars=4,
                verse_length_bars=8,
                chorus_length_bars=8,
                bridge_length_bars=4,
                total_length_minutes=3.5
            )
        )
        templates["pop"] = pop_brief
        
        return templates
        
    def create_brief_from_description(self, description: str) -> CreativeBrief:
        """Create a creative brief from a natural language description"""
        logger.info(f"Creating brief from description: {description}")
        
        # Parse the description to extract key elements
        parsed_elements = self._parse_description(description)
        
        # Start with a template if genre is detected
        template_name = parsed_elements.get("genre_template")
        if template_name and template_name in self.brief_templates:
            brief = self._copy_template(self.brief_templates[template_name])
        else:
            brief = CreativeBrief()
            
        # Apply parsed elements
        brief = self._apply_parsed_elements(brief, parsed_elements)
        
        # Set title based on description
        brief.title = self._generate_title_from_description(description)
        brief.created_at = datetime.now()
        brief.updated_at = datetime.now()
        
        self.current_brief = brief
        return brief
        
    def _parse_description(self, description: str) -> Dict[str, Any]:
        """Parse natural language description for musical elements"""
        desc_lower = description.lower()
        parsed = {}
        
        # Parse BPM
        import re
        bpm_match = re.search(r'(\d+)\s*bpm', desc_lower)
        if bpm_match:
            parsed["tempo_bpm"] = int(bpm_match.group(1))
            
        # Parse key
        key_patterns = [
            r'\b([a-g](?:#|b)?(?:\s*(?:major|minor|maj|min))?)\b',
            r'\b([a-g](?:#|b)?-(?:major|minor|maj|min))\b'
        ]
        for pattern in key_patterns:
            key_match = re.search(pattern, desc_lower)
            if key_match:
                key_str = key_match.group(1).strip()
                parsed["key"] = self._normalize_key_notation(key_str)
                if "minor" in key_str or "min" in key_str:
                    parsed["scale_type"] = "minor"
                else:
                    parsed["scale_type"] = "major"
                break
                
        # Parse genre
        genre_map = {
            "deep house": ("deep_house", MusicGenre.DEEP_HOUSE),
            "tech house": ("tech_house", MusicGenre.TECH_HOUSE),
            "house": ("deep_house", MusicGenre.DEEP_HOUSE),
            "techno": ("techno", MusicGenre.TECHNO),
            "trance": ("trance", MusicGenre.TRANCE),
            "pop": ("pop", MusicGenre.POP),
            "rock": ("rock", MusicGenre.ROCK),
            "ambient": ("ambient", MusicGenre.AMBIENT),
            "jazz": ("jazz", MusicGenre.JAZZ),
            "blues": ("blues", MusicGenre.BLUES)
        }
        
        for genre_name, (template, genre_enum) in genre_map.items():
            if genre_name in desc_lower:
                parsed["genre_template"] = template
                parsed["genre"] = genre_enum
                break
                
        # Parse mood/style descriptors
        mood_keywords = {
            "dark": ["dark", "moody", "mysterious"],
            "uplifting": ["uplifting", "positive", "happy", "bright"],
            "aggressive": ["aggressive", "hard", "intense"],
            "chill": ["chill", "relaxed", "laid-back", "smooth"],
            "energetic": ["energetic", "driving", "powerful"],
            "atmospheric": ["atmospheric", "ambient", "spacious"],
            "minimal": ["minimal", "stripped", "simple"],
            "complex": ["complex", "intricate", "detailed"]
        }
        
        detected_moods = []
        for mood, keywords in mood_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                detected_moods.append(mood)
        parsed["mood"] = detected_moods
        
        # Parse energy level
        if any(word in desc_lower for word in ["high energy", "intense", "peak", "maximum"]):
            parsed["energy_level"] = EnergyLevel.HIGH
        elif any(word in desc_lower for word in ["low energy", "minimal", "quiet"]):
            parsed["energy_level"] = EnergyLevel.LOW
        elif any(word in desc_lower for word in ["moderate", "medium"]):
            parsed["energy_level"] = EnergyLevel.MODERATE
            
        return parsed
        
    def _normalize_key_notation(self, key_str: str) -> str:
        """Normalize key notation to standard format"""
        key_str = key_str.strip().replace("-", " ")
        
        # Handle different notations
        if "major" in key_str or "maj" in key_str:
            note = key_str.split()[0]
            return note.upper()
        elif "minor" in key_str or "min" in key_str:
            note = key_str.split()[0]
            return note.lower() + "m"
        else:
            # Assume major if no modifier
            return key_str.upper()
            
    def _copy_template(self, template: CreativeBrief) -> CreativeBrief:
        """Create a copy of a template brief"""
        template_dict = asdict(template)
        # Remove session-specific data
        template_dict["session_id"] = str(uuid.uuid4())
        template_dict["created_at"] = datetime.now()
        template_dict["updated_at"] = datetime.now()
        template_dict["generated_sections"] = []
        template_dict["generation_history"] = []
        template_dict["quality_scores"] = {}
        template_dict["user_feedback"] = []
        
        return CreativeBrief(**template_dict)
        
    def _apply_parsed_elements(self, brief: CreativeBrief, elements: Dict[str, Any]) -> CreativeBrief:
        """Apply parsed elements to the creative brief"""
        
        # Apply musical parameters
        if "tempo_bpm" in elements:
            brief.musical_parameters.tempo_bpm = elements["tempo_bpm"]
        if "key" in elements:
            brief.musical_parameters.key = elements["key"]
        if "scale_type" in elements:
            brief.musical_parameters.scale_type = elements["scale_type"]
            
        # Apply style requirements
        if "genre" in elements:
            brief.style_requirements.genre = elements["genre"]
        if "mood" in elements:
            brief.style_requirements.mood.extend(elements["mood"])
        if "energy_level" in elements:
            brief.style_requirements.energy_level = elements["energy_level"]
            
        return brief
        
    def _generate_title_from_description(self, description: str) -> str:
        """Generate a title from the description"""
        # Extract key elements for title
        words = description.split()
        key_words = []
        
        for word in words:
            if any(genre in word.lower() for genre in ["house", "techno", "pop", "rock", "jazz", "blues"]):
                key_words.append(word.title())
            elif "bpm" in word.lower():
                key_words.append(word.upper())
            elif any(key in word.lower() for key in ["minor", "major", "a-", "b-", "c-", "d-", "e-", "f-", "g-"]):
                key_words.append(word.title())
                
        if key_words:
            return " ".join(key_words[:3])  # Max 3 words
        else:
            return "Generated Track"
            
    def save_brief(self, brief: Optional[CreativeBrief] = None) -> str:
        """Save creative brief to storage"""
        if brief is None:
            brief = self.current_brief
            
        if brief is None:
            raise ValueError("No brief to save")
            
        brief.updated_at = datetime.now()
        filename = f"{brief.session_id}.json"
        filepath = os.path.join(self.storage_path, filename)
        
        # Convert to JSON-serializable format
        brief_dict = asdict(brief)
        brief_dict["created_at"] = brief.created_at.isoformat()
        brief_dict["updated_at"] = brief.updated_at.isoformat()
        brief_dict["locked_elements"] = list(brief.locked_elements)
        
        # Handle enums
        brief_dict["style_requirements"]["genre"] = brief.style_requirements.genre.value
        brief_dict["style_requirements"]["energy_level"] = brief.style_requirements.energy_level.value
        brief_dict["style_requirements"]["complexity"] = brief.style_requirements.complexity.value
        
        with open(filepath, 'w') as f:
            json.dump(brief_dict, f, indent=2)
            
        logger.info(f"Saved creative brief to {filepath}")
        return filepath
        
    def load_brief(self, session_id: str) -> CreativeBrief:
        """Load creative brief from storage"""
        filename = f"{session_id}.json"
        filepath = os.path.join(self.storage_path, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Brief not found: {session_id}")
            
        with open(filepath, 'r') as f:
            brief_dict = json.load(f)
            
        # Convert back from JSON format
        brief_dict["created_at"] = datetime.fromisoformat(brief_dict["created_at"])
        brief_dict["updated_at"] = datetime.fromisoformat(brief_dict["updated_at"])
        brief_dict["locked_elements"] = set(brief_dict["locked_elements"])
        
        # Handle enums
        brief_dict["style_requirements"]["genre"] = MusicGenre(brief_dict["style_requirements"]["genre"])
        brief_dict["style_requirements"]["energy_level"] = EnergyLevel(brief_dict["style_requirements"]["energy_level"])
        brief_dict["style_requirements"]["complexity"] = Complexity(brief_dict["style_requirements"]["complexity"])
        
        # Reconstruct dataclasses
        style_req = StyleRequirements(**brief_dict["style_requirements"])
        musical_params = MusicalParameters(**brief_dict["musical_parameters"])
        production_req = ProductionRequirements(**brief_dict["production_requirements"])
        arrangement_guide = ArrangementGuidelines(**brief_dict["arrangement_guidelines"])
        
        brief_dict["style_requirements"] = style_req
        brief_dict["musical_parameters"] = musical_params
        brief_dict["production_requirements"] = production_req
        brief_dict["arrangement_guidelines"] = arrangement_guide
        
        brief = CreativeBrief(**brief_dict)
        self.current_brief = brief
        
        logger.info(f"Loaded creative brief: {brief.title}")
        return brief
        
    def update_brief(self, updates: Dict[str, Any]) -> CreativeBrief:
        """Update current creative brief with new information"""
        if self.current_brief is None:
            raise ValueError("No current brief to update")
            
        # Apply updates
        for key, value in updates.items():
            if hasattr(self.current_brief, key):
                setattr(self.current_brief, key, value)
            elif hasattr(self.current_brief.musical_parameters, key):
                setattr(self.current_brief.musical_parameters, key, value)
            elif hasattr(self.current_brief.style_requirements, key):
                setattr(self.current_brief.style_requirements, key, value)
            elif hasattr(self.current_brief.production_requirements, key):
                setattr(self.current_brief.production_requirements, key, value)
                
        self.current_brief.updated_at = datetime.now()
        return self.current_brief
        
    def add_generation_history(self, section_type: str, generation_data: Dict[str, Any]) -> None:
        """Add generation history entry"""
        if self.current_brief is None:
            return
            
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "section_type": section_type,
            "generation_data": generation_data,
            "quality_score": generation_data.get("quality_score", 0.0)
        }
        
        self.current_brief.generation_history.append(history_entry)
        
        if section_type not in self.current_brief.generated_sections:
            self.current_brief.generated_sections.append(section_type)
            
    def get_style_constraints_for_ai(self) -> Dict[str, Any]:
        """Get style constraints formatted for AI generation"""
        if self.current_brief is None:
            return {}
            
        return {
            "musical_parameters": {
                "key": self.current_brief.musical_parameters.key,
                "scale_type": self.current_brief.musical_parameters.scale_type,
                "tempo_bpm": self.current_brief.musical_parameters.tempo_bpm,
                "time_signature": self.current_brief.musical_parameters.time_signature,
                "harmonic_rhythm": self.current_brief.musical_parameters.harmonic_rhythm,
                "melodic_range": self.current_brief.musical_parameters.melodic_range,
                "rhythmic_complexity": self.current_brief.musical_parameters.rhythmic_complexity
            },
            "style_requirements": {
                "genre": self.current_brief.style_requirements.genre.value,
                "energy_level": self.current_brief.style_requirements.energy_level.value,
                "complexity": self.current_brief.style_requirements.complexity.value,
                "mood": self.current_brief.style_requirements.mood,
                "instrumentation": self.current_brief.style_requirements.instrumentation,
                "production_style": self.current_brief.style_requirements.production_style,
                "avoid_elements": self.current_brief.style_requirements.avoid_elements
            },
            "production_requirements": asdict(self.current_brief.production_requirements),
            "arrangement_guidelines": {
                "energy_curve": self.current_brief.arrangement_guidelines.energy_curve,
                "section_transitions": self.current_brief.arrangement_guidelines.section_transitions,
                "total_length_minutes": self.current_brief.arrangement_guidelines.total_length_minutes
            },
            "locked_elements": list(self.current_brief.locked_elements),
            "generation_context": {
                "generated_sections": self.current_brief.generated_sections,
                "session_id": self.current_brief.session_id,
                "title": self.current_brief.title
            }
        }
        
    def validate_brief_consistency(self) -> Dict[str, Any]:
        """Validate that the brief is internally consistent"""
        if self.current_brief is None:
            return {"valid": False, "errors": ["No active brief"]}
            
        errors = []
        warnings = []
        
        # Check tempo appropriateness for genre
        tempo = self.current_brief.musical_parameters.tempo_bpm
        genre = self.current_brief.style_requirements.genre
        
        tempo_ranges = {
            MusicGenre.DEEP_HOUSE: (118, 125),
            MusicGenre.TECH_HOUSE: (125, 132),
            MusicGenre.TECHNO: (130, 150),
            MusicGenre.TRANCE: (130, 140),
            MusicGenre.DRUM_AND_BASS: (160, 180),
            MusicGenre.DUBSTEP: (140, 150),
            MusicGenre.POP: (100, 130),
            MusicGenre.ROCK: (110, 140)
        }
        
        if genre in tempo_ranges:
            min_tempo, max_tempo = tempo_ranges[genre]
            if tempo < min_tempo or tempo > max_tempo:
                warnings.append(f"Tempo {tempo} BPM unusual for {genre.value} (typical: {min_tempo}-{max_tempo})")
                
        # Check key and scale consistency
        key = self.current_brief.musical_parameters.key
        scale_type = self.current_brief.musical_parameters.scale_type
        
        if scale_type == "minor" and not (key.endswith("m") or "minor" in key.lower()):
            warnings.append(f"Key notation '{key}' doesn't match scale type '{scale_type}'")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "score": 1.0 - (len(errors) * 0.3 + len(warnings) * 0.1)
        }
        
    def get_brief_summary(self) -> Dict[str, Any]:
        """Get a summary of the current creative brief"""
        if self.current_brief is None:
            return {"active": False}
            
        return {
            "active": True,
            "session_id": self.current_brief.session_id,
            "title": self.current_brief.title,
            "created_at": self.current_brief.created_at.isoformat(),
            "musical_core": {
                "key": self.current_brief.musical_parameters.key,
                "tempo_bpm": self.current_brief.musical_parameters.tempo_bpm,
                "genre": self.current_brief.style_requirements.genre.value,
                "energy_level": self.current_brief.style_requirements.energy_level.value
            },
            "progress": {
                "generated_sections": self.current_brief.generated_sections,
                "total_generations": len(self.current_brief.generation_history),
                "average_quality": sum(self.current_brief.quality_scores.values()) / max(len(self.current_brief.quality_scores), 1)
            },
            "constraints": {
                "locked_elements": list(self.current_brief.locked_elements),
                "style_mood": self.current_brief.style_requirements.mood,
                "instrumentation": self.current_brief.style_requirements.instrumentation
            }
        } 