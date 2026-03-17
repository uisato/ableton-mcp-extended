# Quick Start Guide

Get started with Ableton MCP Extended in 5 minutes!

!!! tip "Prerequisites"
    Make sure you've completed the [Installation Guide](installation.md) before proceeding.

---

## Your First Commands

Once installed, open your AI assistant (Claude Desktop or Cursor) and try these commands:

### 1. Check Your Session

```
"Get information about my current Ableton session"
```

This will show you:

- Current tempo
- Number of tracks
- Track names and types

### 2. Create a MIDI Track

```
"Create a new MIDI track and name it 'Bass'"
```

A new MIDI track appears in your Ableton session!

### 3. Add Some Notes

```
"Create a 4-bar MIDI clip on track 0, clip slot 0, and add these notes:
- C3 starting at beat 0, duration 0.5
- E3 starting at beat 1, duration 0.5
- G3 starting at beat 2, duration 0.5
- C4 starting at beat 3, duration 0.5"
```

---

## Example Workflows

### Creating a Simple Beat

```
"Create a MIDI track called 'Drums' and load a drum rack.
Then create an 8-bar clip and add a basic four-on-the-floor kick pattern."
```

### Setting Up a Track

```
"Create a MIDI track called 'Lead', load a synthesizer,
set the track volume to 0.8 and pan it slightly left"
```

### Browsing for Sounds

```
"Show me what's available in the Sounds browser category"
```

---

## Natural Language Tips

Ableton MCP Extended works best when you:

### ✅ Be Specific

```
Good: "Create a MIDI track at index 2 and name it 'Melody'"
Less Good: "Make a track"
```

### ✅ Use Musical Terms

```
Good: "Add a C major triad starting at beat 1"
Less Good: "Add some notes"
```

### ✅ Break Down Complex Tasks

```
Good:
1. "Create a MIDI track called 'Bass'"
2. "Load the 'Electric Bass' instrument"
3. "Create a 4-bar clip in slot 0"
4. "Add bass notes..."

Less Good: "Make a complete bass track with everything"
```

---

## Understanding Note Format

When adding notes to clips, use this format:

```python
{
    "pitch": 60,        # MIDI note number (60 = C3)
    "start_time": 0.0,  # Start position in beats
    "duration": 0.5,    # Length in beats
    "velocity": 100,    # Volume (0-127)
    "mute": false       # Optional: mute state
}
```

### MIDI Note Reference

| Note | Number | Note | Number |
|------|--------|------|--------|
| C3   | 60     | C4   | 72     |
| C#3  | 61     | C#4  | 73     |
| D3   | 62     | D4   | 74     |
| D#3  | 63     | D#4  | 75     |
| E3   | 64     | E4   | 76     |
| F3   | 65     | F4   | 77     |
| F#3  | 66     | F#4  | 78     |
| G3   | 67     | G4   | 79     |
| G#3  | 68     | G#4  | 80     |
| A3   | 69     | A4   | 81     |
| A#3  | 70     | A#4  | 82     |
| B3   | 71     | B4   | 83     |

---

## Common Tasks

### Transport Control

```
"Start playback"
"Stop playback"
"Set the tempo to 128 BPM"
```

### Device Control

```
"What devices are on track 0?"
"Get the parameters for device 0 on track 1"
"Set parameter 5 of device 0 on track 1 to 0.75"
```

### Track Management

```
"What tracks do I have?"
"Get detailed info about track 2"
"Set track 1 volume to 0.6"
"Pan track 0 to the right (value 0.7)"
```

---

## Next Steps

Now that you're familiar with the basics:

1. **Explore Features**: Check out the [Features Overview](features/overview.md)
2. **Advanced Usage**: Learn about [ElevenLabs Integration](advanced/elevenlabs.md)
3. **API Reference**: See all available tools in the [API Reference](api-reference.md)

---

## Tips & Tricks

!!! tip "Experiment!"
    The AI assistant can understand context - try having a conversation about what you want to create, and it will figure out the right sequence of commands.

!!! warning "Track Indices"
    Tracks and clips are zero-indexed (first track = 0, second track = 1, etc.)

!!! info "Parameter Values"
    Device parameters are normalized to 0.0-1.0 range, where 0.0 is minimum and 1.0 is maximum.

---

## Need Help?

- Check the [Troubleshooting section](installation.md#troubleshooting) in the installation guide
- Visit [GitHub Discussions](https://github.com/MarvinHauke/ableton-mcp-extended/discussions)
- Open an [Issue](https://github.com/MarvinHauke/ableton-mcp-extended/issues) if you find a bug
