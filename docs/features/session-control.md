# Session and Transport Control

Control Ableton Live's playback and session settings.

---

## Overview

Session control provides the foundation for working with Ableton Live through the MCP server.

---

## Available Tools

### get_session_info

Get comprehensive information about your current Ableton session.

**Returns:**
- Current tempo (BPM)
- Total number of tracks
- Track list with indices, names, and device counts

**Example:**
```
"What's my current session info?"
"Tell me about my Ableton session"
```

---

### start_playback

Start playing the current Ableton session.

**Example:**
```
"Start playback"
"Play"
"Start playing"
```

---

### stop_playback

Stop playback in Ableton.

**Example:**
```
"Stop playback"
"Stop"
"Pause the music"
```

---

### set_tempo

Change the session tempo.

**Parameters:**
- `tempo` (float): New tempo in BPM (typically 60-200)

**Example:**
```
"Set the tempo to 128 BPM"
"Change tempo to 140"
"Set BPM to 90"
```

---

## Common Workflows

### Check Session Before Working

```
"Get session info"
```

This helps you understand:
- How many tracks exist
- What the current tempo is
- Which tracks have devices

### Quick Playback Control

```
"Set tempo to 120 and start playback"
```

---

## Tips

!!! tip "Tempo Range"
    While you can set any tempo, typical ranges are:
    - Slow: 60-90 BPM (ballads, ambient)
    - Medium: 90-120 BPM (pop, rock)
    - Fast: 120-180 BPM (electronic, dance)
    - Very fast: 180+ BPM (drum & bass, hardstyle)

!!! info "Session Info Updates"
    Session info reflects the current state when called. If you make changes, call it again to see updated information.

---

## Related

- [Track Management](track-management.md) - Create and control tracks
- [API Reference](../api-reference.md) - Complete API documentation
