# Features Overview

Ableton MCP Extended provides comprehensive control over Ableton Live through natural language.

---

## Session and Transport Control

Control playback and get session information.

### Available Actions

- **Start/Stop Playback**: Control the transport
- **Get Session Info**: View tempo, time signature, track count
- **Set Tempo**: Change the project tempo

### Example Commands

```
"Start playback"
"Stop playback"
"Set the tempo to 140 BPM"
"What's my current session info?"
```

[Learn more →](session-control.md)

---

## Track Management

Create and control tracks in your session.

### Available Actions

- **Create Tracks**: MIDI and audio tracks
- **Rename Tracks**: Set custom track names
- **Get Track Info**: View devices, parameters, clips
- **Control Properties**: Volume, panning, mute, solo, arm
- **Track Grouping**: Manage track groups and folding

### Example Commands

```
"Create a new MIDI track"
"Rename track 0 to 'Lead Synth'"
"Set track 1 volume to 0.8"
"Get detailed information about track 2"
```

[Learn more →](track-management.md)

---

## MIDI Clips and Notes

Create and manipulate MIDI clips with precision.

### Available Actions

- **Create Clips**: Specify length and position
- **Add Notes**: Single or batch note addition
- **Delete Notes**: Remove notes by time/pitch range
- **Transpose**: Shift notes up or down
- **Quantize**: Align notes to grid
- **Batch Edit**: Modify multiple notes at once
- **Loop Parameters**: Set loop start, end, and enable state
- **Follow Actions**: Configure clip follow behavior

### Example Commands

```
"Create a 4-bar MIDI clip on track 0, slot 0"
"Add a C major chord at beat 0"
"Transpose all notes in the clip up by 5 semitones"
"Quantize notes to 16th notes with 80% strength"
```

[Learn more →](midi-clips.md)

---

## Device and Parameter Control

Load and control instruments and effects.

### Available Actions

- **Load Devices**: Instruments and effects from browser
- **Get Parameters**: List all available parameters
- **Set Parameters**: Control individual parameters
- **Batch Set**: Update multiple parameters at once

!!! info "Parameter Values"
    All parameter values are normalized to 0.0-1.0 range:

    - `0.0` = Minimum value
    - `0.5` = Middle value
    - `1.0` = Maximum value

### Example Commands

```
"Load a synthesizer on track 0"
"What parameters does device 0 on track 1 have?"
"Set the filter cutoff (parameter 5) to 0.7"
"Batch update parameters 0, 1, 2 to values 0.5, 0.8, 0.3"
```

[Learn more →](device-control.md)

---

## Browser Integration

Navigate and load content from Ableton's browser.

### Available Actions

- **Get Browser Tree**: View available categories
- **List Items**: Browse specific paths
- **Load Items**: Load instruments, effects, samples
- **Import Audio**: Import audio files to tracks

### Browser Categories

- `instruments` - Virtual instruments
- `sounds` - Instrument presets and samples
- `drums` - Drum kits and percussion
- `audio_effects` - Audio processing effects
- `midi_effects` - MIDI processing effects

### Example Commands

```
"Show me the browser tree for instruments"
"What items are in the 'Sounds/Piano' path?"
"Load the browser item at path 'Instruments/Synth/Lead'"
"Import the audio file from ~/Music/sample.wav to track 2"
```

[Learn more →](browser.md)

---

## Automation (Experimental)

!!! warning "Experimental Feature"
    Clip automation is currently experimental and may not work perfectly.

### Available Actions

- **Add Envelope Points**: Add automation points to clip envelopes
- **Clear Envelopes**: Remove all automation from a parameter
- **Get Envelope Info**: View existing automation

### Example Commands

```
"Add an automation point at beat 2, value 0.5 for parameter 3"
"Clear the automation envelope for parameter 0"
```

---

## Feature Status

| Feature | Status | Notes |
|---------|--------|-------|
| Session Control | ✅ Stable | Fully implemented |
| Track Management | ✅ Stable | Fully implemented |
| MIDI Clips & Notes | ✅ Stable | Fully implemented |
| Device Control | ✅ Stable | Fully implemented |
| Browser Integration | ✅ Stable | Fully implemented |
| Clip Automation | ⚠️ Experimental | May have issues |
| Scene Management | ❌ Not Implemented | Planned for future |
| Arrangement View | ❌ Not Implemented | Planned for future |
| VST Plugin Control | ⚠️ Limited | Via generic parameters |

---

## Advanced Features

### ElevenLabs Voice Integration

Generate AI voices and import them directly into your session.

[Learn more →](../advanced/elevenlabs.md)

### High-Performance UDP Server

Ultra-low latency parameter control for real-time performance.

[Learn more →](../advanced/udp-server.md)

### Custom Tools

Build your own Ableton controllers using the MCP framework.

[Learn more →](../advanced/custom-tools.md)

---

## Next Steps

- **Try it out**: Use the [Quick Start Guide](../quickstart.md)
- **Dive deeper**: Check the [API Reference](../api-reference.md)
- **Get creative**: Explore [Advanced Features](../advanced/elevenlabs.md)
