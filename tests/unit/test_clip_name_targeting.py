"""clip_name must reach the Remote Script and pick the named clip.

Regression tests for set_arrangement_clip_property and manage_clip_automation,
which used to accept clip_name but only ever send clip_index, so a request for
clip "X" changed the track's first clip and still reported success.
"""

import os
import sys
import types
from unittest.mock import MagicMock, patch

import pytest

# MCP side: make @mcp.tool() a pass-through so the real functions are kept.
_mock_fastmcp = MagicMock()
_mock_fastmcp.FastMCP.return_value.tool.return_value = lambda fn: fn
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = _mock_fastmcp

# Remote Script side: stub Ableton's _Framework. setdefault keeps whichever
# stub another test module installed first; all of them define log_message.


class _StubControlSurface:
    def __init__(self, c_instance=None):
        pass

    def log_message(self, msg):
        pass


_cs_module = types.ModuleType("_Framework.ControlSurface")
_cs_module.ControlSurface = _StubControlSurface
sys.modules.setdefault("_Framework", types.ModuleType("_Framework"))
sys.modules.setdefault("_Framework.ControlSurface", _cs_module)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from AbletonMCP_Remote_Script import AbletonMCP  # noqa: E402
from MCP_Server import server  # noqa: E402


# ── MCP layer ──────────────────────────────────────────────────────


def _connection(result):
    conn = MagicMock()
    conn.send_command.return_value = result
    return conn


class TestArrangementClipTarget:
    def test_name_wins_and_index_is_poisoned(self):
        # -1 makes an outdated Remote Script (which ignores clip_name) fail
        # instead of defaulting to the first clip.
        assert server._arrangement_clip_target(3, "Verse Gtr") == {
            "clip_name": "Verse Gtr", "clip_index": -1}

    def test_index_converted_to_zero_based(self):
        assert server._arrangement_clip_target(3, "") == {"clip_index": 2}

    def test_index_below_one_without_name_is_rejected(self):
        with pytest.raises(ValueError, match="clip_index must be >= 1"):
            server._arrangement_clip_target(0, "")


class TestSetArrangementClipPropertyClipName:
    @patch('MCP_Server.server.get_ableton_connection')
    def test_forwards_clip_name_not_index(self, mock_conn):
        conn = _connection({"clip_name": "Verse Gtr", "property": "muted", "value": True})
        mock_conn.return_value = conn

        server.set_arrangement_clip_property(
            MagicMock(), track_index=2, clip_name="Verse Gtr", muted=True)

        conn.send_command.assert_called_once_with(
            "set_arrangement_clip_property",
            {"track_index": 1, "clip_name": "Verse Gtr", "clip_index": -1,
             "property": "muted", "value": True})

    @patch('MCP_Server.server.get_ableton_connection')
    def test_message_names_the_clip_actually_changed(self, mock_conn):
        # The Remote Script reports which clip it changed; trust that over the request.
        mock_conn.return_value = _connection(
            {"clip_name": "Chorus", "property": "muted", "value": True})

        result = server.set_arrangement_clip_property(
            MagicMock(), track_index=2, clip_index=1, muted=True)

        assert result == "Updated 'Chorus' on track 2: muted=True"

    @patch('MCP_Server.server.get_ableton_connection')
    def test_rename_is_sent_last_so_name_lookup_still_works(self, mock_conn):
        conn = _connection({"clip_name": "Verse Gtr", "property": "x", "value": 1})
        mock_conn.return_value = conn

        result = server.set_arrangement_clip_property(
            MagicMock(), track_index=1, clip_name="Verse Gtr",
            name="Verse Gtr 2", muted=True, color=5)

        sent = [c.args[1] for c in conn.send_command.call_args_list]
        assert [p["property"] for p in sent] == ["muted", "color", "name"]
        assert all(p["clip_name"] == "Verse Gtr" for p in sent)
        assert all(p["clip_index"] == -1 for p in sent)
        assert result.startswith("Updated 'Verse Gtr' on track 1:")

    @patch('MCP_Server.server.get_ableton_connection')
    def test_falls_back_to_requested_name_when_result_has_no_clip_name(self, mock_conn):
        # An older Remote Script returns no clip_name.
        mock_conn.return_value = _connection({"property": "muted", "value": True})

        result = server.set_arrangement_clip_property(
            MagicMock(), track_index=1, clip_name="Verse Gtr", muted=True)

        assert result == "Updated 'Verse Gtr' on track 1: muted=True"

    @patch('MCP_Server.server.get_ableton_connection')
    def test_falls_back_to_index_when_result_is_not_a_dict(self, mock_conn):
        mock_conn.return_value = _connection(None)

        result = server.set_arrangement_clip_property(
            MagicMock(), track_index=1, clip_index=4, muted=False)

        assert result == "Updated clip 4 on track 1: muted=False"

    @patch('MCP_Server.server.get_ableton_connection')
    def test_clip_index_zero_without_name_errors_instead_of_hitting_first_clip(self, mock_conn):
        conn = _connection({})
        mock_conn.return_value = conn

        result = server.set_arrangement_clip_property(
            MagicMock(), track_index=1, clip_index=0, muted=True)

        conn.send_command.assert_not_called()
        assert result.startswith("Error setting arrangement clip property:")

    @patch('MCP_Server.server.get_ableton_connection')
    def test_remote_error_is_reported(self, mock_conn):
        conn = MagicMock()
        conn.send_command.side_effect = Exception("No arrangement clip named 'X' on track 'Gtr'")
        mock_conn.return_value = conn

        result = server.set_arrangement_clip_property(
            MagicMock(), track_index=1, clip_name="X", muted=True)

        assert result == ("Error setting arrangement clip property: "
                          "No arrangement clip named 'X' on track 'Gtr'")


class TestManageClipAutomationClipName:
    @patch('MCP_Server.server.get_ableton_connection')
    def test_forwards_clip_name_not_index(self, mock_conn):
        conn = _connection({"action": "clear_all", "clip_name": "Verse Gtr", "done": True})
        mock_conn.return_value = conn

        result = server.manage_clip_automation(
            MagicMock(), track_index=2, clip_name="Verse Gtr", action="clear_all")

        conn.send_command.assert_called_once_with(
            "manage_clip_automation",
            {"track_index": 1, "clip_name": "Verse Gtr", "clip_index": -1,
             "action": "clear_all", "parameter_name": "volume"})
        assert result == "Cleared all automation on clip 'Verse Gtr', track 2"

    @patch('MCP_Server.server.get_ableton_connection')
    def test_create_message_names_resolved_clip(self, mock_conn):
        mock_conn.return_value = _connection(
            {"action": "create", "parameter": "Volume", "clip_name": "Bridge", "done": True})

        result = server.manage_clip_automation(
            MagicMock(), track_index=3, clip_index=2, action="create",
            parameter_name="volume")

        assert result == "Automation create: volume on clip 'Bridge', track 3"

    @patch('MCP_Server.server.get_ableton_connection')
    def test_falls_back_to_requested_name(self, mock_conn):
        mock_conn.return_value = _connection({"action": "clear", "done": True})

        result = server.manage_clip_automation(
            MagicMock(), track_index=1, clip_name="Verse Gtr", action="clear")

        assert result == "Automation clear: volume on clip 'Verse Gtr', track 1"

    @patch('MCP_Server.server.get_ableton_connection')
    def test_falls_back_to_index(self, mock_conn):
        mock_conn.return_value = _connection(None)

        result = server.manage_clip_automation(
            MagicMock(), track_index=1, clip_index=5, action="clear_all")

        assert result == "Cleared all automation on clip 5, track 1"

    @patch('MCP_Server.server.get_ableton_connection')
    def test_clip_index_zero_without_name_errors(self, mock_conn):
        conn = _connection({})
        mock_conn.return_value = conn

        result = server.manage_clip_automation(
            MagicMock(), track_index=1, clip_index=0, action="clear_all")

        conn.send_command.assert_not_called()
        assert result.startswith("Error managing clip automation:")


# ── Remote Script layer ───────────────────────────────────────────


class _Param:
    def __init__(self, name):
        self.name = name


class _Clip:
    def __init__(self, name):
        self.name = name
        self.muted = False
        self.envelopes_cleared = False
        self.created = []
        self.cleared = []

    def clear_all_envelopes(self):
        self.envelopes_cleared = True

    def create_automation_envelope(self, param):
        self.created.append(param.name)

    def clear_envelope(self, param):
        self.cleared.append(param.name)


class _Track:
    def __init__(self, name, clips):
        self.name = name
        self.arrangement_clips = clips
        self.mixer_device = types.SimpleNamespace(
            volume=_Param("Track Volume"), panning=_Param("Track Panning"),
            sends=[_Param("A-Reverb")])
        self.devices = [types.SimpleNamespace(parameters=[_Param("Cutoff")])]


def _script_with_clips(*names):
    clips = [_Clip(n) for n in names]
    script = AbletonMCP.__new__(AbletonMCP)
    script._song = MagicMock()
    script._song.tracks = [_Track("Gtr", clips)]
    script.logged = []
    script.log_message = script.logged.append
    # Run main-thread work inline, as Live would on its own thread.
    script.schedule_message = lambda _delay, fn: fn()
    return script, clips


class TestRemoteSetArrangementClipProperty:
    def test_name_targets_the_named_clip_not_the_first(self):
        script, clips = _script_with_clips("Intro", "Verse Gtr", "Outro")

        result = script._set_arrangement_clip_property(
            0, None, "muted", True, clip_name="Verse Gtr")

        assert [c.muted for c in clips] == [False, True, False]
        assert result == {"clip_name": "Verse Gtr", "property": "muted", "value": True}

    def test_reports_name_before_rename(self):
        script, clips = _script_with_clips("Verse Gtr")

        result = script._set_arrangement_clip_property(
            0, None, "name", "Verse 2", clip_name="Verse Gtr")

        assert clips[0].name == "Verse 2"
        assert result == {"clip_name": "Verse Gtr", "property": "name", "value": "Verse 2"}

    def test_index_still_works(self):
        script, clips = _script_with_clips("Intro", "Verse Gtr")

        script._set_arrangement_clip_property(0, 1, "muted", True)

        assert [c.muted for c in clips] == [False, True]

    def test_unknown_name_raises_and_logs(self):
        script, clips = _script_with_clips("Intro")

        with pytest.raises(ValueError, match="No arrangement clip named 'Nope'"):
            script._set_arrangement_clip_property(0, None, "muted", True, clip_name="Nope")

        assert clips[0].muted is False
        assert script.logged and "Error setting arrangement clip property" in script.logged[0]

    def test_dispatch_forwards_clip_name(self):
        script, clips = _script_with_clips("Intro", "Verse Gtr")

        response = script._process_command({
            "type": "set_arrangement_clip_property",
            "params": {"track_index": 0, "clip_name": "Verse Gtr", "clip_index": -1,
                       "property": "muted", "value": True},
        })

        assert response == {"status": "success", "result": {
            "clip_name": "Verse Gtr", "property": "muted", "value": True}}
        assert [c.muted for c in clips] == [False, True]

    def test_dispatch_without_index_or_name_errors_instead_of_using_first_clip(self):
        script, clips = _script_with_clips("Intro")

        response = script._process_command({
            "type": "set_arrangement_clip_property",
            "params": {"track_index": 0, "property": "muted", "value": True},
        })

        assert response["status"] == "error"
        assert "clip_index or clip_name" in response["message"]
        assert clips[0].muted is False


    def test_poisoned_index_alone_is_rejected(self):
        # What an outdated Remote Script sees once it drops clip_name.
        script, clips = _script_with_clips("Intro")

        response = script._process_command({
            "type": "set_arrangement_clip_property",
            "params": {"track_index": 0, "clip_index": -1,
                       "property": "muted", "value": True},
        })

        assert response["status"] == "error"
        assert "Clip index -1 out of range" in response["message"]
        assert clips[0].muted is False


class TestRemoteManageClipAutomation:
    def test_clear_all_by_name(self):
        script, clips = _script_with_clips("Intro", "Verse Gtr")

        result = script._manage_clip_automation(0, None, "clear_all", clip_name="Verse Gtr")

        assert [c.envelopes_cleared for c in clips] == [False, True]
        assert result == {"action": "clear_all", "clip_name": "Verse Gtr", "done": True}

    @pytest.mark.parametrize("parameter_name", ["track volume", "A-Reverb", "cutoff"])
    def test_create_by_name_finds_mixer_send_and_device_params(self, parameter_name):
        script, clips = _script_with_clips("Intro", "Verse Gtr")

        result = script._manage_clip_automation(
            0, None, "create", parameter_name, clip_name="Verse Gtr")

        assert clips[0].created == []
        assert [p.lower() for p in clips[1].created] == [parameter_name.lower()]
        assert result["clip_name"] == "Verse Gtr"
        assert result["action"] == "create"

    def test_clear_by_index(self):
        script, clips = _script_with_clips("Intro", "Verse Gtr")

        result = script._manage_clip_automation(0, 1, "clear", "Track Panning")

        assert clips[1].cleared == ["Track Panning"]
        assert result == {"action": "clear", "parameter": "Track Panning",
                          "clip_name": "Verse Gtr", "done": True}

    def test_dispatch_forwards_clip_name(self):
        script, clips = _script_with_clips("Intro", "Verse Gtr")

        response = script._process_command({
            "type": "manage_clip_automation",
            "params": {"track_index": 0, "clip_name": "Verse Gtr",
                       "action": "clear_all", "parameter_name": "volume"},
        })

        assert response["status"] == "success"
        assert response["result"]["clip_name"] == "Verse Gtr"
        assert [c.envelopes_cleared for c in clips] == [False, True]


class TestRemoteDeadCommandRemoved:
    def test_load_instrument_or_effect_is_unknown(self):
        script, _clips = _script_with_clips("Intro")

        response = script._process_command(
            {"type": "load_instrument_or_effect", "params": {}})

        assert response["status"] == "error"
        assert response["message"] == "Unknown command: load_instrument_or_effect"


class TestHarnessErrorPaths:
    def test_error_path_uses_the_stub_control_surface_log_message(self):
        # No per-instance log_message: this goes through whichever
        # ControlSurface stub won the import race. Before the harness fix the
        # browser test's stub had no log_message, so this raised AttributeError.
        script = AbletonMCP.__new__(AbletonMCP)
        script._song = MagicMock()
        script._song.tracks = []
        script.schedule_message = lambda _delay, fn: fn()

        response = script._process_command({
            "type": "set_arrangement_clip_property",
            "params": {"track_index": 3, "clip_name": "X",
                       "property": "muted", "value": True},
        })

        assert response["status"] == "error"
        assert "Track index 3 out of range" in response["message"]
