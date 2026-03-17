# Browser Integration

Navigate and load content from Ableton's browser.

---

## Browser Categories

Ableton's browser is organized into categories:

- **instruments**: Virtual instruments
- **sounds**: Instrument presets and samples
- **drums**: Drum kits and percussion
- **audio_effects**: Audio processing effects
- **midi_effects**: MIDI processing effects

---

## Browsing Content

### get_browser_tree

Get a hierarchical view of browser categories.

**Parameters:**
- `category_type` (str, optional): Category to browse (default: "all")

**Examples:**
```
"Show me the browser tree for instruments"
"What's in the sounds category?"
"Get the browser tree for audio effects"
```

---

### get_browser_items_at_path

List items at a specific browser path.

**Parameters:**
- `path` (str): Browser path (e.g., "Sounds/Piano")

**Examples:**
```
"What items are in Sounds/Piano?"
"Show me what's in Instruments/Synth/Lead"
"List items at Drums/Acoustic"
```

---

## Loading Content

### By Path

```
"Load the instrument at Instruments/Synth/Lead on track 0"
"Load the sound from Sounds/Piano/Grand on track 1"
```

### By URI

```
"Load the browser item with URI 'query:Sounds#grand piano' on track 0"
```

---

## Common Workflows

### Finding and Loading an Instrument

```
1. "Show me the browser tree for instruments"
2. "What items are in Instruments/Synth?"
3. "Load Instruments/Synth/Lead on track 0"
```

### Loading a Drum Kit

```
1. "Get the browser tree for drums"
2. "What's in Drums/Electronic?"
3. "Load an 808 kit on track 1"
```

---

## Browser Paths

Browser paths use forward slashes and follow this structure:

```
Category/Subcategory/Item
```

**Examples:**
- `Instruments/Synth/Lead`
- `Sounds/Piano/Grand`
- `Drums/Electronic/808`
- `Audio Effects/Reverb/Plate`

---

## Tips

!!! tip "Explore First"
    Use `get_browser_tree` to see what's available before trying to load:
    ```
    "Show me the browser tree for sounds"
    ```

!!! info "Case Sensitive"
    Browser paths are case-sensitive. Make sure to use the exact capitalization.

!!! warning "Path Must Exist"
    If a path doesn't exist, you'll get an error. Use the browser tree to verify paths first.

---

## Importing Audio Files

You can also import audio files directly:

```
"Import the audio file from ~/Music/sample.wav to track 2"
```

---

## Related

- [Device Control](device-control.md) - Control loaded devices
- [Track Management](track-management.md) - Manage tracks
- [API Reference](../api-reference.md) - Complete API documentation
