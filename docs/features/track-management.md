# Track Management

Create, rename, and control tracks in your Ableton session.

---

## Creating Tracks

### create_midi_track

Create a new MIDI track at a specific position or at the end.

**Parameters:**
- `index` (int, optional): Position to insert track (-1 for end, default: -1)

**Examples:**
```
"Create a new MIDI track"
"Create a MIDI track at position 2"
"Add a MIDI track at the end"
```

---

## Track Information

### get_track_info

Get detailed information about a specific track.

**Parameters:**
- `track_index` (int): Index of the track (0-based)

**Returns:**
- Track index
- Track name
- List of devices on the track
- Device count

**Examples:**
```
"Get info about track 0"
"Tell me about track 2"
"What devices are on track 1?"
```

---

## Naming Tracks

### set_track_name

Rename a track for better organization.

**Parameters:**
- `track_index` (int): Index of the track
- `name` (str): New track name

**Examples:**
```
"Rename track 0 to 'Bass'"
"Set track 2 name to 'Lead Synth'"
"Name track 1 'Drums'"
```

---

## Common Workflows

### Setting Up a New Track

```
1. "Create a new MIDI track"
2. "Rename track X to 'Melody'"
3. "Load a synth on track X"
```

### Organizing Your Session

```
"Rename track 0 to 'Kick'"
"Rename track 1 to 'Snare'"
"Rename track 2 to 'Hi-Hat'"
```

---

## Track Indices

!!! warning "Zero-Indexed"
    Tracks are zero-indexed, meaning:

    - First track = 0
    - Second track = 1
    - Third track = 2
    - etc.

!!! tip "Finding Track Indices"
    Use `get_session_info` to see all tracks with their indices:
    ```
    "Get session info"
    ```

---

## Tips

!!! tip "Naming Convention"
    Use clear, descriptive names for tracks:

    - ✅ "Bass", "Lead Synth", "Kick Drum"
    - ❌ "Track 1", "untitled", "asdf"

!!! info "Track Limits"
    Ableton Live supports many tracks, but performance may vary based on:

    - Computer specifications
    - Number of devices per track
    - Sample rate and buffer size

---

## Related

- [MIDI Clips](midi-clips.md) - Create clips on tracks
- [Device Control](device-control.md) - Load and control devices
- [API Reference](../api-reference.md) - Complete API documentation
