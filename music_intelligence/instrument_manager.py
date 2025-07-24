#!/usr/bin/env python3
"""
Instrument Manager - Local Caching and Intelligent Selection

This module handles:
- Querying MCP server for available instruments and drum kits
- Caching the data locally for performance
- Providing intelligent genre-based instrument suggestions
- Managing instrument library updates
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class InstrumentManager:
    """Manages local instrument caching and intelligent selection"""
    
    def __init__(self, cache_dir: str = "instrument_cache"):
        """Initialize the instrument manager"""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache file paths
        self.instruments_cache = self.cache_dir / "instruments.json"
        self.drum_kits_cache = self.cache_dir / "drum_kits.json"
        self.metadata_cache = self.cache_dir / "cache_metadata.json"
        
        # Cache expiry (24 hours)
        self.cache_expiry_hours = 24
        
        # Genre-specific mappings
        self.genre_instrument_mapping = {
            'deep house': {
                'drums': ['64 Pads Dub Techno Kit.adg', 'House Kit.adg', '64 Pad Kit Deep House.adg'],
                'bass': ['Bass', 'Analog', 'Wavetable'],
                'lead': ['Analog', 'Drift', 'Wavetable'],
                'pads': ['Drift', 'Analog', 'Emit'],
                'arp': ['Analog', 'Electric']
            },
            'tech house': {
                'drums': ['64 Pad Kit Tech House.adg', 'Techno Kit.adg', 'Drum Rack'],
                'bass': ['Bass', 'Analog', 'Operator'],
                'lead': ['Analog', 'Wavetable', 'Operator'],
                'pads': ['Drift', 'Analog', 'Wavetable'],
                'arp': ['Analog', 'Electric']
            },
            'trap': {
                'drums': ['Trap Kit.adg', 'Hip Hop Kit.adg', 'Drum Rack'],
                'bass': ['Bass', 'Analog', 'Operator'],
                'lead': ['Analog', 'Drift', 'Wavetable'],
                'pads': ['Drift', 'Emit', 'Analog'],
                'arp': ['Electric', 'Analog']
            },
            'jazz': {
                'drums': ['32 Pad Kit Jazz.adg', '64 Pad Kit Jazz.adg', 'Vintage Kit.adg'],
                'bass': ['Electric', 'Bass'],
                'lead': ['Electric', 'Collision', 'Meld'],
                'pads': ['Electric', 'Collision', 'Meld'],
                'piano': ['Electric']
            },
            'rock': {
                'drums': ['32 Pad Kit Rock.adg', '64 Pad Kit Rock.adg', 'Live Kit.adg'],
                'bass': ['Bass', 'Electric'],
                'lead': ['Analog', 'Electric', 'Tension'],
                'pads': ['Analog', 'Electric'],
                'organ': ['Electric']
            },
            'afro house': {
                'drums': ['Afro Kit.adg', '64 Pads Dub Techno Kit.adg', 'World Kit.adg'],
                'bass': ['Bass', 'Analog'],
                'lead': ['Analog', 'Drift'],
                'pads': ['Drift', 'Emit'],
                'perc': ['Drum Rack', 'Impulse']
            },
            'progressive house': {
                'drums': ['Progressive Kit.adg', '64 Pad Kit Progressive.adg', 'House Kit.adg'],
                'bass': ['Bass', 'Analog', 'Wavetable'],
                'lead': ['Wavetable', 'Analog', 'Drift'],
                'pads': ['Drift', 'Wavetable', 'Analog'],
                'arp': ['Analog', 'Wavetable']
            }
        }
        
        logger.info(f"InstrumentManager initialized with cache at {self.cache_dir}")
    
    def is_cache_valid(self) -> bool:
        """Check if the cache is still valid (not expired)"""
        if not self.metadata_cache.exists():
            return False
            
        try:
            with open(self.metadata_cache, 'r') as f:
                metadata = json.load(f)
            
            last_update = datetime.fromisoformat(metadata.get('last_update', '2000-01-01'))
            expiry_time = last_update + timedelta(hours=self.cache_expiry_hours)
            
            return datetime.now() < expiry_time
            
        except Exception as e:
            logger.warning(f"Could not read cache metadata: {e}")
            return False
    
    async def update_cache_from_mcp(self, connection) -> bool:
        """Update the instrument cache by querying the MCP server"""
        try:
            logger.info("🔄 Updating instrument cache from Ableton...")
            
            # Get instruments
            instruments_result = connection.send_command('get_browser_items_at_path', {'path': 'instruments'})
            if instruments_result.get('status') != 'success':
                logger.error(f"Failed to get instruments: {instruments_result}")
                return False
            
            # Get drum kits  
            drums_result = connection.send_command('get_browser_items_at_path', {'path': 'drums'})
            if drums_result.get('status') != 'success':
                logger.error(f"Failed to get drum kits: {drums_result}")
                return False
            
            # Process and categorize instruments
            instruments_data = self._process_instruments(instruments_result.get('items', []))
            drum_kits_data = self._process_drum_kits(drums_result.get('items', []))
            
            # Save to cache
            with open(self.instruments_cache, 'w') as f:
                json.dump(instruments_data, f, indent=2)
            
            with open(self.drum_kits_cache, 'w') as f:
                json.dump(drum_kits_data, f, indent=2)
            
            # Update metadata
            metadata = {
                'last_update': datetime.now().isoformat(),
                'instruments_count': len(instruments_data.get('all', [])),
                'drum_kits_count': len(drum_kits_data.get('all', [])),
                'categories': list(instruments_data.keys())
            }
            
            with open(self.metadata_cache, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"✅ Cache updated: {metadata['instruments_count']} instruments, {metadata['drum_kits_count']} drum kits")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update cache: {e}")
            return False
    
    def _process_instruments(self, raw_instruments: List[Dict]) -> Dict[str, List[Dict]]:
        """Process and categorize instruments"""
        categories = {
            'synthesizers': [],
            'bass': [],
            'melodic': [],
            'atmospheric': [],
            'electronic': [],
            'all': []
        }
        
        for inst in raw_instruments:
            if not inst.get('is_loadable', False):
                continue
                
            name = inst.get('name', 'Unknown')
            name_lower = name.lower()
            
            processed_inst = {
                'name': name,
                'uri': inst.get('uri', ''),
                'category': 'other'
            }
            
            # Categorize by name patterns
            if any(x in name_lower for x in ['bass']):
                processed_inst['category'] = 'bass'
                categories['bass'].append(processed_inst)
            elif any(x in name_lower for x in ['analog', 'drift', 'wavetable', 'operator', 'poli']):
                processed_inst['category'] = 'synthesizers'
                categories['synthesizers'].append(processed_inst)
            elif any(x in name_lower for x in ['electric', 'collision', 'meld', 'tension']):
                processed_inst['category'] = 'melodic'
                categories['melodic'].append(processed_inst)
            elif any(x in name_lower for x in ['emit', 'vector', 'tree']):
                processed_inst['category'] = 'atmospheric'
                categories['atmospheric'].append(processed_inst)
            else:
                processed_inst['category'] = 'electronic'
                categories['electronic'].append(processed_inst)
            
            categories['all'].append(processed_inst)
        
        return categories
    
    def _process_drum_kits(self, raw_drums: List[Dict]) -> Dict[str, List[Dict]]:
        """Process and categorize drum kits"""
        categories = {
            'house': [],
            'techno': [],
            'trap': [],
            'jazz': [],
            'rock': [],
            'world': [],
            'vintage': [],
            'all': []
        }
        
        for kit in raw_drums:
            if not kit.get('is_loadable', False) or not kit.get('name', '').endswith('.adg'):
                continue
                
            name = kit.get('name', 'Unknown')
            name_lower = name.lower()
            
            processed_kit = {
                'name': name,
                'uri': kit.get('uri', ''),
                'category': 'general'
            }
            
            # Categorize by name patterns
            if any(x in name_lower for x in ['house', 'deep', 'tech']):
                processed_kit['category'] = 'house'
                categories['house'].append(processed_kit)
            elif any(x in name_lower for x in ['techno', 'dub']):
                processed_kit['category'] = 'techno'
                categories['techno'].append(processed_kit)
            elif any(x in name_lower for x in ['trap', 'hip hop', 'rap']):
                processed_kit['category'] = 'trap'
                categories['trap'].append(processed_kit)
            elif any(x in name_lower for x in ['jazz', 'swing']):
                processed_kit['category'] = 'jazz'
                categories['jazz'].append(processed_kit)
            elif any(x in name_lower for x in ['rock', 'live', 'acoustic']):
                processed_kit['category'] = 'rock'
                categories['rock'].append(processed_kit)
            elif any(x in name_lower for x in ['world', 'afro', 'latin']):
                processed_kit['category'] = 'world'
                categories['world'].append(processed_kit)
            elif any(x in name_lower for x in ['vintage', '70', '80', '90']):
                processed_kit['category'] = 'vintage'
                categories['vintage'].append(processed_kit)
            
            categories['all'].append(processed_kit)
        
        return categories
    
    def get_cached_instruments(self) -> Optional[Dict[str, List[Dict]]]:
        """Get cached instruments data"""
        if not self.instruments_cache.exists():
            return None
            
        try:
            with open(self.instruments_cache, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load cached instruments: {e}")
            return None
    
    def get_cached_drum_kits(self) -> Optional[Dict[str, List[Dict]]]:
        """Get cached drum kits data"""
        if not self.drum_kits_cache.exists():
            return None
            
        try:
            with open(self.drum_kits_cache, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load cached drum kits: {e}")
            return None
    
    def suggest_instruments_for_genre(self, genre: str, track_types: List[str]) -> Dict[str, Any]:
        """Get intelligent instrument suggestions for a genre"""
        genre_lower = genre.lower()
        
        # Get cached data
        instruments = self.get_cached_instruments()
        drum_kits = self.get_cached_drum_kits()
        
        suggestions = {
            'genre': genre,
            'recommendations': {},
            'available_alternatives': {},
            'cache_status': 'available' if instruments and drum_kits else 'unavailable'
        }
        
        # Get genre-specific recommendations
        genre_map = self.genre_instrument_mapping.get(genre_lower, {})
        
        for track_type in track_types:
            track_type_lower = track_type.lower()
            
            # Get preferred instruments for this genre/track type
            preferred = genre_map.get(track_type_lower, [])
            
            if track_type_lower == 'drums':
                # Find matching drum kits
                available_kits = []
                if drum_kits:
                    for kit in drum_kits.get('all', []):
                        kit_name = kit['name']
                        if any(pref in kit_name for pref in preferred):
                            available_kits.append(kit_name)
                
                suggestions['recommendations'][track_type] = {
                    'preferred': preferred,
                    'available': available_kits[:5],  # Top 5 matches
                    'fallback': 'Drum Rack'
                }
            else:
                # Find matching instruments
                available_instruments = []
                if instruments:
                    for inst in instruments.get('all', []):
                        inst_name = inst['name']
                        if any(pref in inst_name for pref in preferred):
                            available_instruments.append(inst_name)
                
                suggestions['recommendations'][track_type] = {
                    'preferred': preferred,
                    'available': available_instruments[:5],  # Top 5 matches
                    'fallback': preferred[0] if preferred else 'Analog'
                }
        
        return suggestions
    
    def get_formatted_instrument_data_for_ai(self) -> str:
        """Get formatted instrument data for AI consumption"""
        instruments = self.get_cached_instruments()
        drum_kits = self.get_cached_drum_kits()
        
        if not instruments or not drum_kits:
            return "Instrument cache not available. Using basic instrument knowledge."
        
        # Format for AI
        formatted = f"""
📊 ABLETON LIVE INSTRUMENT LIBRARY (Cached Data):

🎹 SYNTHESIZERS ({len(instruments.get('synthesizers', []))}):
{chr(10).join([f"  • {inst['name']}" for inst in instruments.get('synthesizers', [])[:10]])}

🎸 BASS INSTRUMENTS ({len(instruments.get('bass', []))}):
{chr(10).join([f"  • {inst['name']}" for inst in instruments.get('bass', [])[:10]])}

🎵 MELODIC INSTRUMENTS ({len(instruments.get('melodic', []))}):
{chr(10).join([f"  • {inst['name']}" for inst in instruments.get('melodic', [])[:10]])}

🌫️ ATMOSPHERIC ({len(instruments.get('atmospheric', []))}):
{chr(10).join([f"  • {inst['name']}" for inst in instruments.get('atmospheric', [])[:10]])}

🥁 DRUM KITS ({len(drum_kits.get('all', []))}):
House/Techno: {', '.join([kit['name'] for kit in drum_kits.get('house', [])[:5]])}
Jazz: {', '.join([kit['name'] for kit in drum_kits.get('jazz', [])[:5]])}
Rock: {', '.join([kit['name'] for kit in drum_kits.get('rock', [])[:5]])}
Trap: {', '.join([kit['name'] for kit in drum_kits.get('trap', [])[:3]])}

💡 Use these specific instrument names for optimal sound selection.
"""
        
        return formatted.strip() 