# High-Performance UDP Server

Ultra-low latency parameter control for real-time performance and interactive tools.

---

## Overview

The UDP server provides:

- **Ultra-low latency**: 1-5ms response time
- **High throughput**: Handle hundreds of updates per second
- **Real-time control**: Perfect for performance and interactive tools
- **Fire-and-forget**: No response required for maximum speed

---

## When to Use UDP

Use the UDP server when you need:

- ✅ Real-time parameter control
- ✅ High-frequency updates (100+ per second)
- ✅ Interactive controllers
- ✅ Live performance tools
- ✅ Mouse/gesture control

Use the standard TCP server when you need:

- ✅ Reliable delivery
- ✅ Response confirmation
- ✅ Complex queries
- ✅ Session information
- ✅ Browser operations

---

## Installation

### 1. Install the UDP Remote Script

Copy the UDP Remote Script to Ableton's Remote Scripts folder:

**macOS:**
```bash
cp AbletonMCP_UDP/__init__.py \
  ~/Library/Preferences/Ableton/Live\ X/User\ Remote\ Scripts/AbletonMCP_UDP/
```

**Windows:**
```bash
copy AbletonMCP_UDP\__init__.py \
  %USERPROFILE%\Documents\Ableton\User Library\Remote Scripts\AbletonMCP_UDP\
```

### 2. Configure in Ableton

1. Open Ableton Live **Preferences**
2. Go to **Link, Tempo & MIDI**
3. Add a new **Control Surface**: Select **AbletonMCP_UDP**
4. Set **Input/Output** to **None**

### 3. Verify

You should see: **"AbletonMCP: TCP on 9877, UDP on 9878"**

---

## Usage

### Direct UDP Communication

The UDP server listens on **port 9878** (TCP is on 9877).

**Example Python code:**

```python
import socket
import json

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send parameter update
command = {
    "type": "set_device_parameter",
    "params": {
        "track_index": 0,
        "device_index": 0,
        "parameter_index": 5,
        "value": 0.75
    }
}

sock.sendto(json.dumps(command).encode(), ("localhost", 9878))
```

---

## Example: XY Mouse Controller

The repository includes an example XY mouse controller:

```bash
cd experimental_tools/xy_mouse_controller
python mouse_parameter_controller_udp.py
```

This demonstrates:

- Real-time parameter control
- Mouse gesture mapping
- Ultra-low latency updates
- Batch parameter updates

---

## Supported Commands

### set_device_parameter

Set a single parameter value.

**Format:**
```json
{
  "type": "set_device_parameter",
  "params": {
    "track_index": 0,
    "device_index": 0,
    "parameter_index": 5,
    "value": 0.75
  }
}
```

---

### batch_set_device_parameters

Update multiple parameters in one operation.

**Format:**
```json
{
  "type": "batch_set_device_parameters",
  "params": {
    "track_index": 0,
    "device_index": 0,
    "parameter_indices": [0, 1, 2],
    "values": [0.5, 0.8, 0.3]
  }
}
```

---

## Performance Characteristics

| Metric | UDP Server | TCP Server |
|--------|-----------|------------|
| Latency | 1-5ms | 10-50ms |
| Throughput | 500+ msg/sec | 50-100 msg/sec |
| Reliability | Best-effort | Guaranteed |
| Response | None | Always |
| Use Case | Real-time control | Standard operations |

---

## Building Custom Tools

The UDP server enables you to build:

### Interactive Controllers

- XY pads
- Gesture control
- Touchscreen interfaces
- Motion tracking

### Performance Tools

- Live parameter automation
- Expression controllers
- Generative systems
- Real-time effects

### Example Architecture

```python
import socket
import json

class AbletonController:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = "localhost"
        self.port = 9878

    def set_parameter(self, track, device, param, value):
        command = {
            "type": "set_device_parameter",
            "params": {
                "track_index": track,
                "device_index": device,
                "parameter_index": param,
                "value": value
            }
        }
        self.sock.sendto(
            json.dumps(command).encode(),
            (self.host, self.port)
        )

# Use it
controller = AbletonController()
controller.set_parameter(0, 0, 5, 0.75)
```

---

## Tips

!!! tip "Batch Updates"
    Use `batch_set_device_parameters` for updating multiple parameters simultaneously - it's more efficient than individual updates.

!!! info "Fire-and-Forget"
    UDP doesn't confirm delivery. For critical operations, use the TCP server instead.

!!! warning "Network Reliability"
    UDP packets can be lost or arrive out of order. This is acceptable for real-time control where latest value matters most.

---

## Coexistence

Both TCP and UDP servers can run simultaneously:

- **TCP (9877)**: Standard MCP operations
- **UDP (9878)**: Real-time parameter control

Use both for maximum flexibility!

---

## Related

- [Device Control](../features/device-control.md) - Parameter basics
- [Custom Tools](custom-tools.md) - Build your own tools
- [API Reference](../api-reference.md) - Complete reference
