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
        assert normalize_param(50.0, 0.0, 100.0) == 0.5

    def test_minimum_returns_zero(self):
        assert normalize_param(0.0, 0.0, 100.0) == 0.0

    def test_maximum_returns_one(self):
        assert normalize_param(100.0, 0.0, 100.0) == 1.0

    def test_negative_range(self):
        assert normalize_param(-6.0, -12.0, 0.0) == 0.5

    def test_clamp_above_max(self):
        assert normalize_param(150.0, 0.0, 100.0) == 1.0

    def test_clamp_below_min(self):
        assert normalize_param(-10.0, 0.0, 100.0) == 0.0

    def test_min_equals_max_returns_zero(self):
        """Division by zero edge case."""
        assert normalize_param(5.0, 5.0, 5.0) == 0.0

    def test_small_range(self):
        result = normalize_param(0.5, 0.0, 1.0)
        assert abs(result - 0.5) < 1e-9

    def test_already_normalized_range(self):
        """When min=0, max=1, value should pass through."""
        assert normalize_param(0.75, 0.0, 1.0) == 0.75


class TestDenormalizeParam:
    """Tests for denormalize_param()."""

    def test_midpoint(self):
        assert denormalize_param(0.5, 0.0, 100.0) == 50.0

    def test_zero_returns_min(self):
        assert denormalize_param(0.0, 0.0, 100.0) == 0.0

    def test_one_returns_max(self):
        assert denormalize_param(1.0, 0.0, 100.0) == 100.0

    def test_negative_range(self):
        assert denormalize_param(0.5, -12.0, 0.0) == -6.0

    def test_clamp_above_one(self):
        """Values above 1.0 should clamp to max."""
        assert denormalize_param(1.5, 0.0, 100.0) == 100.0

    def test_clamp_below_zero(self):
        """Values below 0.0 should clamp to min."""
        assert denormalize_param(-0.5, 0.0, 100.0) == 0.0

    def test_roundtrip(self):
        """normalize then denormalize should return original value."""
        original = 42.0
        normalized = normalize_param(original, 0.0, 100.0)
        result = denormalize_param(normalized, 0.0, 100.0)
        assert abs(result - original) < 1e-9

    def test_roundtrip_negative_range(self):
        original = -3.0
        normalized = normalize_param(original, -12.0, 0.0)
        result = denormalize_param(normalized, -12.0, 0.0)
        assert abs(result - original) < 1e-9
