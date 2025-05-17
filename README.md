# Ableton MCP Extended

A Python-based integration between Ableton Live and LLM assistants using the Model Context Protocol, with ElevenLabs integration and extended features.

## Features

- Control Ableton Live directly through AI assistants (Claude and Cursor)
- Create and manipulate MIDI clips, tracks, and audio
- Load instruments, effects, and drum kits
- Parameter automation (still experimental)
- High-performance hybrid TCP/UDP server for low-latency parameter control
- Integrate with other MCP servers, like for example ElevenLabs for text-to-speech, voice synthesis, and SFX generation
- Mouse XY parameter control for expressive performance (As an example of powerful tool creation through Ableton MCP)


## Components

### Core MCP Server
The standard MCP server that handles most interactions with Ableton Live through the MCP protocol. Integrates with Claude Desktop and Cursor. It consists in:
  - **Ableton Remote Script** (Ableton_Remote_Script/__init__.py): A MIDI Remote Script for Ableton Live that creates a socket server to receive and execute commands.
  - **MCP Server** (server.py): A Python server that implements the Model Context Protocol and connects to the Ableton Remote Script.

### ElevenLabs Integration
Provides voice synthesis and audio generation capabilities that can be imported directly into Ableton Live. (elevenlabs_mcp/server.py)

### Hybrid TCP/UDP Server
A high-performance alternative server implementation that uses UDP for parameter updates, providing lower latency for real-time control. (Ableton-MCP_hybrid-server/AbletonMCP_UDP/init.py)

### Experimental Tools
- **XY Mouse Controller**: Control any two Ableton parameters simultaneously using your mouse position for expressive performance control. Showing Ableton MCP capabilities for creating new experimental tools for interacting with Ableton Live.

## Requirements

- Python 3.10 or higher
- Ableton Live 11 or higher
- ElevenLabs API key (for voice-related features)
- Additional requirements for specific components (see component READMEs)

## Installation

For complete installation instructions, see [INSTALLATION.md](INSTALLATION.md).

## Usage

### AI Assistant Integration

#### Claude Desktop
Configure Claude Desktop to use the MCP server by editing your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "python",
      "args": [
        "C:/path/to/ableton-mcp-extended/MCP_Server/server.py"
      ]
    }
  }
}
```

Replace `C:/path/to/ableton-mcp-extended/MCP_Server/server.py` with the actual path on your system.
See [INSTALLATION.md](INSTALLATION.md) for detailed instructions.

#### Cursor
Configure Cursor's MCP settings to use the Ableton MCP server with local installation:

```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "python",
      "args": [
        "C:/path/to/ableton-mcp-extended/MCP_Server/server.py"
      ]
    }
  }
}
```

Replace `C:/path/to/ableton-mcp-extended/MCP_Server/server.py` with the actual path on your system.
See [INSTALLATION.md](INSTALLATION.md) for details.

### Hybrid TCP/UDP Server
For the alternative high-performance server, install the AbletonMCP_UDP remote script into your Ableton Live Remote Scripts folder. Both remote scripts can co-exist:

![image](https://github.com/user-attachments/assets/24997e12-8a80-433f-9070-ac72be684a87)

### XY Mouse Controller
For expressive parameter control using your mouse:
```bash
cd experimental_tools/xy_mouse_controller
pip install -r requirements.txt
python mouse_parameter_controller_udp.py
```

## ElevenLabs Integration

The ElevenLabs integration allows for:
- Text-to-speech generation
- Speech-to-text transcription
- Custom voice creation
- Sound effect generation
- Agent creation for conversational AI

To use these features, you'll need an ElevenLabs API key. You can get one by signing up at [https://elevenlabs.io](https://elevenlabs.io).

## Example Workflows

- Creating a drum pattern with randomized timing
- Generating text-to-speech and importing into Ableton
- Building dynamic arrangements with follow actions
- Creating parameter automation from AI instructions
- Using the mouse to expressively control effects parameters
- High-performance real-time control using the UDP server
- Asking Claude to create a complete track from a simple description

## Difference from Original ableton-mcp

This extended version builds upon the original [ahujasid/ableton-mcp](https://github.com/ahujasid/ableton-mcp) repository by adding:

- More integrated tools
- ElevenLabs integration for voice synthesis and audio generation
- Hybrid TCP/UDP server for high-performance parameter updates
- XY Mouse Controller for expressive parameter control
- Comprehensive documentation and installation options

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built upon the Model Context Protocol framework to enable AI control of Ableton Live.

## Inspiration

This project was inspired by the original [ahujasid/ableton-mcp](https://github.com/ahujasid/ableton-mcp) repository, with extended functionality for ElevenLabs integration and additional control methods. 
