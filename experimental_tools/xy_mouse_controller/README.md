# XY Mouse Parameter Controller for Ableton Live (TCP/UDP Hybrid)

Control Ableton Live device parameters in real-time using your mouse position. This tool maps your mouse X/Y coordinates to selected parameters in Ableton Live. It uses a hybrid communication approach:

- **TCP Sockets:** For initial setup, browsing tracks, devices, and parameters.
- **UDP Sockets:** For high-frequency, low-latency parameter updates, providing a responsive control experience.

This script connects directly to a custom Ableton Live Remote Script (modified for TCP and UDP).

## Features

- **Hybrid TCP/UDP Communication**
  - Reliable TCP for setup and information retrieval.
  - High-performance, low-latency UDP for real-time parameter streaming.
- **Interactive Setup**: Select the target track, device, and parameters for X and Y axes at startup.
- **Real-time Control**: Smooth mapping of mouse X/Y movements to two distinct Ableton parameters.
- **Configurable Performance**:
  - Adjustable UDP update interval (frequency of parameter sends).
  - Change threshold for sensitivity to mouse movement.
  - Option to disable console status updates for maximum performance.
- **Batch & Individual UDP Strategies**: Choose how parameter updates are bundled.
- **Connection Health Monitoring (TCP)**: Ensures reliable setup communication.
- **Debug Mode**: Detailed logging for troubleshooting.

## Requirements

- Ableton Live.
- **Custom Ableton Live Remote Script**: Install the provided `__init__.py` (configured for TCP and UDP) into your Ableton Live MIDI Remote Scripts folder.
- Python 3.7+.
- Python packages:
  - `pynput` (mouse tracking)
  - `screeninfo` or `tkinter` (optional; for screen resolution detection)

## Installation

1. **Install Python**: Ensure Python 3.7 or newer is installed.
2. **Install Remote Script**:
   1. Locate your Ableton Live User Library:
      - Windows: `C:\Users\[YourUsername]\Documents\Ableton\User Library`
      - macOS: `~/Music/Ableton/User Library`
   2. Inside `User Library`, navigate to `Remote Scripts` (create if missing).
   3. Create a folder named `AbletonMCP_Hybrid` (or any unique name).
   4. Copy the modified `__init__.py` into `AbletonMCP_Hybrid`.
   5. Restart Ableton Live.
   6. In Live: **Preferences > Link/Tempo/MIDI**, set **Control Surface** to `AbletonMCP_Hybrid`.
3. **Install Python Packages**:

    ```bash
    pip install pynput screeninfo
    ```

## Usage

The main script is `mouse_parameter_controller_udp.py`.

Run in interactive mode:

```bash
python mouse_parameter_controller_udp.py
```

The script will:

1. Connect via TCP to the Remote Script for setup.
2. Initialize a UDP socket for parameter updates.
3. Prompt you to select:
   - Target track
   - Device on that track
   - Parameter for mouse X-axis
   - Parameter for mouse Y-axis
4. Listen for mouse movements and send updates via UDP.
5. Press `Ctrl+C` to exit.

### Command-Line Options

You can bypass interactive setup by providing mapping indices and options:

```bash
python mouse_parameter_controller_udp.py [track_idx device_idx x_param_idx y_param_idx] [options]
```

**Positional Arguments** (all zero-based indices):

- `track_idx`: Target track index
- `device_idx`: Device index on the selected track
- `x_param_idx`: Parameter index for mouse X
- `y_param_idx`: Parameter index for mouse Y

**Options**:

| Flag                      | Argument    | Default | Description                                                      |
|---------------------------|-------------|---------|------------------------------------------------------------------|
| `--debug`                 |             | off     | Enable detailed client-side logging                              |
| `--no-console-updates`    |             | on      | Disable real-time status line for improved performance           |
| `--update-interval`       | `<seconds>` | 0.02    | Minimum time between UDP updates (e.g., 0.04 for 25 Hz)          |
| `--change-threshold`      | `<value>`   | 0.002   | Min normalized change (0.0–1.0) to trigger a UDP update         |
| `--strategy`              | `batch` \| `individual` | batch   | Choose UDP send strategy                                          |
| `--help`                  |             |         | Show this help message and exit                                 |

#### Examples

- Run in interactive mode:

  ```bash
  python mouse_parameter_controller_udp.py
  ```

- Direct mapping (Track 0, Device 0, X → Param 0, Y → Param 1):

  ```bash
  python mouse_parameter_controller_udp.py 0 0 0 1
  ```

- No console updates; 10 Hz updates; higher sensitivity:

  ```bash
  python mouse_parameter_controller_udp.py --no-console-updates --update-interval 0.1 --change-threshold 0.001
  ```

- Individual UDP updates:

  ```bash
  python mouse_parameter_controller_udp.py --strategy individual
  ```

## How It Works

1. **Initialization** (client):
   - TCP connection (default `localhost:9877`) for setup and verification.
   - UDP socket (default `localhost:9878`) for fast updates.
2. **Setup**:
   - Verifies indices via TCP or guides interactively.
3. **Mouse Tracking**:
   - Normalizes X/Y to [0.0, 1.0].
   - Applies change threshold and rate limit.
4. **UDP Messaging**:
   - Constructs JSON (`set_device_parameter` or `batch_set_device_parameters`).
   - Sends as UDP datagram (no acknowledgment) for speed.
5. **Server-Side** (`__init__.py` in Ableton):
   - TCP server for commands.
   - UDP server parses datagrams and schedules parameter changes on Live's main thread.

This hybrid leverages TCP for reliability and UDP for low-latency control.

## Troubleshooting

### Parameters Not Changing (UDP Path)

- Ensure `AbletonMCP_Hybrid` is selected in Live's MIDI preferences and Live was restarted.
- Check `Log.txt` for:
  - "TCP Server started on port 9877"
  - "UDP Server started on port 9878"
  - "UDP: PACKET RECEIVED..."
- Run client with `--debug`:

  ```bash
  python mouse_parameter_controller_udp.py --debug
  ```

- Verify firewall or port conflicts blocking UDP `9878`.
- Confirm correct parameter indices.

### TCP Connection Issues

- Confirm Live is running.
- Match `TCP_PORT` between client and server script.
- Check `Log.txt` for TCP startup errors.

## Tips for Best Experience

- Use `--no-console-updates` for max performance.
- Experiment with `--update-interval` (0.02–0.05 s) and `--change-threshold` (0.001–0.005).
- Batch strategy is generally recommended.

## Development

- Client: `mouse_parameter_controller_udp.py`.
- Server: `__init__.py` in `AbletonMCP_Hybrid`.

*This README is updated to reflect the current hybrid TCP/UDP architecture and usage.*
