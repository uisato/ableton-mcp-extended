# Device and Parameter Control

Load instruments and effects, and control their parameters.

---

## Loading Devices

### load_instrument_or_effect

Load instruments or effects from Ableton's browser onto tracks.

**Parameters:**
- `track_index` (int): Index of the track
- `uri` (str): Browser URI or path to the device

**Examples:**
```
"Load a synthesizer on track 0"
"Load the instrument at path 'Instruments/Synth/Lead' on track 1"
```

---

### load_drum_kit

Load a drum kit onto a track.

**Parameters:**
- `track_index` (int): Index of the track
- `kit_uri` (str): URI or path to the drum kit

**Examples:**
```
"Load an 808 drum kit on track 0"
"Load drums on track 1"
```

---

## Parameter Control

### Normalized Values

All device parameters use normalized values in the range 0.0-1.0:

| Value | Meaning |
|-------|---------|
| 0.0   | Minimum (fully left/down) |
| 0.5   | Middle position |
| 1.0   | Maximum (fully right/up) |

The server automatically converts these to the device's actual parameter range.

**Examples:**
```
"Set filter cutoff to 0.7"
"Set reverb mix to 0.3"
"Set delay time to 0.5"
```

---

## Getting Device Information

**Examples:**
```
"What devices are on track 0?"
"Get the parameters for device 0 on track 1"
"Show me all parameters for the first device on track 2"
```

---

## Common Workflows

### Setting Up a Synth

```
1. "Create a MIDI track"
2. "Load a synthesizer on track 0"
3. "Get parameters for device 0 on track 0"
4. "Set parameter 5 (filter cutoff) to 0.8"
```

### Adding Effects

```
1. "Load a reverb effect on track 1"
2. "Set the reverb mix to 0.4"
```

---

## Tips

!!! tip "Finding Parameters"
    Use "Get parameters" first to see what's available:
    ```
    "What parameters does device 0 on track 1 have?"
    ```
    This shows you the parameter indices and names.

!!! info "Parameter Indices"
    Parameters are zero-indexed:
    - First parameter = 0
    - Second parameter = 1
    - etc.

!!! warning "Device Must Be Loaded"
    Make sure to load a device before trying to control its parameters!

---

## Related

- [Browser Integration](browser.md) - Browse for devices
- [Track Management](track-management.md) - Manage tracks
- [API Reference](../api-reference.md) - Complete API documentation
