# API Reference

Complete reference for all available MCP tools in Ableton MCP Extended.

---

## Session & Transport

### get_session_info

Get detailed information about the current Ableton session.

**Returns:**

- `tempo`: Current tempo (BPM)
- `track_count`: Number of tracks
- `tracks`: Array of track objects with index, name, device_count

**Example:**

```
"Get information about my current Ableton session"
```

---

### start_playback

Start Ableton Live playback.

**Example:**

```
"Start playback"
```

---

### stop_playback

Stop Ableton Live playback.

**Example:**

```
"Stop playback"
```

---

### set_tempo

Set the session tempo.

**Parameters:**

- `tempo` (float): New tempo in BPM (typically 60-200)

**Example:**

```
"Set the tempo to 128 BPM"
```

---

## Track Management

### create_midi_track

Create a new MIDI track.

**Parameters:**

- `index` (int, optional): Position to insert track (-1 for end, default: -1)

**Example:**

```
"Create a new MIDI track"
"Create a MIDI track at position 2"
```

---

### get_track_info

Get detailed information about a specific track.

**Parameters:**

- `track_index` (int): Index of the track (0-based)

**Returns:**

- `index`: Track index
- `name`: Track name
- `devices`: Array of device objects
- `device_count`: Number of devices

**Example:**

```
"Get information about track 0"
```

---

### set_track_name

Set the name of a track.

**Parameters:**

- `track_index` (int): Index of the track
- `name` (str): New track name

**Example:**

```
"Rename track 0 to 'Bass'"
```

---

## MIDI Clips & Notes

### create_clip

Create a new MIDI clip in a track's clip slot.

**Parameters:**

- `track_index` (int): Index of the track
- `clip_index` (int): Clip slot index
- `length` (float, optional): Length in beats (default: 4.0)

**Example:**

```
"Create a 4-bar MIDI clip on track 0, slot 0"
```

---

### set_clip_name

Set the name of a clip.

**Parameters:**

- `track_index` (int): Index of the track
- `clip_index` (int): Clip slot index
- `name` (str): New clip name

**Example:**

```
"Name the clip in track 0, slot 0 as 'Bassline'"
```

---

### add_notes_to_clip

Add MIDI notes to a clip.

**Parameters:**

- `track_index` (int): Index of the track
- `clip_index` (int): Clip slot index
- `notes` (array): Array of note objects

**Note Object Format:**

```json
{
  "pitch": 60,         // MIDI note number (0-127)
  "start_time": 0.0,   // Start position in beats
  "duration": 0.5,     // Length in beats
  "velocity": 100,     // Velocity (0-127)
  "mute": false        // Mute state (optional)
}
```

**Example:**

```
"Add notes to clip: C3 at beat 0, E3 at beat 1, G3 at beat 2"
```

---

## Device Control

### load_instrument_or_effect

Load an instrument or effect onto a track from the browser.

**Parameters:**

- `track_index` (int): Index of the track
- `uri` (str): Browser URI or path to the device

**Example:**

```
"Load the instrument at path 'Instruments/Synth/Lead' on track 0"
```

---

### get_browser_tree

Get a hierarchical tree of browser categories.

**Parameters:**

- `category_type` (str, optional): Type of categories (default: "all")
  - `"all"`: All categories
  - `"instruments"`: Virtual instruments
  - `"sounds"`: Presets and samples
  - `"drums"`: Drum kits
  - `"audio_effects"`: Audio effects
  - `"midi_effects"`: MIDI effects

**Example:**

```
"Show me the browser tree for instruments"
```

---

### get_browser_items_at_path

Get items at a specific browser path.

**Parameters:**

- `path` (str): Browser path (e.g., "Sounds/Piano")

**Example:**

```
"What items are in the Sounds/Piano folder?"
```

---

### load_drum_kit

Load a drum kit onto a track.

**Parameters:**

- `track_index` (int): Index of the track
- `kit_uri` (str): URI or path to the drum kit

**Example:**

```
"Load the 808 drum kit on track 1"
```

---

## Parameter Values

All device parameter values are normalized to the 0.0-1.0 range:

| Value | Meaning |
|-------|---------|
| 0.0   | Minimum (fully counter-clockwise) |
| 0.5   | Middle position |
| 1.0   | Maximum (fully clockwise) |

!!! tip "Converting Values"
    The server automatically converts normalized values to the device's actual range.
    You don't need to know the min/max values - just use 0.0 to 1.0!

---

## MIDI Note Numbers

Quick reference for MIDI note numbers:

| Octave | C   | C#  | D   | D#  | E   | F   | F#  | G   | G#  | A   | A#  | B   |
|--------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0      | 12  | 13  | 14  | 15  | 16  | 17  | 18  | 19  | 20  | 21  | 22  | 23  |
| 1      | 24  | 25  | 26  | 27  | 28  | 29  | 30  | 31  | 32  | 33  | 34  | 35  |
| 2      | 36  | 37  | 38  | 39  | 40  | 41  | 42  | 43  | 44  | 45  | 46  | 47  |
| 3      | 48  | 49  | 50  | 51  | 52  | 53  | 54  | 55  | 56  | 57  | 58  | 59  |
| 4      | 60  | 61  | 62  | 63  | 64  | 65  | 66  | 67  | 68  | 69  | 70  | 71  |
| 5      | 72  | 73  | 74  | 75  | 76  | 77  | 78  | 79  | 80  | 81  | 82  | 83  |

**Common reference points:**

- Middle C = C4 = 60
- A440 = A4 = 69
- Typical bass range: E1 (28) to E3 (52)
- Typical melody range: C4 (60) to C6 (84)

---

## Error Handling

All tools return error messages in a readable format when something goes wrong:

```
"Error creating track: Track index out of range"
"Error loading device: Browser path not found"
```

Common errors:

- **Index out of range**: Track/clip/device index doesn't exist
- **Connection refused**: Ableton Live not running or Remote Script not loaded
- **Invalid parameter**: Value outside allowed range or wrong type
- **Browser path not found**: Invalid browser URI or path

---

## Type Reference

### Track Index
- Type: `int`
- Range: `0` to `track_count - 1`
- Zero-indexed (first track = 0)

### Clip Index
- Type: `int`
- Range: `0` to available clip slots
- Zero-indexed (first clip slot = 0)

### Device Index
- Type: `int`
- Range: `0` to device_count - 1
- Zero-indexed (first device = 0)

### Parameter Index
- Type: `int`
- Range: `0` to parameter_count - 1
- Zero-indexed (first parameter = 0)

### Normalized Value
- Type: `float`
- Range: `0.0` to `1.0`
- Used for all parameter values

### Time (Beats)
- Type: `float`
- Range: `0.0` to clip length
- Measured in beats (quarter notes)

### MIDI Note
- Type: `int`
- Range: `0` to `127`
- Middle C (C4) = 60

### Velocity
- Type: `int`
- Range: `0` to `127`
- Typical: 64-127 (medium to loud)

---

## Advanced: UDP Server Tools

The UDP server provides high-performance, real-time parameter control.

!!! info "UDP Server Required"
    These tools require the AbletonMCP_UDP Remote Script to be installed and enabled.

### Features

- Ultra-low latency (~1-5ms)
- Batch parameter updates
- Real-time performance control
- No response required (fire-and-forget)

See [UDP High Performance](advanced/udp-server.md) for details.

---

## Next Steps

- Try the [Quick Start Guide](quickstart.md)
- Explore [Features Overview](features/overview.md)
- Check out [Advanced Features](advanced/elevenlabs.md)
