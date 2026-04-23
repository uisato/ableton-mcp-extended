"""Unit tests for external plugin listing/loading tools."""
import sys
import os
from unittest.mock import MagicMock, patch
import pytest

# Mock MCP dependencies before importing server module
_mock_mcp_module = MagicMock()
_mock_fastmcp = MagicMock()
_mock_fastmcp.FastMCP.return_value.tool.return_value = lambda fn: fn
sys.modules['mcp'] = _mock_mcp_module
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = _mock_fastmcp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MCP_Server.server import (
    list_external_plugins,
    load_external_plugin,
    _invalidate_external_plugin_cache,
)


@pytest.fixture(autouse=True)
def reset_external_plugin_cache():
    """Ensure tests don't leak plugin discovery cache state."""
    _invalidate_external_plugin_cache()
    yield
    _invalidate_external_plugin_cache()


def _browser_response_for(path, tree):
    """Return canned browser path response or unknown-category error."""
    return tree.get(path, {
        "path": path,
        "error": "Unknown or unavailable category: {0}".format(path.split("/")[0]),
        "items": [],
    })


class TestListExternalPlugins:
    """Tests for list_external_plugins."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_lists_and_filters_plugins_by_query(self, mock_conn):
        # Plugin discovery should recurse under plugins root and include matching names.
        mock_ableton = MagicMock()
        tree = {
            "plugins": {
                "path": "plugins",
                "items": [
                    {"name": "VST3", "is_folder": True, "is_device": False, "is_loadable": False, "uri": "uri:vst3"},
                ],
            },
            "plugins/VST3": {
                "path": "plugins/VST3",
                "items": [
                    {"name": "FabFilter", "is_folder": True, "is_device": False, "is_loadable": False, "uri": "uri:fabfilter"},
                ],
            },
            "plugins/VST3/FabFilter": {
                "path": "plugins/VST3/FabFilter",
                "items": [
                    {"name": "FabFilter Pro-Q 3", "is_folder": False, "is_device": True, "is_loadable": True, "uri": "uri:proq3"},
                    {"name": "FabFilter Pro-C 2", "is_folder": False, "is_device": True, "is_loadable": True, "uri": "uri:proc2"},
                ],
            },
        }

        def side_effect(command, params=None):
            if command == "get_browser_items_at_path":
                return _browser_response_for(params.get("path", ""), tree)
            raise AssertionError("Unexpected command: {0}".format(command))

        mock_ableton.send_command.side_effect = side_effect
        mock_conn.return_value = mock_ableton

        result = list_external_plugins(MagicMock(), query="pro-q", max_results=10)

        assert "FabFilter Pro-Q 3" in result
        assert "FabFilter Pro-C 2" not in result  # Query should narrow results

    @patch('MCP_Server.server.get_ableton_connection')
    def test_returns_error_when_no_plugin_root_available(self, mock_conn):
        # If plugin roots cannot be resolved, tool should return a useful error.
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "error": "Unknown or unavailable category: plugins",
            "items": [],
        }
        mock_conn.return_value = mock_ableton

        result = list_external_plugins(MagicMock())
        assert "Error listing external plugins" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_uses_cache_on_repeated_calls(self, mock_conn):
        # Two list calls without refresh should only trigger one discovery traversal.
        mock_ableton = MagicMock()
        tree = {
            "plugins": {
                "path": "plugins",
                "items": [
                    {"name": "Serum", "is_folder": False, "is_device": True, "is_loadable": True, "uri": "uri:serum"},
                ],
            },
        }

        def side_effect(command, params=None):
            if command == "get_browser_items_at_path":
                return _browser_response_for(params.get("path", ""), tree)
            raise AssertionError("Unexpected command: {0}".format(command))

        mock_ableton.send_command.side_effect = side_effect
        mock_conn.return_value = mock_ableton

        first = list_external_plugins(MagicMock(), query="", max_results=10)
        second = list_external_plugins(MagicMock(), query="", max_results=10)

        assert "Serum" in first
        assert "Serum" in second
        # First traversal asks only for the plugins root in this tree.
        assert mock_ableton.send_command.call_count == 1

    @patch('MCP_Server.server.get_ableton_connection')
    def test_refresh_cache_forces_rescan(self, mock_conn):
        # refresh_cache=True should bypass cached discovery and call browser again.
        mock_ableton = MagicMock()
        tree = {
            "plugins": {
                "path": "plugins",
                "items": [
                    {"name": "Diva", "is_folder": False, "is_device": True, "is_loadable": True, "uri": "uri:diva"},
                ],
            },
        }

        def side_effect(command, params=None):
            if command == "get_browser_items_at_path":
                return _browser_response_for(params.get("path", ""), tree)
            raise AssertionError("Unexpected command: {0}".format(command))

        mock_ableton.send_command.side_effect = side_effect
        mock_conn.return_value = mock_ableton

        list_external_plugins(MagicMock(), query="", max_results=10)
        list_external_plugins(MagicMock(), query="", max_results=10, refresh_cache=True)

        assert mock_ableton.send_command.call_count == 2

    @patch('MCP_Server.server.get_ableton_connection')
    def test_many_plugins_respects_max_results_limit(self, mock_conn):
        # Large plugin inventories should be truncated to max_results in output.
        mock_ableton = MagicMock()
        many_items = [
            {
                "name": "Plugin {0:03d}".format(i),
                "is_folder": False,
                "is_device": True,
                "is_loadable": True,
                "uri": "uri:plugin_{0:03d}".format(i),
            }
            for i in range(1, 61)
        ]
        tree = {
            "plugins": {
                "path": "plugins",
                "items": many_items,
            },
        }

        def side_effect(command, params=None):
            if command == "get_browser_items_at_path":
                return _browser_response_for(params.get("path", ""), tree)
            raise AssertionError("Unexpected command: {0}".format(command))

        mock_ableton.send_command.side_effect = side_effect
        mock_conn.return_value = mock_ableton

        result = list_external_plugins(MagicMock(), max_results=10)
        listing_lines = [line for line in result.splitlines() if line.startswith("  ")]

        assert "showing 10" in result
        assert len(listing_lines) == 10
        assert "Use max_results=60" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_many_plugins_are_sorted_in_listing(self, mock_conn):
        # Results should be name-sorted for stable UX on large inventories.
        mock_ableton = MagicMock()
        tree = {
            "plugins": {
                "path": "plugins",
                "items": [
                    {"name": "ZuluSynth", "is_folder": False, "is_device": True, "is_loadable": True, "uri": "uri:zulu"},
                    {"name": "AlphaVerb", "is_folder": False, "is_device": True, "is_loadable": True, "uri": "uri:alpha"},
                    {"name": "BetaEQ", "is_folder": False, "is_device": True, "is_loadable": True, "uri": "uri:beta"},
                ],
            },
        }

        def side_effect(command, params=None):
            if command == "get_browser_items_at_path":
                return _browser_response_for(params.get("path", ""), tree)
            raise AssertionError("Unexpected command: {0}".format(command))

        mock_ableton.send_command.side_effect = side_effect
        mock_conn.return_value = mock_ableton

        result = list_external_plugins(MagicMock(), max_results=10)
        assert result.index("AlphaVerb") < result.index("BetaEQ") < result.index("ZuluSynth")


class TestLoadExternalPlugin:
    """Tests for load_external_plugin."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_loads_best_match_and_converts_track_index(self, mock_conn):
        # Should match by name and send load_browser_item with 0-based track index.
        mock_ableton = MagicMock()
        tree = {
            "plugins": {
                "path": "plugins",
                "items": [
                    {"name": "VST3", "is_folder": True, "is_device": False, "is_loadable": False, "uri": "uri:vst3"},
                ],
            },
            "plugins/VST3": {
                "path": "plugins/VST3",
                "items": [
                    {"name": "FabFilter Pro-Q 3", "is_folder": False, "is_device": True, "is_loadable": True, "uri": "uri:proq3"},
                ],
            },
        }

        def side_effect(command, params=None):
            if command == "get_browser_items_at_path":
                return _browser_response_for(params.get("path", ""), tree)
            if command == "load_browser_item":
                return {"loaded": True, "item_name": "FabFilter Pro-Q 3"}
            raise AssertionError("Unexpected command: {0}".format(command))

        mock_ableton.send_command.side_effect = side_effect
        mock_conn.return_value = mock_ableton

        result = load_external_plugin(MagicMock(), track_index=2, plugin_name="FabFilter Pro-Q 3")

        assert "Loaded external plugin 'FabFilter Pro-Q 3'" in result
        load_calls = [
            c for c in mock_ableton.send_command.call_args_list
            if c[0][0] == "load_browser_item"
        ]
        assert len(load_calls) == 1
        assert load_calls[0][0][1]["track_index"] == 1  # 2 -> 1
        assert load_calls[0][0][1]["item_uri"] == "uri:proq3"

    @patch('MCP_Server.server.get_ableton_connection')
    def test_ambiguous_match_requires_more_specific_query(self, mock_conn):
        # With equal-strength matches and no exact hit, tool should not guess.
        mock_ableton = MagicMock()
        tree = {
            "plugins": {
                "path": "plugins",
                "items": [
                    {"name": "Massive", "is_folder": False, "is_device": True, "is_loadable": True, "uri": "uri:massive"},
                    {"name": "Massive X", "is_folder": False, "is_device": True, "is_loadable": True, "uri": "uri:massivex"},
                ],
            },
        }

        def side_effect(command, params=None):
            if command == "get_browser_items_at_path":
                return _browser_response_for(params.get("path", ""), tree)
            raise AssertionError("Unexpected command: {0}".format(command))

        mock_ableton.send_command.side_effect = side_effect
        mock_conn.return_value = mock_ableton

        result = load_external_plugin(MagicMock(), track_index=1, plugin_name="mass")

        assert "Multiple plugins match" in result
        assert "Massive" in result
        assert "Massive X" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_exact_match_mode_requires_strict_name(self, mock_conn):
        # exact_match=True should reject partial names that only fuzzy-match.
        mock_ableton = MagicMock()
        tree = {
            "plugins": {
                "path": "plugins",
                "items": [
                    {"name": "Massive X", "is_folder": False, "is_device": True, "is_loadable": True, "uri": "uri:massivex"},
                ],
            },
        }

        def side_effect(command, params=None):
            if command == "get_browser_items_at_path":
                return _browser_response_for(params.get("path", ""), tree)
            raise AssertionError("Unexpected command: {0}".format(command))

        mock_ableton.send_command.side_effect = side_effect
        mock_conn.return_value = mock_ableton

        result = load_external_plugin(
            MagicMock(),
            track_index=1,
            plugin_name="massive",
            exact_match=True,
        )

        assert "No external plugin matched 'massive'" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_multiple_loads_reuse_discovery_cache(self, mock_conn):
        # Repeated loads should not rescan browser each time while cache is warm.
        mock_ableton = MagicMock()
        tree = {
            "plugins": {
                "path": "plugins",
                "items": [
                    {"name": "Serum", "is_folder": False, "is_device": True, "is_loadable": True, "uri": "uri:serum"},
                ],
            },
        }

        def side_effect(command, params=None):
            if command == "get_browser_items_at_path":
                return _browser_response_for(params.get("path", ""), tree)
            if command == "load_browser_item":
                return {"loaded": True, "item_name": "Serum"}
            raise AssertionError("Unexpected command: {0}".format(command))

        mock_ableton.send_command.side_effect = side_effect
        mock_conn.return_value = mock_ableton

        load_external_plugin(MagicMock(), track_index=1, plugin_name="Serum")
        load_external_plugin(MagicMock(), track_index=1, plugin_name="Serum")
        load_external_plugin(MagicMock(), track_index=1, plugin_name="Serum")

        discover_calls = [
            c for c in mock_ableton.send_command.call_args_list
            if c[0][0] == "get_browser_items_at_path"
        ]
        load_calls = [
            c for c in mock_ableton.send_command.call_args_list
            if c[0][0] == "load_browser_item"
        ]
        assert len(discover_calls) == 1
        assert len(load_calls) == 3

    @patch('MCP_Server.server.get_ableton_connection')
    def test_loading_different_plugins_back_to_back_without_rescan(self, mock_conn):
        # Switching plugin names between loads should still use cached discovery set.
        mock_ableton = MagicMock()
        tree = {
            "plugins": {
                "path": "plugins",
                "items": [
                    {"name": "Serum", "is_folder": False, "is_device": True, "is_loadable": True, "uri": "uri:serum"},
                    {"name": "Diva", "is_folder": False, "is_device": True, "is_loadable": True, "uri": "uri:diva"},
                ],
            },
        }

        def side_effect(command, params=None):
            if command == "get_browser_items_at_path":
                return _browser_response_for(params.get("path", ""), tree)
            if command == "load_browser_item":
                return {"loaded": True, "item_name": "Loaded"}
            raise AssertionError("Unexpected command: {0}".format(command))

        mock_ableton.send_command.side_effect = side_effect
        mock_conn.return_value = mock_ableton

        res1 = load_external_plugin(MagicMock(), track_index=1, plugin_name="Serum")
        res2 = load_external_plugin(MagicMock(), track_index=1, plugin_name="Diva")

        assert "Loaded external plugin 'Serum'" in res1
        assert "Loaded external plugin 'Diva'" in res2

        discover_calls = [
            c for c in mock_ableton.send_command.call_args_list
            if c[0][0] == "get_browser_items_at_path"
        ]
        assert len(discover_calls) == 1
