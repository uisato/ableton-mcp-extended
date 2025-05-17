# AbletonMCP/__init__.py
from __future__ import absolute_import, print_function, unicode_literals

from _Framework.ControlSurface import ControlSurface
import socket
import json
import threading
import time
import traceback

try:
    import Queue as queue
except ImportError:
    import queue

TCP_PORT = 9877
UDP_PORT = 9878 
HOST = "localhost"

def create_instance(c_instance):
    return AbletonMCP(c_instance)

class AbletonMCP(ControlSurface):
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self.log_message("AbletonMCP: Initializing (Hybrid TCP/UDP)...")
        
        self._song = self.song()
        self.running = False # Set to True once servers start

        self.tcp_server_socket = None
        self.tcp_client_threads = []
        self.tcp_server_thread = None
        
        self.udp_server_socket = None
        self.udp_server_thread = None

        self.start_tcp_server()
        self.start_udp_server() 
        
        self.log_message("AbletonMCP: Initialized.")
        self.show_message(f"AbletonMCP: TCP on {TCP_PORT}, UDP on {UDP_PORT}")
    
    def disconnect(self):
        self.log_message("AbletonMCP: Disconnecting...")
        self.running = False
        
        if self.tcp_server_socket:
            try: self.tcp_server_socket.close()
            except: pass
        if self.tcp_server_thread and self.tcp_server_thread.is_alive():
            self.tcp_server_thread.join(1.0)
        
        if self.udp_server_socket:
            try: self.udp_server_socket.close()
            except: pass
        if self.udp_server_thread and self.udp_server_thread.is_alive():
            self.udp_server_thread.join(1.0)
        
        ControlSurface.disconnect(self)
        self.log_message("AbletonMCP: Disconnected.")

    def start_tcp_server(self):
        try:
            self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_server_socket.bind((HOST, TCP_PORT))
            self.tcp_server_socket.listen(5)
            
            self.running = True 
            self.tcp_server_thread = threading.Thread(target=self._tcp_server_loop)
            self.tcp_server_thread.daemon = True
            self.tcp_server_thread.start()
            self.log_message(f"TCP Server started on port {TCP_PORT}")
        except Exception as e:
            self.log_message(f"Error starting TCP server: {e}")
            self.show_message(f"AbletonMCP: TCP Server Error - {e}")

    def _tcp_server_loop(self):
        try:
            self.log_message("TCP server thread started.")
            self.tcp_server_socket.settimeout(1.0)
            while self.running:
                try:
                    client_socket, address = self.tcp_server_socket.accept()
                    self.log_message(f"TCP Connection from {address}")
                    handler_thread = threading.Thread(target=self._handle_tcp_client, args=(client_socket,))
                    handler_thread.daemon = True
                    handler_thread.start()
                    self.tcp_client_threads.append(handler_thread)
                    self.tcp_client_threads = [t for t in self.tcp_client_threads if t.is_alive()]
                except socket.timeout: continue
                except Exception as e:
                    if self.running: self.log_message(f"TCP server accept error: {e}")
                    time.sleep(0.5)
            self.log_message("TCP server thread stopped.")
        except Exception as e: self.log_message(f"TCP server thread critical error: {e}")

    def _handle_tcp_client(self, client_socket):
        self.log_message("TCP client handler started.")
        buffer = ''
        try:
            while self.running:
                try:
                    data = client_socket.recv(8192)
                    if not data: self.log_message("TCP Client disconnected."); break
                    
                    try: buffer += data.decode('utf-8')
                    except AttributeError: buffer += data
                    
                    processed_something = True
                    while processed_something and buffer:
                        processed_something = False
                        try:
                            # Attempt to find one complete JSON object
                            # This is a simplified approach. A robust solution needs better framing or streaming parser.
                            # For now, we try to load the whole buffer. If it works, great.
                            # If not, we assume it's incomplete and wait for more.
                            # This could fail if multiple complete JSONs are in buffer without clear delimiters.
                            
                            # Let's try to parse only up to the first '}' if '{' is present
                            # This is still not perfect but might handle simple cases better.
                            first_brace = buffer.find('{')
                            if first_brace != -1:
                                # Try to find a matching brace. This is complex.
                                # Simplified: Try to parse the whole buffer. If it works, use it.
                                # If client sends one command and waits, this is fine.
                                command_json = json.loads(buffer) # Try to parse the whole buffer
                                self.log_message(f"TCP RCV from client: Type '{command_json.get('type', 'unknown')}'")
                                response = self._process_command(command_json)
                                
                                try: client_socket.sendall(json.dumps(response).encode('utf-8'))
                                except AttributeError: client_socket.sendall(json.dumps(response))
                                
                                buffer = "" # Clear buffer as it was all one command
                                processed_something = True 
                            # If no starting brace, or json.loads failed, it will fall to ValueError below
                            # and we'll wait for more data.

                        except ValueError: # JSONDecodeError is a subclass of ValueError
                            # Incomplete JSON in buffer, or malformed. Wait for more data.
                            # self.log_message(f"TCP: Incomplete JSON or parse error. Buffer: {buffer[:100]}")
                            break # Break from inner while, continue outer to recv more data
                except ConnectionResetError: self.log_message("TCP Client connection reset."); break
                except Exception as e:
                    self.log_message(f"TCP Error handling client data: {e}\n{traceback.format_exc()}")
                    try:
                        err_resp = {"status": "error", "message": str(e)}
                        client_socket.sendall(json.dumps(err_resp).encode('utf-8'))
                    except: pass
                    if not isinstance(e, ValueError): break 
        except Exception as e: self.log_message(f"TCP Error in client handler: {e}")
        finally:
            try: client_socket.close()
            except: pass
            self.log_message("TCP client handler stopped.")

    def start_udp_server(self):
        try:
            self.udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_server_socket.bind((HOST, UDP_PORT))
            if not self.running: self.running = True 
            self.udp_server_thread = threading.Thread(target=self._udp_server_loop)
            self.udp_server_thread.daemon = True
            self.udp_server_thread.start()
            self.log_message(f"UDP Server started on port {UDP_PORT}")
        except Exception as e:
            self.log_message(f"Error starting UDP server: {e}\n{traceback.format_exc()}") # Log traceback for UDP start error
            self.show_message(f"AbletonMCP: UDP Server Error - {e}")

    def _udp_server_loop(self):
        try:
            self.log_message("UDP server thread started.")
            while self.running:
                try:
                    data, addr = self.udp_server_socket.recvfrom(1024)
                    self.log_message("!!!!!!!! UDP: PACKET RECEIVED from " + str(addr) + " Data: " + str(data[:120])) # DEBUGGING LINE
                    if not self.running: break 
                    
                    try:
                        command_str = data.decode('utf-8')
                        command_json = json.loads(command_str)
                        self._process_udp_command(command_json) 
                    except Exception as e:
                        self.log_message(f"UDP: Error processing datagram: {e}. Data: {str(data[:100])}")
                except socket.error as se: 
                    if self.running: self.log_message(f"UDP server socket error: {se}")
                    break 
                except Exception as e: 
                    if self.running: self.log_message(f"UDP server loop error: {e}")
                    time.sleep(0.1) 
            self.log_message("UDP server thread stopped.")
        except Exception as e:
            self.log_message(f"UDP server thread critical error: {e}\n{traceback.format_exc()}")

    def _process_udp_command(self, command):
        self.log_message("--- UDP: _process_udp_command called with: " + str(command.get("type", "UNKNOWN_TYPE"))) # DEBUGGING LINE
        command_type = command.get("type", "")
        params = command.get("params", {})
        def task():
            try:
                if command_type == "set_device_parameter":
                    self.log_message(f"UDP: MainThread processing set_device_parameter with params: {str(params)}") # DEBUGGING
                    self._set_device_parameter(params.get("track_index", 0), 
                                               params.get("device_index", 0), 
                                               params.get("parameter_index", 0), 
                                               params.get("value", 0.0))
                elif command_type == "batch_set_device_parameters":
                    self.log_message(f"UDP: MainThread processing batch_set_device_parameters with params: {str(params)}") # DEBUGGING
                    self._batch_set_device_parameters(params.get("track_index", 0), 
                                                      params.get("device_index", 0), 
                                                      params.get("parameter_indices", []), 
                                                      params.get("values", []))
                else:
                    self.log_message(f"UDP: Received unknown or unsupported command type on main thread: {command_type}")
            except Exception as e_task:
                self.log_message(f"UDP: Error executing command '{command_type}' on main thread: {e_task}\n{traceback.format_exc()}")
        self.schedule_message(0, task)

    def _process_command(self, command): # For TCP
        command_type = command.get("type", "")
        params = command.get("params", {})
        response = {"status": "success", "result": {}}
        
        try:
            if command_type == "get_session_info": response["result"] = self._get_session_info()
            elif command_type == "get_track_info": response["result"] = self._get_track_info(params.get("track_index", 0))
            elif command_type == "get_device_parameters": response["result"] = self._get_device_parameters(params.get("track_index",0), params.get("device_index",0))
            elif command_type == "get_clip_envelope": response["result"] = self._get_clip_envelope(params.get("track_index", 0), params.get("clip_index", 0), params.get("device_index", 0), params.get("parameter_index", 0))
            elif command_type == "get_notes_from_clip": response["result"] = self._get_notes_from_clip(params.get("track_index", 0), params.get("clip_index", 0))
            elif command_type == "get_browser_tree": response["result"] = self.get_browser_tree(params.get("category_type", "all"))
            elif command_type == "get_browser_items_at_path": response["result"] = self.get_browser_items_at_path(params.get("path", ""))
            elif command_type == "get_scenes_info": response["result"] = self._get_scenes_info()
            
            elif command_type in [
                "create_midi_track", "set_track_name", "create_clip", "add_notes_to_clip", 
                "set_clip_name", "set_tempo", "fire_clip", "stop_clip", "start_playback", 
                "stop_playback", "load_instrument_or_effect", "load_browser_item",
                "add_clip_envelope_point", "clear_clip_envelope", "create_scene", 
                "set_scene_name", "delete_scene", "fire_scene", "batch_edit_notes_in_clip",
                "delete_notes_from_clip", "transpose_notes_in_clip", "create_audio_track", 
                "set_clip_loop_parameters", "set_clip_follow_action", "quantize_notes_in_clip",
                "randomize_note_timing", "set_note_probability", "import_audio_file",
                "set_track_level", "set_track_pan",
                "set_device_parameter", "batch_set_device_parameters" # TCP fallbacks
                ]:
                response_q = queue.Queue()
                def task_wrapper():
                    task_result = None
                    try:
                        # Ensure all command types are correctly routed to their _methods
                        if command_type == "create_midi_track": task_result = self._create_midi_track(params.get("index", -1))
                        elif command_type == "set_track_name": task_result = self._set_track_name(params.get("track_index",0), params.get("name",""))
                        elif command_type == "create_clip": task_result = self._create_clip(params.get("track_index",0), params.get("clip_index",0), params.get("length", 4.0))
                        elif command_type == "add_notes_to_clip": task_result = self._add_notes_to_clip(params.get("track_index",0), params.get("clip_index",0), params.get("notes",[]))
                        elif command_type == "set_clip_name": task_result = self._set_clip_name(params.get("track_index",0), params.get("clip_index",0), params.get("name",""))
                        elif command_type == "set_tempo": task_result = self._set_tempo(params.get("tempo", 120.0))
                        elif command_type == "fire_clip": task_result = self._fire_clip(params.get("track_index",0), params.get("clip_index",0))
                        elif command_type == "stop_clip": task_result = self._stop_clip(params.get("track_index",0), params.get("clip_index",0))
                        elif command_type == "start_playback": task_result = self._start_playback()
                        elif command_type == "stop_playback": task_result = self._stop_playback()
                        elif command_type == "load_instrument_or_effect" or command_type == "load_browser_item":
                            task_result = self._load_instrument_or_effect(params.get("track_index",0), params.get("uri", params.get("item_uri","")))
                        elif command_type == "set_device_parameter":
                            task_result = self._set_device_parameter(params.get("track_index",0), params.get("device_index",0), params.get("parameter_index",0), params.get("value",0.0))
                        elif command_type == "batch_set_device_parameters":
                            task_result = self._batch_set_device_parameters(params.get("track_index",0), params.get("device_index",0), params.get("parameter_indices",[]), params.get("values",[]))
                        elif command_type == "add_clip_envelope_point":
                            task_result = self._add_clip_envelope_point(params.get("track_index",0),params.get("clip_index",0),params.get("device_index",0),params.get("parameter_index",0),params.get("time",0.0),params.get("value",0.0),params.get("curve_type",0))
                        elif command_type == "clear_clip_envelope":
                            task_result = self._clear_clip_envelope(params.get("track_index",0),params.get("clip_index",0),params.get("device_index",0),params.get("parameter_index",0))
                        elif command_type == "create_scene": task_result = self._create_scene(params.get("index",-1))
                        elif command_type == "set_scene_name": task_result = self._set_scene_name(params.get("index",0),params.get("name",""))
                        elif command_type == "delete_scene": task_result = self._delete_scene(params.get("index",0))
                        elif command_type == "fire_scene": task_result = self._fire_scene(params.get("index",0))
                        elif command_type == "batch_edit_notes_in_clip": task_result = self._batch_edit_notes_in_clip(params.get("track_index",0),params.get("clip_index",0),params.get("note_ids",[]),params.get("note_data_array",[]))
                        elif command_type == "delete_notes_from_clip": task_result = self._delete_notes_from_clip(params.get("track_index",0),params.get("clip_index",0),params.get("from_time"),params.get("to_time"),params.get("from_pitch"),params.get("to_pitch"))
                        elif command_type == "transpose_notes_in_clip": task_result = self._transpose_notes_in_clip(params.get("track_index",0),params.get("clip_index",0),params.get("semitones",0),params.get("from_time"),params.get("to_time"),params.get("from_pitch"),params.get("to_pitch"))
                        elif command_type == "create_audio_track": task_result = self._create_audio_track(params.get("index",-1))
                        elif command_type == "set_clip_loop_parameters": task_result = self._set_clip_loop_parameters(params.get("track_index",0),params.get("clip_index",0),params.get("loop_start",0.0),params.get("loop_end",4.0),params.get("loop_enabled",True))
                        elif command_type == "set_clip_follow_action": task_result = self._set_clip_follow_action(params.get("track_index",0),params.get("clip_index",0),params.get("action","stop"),params.get("target_clip"),params.get("chance",1.0),params.get("time",1.0))
                        elif command_type == "quantize_notes_in_clip": task_result = self._quantize_notes_in_clip(params.get("track_index",0),params.get("clip_index",0),params.get("grid_size",0.25),params.get("strength",1.0),params.get("from_time"),params.get("to_time"),params.get("from_pitch"),params.get("to_pitch"))
                        elif command_type == "randomize_note_timing": task_result = self._randomize_note_timing(params.get("track_index",0),params.get("clip_index",0),params.get("amount",0.1),params.get("from_time"),params.get("to_time"),params.get("from_pitch"),params.get("to_pitch"))
                        elif command_type == "set_note_probability": task_result = self._set_note_probability(params.get("track_index",0),params.get("clip_index",0),params.get("probability",1.0),params.get("from_time"),params.get("to_time"),params.get("from_pitch"),params.get("to_pitch"))
                        elif command_type == "import_audio_file": task_result = self._import_audio_file(params.get("uri",""),params.get("track_index",-1),params.get("clip_index",0),params.get("create_track_if_needed",True))
                        elif command_type == "set_track_level": task_result = self._set_track_level(params.get("track_index",0),params.get("level",0.8))
                        elif command_type == "set_track_pan": task_result = self._set_track_pan(params.get("track_index",0),params.get("pan",0.0))
                        else: # Should not happen if command_type is in the list
                            response_q.put({"status": "error", "message": f"Unmapped state-modifying command: {command_type}"})
                            return
                        response_q.put({"status": "success", "result": task_result})
                    except Exception as e_task:
                        self.log_message(f"TCP Task Error ({command_type}): {e_task}\n{traceback.format_exc()}")
                        response_q.put({"status": "error", "message": str(e_task)})
                try: self.schedule_message(0, task_wrapper)
                except AssertionError: task_wrapper()
                try: response.update(response_q.get(timeout=10.0))
                except queue.Empty: response.update({"status": "error", "message": "Operation timeout"})
            else: response.update({"status": "error", "message": f"TCP: Unknown command: {command_type}"})
        except Exception as e_proc:
            self.log_message(f"TCP Error processing '{command_type}': {e_proc}\n{traceback.format_exc()}")
            response.update({"status": "error", "message": str(e_proc)})
        return response

    # --- Command Implementations ---
    def _get_session_info(self):
        try:
            return {"tempo": self._song.tempo, "track_count": len(self._song.tracks), 
                    "tracks": [{"index": i, "name": t.name, "device_count":len(t.devices)} for i,t in enumerate(self._song.tracks)]} # Example detail
        except Exception as e: self.log_message(f"Ex in _get_session_info: {e}"); raise

    def _get_track_info(self, track_index):
        if not (0 <= track_index < len(self._song.tracks)): raise IndexError("Track index out of range")
        track = self._song.tracks[track_index]
        devices_info = [{"index": i, "name": d.name} for i, d in enumerate(track.devices)]
        return {"index": track_index, "name": track.name, "devices": devices_info, "device_count": len(devices_info)}

    def _get_device_parameters(self, track_index, device_index):
        if not (0 <= track_index < len(self._song.tracks)): raise IndexError("Track index out of range")
        track = self._song.tracks[track_index]
        if not (0 <= device_index < len(track.devices)): raise IndexError("Device index out of range")
        device = track.devices[device_index]
        parameters_info = []
        for i, p in enumerate(device.parameters):
            norm_val = 0
            if (p.max - p.min) != 0:
                norm_val = (p.value - p.min) / (p.max - p.min)
            parameters_info.append({
                "index": i, "name": p.name, "value": p.value, "normalized_value": norm_val,
                "min": p.min, "max": p.max, "is_quantized": p.is_quantized, "is_enabled": p.is_enabled
            })
        return {"track_name": track.name, "device_name": device.name, "parameters": parameters_info}

    def _set_device_parameter(self, track_index, device_index, parameter_index, value):
        try:
            # self.log_message(f"MainThread: Setting T{track_index},D{device_index},P{parameter_index}={value:.3f}") # DEBUG LINE
            if not (0 <= track_index < len(self._song.tracks)): return {"error": "Track index out of range"}
            track = self._song.tracks[track_index]
            if not (0 <= device_index < len(track.devices)): return {"error": "Device index out of range"}
            device = track.devices[device_index]
            if not (0 <= parameter_index < len(device.parameters)): return {"error": f"Param index {parameter_index} out of range for dev with {len(device.parameters)} params"}
            parameter = device.parameters[parameter_index]
            if not (0.0 <= value <= 1.0): return {"error": f"Norm value {value} out of 0-1 range"}
            
            actual_value = parameter.min + value * (parameter.max - parameter.min)
            parameter.value = actual_value
            return {"parameter_name": parameter.name, "value": parameter.value, "normalized_value": value}
        except Exception as e:
            self.log_message(f"Error in _set_device_parameter: {e}\n{traceback.format_exc()}")
            return {"error": str(e)}

    def _batch_set_device_parameters(self, track_index, device_index, parameter_indices, values):
        try:
            # self.log_message(f"MainThread: Batch T{track_index},D{device_index}, Params:{len(parameter_indices)}") # DEBUG LINE
            if not (0 <= track_index < len(self._song.tracks)): return {"error": "Track index out of range"}
            track = self._song.tracks[track_index]
            if not (0 <= device_index < len(track.devices)): return {"error": "Device index out of range"}
            device = track.devices[device_index]
            if len(parameter_indices) != len(values): return {"error": "Indices/values length mismatch"}

            updated_params_info = []
            for i in range(len(parameter_indices)):
                p_idx, val_norm = parameter_indices[i], values[i]
                if not (0 <= p_idx < len(device.parameters)):
                    self.log_message(f"Batch: Invalid param index {p_idx}"); continue
                if not (0.0 <= val_norm <= 1.0):
                    self.log_message(f"Batch: Invalid value {val_norm} for P{p_idx}"); continue
                param = device.parameters[p_idx]
                actual_val = param.min + val_norm * (param.max - param.min)
                param.value = actual_val
                updated_params_info.append({"index": p_idx, "name": param.name, "normalized_value": val_norm})
            return {"updated_parameters_count": len(updated_params_info), "details": updated_params_info}
        except Exception as e:
            self.log_message(f"Error in _batch_set_device_parameters: {e}\n{traceback.format_exc()}")
            return {"error": str(e)}
            
    # Placeholder for other command implementations that should be present
    def _create_midi_track(self, index): self.log_message("_create_midi_track called"); return {"status": "ok_placeholder"}
    def _set_track_name(self, track_index, name): self.log_message("_set_track_name called"); return {"status": "ok_placeholder"}
    def _create_clip(self, track_index, clip_index, length): self.log_message("_create_clip called"); return {"status": "ok_placeholder"}
    def _add_notes_to_clip(self, track_index, clip_index, notes): self.log_message("_add_notes_to_clip called"); return {"status": "ok_placeholder"}
    def _set_clip_name(self, track_index, clip_index, name): self.log_message("_set_clip_name called"); return {"status": "ok_placeholder"}
    def _set_tempo(self, tempo): self.log_message("_set_tempo called"); self._song.tempo = tempo; return {"tempo": self._song.tempo}
    def _fire_clip(self, track_index, clip_index): self.log_message("_fire_clip called"); return {"status": "ok_placeholder"}
    def _stop_clip(self, track_index, clip_index): self.log_message("_stop_clip called"); return {"status": "ok_placeholder"}
    def _start_playback(self): self.log_message("_start_playback called"); self._song.start_playing(); return {"playing": True}
    def _stop_playback(self): self.log_message("_stop_playback called"); self._song.stop_playing(); return {"playing": False}
    def _load_instrument_or_effect(self, track_index, item_uri): self.log_message("_load_instrument_or_effect called"); return {"status": "ok_placeholder"}
    def _add_clip_envelope_point(self, track_index, clip_index, device_index, parameter_index, time_val, value, curve_type): self.log_message("_add_clip_envelope_point called"); return {"status": "ok_placeholder"}
    def _clear_clip_envelope(self, track_index, clip_index, device_index, parameter_index): self.log_message("_clear_clip_envelope called"); return {"status": "ok_placeholder"}
    def _create_scene(self, index): self.log_message("_create_scene called"); return {"status": "ok_placeholder"}
    def _set_scene_name(self, index, name): self.log_message("_set_scene_name called"); return {"status": "ok_placeholder"}
    def _delete_scene(self, index): self.log_message("_delete_scene called"); return {"status": "ok_placeholder"}
    def _fire_scene(self, index): self.log_message("_fire_scene called"); return {"status": "ok_placeholder"}
    def _batch_edit_notes_in_clip(self, track_index, clip_index, note_ids, note_data_array): self.log_message("_batch_edit_notes_in_clip called"); return {"status": "ok_placeholder"}
    def _delete_notes_from_clip(self, track_index, clip_index, from_time, to_time, from_pitch, to_pitch): self.log_message("_delete_notes_from_clip called"); return {"status": "ok_placeholder"}
    def _transpose_notes_in_clip(self, track_index, clip_index, semitones, from_time, to_time, from_pitch, to_pitch): self.log_message("_transpose_notes_in_clip called"); return {"status": "ok_placeholder"}
    def _create_audio_track(self, index): self.log_message("_create_audio_track called"); return {"status": "ok_placeholder"}
    def _set_clip_loop_parameters(self, track_index, clip_index, loop_start, loop_end, loop_enabled): self.log_message("_set_clip_loop_parameters called"); return {"status": "ok_placeholder"}
    def _set_clip_follow_action(self, track_index, clip_index, action, target_clip, chance, time_val): self.log_message("_set_clip_follow_action called"); return {"status": "ok_placeholder"}
    def _quantize_notes_in_clip(self, track_index, clip_index, grid_size, strength, from_time, to_time, from_pitch, to_pitch): self.log_message("_quantize_notes_in_clip called"); return {"status": "ok_placeholder"}
    def _randomize_note_timing(self, track_index, clip_index, amount, from_time, to_time, from_pitch, to_pitch): self.log_message("_randomize_note_timing called"); return {"status": "ok_placeholder"}
    def _set_note_probability(self, track_index, clip_index, probability, from_time, to_time, from_pitch, to_pitch): self.log_message("_set_note_probability called"); return {"status": "ok_placeholder"}
    def _import_audio_file(self, uri, track_index, clip_index, create_track_if_needed): self.log_message("_import_audio_file called"); return {"status": "ok_placeholder"}
    def _set_track_level(self, track_index, level): self.log_message("_set_track_level called"); return {"status": "ok_placeholder"}
    def _set_track_pan(self, track_index, pan): self.log_message("_set_track_pan called"); return {"status": "ok_placeholder"}
    def _get_clip_envelope(self, track_index, clip_index, device_index, parameter_index): self.log_message("_get_clip_envelope called"); return {"status": "placeholder_no_data"}
    def _get_notes_from_clip(self, track_index, clip_index): self.log_message("_get_notes_from_clip called"); return {"status": "placeholder_no_data"}
    def get_browser_tree(self, category_type="all"): self.log_message("get_browser_tree called"); return {"status": "placeholder_no_data"}
    def get_browser_items_at_path(self, path): self.log_message("get_browser_items_at_path called"); return {"status": "placeholder_no_data"}
    def _get_scenes_info(self): self.log_message("_get_scenes_info called"); return {"status": "placeholder_no_data"}