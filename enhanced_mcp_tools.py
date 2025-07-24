"""
Enhanced MCP Tools - AI Music Producer Integration

This module extends the existing MCP server with AI-powered music generation
capabilities using Google Gemini 2.5 Flash.

New High-Level Generation Tools:
- generate_complete_track: Create full arranged tracks
- analyze_and_replicate_style: Style analysis and replication  
- create_arrangement_from_elements: Professional arrangement
- Style-specific generators for different genres
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Import existing MCP framework
import mcp
from mcp import Context
from mcp.server import Server

# Import our AI Music Producer
from music_intelligence import GeminiOrchestrator, StyleAnalyzer, StockPluginExpert

logger = logging.getLogger(__name__)

# Global instances
orchestrator: Optional[GeminiOrchestrator] = None
style_analyzer: Optional[StyleAnalyzer] = None
plugin_expert: Optional[StockPluginExpert] = None


def initialize_ai_systems():
    """Initialize AI systems if not already done"""
    global orchestrator, style_analyzer, plugin_expert
    
    if orchestrator is None:
        orchestrator = GeminiOrchestrator()
        style_analyzer = StyleAnalyzer()
        plugin_expert = StockPluginExpert()
        logger.info("AI Music Producer systems initialized")


# ============================================================================
# HIGH-LEVEL GENERATION TOOLS
# ============================================================================

@mcp.tool()
async def generate_complete_track(
    ctx: Context,
    user_request: str,
    style: Optional[str] = None,
    artist_reference: Optional[str] = None,
    bpm: Optional[int] = None,
    key: Optional[str] = None,
    length_minutes: float = 6.0,
    complexity: str = "professional"
) -> str:
    """
    Generate a complete, arranged track based on user request
    
    Args:
        user_request: Natural language description of the desired track
        style: Optional specific style override
        artist_reference: Optional artist reference override
        bpm: Optional BPM override
        key: Optional key override
        length_minutes: Track length in minutes
        complexity: simple/intermediate/professional
        
    Returns:
        Success message with track generation details
    """
    initialize_ai_systems()
    
    try:
        logger.info(f"Generating complete track: {user_request}")
        
        # Phase 1: Analyze user request
        analysis = await orchestrator.analyze_user_request(user_request)
        
        # Apply overrides if provided
        if style:
            analysis["style"] = style
        if artist_reference:
            analysis["artist_reference"] = artist_reference
        if bpm:
            analysis["bpm"] = bpm
        if key:
            analysis["key"] = key
        analysis["length_minutes"] = length_minutes
        analysis["complexity"] = complexity
        
        # Phase 2: Create detailed creative brief
        brief = await orchestrator.create_creative_brief(analysis)
        
        # Phase 3: Generate arrangement plan
        arrangement = await orchestrator.generate_arrangement_plan(brief)
        
        # Phase 4: Get plugin recommendations for each element
        recommendations = {}
        for element in brief.track_elements:
            rec = plugin_expert.get_plugin_recommendation(element, brief.style)
            recommendations[element] = rec
        
        # Return comprehensive generation plan
        result = {
            "status": "success",
            "message": f"Complete {brief.style} track generated successfully!",
            "analysis": analysis,
            "creative_brief": {
                "style": brief.style,
                "bpm": brief.bpm,
                "key": brief.key,
                "track_elements": brief.track_elements,
                "harmonic_progression": brief.harmonic_progression,
                "arrangement_length": brief.arrangement_length
            },
            "arrangement": arrangement,
            "plugin_recommendations": recommendations,
            "next_steps": [
                f"1. Set project BPM to {brief.bpm}",
                f"2. Set key to {brief.key}",
                "3. Create tracks for each element",
                "4. Apply recommended plugins and settings",
                "5. Follow arrangement plan for section structure"
            ]
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error generating complete track: {e}")
        return f"Error generating track: {str(e)}"


@mcp.tool() 
async def analyze_and_replicate_style(
    ctx: Context,
    reference_description: str,
    target_elements: List[str]
) -> str:
    """
    Analyze style from description and replicate key elements
    
    Args:
        reference_description: Description of the reference style/artist
        target_elements: List of elements to focus on (bass, lead, drums, etc.)
        
    Returns:
        Style analysis and replication guide
    """
    initialize_ai_systems()
    
    try:
        logger.info(f"Analyzing style: {reference_description}")
        
        # Use Gemini to analyze the reference
        analysis_prompt = f"""
        Analyze this musical reference and extract detailed style characteristics:
        "{reference_description}"
        
        Focus on these elements: {target_elements}
        
        Provide a detailed analysis including:
        - Genre/style classification
        - Key musical characteristics
        - Production techniques
        - Specific plugin recommendations for Ableton Live
        - Step-by-step replication guide
        
        Format as detailed JSON with actionable production advice.
        """
        
        orchestrator.start_chat_session()
        analysis_response = await orchestrator.chat(analysis_prompt)
        
        # Get style characteristics if we can identify the style
        style_name = "deep_house"  # Default
        try:
            # Try to extract style from response
            if "afro house" in analysis_response.lower():
                style_name = "afro_house"
            elif "progressive" in analysis_response.lower():
                style_name = "progressive_house"
            elif "tech house" in analysis_response.lower():
                style_name = "tech_house"
            elif "keinemusik" in analysis_response.lower():
                style_name = "keinemusik"
        except:
            pass
        
        style_chars = style_analyzer.get_style_characteristics(style_name)
        
        # Get plugin recommendations for target elements
        recommendations = {}
        for element in target_elements:
            rec = plugin_expert.get_plugin_recommendation(element, style_name)
            recommendations[element] = rec
        
        result = {
            "status": "success",
            "reference": reference_description,
            "identified_style": style_name,
            "ai_analysis": analysis_response,
            "style_characteristics": {
                "bpm_range": style_chars.bpm_range,
                "key_preferences": style_chars.key_preferences,
                "signature_techniques": style_chars.signature_techniques,
                "energy_curve": style_chars.energy_curve
            },
            "plugin_recommendations": recommendations,
            "replication_guide": f"Follow the AI analysis above for detailed replication steps using Ableton Live stock plugins."
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error analyzing style: {e}")
        return f"Error analyzing style: {str(e)}"


@mcp.tool()
async def create_arrangement_from_elements(
    ctx: Context,
    existing_elements: List[str],
    target_style: str,
    arrangement_length: float = 6.0,
    energy_progression: str = "building"
) -> str:
    """
    Create professional arrangement from existing musical elements
    
    Args:
        existing_elements: List of existing track elements
        target_style: Target musical style
        arrangement_length: Length in minutes
        energy_progression: building/steady/dynamic/epic
        
    Returns:
        Detailed arrangement plan
    """
    initialize_ai_systems()
    
    try:
        logger.info(f"Creating arrangement for {target_style} with {len(existing_elements)} elements")
        
        # Get style characteristics
        style_chars = style_analyzer.get_style_characteristics(target_style)
        
        # Create arrangement prompt for Gemini
        arrangement_prompt = f"""
        Create a professional arrangement plan for a {target_style} track.
        
        Available elements: {existing_elements}
        Track length: {arrangement_length} minutes
        Energy progression: {energy_progression}
        Style BPM range: {style_chars.bpm_range}
        
        Create a detailed, bar-by-bar arrangement plan that:
        1. Uses all available elements effectively
        2. Follows {target_style} conventions
        3. Creates proper energy flow ({energy_progression})
        4. Includes smooth transitions
        5. Results in a professional, DJ-friendly arrangement
        
        Format as JSON with specific bar numbers, active elements, and transition notes.
        """
        
        orchestrator.start_chat_session()
        arrangement_response = await orchestrator.chat(arrangement_prompt)
        
        # Get recommended BPM
        recommended_bpm = style_analyzer.get_recommended_bpm(target_style, "medium")
        
        result = {
            "status": "success",
            "target_style": target_style,
            "arrangement_length": arrangement_length,
            "recommended_bpm": recommended_bpm,
            "available_elements": existing_elements,
            "energy_progression": energy_progression,
            "arrangement_plan": arrangement_response,
            "style_tips": {
                "intro_length": style_chars.arrangement_style.get("intro_length", 32),
                "breakdown_style": style_chars.arrangement_style.get("breakdown_style", "filter_sweeps"),
                "signature_techniques": style_chars.signature_techniques[:3]
            }
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error creating arrangement: {e}")
        return f"Error creating arrangement: {str(e)}"


# ============================================================================
# STYLE-SPECIFIC GENERATORS
# ============================================================================

@mcp.tool()
async def create_afro_house_track(
    ctx: Context,
    artist_inspiration: str = "Black Coffee",
    emotional_arc: str = "building",
    bpm: int = 122,
    include_vocals: bool = True
) -> str:
    """
    Generate authentic Afro House track
    
    Args:
        artist_inspiration: Artist reference for style direction
        emotional_arc: building/steady/epic/intimate
        bpm: Beats per minute
        include_vocals: Whether to include vocal elements
        
    Returns:
        Complete Afro House track generation plan
    """
    initialize_ai_systems()
    
    try:
        # Create Afro House specific request
        request = f"""
        Create an Afro House track inspired by {artist_inspiration} at {bpm} BPM.
        Emotional arc: {emotional_arc}
        Include vocal elements: {include_vocals}
        Focus on organic percussion, warm basslines, and atmospheric elements.
        """
        
        return await generate_complete_track(
            ctx, request, style="afro_house", artist_reference=artist_inspiration, bpm=bpm
        )
        
    except Exception as e:
        logger.error(f"Error creating Afro House track: {e}")
        return f"Error creating Afro House track: {str(e)}"


@mcp.tool()
async def create_keinemusik_style_track(
    ctx: Context,
    sophistication_level: str = "high",
    vocal_elements: bool = True,
    harmonic_complexity: str = "advanced"
) -> str:
    """
    Generate Keinemusik-inspired sophisticated deep house
    
    Args:
        sophistication_level: simple/medium/high/expert
        vocal_elements: Include processed vocal elements
        harmonic_complexity: simple/intermediate/advanced/jazz
        
    Returns:
        Complete Keinemusik-style track generation plan
    """
    initialize_ai_systems()
    
    try:
        request = f"""
        Create a sophisticated deep house track in the style of Keinemusik.
        Sophistication level: {sophistication_level}
        Include vocal elements: {vocal_elements}
        Harmonic complexity: {harmonic_complexity}
        Focus on vintage electric pianos, sophisticated arrangements, and emotional storytelling.
        """
        
        return await generate_complete_track(
            ctx, request, style="keinemusik", artist_reference="Keinemusik"
        )
        
    except Exception as e:
        logger.error(f"Error creating Keinemusik-style track: {e}")
        return f"Error creating Keinemusik-style track: {str(e)}"


@mcp.tool()
async def create_progressive_house_anthem(
    ctx: Context,
    energy_level: str = "epic",
    build_intensity: str = "cinematic",
    breakdown_style: str = "emotional"
) -> str:
    """
    Generate epic progressive house anthem
    
    Args:
        energy_level: moderate/high/epic/euphoric
        build_intensity: gentle/steady/dramatic/cinematic
        breakdown_style: minimal/emotional/epic/orchestral
        
    Returns:
        Complete progressive house anthem generation plan
    """
    initialize_ai_systems()
    
    try:
        request = f"""
        Create an epic progressive house anthem.
        Energy level: {energy_level}
        Build intensity: {build_intensity}
        Breakdown style: {breakdown_style}
        Focus on soaring leads, epic builds, emotional breakdowns, and euphoric drops.
        """
        
        return await generate_complete_track(
            ctx, request, style="progressive_house", bpm=130
        )
        
    except Exception as e:
        logger.error(f"Error creating progressive house anthem: {e}")
        return f"Error creating progressive house anthem: {str(e)}"


# ============================================================================
# UTILITY AND ANALYSIS TOOLS
# ============================================================================

@mcp.tool()
def get_style_characteristics(ctx: Context, style: str) -> str:
    """
    Get detailed characteristics for a musical style
    
    Args:
        style: Musical style name
        
    Returns:
        Detailed style characteristics
    """
    initialize_ai_systems()
    
    try:
        chars = style_analyzer.get_style_characteristics(style)
        
        result = {
            "style": style,
            "bpm_range": chars.bpm_range,
            "key_preferences": chars.key_preferences,
            "chord_progressions": chars.chord_progressions,
            "rhythmic_patterns": chars.rhythmic_patterns,
            "sound_palette": chars.sound_palette,
            "arrangement_style": chars.arrangement_style,
            "signature_techniques": chars.signature_techniques,
            "energy_curve": chars.energy_curve,
            "common_instruments": chars.common_instruments
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting style characteristics: {e}")
        return f"Error getting style characteristics: {str(e)}"


@mcp.tool()
def get_plugin_recommendation(
    ctx: Context, 
    sound_type: str, 
    style: str
) -> str:
    """
    Get Ableton Live stock plugin recommendation for specific sound and style
    
    Args:
        sound_type: Type of sound (bass, lead, pad, kick, etc.)
        style: Musical style
        
    Returns:
        Plugin recommendation with settings
    """
    initialize_ai_systems()
    
    try:
        recommendation = plugin_expert.get_plugin_recommendation(sound_type, style)
        return json.dumps(recommendation, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting plugin recommendation: {e}")
        return f"Error getting plugin recommendation: {str(e)}"


@mcp.tool()
def list_available_styles(ctx: Context) -> str:
    """
    List all available musical styles in the database
    
    Returns:
        List of available styles with descriptions
    """
    initialize_ai_systems()
    
    try:
        styles = style_analyzer.list_available_styles()
        
        style_descriptions = {
            "afro_house": "Organic, African-influenced house music with warm basslines and polyrhythmic percussion",
            "deep_house": "Sophisticated house music with jazz influences and vintage warmth",
            "keinemusik": "Sophisticated deep house with vintage electric pianos and emotional storytelling",
            "progressive_house": "Epic, cinematic house music with soaring leads and dramatic builds",
            "tech_house": "Punchy, tribal-influenced house music with crisp production"
        }
        
        result = {
            "available_styles": styles,
            "descriptions": style_descriptions
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error listing styles: {e}")
        return f"Error listing styles: {str(e)}"


@mcp.tool()
async def chat_with_ai_producer(ctx: Context, message: str) -> str:
    """
    Chat with the AI Music Producer for guidance and advice
    
    Args:
        message: Your question or request
        
    Returns:
        AI Producer response with guidance
    """
    initialize_ai_systems()
    
    try:
        # Start chat session if not already started
        if not orchestrator.chat_session:
            orchestrator.start_chat_session()
        
        response = await orchestrator.chat(message)
        return response
        
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        return f"Error in chat: {str(e)}"


# ============================================================================
# INITIALIZATION AND EXPORT
# ============================================================================

def register_enhanced_tools(server: Server):
    """Register all enhanced tools with the MCP server"""
    
    # High-level generation tools
    server.add_tool(generate_complete_track)
    server.add_tool(analyze_and_replicate_style)
    server.add_tool(create_arrangement_from_elements)
    
    # Style-specific generators
    server.add_tool(create_afro_house_track)
    server.add_tool(create_keinemusik_style_track)
    server.add_tool(create_progressive_house_anthem)
    
    # Utility tools
    server.add_tool(get_style_characteristics)
    server.add_tool(get_plugin_recommendation)
    server.add_tool(list_available_styles)
    server.add_tool(chat_with_ai_producer)
    
    logger.info("Enhanced MCP tools registered successfully")


if __name__ == "__main__":
    # Test the tools
    async def test_tools():
        """Test the enhanced tools"""
        ctx = Context()
        
        print("Testing AI Music Producer Tools...")
        
        # Test style characteristics
        result = get_style_characteristics(ctx, "afro_house")
        print("Style characteristics:", result[:200] + "...")
        
        # Test plugin recommendation
        result = get_plugin_recommendation(ctx, "bass", "afro_house")
        print("Plugin recommendation:", result)
        
        # Test complete track generation
        result = await generate_complete_track(
            ctx, 
            "Create an Afro House track in the style of Black Coffee"
        )
        print("Track generation:", result[:300] + "...")
    
    asyncio.run(test_tools()) 