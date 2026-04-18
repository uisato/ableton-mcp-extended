"""Unit tests for get_browser_items_at_path limit/offset pagination.

Covers both halves:
- The MCP-server wrapper builds the correct payload (limit omitted when 0,
  offset always sent, IntParam strings coerced to ints).
- Response formatting passes through total_count / returned from the Remote
  Script so the LLM can page.
"""
import json
import os
import sys
from unittest.mock import MagicMock, patch

# Mock MCP dependencies before importing server
_mock_mcp_module = MagicMock()
_mock_fastmcp = MagicMock()
_mock_fastmcp.FastMCP.return_value.tool.return_value = lambda fn: fn
sys.modules['mcp'] = _mock_mcp_module
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = _mock_fastmcp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MCP_Server.server import get_browser_items_at_path  # noqa: E402


def _fake_response(items, total=None, returned=None, offset=0, limit=None):
    return {
        "path": "drums/acoustic",
        "name": "acoustic",
        "uri": "view:drums#acoustic",
        "is_folder": True,
        "is_device": False,
        "is_loadable": False,
        "items": items,
        "total_count": total if total is not None else len(items),
        "returned": returned if returned is not None else len(items),
        "offset": offset,
        "limit": limit,
    }


class TestPayload:
    """The wrapper must build the right payload for the Remote Script."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_default_limit_50_is_sent(self, mock_conn):
        # Default (no explicit limit) should send limit=50 to RS
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = _fake_response([])
        mock_conn.return_value = mock_ableton

        get_browser_items_at_path(MagicMock(), path="drums/acoustic")

        mock_ableton.send_command.assert_called_with(
            "get_browser_items_at_path",
            {"path": "drums/acoustic", "offset": 0, "limit": 50},
        )

    @patch('MCP_Server.server.get_ableton_connection')
    def test_limit_zero_omits_limit(self, mock_conn):
        # limit=0 means "all items" → payload must NOT include limit,
        # so the Remote Script defaults to unlimited slicing
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = _fake_response([])
        mock_conn.return_value = mock_ableton

        get_browser_items_at_path(MagicMock(), path="drums/", limit="0")

        mock_ableton.send_command.assert_called_with(
            "get_browser_items_at_path",
            {"path": "drums/", "offset": 0},
        )

    @patch('MCP_Server.server.get_ableton_connection')
    def test_string_params_coerced(self, mock_conn):
        # IntParam is typed as str (Cowork compat); _i must coerce to int
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = _fake_response([])
        mock_conn.return_value = mock_ableton

        get_browser_items_at_path(MagicMock(), path="x", limit="25", offset="100")

        mock_ableton.send_command.assert_called_with(
            "get_browser_items_at_path",
            {"path": "x", "offset": 100, "limit": 25},
        )

    @patch('MCP_Server.server.get_ableton_connection')
    def test_custom_limit_and_offset(self, mock_conn):
        # Pagination: page 2 of size 25 → offset=25, limit=25
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = _fake_response([])
        mock_conn.return_value = mock_ableton

        get_browser_items_at_path(MagicMock(), path="x", limit=25, offset=25)

        mock_ableton.send_command.assert_called_with(
            "get_browser_items_at_path",
            {"path": "x", "offset": 25, "limit": 25},
        )


class TestResponsePassthrough:
    """Response must expose total_count / returned so the LLM can page."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_pagination_metadata_in_json(self, mock_conn):
        mock_ableton = MagicMock()
        items = [{"name": f"kit_{i}", "uri": f"u{i}"} for i in range(50)]
        mock_ableton.send_command.return_value = _fake_response(
            items, total=500, returned=50, offset=0, limit=50
        )
        mock_conn.return_value = mock_ableton

        result = get_browser_items_at_path(MagicMock(), path="drums/acoustic")
        parsed = json.loads(result)

        assert parsed["total_count"] == 500
        assert parsed["returned"] == 50
        assert parsed["offset"] == 0
        assert parsed["limit"] == 50
        assert len(parsed["items"]) == 50

    @patch('MCP_Server.server.get_ableton_connection')
    def test_error_response_still_surfaces(self, mock_conn):
        # When the RS returns available_categories (bad path), we still need
        # the friendly error message — pagination changes must not mask that
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "path": "wrongcat",
            "error": "Unknown or unavailable category: wrongcat",
            "available_categories": ["instruments", "drums"],
            "items": [],
        }
        mock_conn.return_value = mock_ableton

        result = get_browser_items_at_path(MagicMock(), path="wrongcat")
        assert "Unknown or unavailable category" in result
        assert "instruments" in result
