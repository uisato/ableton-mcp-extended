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
        # When both bar and beat are provided, bar should take precedence
        assert _convert_bar_to_beat(5, 99.0) == 16.0

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    def test_bar_zero_uses_beat(self, mock_ts):
        # When bar is 0 (unset), the raw beat value should be used instead
        assert _convert_bar_to_beat(0, 12.0) == 12.0

    @patch('MCP_Server.server._get_time_signature', return_value=(3, 4))
    def test_bar_with_3_4(self, mock_ts):
        # Bar conversion should respect a 3/4 time signature
        assert _convert_bar_to_beat(5, 0.0) == 12.0


class TestGetArrangementInfoCommand:
    """Test get_arrangement_info command dict construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_track_0_sends_minus_1(self, mock_conn):
        """track_index=0 (all tracks) should send -1 to the Remote Script."""
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
        """track_index=3 (1-based) should convert to 2 (0-based) for the Remote Script."""
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
        """get_cue_points should send the correct command with no index params."""
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"cue_points": []}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import get_cue_points
        get_cue_points(MagicMock())

        mock_ableton.send_command.assert_any_call("get_cue_points")


class TestSetSongTimeCommand:
    """Test set_song_time command construction."""

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_bar_8_sends_beat_28(self, mock_conn, mock_ts):
        # Bar 8 in 4/4 = (8-1)*4 = beat 28.0; verify the RS receives this value
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
        # When bar=0, the raw beat value should be sent directly to the RS
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"time": 12.0}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import set_song_time
        set_song_time(MagicMock(), beat=12.0)

        mock_ableton.send_command.assert_any_call(
            "set_song_time", {"time": 12.0})


class TestSetArrangementLoopCommand:
    """Test set_arrangement_loop command construction."""

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_bar_range(self, mock_conn, mock_ts):
        # Bars 4–8 in 4/4: start=12.0, length=16.0; verify correct loop region
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
    """Test jump_to_cue_point command construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_direction_next(self, mock_conn):
        # Jumping by direction should send the direction string to the RS
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"direction": "next"}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import jump_to_cue_point
        jump_to_cue_point(MagicMock(), direction="next")

        mock_ableton.send_command.assert_called_with(
            "jump_to_cue", {"direction": "next"})

    @patch('MCP_Server.server.get_ableton_connection')
    def test_name(self, mock_conn):
        # Jumping by name should send the cue point name to the RS
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"name": "Verse"}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import jump_to_cue_point
        jump_to_cue_point(MagicMock(), name="Verse")

        mock_ableton.send_command.assert_called_with(
            "jump_to_cue", {"name": "Verse"})


class TestCreateCuePointCommand:
    """Test create/delete cue point commands."""

    @staticmethod
    def _wire(mock_conn, readback_cues):
        mock_ableton = MagicMock()
        def send(cmd, _params=None):
            if cmd == "get_cue_points":
                return {"cue_points": readback_cues}
            return {}
        mock_ableton.send_command.side_effect = send
        mock_conn.return_value = mock_ableton
        return mock_ableton

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_create_at_bar_sends_correct_params(self, mock_conn, mock_ts):
        # Creating a cue point at bar 5 should convert to beat 16.0 and include the name
        mock_ableton = self._wire(mock_conn, [{"time": 16.0, "name": "Bridge"}])

        from MCP_Server.server import create_cue_point
        create_cue_point(MagicMock(), bar=5, name="Bridge")

        mock_ableton.send_command.assert_any_call(
            "create_cue_point", {"time": 16.0, "name": "Bridge"})

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_response_uses_readback_name_when_applied(self, mock_conn, mock_ts):
        self._wire(mock_conn, [{"time": 16.0, "name": "Bridge"}])

        from MCP_Server.server import create_cue_point
        result = create_cue_point(MagicMock(), bar=5, name="Bridge")

        assert "Bridge" in result
        assert "not applied" not in result
        assert "bar 5" in result

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_response_warns_when_name_not_applied(self, mock_conn, mock_ts):
        # Live 11 returns the locator default name ("1") regardless of requested name.
        self._wire(mock_conn, [{"time": 16.0, "name": "1"}])

        from MCP_Server.server import create_cue_point
        result = create_cue_point(MagicMock(), bar=5, name="Bridge")

        assert "not applied" in result
        assert "Bridge" in result
        assert "'1'" in result
        assert "bar 5" in result

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_response_no_name_requested_uses_actual(self, mock_conn, mock_ts):
        self._wire(mock_conn, [{"time": 16.0, "name": "1"}])

        from MCP_Server.server import create_cue_point
        result = create_cue_point(MagicMock(), bar=5, name="")

        assert "not applied" not in result
        assert "bar 5" in result

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_falls_back_when_readback_finds_nothing(self, mock_conn, mock_ts):
        # If the readback can't find the cue (race/failure), don't lie about state — fall back.
        self._wire(mock_conn, [])

        from MCP_Server.server import create_cue_point
        result = create_cue_point(MagicMock(), bar=5, name="Bridge")

        assert "bar 5" in result
        # No false "name applied" claim and no false "not applied" claim either.

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_delete_at_bar(self, mock_conn, mock_ts):
        # Deleting a cue point at bar 5 should convert to beat 16.0
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import delete_cue_point
        delete_cue_point(MagicMock(), bar=5)

        mock_ableton.send_command.assert_called_with(
            "delete_cue_point", {"time": 16.0})


class TestCreateArrangementMidiClipCommand:
    """Test create_arrangement_midi_clip command construction."""

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_bar_range_converts(self, mock_conn, mock_ts):
        # Track 1 → 0, bars 5–9 → position 16.0, length 16.0
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
    def test_passes_name_through(self, mock_conn, mock_ts):
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"overlapped_clips": []}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import create_arrangement_midi_clip
        create_arrangement_midi_clip(
            MagicMock(), track_index=1, start_bar=1, end_bar=5, name="Intro")

        args = mock_ableton.send_command.call_args
        assert args[0][1]["name"] == "Intro"

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_overlap_warning(self, mock_conn, mock_ts):
        # When the RS reports overlapped clips, the result should contain a warning
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "start_time": 0.0, "overlapped_clips": ["Intro"]}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import create_arrangement_midi_clip
        result = create_arrangement_midi_clip(
            MagicMock(), track_index=1, start_bar=1, end_bar=5)

        assert "Warning" in result or "warning" in result.lower() or "overlapped" in result.lower()


class TestCreateArrangementAudioClipCommand:
    """Test create_arrangement_audio_clip command construction."""

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_converts_indices(self, mock_conn, mock_ts):
        # Track 2 → 1 (0-based), file path passed through unchanged
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
    """Test duplicate_clip_to_arrangement command construction."""

    @patch('MCP_Server.server._get_time_signature', return_value=(4, 4))
    @patch('MCP_Server.server.get_ableton_connection')
    def test_converts_all_indices(self, mock_conn, mock_ts):
        # Both track and clip indices convert from 1-based to 0-based; bar converts to beat
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
    """Test delete_arrangement_clip command construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_by_index(self, mock_conn):
        # Deleting by index: track 1 → 0, clip 2 → 1 (both 1-based to 0-based)
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
        # Deleting by name should pass clip_name and omit clip_index from the command
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
    """Test set_arrangement_clip_property command construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_index_conversion(self, mock_conn):
        # Track 2 → 1, clip 3 → 2 when sending to the RS
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
        # Only properties with non-None values should generate RS commands
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
        # Setting two properties should result in two separate RS commands
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
        # When no properties are specified, no RS commands should be sent
        mock_ableton = MagicMock()
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import set_arrangement_clip_property
        result = set_arrangement_clip_property(
            MagicMock(), track_index=1, clip_index=1)

        mock_ableton.send_command.assert_not_called()
        assert "No properties" in result


class TestSetAbletonViewCommand:
    """Test set_ableton_view command construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_sends_view_name(self, mock_conn):
        # The view name string should be passed through to the RS as view_name
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"visible": True}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import set_ableton_view
        set_ableton_view(MagicMock(), view="Session")

        mock_ableton.send_command.assert_called_with(
            "set_view", {"view_name": "Session"})


class TestControlArrangementViewCommand:
    """Test control_arrangement_view command construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_collapse_converts_index(self, mock_conn):
        # Track index 3 (1-based) should convert to 2 (0-based) for collapse action
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
        # Zoom actions that don't need a track index should default track_index to 0
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"action": "zoom_in", "done": True}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import control_arrangement_view
        control_arrangement_view(MagicMock(), action="zoom_in")

        mock_ableton.send_command.assert_called_with(
            "control_arrangement_view", {"action": "zoom_in", "track_index": 0})


class TestManageClipAutomationCommand:
    """Test manage_clip_automation command construction."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_create_converts_indices(self, mock_conn):
        # Track 2 → 1, clip 3 → 2; action and parameter_name pass through
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
        # The clear_all action should produce a result message indicating all automation was cleared
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"action": "clear_all", "done": True}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import manage_clip_automation
        result = manage_clip_automation(
            MagicMock(), track_index=1, clip_index=1, action="clear_all")

        assert "Cleared all" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_clip_name_forwarded_and_takes_precedence(self, mock_conn):
        # clip_name must be forwarded; clip_index must NOT be sent so the
        # Remote Script resolves by name unambiguously.
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {"action": "create", "done": True}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import manage_clip_automation
        manage_clip_automation(
            MagicMock(), track_index=2, clip_index=4, clip_name="Lead",
            action="create", parameter_name="volume")

        payload = mock_ableton.send_command.call_args[0][1]
        assert payload["clip_name"] == "Lead"
        assert "clip_index" not in payload
        assert payload["track_index"] == 1

    @patch('MCP_Server.server.get_ableton_connection')
    def test_remote_parameter_name_surfaces_in_message(self, mock_conn):
        # Server must not fabricate the parameter — it should reflect what
        # the Remote Script reports (e.g. "Track Volume" for an alias).
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "action": "create", "parameter": "Track Volume", "done": True}
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import manage_clip_automation
        result = manage_clip_automation(
            MagicMock(), track_index=1, clip_index=1,
            action="create", parameter_name="volume")

        assert "Track Volume" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_zero_clip_index_without_name_errors(self, mock_conn):
        # 0 violates the 1-based contract; reject before round-tripping.
        mock_ableton = MagicMock()
        mock_conn.return_value = mock_ableton

        from MCP_Server.server import manage_clip_automation
        result = manage_clip_automation(
            MagicMock(), track_index=1, clip_index=0,
            action="create", parameter_name="volume")

        assert "Error" in result
        mock_ableton.send_command.assert_not_called()
