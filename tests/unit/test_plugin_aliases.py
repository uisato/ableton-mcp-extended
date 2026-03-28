"""Unit tests for plugin alias resolution (T037)."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MCP_Server.plugin_aliases import (
    resolve_alias,
    get_alias_for_param,
    get_categories,
    KNOWN_PLUGINS,
)


class TestResolveAlias:
    """Test resolve_alias function."""

    def test_known_alias_serum(self):
        result = resolve_alias("Serum", "wavetable position")
        assert result == "Osc A WT Pos"

    def test_case_insensitive(self):
        result = resolve_alias("Serum", "Wavetable Position")
        assert result == "Osc A WT Pos"

    def test_unknown_alias_returns_none(self):
        result = resolve_alias("Serum", "nonexistent parameter")
        assert result is None

    def test_unknown_plugin_returns_none(self):
        result = resolve_alias("SomeUnknownPlugin", "filter cutoff")
        assert result is None

    def test_real_name_not_resolved_as_alias(self):
        """Direct parameter names should NOT match aliases."""
        result = resolve_alias("Serum", "Osc A WT Pos")
        # "Osc A WT Pos" is a real name, not a friendly alias
        assert result is None

    def test_filter_cutoff(self):
        result = resolve_alias("Serum", "filter cutoff")
        assert result == "Fil Cutoff"

    def test_macro(self):
        result = resolve_alias("Serum", "macro 1")
        assert result == "Macro 1"

    def test_device_name_contains_match(self):
        """Device name may contain extra text like 'Serum FX'."""
        result = resolve_alias("Serum FX", "filter cutoff")
        assert result == "Fil Cutoff"


class TestGetAliasForParam:
    """Test reverse alias lookup."""

    def test_known_param(self):
        result = get_alias_for_param("Serum", "Osc A WT Pos")
        assert result == "wavetable position"

    def test_unknown_param(self):
        result = get_alias_for_param("Serum", "SomeRandomParam")
        assert result is None

    def test_unknown_plugin(self):
        result = get_alias_for_param("UnknownPlugin", "Osc A WT Pos")
        assert result is None


class TestGetCategories:
    """Test category retrieval."""

    def test_serum_has_categories(self):
        cats = get_categories("Serum")
        assert cats is not None
        assert "Oscillator A" in cats
        assert "Filter" in cats

    def test_unknown_plugin_returns_none(self):
        cats = get_categories("UnknownPlugin")
        assert cats is None

    def test_categories_have_prefixes(self):
        cats = get_categories("Serum")
        assert "Osc A" in cats["Oscillator A"]
