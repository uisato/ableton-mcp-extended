"""Unit tests for track-level MCP tools."""
import sys
import os
from unittest.mock import MagicMock, patch

# Mock MCP dependencies before importing server
_mock_mcp_module = MagicMock()
_mock_fastmcp = MagicMock()
_mock_fastmcp.FastMCP.return_value.tool.return_value = lambda fn: fn
sys.modules['mcp'] = _mock_mcp_module
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = _mock_fastmcp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MCP_Server.server import delete_track, get_track_deletion_status


class TestDeleteTrackSafetyGuard:
    """Prevent deleting the final remaining session track."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_blocks_delete_by_index_when_only_one_track_remains(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"track_count": 1}
        mock_conn.return_value = mock_ableton

        result = delete_track(MagicMock(), track_index=1)

        assert "Cannot delete the last remaining session track" in result
        assert "Create a new track before deleting" in result
        mock_ableton.send_command.assert_called_once_with("get_session_info")

    @patch('MCP_Server.server.get_ableton_connection')
    def test_blocks_delete_by_name_when_only_one_track_remains(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"track_count": 1}
        mock_conn.return_value = mock_ableton

        result = delete_track(MagicMock(), track_index=0, track_name="My Track")

        assert "Cannot delete the last remaining session track" in result
        assert "Create a new track before deleting" in result
        mock_ableton.send_command.assert_called_once_with("get_session_info")


class TestDeleteTrackBehavior:
    """Normal delete behavior when more than one track exists."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_delete_by_index_still_works_with_multiple_tracks(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.side_effect = [
            {"track_count": 3},  # get_session_info
            {"deleted_track": "Bass", "remaining_tracks": 2},  # delete_track
        ]
        mock_conn.return_value = mock_ableton

        result = delete_track(MagicMock(), track_index=2)

        assert "Deleted track 'Bass'" in result
        calls = mock_ableton.send_command.call_args_list
        assert calls[1][0][0] == "delete_track"
        assert calls[1][0][1]["track_index"] == 1  # 2 -> 1

    @patch('MCP_Server.server.get_ableton_connection')
    def test_delete_by_name_resolves_and_deletes(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.side_effect = [
            {"track_count": 3},  # get_session_info
            {"name": "Drums"},   # get_track_info index 0
            {"name": "Bass"},    # get_track_info index 1
            {"deleted_track": "Bass", "remaining_tracks": 2},  # delete_track
        ]
        mock_conn.return_value = mock_ableton

        result = delete_track(MagicMock(), track_index=0, track_name="Bass")

        assert "Deleted track 'Bass'" in result
        delete_call = mock_ableton.send_command.call_args_list[-1]
        assert delete_call[0][0] == "delete_track"
        assert delete_call[0][1]["track_index"] == 1


class TestTrackDeletionStatus:
    """Tests for get_track_deletion_status precheck tool."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_reports_blocked_when_one_track_remains(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"track_count": 1}
        mock_conn.return_value = mock_ableton

        result = get_track_deletion_status(MagicMock())

        assert "Track deletion blocked" in result
        assert "Create a new track before deleting" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_reports_max_deletions_when_multiple_tracks_exist(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"track_count": 4}
        mock_conn.return_value = mock_ableton

        result = get_track_deletion_status(MagicMock())

        assert "Track deletion available" in result
        assert "up to 3 more track(s)" in result
