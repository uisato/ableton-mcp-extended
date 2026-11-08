"""Static checks that the MCP server and the Remote Script agree on commands.

Adding a write command means editing three lists that nothing else ties
together: the Remote Script's main-thread "gate" list, the if/elif chain in
``main_thread_task``, and the MCP server's ``is_modifying_command`` list. A
gate entry with no chain branch silently returns ``{"status": "success",
"result": None}``, so drift looks like success. These tests parse both modules
(no imports, no Live) and fail on any disagreement.
"""

import ast
import os

import pytest

_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
_SERVER = os.path.join(_ROOT, "MCP_Server", "server.py")
_REMOTE = os.path.join(_ROOT, "AbletonMCP_Remote_Script", "__init__.py")


def _parse(path):
    with open(path, encoding="utf-8") as f:
        return ast.parse(f.read(), filename=path)


def _string_list(node):
    if not isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return None
    values = []
    for elt in node.elts:
        if not (isinstance(elt, ast.Constant) and isinstance(elt.value, str)):
            return None
        values.append(elt.value)
    return values


def _is_command_type(node):
    return isinstance(node, ast.Name) and node.id == "command_type"


def _compare_strings(test, op_type):
    """Return string(s) from `command_type == "x"` or `command_type in [...]`."""
    if not (isinstance(test, ast.Compare) and _is_command_type(test.left)
            and len(test.ops) == 1 and isinstance(test.ops[0], op_type)):
        return None
    comparator = test.comparators[0]
    if op_type is ast.Eq:
        if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
            return [comparator.value]
        return None
    return _string_list(comparator)


def _if_chain(if_node):
    """Yield each (test, body) along an if/elif chain."""
    while True:
        yield if_node.test, if_node.body
        if len(if_node.orelse) == 1 and isinstance(if_node.orelse[0], ast.If):
            if_node = if_node.orelse[0]
        else:
            return


def _find_function(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError("function {0} not found".format(name))


def _remote_script_commands():
    """Return (gate, chain, direct) command sets from _process_command."""
    process = _find_function(_parse(_REMOTE), "_process_command")
    dispatch = next(
        node for node in ast.walk(process)
        if isinstance(node, ast.If) and _compare_strings(node.test, ast.Eq)
    )

    gate, direct, gate_body = [], [], None
    for test, body in _if_chain(dispatch):
        in_list = _compare_strings(test, ast.In)
        if in_list is not None:
            assert gate_body is None, "expected exactly one main-thread gate list"
            gate, gate_body = in_list, body
            continue
        names = _compare_strings(test, ast.Eq)
        assert names, "unrecognised dispatch test at line {0}".format(test.lineno)
        direct.extend(names)
    assert gate_body is not None, "main-thread gate list not found"

    task = next(
        node for stmt in gate_body for node in ast.walk(stmt)
        if isinstance(node, ast.FunctionDef) and node.name == "main_thread_task"
    )
    chain_if = next(
        node for node in ast.walk(task)
        if isinstance(node, ast.If) and _compare_strings(node.test, ast.Eq)
    )
    chain = []
    for test, _body in _if_chain(chain_if):
        names = _compare_strings(test, ast.Eq)
        assert names, "unrecognised chain test at line {0}".format(test.lineno)
        chain.extend(names)
    return gate, chain, direct


def _mcp_sent_commands():
    sent = set()
    for node in ast.walk(_parse(_SERVER)):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "send_command" and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)):
            sent.add(node.args[0].value)
    return sent


def _mcp_modifying_commands():
    send = _find_function(_parse(_SERVER), "send_command")
    for node in ast.walk(send):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "is_modifying_command"):
            values = _compare_strings(node.value, ast.In)
            assert values is not None, "is_modifying_command is not a literal list"
            return values
    raise AssertionError("is_modifying_command not found in send_command")


@pytest.fixture(scope="module")
def remote():
    gate, chain, direct = _remote_script_commands()
    return {"gate": gate, "chain": chain, "direct": direct}


def _duplicates(values):
    return sorted({v for v in values if values.count(v) > 1})


def test_parser_finds_known_commands(remote):
    # Guard against the parser silently matching nothing.
    assert "set_arrangement_clip_property" in remote["gate"]
    assert "set_arrangement_clip_property" in remote["chain"]
    assert "get_session_info" in remote["direct"]
    assert "set_arrangement_clip_property" in _mcp_modifying_commands()
    assert "get_session_info" in _mcp_sent_commands()


def test_every_gate_command_has_a_chain_branch(remote):
    missing = sorted(set(remote["gate"]) - set(remote["chain"]))
    assert not missing, (
        "In the main-thread gate list but no main_thread_task branch "
        "(would return success with result None): {0}".format(missing))


def test_every_chain_branch_is_reachable_through_the_gate(remote):
    dead = sorted(set(remote["chain"]) - set(remote["gate"]))
    assert not dead, "main_thread_task branches the gate never routes to: {0}".format(dead)


def test_no_command_dispatched_both_directly_and_on_main_thread(remote):
    both = sorted(set(remote["gate"]) & set(remote["direct"]))
    assert not both, "Commands in both the direct and main-thread paths: {0}".format(both)


def test_no_duplicate_entries(remote):
    assert not _duplicates(remote["gate"]), "duplicate gate entries"
    assert not _duplicates(remote["chain"]), "duplicate chain branches"
    assert not _duplicates(remote["direct"]), "duplicate direct branches"
    assert not _duplicates(_mcp_modifying_commands()), "duplicate MCP modifying entries"


def test_mcp_modifying_list_matches_remote_gate(remote):
    mcp = set(_mcp_modifying_commands())
    gate = set(remote["gate"])
    assert mcp == gate, (
        "MCP is_modifying_command and Remote Script gate list disagree. "
        "Only in MCP: {0}. Only in Remote Script: {1}".format(
            sorted(mcp - gate), sorted(gate - mcp)))


def test_every_mcp_command_has_a_remote_handler(remote):
    handled = set(remote["chain"]) | set(remote["direct"])
    missing = sorted(_mcp_sent_commands() - handled)
    assert not missing, "MCP sends commands with no Remote Script handler: {0}".format(missing)
