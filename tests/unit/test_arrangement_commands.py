"""Unit tests for arrangement MCP tool command construction and index conversion."""

import sys
import os
from unittest.mock import MagicMock, patch, call

# Mock mcp dependencies before importing server module
# Make @mcp.tool() a pass-through decorator so actual functions are preserved
_mock_mcp_module = MagicMock()
_mock_fastmcp = MagicMock()
_mock_fastmcp.FastMCP.return_value.tool.return_value = lambda fn: fn
sys.modules['mcp'] = _mock_mcp_module
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = _mock_fastmcp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MCP_Server.server import (
    bar_to_beat, beat_to_bar,
    _convert_bar_to_beat,
)


class TestConvertBarToBeat:
    """Test the _convert_bar_to_beat helper that dispatches bar vs beat."""

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    def test_bar_takes_precedence(self, mock_ts):
        assert _convert_bar_to_beat(5, 99.0) == 16.0

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    def test_bar_zero_uses_beat(self, mock_ts):
        assert _convert_bar_to_beat(0, 12.0) == 12.0

    @patch('MCP_Server.server._get_time_signature', return_value=(3, 4))
    def test_bar_with_3_4(self, mock_ts):
        assert _convert_bar_to_beat(5, 0.0) == 12.0


class TestGetArrangementInfoCommand:
    """T016: Test get_arrangement_info command dict construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_track_0_sends_minus_1(self, mock_conn):
        """track_index=0 (all tracks) should send -1 to RS."""
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "transport": {"tempo": 120, "signature_numerator": 4,
                          "signature_denominator": 4, "is_playing": False,
                          "current_time": 0, "loop_enabled": False},
            "tracks": []
        }
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import get_arrangement_info
        get_arrangement_info(MagicMock(), track_index=0)

        mock_ableton.send_command.assert_called_with(
            "get_arrangement_info", {"track_index": -1})

    @patch('MCP_Server.server.get_ableton_connection')
    def test_track_3_sends_2(self, mock_conn):
        """track_index=3 (1-based) should send 2 (0-based) to RS."""
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "transport": {"tempo": 120, "signature_numerator": 4,
                          "signature_denominator": 4, "is_playing": False,
                          "current_time": 0, "loop_enabled": False},
            "tracks": []
        }
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import get_arrangement_info
        get_arrangement_info(MagicMock(), track_index=3)

        mock_ableton.send_command.assert_called_with(
            "get_arrangement_info", {"track_index": 2})

    @patch('MCP_Server.server.get_ableton_connection')
    def test_get_cue_points_command(self, mock_conn):
        """get_cue_points should send correct command."""
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"cue_points": []}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import get_cue_points
        get_cue_points(MagicMock())

        mock_ableton.send_command.assert_any_call("get_cue_points")


class TestSetSongTimeCommand:
    """T028: Test set_song_time command construction."""

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_bar_8_sends_beat_28(self, mock_conn, mock_ts):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"time": 28.0}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import set_song_time
        set_song_time(MagicMock(), bar=8)

        mock_ableton.send_command.assert_called_with(
            "set_song_time", {"time": 28.0})

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_beat_direct(self, mock_conn, mock_ts):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"time": 12.0}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import set_song_time
        set_song_time(MagicMock(), beat=12.0)

        mock_ableton.send_command.assert_any_call(
            "set_song_time", {"time": 12.0})


class TestSetArrangementLoopCommand:
    """T028: Test set_arrangement_loop command construction."""

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_bar_range(self, mock_conn, mock_ts):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "enabled": True, "start": 12.0, "length": 16.0}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import set_arrangement_loop
        set_arrangement_loop(MagicMock(), enabled=True, start_bar=4, end_bar=8)

        args = mock_ableton.send_command.call_args
        assert args[0][0] == "set_arrangement_loop"
        assert args[0][1]["enabled"] is True
        assert args[0][1]["start"] == 12.0
        assert args[0][1]["length"] == 16.0


class TestJumpToCuePointCommand:
    """T028: Test jump_to_cue_point command construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_direction_next(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"direction": "next"}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import jump_to_cue_point
        jump_to_cue_point(MagicMock(), direction="next")

        mock_ableton.send_command.assert_called_with(
            "jump_to_cue", {"direction": "next"})

    @patch('MCP_Server.server.get_ableton_connection')
    def test_name(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"name": "Verse"}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import jump_to_cue_point
        jump_to_cue_point(MagicMock(), name="Verse")

        mock_ableton.send_command.assert_called_with(
            "jump_to_cue", {"name": "Verse"})


class TestCreateCuePointCommand:
    """T028: Test create/delete cue point commands."""

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_create_at_bar(self, mock_conn, mock_ts):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import create_cue_point
        create_cue_point(MagicMock(), bar=5, name="Bridge")

        mock_ableton.send_command.assert_called_with(
            "create_cue_point", {"time": 16.0, "name": "Bridge"})

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_delete_at_bar(self, mock_conn, mock_ts):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import delete_cue_point
        delete_cue_point(MagicMock(), bar=5)

        mock_ableton.send_command.assert_called_with(
            "delete_cue_point", {"time": 16.0})


class TestCreateArrangementMidiClipCommand:
    """T038: Test create_arrangement_midi_clip command construction."""

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_bar_range_converts(self, mock_conn, mock_ts):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "start_time": 16.0, "overlapped_clips": []}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import create_arrangement_midi_clip
        create_arrangement_midi_clip(
            MagicMock(), track_index=1, start_bar=5, end_bar=9)

        args = mock_ableton.send_command.call_args
        assert args[0][0] == "create_arrangement_clip"
        assert args[0][1]["track_index"] == 0  # 1-based → 0-based
        assert args[0][1]["position"] == 16.0
        assert args[0][1]["length"] == 16.0

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_overlap_warning(self, mock_conn, mock_ts):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "start_time": 0.0, "overlapped_clips": ["Intro"]}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import create_arrangement_midi_clip
        result = create_arrangement_midi_clip(
            MagicMock(), track_index=1, start_bar=1, end_bar=5)

        assert "Warning" in result or "warning" in result.lower() or "overlapped" in result.lower()


class TestCreateArrangementAudioClipCommand:
    """T038: Test create_arrangement_audio_clip command construction."""

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_converts_indices(self, mock_conn, mock_ts):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import create_arrangement_audio_clip
        create_arrangement_audio_clip(
            MagicMock(), track_index=2, file_path="/audio.wav", start_bar=3)

        args = mock_ableton.send_command.call_args
        assert args[0][1]["track_index"] == 1  # 1-based → 0-based
        assert args[0][1]["file_path"] == "/audio.wav"


class TestDuplicateClipToArrangementCommand:
    """T038: Test duplicate_clip_to_arrangement command construction."""

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_converts_all_indices(self, mock_conn, mock_ts):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import duplicate_clip_to_arrangement
        duplicate_clip_to_arrangement(
            MagicMock(), track_index=2, clip_index=3, destination_bar=5)

        args = mock_ableton.send_command.call_args
        assert args[0][1]["track_index"] == 1  # 2 → 1
        assert args[0][1]["clip_index"] == 2  # 3 → 2
        assert args[0][1]["destination_time"] == 16.0


class TestDeleteArrangementClipCommand:
    """T038: Test delete_arrangement_clip command construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_by_index(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"deleted": True}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import delete_arrangement_clip
        delete_arrangement_clip(MagicMock(), track_index=1, clip_index=2)

        args = mock_ableton.send_command.call_args
        assert args[0][1]["track_index"] == 0
        assert args[0][1]["clip_index"] == 1

    @patch('MCP_Server.server.get_ableton_connection')
    def test_by_name(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"deleted": True}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import delete_arrangement_clip
        delete_arrangement_clip(
            MagicMock(), track_index=1, clip_name="Intro")

        args = mock_ableton.send_command.call_args
        assert args[0][1]["clip_name"] == "Intro"
        assert "clip_index" not in args[0][1]


class TestSetArrangementClipPropertyCommand:
    """T042: Test set_arrangement_clip_property command construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_index_conversion(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"property": "muted", "value": True}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import set_arrangement_clip_property
        set_arrangement_clip_property(
            MagicMock(), track_index=2, clip_index=3, muted=True)

        args = mock_ableton.send_command.call_args
        assert args[0][1]["track_index"] == 1  # 2 → 1
        assert args[0][1]["clip_index"] == 2  # 3 → 2

    @patch('MCP_Server.server.get_ableton_connection')
    def test_only_non_none_sent(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"property": "muted", "value": True}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import set_arrangement_clip_property
        set_arrangement_clip_property(
            MagicMock(), track_index=1, clip_index=1, muted=True)

        # Should only send one command (for muted)
        assert mock_ableton.send_command.call_count == 1

    @patch('MCP_Server.server.get_ableton_connection')
    def test_multiple_props_sends_multiple(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"property": "x", "value": True}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import set_arrangement_clip_property
        set_arrangement_clip_property(
            MagicMock(), track_index=1, clip_index=1,
            muted=True, looping=False)

        assert mock_ableton.send_command.call_count == 2

    @patch('MCP_Server.server.get_ableton_connection')
    def test_no_props_no_command(self, mock_conn):
        mock_ableton = MagicMock()
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import set_arrangement_clip_property
        result = set_arrangement_clip_property(
            MagicMock(), track_index=1, clip_index=1)

        mock_ableton.send_command.assert_not_called()
        assert "No properties" in result


class TestSetAbletonViewCommand:
    """T048: Test set_ableton_view command construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_sends_view_name(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"visible": True}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import set_ableton_view
        set_ableton_view(MagicMock(), view="Session")

        mock_ableton.send_command.assert_called_with(
            "set_view", {"view_name": "Session"})


class TestControlArrangementViewCommand:
    """T048: Test control_arrangement_view command construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_collapse_converts_index(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"action": "collapse_track", "done": True}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import control_arrangement_view
        control_arrangement_view(
            MagicMock(), action="collapse_track", track_index=3)

        args = mock_ableton.send_command.call_args
        assert args[0][1]["track_index"] == 2  # 3 → 2

    @patch('MCP_Server.server.get_ableton_connection')
    def test_zoom_in(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"action": "zoom_in", "done": True}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import control_arrangement_view
        control_arrangement_view(MagicMock(), action="zoom_in")

        mock_ableton.send_command.assert_called_with(
            "control_arrangement_view", {"action": "zoom_in", "track_index": 0})


class TestManageClipAutomationCommand:
    """T052: Test manage_clip_automation command construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_create_converts_indices(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"action": "create", "done": True}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import manage_clip_automation
        manage_clip_automation(
            MagicMock(), track_index=2, clip_index=3,
            action="create", parameter_name="volume")

        args = mock_ableton.send_command.call_args
        assert args[0][1]["track_index"] == 1  # 2 → 1
        assert args[0][1]["clip_index"] == 2  # 3 → 2
        assert args[0][1]["action"] == "create"
        assert args[0][1]["parameter_name"] == "volume"

    @patch('MCP_Server.server.get_ableton_connection')
    def test_clear_all(self, mock_conn):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"action": "clear_all", "done": True}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import manage_clip_automation
        result = manage_clip_automation(
            MagicMock(), track_index=1, clip_index=1, action="clear_all")

        assert "Cleared all" in result
