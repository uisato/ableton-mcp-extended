# Contributing Guide

Thank you for your interest in contributing to Ableton MCP Extended!

---

## How to Contribute

There are many ways to contribute to this project:

- 🐛 **Report bugs**
- 💡 **Suggest features**
- 📝 **Improve documentation**
- 🔧 **Fix issues**
- ✨ **Add new features**
- 🎵 **Share examples**

---

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone git@github.com:YOUR_USERNAME/ableton-mcp-extended.git
cd ableton-mcp-extended

# Add upstream remote
git remote add upstream git@github.com:MarvinHauke/ableton-mcp-extended.git
```

### 2. Set Up Development Environment

```bash
# Install in editable mode with all dependencies
pip install -e ".[docs,xy_controller]"

# Install the Remote Script
cp AbletonMCP_Remote_Script/__init__.py ~/path/to/Remote\ Scripts/AbletonMCP/
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

---

## Project Structure

```
ableton-mcp-extended/
├── MCP_Server/              # Main MCP server
│   ├── server.py           # FastMCP server with tools
│   └── __init__.py
├── AbletonMCP_Remote_Script/  # Standard TCP Remote Script
│   └── __init__.py
├── AbletonMCP_UDP/          # High-performance UDP Remote Script
│   └── __init__.py
├── elevenlabs_mcp/          # ElevenLabs integration
├── experimental_tools/      # Example tools
├── docs/                    # Documentation (MkDocs)
├── pyproject.toml          # Project configuration
└── mkdocs.yml              # Documentation configuration
```

---

## Development Workflow

### Making Changes

1. **Make your changes** in your feature branch
2. **Test thoroughly** with Ableton Live
3. **Update documentation** if needed
4. **Commit with clear messages**

### Testing

```bash
# Test the MCP server
python3 MCP_Server/server.py

# Test with your AI assistant
# Configure it to point to your local development version
```

### Documentation

If you're updating documentation:

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Serve docs locally
mkdocs serve

# Visit http://127.0.0.1:8000
```

---

## Code Style

### Python

- Follow [PEP 8](https://pep8.org/)
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small

**Example:**

```python
@mcp.tool()
def create_midi_track(ctx: Context, index: int = -1) -> str:
    """
    Create a new MIDI track in Ableton Live.

    Parameters:
    - index: Position to insert the track (-1 for end)

    Returns:
    - Success message with track index
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_midi_track", {"index": index})
        return f"Created MIDI track at index {result.get('index', index)}"
    except Exception as e:
        return f"Error creating MIDI track: {str(e)}"
```

### Documentation

- Use clear, concise language
- Include code examples
- Add warnings for experimental features
- Use proper Markdown formatting

---

## Adding New Features

### Adding a New MCP Tool

1. **Add the tool in `MCP_Server/server.py`:**

```python
@mcp.tool()
def your_new_tool(ctx: Context, param1: str, param2: int) -> str:
    """
    Description of what your tool does.

    Parameters:
    - param1: Description
    - param2: Description
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("your_command", {
            "param1": param1,
            "param2": param2
        })
        return f"Success: {result}"
    except Exception as e:
        return f"Error: {str(e)}"
```

2. **Implement in Remote Script (`AbletonMCP_UDP/__init__.py`):**

```python
def _your_command(self, param1, param2):
    """Implementation using Ableton Live API"""
    try:
        # Use self._song and Ableton API here
        result = {"success": True}
        return result
    except Exception as e:
        self.log_message(f"Error in _your_command: {e}")
        raise
```

3. **Add command handling** in `_process_command` method

4. **Update documentation** in `docs/api-reference.md`

5. **Test thoroughly**

---

## Commit Guidelines

### Commit Message Format

```
type(scope): brief description

Longer description if needed

Fixes #123
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples

```
feat(mcp): add scene management tools

Implements create_scene, delete_scene, and fire_scene tools.
Adds corresponding Remote Script methods.

Fixes #42
```

```
fix(server): improve connection retry logic

Increases retry timeout and adds exponential backoff.

Fixes #56
```

```
docs(api): add examples for device control

Adds code examples and clarifies parameter ranges.
```

---

## Pull Request Process

1. **Update documentation** for any new features
2. **Test your changes** thoroughly
3. **Create a pull request** with clear description
4. **Link related issues** (Fixes #123)
5. **Respond to review feedback**

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
How did you test these changes?

## Related Issues
Fixes #123

## Checklist
- [ ] Code follows project style
- [ ] Documentation updated
- [ ] Changes tested with Ableton Live
- [ ] Commit messages are clear
```

---

## Reporting Bugs

Use the [GitHub Issues](https://github.com/MarvinHauke/ableton-mcp-extended/issues) with the bug report template.

### Include:

- **Description** of the bug
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **System information**:
  - OS (macOS/Windows)
  - Python version
  - Ableton Live version
  - MCP client (Claude Desktop/Cursor)

---

## Feature Requests

Use [GitHub Discussions](https://github.com/MarvinHauke/ableton-mcp-extended/discussions) or [Issues](https://github.com/MarvinHauke/ableton-mcp-extended/issues) with the feature request template.

### Include:

- **Clear description** of the feature
- **Use case**: Why is this useful?
- **Proposed solution**: How might it work?
- **Alternatives**: Other approaches you've considered

---

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect differing viewpoints
- Accept responsibility for mistakes

---

## Questions?

- **GitHub Discussions**: [Ask questions](https://github.com/MarvinHauke/ableton-mcp-extended/discussions)
- **GitHub Issues**: [Report problems](https://github.com/MarvinHauke/ableton-mcp-extended/issues)

---

## Recognition

Contributors will be:

- Listed in project documentation
- Mentioned in release notes
- Credited for their contributions

Thank you for contributing to Ableton MCP Extended! 🎵
