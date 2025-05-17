# Installation Guide

This document provides detailed installation instructions for all components of the Ableton MCP project.

## Core MCP Server

1. Install Python 3.10 or higher
2. Clone the repository:
   ```bash
   git clone https://github.com/uisato/ableton-mcp.git
   cd ableton-mcp
   ```
3. Install the package:
   ```bash
   pip install -e .
   ```
4. Set up your environment variables by creating a `.env` file in the project root:
   ```
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ELEVENLABS_OUTPUT_DIR=/path/to/your/ableton/user/library/eleven_labs_audio
   ```
5. Start the server:
   ```bash
   python -m MCP_Server.server
   ```

## ElevenLabs Integration

1. Sign up for an ElevenLabs account at [https://elevenlabs.io](https://elevenlabs.io)
2. Obtain your API key from your account settings
3. Add the API key to your `.env` file:
   ```
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ```
4. Create a directory in your Ableton User Library for ElevenLabs audio files:
   ```
   ELEVENLABS_OUTPUT_DIR=/path/to/your/ableton/user/library/eleven_labs_audio
   ```

## XY Mouse Controller

The XY Mouse Controller allows you to control two Ableton parameters simultaneously using your mouse position.

1. Install the additional requirements:
   ```bash
   cd experimental_tools/xy_mouse_controller
   pip install -r requirements.txt
   ```
2. Before running, make sure the Ableton Live MCP Server or Hybrid TCP/UDP Server is running
3. Run the mouse controller:
   ```bash
   python mouse_parameter_controller_udp.py
   ```
4. Follow the on-screen prompts to select which parameters you want to control

### XY Mouse Controller - Troubleshooting

- **Screen Resolution Detection**: If you have issues with screen resolution detection, install the `screeninfo` package: `pip install screeninfo`
- **Mouse Control**: Make sure you have the appropriate permissions for mouse tracking on your OS

## Hybrid TCP/UDP Server (AbletonMCP_UDP)

The Hybrid server uses both TCP and UDP protocols. TCP is used for reliable commands, while UDP is used for high-frequency parameter updates.

### Installing as a Remote Script

1. Locate your Ableton Live User Remote Scripts folder:
   - Windows: `C:\Users\[username]\Documents\Ableton\User Library\Remote Scripts`
   - macOS: `/Users/[username]/Music/Ableton/User Library/Remote Scripts`

2. Create a new folder named `AbletonMCP_UDP` in this directory

3. Copy the `__init__.py` file from `ableton-mcp_hybrid-server/AbletonMCP_UDP/` to this new folder

4. Restart Ableton Live

5. In Ableton Live, go to Preferences > Link/MIDI and select "AbletonMCP_UDP" from the Control Surface dropdown

### Using with XY Mouse Controller

The XY Mouse Controller is already configured to work with the Hybrid TCP/UDP Server. When running the XY Mouse Controller, it will automatically detect and use the UDP protocol if available.

## Troubleshooting

### Port Conflicts

Both servers use specific ports:
- Core MCP Server: Port 3030 for HTTP
- Hybrid TCP/UDP Server: Port 9877 for TCP and 9878 for UDP

If you encounter port conflicts, make sure no other application is using these ports.

### API Key Issues

If you encounter issues with the ElevenLabs integration:
1. Verify your API key is correct
2. Check your ElevenLabs subscription status
3. Ensure your `.env` file is in the correct location

### Python Dependencies

If you encounter import errors:
1. Make sure you've installed the package with `pip install -e .`
2. For specific components, install their requirements separately
3. Check that you're using Python 3.10 or higher 