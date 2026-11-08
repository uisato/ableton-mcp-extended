"""The MCP server and the Remote Script must agree on which commands write.

The Remote Script runs MAIN_THREAD_COMMANDS on Live's main thread; the MCP
server gives MODIFYING_COMMANDS the longer write timeout. Nothing else ties the
two lists together, so these tests compare them, and check them against the
commands the MCP tools actually send over the wire. In that protocol, read
commands are named ``get_*`` and everything else changes Live's state.
"""

import inspect
import os
import sys
import types
from unittest.mock import MagicMock, patch

import pytest

_mock_fastmcp = MagicMock()
_mock_fastmcp.FastMCP.return_value.tool.return_value = lambda fn: fn
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = _mock_fastmcp


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

from AbletonMCP_Remote_Script import MAIN_THREAD_COMMANDS  # noqa: E402
from MCP_Server import server  # noqa: E402

_PLACEHOLDERS = {int: 1, float: 1.0, str: "x", bool: True}

# Arguments that get a tool past its input checks to the command it exists for.
_TOOL_ARGS = {
    "delete_arrangement_clip": {"clip_index": 1},
    "set_arrangement_clip_property": {"muted": True},
    "delete_track": {"track_index": 1},
}

# Enough session state for delete_track to pass its last-track guard.
_RESPONSE = {"track_count": 2}


def _mcp_tools():
    return {
        name: fn for name, fn in inspect.getmembers(server, inspect.isfunction)
        if fn.__module__ == server.__name__
        and list(inspect.signature(fn).parameters)[:1] == ["ctx"]
    }


def _call_args(name, tool):
    params = list(inspect.signature(tool).parameters.values())[1:]
    kwargs = {p.name: _PLACEHOLDERS.get(p.annotation, [])
              for p in params if p.default is inspect.Parameter.empty}
    kwargs.update(_TOOL_ARGS.get(name, {}))
    return kwargs


@pytest.fixture(scope="module")
def sent_by_tool():
    """Run every MCP tool against a recording connection."""
    tools = _mcp_tools()
    assert tools, "no MCP tools found; is @mcp.tool() a pass-through?"
    sent = {}
    try:
        for name, tool in sorted(tools.items()):
            server._invalidate_external_plugin_cache()
            conn = MagicMock()
            conn.send_command.return_value = dict(_RESPONSE)
            with patch.object(server, "get_ableton_connection", return_value=conn):
                tool(MagicMock(), **_call_args(name, tool))
            sent[name] = [c.args[0] for c in conn.send_command.call_args_list]
    finally:
        server._invalidate_external_plugin_cache()
    return sent


def _duplicates(values):
    return sorted({v for v in values if values.count(v) > 1})


def test_modifying_commands_match_main_thread_commands():
    mcp, remote = set(server.MODIFYING_COMMANDS), set(MAIN_THREAD_COMMANDS)
    assert mcp == remote, (
        "MCP MODIFYING_COMMANDS and Remote Script MAIN_THREAD_COMMANDS disagree. "
        "Only in MCP: {0}. Only in Remote Script: {1}".format(
            sorted(mcp - remote), sorted(remote - mcp)))


def test_command_lists_have_no_duplicates():
    assert not _duplicates(server.MODIFYING_COMMANDS)
    assert not _duplicates(MAIN_THREAD_COMMANDS)


def test_every_mcp_tool_sends_a_command(sent_by_tool):
    silent = sorted(name for name, commands in sent_by_tool.items() if not commands)
    assert not silent, (
        "These tools sent nothing, so their commands go unchecked; "
        "add arguments to _TOOL_ARGS: {0}".format(silent))


def test_every_write_command_the_mcp_sends_is_modifying(sent_by_tool):
    sent = set().union(*sent_by_tool.values())
    writes = {c for c in sent if not c.startswith("get_")}
    unclassified = sorted(writes - set(server.MODIFYING_COMMANDS))
    assert not unclassified, (
        "MCP tools send write commands missing from MODIFYING_COMMANDS "
        "and MAIN_THREAD_COMMANDS: {0}".format(unclassified))


def test_no_read_command_the_mcp_sends_is_modifying(sent_by_tool):
    sent = set().union(*sent_by_tool.values())
    reads = {c for c in sent if c.startswith("get_")}
    misclassified = sorted(reads & set(server.MODIFYING_COMMANDS))
    assert not misclassified, (
        "Read commands listed as modifying: {0}".format(misclassified))
