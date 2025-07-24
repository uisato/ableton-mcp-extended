#!/usr/bin/env python3
"""
AI Music Production Experts
Specialized Gemini-powered experts for different aspects of music production
"""

import json
import logging
from typing import Dict, List, Any, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)

class AIExpertBase:
    """Base class for AI music production experts"""
    
    def __init__(self, model, expert_type: str):
        self.model = model
        self.expert_type = expert_type
        logger.info(f"🧠 {expert_type} AI Expert initialized")
    
    async def generate_content(self, prompt: str, context: Dict = None) -> Dict:
        """Generate content with expert knowledge"""
        try:
            full_prompt = self._build_expert_prompt(prompt, context or {})
            
            # Use asyncio to run the synchronous Gemini call in a thread pool
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(full_prompt)
            )
            
            # Check if response is valid
            if not response or not response.text:
                logger.warning(f"❌ {self.expert_type} returned empty response")
                return self._fallback_response(prompt, context)
            
            response_text = response.text.strip()
            logger.debug(f"🧠 {self.expert_type} raw response: {response_text[:200]}...")
            
            # Try to parse JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"❌ {self.expert_type} JSON decode error: {e}")
                logger.error(f"Raw response was: {response_text}")
                
                # Try to extract JSON from response if it's embedded in text
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        pass
                
                return self._fallback_response(prompt, context)
                
        except Exception as e:
            logger.error(f"❌ {self.expert_type} generation error: {e}")
            return self._fallback_response(prompt, context)
    
    def _build_expert_prompt(self, prompt: str, context: Dict) -> str:
        """Build expert-specific prompt - override in subclasses"""
        return prompt
    
    def _fallback_response(self, prompt: str, context: Dict) -> Dict:
        """Fallback response if AI fails - override in subclasses"""
        return {"error": "AI generation failed"}

class DrumExpert(AIExpertBase):
    """Expert in drum programming and rhythm creation"""
    
    def __init__(self, model):
        super().__init__(model, "Drum Expert")
    
    def _build_expert_prompt(self, prompt: str, context: Dict) -> str:
        style = context.get('style', 'House')
        bpm = context.get('bpm', 120)
        section = context.get('section', 'main')
        bars = context.get('bars', 8)
        
        # Get cross-shared expert information
        harmonic_info = context.get('harmonic_info', {})
        
        collaboration_section = ""
        if harmonic_info:
            harmonic_analysis = harmonic_info.get('harmonic_analysis', {})
            chord_progression = context.get('chord_progression', [])
            collaboration_section = f"""

COLLABORATIVE INFORMATION FROM HARMONY EXPERT:
🎹 HARMONY EXPERT SHARED:
- Chord progression: {chord_progression}
- Harmonic rhythm: {harmonic_analysis.get('progression_type', 'standard')}
- Tension points: {harmonic_analysis.get('tension_points', 'chord changes')}
- Voice leading: {harmonic_analysis.get('voice_leading', 'smooth')}

IMPORTANT: Your drum patterns should complement the harmonic rhythm and chord changes.
Consider emphasizing beats that align with chord changes and creating rhythmic tension/release
that supports the harmonic progression.
"""
        
        return f"""
You are a world-class drum programmer and rhythm expert specializing in {style} music.

EXPERTISE AREAS:
- Professional drum programming for {style} at {bpm} BPM
- Understanding of groove, swing, and rhythmic tension
- Knowledge of classic drum machines (808, 909, 707) and their characteristics
- Expertise in layering percussion elements for depth and interest
- Collaborative awareness of how rhythm supports harmonic progressions

CURRENT TASK: {prompt}

CONTEXT:
- Style: {style}
- BPM: {bpm}
- Section: {section} 
- Length: {bars} bars
- Energy level: {context.get('energy', 'medium')}
{collaboration_section}

ENHANCED REQUIREMENTS (with expert collaboration):
1. Create a COMPLETE drum kit arrangement, not just kicks
2. Include: Kick, Snare/Clap, Hi-hats (closed/open), Percussion layers
3. SUPPORT the harmonic rhythm and chord changes with your patterns
4. Consider the groove and feel of {style} music
5. Create patterns that evolve over {bars} bars, not just 1-bar loops
6. Use proper velocities for dynamic interest
7. Consider the section type ({section}) for appropriate intensity
8. Emphasize important harmonic moments with rhythmic accents
9. Create rhythmic tension and release that supports the harmony

DRUM RACK SLOTS (Standard GM mapping):
- Slot 36: Kick drum (main)
- Slot 38: Snare drum 
- Slot 40: Clap (alternative snare)
- Slot 42: Closed Hi-hat
- Slot 44: Pedal Hi-hat  
- Slot 46: Open Hi-hat
- Slot 49: Crash cymbal
- Slot 51: Ride cymbal
- Slots 60-67: Percussion (shakers, tambourine, cowbell, etc.)

Respond with JSON only:
{{
    "kick_pattern": {{
        "notes": [
            {{"slot": 36, "time": 0.0, "velocity": 100, "duration": 0.1}},
            {{"slot": 36, "time": 4.0, "velocity": 95, "duration": 0.1}}
        ],
        "description": "Four-on-floor with subtle velocity variations that support chord changes",
        "bars": {bars}
    }},
    "snare_pattern": {{
        "notes": [
            {{"slot": 38, "time": 2.0, "velocity": 85, "duration": 0.1}},
            {{"slot": 38, "time": 6.0, "velocity": 90, "duration": 0.1}}
        ],
        "description": "Snare pattern that emphasizes harmonic rhythm and chord transitions",
        "bars": {bars}
    }},
    "hihat_pattern": {{
        "notes": [
            {{"slot": 42, "time": 1.0, "velocity": 70, "duration": 0.05}},
            {{"slot": 42, "time": 3.0, "velocity": 65, "duration": 0.05}}
        ],
        "description": "Hi-hat groove that complements harmonic movement",
        "bars": {bars}
    }},
    "percussion_pattern": {{
        "notes": [
            {{"slot": 60, "time": 0.5, "velocity": 60, "duration": 0.1}},
            {{"slot": 62, "time": 7.5, "velocity": 55, "duration": 0.1}}
        ],
        "description": "Percussion that adds texture while supporting harmonic flow",
        "bars": {bars}
    }},
    "groove_characteristics": {{
        "swing": "16th note groove with {context.get('swing', 'subtle')} swing",
        "intensity": "{context.get('energy', 'medium')} energy level",
        "style_elements": "Classic {style} drum programming techniques",
        "harmonic_integration": "How the rhythm supports and enhances the chord progression"
    }},
    "musical_description": "Overall description of the drum arrangement, its role in the {section} section, and harmonic collaboration"
}}

Create patterns that span the full {bars} bars with musical development, evolution, and harmonic awareness.
"""
    
    def _fallback_response(self, prompt: str, context: Dict) -> Dict:
        bars = context.get('bars', 8)
        # Create basic 4-on-floor with snare pattern
        return {
            "kick_pattern": {
                "notes": [{"slot": 36, "time": i * 1.0, "velocity": 100, "duration": 0.1} for i in range(0, bars * 4, 1)],
                "description": "Basic four-on-floor pattern",
                "bars": bars
            },
            "snare_pattern": {
                "notes": [{"slot": 38, "time": i * 1.0, "velocity": 85, "duration": 0.1} for i in range(2, bars * 4, 4)],
                "description": "Snare on beats 2 and 4",
                "bars": bars
            },
            "hihat_pattern": {
                "notes": [{"slot": 42, "time": i * 0.5, "velocity": 70, "duration": 0.05} for i in range(1, bars * 8, 2)],
                "description": "Eighth note hi-hats",
                "bars": bars
            },
            "percussion_pattern": {"notes": [], "description": "No percussion", "bars": bars},
            "groove_characteristics": {"swing": "straight", "intensity": "medium", "style_elements": "basic house"},
            "musical_description": "Fallback basic drum pattern"
        }

class BassExpert(AIExpertBase):
    """Expert in bass programming and harmonic foundation"""
    
    def __init__(self, model):
        super().__init__(model, "Bass Expert")
    
    def _build_expert_prompt(self, prompt: str, context: Dict) -> str:
        style = context.get('style', 'House')
        key = context.get('key', 'Am')
        bpm = context.get('bpm', 120)
        section = context.get('section', 'main')
        bars = context.get('bars', 8)
        chord_progression = context.get('chord_progression', ['Am', 'F', 'C', 'G'])
        
        # Get cross-shared expert information
        harmony_info = context.get('harmony_info', {})
        drum_info = context.get('drum_info', {})
        refinement_request = context.get('refinement_request', '')
        other_experts = context.get('other_experts', {})
        
        collaboration_section = ""
        if harmony_info or drum_info:
            collaboration_section = f"""

COLLABORATIVE INFORMATION FROM OTHER EXPERTS:
"""
            if harmony_info:
                harmonic_analysis = harmony_info.get('harmonic_analysis', {})
                collaboration_section += f"""
🎹 HARMONY EXPERT SHARED:
- Chord progression: {chord_progression}
- Harmonic rhythm: {harmonic_analysis.get('progression_type', 'standard')}
- Key center: {harmonic_analysis.get('key_center', key)}
- Tension points: {harmonic_analysis.get('tension_points', 'chord changes')}
- Voice leading: {harmonic_analysis.get('voice_leading', 'smooth')}
"""
            
            if drum_info:
                groove_char = drum_info.get('groove_characteristics', {})
                collaboration_section += f"""
🥁 DRUM EXPERT SHARED:
- Rhythmic feel: {drum_info.get('musical_description', 'driving rhythm')}
- Swing: {groove_char.get('swing', 'straight')}
- Intensity: {groove_char.get('intensity', 'medium')}
- Style elements: {groove_char.get('style_elements', f'{style} groove')}

IMPORTANT: Your bass line must lock in with the kick drum pattern and complement the overall groove.
"""

        refinement_section = ""
        if refinement_request:
            refinement_section = f"""

REFINEMENT REQUEST:
{refinement_request}

OTHER EXPERT CONTEXT FOR REFINEMENT:
{json.dumps(other_experts, indent=2)[:300]}...

FOCUS: Address the refinement request while maintaining musical coherence with other parts.
"""
        
        return f"""
You are a world-class bass player and programmer, expert in {style} music production.

EXPERTISE AREAS:
- Deep understanding of {style} bass lines and sub-bass techniques
- Harmonic knowledge: root motion, inversions, walking bass, rhythmic patterns
- Knowledge of bass synthesis and processing techniques
- Understanding how bass interacts with kick drums and other elements
- Collaborative awareness of how bass fits with harmony, rhythm, and melody

CURRENT TASK: {prompt}

CONTEXT:
- Style: {style}
- Key: {key}
- BPM: {bpm}
- Section: {section}
- Length: {bars} bars
- Chord progression: {chord_progression}
- Energy level: {context.get('energy', 'medium')}
{collaboration_section}
{refinement_section}

ENHANCED REQUIREMENTS (with expert collaboration):
1. Create a bass line that supports the chord progression musically
2. LOCK IN with the drum groove and kick pattern timing
3. Consider harmonic rhythm from the chord changes
4. Create patterns that evolve over {bars} bars with musical interest
5. Use appropriate rhythmic patterns for {style} that complement the drums
6. Include note variations, not just root notes
7. Respond to tension and resolution points in the harmony
8. Support the overall section energy and style characteristics

BASS LINE PRINCIPLES:
- Root notes provide harmonic foundation
- Passing tones create movement between chords
- Rhythmic displacement adds groove and interest  
- Octave jumps create dynamics
- Sustained notes vs. rhythmic patterns based on section energy
- Interlock with kick drum for tight low-end
- Support harmonic voice leading and chord function

Respond with JSON only:
{{
    "bass_line": {{
        "notes": [
            {{"pitch": 40, "time": 0.0, "velocity": 85, "duration": 3.5, "note_name": "E2", "function": "root"}},
            {{"pitch": 41, "time": 4.0, "velocity": 80, "duration": 3.5, "note_name": "F2", "function": "root"}},
            {{"pitch": 43, "time": 8.0, "velocity": 85, "duration": 1.5, "note_name": "G2", "function": "root"}},
            {{"pitch": 45, "time": 10.0, "velocity": 75, "duration": 1.5, "note_name": "A2", "function": "passing_tone"}}
        ],
        "bars": {bars},
        "description": "Bass line description with harmonic analysis and rhythm coordination"
    }},
    "sub_bass": {{
        "notes": [
            {{"pitch": 28, "time": 0.0, "velocity": 95, "duration": 4.0, "note_name": "E1", "function": "fundamental"}}
        ],
        "bars": {bars},
        "description": "Sub-bass layer for low-end foundation that supports kick drum"
    }},
    "harmonic_analysis": {{
        "chord_support": "How the bass supports each chord in the progression",
        "movement_pattern": "Description of bass movement and voice leading",
        "rhythmic_character": "Rhythmic characteristics and groove relationship with drums",
        "collaboration_notes": "How this bass line responds to other expert inputs"
    }},
    "style_elements": {{
        "genre_characteristics": "Specific {style} bass techniques used",
        "production_notes": "Notes on synthesis and processing for {style}",
        "expert_coordination": "How this part coordinates with harmony and rhythm experts"
    }},
    "musical_description": "Overall description of bass arrangement, harmonic function, and expert collaboration"
}}

Create a bass line that serves the song musically AND collaborates with other expert parts.
"""
    
    def _fallback_response(self, prompt: str, context: Dict) -> Dict:
        bars = context.get('bars', 8)
        # Create basic root note progression
        return {
            "bass_line": {
                "notes": [
                    {"pitch": 40, "time": 0.0, "velocity": 85, "duration": 3.5, "note_name": "E2", "function": "root"},
                    {"pitch": 37, "time": 4.0, "velocity": 85, "duration": 3.5, "note_name": "C#2", "function": "root"}
                ],
                "bars": bars,
                "description": "Basic root note pattern"
            },
            "sub_bass": {"notes": [], "bars": bars, "description": "No sub-bass"},
            "harmonic_analysis": {"chord_support": "basic", "movement_pattern": "static", "rhythmic_character": "simple"},
            "style_elements": {"genre_characteristics": "basic", "production_notes": "standard"},
            "musical_description": "Fallback basic bass pattern"
        }

class HarmonyExpert(AIExpertBase):
    """Expert in chord progressions and harmonic content"""
    
    def __init__(self, model):
        super().__init__(model, "Harmony Expert")
    
    def _build_expert_prompt(self, prompt: str, context: Dict) -> str:
        style = context.get('style', 'House')
        key = context.get('key', 'Am')
        section = context.get('section', 'main')
        bars = context.get('bars', 8)
        
        return f"""
You are a world-class composer and harmonist, expert in {style} chord progressions and voicings.

EXPERTISE AREAS:
- Advanced harmonic theory and chord progressions in {style}
- Voicing techniques: inversions, extensions, sus chords, color tones
- Understanding of tension and release in harmonic progressions
- Knowledge of {style}-specific harmonic conventions and innovations

CURRENT TASK: {prompt}

CONTEXT:
- Style: {style}
- Key: {key}
- Section: {section}
- Length: {bars} bars
- Energy level: {context.get('energy', 'medium')}

REQUIREMENTS:
1. Create a compelling chord progression appropriate for {style}
2. Use sophisticated voicings, not just basic triads
3. Consider harmonic rhythm (how often chords change)
4. Create voice leading that sounds smooth and musical
5. Include chord extensions and color tones where appropriate
6. Consider the emotional arc of the {section} section

HARMONIC PRINCIPLES:
- Voice leading: smooth movement between chord tones
- Harmonic rhythm: varied chord durations create interest
- Tension and resolution: use of dissonance and consonance
- Style-appropriate progressions: ii-V-I, vi-IV-I-V, etc.
- Chord extensions: 7ths, 9ths, sus chords for modern sound

Respond with JSON only:
{{
    "chord_progression": [
        {{
            "chord_symbol": "Am7",
            "chord_notes": [57, 60, 64, 67],
            "note_names": ["A3", "C4", "E4", "G4"],
            "start_time": 0.0,
            "duration": 4.0,
            "voicing_type": "close_position",
            "function": "tonic",
            "extensions": ["7th"]
        }},
        {{
            "chord_symbol": "Fmaj9",
            "chord_notes": [53, 57, 60, 65, 69],
            "note_names": ["F3", "A3", "C4", "F4", "A4"],
            "start_time": 4.0,
            "duration": 4.0,
            "voicing_type": "open_position",
            "function": "subdominant",
            "extensions": ["9th"]
        }}
    ],
    "harmonic_analysis": {{
        "key_center": "{key}",
        "progression_type": "Type of progression (e.g., circle of fifths, diatonic, modal)",
        "tension_points": "Where harmonic tension occurs and resolves",
        "voice_leading": "Description of voice leading techniques used"
    }},
    "style_characteristics": {{
        "genre_elements": "Specific {style} harmonic conventions used",
        "modern_techniques": "Contemporary harmonic techniques applied",
        "emotional_character": "Emotional effect of the progression"
    }},
    "performance_notes": {{
        "rhythm_pattern": "Suggested rhythmic pattern for chord performance",
        "dynamics": "Dynamic contour suggestions",
        "articulation": "Performance articulation notes"
    }},
    "musical_description": "Overall description of harmonic content and function"
}}

Create harmonies that serve the emotional and musical arc of the song.
"""
    
    def _fallback_response(self, prompt: str, context: Dict) -> Dict:
        return {
            "chord_progression": [
                {
                    "chord_symbol": "Am",
                    "chord_notes": [57, 60, 64],
                    "note_names": ["A3", "C4", "E4"],
                    "start_time": 0.0,
                    "duration": 4.0,
                    "voicing_type": "basic",
                    "function": "tonic",
                    "extensions": []
                }
            ],
            "harmonic_analysis": {"key_center": "Am", "progression_type": "basic", "tension_points": "none", "voice_leading": "basic"},
            "style_characteristics": {"genre_elements": "basic", "modern_techniques": "none", "emotional_character": "neutral"},
            "performance_notes": {"rhythm_pattern": "sustained", "dynamics": "static", "articulation": "legato"},
            "musical_description": "Fallback basic chord"
        }

class MelodyExpert(AIExpertBase):
    """Expert in melody creation and lead lines"""
    
    def __init__(self, model):
        super().__init__(model, "Melody Expert")
    
    def _build_expert_prompt(self, prompt: str, context: Dict) -> str:
        style = context.get('style', 'House')
        key = context.get('key', 'Am')
        section = context.get('section', 'main')
        bars = context.get('bars', 8)
        chord_progression = context.get('chord_progression', ['Am', 'F', 'C', 'G'])
        
        # Get cross-shared expert information
        harmony_info = context.get('harmony_info', {})
        bass_info = context.get('bass_info', {})
        drum_info = context.get('drum_info', {})
        refinement_request = context.get('refinement_request', '')
        other_experts = context.get('other_experts', {})
        
        collaboration_section = ""
        if harmony_info or bass_info or drum_info:
            collaboration_section = f"""

COLLABORATIVE INFORMATION FROM OTHER EXPERTS:
"""
            if harmony_info:
                harmonic_analysis = harmony_info.get('harmonic_analysis', {})
                collaboration_section += f"""
🎹 HARMONY EXPERT SHARED:
- Chord progression: {chord_progression}
- Harmonic rhythm: {harmonic_analysis.get('progression_type', 'standard')}
- Tension points: {harmonic_analysis.get('tension_points', 'chord changes')}
- Voice leading: {harmonic_analysis.get('voice_leading', 'smooth')}
- Emotional character: {harmony_info.get('style_characteristics', {}).get('emotional_character', 'neutral')}
"""
            
            if bass_info:
                bass_analysis = bass_info.get('harmonic_analysis', {})
                collaboration_section += f"""
🎸 BASS EXPERT SHARED:
- Bass movement: {bass_analysis.get('movement_pattern', 'root-based')}
- Rhythmic character: {bass_analysis.get('rhythmic_character', 'steady')}
- Harmonic support: {bass_analysis.get('chord_support', 'standard')}

IMPORTANT: Your melody should complement the bass line, not compete with it in the same register.
"""
            
            if drum_info:
                groove_char = drum_info.get('groove_characteristics', {})
                collaboration_section += f"""
🥁 DRUM EXPERT SHARED:
- Rhythmic feel: {drum_info.get('musical_description', 'driving rhythm')}
- Swing: {groove_char.get('swing', 'straight')}
- Intensity: {groove_char.get('intensity', 'medium')}
- Style elements: {groove_char.get('style_elements', f'{style} groove')}

IMPORTANT: Your melody rhythm should work with and enhance the drum groove, not conflict with it.
"""

        refinement_section = ""
        if refinement_request:
            refinement_section = f"""

REFINEMENT REQUEST:
{refinement_request}

OTHER EXPERT CONTEXT FOR REFINEMENT:
{json.dumps(other_experts, indent=2)[:300]}...

FOCUS: Address the refinement request while maintaining musical coherence with harmony, bass, and drums.
"""
        
        return f"""
You are a world-class melodist and lead synthesizer programmer, expert in {style} music.

EXPERTISE AREAS:
- Memorable melody creation in {style} with strong hooks and phrases
- Understanding of scales, modes, and melodic ornamentation
- Knowledge of synth lead programming and sound design
- Understanding of call-and-response, sequence, and motivic development
- Collaborative awareness of how melody fits with harmony, bass, and rhythm

CURRENT TASK: {prompt}

CONTEXT:
- Style: {style}
- Key: {key}
- Section: {section}
- Length: {bars} bars
- Chord progression: {chord_progression}
- Energy level: {context.get('energy', 'medium')}
{collaboration_section}
{refinement_section}

ENHANCED REQUIREMENTS (with expert collaboration):
1. Create memorable, singable melodies that fit {style}
2. USE CHORD TONES and appropriate scales that work with the harmony
3. COMPLEMENT the bass line - stay in higher registers, avoid bass frequencies
4. WORK WITH the drum groove - use rhythmic patterns that enhance, not compete
5. Use motivic development: repetition, sequence, variation
6. Create phrases that have clear beginnings and endings
7. Include both rhythmic and pitch interest
8. Consider the emotional arc appropriate for the {section}
9. Respond to harmonic tension and resolution points
10. Balance complexity with memorability

MELODIC PRINCIPLES:
- Phrase structure: clear 2, 4, or 8-bar phrases
- Contour: mix of steps and leaps for interest
- Rhythmic variety: mix of note values and syncopation that complements drums
- Scale relationships: chord tones, passing tones, neighbor tones
- Motivic development: use small ideas and develop them
- Register awareness: stay clear of bass register conflicts
- Groove integration: work with, not against, the established rhythm

Respond with JSON only:
{{
    "melody_line": {{
        "phrases": [
            {{
                "phrase_number": 1,
                "notes": [
                    {{"pitch": 69, "time": 0.0, "velocity": 85, "duration": 0.5, "note_name": "A4", "function": "chord_tone"}},
                    {{"pitch": 67, "time": 0.5, "velocity": 80, "duration": 0.5, "note_name": "G4", "function": "passing_tone"}},
                    {{"pitch": 64, "time": 1.0, "velocity": 85, "duration": 1.0, "note_name": "E4", "function": "chord_tone"}}
                ],
                "bars": 2,
                "character": "opening statement",
                "harmonic_support": "Am7 chord",
                "collaboration_notes": "Works with bass and drum patterns"
            }}
        ],
        "total_bars": {bars},
        "description": "Melodic analysis, character description, and expert collaboration"
    }},
    "melodic_analysis": {{
        "key_center": "{key}",
        "scale_usage": "Primary scales and modes used",
        "phrase_structure": "How phrases are organized (AABA, etc.)",
        "motivic_development": "How melodic ideas are developed",
        "climax_point": "Where the melodic high point occurs",
        "collaboration_analysis": "How melody works with harmony, bass, and drums"
    }},
    "style_elements": {{
        "genre_characteristics": "Specific {style} melodic conventions",
        "hook_factor": "What makes this melody memorable",
        "energy_arc": "How melody supports section energy",
        "expert_coordination": "How melody coordinates with other expert parts"
    }},
    "performance_notes": {{
        "articulation": "Legato, staccato, or mixed articulation",
        "expression": "Vibrato, bends, or other expression techniques",
        "layering": "Suggestions for harmony or counter-melodies",
        "mix_considerations": "How to balance with bass and drums in the mix"
    }},
    "musical_description": "Overall description of melodic content, purpose, and collaborative role"
}}

Create melodies that people will remember AND that work perfectly with the other expert parts.
"""
    
    def _fallback_response(self, prompt: str, context: Dict) -> Dict:
        bars = context.get('bars', 8)
        return {
            "melody_line": {
                "phrases": [
                    {
                        "phrase_number": 1,
                        "notes": [
                            {"pitch": 69, "time": 0.0, "velocity": 85, "duration": 1.0, "note_name": "A4", "function": "chord_tone"},
                            {"pitch": 67, "time": 1.0, "velocity": 85, "duration": 1.0, "note_name": "G4", "function": "chord_tone"}
                        ],
                        "bars": bars,
                        "character": "basic",
                        "harmonic_support": "basic"
                    }
                ],
                "total_bars": bars,
                "description": "Fallback basic melody"
            },
            "melodic_analysis": {"key_center": "Am", "scale_usage": "natural minor", "phrase_structure": "basic", "motivic_development": "none", "climax_point": "none"},
            "style_elements": {"genre_characteristics": "basic", "hook_factor": "simple", "energy_arc": "static"},
            "performance_notes": {"articulation": "legato", "expression": "none", "layering": "none"},
            "musical_description": "Fallback basic melody"
        }

class AIExpertOrchestrator:
    """Orchestrates all AI experts with collaborative cross-sharing and iterative refinement"""
    
    def __init__(self, model):
        self.model = model
        self.drum_expert = DrumExpert(model)
        self.bass_expert = BassExpert(model)
        self.harmony_expert = HarmonyExpert(model)
        self.melody_expert = MelodyExpert(model)
        logger.info("🎼 AI Expert Orchestrator initialized with collaborative specialists")
    
    async def generate_complete_section(self, style: str, key: str, bpm: int, section: str, bars: int, energy: str = "medium") -> Dict:
        """Generate a complete musical section using collaborative expert cross-sharing"""
        logger.info(f"🎵 Generating {section} section with expert collaboration: {style} in {key} at {bpm} BPM ({bars} bars)")
        
        context = {
            'style': style,
            'key': key,
            'bpm': bpm,
            'section': section,
            'bars': bars,
            'energy': energy
        }
        
        # PHASE 1: Foundation - Harmony Expert sets the harmonic framework
        logger.info("🎹 Phase 1: Harmony Expert creating harmonic foundation...")
        harmony_result = await self.harmony_expert.generate_content(
            f"Create a {bars}-bar chord progression for the {section} section of a {style} track in {key}",
            context
        )
        
        # Share harmony findings with all other experts
        shared_context = context.copy()
        if 'chord_progression' in harmony_result:
            chord_symbols = [chord['chord_symbol'] for chord in harmony_result['chord_progression']]
            shared_context['chord_progression'] = chord_symbols
            shared_context['harmonic_rhythm'] = harmony_result.get('harmonic_analysis', {})
            shared_context['chord_extensions'] = [chord.get('extensions', []) for chord in harmony_result['chord_progression']]
        
        # PHASE 2: Rhythmic Foundation - Drum Expert considers harmonic rhythm
        logger.info("🥁 Phase 2: Drum Expert creating rhythmic foundation with harmonic awareness...")
        drum_context = shared_context.copy()
        drum_context['harmonic_info'] = harmony_result
        
        drum_result = await self.drum_expert.generate_content(
            f"Create a {bars}-bar drum arrangement that complements the harmonic rhythm and chord changes",
            drum_context
        )
        
        # Share drum findings
        if 'groove_characteristics' in drum_result:
            shared_context['drum_groove'] = drum_result['groove_characteristics']
            shared_context['rhythmic_feel'] = drum_result.get('musical_description', '')
        
        # PHASE 3: Bass Foundation - Bass Expert supports harmony and groove
        logger.info("🎸 Phase 3: Bass Expert creating bass line that supports harmony and groove...")
        bass_context = shared_context.copy()
        bass_context['harmony_info'] = harmony_result
        bass_context['drum_info'] = drum_result
        
        bass_result = await self.bass_expert.generate_content(
            f"Create a bass line that supports the chord progression and complements the drum groove",
            bass_context
        )
        
        # Share bass findings
        if 'harmonic_analysis' in bass_result:
            shared_context['bass_movement'] = bass_result['harmonic_analysis']
        
        # PHASE 4: Melody Creation - Melody Expert considers all other parts
        melody_result = None
        if section in ['Drop_1', 'Drop_2', 'main', 'chorus', 'Build_1', 'Build_2']:
            logger.info("🎺 Phase 4: Melody Expert creating melody that works with all other parts...")
            melody_context = shared_context.copy()
            melody_context['harmony_info'] = harmony_result
            melody_context['bass_info'] = bass_result
            melody_context['drum_info'] = drum_result
            
            melody_result = await self.melody_expert.generate_content(
                f"Create a melody that works with the chord progression, bass line, and drum groove",
                melody_context
            )
        
        # PHASE 5: Collaborative Refinement - Orchestrator reviews and refines
        logger.info("🎼 Phase 5: Orchestrator reviewing and refining collaboration...")
        refinement_analysis = await self._analyze_expert_collaboration(
            harmony_result, bass_result, drum_result, melody_result, shared_context
        )
        
        # PHASE 6: Iterative Refinement (if needed)
        if refinement_analysis.get('needs_refinement', False):
            logger.info("🔄 Phase 6: Applying iterative refinements based on expert feedback...")
            refined_results = await self._apply_collaborative_refinements(
                harmony_result, bass_result, drum_result, melody_result, 
                refinement_analysis, shared_context
            )
            if refined_results:
                return refined_results
        
        return {
            'harmony': harmony_result,
            'bass': bass_result,
            'drums': drum_result,
            'melody': melody_result,
            'context': shared_context,
            'expert_analysis': {
                'section_type': section,
                'musical_complexity': 'high' if melody_result else 'medium',
                'generation_success': all([harmony_result, bass_result, drum_result]),
                'collaboration_quality': refinement_analysis.get('collaboration_score', 'good'),
                'expert_interactions': refinement_analysis.get('interactions', [])
            },
            'refinement_analysis': refinement_analysis
        }
    
    async def _analyze_expert_collaboration(self, harmony, bass, drums, melody, context) -> Dict:
        """AI analyzes how well the experts collaborated and if refinement is needed"""
        try:
            collaboration_prompt = f"""
            Analyze this musical collaboration between AI experts and determine if refinement is needed.

            HARMONY EXPERT OUTPUT: {json.dumps(harmony, indent=2)[:500]}...
            BASS EXPERT OUTPUT: {json.dumps(bass, indent=2)[:500]}...
            DRUM EXPERT OUTPUT: {json.dumps(drums, indent=2)[:500]}...
            MELODY EXPERT OUTPUT: {json.dumps(melody, indent=2)[:500] if melody else 'No melody'}...
            
            CONTEXT: {context.get('style')} in {context.get('key')} at {context.get('bpm')} BPM

            Analyze the collaboration and respond with JSON:
            {{
                "collaboration_score": "excellent/good/fair/poor",
                "needs_refinement": true/false,
                "issues_found": [
                    "specific issues like 'bass conflicts with harmony', 'melody too busy for drums', etc."
                ],
                "strengths": [
                    "what works well in this collaboration"
                ],
                "refinement_suggestions": [
                    "specific suggestions for each expert to improve collaboration"
                ],
                "interactions": [
                    "how the experts successfully influenced each other"
                ]
            }}
            """
            
            # Use async executor for synchronous Gemini call
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(collaboration_prompt)
            )
            return json.loads(response.text.strip())
            
        except Exception as e:
            logger.warning(f"Collaboration analysis failed: {e}")
            return {
                "collaboration_score": "good",
                "needs_refinement": False,
                "issues_found": [],
                "strengths": ["Basic collaboration successful"],
                "refinement_suggestions": [],
                "interactions": ["Standard expert coordination"]
            }
    
    async def _apply_collaborative_refinements(self, harmony, bass, drums, melody, analysis, context) -> Optional[Dict]:
        """Apply refinements based on expert collaboration analysis"""
        try:
            refinement_tasks = []
            
            # Check if any expert needs refinement
            for suggestion in analysis.get('refinement_suggestions', []):
                if 'harmony' in suggestion.lower():
                    refinement_tasks.append(('harmony', suggestion))
                elif 'bass' in suggestion.lower():
                    refinement_tasks.append(('bass', suggestion))
                elif 'drum' in suggestion.lower():
                    refinement_tasks.append(('drums', suggestion))
                elif 'melody' in suggestion.lower() and melody:
                    refinement_tasks.append(('melody', suggestion))
            
            # Apply refinements
            refined_results = {
                'harmony': harmony,
                'bass': bass,
                'drums': drums,
                'melody': melody,
                'context': context,
                'expert_analysis': {
                    'section_type': context.get('section'),
                    'musical_complexity': 'high' if melody else 'medium',
                    'generation_success': True,
                    'collaboration_quality': 'refined',
                    'refinements_applied': len(refinement_tasks)
                },
                'refinement_analysis': analysis
            }
            
            if refinement_tasks:
                logger.info(f"🔧 Applying {len(refinement_tasks)} collaborative refinements...")
                
                for expert_type, suggestion in refinement_tasks[:2]:  # Limit to 2 refinements to avoid loops
                    logger.info(f"🔧 Refining {expert_type}: {suggestion[:100]}...")
                    
                    if expert_type == 'bass':
                        refined_context = context.copy()
                        refined_context['refinement_request'] = suggestion
                        refined_context['other_experts'] = {
                            'harmony': harmony,
                            'drums': drums,
                            'melody': melody
                        }
                        
                        refined_bass = await self.bass_expert.generate_content(
                            f"Refine the bass line based on this feedback: {suggestion}",
                            refined_context
                        )
                        refined_results['bass'] = refined_bass
                        
                    elif expert_type == 'melody' and melody:
                        refined_context = context.copy()
                        refined_context['refinement_request'] = suggestion
                        refined_context['other_experts'] = {
                            'harmony': harmony,
                            'bass': bass,
                            'drums': drums
                        }
                        
                        refined_melody = await self.melody_expert.generate_content(
                            f"Refine the melody based on this feedback: {suggestion}",
                            refined_context
                        )
                        refined_results['melody'] = refined_melody
            
            return refined_results
            
        except Exception as e:
            logger.warning(f"Refinement application failed: {e}")
            return None 