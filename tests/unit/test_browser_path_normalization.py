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


def test_get_browser_tree_recurses_into_folder_children():
    # Tree should expose nested folders so callers can see structure, not just root.
    bass = _FakeItem("Bass")
    lead = _FakeItem("Lead")
    operator = _FakeItem("Operator", children=[bass, lead])
    analog = _FakeItem("Analog", is_device=True, is_loadable=True)
    instruments = _FakeItem("Instruments", children=[analog, operator])
    browser = types.SimpleNamespace(
        instruments=instruments,
        sounds=_FakeItem("Sounds"),
        drums=_FakeItem("Drums"),
        audio_effects=_FakeItem("Audio Effects"),
        midi_effects=_FakeItem("MIDI Effects"),
    )
    surface = _make_surface_with_browser(browser)

    result = surface.get_browser_tree("instruments")

    categories = result["categories"]
    assert len(categories) == 1
    root = categories[0]
    assert root["name"] == "Instruments"
    child_names = sorted(c["name"] for c in root["children"])
    assert child_names == ["Analog", "Operator"]
    operator_node = next(c for c in root["children"] if c["name"] == "Operator")
    grandchild_names = sorted(c["name"] for c in operator_node["children"])
    assert grandchild_names == ["Bass", "Lead"]


def test_get_browser_tree_reports_total_folder_count():
    # total_folders should reflect every folder node visited in the tree.
    bass_presets = _FakeItem("Bass", children=[_FakeItem("Sub.adv", is_loadable=True)])
    operator = _FakeItem("Operator", children=[bass_presets])
    instruments = _FakeItem("Instruments", children=[operator, _FakeItem("Analog")])
    browser = types.SimpleNamespace(
        instruments=instruments,
        sounds=_FakeItem("Sounds"),
        drums=_FakeItem("Drums"),
        audio_effects=_FakeItem("Audio Effects"),
        midi_effects=_FakeItem("MIDI Effects"),
    )
    surface = _make_surface_with_browser(browser)

    result = surface.get_browser_tree("instruments")

    # Three folder nodes: Instruments, Operator, Bass. Analog and Sub.adv are leaves.
    assert result["total_folders"] == 3


def test_get_browser_tree_includes_navigable_path_per_node():
    # Tree paths must be usable as input to get_browser_items_at_path.
    bass = _FakeItem("Bass")
    operator = _FakeItem("Operator", children=[bass])
    instruments = _FakeItem("Instruments", children=[operator])
    browser = types.SimpleNamespace(
        instruments=instruments,
        sounds=_FakeItem("Sounds"),
        drums=_FakeItem("Drums"),
        audio_effects=_FakeItem("Audio Effects"),
        midi_effects=_FakeItem("MIDI Effects"),
    )
    surface = _make_surface_with_browser(browser)

    result = surface.get_browser_tree("instruments")
    operator_node = result["categories"][0]["children"][0]
    bass_node = operator_node["children"][0]

    assert operator_node["path"] == "Instruments/Operator"
    assert bass_node["path"] == "Instruments/Operator/Bass"


def test_get_browser_tree_caps_children_and_marks_has_more():
    # Drums has hundreds of leaf children. Tree must cap and signal truncation.
    many = [_FakeItem("Kit{0}.adg".format(i), is_loadable=True) for i in range(50)]
    drums = _FakeItem("Drums", children=many)
    browser = types.SimpleNamespace(
        instruments=_FakeItem("Instruments"),
        sounds=_FakeItem("Sounds"),
        drums=drums,
        audio_effects=_FakeItem("Audio Effects"),
        midi_effects=_FakeItem("MIDI Effects"),
    )
    surface = _make_surface_with_browser(browser)

    result = surface.get_browser_tree("drums")
    drums_node = result["categories"][0]

    assert drums_node["has_more"] is True
    assert len(drums_node["children"]) < 50


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
