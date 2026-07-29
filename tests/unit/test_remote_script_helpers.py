"""Unit tests for AbletonMCP Remote Script helpers."""

import os
import sys
import types
from unittest.mock import MagicMock

import pytest


class _StubControlSurface:
    def __init__(self, c_instance):
        pass

    def log_message(self, msg):
        pass


_framework = types.ModuleType("_Framework")
_cs_module = types.ModuleType("_Framework.ControlSurface")
_cs_module.ControlSurface = _StubControlSurface
sys.modules.setdefault("_Framework", _framework)
sys.modules.setdefault("_Framework.ControlSurface", _cs_module)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from AbletonMCP_Remote_Script import AbletonMCP  # noqa: E402


class _NormalTrack:
    is_foldable = False

    def __init__(self, name="Track", arm=False, has_midi_input=True,
                 has_audio_input=False, arrangement_clips=None):
        self.name = name
        self.arm = arm
        self.mute = False
        self.solo = False
        self.has_midi_input = has_midi_input
        self.has_audio_input = has_audio_input
        self.clip_slots = []
        self.devices = []
        self.arrangement_clips = list(arrangement_clips or [])
        self.mixer_device = MagicMock()
        self.mixer_device.volume.value = 0.85
        self.mixer_device.panning.value = 0.0


class _GroupTrack:
    is_foldable = True

    def __init__(self, name="Mix Bus"):
        self.name = name
        self.mute = False
        self.solo = False
        self.has_midi_input = False
        self.has_audio_input = False
        self.clip_slots = []
        self.devices = []
        self.mixer_device = MagicMock()
        self.mixer_device.volume.value = 0.85
        self.mixer_device.panning.value = 0.0

    @property
    def arm(self):
        raise RuntimeError("Master and Return Tracks have no 'Arm' state!")

    @property
    def arrangement_clips(self):
        raise RuntimeError(
            "Master, Group and Return Tracks have no arrangement clips")


def _make_script(tracks=()):
    script = AbletonMCP.__new__(AbletonMCP)
    # Whichever test module registers the _Framework.ControlSurface stub FIRST
    # wins: test_browser_path_normalization.py assigns into sys.modules while
    # this file uses setdefault, and collection is alphabetical. So the base
    # class here may be a stub with no log_message. Every handler calls
    # self.log_message in its except block, which turned every intended
    # IndexError/ValueError into an AttributeError once the full suite ran --
    # making error paths untestable. A no-op keeps the tests order-independent.
    script.log_message = lambda msg: None
    script._song = MagicMock()
    script._song.tracks = list(tracks)
    script._song.return_tracks = []
    script._song.master_track = MagicMock()
    return script


class TestGetTrackInfoOnGroupTrack:
    def test_returns_info_without_raising(self):
        script = _make_script([_GroupTrack("Mix Bus")])

        result = script._get_track_info(0)

        assert result["name"] == "Mix Bus"
        assert result["is_group_track"] is True
        assert result["arm"] is None

    def test_normal_track_still_reports_arm(self):
        script = _make_script([_NormalTrack("Synth", arm=True)])

        result = script._get_track_info(0)

        assert result["arm"] is True
        assert result["is_group_track"] is False


class TestGetArrangementInfoSkipsGroupTracks:
    def test_all_tracks_skips_group(self):
        normal = _NormalTrack("Drums")
        group = _GroupTrack("Mix Bus")
        script = _make_script([group, normal])

        result = script._get_arrangement_info(-1)

        names = [t["name"] for t in result["tracks"]]
        assert names == ["Drums"]

    def test_explicit_group_returns_empty_clips(self):
        script = _make_script([_GroupTrack("Mix Bus")])

        result = script._get_arrangement_info(0)

        assert len(result["tracks"]) == 1
        assert result["tracks"][0]["arrangement_clips"] == []
        assert result["tracks"][0]["is_group_track"] is True

    def test_normal_track_unaffected(self):
        script = _make_script([_NormalTrack("Drums")])

        result = script._get_arrangement_info(0)

        assert result["tracks"][0]["name"] == "Drums"
        assert result["tracks"][0]["is_group_track"] is False


class TestCreateCuePointAssignsName:
    @staticmethod
    def _wire_toggle(script, returned_cue):
        script._song.cue_points = ()

        def toggle():
            script._song.cue_points = (returned_cue,)

        script._song.set_or_delete_cue.side_effect = toggle

    def test_assigns_name_to_created_cue(self):
        script = _make_script()
        cue = MagicMock()
        cue.time = 16.0
        cue.name = ""
        self._wire_toggle(script, cue)

        script._create_cue_point(time=16.0, name="Drop")

        assert cue.name == "Drop"

    def test_blank_name_does_not_overwrite(self):
        script = _make_script()
        cue = MagicMock()
        cue.time = 16.0
        cue.name = "1.1.1"
        self._wire_toggle(script, cue)

        script._create_cue_point(time=16.0, name="")

        assert cue.name == "1.1.1"


class TestSetTrackMuteAndSolo:
    def test_mute_sets_the_flag_and_reports_it(self):
        track = _NormalTrack("Drums")
        script = _make_script([track])

        result = script._set_track_mute(0, True)

        assert track.mute is True
        assert result == {"track_name": "Drums", "mute": True}

    def test_mute_can_be_cleared(self):
        track = _NormalTrack("Drums")
        track.mute = True
        script = _make_script([track])

        result = script._set_track_mute(0, False)

        assert track.mute is False
        assert result["mute"] is False

    def test_solo_sets_the_flag_and_reports_it(self):
        track = _NormalTrack("Bass")
        script = _make_script([track])

        result = script._set_track_solo(0, True)

        assert track.solo is True
        assert result == {"track_name": "Bass", "solo": True}

    def test_group_tracks_can_be_muted(self):
        group = _GroupTrack("Mix Bus")
        script = _make_script([group])

        result = script._set_track_mute(0, True)

        assert group.mute is True
        assert result["track_name"] == "Mix Bus"

    def test_return_tracks_can_be_muted(self):
        normal = _NormalTrack("Drums")
        send = _NormalTrack("A-Reverb")
        script = _make_script([normal])
        script._song.return_tracks = [send]

        result = script._set_track_mute(1, True)

        assert send.mute is True
        assert result["track_name"] == "A-Reverb"

    def test_index_out_of_range_raises(self):
        script = _make_script([_NormalTrack("Drums")])

        with pytest.raises(IndexError):
            script._set_track_mute(7, True)


class TestSetTrackArmGuards:
    def test_arms_a_normal_track(self):
        track = _NormalTrack("Synth")
        script = _make_script([track])

        result = script._set_track_arm(0, True)

        assert track.arm is True
        assert result == {"track_name": "Synth", "arm": True}

    def test_group_track_is_refused_before_live_can_raise(self):
        """_GroupTrack.arm raises RuntimeError, as Live does.

        The guard must fire FIRST, so the caller gets a sentence it can act on
        instead of "Master and Return Tracks have no 'Arm' state!".
        """
        script = _make_script([_GroupTrack("Mix Bus")])

        with pytest.raises(ValueError) as excinfo:
            script._set_track_arm(0, True)

        assert "no Arm state" in str(excinfo.value)

    def test_return_track_is_refused(self):
        script = _make_script([_NormalTrack("Drums")])
        script._song.return_tracks = [_NormalTrack("A-Reverb")]

        with pytest.raises(IndexError) as excinfo:
            script._set_track_arm(1, True)

        assert "no Arm state" in str(excinfo.value)

    def test_a_track_that_cannot_be_armed_is_refused(self):
        track = _NormalTrack("Odd")
        track.can_be_armed = False
        script = _make_script([track])

        with pytest.raises(ValueError) as excinfo:
            script._set_track_arm(0, True)

        assert "cannot be armed" in str(excinfo.value)


class TestMuteSoloArmAreActuallyReachable:
    """A handler missing from EITHER dispatcher list is dead code.

    load_instrument_or_effect has a handler and is absent from the gate list, so
    the script answers "Unknown command" -- a bug that survived because every
    test called the handler directly and none went through _process_command.

    A command in the gate list but missing from the main_thread_task elif chain
    fails worse: it reaches the main-thread block, matches no branch, leaves
    result as None and returns {"status": "success", "result": None}. It looks
    like it worked.

    These tests go through _process_command, so they catch both.
    """

    @staticmethod
    def _dispatch(script, command_type, params):
        # schedule_message raises AssertionError off the main thread, which the
        # dispatcher already handles by running the task inline. That is the
        # real code path, not a bypass.
        script.schedule_message = MagicMock(side_effect=AssertionError)
        return script._process_command({"type": command_type, "params": params})

    def test_set_track_mute_round_trips_through_the_dispatcher(self):
        track = _NormalTrack("Drums")
        script = _make_script([track])

        response = self._dispatch(script, "set_track_mute",
                                  {"track_index": 0, "mute": True})

        assert response["status"] == "success", response
        assert response["result"] == {"track_name": "Drums", "mute": True}
        assert track.mute is True

    def test_set_track_solo_round_trips_through_the_dispatcher(self):
        track = _NormalTrack("Bass")
        script = _make_script([track])

        response = self._dispatch(script, "set_track_solo",
                                  {"track_index": 0, "solo": True})

        assert response["status"] == "success", response
        assert response["result"] == {"track_name": "Bass", "solo": True}
        assert track.solo is True

    def test_set_track_arm_round_trips_through_the_dispatcher(self):
        track = _NormalTrack("Synth")
        script = _make_script([track])

        response = self._dispatch(script, "set_track_arm",
                                  {"track_index": 0, "arm": True})

        assert response["status"] == "success", response
        assert response["result"] == {"track_name": "Synth", "arm": True}
        assert track.arm is True

    def test_arming_a_group_track_reports_an_error_not_a_success(self):
        script = _make_script([_GroupTrack("Mix Bus")])

        response = self._dispatch(script, "set_track_arm",
                                  {"track_index": 0, "arm": True})

        assert response["status"] == "error", response
        assert "no Arm state" in response["message"]

    def test_an_unknown_command_still_errors(self):
        """The control. Without it the assertions above could be vacuous."""
        script = _make_script([_NormalTrack("Drums")])

        response = self._dispatch(script, "set_track_frobnicate",
                                  {"track_index": 0})

        assert response["status"] == "error", response
        assert "Unknown command" in response["message"]
