"""Plugin parameter alias registry for known VST/AU plugins.

Maps friendly parameter names to real parameter names exposed by
the Live API. Used by MCP tools to resolve user-friendly names
before sending commands to the Remote Script.
"""

from typing import Optional, Dict

# Registry of known plugins with friendly parameter aliases and categories.
# Each plugin entry has:
#   "aliases": {friendly_name: real_param_name}
#   "categories": {category_name: [param_name_prefixes]}
KNOWN_PLUGINS: Dict[str, dict] = {
    "Serum": {
        "aliases": {
            "wavetable position": "Osc A WT Pos",
            "wavetable position a": "Osc A WT Pos",
            "wavetable position b": "Osc B WT Pos",
            "osc a level": "Osc A Level",
            "osc b level": "Osc B Level",
            "osc a pan": "Osc A Pan",
            "osc b pan": "Osc B Pan",
            "osc a unison": "Osc A Unison",
            "osc b unison": "Osc B Unison",
            "osc a detune": "Osc A UniDet",
            "osc b detune": "Osc B UniDet",
            "osc a octave": "Osc A Oct",
            "osc b octave": "Osc B Oct",
            "osc a semi": "Osc A Semi",
            "osc b semi": "Osc B Semi",
            "osc a fine": "Osc A Fine",
            "osc b fine": "Osc B Fine",
            "filter cutoff": "Fil Cutoff",
            "filter resonance": "Fil Reso",
            "filter drive": "Fil Drive",
            "filter mix": "Fil Mix",
            "filter pan": "Fil Pan",
            "filter fat": "Fil Fat",
            "noise level": "Noise Level",
            "noise pan": "Noise Pan",
            "sub level": "Sub Level",
            "sub pan": "Sub Pan",
            "macro 1": "Macro 1",
            "macro 2": "Macro 2",
            "macro 3": "Macro 3",
            "macro 4": "Macro 4",
            "macro 5": "Macro 5",
            "macro 6": "Macro 6",
            "macro 7": "Macro 7",
            "macro 8": "Macro 8",
            "master volume": "Master Vol",
        },
        "categories": {
            "Oscillator A": ["Osc A"],
            "Oscillator B": ["Osc B"],
            "Filter": ["Fil "],
            "Noise": ["Noise"],
            "Sub": ["Sub "],
            "Envelope": ["Env "],
            "LFO": ["LFO"],
            "Macro": ["Macro"],
            "Effects": ["FX"],
            "Master": ["Master"],
        },
    },
}


def resolve_alias(device_name: str, friendly_name: str) -> Optional[str]:
    """Resolve a friendly parameter name to the real parameter name.

    Returns the real parameter name if found, or None if no alias exists.
    Matching is case-insensitive on the friendly name.
    """
    profile = _find_profile(device_name)
    if profile is None:
        return None
    aliases = profile.get("aliases", {})
    friendly_lower = friendly_name.lower()
    for alias, real_name in aliases.items():
        if alias.lower() == friendly_lower:
            return real_name
    return None


def get_categories(device_name: str) -> Optional[Dict[str, list]]:
    """Get category definitions for a known plugin.

    Returns a dict of {category_name: [param_name_prefixes]},
    or None if the plugin is not in the registry.
    """
    profile = _find_profile(device_name)
    if profile is None:
        return None
    return profile.get("categories")


def get_alias_for_param(device_name: str, param_name: str) -> Optional[str]:
    """Get the friendly alias for a real parameter name.

    Returns the friendly alias if found, or None.
    """
    profile = _find_profile(device_name)
    if profile is None:
        return None
    aliases = profile.get("aliases", {})
    for alias, real_name in aliases.items():
        if real_name == param_name:
            return alias
    return None


def _find_profile(device_name: str) -> Optional[dict]:
    """Find a plugin profile by device name (case-insensitive contains)."""
    name_lower = device_name.lower()
    for plugin_name, profile in KNOWN_PLUGINS.items():
        if plugin_name.lower() in name_lower:
            return profile
    return None
