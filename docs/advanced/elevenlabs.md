# ElevenLabs Voice Integration

Generate AI voices and import them directly into your Ableton session.

---

## Overview

The ElevenLabs integration allows you to:

- Generate text-to-speech audio
- Create custom voices
- Clone existing voices
- Generate sound effects
- Import generated audio directly into Ableton

---

## Setup

### 1. Get an API Key

1. Sign up at [elevenlabs.io](https://elevenlabs.io)
2. Navigate to your account settings
3. Generate an API key

### 2. Configure Your AI Assistant

Add the ElevenLabs server to your MCP configuration:

```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "python3",
      "args": ["/path/to/MCP_Server/server.py"]
    },
    "ElevenLabs": {
      "command": "python3",
      "args": ["/path/to/elevenlabs_mcp/server.py"],
      "env": {
        "ELEVENLABS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

---

## Usage

### Generate Voice

```
"Generate a voice saying 'Hello from ElevenLabs' and import it into Ableton"
```

### Create Narration

```
"Create a narration with this text: 'Welcome to the future of music production'
and import it into track 2"
```

### Generate Sound Effects

```
"Generate a whoosh sound effect and add it to my session"
```

---

## Workflow Example

### Creating a Spoken Word Track

```
1. "Create an audio track called 'Narration'"
2. "Generate a voice saying: 'In the beginning, there was sound.
    And the sound was good.' Import it to the Narration track"
3. "Add a reverb effect to the Narration track"
4. "Set the reverb mix to 0.3"
```

---

## Voice Options

ElevenLabs offers various voices with different characteristics:

- **Default voices**: Pre-made, high-quality voices
- **Custom voices**: Train your own voice model
- **Voice cloning**: Clone any voice from a sample

Check the ElevenLabs documentation for available voices and settings.

---

## Tips

!!! tip "Audio Quality"
    ElevenLabs generates high-quality audio suitable for:
    - Podcasts
    - Voiceovers
    - Spoken word pieces
    - Character voices
    - Narration

!!! info "Credits"
    ElevenLabs uses a credit system. Check your account for available credits.

!!! warning "Processing Time"
    Voice generation may take a few seconds depending on:
    - Text length
    - Voice model complexity
    - Current API load

---

## Creative Applications

### Music Production

- Add spoken word elements to tracks
- Create intro/outro narrations
- Generate character dialogue
- Add vocal samples

### Sound Design

- Generate custom sound effects
- Create ambient vocal textures
- Design unique audio elements

---

## Related

- [Track Management](../features/track-management.md) - Create audio tracks
- [Browser Integration](../features/browser.md) - Load audio files
- [Installation Guide](../installation.md#elevenlabs-voice-integration) - Setup details
