"""Tests for ABLETON_HOST / ABLETON_PORT env-var configuration."""

import importlib
import os
from unittest import mock


def _reload_server_module():
    import MCP_Server.server as server  # noqa: WPS433 (import in function for reload)

    return importlib.reload(server)


def test_get_ableton_connection_uses_default_host_and_port_when_env_unset():
    """When no env vars are set, AbletonConnection should be constructed with localhost:9877."""
    env_without_overrides = {
        k: v for k, v in os.environ.items() if k not in {"ABLETON_HOST", "ABLETON_PORT"}
    }
    with mock.patch.dict(os.environ, env_without_overrides, clear=True):
        server = _reload_server_module()
        with mock.patch.object(server, "_ableton_connection", None):
            with mock.patch.object(server, "AbletonConnection") as mock_cls:
                mock_cls.return_value.connect.return_value = True
                server.get_ableton_connection()
                mock_cls.assert_called_with(host="localhost", port=9877)


def test_get_ableton_connection_uses_env_host_and_port_when_set():
    """When ABLETON_HOST / ABLETON_PORT are set, AbletonConnection should pick them up."""
    overrides = {"ABLETON_HOST": "live-host.example.com", "ABLETON_PORT": "12345"}
    with mock.patch.dict(os.environ, overrides, clear=False):
        server = _reload_server_module()
        with mock.patch.object(server, "_ableton_connection", None):
            with mock.patch.object(server, "AbletonConnection") as mock_cls:
                mock_cls.return_value.connect.return_value = True
                server.get_ableton_connection()
                mock_cls.assert_called_with(host="live-host.example.com", port=12345)


def test_ableton_port_env_is_coerced_to_int():
    """ABLETON_PORT is a string env var; it must be coerced to int for AbletonConnection."""
    with mock.patch.dict(os.environ, {"ABLETON_PORT": "8765"}, clear=False):
        server = _reload_server_module()
        with mock.patch.object(server, "_ableton_connection", None):
            with mock.patch.object(server, "AbletonConnection") as mock_cls:
                mock_cls.return_value.connect.return_value = True
                server.get_ableton_connection()
                args, kwargs = mock_cls.call_args
                assert isinstance(kwargs["port"], int)
                assert kwargs["port"] == 8765
