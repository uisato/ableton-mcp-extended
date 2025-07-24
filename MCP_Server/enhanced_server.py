#!/usr/bin/env python3
"""
Enhanced MCP Server with Full Instrument Library Access

This server exposes Ableton's complete instrument library to Gemini,
allowing intelligent instrument selection based on musical style.
"""

import mcp
from mcp.server.fastmcp import FastMCP
from MCP_Server.server import AbletonConnection, get_ableton_connection
import json
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize enhanced MCP server
mcp = FastMCP("Enhanced Ableton MCP Server")

@mcp.tool()
def get_available_instruments(ctx) -> str:
    """
    Get the complete list of available instruments in Ableton Live.
    Returns instruments categorized by type for intelligent selection.
    """
    try:
        ableton = get_ableton_connection()
        
        # Get all instruments
        result = ableton.send_command('get_browser_items_at_path', {'path': 'instruments'})
        
        # Fix: Handle the actual response format
        if 'items' in result:
            instruments = result['items']
        else:
            return f"❌ Unexpected response format: {result}"
            
        # Categorize instruments
        categories = {
            'Synthesizers': [],
            'Bass_Instruments': [],
            'Drum_Instruments': [],
            'Melodic_Instruments': [],
            'Atmospheric': [],
            'Electronic': [],
            'Other': []
        }
        
        for inst in instruments:
            name = inst.get('name', 'Unknown')
            is_loadable = inst.get('is_loadable', False)
            
            if not is_loadable:
                continue
                
            # Categorize by name patterns
            name_lower = name.lower()
            if any(x in name_lower for x in ['bass']):
                categories['Bass_Instruments'].append({
                    'name': name,
                    'uri': inst.get('uri', ''),
                    'description': 'Bass synthesizer/instrument'
                })
            elif any(x in name_lower for x in ['drum', 'impulse']):
                categories['Drum_Instruments'].append({
                    'name': name,
                    'uri': inst.get('uri', ''),
                    'description': 'Drum machine/sampler'
                })
            elif any(x in name_lower for x in ['analog', 'drift', 'wavetable', 'operator', 'poli']):
                categories['Synthesizers'].append({
                    'name': name,
                    'uri': inst.get('uri', ''),
                    'description': 'Synthesizer for leads, pads, arpeggios'
                })
            elif any(x in name_lower for x in ['electric', 'collision', 'meld', 'tension']):
                categories['Melodic_Instruments'].append({
                    'name': name,
                    'uri': inst.get('uri', ''),
                    'description': 'Melodic instrument (piano, mallet, strings)'
                })
            elif any(x in name_lower for x in ['emit', 'vector', 'tree']):
                categories['Atmospheric'].append({
                    'name': name,
                    'uri': inst.get('uri', ''),
                    'description': 'Atmospheric/textural instrument'
                })
            elif any(x in name_lower for x in ['ds ', 'sampler', 'simpler']):
                categories['Electronic'].append({
                    'name': name,
                    'uri': inst.get('uri', ''),
                    'description': 'Electronic/digital instrument'
                })
            else:
                categories['Other'].append({
                    'name': name,
                    'uri': inst.get('uri', ''),
                    'description': 'Other instrument'
                })
        
        return f"""📊 AVAILABLE INSTRUMENTS IN ABLETON LIVE:

🎹 SYNTHESIZERS ({len(categories['Synthesizers'])}):
{chr(10).join([f"  • {inst['name']}: {inst['description']}" for inst in categories['Synthesizers']])}

🎸 BASS INSTRUMENTS ({len(categories['Bass_Instruments'])}):
{chr(10).join([f"  • {inst['name']}: {inst['description']}" for inst in categories['Bass_Instruments']])}

🥁 DRUM INSTRUMENTS ({len(categories['Drum_Instruments'])}):
{chr(10).join([f"  • {inst['name']}: {inst['description']}" for inst in categories['Drum_Instruments']])}

🎵 MELODIC INSTRUMENTS ({len(categories['Melodic_Instruments'])}):
{chr(10).join([f"  • {inst['name']}: {inst['description']}" for inst in categories['Melodic_Instruments']])}

🌫️ ATMOSPHERIC ({len(categories['Atmospheric'])}):
{chr(10).join([f"  • {inst['name']}: {inst['description']}" for inst in categories['Atmospheric']])}

⚡ ELECTRONIC ({len(categories['Electronic'])}):
{chr(10).join([f"  • {inst['name']}: {inst['description']}" for inst in categories['Electronic']])}

🔧 OTHER ({len(categories['Other'])}):
{chr(10).join([f"  • {inst['name']}: {inst['description']}" for inst in categories['Other']])}

💡 USAGE: Use load_specific_instrument() with the exact instrument name to load any of these."""
        
    except Exception as e:
        logger.error(f"Error getting instruments: {str(e)}")
        return f"❌ Error getting instruments: {str(e)}"

@mcp.tool()
def get_available_drum_kits(ctx) -> str:
    """
    Get the complete list of available drum kits and presets.
    Returns drum kits categorized by genre/style for intelligent selection.
    """
    try:
        ableton = get_ableton_connection()
        
        # Get all drums
        result = ableton.send_command('get_browser_items_at_path', {'path': 'drums'})
        
        # Fix: Handle the actual response format
        if 'items' in result:
            drums = result['items']
        else:
            return f"❌ Unexpected response format: {result}"
        
        # Filter loadable drum kits
        drum_kits = [d for d in drums if d.get('is_loadable', False) and '.adg' in d.get('name', '')]
        
        # Categorize by style
        categories = {
            'Electronic/Techno': [],
            'Hip_Hop/Trap': [],
            'Jazz/Acoustic': [],
            'Rock/Pop': [],
            'House/Dance': [],
            'Vintage_Machines': [],
            'Experimental': [],
            'General': []
        }
        
        for kit in drum_kits[:100]:  # First 100 for readability
            name = kit.get('name', 'Unknown')
            name_lower = name.lower()
            
            kit_info = {
                'name': name,
                'uri': kit.get('uri', '')
            }
            
            if any(x in name_lower for x in ['techno', 'dub', 'electronic', 'minimal', 'acid', 'rave']):
                categories['Electronic/Techno'].append(kit_info)
            elif any(x in name_lower for x in ['hip', 'hop', 'trap', 'drill', 'boom', 'bap']):
                categories['Hip_Hop/Trap'].append(kit_info)
            elif any(x in name_lower for x in ['jazz', 'acoustic', 'brush', 'vintage']):
                categories['Jazz/Acoustic'].append(kit_info)
            elif any(x in name_lower for x in ['rock', 'pop', 'punk', 'metal']):
                categories['Rock/Pop'].append(kit_info)
            elif any(x in name_lower for x in ['house', 'dance', 'club', 'disco']):
                categories['House/Dance'].append(kit_info)
            elif any(x in name_lower for x in ['808', '909', '707', '606', '505']) or 'core kit' in name_lower:
                categories['Vintage_Machines'].append(kit_info)
            elif any(x in name_lower for x in ['experimental', 'glitch', 'noise', 'fx', 'weird']):
                categories['Experimental'].append(kit_info)
            else:
                categories['General'].append(kit_info)
        
        return f"""🥁 AVAILABLE DRUM KITS IN ABLETON LIVE:
        
🤖 ELECTRONIC/TECHNO ({len(categories['Electronic/Techno'])}):
{chr(10).join([f"  • {kit['name']}" for kit in categories['Electronic/Techno'][:8]])}

🎤 HIP HOP/TRAP ({len(categories['Hip_Hop/Trap'])}):
{chr(10).join([f"  • {kit['name']}" for kit in categories['Hip_Hop/Trap'][:8]])}

🏠 HOUSE/DANCE ({len(categories['House/Dance'])}):
{chr(10).join([f"  • {kit['name']}" for kit in categories['House/Dance'][:8]])}

🥁 VINTAGE MACHINES ({len(categories['Vintage_Machines'])}):
{chr(10).join([f"  • {kit['name']}" for kit in categories['Vintage_Machines'][:8]])}

🎷 JAZZ/ACOUSTIC ({len(categories['Jazz/Acoustic'])}):
{chr(10).join([f"  • {kit['name']}" for kit in categories['Jazz/Acoustic'][:8]])}

🎸 ROCK/POP ({len(categories['Rock/Pop'])}):
{chr(10).join([f"  • {kit['name']}" for kit in categories['Rock/Pop'][:8]])}

⚡ EXPERIMENTAL ({len(categories['Experimental'])}):
{chr(10).join([f"  • {kit['name']}" for kit in categories['Experimental'][:8]])}

🎵 GENERAL ({len(categories['General'])}):
{chr(10).join([f"  • {kit['name']}" for kit in categories['General'][:8]])}

Total: {len(drum_kits)} drum kits available
💡 USAGE: Use load_specific_drum_kit() with the exact kit name."""
        
    except Exception as e:
        logger.error(f"Error getting drum kits: {str(e)}")
        return f"❌ Error getting drum kits: {str(e)}"

@mcp.tool()
def load_specific_instrument(ctx, track_index: int, instrument_name: str) -> str:
    """
    Load a specific instrument by its exact name.
    
    Parameters:
    - track_index: The track to load the instrument on
    - instrument_name: Exact name of the instrument (e.g., "Analog", "Bass", "Drift")
    """
    try:
        ableton = get_ableton_connection()
        
        # Get the instrument's URI first
        result = ableton.send_command('get_browser_items_at_path', {'path': 'instruments'})
        
        if result.get('status') == 'success' and 'items' in result:
            instruments = result['items']
            
            # Find the specific instrument
            target_instrument = None
            for inst in instruments:
                if inst.get('name', '').lower() == instrument_name.lower():
                    target_instrument = inst
                    break
            
            if not target_instrument:
                return f"❌ Instrument '{instrument_name}' not found. Use get_available_instruments() to see options."
            
            if not target_instrument.get('is_loadable', False):
                return f"❌ Instrument '{instrument_name}' is not loadable."
            
            # Load the instrument using browser URI
            load_result = ableton.send_command('load_browser_item', {
                'track_index': track_index,
                'item_uri': target_instrument.get('uri', '')
            })
            
            if load_result.get('status') == 'success':
                return f"✅ Loaded '{instrument_name}' on track {track_index}"
            else:
                return f"❌ Failed to load '{instrument_name}': {load_result}"
                
        else:
            return f"❌ Failed to get instruments list: {result}"
            
    except Exception as e:
        logger.error(f"Error loading specific instrument: {str(e)}")
        return f"❌ Error loading instrument: {str(e)}"

@mcp.tool()
def load_specific_drum_kit(ctx, track_index: int, kit_name: str) -> str:
    """
    Load a specific drum kit by its exact name.
    
    Parameters:
    - track_index: The track to load the drum kit on
    - kit_name: Exact name of the drum kit (e.g., "64 Pads Dub Techno Kit.adg")
    """
    try:
        ableton = get_ableton_connection()
        
        # Get the drum kit's URI first
        result = ableton.send_command('get_browser_items_at_path', {'path': 'drums'})
        
        if result.get('status') == 'success' and 'items' in result:
            drums = result['items']
            
            # Find the specific drum kit
            target_kit = None
            for kit in drums:
                if kit.get('name', '').lower() == kit_name.lower():
                    target_kit = kit
                    break
            
            if not target_kit:
                return f"❌ Drum kit '{kit_name}' not found. Use get_available_drum_kits() to see options."
            
            if not target_kit.get('is_loadable', False):
                return f"❌ Drum kit '{kit_name}' is not loadable."
            
            # Load the drum kit using browser URI  
            load_result = ableton.send_command('load_browser_item', {
                'track_index': track_index,
                'item_uri': target_kit.get('uri', '')
            })
            
            if load_result.get('status') == 'success':
                return f"✅ Loaded drum kit '{kit_name}' on track {track_index}"
            else:
                return f"❌ Failed to load drum kit '{kit_name}': {load_result}"
                
        else:
            return f"❌ Failed to get drum kits list: {result}"
            
    except Exception as e:
        logger.error(f"Error loading specific drum kit: {str(e)}")
        return f"❌ Error loading drum kit: {str(e)}"

@mcp.tool()
def suggest_instruments_for_genre(ctx, genre: str, track_types: List[str]) -> str:
    """
    Get AI-curated instrument suggestions for a specific genre.
    
    Parameters:
    - genre: Musical genre (e.g., "deep house", "jazz", "trap", "rock")
    - track_types: List of track types needed (e.g., ["drums", "bass", "lead", "pads"])
    """
    
    # Genre-specific instrument mappings
    genre_suggestions = {
        'deep house': {
            'drums': ['64 Pads Dub Techno Kit.adg', 'Drum Rack'],
            'bass': ['Bass', 'Analog'],
            'lead': ['Analog', 'Drift'],
            'pads': ['Drift', 'Analog'],
            'arp': ['Analog', 'Electric']
        },
        'trap': {
            'drums': ['Drum Rack', 'Impulse'],
            'bass': ['Bass', 'Analog'],
            'lead': ['Analog', 'Drift'],
            'pads': ['Drift', 'Emit'],
            'arp': ['Electric', 'Analog']
        },
        'jazz': {
            'drums': ['32 Pad Kit Jazz.adg', '64 Pad Kit Jazz.adg'],
            'bass': ['Electric', 'Bass'],
            'lead': ['Electric', 'Collision'],
            'pads': ['Electric', 'Collision'],
            'piano': ['Electric']
        },
        'rock': {
            'drums': ['32 Pad Kit Rock.adg', '64 Pad Kit Rock.adg'],
            'bass': ['Bass', 'Electric'],
            'lead': ['Analog', 'Electric'],
            'pads': ['Analog', 'Electric'],
            'organ': ['Electric']
        }
    }
    
    suggestions = genre_suggestions.get(genre.lower(), {})
    
    if not suggestions:
        return f"❌ No specific suggestions for genre '{genre}'. Use get_available_instruments() and get_available_drum_kits() to explore options."
    
    result = f"🎵 INSTRUMENT SUGGESTIONS FOR {genre.upper()}:\n\n"
    
    for track_type in track_types:
        if track_type.lower() in suggestions:
            instruments = suggestions[track_type.lower()]
            result += f"🎛️ {track_type.upper()}:\n"
            for i, inst in enumerate(instruments, 1):
                result += f"  {i}. {inst}\n"
            result += "\n"
        else:
            result += f"⚠️ {track_type.upper()}: No specific suggestions (use general instruments)\n\n"
    
    result += "💡 USAGE:\n"
    result += "- Use load_specific_instrument() for synthesizers\n"
    result += "- Use load_specific_drum_kit() for drum kits\n"
    result += "- These are curated suggestions - explore full library for more options!"
    
    return result

if __name__ == "__main__":
    mcp.run() 