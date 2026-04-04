"""Unit tests for bar_to_beat and beat_to_bar conversion utilities."""

import sys
import os
from unittest.mock import MagicMock

# Mock mcp dependencies before importing server module
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = MagicMock()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MCP_Server.server import bar_to_beat, beat_to_bar


class TestBarToBeat:
    def test_4_4_bar_1(self):
        # Bar 1 in 4/4 time starts at beat 0.0 (the very beginning)
        assert bar_to_beat(1, 4, 4) == 0.0

    def test_4_4_bar_2(self):
        # Bar 2 in 4/4 time starts at beat 4.0 (one bar of 4 beats)
        assert bar_to_beat(2, 4, 4) == 4.0

    def test_4_4_bar_5(self):
        # Bar 5 in 4/4 time starts at beat 16.0 (four bars × 4 beats)
        assert bar_to_beat(5, 4, 4) == 16.0

    def test_4_4_bar_17(self):
        # Bar 17 in 4/4 time starts at beat 64.0 (sixteen bars × 4 beats)
        assert bar_to_beat(17, 4, 4) == 64.0

    def test_3_4_bar_1(self):
        # Bar 1 in 3/4 time still starts at beat 0.0
        assert bar_to_beat(1, 3, 4) == 0.0

    def test_3_4_bar_5(self):
        # Bar 5 in 3/4 time: 4 bars × 3 beats per bar = beat 12.0
        assert bar_to_beat(5, 3, 4) == 12.0

    def test_6_8_bar_1(self):
        # Bar 1 in 6/8 time starts at beat 0.0
        assert bar_to_beat(1, 6, 8) == 0.0

    def test_6_8_bar_5(self):
        # Bar 5 in 6/8 time: 4 bars × 3 beats per bar = beat 12.0
        # (6 eighth notes = 3 quarter-note beats per bar)
        assert bar_to_beat(5, 6, 8) == 12.0

    def test_6_8_bar_9(self):
        # Bar 9 in 6/8 time: 8 bars × 3 beats per bar = beat 24.0
        assert bar_to_beat(9, 6, 8) == 24.0

    def test_default_time_signature(self):
        # When no time signature is given, defaults to 4/4; bar 3 = beat 8.0
        assert bar_to_beat(3) == 8.0


class TestBeatToBar:
    def test_4_4_beat_0(self):
        # Beat 0.0 in 4/4 time is bar 1 (1-based)
        assert beat_to_bar(0.0, 4, 4) == 1

    def test_4_4_beat_4(self):
        # Beat 4.0 in 4/4 time is bar 2 (exactly one bar elapsed)
        assert beat_to_bar(4.0, 4, 4) == 2

    def test_4_4_beat_16(self):
        # Beat 16.0 in 4/4 time is bar 5 (four complete bars)
        assert beat_to_bar(16.0, 4, 4) == 5

    def test_4_4_beat_64(self):
        # Beat 64.0 in 4/4 time is bar 17 (sixteen complete bars)
        assert beat_to_bar(64.0, 4, 4) == 17

    def test_3_4_beat_0(self):
        # Beat 0.0 in 3/4 time is bar 1
        assert beat_to_bar(0.0, 3, 4) == 1

    def test_3_4_beat_12(self):
        # Beat 12.0 in 3/4 time is bar 5 (4 bars × 3 beats)
        assert beat_to_bar(12.0, 3, 4) == 5

    def test_6_8_beat_0(self):
        # Beat 0.0 in 6/8 time is bar 1
        assert beat_to_bar(0.0, 6, 8) == 1

    def test_6_8_beat_12(self):
        # Beat 12.0 in 6/8 time is bar 5
        assert beat_to_bar(12.0, 6, 8) == 5

    def test_mid_bar_rounds_down(self):
        # A beat position mid-bar should round down to the current bar number
        assert beat_to_bar(2.5, 4, 4) == 1

    def test_default_time_signature(self):
        # Defaults to 4/4; beat 8.0 should be bar 3
        assert beat_to_bar(8.0) == 3


class TestRoundTrip:
    def test_4_4_round_trip(self):
        # Converting bar→beat→bar in 4/4 should return the original bar
        for bar in range(1, 20):
            beat = bar_to_beat(bar, 4, 4)
            assert beat_to_bar(beat, 4, 4) == bar

    def test_3_4_round_trip(self):
        # Converting bar→beat→bar in 3/4 should return the original bar
        for bar in range(1, 20):
            beat = bar_to_beat(bar, 3, 4)
            assert beat_to_bar(beat, 3, 4) == bar

    def test_6_8_round_trip(self):
        # Converting bar→beat→bar in 6/8 should return the original bar
        for bar in range(1, 20):
            beat = bar_to_beat(bar, 6, 8)
            assert beat_to_bar(beat, 6, 8) == bar
