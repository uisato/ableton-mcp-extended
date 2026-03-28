"""Demo: create a 4/4 backbeat pattern on track 1 arrangement."""

import socket
import json
import time

KICK = 36
SNARE = 38
HIHAT_CLOSED = 42


def send_command(cmd_type, params=None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15.0)
    s.connect(('localhost', 9877))
    cmd = json.dumps({'type': cmd_type, 'params': params or {}})
    s.sendall(cmd.encode('utf-8'))

    chunks = []
    while True:
        try:
            chunk = s.recv(8192)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                json.loads(b''.join(chunks).decode('utf-8'))
                break
            except json.JSONDecodeError:
                continue
        except socket.timeout:
            break

    s.close()
    data = b''.join(chunks).decode('utf-8')
    result = json.loads(data)
    if result.get('status') == 'error':
        print(f"  ERROR: {result.get('message')}")
    return result


def main():
    # Step 1: Delete old test clip if it exists
    print("1. Cleaning up old clips...")
    info = send_command('get_arrangement_info', {'track_index': 0})
    if info.get('status') == 'success':
        clips = info['result']['tracks'][0].get('arrangement_clips', [])
        for i in range(len(clips) - 1, -1, -1):
            print(f"   Deleting clip {i}...")
            send_command('delete_arrangement_clip', {
                'track_index': 0, 'clip_index': i})
            time.sleep(0.2)

    # Step 2: Create a 4-bar MIDI clip (16 beats in 4/4)
    print("2. Creating 4-bar MIDI clip...")
    result = send_command('create_arrangement_clip', {
        'track_index': 0,
        'position': 0.0,
        'length': 16.0,
    })
    print(f"   Clip created: {result.get('status')}")
    time.sleep(0.3)

    # Step 3: Build the backbeat pattern
    print("3. Building backbeat pattern...")
    notes = []

    for bar in range(4):
        offset = bar * 4.0

        # Kick on beats 1 and 3
        notes.append({"pitch": KICK, "start_time": offset + 0.0,
                       "duration": 0.5, "velocity": 100, "mute": False})
        notes.append({"pitch": KICK, "start_time": offset + 2.0,
                       "duration": 0.5, "velocity": 100, "mute": False})

        # Snare on beats 2 and 4
        notes.append({"pitch": SNARE, "start_time": offset + 1.0,
                       "duration": 0.5, "velocity": 100, "mute": False})
        notes.append({"pitch": SNARE, "start_time": offset + 3.0,
                       "duration": 0.5, "velocity": 100, "mute": False})

        # Hi-hat on every 8th note
        for eighth in range(8):
            notes.append({"pitch": HIHAT_CLOSED,
                          "start_time": offset + eighth * 0.5,
                          "duration": 0.25, "velocity": 80, "mute": False})

    print(f"   Total notes: {len(notes)}")

    # Step 4: Add notes to arrangement clip
    print("4. Adding notes to arrangement clip...")
    result = send_command('add_notes_to_arrangement_clip', {
        'track_index': 0,
        'clip_index': 0,
        'notes': notes,
    })
    print(f"   Result: {result.get('status')}")

    # Step 5: Name the clip
    print("5. Naming clip 'Backbeat'...")
    send_command('set_arrangement_clip_property', {
        'track_index': 0, 'clip_index': 0,
        'property': 'name', 'value': 'Backbeat',
    })

    # Step 6: Verify
    print("6. Verifying...")
    info = send_command('get_arrangement_info', {'track_index': 0})
    if info.get('status') == 'success':
        track = info['result']['tracks'][0]
        clips = track.get('arrangement_clips', [])
        print(f"   Track: {track['name']}")
        for c in clips:
            print(f"   Clip: \"{c['name']}\" [{c['start_time']}-{c['end_time']}] "
                  f"muted={c['muted']}")

    print("\nDone! Load a Drum Rack on track 1 and hit play.")


if __name__ == '__main__':
    main()
