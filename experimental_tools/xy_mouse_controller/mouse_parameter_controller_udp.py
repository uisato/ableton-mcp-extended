#!/usr/bin/env python
"""
Mouse Parameter Controller for Ableton MCP

Maps mouse X/Y coordinates to Ableton Live device parameters.
Uses TCP for general commands and UDP for high-frequency parameter updates.

Usage:
    python mouse_parameter_controller.py

Controls:
    Mouse Movement: Maps X/Y position to selected parameters
    Ctrl+C: Exit the application
"""

import socket
import json
import time
import threading
import sys
from pynput import mouse

# Try different screen resolution detection methods
try:
    from screeninfo import get_monitors
    def get_screen_resolution():
        monitor = get_monitors()[0]
        return monitor.width, monitor.height
except ImportError:
    try:
        import tkinter as tk
        def get_screen_resolution():
            root = tk.Tk()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()
            return width, height
    except ImportError:
        def get_screen_resolution():
            print("Warning: Could not detect screen resolution. Using default 1920x1080.")
            print("Install 'screeninfo' or 'tkinter' for automatic resolution detection.")
            return 1920, 1080

# Configuration
HOST = "localhost"
TCP_PORT = 9877  # For general commands
UDP_PORT = 9878  # For parameter updates (fire-and-forget)

TRACK_INDEX = 0
DEVICE_INDEX = 0
X_PARAM_INDEX = 0
Y_PARAM_INDEX = 1

DEFAULT_MIN_PARAM_UPDATE_INTERVAL = 0.02
DEFAULT_CHANGE_THRESHOLD = 0.002
DEFAULT_CONSOLE_UPDATES_ENABLED = True
DEFAULT_DEBUG_MODE = False # Set to True when actively debugging UDP

MIN_PARAM_UPDATE_INTERVAL = DEFAULT_MIN_PARAM_UPDATE_INTERVAL
CHANGE_THRESHOLD = DEFAULT_CHANGE_THRESHOLD
CONSOLE_UPDATES_ENABLED = DEFAULT_CONSOLE_UPDATES_ENABLED
debug_mode = DEFAULT_DEBUG_MODE

MAX_RETRIES = 3
SOCKET_TIMEOUT = 5.0
BUFFER_SIZE = 8192

last_x_value = -1
last_y_value = -1
tcp_sock = None
udp_sock = None
connected_tcp = False
running = True
screen_width, screen_height = get_screen_resolution()
current_tracks = []
available_devices = []
device_parameters = {}
last_param_update_time = 0
PARAM_UPDATE_STRATEGY = "batch"
parameter_update_success_count_tcp = 0
parameter_update_failure_count_tcp = 0
last_successful_tcp_command_time = 0

def debug_log(message):
    if debug_mode:
        print(f"[DEBUG_CLIENT] {time.time():.3f}: {message}")

def _is_json_complete(json_str):
    try: json.loads(json_str); return True
    except json.JSONDecodeError: return False

def receive_full_response_tcp(sock_obj, buffer_size=BUFFER_SIZE):
    if not sock_obj: return None
    try:
        sock_obj.settimeout(SOCKET_TIMEOUT) 
        data = sock_obj.recv(buffer_size)
        if not data:
            debug_log("receive_full_response_tcp: No initial data, connection closed.")
            return None
        response_str = data.decode('utf-8')
        attempts = 0
        while not _is_json_complete(response_str) and attempts < 10:
            try:
                sock_obj.settimeout(0.5)
                more_data = sock_obj.recv(buffer_size)
                if not more_data: break
                response_str += more_data.decode('utf-8')
                attempts += 1
            except socket.timeout: break
            except Exception as e: debug_log(f"receive_full_response_tcp: More data error: {e}"); break
        return response_str
    except socket.timeout: debug_log("receive_full_response_tcp: Timeout."); return None
    except ConnectionResetError:
        debug_log("receive_full_response_tcp: ConnectionResetError.")
        global connected_tcp, tcp_sock
        connected_tcp = False; tcp_sock = None
        return None
    except Exception as e: debug_log(f"receive_full_response_tcp: Error: {e}"); return None

def send_command_tcp(command_type, params=None):
    global tcp_sock, connected_tcp
    if not connected_tcp and not connect_tcp():
        debug_log(f"send_command_tcp ({command_type}): TCP Not connected and connect failed.")
        return False
    if params is None: params = {}
    try:
        if tcp_sock is None:
            if not connect_tcp(): return False
        
        tcp_sock.settimeout(SOCKET_TIMEOUT)
        command = {"type": command_type, "params": params}
        cmd_str = json.dumps(command)
        debug_log(f"TCP_TX ({command_type}): {cmd_str}")
        tcp_sock.sendall(cmd_str.encode('utf-8'))
        
        response_raw = receive_full_response_tcp(tcp_sock)
        if not response_raw:
            debug_log(f"TCP_RX ({command_type}): No response."); return False
        
        debug_log(f"TCP_RX ({command_type}): {response_raw[:100]}{'...' if len(response_raw) > 100 else ''}")
        try:
            response_json = json.loads(response_raw)
            if response_json.get("error"):
                debug_log(f"TCP Server error for {command_type}: {response_json['error']}")
                return False
            return response_json.get("status") == "success" or "result" in response_json
        except json.JSONDecodeError:
            debug_log(f"TCP Invalid JSON for {command_type}: {response_raw[:50]}..."); return False
    except socket.timeout:
        debug_log(f"TCP Socket timeout sending {command_type}."); connected_tcp = False; tcp_sock = None; return False
    except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError) as e:
        debug_log(f"TCP Connection error sending {command_type}: {e}"); connected_tcp = False; tcp_sock = None; return False
    except Exception as e:
        debug_log(f"TCP Generic error sending {command_type}: {e}");
        if not isinstance(e, socket.timeout): connected_tcp = False; tcp_sock = None
        return False

def send_command_with_response_tcp(command_type, params=None, max_retries=MAX_RETRIES):
    global tcp_sock, connected_tcp, last_successful_tcp_command_time
    if not connected_tcp and not connect_tcp():
        debug_log(f"send_command_with_response_tcp ({command_type}): TCP Not connected and connect failed.")
        return None
    
    for retry in range(max_retries + 1):
        try:
            if tcp_sock is None:
                if not connect_tcp():
                    if retry < max_retries: time.sleep(0.5); continue
                    else: return None
            
            command = {"type": command_type, "params": params or {}}
            cmd_str = json.dumps(command)
            debug_log(f"TCP_TX_REQ ({command_type}, attempt {retry+1}): {cmd_str}")
            tcp_sock.sendall(cmd_str.encode('utf-8'))
            
            response_data_raw = receive_full_response_tcp(tcp_sock)
            if not response_data_raw:
                debug_log(f"TCP_RX_RESP ({command_type}, attempt {retry+1}): No data.")
                connected_tcp = False; tcp_sock = None
                if retry < max_retries: time.sleep(0.5 + retry*0.5); continue
                else: return None
            
            debug_log(f"TCP_RX_RESP ({command_type}, {len(response_data_raw)}B): {response_data_raw[:100]}...")
            try:
                response_json = json.loads(response_data_raw)
                if response_json.get("error"):
                    debug_log(f"TCP Command {command_type} error in response: {response_json['error']}")
                    if retry < max_retries: time.sleep(0.5); continue
                    return None
                
                if "result" in response_json or response_json.get("status") == "success":
                    last_successful_tcp_command_time = time.time()
                    return response_json
                
                debug_log(f"TCP Command {command_type} unexpected response: {response_json}")
                if retry < max_retries: time.sleep(0.5); continue
                return None
            except json.JSONDecodeError:
                debug_log(f"TCP Invalid JSON for {command_type}: {response_data_raw[:100]}...")
                if retry < max_retries: time.sleep(0.5); continue
                return None
        except socket.timeout:
            debug_log(f"TCP Socket timeout for {command_type} (attempt {retry+1}).")
            connected_tcp = False; tcp_sock = None
            if retry < max_retries: time.sleep(0.5); continue
            return None
        except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError) as e:
            debug_log(f"TCP Connection error for {command_type} (attempt {retry+1}): {e}")
            connected_tcp = False; tcp_sock = None
            if retry < max_retries: time.sleep(0.5); continue
            return None
        except Exception as e:
            debug_log(f"TCP Generic exception for {command_type} (attempt {retry+1}): {e}")
            connected_tcp = False; tcp_sock = None
            if retry < max_retries: time.sleep(0.5); continue
            return None
    debug_log(f"TCP All retries failed for {command_type}.")
    return None

def connect_tcp():
    global tcp_sock, connected_tcp, last_successful_tcp_command_time
    if connected_tcp and tcp_sock:
        return True
    
    if CONSOLE_UPDATES_ENABLED: print("Connecting to Ableton MCP (TCP)...")
    try:
        if tcp_sock:
            try: tcp_sock.close()
            except: pass
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.settimeout(SOCKET_TIMEOUT)
        debug_log(f"Attempting TCP connect to {HOST}:{TCP_PORT}")
        tcp_sock.connect((HOST, TCP_PORT))
        connected_tcp = True
        
        session_info_resp = send_command_with_response_tcp("get_session_info", max_retries=1)
        if session_info_resp and (session_info_resp.get("result") or session_info_resp.get("track_count") is not None):
            session_data = session_info_resp.get("result", session_info_resp)
            track_count = session_data.get("track_count", len(session_data.get("tracks",[])))
            if CONSOLE_UPDATES_ENABLED: print(f"TCP Connected. {track_count} tracks.")
            debug_log(f"TCP Connection successful. Tracks: {track_count}")
            last_successful_tcp_command_time = time.time()
            return True
        else:
            if CONSOLE_UPDATES_ENABLED: print("TCP Connected but failed session info. Will retry.")
            debug_log("TCP Connected, but session info failed/malformed.")
            last_successful_tcp_command_time = time.time()
            return True
    except Exception as e:
        if CONSOLE_UPDATES_ENABLED: print(f"TCP Connection error: {e}")
        debug_log(f"TCP Connection error: {e}")
        connected_tcp = False; tcp_sock = None
        return False

def init_udp_socket():
    global udp_sock
    try:
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        debug_log(f"UDP socket initialized for sending to {HOST}:{UDP_PORT}")
        return True
    except Exception as e:
        debug_log(f"Failed to initialize UDP socket: {e}")
        udp_sock = None
        return False

def get_session_info():
    response = send_command_with_response_tcp("get_session_info")
    if response:
        session_data = response.get("result", response)
        if isinstance(session_data, dict):
            if "track_count" in session_data: return session_data
            if "tracks" in session_data and isinstance(session_data["tracks"], list):
                return {"track_count": len(session_data["tracks"]), "tracks": session_data["tracks"]}
        debug_log(f"get_session_info: Unexpected data format: {session_data}")
    return None

def get_tracks():
    session_info = get_session_info()
    if not session_info: return []
    tracks = []
    if "tracks" in session_info and isinstance(session_info["tracks"], list):
        for i, track_item in enumerate(session_info["tracks"]):
            if isinstance(track_item, dict):
                dev_count = 0
                if "devices" in track_item:
                    df = track_item["devices"]
                    if isinstance(df, list): dev_count = len(df)
                    elif isinstance(df, dict): dev_count = df.get("device_count", 0)
                elif "device_count" in track_item: dev_count = track_item.get("device_count",0)
                tracks.append({
                    "index": track_item.get("index", i),
                    "name": track_item.get("name", f"Track {i}"),
                    "device_count": dev_count
                })
            else: tracks.append({"index": i, "name": f"Track {i}", "device_count": 0})
        if tracks: return tracks

    track_count = session_info.get("track_count", 0)
    if track_count == 0: return []
    for i in range(track_count):
        track_info_resp = send_command_with_response_tcp("get_track_info", {"track_index": i})
        track_data = track_info_resp.get("result", track_info_resp) if track_info_resp else None
        if track_data and isinstance(track_data, dict):
            dev_count = 0
            if "devices" in track_data:
                df = track_data["devices"]
                if isinstance(df, list): dev_count = len(df)
                elif isinstance(df, dict): dev_count = df.get("device_count", 0)
            elif "device_count" in track_data: dev_count = track_data.get("device_count",0)
            tracks.append({
                "index": track_data.get("index", i),
                "name": track_data.get("name", f"Track {i}"),
                "device_count": dev_count
            })
        else: tracks.append({"index": i, "name": f"Track {i}", "device_count": 0})
    return tracks

def get_devices(track_index):
    devices = []
    track_info_resp = send_command_with_response_tcp("get_track_info", {"track_index": track_index})
    actual_track_data = track_info_resp.get("result", track_info_resp) if track_info_resp else None

    if actual_track_data and isinstance(actual_track_data, dict) and "devices" in actual_track_data:
        devices_field = actual_track_data["devices"]
        if isinstance(devices_field, list):
            for i, dev_item in enumerate(devices_field):
                if isinstance(dev_item, dict):
                    devices.append({"index": dev_item.get("index", i), "name": dev_item.get("name", f"Device {i}")})
                else: devices.append({"index": i, "name": f"Device {i}"})
            if devices: return devices
        elif isinstance(devices_field, dict) and "devices" in devices_field and isinstance(devices_field["devices"], list):
            for i, dev_item in enumerate(devices_field["devices"]):
                 if isinstance(dev_item, dict):
                    devices.append({"index": dev_item.get("index", i), "name": dev_item.get("name", f"Device {i}")})
                 else: devices.append({"index": i, "name": f"Device {i}"})
            if devices: return devices
    
    dev_count_iter = 0
    if actual_track_data and isinstance(actual_track_data, dict):
        if "device_count" in actual_track_data: dev_count_iter = actual_track_data.get("device_count",0)
        elif "devices" in actual_track_data and isinstance(actual_track_data["devices"], dict):
            dev_count_iter = actual_track_data["devices"].get("device_count",0)

    if dev_count_iter > 0 and not devices: # Only if devices list is still empty
        debug_log(f"Device list not in track_info, fetching {dev_count_iter} device names via get_device_parameters.")
        for i in range(dev_count_iter):
            dev_params_resp = send_command_with_response_tcp("get_device_parameters", {"track_index": track_index, "device_index": i})
            dev_name = f"Device {i}"
            if dev_params_resp:
                dev_data = dev_params_resp.get("result", dev_params_resp)
                if isinstance(dev_data, dict): dev_name = dev_data.get("device_name", f"Device {i}")
            devices.append({"index": i, "name": dev_name})
        if devices: return devices
    return devices if devices else []


def get_device_parameters(track_index, device_index):
    global device_parameters
    device_key = f"{track_index}:{device_index}"
    if device_key in device_parameters and device_parameters[device_key] is not None:
        return device_parameters[device_key]
    
    params_resp = send_command_with_response_tcp("get_device_parameters", {"track_index": track_index, "device_index": device_index})
    params_list = []
    if params_resp:
        result_data = params_resp.get("result", params_resp)
        if isinstance(result_data, dict) and "parameters" in result_data and isinstance(result_data["parameters"], list):
            params_list = result_data["parameters"]
    device_parameters[device_key] = params_list
    return params_list

def fetch_device_info(track_index=None, device_index=None):
    target_track_idx = TRACK_INDEX if track_index is None else track_index
    target_device_idx = DEVICE_INDEX if device_index is None else device_index
    
    track_name = f"Track {target_track_idx}"
    track_info_resp = send_command_with_response_tcp("get_track_info", {"track_index": target_track_idx})
    if track_info_resp:
        track_data = track_info_resp.get("result", track_info_resp)
        if isinstance(track_data, dict) and "name" in track_data: track_name = track_data["name"]

    parameters = get_device_parameters(target_track_idx, target_device_idx)
    
    device_name = f"Device {target_device_idx}"
    dev_params_full_resp = send_command_with_response_tcp("get_device_parameters", {"track_index": target_track_idx, "device_index": target_device_idx})
    if dev_params_full_resp:
        dev_data_wrapper = dev_params_full_resp.get("result", dev_params_full_resp)
        if isinstance(dev_data_wrapper, dict) and "device_name" in dev_data_wrapper:
            device_name = dev_data_wrapper["device_name"]
    
    return {"track_index": target_track_idx, "track_name": track_name, 
            "device_index": target_device_idx, "device_name": device_name, 
            "parameter_count": len(parameters)}

def interactive_parameter_selection():
    global TRACK_INDEX, DEVICE_INDEX, X_PARAM_INDEX, Y_PARAM_INDEX
    print("\nLoading tracks...")
    tracks = get_tracks()
    if not tracks: print("No tracks found."); return False
    print("\nAvailable tracks:"); [print(f"  {t.get('index', 'N/A')}: {t.get('name', 'Unknown')} ({t.get('device_count', 'N/A')} dev)") for t in tracks]
    while True:
        try:
            ti = input(f"\nTrack (0-{len(tracks)-1 if tracks else 0}, q=quit): ")
            if ti.lower() == 'q': return False
            TRACK_INDEX = int(ti)
            if not any(t.get('index') == TRACK_INDEX for t in tracks): print("Invalid."); continue
            break
        except ValueError: print("Invalid number.")
    
    tn = next((t['name'] for t in tracks if t['index'] == TRACK_INDEX), f"Track {TRACK_INDEX}")
    print(f"\nSelected track: {tn}. Loading devices...")
    devices = get_devices(TRACK_INDEX)
    if not devices: print(f"No devices on track {tn}."); return False
    print("\nAvailable devices:"); [print(f"  {d.get('index', 'N/A')}: {d.get('name', 'Unknown')}") for d in devices]
    while True:
        try:
            di = input(f"\nDevice (0-{len(devices)-1 if devices else 0}, q=quit): ")
            if di.lower() == 'q': return False
            DEVICE_INDEX = int(di)
            if not any(d.get('index') == DEVICE_INDEX for d in devices): print("Invalid."); continue
            break
        except ValueError: print("Invalid number.")

    dn = next((d['name'] for d in devices if d['index'] == DEVICE_INDEX), f"Device {DEVICE_INDEX}")
    print(f"\nSelected device: {dn}. Loading parameters...")
    parameters = get_device_parameters(TRACK_INDEX, DEVICE_INDEX)
    if not parameters: print(f"No parameters on device {dn}."); return False
    print("\nAvailable parameters:"); 
    for p in parameters:
        val_disp = "N/A"
        norm_v = p.get("normalized_value")
        act_v = p.get("value")
        if norm_v is not None and isinstance(norm_v, float): val_disp = f"{norm_v:.2f} (norm)"
        elif act_v is not None: val_disp = f"{act_v:.2f} (act)" if isinstance(act_v, float) else str(act_v)
        print(f"  {p.get('index','N/A')}: {p.get('name','Param?')} (curr: {val_disp})")
    
    while True:
        try:
            xi = input(f"\nX param index (q=quit): "); 
            if xi.lower() == 'q': return False
            X_PARAM_INDEX = int(xi)
            if not any(p.get('index') == X_PARAM_INDEX for p in parameters): print("Invalid."); continue
            break
        except ValueError: print("Invalid num.")
    while True:
        try:
            yi = input(f"\nY param index (q=quit): "); 
            if yi.lower() == 'q': return False
            Y_PARAM_INDEX = int(yi)
            if not any(p.get('index') == Y_PARAM_INDEX for p in parameters): print("Invalid."); continue
            if Y_PARAM_INDEX == X_PARAM_INDEX: print("Y cannot be same as X."); continue
            break
        except ValueError: print("Invalid num.")

    pxn = next((p['name'] for p in parameters if p.get('index') == X_PARAM_INDEX), f"P{X_PARAM_INDEX}")
    pyn = next((p['name'] for p in parameters if p.get('index') == Y_PARAM_INDEX), f"P{Y_PARAM_INDEX}")
    print(f"\n--- Mapping Configured ---\nTrack: {TRACK_INDEX}-{tn}\nDevice: {DEVICE_INDEX}-{dn}")
    print(f"X -> P{X_PARAM_INDEX}:{pxn}\nY -> P{Y_PARAM_INDEX}:{pyn}\n------------------------")
    return True

def tcp_connection_health_check():
    global connected_tcp, tcp_sock, last_successful_tcp_command_time, parameter_update_failure_count_tcp
    current_time = time.time()
    if parameter_update_failure_count_tcp > 3 or \
       (last_successful_tcp_command_time > 0 and current_time - last_successful_tcp_command_time > 10.0):
        debug_log("Performing TCP connection health check...")
        if not connected_tcp or tcp_sock is None:
            debug_log("TCP: Attempting reconnect during health check.")
            return connect_tcp()
        
        if send_command_with_response_tcp("get_session_info", {}, max_retries=0) is not None:
            debug_log("TCP health check passed.")
            return True
        else:
            debug_log("TCP health check failed (no response to session info).")
            connected_tcp = False; tcp_sock = None
            return False
    return connected_tcp

def send_parameter_update_udp(track_idx, device_idx, param_idx, value):
    global udp_sock
    if not udp_sock:
        debug_log("UDP: Socket not initialized, cannot send parameter update.")
        return
    message = {
        "type": "set_device_parameter",
        "params": {
            "track_index": track_idx, "device_index": device_idx,
            "parameter_index": param_idx, "value": value
        }
    }
    try:
        payload = json.dumps(message).encode('utf-8')
        # DEBUGGING: Print exactly what's being sent via UDP
        debug_log(f"UDP_TX_SINGLE to {HOST}:{UDP_PORT} -> {payload.decode()}")
        udp_sock.sendto(payload, (HOST, UDP_PORT))
    except Exception as e:
        debug_log(f"UDP: Error sending parameter update: {e}")

def send_batch_parameter_update_udp(track_idx, device_idx, param_indices, values):
    global udp_sock
    if not udp_sock:
        debug_log("UDP: Socket not initialized, cannot send batch parameter update.")
        return
    message = {
        "type": "batch_set_device_parameters",
        "params": {
            "track_index": track_idx, "device_index": device_idx,
            "parameter_indices": param_indices, "values": values
        }
    }
    try:
        payload = json.dumps(message).encode('utf-8')
        # DEBUGGING: Print exactly what's being sent via UDP
        debug_log(f"UDP_TX_BATCH to {HOST}:{UDP_PORT} -> {payload.decode()}")
        udp_sock.sendto(payload, (HOST, UDP_PORT))
    except Exception as e:
        debug_log(f"UDP: Error sending batch parameter update: {e}")

def update_parameters_via_udp(x, y):
    global last_x_value, last_y_value
    norm_x = max(0.0, min(1.0, x / screen_width))
    norm_y = max(0.0, min(1.0, 1.0 - (y / screen_height)))
    x_changed = abs(norm_x - last_x_value) > CHANGE_THRESHOLD
    y_changed = abs(norm_y - last_y_value) > CHANGE_THRESHOLD
    if not (x_changed or y_changed): return

    if PARAM_UPDATE_STRATEGY == "batch":
        indices, values = [], []
        if x_changed: indices.append(X_PARAM_INDEX); values.append(norm_x)
        if y_changed: indices.append(Y_PARAM_INDEX); values.append(norm_y)
        if indices: send_batch_parameter_update_udp(TRACK_INDEX, DEVICE_INDEX, indices, values)
    elif PARAM_UPDATE_STRATEGY == "individual":
        if x_changed: send_parameter_update_udp(TRACK_INDEX, DEVICE_INDEX, X_PARAM_INDEX, norm_x)
        if y_changed: send_parameter_update_udp(TRACK_INDEX, DEVICE_INDEX, Y_PARAM_INDEX, norm_y)

    if x_changed: last_x_value = norm_x
    if y_changed: last_y_value = norm_y

    if CONSOLE_UPDATES_ENABLED:
        x_param_name = "X_P"; y_param_name = "Y_P"
        dk = f"{TRACK_INDEX}:{DEVICE_INDEX}"
        if dk in device_parameters and device_parameters[dk]:
            for p in device_parameters[dk]:
                if p.get("index") == X_PARAM_INDEX: x_param_name = p.get("name","P")[:10]
                if p.get("index") == Y_PARAM_INDEX: y_param_name = p.get("name","P")[:10]
        
        sx = f"X:{norm_x:.2f}->{x_param_name}({X_PARAM_INDEX})" if x_changed else f"X:{last_x_value:.2f}"
        sy = f"Y:{norm_y:.2f}->{y_param_name}({Y_PARAM_INDEX})" if y_changed else f"Y:{last_y_value:.2f}"
        sl = f"T{TRACK_INDEX},D{DEVICE_INDEX}| {sx}, {sy} (UDP)"
        sys.stdout.write("\r" + sl.ljust(100)); sys.stdout.flush()

def on_move(x, y):
    global last_param_update_time
    if running:
        ct = time.time()
        if (ct - last_param_update_time) >= MIN_PARAM_UPDATE_INTERVAL:
            update_parameters_via_udp(x, y)
            last_param_update_time = ct

def main():
    global running, X_PARAM_INDEX, Y_PARAM_INDEX, TRACK_INDEX, DEVICE_INDEX
    global debug_mode, CONSOLE_UPDATES_ENABLED, MIN_PARAM_UPDATE_INTERVAL, CHANGE_THRESHOLD
    global PARAM_UPDATE_STRATEGY, tcp_sock, udp_sock
    
    print("Mouse-to-Ableton Parameter Controller (Hybrid TCP/UDP)")
    print("===================================================")
    print(f"Screen resolution: {screen_width}x{screen_height}")

    debug_mode = DEFAULT_DEBUG_MODE
    CONSOLE_UPDATES_ENABLED = DEFAULT_CONSOLE_UPDATES_ENABLED
    MIN_PARAM_UPDATE_INTERVAL = DEFAULT_MIN_PARAM_UPDATE_INTERVAL
    CHANGE_THRESHOLD = DEFAULT_CHANGE_THRESHOLD
    PARAM_UPDATE_STRATEGY = "batch"

    args = sys.argv[1:]; use_cli_params = False; i = 0; positional_args_values = []
    usage_msg = (
        "Usage: python mouse_parameter_controller.py [track device x_param y_param] [options]\nOptions:\n"
        "  --debug                      Enable detailed logging.\n"
        "  --no-console-updates         Disable real-time console status updates.\n"
        "  --update-interval <sec>      Min time between UDP param updates. Default: {DEFAULT_MIN_PARAM_UPDATE_INTERVAL}\n"
        "  --change-threshold <val>     Min normalized param change for UDP. Default: {DEFAULT_CHANGE_THRESHOLD}\n"
        "  --strategy <batch|individual> UDP Parameter update strategy. Default: batch\n"
        "  --help                       Show this help message."
    ).format(DEFAULT_MIN_PARAM_UPDATE_INTERVAL=DEFAULT_MIN_PARAM_UPDATE_INTERVAL, DEFAULT_CHANGE_THRESHOLD=DEFAULT_CHANGE_THRESHOLD)

    if "--help" in args: print(usage_msg); return
    while i < len(args):
        arg = args[i]
        if arg == "--debug": debug_mode = True; i += 1
        elif arg == "--no-console-updates": CONSOLE_UPDATES_ENABLED = False; i += 1
        elif arg == "--update-interval":
            if i + 1 < len(args):
                try: MIN_PARAM_UPDATE_INTERVAL = float(args[i+1]); i += 2
                except ValueError: print_usage_and_exit(usage_msg, "Invalid --update-interval.")
            else: print_usage_and_exit(usage_msg, "--update-interval requires value.")
        elif arg == "--change-threshold":
            if i + 1 < len(args):
                try: CHANGE_THRESHOLD = float(args[i+1]); i += 2
                except ValueError: print_usage_and_exit(usage_msg, "Invalid --change-threshold.")
            else: print_usage_and_exit(usage_msg, "--change-threshold requires value.")
        elif arg == "--strategy":
            if i + 1 < len(args) and args[i+1] in ["batch", "individual"]:
                PARAM_UPDATE_STRATEGY = args[i+1]; i += 2
            else: print_usage_and_exit(usage_msg, "--strategy requires 'batch' or 'individual'.")
        elif not arg.startswith("--"): positional_args_values.append(arg); i += 1
        else: print(f"Warning: Unknown option {arg}"); i +=1
    
    if len(positional_args_values) == 4:
        try:
            TRACK_INDEX, DEVICE_INDEX, X_PARAM_INDEX, Y_PARAM_INDEX = map(int, positional_args_values)
            use_cli_params = True
        except ValueError: print("Warning: Positional args not all ints. Using interactive."); use_cli_params = False
    elif len(positional_args_values) > 0: print(f"Warning: Expected 0 or 4 positional args, got {len(positional_args_values)}. Ignoring.")
        
    if debug_mode: print("Debug mode enabled.")
    if not CONSOLE_UPDATES_ENABLED: print("Console updates disabled.")
    hz = (1/MIN_PARAM_UPDATE_INTERVAL if MIN_PARAM_UPDATE_INTERVAL > 0 else 'N/A')
    print(f"UDP Update interval: {MIN_PARAM_UPDATE_INTERVAL:.3f}s ({hz if isinstance(hz, str) else f'{hz:.1f}'} Hz)")
    print(f"UDP Change threshold: {CHANGE_THRESHOLD:.4f}")
    print(f"UDP Update strategy: {PARAM_UPDATE_STRATEGY}")
    if use_cli_params: print(f"CLI Mapping: T{TRACK_INDEX},D{DEVICE_INDEX}, X->P{X_PARAM_INDEX}, Y->P{Y_PARAM_INDEX}")
    else: print("Using interactive mode for mapping.")

    try:
        if not connect_tcp(): print("Initial TCP connection failed. Exiting."); return
        if not init_udp_socket(): print("Failed to init UDP socket. Exiting."); return
        # DEBUGGING: Confirm UDP socket object
        if udp_sock:
             debug_log(f"UDP Socket object after init: {udp_sock}")
        else:
             debug_log("!!! UDP Socket is None after init_udp_socket() !!!")


        if not use_cli_params:
            if not interactive_parameter_selection(): print("Setup aborted. Exiting."); return
        else: 
            print("Fetching info for CLI mapping (TCP)...")
            device_info = fetch_device_info(TRACK_INDEX, DEVICE_INDEX) 
            if device_info and device_info.get("parameter_count", 0) > 0:
                params_on_dev = get_device_parameters(TRACK_INDEX, DEVICE_INDEX)
                x_valid = any(p.get('index') == X_PARAM_INDEX for p in params_on_dev)
                y_valid = any(p.get('index') == Y_PARAM_INDEX for p in params_on_dev)
                pc = device_info.get("parameter_count",0)
                if not (x_valid and y_valid and X_PARAM_INDEX < pc and Y_PARAM_INDEX < pc):
                    print(f"Warning: Params X:{X_PARAM_INDEX} or Y:{Y_PARAM_INDEX} invalid for dev '{device_info.get('device_name','?')}' (count: {pc}).")
                    if not interactive_parameter_selection(): print("Setup aborted. Exiting."); return
                else:
                    xn = next((p.get('name') for p in params_on_dev if p.get('index') == X_PARAM_INDEX),"")
                    yn = next((p.get('name') for p in params_on_dev if p.get('index') == Y_PARAM_INDEX),"")
                    print(f"Configured for Dev:'{device_info.get('device_name','?')}' on Trk:'{device_info.get('track_name','?')}'")
                    print(f"  X->{xn}(P{X_PARAM_INDEX}), Y->{yn}(P{Y_PARAM_INDEX})")
            else:
                print(f"Warning: No info/params for T{TRACK_INDEX}/D{DEVICE_INDEX}.")
                if not interactive_parameter_selection(): print("Setup aborted. Exiting."); return
            
        listener = mouse.Listener(on_move=on_move)
        listener.start()
            
        print("\nMouse controller ACTIVE! (Parameters via UDP)")
        if CONSOLE_UPDATES_ENABLED: print("Move mouse. TCP for setup, UDP for params.")
        else: print("Move mouse. Console updates off. Check Ableton.")
        print("Press Ctrl+C to exit.")
            
        while running:
            time.sleep(0.5) 
            tcp_connection_health_check()
                
    except KeyboardInterrupt: print("\nShutting down (Ctrl+C)...")
    except Exception as e:
        print(f"\nUNEXPECTED ERROR in main: {e}")
        if debug_mode: import traceback; traceback.print_exc()
    finally:
        running = False
        if 'listener' in locals() and listener.is_alive(): listener.stop()
        if tcp_sock: debug_log("Closing TCP socket."); tcp_sock.close()
        if udp_sock: debug_log("Closing UDP socket."); udp_sock.close()
        print("Exited.")

def print_usage_and_exit(usage_msg, error_msg=""):
    if error_msg: print(f"Error: {error_msg}")
    print(usage_msg); sys.exit(1)

if __name__ == "__main__":
    main()