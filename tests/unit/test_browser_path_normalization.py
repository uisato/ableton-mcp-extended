"""Unit tests for browser category/path normalization in the Remote Script."""
import os
import sys
import types


# Mock Ableton's ControlSurface dependency before importing the Remote Script.
_framework_module = types.ModuleType("_Framework")
_control_surface_module = types.ModuleType("_Framework.ControlSurface")


class _DummyControlSurface:
    pass


_control_surface_module.ControlSurface = _DummyControlSurface
sys.modules["_Framework"] = _framework_module
sys.modules["_Framework.ControlSurface"] = _control_surface_module

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from AbletonMCP_Remote_Script import AbletonMCP  # noqa: E402


class _FakeItem:
    def __init__(self, name, children=None, is_device=False, is_loadable=False, uri=None):
        self.name = name
        self.children = children or []
        self.is_device = is_device
        self.is_loadable = is_loadable
        self.uri = uri or "uri:{0}".format(name)
        self.is_folder = bool(self.children)


def _make_surface_with_browser(browser):
    """Create an AbletonMCP instance without running ControlSurface init."""
    surface = AbletonMCP.__new__(AbletonMCP)
    surface.log_message = lambda _msg: None
    surface.application = lambda: types.SimpleNamespace(browser=browser)
    return surface


def test_normalize_browser_category_aliases():
    surface = AbletonMCP.__new__(AbletonMCP)

    # Hyphen and spaced variants should normalize to canonical snake_case roots.
    assert surface._normalize_browser_category_name("audio-effects") == "audio_effects"
    assert surface._normalize_browser_category_name("Audio Effects") == "audio_effects"
    # Common shorthand should map to the same canonical category.
    assert surface._normalize_browser_category_name("midi fx") == "midi_effects"
    # Plugin-format aliases should normalize to the plugins root.
    assert surface._normalize_browser_category_name("vst3") == "plugins"


def test_split_browser_path_trims_and_drops_empty_parts():
    surface = AbletonMCP.__new__(AbletonMCP)

    # Leading/trailing spaces and duplicate slashes should be cleaned.
    assert surface._split_browser_path(" /instruments//Pianos/ ") == ["instruments", "Pianos"]
    # Empty input should produce no path parts.
    assert surface._split_browser_path("") == []


def test_get_browser_item_resolves_instruments_root_typo_regression():
    # Regression test for old typo path check ("nstruments") that broke
    # valid "instruments/..." paths.
    pianos = _FakeItem("Pianos")
    browser = types.SimpleNamespace(
        instruments=_FakeItem("Instruments", children=[pianos]),
        sounds=_FakeItem("Sounds"),
        drums=_FakeItem("Drums"),
        audio_effects=_FakeItem("Audio Effects"),
        midi_effects=_FakeItem("MIDI Effects"),
        plugins=_FakeItem("Plugins"),
    )
    surface = _make_surface_with_browser(browser)

    # A normal instruments path should now resolve correctly.
    result = surface._get_browser_item(uri=None, path="instruments/Pianos")

    # The path lookup should find the expected child node.
    assert result["found"] is True
    assert result["item"]["name"] == "Pianos"


def test_get_browser_items_at_path_normalizes_hyphenated_audio_effects():
    compressor = _FakeItem("Compressor", is_device=True, is_loadable=True)
    dynamics = _FakeItem("Dynamics", children=[compressor])
    browser = types.SimpleNamespace(
        instruments=_FakeItem("Instruments"),
        sounds=_FakeItem("Sounds"),
        drums=_FakeItem("Drums"),
        audio_effects=_FakeItem("Audio Effects", children=[dynamics]),
        midi_effects=_FakeItem("MIDI Effects"),
        plugins=_FakeItem("Plugins"),
    )
    surface = _make_surface_with_browser(browser)

    # Hyphenated root alias should resolve to audio_effects.
    result = surface.get_browser_items_at_path("audio-effects/Dynamics")

    # After root normalization, path traversal should return the folder contents.
    assert result["name"] == "Dynamics"
    assert len(result["items"]) == 1
    assert result["items"][0]["name"] == "Compressor"


def test_get_browser_items_at_path_normalizes_vst_alias_to_plugins():
    synth = _FakeItem("MegaSynth", is_device=True, is_loadable=True)
    vendor = _FakeItem("Acme", children=[synth])
    browser = types.SimpleNamespace(
        instruments=_FakeItem("Instruments"),
        sounds=_FakeItem("Sounds"),
        drums=_FakeItem("Drums"),
        audio_effects=_FakeItem("Audio Effects"),
        midi_effects=_FakeItem("MIDI Effects"),
        plugins=_FakeItem("Plugins", children=[vendor]),
    )
    surface = _make_surface_with_browser(browser)

    # vst3 should normalize to plugins, then navigate to vendor folder.
    result = surface.get_browser_items_at_path("vst3/Acme")

    # The resolved folder should expose its plugin child.
    assert result["name"] == "Acme"
    assert result["items"][0]["name"] == "MegaSynth"


def test_get_browser_items_at_path_unknown_category_error_is_normalized():
    browser = types.SimpleNamespace(
        instruments=_FakeItem("Instruments"),
        sounds=_FakeItem("Sounds"),
        drums=_FakeItem("Drums"),
        midi_effects=_FakeItem("MIDI Effects"),
    )
    surface = _make_surface_with_browser(browser)

    # "audio fx" normalizes to audio_effects, but that root is intentionally absent.
    result = surface.get_browser_items_at_path("audio fx/Utility")

    # Error should clearly report unknown category using normalized name.
    assert "Unknown or unavailable category" in result["error"]
    assert "audio_effects" in result["error"]
