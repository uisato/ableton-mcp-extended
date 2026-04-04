"""Unit tests for the 1-based → 0-based index conversion helpers."""

import sys
import os
from unittest.mock import MagicMock
import pytest

# Mock mcp dependencies before importing server module
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = MagicMock()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MCP_Server.server import _to_zero_based, _optional_to_zero_based


# ── _to_zero_based ──────────────────────────────────────────────


class TestToZeroBased:
    def test_converts_1_to_0(self):
        # The smallest valid 1-based index should map to 0
        assert _to_zero_based(1) == 0

    def test_converts_5_to_4(self):
        # A mid-range 1-based index subtracts one correctly
        assert _to_zero_based(5) == 4

    def test_converts_100_to_99(self):
        # Large indices convert correctly without overflow issues
        assert _to_zero_based(100) == 99

    def test_rejects_zero(self):
        # Zero is not a valid 1-based index and should raise ValueError
        with pytest.raises(ValueError, match="must be >= 1"):
            _to_zero_based(0)

    def test_rejects_negative(self):
        # Negative values are invalid 1-based indices
        with pytest.raises(ValueError, match="must be >= 1"):
            _to_zero_based(-1)

    def test_error_includes_field_name(self):
        # The error message should include the custom field name for debugging
        with pytest.raises(ValueError, match="track_index"):
            _to_zero_based(0, "track_index")

    def test_default_field_name(self):
        # When no field name is given, the error should use the default "index"
        with pytest.raises(ValueError, match="index"):
            _to_zero_based(0)


# ── _optional_to_zero_based ─────────────────────────────────────


class TestOptionalToZeroBased:
    def test_zero_returns_none(self):
        # Zero means "not specified" for optional indices, so it returns None
        assert _optional_to_zero_based(0) is None

    def test_converts_1_to_0(self):
        # A provided optional index of 1 should convert to 0-based
        assert _optional_to_zero_based(1) == 0

    def test_converts_3_to_2(self):
        # A mid-range optional index subtracts one correctly
        assert _optional_to_zero_based(3) == 2

    def test_rejects_negative(self):
        # Negative values are never valid, even for optional indices
        with pytest.raises(ValueError, match="must be >= 0"):
            _optional_to_zero_based(-1)

    def test_error_includes_field_name(self):
        # The error message should include the custom field name for debugging
        with pytest.raises(ValueError, match="chain_index"):
            _optional_to_zero_based(-1, "chain_index")
