# Live 11 Compatibility Notes

This project supports Ableton Live 11 and Live 12. The tools work on both, but Live 11's Live API is more limited in two end-user-visible ways.

## Cue point names are read-only on Live 11

`CuePoint.name` is read-only in Live 11's Live API; the assignment is silently dropped. When you create a cue point:

- **Live 12:** the `name` you pass is applied (`"Verse"`, `"Drop"`, …).
- **Live 11:** Live assigns its own auto-generated locator name (`"1"`, `"2"`, `"3"`, …) regardless of what you pass.

`create_cue_point`'s response reflects what Live actually saved, not what you requested. Tools that look up cues by name (`jump_to_cue_point(name=…)`, name-based `delete_cue_point`) will only find them by Live's auto-generated names on Live 11. If your workflow depends on named cues, on Live 11 use direction-based jumps (`prev`/`next`) or jump by the locator name Live assigned.

## Creating an arrangement MIDI clip needs an empty session slot on Live 11

`Track.create_midi_clip(start_time, length)` is a Live 12 API; Live 11's `Track` has no such method. The Live 11 path stages a session-view clip and duplicates it into the arrangement, deleting the staged clip afterwards.

- **Live 12:** `create_arrangement_midi_clip` works on any track.
- **Live 11:** the target track must have at least one empty session-clip slot. If all slots are full, the call fails with `"No empty session clip slot available on track 'X'; Live 11 needs one free slot to stage an arrangement MIDI clip"`.

Free up a session slot on the target track before calling `create_arrangement_midi_clip`.
