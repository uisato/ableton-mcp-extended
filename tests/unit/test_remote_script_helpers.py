"""Unit tests for AbletonMCP Remote Script helpers."""

import os
import sys
import types
from unittest.mock import MagicMock


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
    script.log_message = lambda _msg: None
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


class _Live12Track(_NormalTrack):
    """Live 12 exposes create_midi_clip(start_time, length) on Track."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.create_midi_clip = MagicMock()


class _Live11Track(_NormalTrack):
    """Live 11 has no create_midi_clip on Track — must round-trip through a slot."""

    def __init__(self, slots=None, **kw):
        super().__init__(**kw)
        self.clip_slots = list(slots or [])
        self.duplicate_clip_to_arrangement = MagicMock()


def _empty_slot():
    slot = MagicMock()
    slot.has_clip = False
    new_clip = MagicMock()

    def _create(length):
        slot.has_clip = True
        slot.clip = new_clip

    def _delete():
        slot.has_clip = False
        slot.clip = None

    slot.create_clip.side_effect = _create
    slot.delete_clip.side_effect = _delete
    return slot, new_clip


def _full_slot():
    slot = MagicMock()
    slot.has_clip = True
    return slot


class TestCreateArrangementClipLive12:
    def test_calls_create_midi_clip_with_start_and_length(self):
        track = _Live12Track()
        script = _make_script([track])

        script._create_arrangement_clip(track_index=0, position=8.0, length=16.0)

        track.create_midi_clip.assert_called_once_with(8.0, 16.0)

    def test_assigns_name_to_new_clip(self):
        track = _Live12Track()
        new_clip = MagicMock()
        new_clip.start_time = 8.0
        new_clip.end_time = 12.0
        track.create_midi_clip.return_value = new_clip
        script = _make_script([track])

        script._create_arrangement_clip(
            track_index=0, position=8.0, length=4.0, name="Intro")

        assert new_clip.name == "Intro"

    def test_blank_name_does_not_overwrite(self):
        track = _Live12Track()
        new_clip = MagicMock()
        new_clip.start_time = 0.0
        new_clip.end_time = 4.0
        new_clip.name = "Original"
        track.create_midi_clip.return_value = new_clip
        script = _make_script([track])

        script._create_arrangement_clip(
            track_index=0, position=0.0, length=4.0, name="")

        assert new_clip.name == "Original"


class TestCreateArrangementClipLive11Fallback:
    def test_round_trips_through_empty_session_slot(self):
        empty, new_clip = _empty_slot()
        track = _Live11Track(slots=[_full_slot(), empty])
        script = _make_script([track])

        script._create_arrangement_clip(track_index=0, position=8.0, length=4.0)

        empty.create_clip.assert_called_once_with(4.0)
        track.duplicate_clip_to_arrangement.assert_called_once_with(new_clip, 8.0)
        empty.delete_clip.assert_called_once_with()

    def test_cleans_up_session_clip_when_duplicate_fails(self):
        empty, _ = _empty_slot()
        track = _Live11Track(slots=[empty])
        track.duplicate_clip_to_arrangement.side_effect = RuntimeError("boom")
        script = _make_script([track])

        try:
            script._create_arrangement_clip(track_index=0, position=0.0, length=4.0)
        except RuntimeError:
            pass

        empty.delete_clip.assert_called_once_with()

    def test_raises_when_no_empty_slot(self):
        track = _Live11Track(slots=[_full_slot(), _full_slot()])
        script = _make_script([track])

        try:
            script._create_arrangement_clip(track_index=0, position=0.0, length=4.0)
        except Exception as e:
            assert "empty" in str(e).lower() or "slot" in str(e).lower()
        else:
            raise AssertionError("expected an error when no empty slot is available")

        track.duplicate_clip_to_arrangement.assert_not_called()
