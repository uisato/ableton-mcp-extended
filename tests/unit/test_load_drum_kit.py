"""Unit tests for the load_drum_kit MCP tool."""
import os
import sys
from unittest.mock import MagicMock, patch


_mock_mcp_module = MagicMock()
_mock_fastmcp = MagicMock()
_mock_fastmcp.FastMCP.return_value.tool.return_value = lambda fn: fn
sys.modules["mcp"] = _mock_mcp_module
sys.modules["mcp.server"] = MagicMock()
sys.modules["mcp.server.fastmcp"] = _mock_fastmcp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from MCP_Server.server import load_drum_kit  # noqa: E402


@patch("MCP_Server.server.get_ableton_connection")
def test_loads_kit_when_path_resolves_directly_to_loadable_file(mock_conn):
    # Stock Ableton kits live as .adg files directly under drums/, with no children.
    # The tool must accept a path that resolves to such a leaf and load it.
    mock_ableton = MagicMock()

    def side_effect(command, params=None):
        if command == "load_browser_item":
            return {"loaded": True}
        if command == "get_browser_items_at_path":
            return {
                "path": params["path"],
                "name": "808 Core Kit.adg",
                "uri": "query:Drums#FileId_4197",
                "is_folder": False,
                "is_loadable": True,
                "items": [],
            }
        raise AssertionError("unexpected command: {0}".format(command))

    mock_ableton.send_command.side_effect = side_effect
    mock_conn.return_value = mock_ableton

    result = load_drum_kit(
        MagicMock(),
        track_index=1,
        rack_uri="query:Drums#Drum%20Rack",
        kit_path="drums/808 Core Kit.adg",
    )

    assert "808 Core Kit.adg" in result
    load_calls = [
        call for call in mock_ableton.send_command.call_args_list
        if call.args[0] == "load_browser_item"
    ]
    # First load = drum rack. Second load = the resolved kit URI.
    assert len(load_calls) == 2
    assert load_calls[1].args[1]["item_uri"] == "query:Drums#FileId_4197"


@patch("MCP_Server.server.get_ableton_connection")
def test_accepts_kit_uri_directly_consistent_with_load_instrument(mock_conn):
    # Mirroring load_instrument_or_effect, kit_path may be a browser URI.
    # When given a URI, no path resolution should be attempted.
    mock_ableton = MagicMock()

    def side_effect(command, params=None):
        if command == "load_browser_item":
            return {"loaded": True}
        if command == "get_browser_items_at_path":
            raise AssertionError("URI form should not call get_browser_items_at_path")
        raise AssertionError("unexpected command: {0}".format(command))

    mock_ableton.send_command.side_effect = side_effect
    mock_conn.return_value = mock_ableton

    result = load_drum_kit(
        MagicMock(),
        track_index=1,
        rack_uri="query:Drums#Drum%20Rack",
        kit_path="query:Drums#FileId_4197",
    )

    assert "track 1" in result
    load_calls = [
        call for call in mock_ableton.send_command.call_args_list
        if call.args[0] == "load_browser_item"
    ]
    assert load_calls[1].args[1]["item_uri"] == "query:Drums#FileId_4197"


@patch("MCP_Server.server.get_ableton_connection")
def test_falls_back_to_first_loadable_child_for_folder_paths(mock_conn):
    # When the path resolves to a folder, pick the first loadable child as before.
    mock_ableton = MagicMock()

    def side_effect(command, params=None):
        if command == "load_browser_item":
            return {"loaded": True}
        if command == "get_browser_items_at_path":
            return {
                "path": params["path"],
                "name": "Custom",
                "uri": "user-library:Drum Kits#Custom",
                "is_folder": True,
                "is_loadable": False,
                "items": [
                    {"name": "MyKit.adg", "is_loadable": True, "uri": "user-library:Drum Kits#MyKit"},
                ],
            }
        raise AssertionError("unexpected command: {0}".format(command))

    mock_ableton.send_command.side_effect = side_effect
    mock_conn.return_value = mock_ableton

    result = load_drum_kit(
        MagicMock(),
        track_index=2,
        rack_uri="query:Drums#Drum%20Rack",
        kit_path="user-library/Drum Kits/Custom",
    )

    assert "MyKit.adg" in result
    load_calls = [
        call for call in mock_ableton.send_command.call_args_list
        if call.args[0] == "load_browser_item"
    ]
    assert load_calls[1].args[1]["item_uri"] == "user-library:Drum Kits#MyKit"


@patch("MCP_Server.server.get_ableton_connection")
def test_reports_failure_when_path_is_unloadable_folder(mock_conn):
    # Resolving to a folder with no loadable children must surface an error,
    # not silently no-op after loading the rack.
    mock_ableton = MagicMock()

    def side_effect(command, params=None):
        if command == "load_browser_item":
            return {"loaded": True}
        if command == "get_browser_items_at_path":
            return {
                "path": params["path"],
                "name": "Empty",
                "uri": None,
                "is_folder": True,
                "is_loadable": False,
                "items": [],
            }
        raise AssertionError("unexpected command: {0}".format(command))

    mock_ableton.send_command.side_effect = side_effect
    mock_conn.return_value = mock_ableton

    result = load_drum_kit(
        MagicMock(),
        track_index=1,
        rack_uri="query:Drums#Drum%20Rack",
        kit_path="drums/Empty",
    )

    assert "no loadable" in result.lower()
