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

from MCP_Server.server import (
    delete_track,
    get_track_deletion_status,
    set_track_arm,
    set_track_mute,
    set_track_solo,
)


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


class TestTrackMuteSoloArm:
    """The mixer-state tools: 1-based in, 0-based on the wire."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_mute_converts_the_index_and_reports_the_name(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"track_name": "Bass",
                                                  "mute": True}
        mock_conn.return_value = mock_ableton

        result = set_track_mute(MagicMock(), track_index=3, mute=True)

        assert "Bass" in result and "muted" in result
        call = mock_ableton.send_command.call_args
        assert call[0][0] == "set_track_mute"
        assert call[0][1]["track_index"] == 2      # 3 (1-based) -> 2 (0-based)
        assert call[0][1]["mute"] is True

    @patch('MCP_Server.server.get_ableton_connection')
    def test_unmute_reads_as_unmuted(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"track_name": "Bass",
                                                  "mute": False}
        mock_conn.return_value = mock_ableton

        result = set_track_mute(MagicMock(), track_index=1, mute=False)

        assert "unmuted" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_solo_converts_the_index(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"track_name": "Drums",
                                                  "solo": True}
        mock_conn.return_value = mock_ableton

        result = set_track_solo(MagicMock(), track_index=2, solo=True)

        assert "Drums" in result and "soloed" in result
        call = mock_ableton.send_command.call_args
        assert call[0][0] == "set_track_solo"
        assert call[0][1]["track_index"] == 1

    @patch('MCP_Server.server.get_ableton_connection')
    def test_arm_converts_the_index(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"track_name": "Synth",
                                                  "arm": True}
        mock_conn.return_value = mock_ableton

        result = set_track_arm(MagicMock(), track_index=4, arm=True)

        assert "Synth" in result and "armed" in result
        call = mock_ableton.send_command.call_args
        assert call[0][0] == "set_track_arm"
        assert call[0][1]["track_index"] == 3

    @patch('MCP_Server.server.get_ableton_connection')
    def test_zero_index_is_rejected_before_the_socket(self, mock_conn):
        mock_ableton = MagicMock()
        mock_conn.return_value = mock_ableton

        for tool in (set_track_mute, set_track_solo, set_track_arm):
            result = tool(MagicMock(), track_index=0)
            assert "1-based" in result, (tool.__name__, result)
        mock_ableton.send_command.assert_not_called()
