"""Regression: server.py must work when launched as `python /path/to/server.py`.

Claude Desktop's MCP launcher invokes the server by absolute script path, which
puts only the script's directory on sys.path — the parent `MCP_Server` package
is not importable that way, so any `from MCP_Server.X import Y` inside a tool
handler must be resilient to that layout.
"""
import os
import subprocess
import sys
import textwrap


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PKG_DIR = os.path.join(REPO_ROOT, "MCP_Server")
SERVER_PATH = os.path.join(PKG_DIR, "server.py")


def _run_in_script_mode(snippet: str) -> subprocess.CompletedProcess:
    bootstrap = textwrap.dedent(
        f"""
        import sys
        from unittest.mock import MagicMock
        sys.modules['mcp'] = MagicMock()
        sys.modules['mcp.server'] = MagicMock()
        fastmcp = MagicMock()
        fastmcp.FastMCP.return_value.tool.return_value = lambda fn: fn
        sys.modules['mcp.server.fastmcp'] = fastmcp

        sys.path = [p for p in sys.path if p not in ('', {REPO_ROOT!r})]
        sys.path.insert(0, {PKG_DIR!r})

        import importlib.util
        spec = importlib.util.spec_from_file_location('server', {SERVER_PATH!r})
        server = importlib.util.module_from_spec(spec)
        sys.modules['server'] = server
        spec.loader.exec_module(server)
        """
    )
    return subprocess.run(
        [sys.executable, "-c", bootstrap + "\n" + snippet],
        capture_output=True,
        text=True,
        cwd="/",
    )


def test_get_device_parameters_does_not_crash_on_lazy_import():
    snippet = textwrap.dedent(
        """
        from unittest.mock import MagicMock
        ableton = MagicMock()
        ableton.send_command.return_value = {
            'device_name': 'Pro-Q 3',
            'device_class': 'PluginDevice',
            'parameter_count': 1,
            'parameters': [{
                'index': 0, 'name': 'Output Gain', 'value': 0.5,
                'min': 0.0, 'max': 1.0, 'display_value': '0 dB',
                'is_enabled': True, 'is_quantized': False, 'value_items': [],
            }],
        }
        server.get_ableton_connection = lambda: ableton
        out = server.get_device_parameters(MagicMock(), track_index=2, device_index=2)
        print(out)
        """
    )
    proc = _run_in_script_mode(snippet)
    assert proc.returncode == 0, proc.stderr
    assert "No module named" not in proc.stdout, proc.stdout
    assert "Pro-Q 3" in proc.stdout


def test_set_device_parameter_does_not_crash_on_lazy_import():
    snippet = textwrap.dedent(
        """
        from unittest.mock import MagicMock
        ableton = MagicMock()
        ableton.send_command.side_effect = [
            {'device_name': 'Pro-Q 3'},
            {'parameter_name': 'Output Gain', 'display_value': '0 dB',
             'new_value': 0.5, 'clamped': False},
        ]
        server.get_ableton_connection = lambda: ableton
        out = server.set_device_parameter(
            MagicMock(), track_index=2, device_index=2,
            parameter_name='Output Gain', value=0.5,
        )
        print(out)
        """
    )
    proc = _run_in_script_mode(snippet)
    assert proc.returncode == 0, proc.stderr
    assert "No module named" not in proc.stdout, proc.stdout
    assert "Output Gain" in proc.stdout
