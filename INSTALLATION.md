# Installation Guide

This document provides detailed installation instructions for all components of the Ableton MCP project.

## Prerequisites

- Ableton Live 10 or newer
- Python 3.10 or higher
- uv package manager (strongly recommended for AI assistant integration)

### Installing uv Package Manager

The uv package manager is required for proper integration with Claude Desktop and Cursor:

- **macOS:** Install via Homebrew:
  ```bash
  brew install uv
  ```
- **Windows/Linux:** Install from [uv's official website](https://docs.astral.sh/uv/getting-started/installation/)

⚠️ **Important:** Do not proceed with Claude/Cursor integration before installing UV.

## AI Assistant Integration

### Claude Desktop Integration

1. Open Claude Desktop application
2. Go to Claude > Settings > Developer > Edit Config
3. Edit the `claude_desktop_config.json` file to include:
   ```json
   {
     "mcpServers": {
       "AbletonMCP": {
         "command": "uvx",
         "args": [
           "ableton-mcp"
         ]
       }
     }
   }
   ```
4. Save the config file and restart Claude Desktop
5. When properly configured, you'll see a hammer icon with Ableton MCP tools in Claude

### Cursor Integration

1. Open Cursor
2. Go to Settings > MCP
3. Add a new MCP server with:
   - Name: AbletonMCP
   - Command: `uvx ableton-mcp`
4. Save the settings

⚠️ **Important:** Only run one instance of the MCP server (either on Cursor or Claude Desktop), not both simultaneously.

## Core MCP Server

1. Clone the repository:
   ```bash
   git clone https://github.com/uisato/ableton-mcp.git
   cd ableton-mcp
   ```
2. Install the package:
   ```bash
   pip install -e .
   ```
3. Set up your environment variables by creating a `.env` file in the project root:
   ```
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ELEVENLABS_OUTPUT_DIR=/path/to/your/ableton/user/library/eleven_labs_audio
   ```
4. Start the server manually (only if not using Claude Desktop or Cursor):
   ```bash
   python -m MCP_Server.server
   ```

## Ableton Remote Script Installation

Follow these steps to install the Ableton Remote Script:

1. Locate your Ableton Live Remote Scripts directory:

   **For macOS:**
   - Method 1: Go to Applications > Right-click on Ableton Live > Show Package Contents > Navigate to:
     `Contents/App-Resources/MIDI Remote Scripts/`
   - Method 2: If not found, try:
     `/Users/[Username]/Library/Preferences/Ableton/Live XX/User Remote Scripts`

   **For Windows:**
   - Method 1: `C:\Users\[Username]\AppData\Roaming\Ableton\Live x.x.x\Preferences\User Remote Scripts`
   - Method 2: `C:\ProgramData\Ableton\Live XX\Resources\MIDI Remote Scripts\`
   - Method 3: `C:\Program Files\Ableton\Live XX\Resources\MIDI Remote Scripts\`

   *Note: Replace XX with your Ableton version number (e.g., 10, 11, 12)*

2. Create a folder called `AbletonMCP` in the Remote Scripts directory
3. Copy the `__init__.py` file from `AbletonMCP_Remote_Script/` to this new folder
4. Launch Ableton Live
5. Go to Settings/Preferences → Link, Tempo & MIDI
6. In the Control Surface dropdown, select "AbletonMCP"
7. Set Input and Output to "None"

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

1. Locate your Ableton Live User Remote Scripts folder (see instructions above)
2. Create a new folder named `AbletonMCP_UDP` in this directory
3. Copy the `__init__.py` file from `ableton-mcp_hybrid-server/AbletonMCP_UDP/` to this new folder
4. Restart Ableton Live
5. In Ableton Live, go to Preferences > Link/MIDI and select "AbletonMCP_UDP" from the Control Surface dropdown

### Using with XY Mouse Controller

The XY Mouse Controller is already configured to work with the Hybrid TCP/UDP Server. When running the XY Mouse Controller, it will automatically detect and use the UDP protocol if available.

## Using the AI Assistant Integration

Once everything is properly set up:

1. Make sure Ableton Live is running with the Remote Script enabled
2. Open either Claude Desktop or Cursor (not both)
3. In Claude Desktop, you'll see a hammer icon with available Ableton tools
4. In Cursor, you can directly ask Claude to control Ableton

Example commands you can try:
- "Create a new MIDI track with a synth bass"
- "Add a 4-bar drumbeat to track 1"
- "Get information about my current Ableton session"
- "Generate a voice sample saying 'welcome to my track' and import it into Ableton"

## Troubleshooting

### AI Assistant Integration Issues

- **Tools not showing up**: Verify your claude_desktop_config.json or Cursor MCP settings
- **Command not found errors**: Make sure you've installed uv/uvx properly
- **Multiple instances**: Ensure you're only running one instance of the MCP server
- **Timeout issues**: Try simplifying your requests or breaking them into smaller steps

### Port Conflicts

Different servers use specific ports:
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

### Common Issues

- **Connection dropped**: Try restarting both the AI assistant and Ableton Live
- **Remote script not responding**: Verify it's properly installed and selected in Ableton's preferences
- **ElevenLabs errors**: Check your API key and quota limits
- **"Have you tried turning it off and on again?"**: This classic IT solution often works! Restart all components 