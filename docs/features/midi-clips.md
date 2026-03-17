# MIDI Clips and Notes

Create and manipulate MIDI clips with precision control over notes.

---

## Creating Clips

### create_clip

Create a new MIDI clip in a track's clip slot.

**Parameters:**
- `track_index` (int): Index of the track
- `clip_index` (int): Clip slot index
- `length` (float, optional): Length in beats (default: 4.0)

**Examples:**
```
"Create a 4-bar MIDI clip on track 0, slot 0"
"Create an 8-beat clip on track 1, slot 2"
```

---

### set_clip_name

Name your clips for better organization.

**Parameters:**
- `track_index` (int): Index of the track
- `clip_index` (int): Clip slot index
- `name` (str): New clip name

**Examples:**
```
"Name the clip in track 0, slot 0 as 'Bassline'"
"Set clip name to 'Melody Idea'"
```

---

## Adding Notes

### add_notes_to_clip

Add MIDI notes to an existing clip.

**Parameters:**
- `track_index` (int): Index of the track
- `clip_index` (int): Clip slot index
- `notes` (array): Array of note objects

**Note Format:**
```json
{
  "pitch": 60,         // MIDI note number (0-127)
  "start_time": 0.0,   // Start position in beats
  "duration": 0.5,     // Length in beats
  "velocity": 100,     // Velocity (0-127)
  "mute": false        // Optional: mute state
}
```

**Examples:**
```
"Add a C4 note at beat 0"
"Add notes: C3 at 0, E3 at 1, G3 at 2"
"Create a C major chord at beat 1"
```

---

## Note Editing

### Transpose

Shift notes up or down by semitones.

**Examples:**
```
"Transpose all notes up by 12 semitones"
"Shift notes down by 5"
```

### Quantize

Align notes to a rhythmic grid.

**Examples:**
```
"Quantize notes to 16th notes"
"Quantize with 80% strength"
```

---

## Common Workflows

### Creating a Simple Melody

```
1. "Create a 4-bar clip on track 0, slot 0"
2. "Add these notes:
   - C4 at beat 0, duration 1
   - E4 at beat 1, duration 1
   - G4 at beat 2, duration 1
   - C5 at beat 3, duration 1"
3. "Name the clip 'Melody 1'"
```

### Creating a Chord Progression

```
"Create a clip and add:
- C major triad at beat 0
- F major triad at beat 4
- G major triad at beat 8
- C major triad at beat 12"
```

---

## MIDI Note Reference

Quick reference for common notes:

| Note | Number | Frequency | Use Case |
|------|--------|-----------|----------|
| C2   | 36     | 65.4 Hz   | Sub bass |
| C3   | 48     | 130.8 Hz  | Bass |
| C4   | 60     | 261.6 Hz  | Middle C |
| C5   | 72     | 523.3 Hz  | Melody |
| C6   | 84     | 1047 Hz   | High melody |

**Intervals:**
- Octave = +12 semitones
- Fifth = +7 semitones
- Major third = +4 semitones
- Minor third = +3 semitones

---

## Musical Time

Time in clips is measured in beats (quarter notes):

| Value | Duration |
|-------|----------|
| 0.25  | 16th note |
| 0.5   | 8th note |
| 1.0   | Quarter note |
| 2.0   | Half note |
| 4.0   | Whole note |

---

## Tips

!!! tip "Building Chords"
    Common chord intervals from root:

    - Major: 0, 4, 7 (C-E-G)
    - Minor: 0, 3, 7 (C-Eb-G)
    - Diminished: 0, 3, 6
    - Augmented: 0, 4, 8

!!! info "Velocity"
    Velocity affects note loudness:

    - 0-40: Very quiet (pp-p)
    - 41-80: Medium (mp-mf)
    - 81-100: Loud (f)
    - 101-127: Very loud (ff-fff)

!!! warning "Clip Slot Indices"
    Clip slots are zero-indexed like tracks:

    - First clip slot = 0
    - Second clip slot = 1
    - etc.

---

## Related

- [Track Management](track-management.md) - Create tracks for clips
- [Device Control](device-control.md) - Load instruments
- [API Reference](../api-reference.md) - Complete API documentation
