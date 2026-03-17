# Building Custom Tools

Create your own Ableton controllers and interactive tools using the MCP framework.

---

## Overview

Ableton MCP Extended provides a foundation for building:

- Custom MIDI controllers
- Interactive music applications
- Generative music systems
- Performance tools
- Educational applications

---

## Example: XY Mouse Controller

The repository includes a complete example of a custom controller:

**Location:** `experimental_tools/xy_mouse_controller/`

This demonstrates:

- Real-time parameter control via UDP
- Mouse gesture mapping
- Multi-parameter control
- Low-latency performance

### Running the Example

```bash
cd experimental_tools/xy_mouse_controller
pip install -r requirements.txt
python mouse_parameter_controller_udp.py
```

---

## Architecture

### Components

1. **Your Custom Tool** (Python, JavaScript, etc.)
2. **UDP/TCP Communication** (Socket connection)
3. **Ableton Remote Script** (Receives commands)
4. **Ableton Live API** (Executes changes)

```
Your Tool → UDP/TCP → Remote Script → Ableton API → Changes in Live
```

---

## Building a Custom Tool

### 1. Choose a Protocol

**TCP (Recommended for beginners):**
- Reliable delivery
- Request/response pattern
- Easier to debug

**UDP (For advanced real-time control):**
- Ultra-low latency
- Fire-and-forget
- High throughput

### 2. Establish Connection

**Python TCP Example:**
```python
import socket
import json

def send_command(command_type, params):
    # Connect to TCP server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 9877))

    # Send command
    command = {
        "type": command_type,
        "params": params
    }
    sock.sendall(json.dumps(command).encode())

    # Receive response
    response = sock.recv(8192).decode()
    sock.close()
    return json.loads(response)
```

**Python UDP Example:**
```python
import socket
import json

def send_udp_command(command_type, params):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    command = {
        "type": command_type,
        "params": params
    }
    sock.sendto(
        json.dumps(command).encode(),
        ("localhost", 9878)
    )
```

### 3. Implement Your Logic

```python
class CustomController:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def map_gesture_to_parameter(self, x, y):
        # Map X coordinate to filter cutoff
        cutoff = x / screen_width  # Normalize to 0-1

        # Map Y coordinate to resonance
        resonance = 1.0 - (y / screen_height)  # Normalize and invert

        # Update both parameters
        self.batch_update(0, 0, [5, 6], [cutoff, resonance])

    def batch_update(self, track, device, params, values):
        command = {
            "type": "batch_set_device_parameters",
            "params": {
                "track_index": track,
                "device_index": device,
                "parameter_indices": params,
                "values": values
            }
        }
        self.sock.sendto(
            json.dumps(command).encode(),
            ("localhost", 9878)
        )
```

---

## Example Projects

### 1. Simple Drum Sequencer

Control clip playback with a grid interface:

```python
def trigger_clip(track_index, clip_index):
    send_command("fire_clip", {
        "track_index": track_index,
        "clip_index": clip_index
    })
```

### 2. Parameter Randomizer

Randomly modulate device parameters:

```python
import random

def randomize_parameters(track, device, param_count):
    params = list(range(param_count))
    values = [random.random() for _ in params]

    send_udp_command("batch_set_device_parameters", {
        "track_index": track,
        "device_index": device,
        "parameter_indices": params,
        "values": values
    })
```

### 3. Gesture Recorder

Record and playback parameter gestures:

```python
class GestureRecorder:
    def __init__(self):
        self.recording = []

    def record_gesture(self, param_values):
        self.recording.append({
            "timestamp": time.time(),
            "values": param_values
        })

    def playback(self, track, device):
        start_time = time.time()
        for event in self.recording:
            # Wait until timestamp
            while time.time() - start_time < event["timestamp"]:
                time.sleep(0.001)

            # Apply parameter values
            send_udp_command("batch_set_device_parameters", {
                "track_index": track,
                "device_index": device,
                "parameter_indices": list(range(len(event["values"]))),
                "values": event["values"]
            })
```

---

## Best Practices

### Performance

!!! tip "Use UDP for Real-Time"
    For >30 updates per second, use UDP for lower latency.

!!! tip "Batch Updates"
    Update multiple parameters in one command using `batch_set_device_parameters`.

!!! tip "Throttle Updates"
    Limit update rate to what's perceptually necessary (100-200 Hz max).

### Reliability

!!! warning "Handle Disconnection"
    Check if Ableton is running before sending commands.

!!! warning "Validate Parameters"
    Ensure parameter indices and values are valid before sending.

### User Experience

!!! info "Provide Feedback"
    Visual or audio feedback helps users understand what's happening.

!!! info "Error Handling"
    Gracefully handle errors and connection issues.

---

## Tools and Libraries

### Recommended Python Libraries

- **socket**: Network communication (built-in)
- **pynput**: Mouse and keyboard input
- **screeninfo**: Screen dimensions
- **pygame**: Game-style interfaces
- **tkinter**: GUI applications
- **flask**: Web-based controllers

### Example Stack

```
pynput (input) → Your Logic → socket (output) → Ableton
```

---

## Advanced Topics

### Multi-Parameter Mapping

Map one input to multiple parameters:

```python
def map_one_to_many(input_value):
    # Map to multiple parameters with different curves
    cutoff = input_value  # Linear
    resonance = input_value ** 2  # Exponential
    drive = math.sin(input_value * math.pi)  # Sine wave

    batch_update(0, 0, [5, 6, 7], [cutoff, resonance, drive])
```

### Parameter Smoothing

Smooth parameter changes for better sound:

```python
class Smoother:
    def __init__(self, smooth_time=0.1):
        self.current = 0.0
        self.target = 0.0
        self.smooth_time = smooth_time

    def set_target(self, value):
        self.target = value

    def update(self, delta_time):
        # Exponential smoothing
        alpha = 1.0 - math.exp(-delta_time / self.smooth_time)
        self.current += (self.target - self.current) * alpha
        return self.current
```

---

## Resources

- **Example Code**: `experimental_tools/xy_mouse_controller/`
- **Remote Script**: `AbletonMCP_UDP/__init__.py`
- **MCP Server**: `MCP_Server/server.py`

---

## Share Your Creations!

Built something cool? Share it with the community:

- **GitHub Discussions**: Post your project
- **Tag @uisato_**: Share on social media
- **Contribute**: Submit a PR with your example

---

## Related

- [UDP High Performance](udp-server.md) - Real-time control details
- [Device Control](../features/device-control.md) - Parameter basics
- [API Reference](../api-reference.md) - Complete command reference
