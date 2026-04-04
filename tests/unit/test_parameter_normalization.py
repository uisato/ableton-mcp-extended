"""Unit tests for parameter normalization helpers (T003)."""
import sys
import os
from unittest.mock import MagicMock

# Mock MCP dependencies before importing server
_mock_mcp_module = MagicMock()
_mock_fastmcp = MagicMock()
_mock_fastmcp.FastMCP.return_value.tool.return_value = lambda fn: fn
sys.modules['mcp'] = _mock_mcp_module
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = _mock_fastmcp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MCP_Server.server import normalize_param, denormalize_param


class TestNormalizeParam:
    """Tests for normalize_param()."""

    def test_midpoint(self):
        # The midpoint of a 0–100 range should normalize to 0.5
        assert normalize_param(50.0, 0.0, 100.0) == 0.5

    def test_minimum_returns_zero(self):
        # A value at the minimum of its range normalizes to 0.0
        assert normalize_param(0.0, 0.0, 100.0) == 0.0

    def test_maximum_returns_one(self):
        # A value at the maximum of its range normalizes to 1.0
        assert normalize_param(100.0, 0.0, 100.0) == 1.0

    def test_negative_range(self):
        # Normalization works correctly with negative min/max values
        assert normalize_param(-6.0, -12.0, 0.0) == 0.5

    def test_clamp_above_max(self):
        # Values exceeding the max should be clamped to 1.0
        assert normalize_param(150.0, 0.0, 100.0) == 1.0

    def test_clamp_below_min(self):
        # Values below the min should be clamped to 0.0
        assert normalize_param(-10.0, 0.0, 100.0) == 0.0

    def test_min_equals_max_returns_zero(self):
        """Division by zero edge case: when min == max, return 0.0."""
        assert normalize_param(5.0, 5.0, 5.0) == 0.0

    def test_small_range(self):
        # Normalization remains accurate with very small ranges
        result = normalize_param(0.5, 0.0, 1.0)
        assert abs(result - 0.5) < 1e-9

    def test_already_normalized_range(self):
        """When min=0 and max=1, the value should pass through unchanged."""
        assert normalize_param(0.75, 0.0, 1.0) == 0.75


class TestDenormalizeParam:
    """Tests for denormalize_param()."""

    def test_midpoint(self):
        # Normalized 0.5 in a 0–100 range should denormalize to 50.0
        assert denormalize_param(0.5, 0.0, 100.0) == 50.0

    def test_zero_returns_min(self):
        # Normalized 0.0 should map back to the minimum of the range
        assert denormalize_param(0.0, 0.0, 100.0) == 0.0

    def test_one_returns_max(self):
        # Normalized 1.0 should map back to the maximum of the range
        assert denormalize_param(1.0, 0.0, 100.0) == 100.0

    def test_negative_range(self):
        # Denormalization works correctly with negative min/max values
        assert denormalize_param(0.5, -12.0, 0.0) == -6.0

    def test_clamp_above_one(self):
        """Normalized values above 1.0 should clamp to the max of the range."""
        assert denormalize_param(1.5, 0.0, 100.0) == 100.0

    def test_clamp_below_zero(self):
        """Normalized values below 0.0 should clamp to the min of the range."""
        assert denormalize_param(-0.5, 0.0, 100.0) == 0.0

    def test_roundtrip(self):
        """Normalizing then denormalizing should return the original value."""
        original = 42.0
        normalized = normalize_param(original, 0.0, 100.0)
        result = denormalize_param(normalized, 0.0, 100.0)
        assert abs(result - original) < 1e-9

    def test_roundtrip_negative_range(self):
        # Round-trip accuracy holds for negative parameter ranges too
        original = -3.0
        normalized = normalize_param(original, -12.0, 0.0)
        result = denormalize_param(normalized, -12.0, 0.0)
        assert abs(result - original) < 1e-9
