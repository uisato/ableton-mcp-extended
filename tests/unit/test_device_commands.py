"""Unit tests for device MCP tools (T011, T015, T020, T026, T030, T034)."""
import sys
import os
from unittest.mock import MagicMock, patch

# Mock MCP dependencies before importing server
_mock_mcp_module = MagicMock()
_mock_fastmcp = MagicMock()
_mock_fastmcp.FastMCP.return_value.tool.return_value = lambda fn: fn
sys.modules['mcp'] = _mock_mcp_module
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = _mock_fastmcp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from MCP_Server.server import (
    get_device_parameters,
    set_device_parameter,
    enable_device,
    disable_device,
    get_chain_info,
    get_drum_pad_info,
    delete_device,
    navigate_device_preset,
)


class TestGetDeviceParameters:
    """Test get_device_parameters tool."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_sends_correct_command(self, mock_conn):
        # Track 1 → 0, device 2 → 1; verify the RS receives 0-based indices
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "device_name": "Wavetable",
            "device_class": "Wavetable",
            "parameter_count": 2,
            "parameters": [
                {"index": 0, "name": "Osc 1 Shape", "value": 0.5, "min": 0.0,
                 "max": 1.0, "display_value": "50%", "is_enabled": True,
                 "is_quantized": False, "value_items": []},
                {"index": 1, "name": "Filter Freq", "value": 0.8, "min": 0.0,
                 "max": 1.0, "display_value": "800 Hz", "is_enabled": True,
                 "is_quantized": False, "value_items": []},
            ],
        }
        mock_conn.return_value = mock_ableton

        result = get_device_parameters(MagicMock(), track_index=1, device_index=2)
        mock_ableton.send_command.assert_called_with("get_device_parameters", {
            "track_index": 0,
            "device_index": 1,
            "chain_index": None,
            "show_all": True,
        })
        assert "Wavetable" in result
        assert "2 parameters" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_detail_mode_show_all(self, mock_conn):
        # With show_all=True, the result should list individual parameter names and values
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "device_name": "Serum",
            "device_class": "PluginDevice",
            "parameter_count": 1,
            "parameters": [
                {"index": 0, "name": "Osc A WT Pos", "value": 0.5, "min": 0.0,
                 "max": 1.0, "display_value": "50%", "is_enabled": True,
                 "is_quantized": False, "value_items": []},
            ],
        }
        mock_conn.return_value = mock_ableton

        result = get_device_parameters(MagicMock(), track_index=1, show_all=True)
        assert "Osc A WT Pos" in result
        assert "50%" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_chain_index_converted(self, mock_conn):
        # Chain index 2 (1-based) should convert to 1 (0-based) before sending
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "device_name": "Test", "device_class": "Test",
            "parameter_count": 0, "parameters": [],
        }
        mock_conn.return_value = mock_ableton

        get_device_parameters(MagicMock(), track_index=1, chain_index=2)
        call_args = mock_ableton.send_command.call_args
        assert call_args[0][1]["chain_index"] == 1  # 2 - 1

    @patch('MCP_Server.server.get_categories', return_value={})
    @patch('MCP_Server.server.get_ableton_connection')
    def test_summary_drops_bucket_when_only_one_category(self, mock_conn, _mock_cats):
        # When categorization yields one bucket (e.g. all "Other" because the
        # device has no defined prefixes), don't print "Other: N parameters" —
        # it's noise. Drop it and just point at show_all.
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "device_name": "Operator",
            "device_class": "Operator",
            "parameter_count": 3,
            "parameters": [
                {"index": 0, "name": "Foo", "value": 0.0, "min": 0.0, "max": 1.0,
                 "display_value": "0", "is_enabled": True, "is_quantized": False,
                 "value_items": []},
                {"index": 1, "name": "Bar", "value": 0.0, "min": 0.0, "max": 1.0,
                 "display_value": "0", "is_enabled": True, "is_quantized": False,
                 "value_items": []},
                {"index": 2, "name": "Baz", "value": 0.0, "min": 0.0, "max": 1.0,
                 "display_value": "0", "is_enabled": True, "is_quantized": False,
                 "value_items": []},
            ],
        }
        mock_conn.return_value = mock_ableton

        result = get_device_parameters(MagicMock(), track_index=1)
        assert "Other:" not in result
        assert "show_all=True" in result


class TestSetDeviceParameter:
    """Test set_device_parameter tool."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_sends_correct_command_by_name(self, mock_conn):
        # Setting a parameter by name should resolve the name and send the correct value
        mock_ableton = MagicMock()
        # First call: get_device_parameters for alias resolution
        mock_ableton.send_command.side_effect = [
            {"device_name": "Wavetable", "parameters": []},
            {"parameter_name": "Filter Freq", "old_value": 0.5,
             "new_value": 0.8, "display_value": "800 Hz", "clamped": False},
        ]
        mock_conn.return_value = mock_ableton

        result = set_device_parameter(MagicMock(), track_index=1,
                                      parameter_name="Filter Freq", value=0.8)
        assert "Filter Freq" in result
        assert "800 Hz" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_sends_by_index(self, mock_conn):
        # Setting a parameter by index should bypass alias resolution
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "parameter_name": "Volume", "old_value": 0.5,
            "new_value": 0.75, "display_value": "-3 dB", "clamped": False,
        }
        mock_conn.return_value = mock_ableton

        result = set_device_parameter(MagicMock(), track_index=1, parameter_index=5, value=0.75)
        assert "Volume" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_clamp_warning(self, mock_conn):
        # When the RS clamps a value, the result should mention it was clamped
        mock_ableton = MagicMock()
        mock_ableton.send_command.side_effect = [
            {"device_name": "Test", "parameters": []},
            {"parameter_name": "P", "old_value": 0.0,
             "new_value": 1.0, "display_value": "max", "clamped": True},
        ]
        mock_conn.return_value = mock_ableton

        result = set_device_parameter(MagicMock(), track_index=1,
                                      parameter_name="P", value=1.5)
        assert "clamped" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_alias_resolution(self, mock_conn):
        # A friendly alias like "wavetable position" should resolve to the real param name
        mock_ableton = MagicMock()
        mock_ableton.send_command.side_effect = [
            {"device_name": "Serum", "parameters": []},
            {"parameter_name": "Osc A WT Pos", "old_value": 0.0,
             "new_value": 0.5, "display_value": "50%", "clamped": False},
        ]
        mock_conn.return_value = mock_ableton

        result = set_device_parameter(MagicMock(), track_index=1,
                                      parameter_name="wavetable position", value=0.5)
        # The alias should have been resolved to "Osc A WT Pos"
        second_call = mock_ableton.send_command.call_args_list[1]
        assert second_call[0][1]["parameter_name"] == "Osc A WT Pos"
        assert "alias" in result

    def test_value_is_required(self):
        # Calling without value should fail with TypeError — guards against
        # silent default-to-0.0 when an LLM uses a synonym like
        # ``normalized_value=`` and the unknown kwarg gets dropped.
        try:
            set_device_parameter(MagicMock(), track_index=1, parameter_index=5)
        except TypeError as e:
            assert "value" in str(e).lower()
        else:
            raise AssertionError("expected TypeError when 'value' is omitted")


class TestEnableDisableDevice:
    """Test enable_device and disable_device tools."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_enable_by_index(self, mock_conn):
        # Enabling device 2 on track 1 should send enabled=True with 0-based indices
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "device_name": "Compressor", "is_active": True,
        }
        mock_conn.return_value = mock_ableton

        result = enable_device(MagicMock(), track_index=1, device_index=2)
        call_args = mock_ableton.send_command.call_args
        assert call_args[0][0] == "set_device_enabled"
        assert call_args[0][1]["enabled"] is True
        assert "enabled" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_disable_by_index(self, mock_conn):
        # Disabling device 1 on track 1 should send enabled=False
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "device_name": "EQ Eight", "is_active": False,
        }
        mock_conn.return_value = mock_ableton

        result = disable_device(MagicMock(), track_index=1, device_index=1)
        call_args = mock_ableton.send_command.call_args
        assert call_args[0][1]["enabled"] is False
        assert "disabled" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_by_name_resolves(self, mock_conn):
        # When device_name is given instead of device_index, resolve to the correct 0-based index
        mock_ableton = MagicMock()
        mock_ableton.send_command.side_effect = [
            {"devices": [{"index": 0, "name": "Compressor"}, {"index": 1, "name": "EQ Eight"}]},
            {"device_name": "EQ Eight", "is_active": False},
        ]
        mock_conn.return_value = mock_ableton

        result = disable_device(MagicMock(), track_index=1, device_name="EQ Eight")
        second_call = mock_ableton.send_command.call_args_list[1]
        assert second_call[0][1]["device_index"] == 1

    @patch('MCP_Server.server.get_ableton_connection')
    def test_ambiguous_name_error(self, mock_conn):
        # Multiple devices with the same name should produce an error instead of guessing
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "devices": [{"index": 0, "name": "EQ Eight"}, {"index": 1, "name": "EQ Eight"}],
        }
        mock_conn.return_value = mock_ableton

        result = disable_device(MagicMock(), track_index=1, device_name="EQ Eight")
        assert "Multiple" in result


class TestGetChainInfo:
    """Test get_chain_info and get_drum_pad_info."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_list_chains(self, mock_conn):
        # Listing chains should show chain count, names, and devices inside each chain
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "device_name": "Instrument Rack",
            "chain_count": 2,
            "chains": [
                {"index": 0, "name": "A", "mute": False, "solo": False,
                 "device_count": 1, "devices": [{"index": 0, "name": "Serum", "type": "instrument"}]},
                {"index": 1, "name": "B", "mute": True, "solo": False,
                 "device_count": 1, "devices": [{"index": 0, "name": "Diva", "type": "instrument"}]},
            ],
        }
        mock_conn.return_value = mock_ableton

        result = get_chain_info(MagicMock(), track_index=1)
        assert "2 chains" in result
        assert "Serum" in result
        assert "[muted]" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_not_a_rack_error(self, mock_conn):
        # Requesting chain info on a non-rack device should return an error message
        mock_ableton = MagicMock()
        mock_ableton.send_command.side_effect = Exception("Device 'Serum' is not a rack")
        mock_conn.return_value = mock_ableton

        result = get_chain_info(MagicMock(), track_index=1)
        assert "Error" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_drum_pad_info(self, mock_conn):
        # Drum pad info should list filled pads with their note numbers, names, and devices
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "device_name": "Drum Rack",
            "filled_pads": [
                {"note": 36, "name": "Kick", "mute": False, "solo": False,
                 "chains": [{"name": "Chain", "devices": [{"index": 0, "name": "Simpler", "type": "instrument"}]}]},
            ],
        }
        mock_conn.return_value = mock_ableton

        result = get_drum_pad_info(MagicMock(), track_index=1)
        assert "1 filled pads" in result
        assert "Kick" in result
        assert "Note 36" in result


class TestDeleteDevice:
    """Test delete_device tool."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_delete_by_index(self, mock_conn):
        # Track 1 → 0, device 2 → 1; verify the correct 0-based indices are sent
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "deleted_device": "Compressor", "remaining_devices": 1,
        }
        mock_conn.return_value = mock_ableton

        result = delete_device(MagicMock(), track_index=1, device_index=2)
        mock_ableton.send_command.assert_called_with("delete_device", {
            "track_index": 0, "device_index": 1,
        })
        assert "Deleted Compressor" in result
        assert "1 devices remaining" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_delete_by_name(self, mock_conn):
        # When deleting by name, resolve the device name to its 0-based index first
        mock_ableton = MagicMock()
        mock_ableton.send_command.side_effect = [
            {"devices": [{"index": 0, "name": "EQ Eight"}, {"index": 1, "name": "Limiter"}]},
            {"deleted_device": "Limiter", "remaining_devices": 1},
        ]
        mock_conn.return_value = mock_ableton

        result = delete_device(MagicMock(), track_index=1, device_name="Limiter")
        second_call = mock_ableton.send_command.call_args_list[1]
        assert second_call[0][1]["device_index"] == 1


class TestNavigateDevicePreset:
    """Test navigate_device_preset tool."""

    @patch('MCP_Server.server.get_ableton_connection')
    def test_next_preset(self, mock_conn):
        # Navigating to next preset should send 0-based indices and direction="next"
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "device_name": "Serum", "preset_name": "Warm Pad",
            "preset_index": 5, "preset_count": 128,
        }
        mock_conn.return_value = mock_ableton

        result = navigate_device_preset(MagicMock(), track_index=1, direction="next")
        mock_ableton.send_command.assert_called_with("navigate_preset", {
            "track_index": 0, "device_index": 0, "chain_index": None, "direction": "next",
        })
        assert "Warm Pad" in result
        assert "6/128" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_current_preset(self, mock_conn):
        # Direction "current" should report the active preset without changing it
        mock_ableton = MagicMock()
        mock_ableton.send_command.return_value = {
            "device_name": "Serum", "preset_name": "Init",
            "preset_index": 0, "preset_count": 128,
        }
        mock_conn.return_value = mock_ableton

        result = navigate_device_preset(MagicMock(), track_index=1, direction="current")
        assert "current preset is" in result
        assert "Init" in result

    @patch('MCP_Server.server.get_ableton_connection')
    def test_no_presets_error(self, mock_conn):
        # When a device has no presets, the error should be reported gracefully
        mock_ableton = MagicMock()
        mock_ableton.send_command.side_effect = Exception("Device has no presets")
        mock_conn.return_value = mock_ableton

        result = navigate_device_preset(MagicMock(), track_index=1, direction="next")
        assert "Error" in result
