# Ableton MCP (Model Context Protocol)

A Python-based integration between Ableton Live and LLM assistants using the Model Context Protocol.

## Features

- Control Ableton Live directly through AI assistants
- Create and manipulate MIDI clips, tracks, and audio
- Load instruments, effects, and drum kits
- Automate parameters and create dynamic music
- Integrate with ElevenLabs for text-to-speech and voice synthesis
- Mouse XY parameter control for expressive performance
- High-performance hybrid TCP/UDP server for low-latency parameter control

## Components

### Core MCP Server
The standard MCP server that handles most interactions with Ableton Live through the MCP protocol.

### ElevenLabs Integration
Provides voice synthesis and audio generation capabilities that can be imported directly into Ableton Live.

### Hybrid TCP/UDP Server
A high-performance alternative server implementation that uses UDP for parameter updates, providing lower latency for real-time control.

### Experimental Tools
- **XY Mouse Controller**: Control any two Ableton parameters simultaneously using your mouse position for expressive performance control.

## Requirements

- Python 3.10 or higher
- Ableton Live 11 or higher
- ElevenLabs API key (for voice-related features)
- Additional requirements for specific components (see component READMEs)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/uisato/ableton-mcp.git
   cd ableton-mcp
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Set up environment variables:
   
   Create a `.env` file in the root directory with the following variables:
   ```
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ELEVENLABS_OUTPUT_DIR=/path/to/your/ableton/user/library/eleven_labs_audio
   ```

## Usage

### Standard MCP Server
1. Start the Ableton MCP server:
   ```bash
   python -m MCP_Server.server
   ```

2. In your AI assistant (like Cursor with Claude), you can now interact with Ableton using the provided tools.

### XY Mouse Controller
For expressive parameter control using your mouse:
```bash
cd experimental_tools/xy_mouse_controller
pip install -r requirements.txt
python mouse_parameter_controller_udp.py
```

### Hybrid TCP/UDP Server
For the alternative high-performance server, install the AbletonMCP_UDP remote script into your Ableton Live Remote Scripts folder.

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built upon the Model Context Protocol framework to enable AI control of Ableton Live. 