# AbletonMCP/init.py
from __future__ import absolute_import, print_function, unicode_literals

from _Framework.ControlSurface import ControlSurface
import socket
import json
import threading
import time
import traceback

# Change queue import for Python 2
try:
    import Queue as queue  # Python 2
except ImportError:
    import queue  # Python 3

# Constants for socket communication
DEFAULT_PORT = 9877
HOST = "localhost"

def create_instance(c_instance):
    """Create and return the AbletonMCP script instance"""
    return AbletonMCP(c_instance)

class AbletonMCP(ControlSurface):
    """AbletonMCP Remote Script for Ableton Live"""
    
    def __init__(self, c_instance):
        """Initialize the control surface"""
        ControlSurface.__init__(self, c_instance)
        self.log_message("AbletonMCP Remote Script initializing...")
        
        # Socket server for communication
        self.server = None
        self.client_threads = []
        self.server_thread = None
        self.running = False
        
        # Cache the song reference for easier access
        self._song = self.song()
        
        # Start the socket server
        self.start_server()
        
        self.log_message("AbletonMCP initialized")
        
        # Show a message in Ableton
        self.show_message("AbletonMCP: Listening for commands on port " + str(DEFAULT_PORT))
    
    def disconnect(self):
        """Called when Ableton closes or the control surface is removed"""
        self.log_message("AbletonMCP disconnecting...")
        self.running = False
        
        # Stop the server
        if self.server:
            try:
                self.server.close()
            except:
                pass
        
        # Wait for the server thread to exit
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(1.0)
            
        # Clean up any client threads
        for client_thread in self.client_threads[:]:
            if client_thread.is_alive():
                # We don't join them as they might be stuck
                self.log_message("Client thread still alive during disconnect")
        
        ControlSurface.disconnect(self)
        self.log_message("AbletonMCP disconnected")
    
    def start_server(self):
        """Start the socket server in a separate thread"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((HOST, DEFAULT_PORT))
            self.server.listen(5)  # Allow up to 5 pending connections
            
            self.running = True
            self.server_thread = threading.Thread(target=self._server_thread)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.log_message("Server started on port " + str(DEFAULT_PORT))
        except Exception as e:
            self.log_message("Error starting server: " + str(e))
            self.show_message("AbletonMCP: Error starting server - " + str(e))
    
    def _server_thread(self):
        """Server thread implementation - handles client connections"""
        try:
            self.log_message("Server thread started")
            # Set a timeout to allow regular checking of running flag
            self.server.settimeout(1.0)
            
            while self.running:
                try:
                    # Accept connections with timeout
                    client, address = self.server.accept()
                    self.log_message("Connection accepted from " + str(address))
                    self.show_message("AbletonMCP: Client connected")
                    
                    # Handle client in a separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client,)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                    # Keep track of client threads
                    self.client_threads.append(client_thread)
                    
                    # Clean up finished client threads
                    self.client_threads = [t for t in self.client_threads if t.is_alive()]
                    
                except socket.timeout:
                    # No connection yet, just continue
                    continue
                except Exception as e:
                    if self.running:  # Only log if still running
                        self.log_message("Server accept error: " + str(e))
                    time.sleep(0.5)
            
            self.log_message("Server thread stopped")
        except Exception as e:
            self.log_message("Server thread error: " + str(e))
    
    def _handle_client(self, client):
        """Handle communication with a connected client"""
        self.log_message("Client handler started")
        client.settimeout(None)  # No timeout for client socket
        buffer = ''  # Changed from b'' to '' for Python 2
        
        try:
            while self.running:
                try:
                    # Receive data
                    data = client.recv(8192)
                    
                    if not data:
                        # Client disconnected
                        self.log_message("Client disconnected")
                        break
                    
                    # Accumulate data in buffer with explicit encoding/decoding
                    try:
                        # Python 3: data is bytes, decode to string
                        buffer += data.decode('utf-8')
                    except AttributeError:
                        # Python 2: data is already string
                        buffer += data
                    
                    try:
                        # Try to parse command from buffer
                        command = json.loads(buffer)  # Removed decode('utf-8')
                        buffer = ''  # Clear buffer after successful parse
                        
                        self.log_message("Received command: " + str(command.get("type", "unknown")))
                        
                        # Process the command and get response
                        response = self._process_command(command)
                        
                        # Send the response with explicit encoding
                        try:
                            # Python 3: encode string to bytes
                            client.sendall(json.dumps(response).encode('utf-8'))
                        except AttributeError:
                            # Python 2: string is already bytes
                            client.sendall(json.dumps(response))
                    except ValueError:
                        # Incomplete data, wait for more
                        continue
                        
                except Exception as e:
                    self.log_message("Error handling client data: " + str(e))
                    self.log_message(traceback.format_exc())
                    
                    # Send error response if possible
                    error_response = {
                        "status": "error",
                        "message": str(e)
                    }
                    try:
                        # Python 3: encode string to bytes
                        client.sendall(json.dumps(error_response).encode('utf-8'))
                    except AttributeError:
                        # Python 2: string is already bytes
                        client.sendall(json.dumps(error_response))
                    except:
                        # If we can't send the error, the connection is probably dead
                        break
                    
                    # For serious errors, break the loop
                    if not isinstance(e, ValueError):
                        break
        except Exception as e:
            self.log_message("Error in client handler: " + str(e))
        finally:
            try:
                client.close()
            except:
                pass
            self.log_message("Client handler stopped")
    
    def _process_command(self, command):
        """Process a command from the client and return a response"""
        command_type = command.get("type", "")
        params = command.get("params", {})
        
        # Initialize response
        response = {
            "status": "success",
            "result": {}
        }
        
        try:
            # Route the command to the appropriate handler
            if command_type == "get_session_info":
                response["result"] = self._get_session_info()
            elif command_type == "get_track_info":
                track_index = params.get("track_index", 0)
                response["result"] = self._get_track_info(track_index)
            # Commands that modify Live's state should be scheduled on the main thread
            elif command_type in ["create_midi_track", "set_track_name",
                                 "create_clip", "add_notes_to_clip", "set_clip_name",
                                 "set_tempo", "fire_clip", "stop_clip",
                                 "start_playback", "stop_playback", "load_browser_item",
                                 "set_song_time", "set_arrangement_loop", "jump_to_cue",
                                 "create_cue_point", "delete_cue_point",
                                 "create_arrangement_clip", "create_arrangement_audio_clip",
                                 "duplicate_to_arrangement", "delete_arrangement_clip",
                                 "set_arrangement_clip_property",
                                 "set_view", "control_arrangement_view",
                                 "manage_clip_automation",
                                 "add_notes_to_arrangement_clip"]:
                # Use a thread-safe approach with a response queue
                response_queue = queue.Queue()
                
                # Define a function to execute on the main thread
                def main_thread_task():
                    try:
                        result = None
                        if command_type == "create_midi_track":
                            index = params.get("index", -1)
                            result = self._create_midi_track(index)
                        elif command_type == "set_track_name":
                            track_index = params.get("track_index", 0)
                            name = params.get("name", "")
                            result = self._set_track_name(track_index, name)
                        elif command_type == "create_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            length = params.get("length", 4.0)
                            result = self._create_clip(track_index, clip_index, length)
                        elif command_type == "add_notes_to_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            notes = params.get("notes", [])
                            result = self._add_notes_to_clip(track_index, clip_index, notes)
                        elif command_type == "set_clip_name":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            name = params.get("name", "")
                            result = self._set_clip_name(track_index, clip_index, name)
                        elif command_type == "set_tempo":
                            tempo = params.get("tempo", 120.0)
                            result = self._set_tempo(tempo)
                        elif command_type == "fire_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._fire_clip(track_index, clip_index)
                        elif command_type == "stop_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._stop_clip(track_index, clip_index)
                        elif command_type == "start_playback":
                            result = self._start_playback()
                        elif command_type == "stop_playback":
                            result = self._stop_playback()
                        elif command_type == "load_instrument_or_effect":
                            track_index = params.get("track_index", 0)
                            uri = params.get("uri", "")
                            result = self._load_instrument_or_effect(track_index, uri)
                        elif command_type == "load_browser_item":
                            track_index = params.get("track_index", 0)
                            item_uri = params.get("item_uri", "")
                            result = self._load_browser_item(track_index, item_uri)
                        elif command_type == "set_song_time":
                            time_val = params.get("time", 0.0)
                            result = self._set_song_time(time_val)
                        elif command_type == "set_arrangement_loop":
                            enabled = params.get("enabled", True)
                            start = params.get("start", None)
                            length = params.get("length", None)
                            result = self._set_arrangement_loop(enabled, start, length)
                        elif command_type == "jump_to_cue":
                            direction = params.get("direction", None)
                            name = params.get("name", None)
                            result = self._jump_to_cue(direction, name)
                        elif command_type == "create_cue_point":
                            time_val = params.get("time", 0.0)
                            name = params.get("name", "")
                            result = self._create_cue_point(time_val, name)
                        elif command_type == "delete_cue_point":
                            time_val = params.get("time", 0.0)
                            result = self._delete_cue_point(time_val)
                        elif command_type == "create_arrangement_clip":
                            ti = params.get("track_index", 0)
                            pos = params.get("position", 0.0)
                            length = params.get("length", 4.0)
                            result = self._create_arrangement_clip(ti, pos, length)
                        elif command_type == "create_arrangement_audio_clip":
                            ti = params.get("track_index", 0)
                            pos = params.get("position", 0.0)
                            fp = params.get("file_path", "")
                            result = self._create_arrangement_audio_clip(ti, pos, fp)
                        elif command_type == "duplicate_to_arrangement":
                            ti = params.get("track_index", 0)
                            ci = params.get("clip_index", 0)
                            dt = params.get("destination_time", 0.0)
                            result = self._duplicate_to_arrangement(ti, ci, dt)
                        elif command_type == "delete_arrangement_clip":
                            ti = params.get("track_index", 0)
                            ci = params.get("clip_index", None)
                            cn = params.get("clip_name", None)
                            result = self._delete_arrangement_clip(ti, ci, cn)
                        elif command_type == "set_arrangement_clip_property":
                            ti = params.get("track_index", 0)
                            ci = params.get("clip_index", 0)
                            prop = params.get("property", "")
                            val = params.get("value", None)
                            result = self._set_arrangement_clip_property(ti, ci, prop, val)
                        elif command_type == "set_view":
                            vn = params.get("view_name", "Arranger")
                            result = self._set_view(vn)
                        elif command_type == "control_arrangement_view":
                            action = params.get("action", "")
                            ti = params.get("track_index", 0)
                            result = self._control_arrangement_view(action, ti)
                        elif command_type == "manage_clip_automation":
                            ti = params.get("track_index", 0)
                            ci = params.get("clip_index", 0)
                            action = params.get("action", "create")
                            pn = params.get("parameter_name", "")
                            result = self._manage_clip_automation(ti, ci, action, pn)
                        elif command_type == "add_notes_to_arrangement_clip":
                            ti = params.get("track_index", 0)
                            ci = params.get("clip_index", 0)
                            notes = params.get("notes", [])
                            result = self._add_notes_to_arrangement_clip(ti, ci, notes)

                        # Put the result in the queue
                        response_queue.put({"status": "success", "result": result})
                    except Exception as e:
                        self.log_message("Error in main thread task: " + str(e))
                        self.log_message(traceback.format_exc())
                        response_queue.put({"status": "error", "message": str(e)})
                
                # Schedule the task to run on the main thread
                try:
                    self.schedule_message(0, main_thread_task)
                except AssertionError:
                    # If we're already on the main thread, execute directly
                    main_thread_task()
                
                # Wait for the response with a timeout
                try:
                    task_response = response_queue.get(timeout=10.0)
                    if task_response.get("status") == "error":
                        response["status"] = "error"
                        response["message"] = task_response.get("message", "Unknown error")
                    else:
                        response["result"] = task_response.get("result", {})
                except queue.Empty:
                    response["status"] = "error"
                    response["message"] = "Timeout waiting for operation to complete"
            elif command_type == "get_browser_item":
                uri = params.get("uri", None)
                path = params.get("path", None)
                response["result"] = self._get_browser_item(uri, path)
            elif command_type == "get_browser_categories":
                category_type = params.get("category_type", "all")
                response["result"] = self._get_browser_categories(category_type)
            elif command_type == "get_browser_items":
                path = params.get("path", "")
                item_type = params.get("item_type", "all")
                response["result"] = self._get_browser_items(path, item_type)
            # Add the new browser commands
            elif command_type == "get_browser_tree":
                category_type = params.get("category_type", "all")
                response["result"] = self.get_browser_tree(category_type)
            elif command_type == "get_browser_items_at_path":
                path = params.get("path", "")
                response["result"] = self.get_browser_items_at_path(path)
            elif command_type == "get_arrangement_info":
                track_index = params.get("track_index", -1)
                response["result"] = self._get_arrangement_info(track_index)
            elif command_type == "get_cue_points":
                response["result"] = self._get_cue_points()
            else:
                response["status"] = "error"
                response["message"] = "Unknown command: " + command_type
        except Exception as e:
            self.log_message("Error processing command: " + str(e))
            self.log_message(traceback.format_exc())
            response["status"] = "error"
            response["message"] = str(e)
        
        return response
    
    # Arrangement helper methods

    def _get_arrangement_clip_info(self, clip):
        """Serialize a Clip object to ArrangementClipInfo dict."""
        try:
            return {
                "name": clip.name,
                "start_time": clip.start_time,
                "end_time": clip.end_time,
                "length": clip.end_time - clip.start_time,
                "is_midi": clip.is_midi_clip,
                "is_audio": clip.is_audio_clip,
                "muted": clip.muted,
                "color": clip.color,
                "looping": clip.looping,
                "loop_start": clip.loop_start,
                "loop_end": clip.loop_end,
            }
        except Exception as e:
            self.log_message("Error getting arrangement clip info: " + str(e))
            return {"name": "unknown", "error": str(e)}

    def _get_transport_info(self):
        """Serialize Song transport state to TransportInfo dict."""
        try:
            return {
                "is_playing": self._song.is_playing,
                "tempo": self._song.tempo,
                "signature_numerator": self._song.signature_numerator,
                "signature_denominator": self._song.signature_denominator,
                "current_time": self._song.current_song_time,
                "song_length": self._song.song_length,
                "loop_enabled": self._song.loop,
                "loop_start": self._song.loop_start,
                "loop_length": self._song.loop_length,
                "arrangement_overdub": self._song.arrangement_overdub,
                "back_to_arranger": self._song.back_to_arranger,
            }
        except Exception as e:
            self.log_message("Error getting transport info: " + str(e))
            raise

    def _resolve_arrangement_clip(self, track_index, clip_index=None, clip_name=None):
        """Resolve an arrangement clip by index or name.

        Returns (track, clip) tuple.
        """
        if track_index < 0 or track_index >= len(self._song.tracks):
            raise IndexError("Track index {0} out of range (0-{1})".format(
                track_index, len(self._song.tracks) - 1))

        track = self._song.tracks[track_index]
        clips = track.arrangement_clips

        if clip_name:
            matches = [(i, c) for i, c in enumerate(clips) if c.name == clip_name]
            if len(matches) == 0:
                raise ValueError("No arrangement clip named '{0}' on track '{1}'".format(
                    clip_name, track.name))
            if len(matches) > 1:
                raise ValueError("Ambiguous: {0} clips named '{1}' on track '{2}'".format(
                    len(matches), clip_name, track.name))
            return track, matches[0][1]

        if clip_index is None:
            raise ValueError("Either clip_index or clip_name must be provided")

        if clip_index < 0 or clip_index >= len(clips):
            raise IndexError("Clip index {0} out of range (0-{1}) on track '{2}'".format(
                clip_index, len(clips) - 1, track.name))

        return track, clips[clip_index]

    def _check_overlap(self, track, position, length):
        """Return list of clip names that overlap with [position, position+length)."""
        overlapped = []
        end = position + length
        for clip in track.arrangement_clips:
            if clip.start_time < end and clip.end_time > position:
                overlapped.append(clip.name or "(unnamed)")
        return overlapped

    # Command implementations

    def _get_session_info(self):
        """Get information about the current session"""
        try:
            result = {
                "tempo": self._song.tempo,
                "signature_numerator": self._song.signature_numerator,
                "signature_denominator": self._song.signature_denominator,
                "track_count": len(self._song.tracks),
                "return_track_count": len(self._song.return_tracks),
                "master_track": {
                    "name": "Master",
                    "volume": self._song.master_track.mixer_device.volume.value,
                    "panning": self._song.master_track.mixer_device.panning.value
                }
            }
            return result
        except Exception as e:
            self.log_message("Error getting session info: " + str(e))
            raise
    
    def _get_track_info(self, track_index):
        """Get information about a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            track = self._song.tracks[track_index]
            
            # Get clip slots
            clip_slots = []
            for slot_index, slot in enumerate(track.clip_slots):
                clip_info = None
                if slot.has_clip:
                    clip = slot.clip
                    clip_info = {
                        "name": clip.name,
                        "length": clip.length,
                        "is_playing": clip.is_playing,
                        "is_recording": clip.is_recording
                    }
                
                clip_slots.append({
                    "index": slot_index,
                    "has_clip": slot.has_clip,
                    "clip": clip_info
                })
            
            # Get devices
            devices = []
            for device_index, device in enumerate(track.devices):
                devices.append({
                    "index": device_index,
                    "name": device.name,
                    "class_name": device.class_name,
                    "type": self._get_device_type(device)
                })
            
            result = {
                "index": track_index,
                "name": track.name,
                "is_audio_track": track.has_audio_input,
                "is_midi_track": track.has_midi_input,
                "mute": track.mute,
                "solo": track.solo,
                "arm": track.arm,
                "volume": track.mixer_device.volume.value,
                "panning": track.mixer_device.panning.value,
                "clip_slots": clip_slots,
                "devices": devices
            }
            return result
        except Exception as e:
            self.log_message("Error getting track info: " + str(e))
            raise
    
    def _create_midi_track(self, index):
        """Create a new MIDI track at the specified index"""
        try:
            # Create the track
            self._song.create_midi_track(index)
            
            # Get the new track
            new_track_index = len(self._song.tracks) - 1 if index == -1 else index
            new_track = self._song.tracks[new_track_index]
            
            result = {
                "index": new_track_index,
                "name": new_track.name
            }
            return result
        except Exception as e:
            self.log_message("Error creating MIDI track: " + str(e))
            raise
    
    
    def _set_track_name(self, track_index, name):
        """Set the name of a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            # Set the name
            track = self._song.tracks[track_index]
            track.name = name
            
            result = {
                "name": track.name
            }
            return result
        except Exception as e:
            self.log_message("Error setting track name: " + str(e))
            raise
    
    def _create_clip(self, track_index, clip_index, length):
        """Create a new MIDI clip in the specified track and clip slot"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            track = self._song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            
            clip_slot = track.clip_slots[clip_index]
            
            # Check if the clip slot already has a clip
            if clip_slot.has_clip:
                raise Exception("Clip slot already has a clip")
            
            # Create the clip
            clip_slot.create_clip(length)
            
            result = {
                "name": clip_slot.clip.name,
                "length": clip_slot.clip.length
            }
            return result
        except Exception as e:
            self.log_message("Error creating clip: " + str(e))
            raise
    
    def _add_notes_to_clip(self, track_index, clip_index, notes):
        """Add MIDI notes to a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            track = self._song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            
            clip_slot = track.clip_slots[clip_index]
            
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            
            clip = clip_slot.clip
            
            # Convert note data to Live's format
            live_notes = []
            for note in notes:
                pitch = note.get("pitch", 60)
                start_time = note.get("start_time", 0.0)
                duration = note.get("duration", 0.25)
                velocity = note.get("velocity", 100)
                mute = note.get("mute", False)
                
                live_notes.append((pitch, start_time, duration, velocity, mute))
            
            # Add the notes
            clip.set_notes(tuple(live_notes))
            
            result = {
                "note_count": len(notes)
            }
            return result
        except Exception as e:
            self.log_message("Error adding notes to clip: " + str(e))
            raise
    
    def _set_clip_name(self, track_index, clip_index, name):
        """Set the name of a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            track = self._song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            
            clip_slot = track.clip_slots[clip_index]
            
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            
            clip = clip_slot.clip
            clip.name = name
            
            result = {
                "name": clip.name
            }
            return result
        except Exception as e:
            self.log_message("Error setting clip name: " + str(e))
            raise
    
    def _set_tempo(self, tempo):
        """Set the tempo of the session"""
        try:
            self._song.tempo = tempo
            
            result = {
                "tempo": self._song.tempo
            }
            return result
        except Exception as e:
            self.log_message("Error setting tempo: " + str(e))
            raise
    
    def _fire_clip(self, track_index, clip_index):
        """Fire a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            track = self._song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            
            clip_slot = track.clip_slots[clip_index]
            
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            
            clip_slot.fire()
            
            result = {
                "fired": True
            }
            return result
        except Exception as e:
            self.log_message("Error firing clip: " + str(e))
            raise
    
    def _stop_clip(self, track_index, clip_index):
        """Stop a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            track = self._song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            
            clip_slot = track.clip_slots[clip_index]
            
            clip_slot.stop()
            
            result = {
                "stopped": True
            }
            return result
        except Exception as e:
            self.log_message("Error stopping clip: " + str(e))
            raise
    
    
    def _start_playback(self):
        """Start playing the session"""
        try:
            self._song.start_playing()
            
            result = {
                "playing": self._song.is_playing
            }
            return result
        except Exception as e:
            self.log_message("Error starting playback: " + str(e))
            raise
    
    def _stop_playback(self):
        """Stop playing the session"""
        try:
            self._song.stop_playing()
            
            result = {
                "playing": self._song.is_playing
            }
            return result
        except Exception as e:
            self.log_message("Error stopping playback: " + str(e))
            raise
    
    def _get_browser_item(self, uri, path):
        """Get a browser item by URI or path"""
        try:
            # Access the application's browser instance instead of creating a new one
            app = self.application()
            if not app:
                raise RuntimeError("Could not access Live application")
                
            result = {
                "uri": uri,
                "path": path,
                "found": False
            }
            
            # Try to find by URI first if provided
            if uri:
                item = self._find_browser_item_by_uri(app.browser, uri)
                if item:
                    result["found"] = True
                    result["item"] = {
                        "name": item.name,
                        "is_folder": item.is_folder,
                        "is_device": item.is_device,
                        "is_loadable": item.is_loadable,
                        "uri": item.uri
                    }
                    return result
            
            # If URI not provided or not found, try by path
            if path:
                # Parse the path and navigate to the specified item
                path_parts = path.split("/")
                
                # Determine the root based on the first part
                current_item = None
                if path_parts[0].lower() == "nstruments":
                    current_item = app.browser.instruments
                elif path_parts[0].lower() == "sounds":
                    current_item = app.browser.sounds
                elif path_parts[0].lower() == "drums":
                    current_item = app.browser.drums
                elif path_parts[0].lower() == "audio_effects":
                    current_item = app.browser.audio_effects
                elif path_parts[0].lower() == "midi_effects":
                    current_item = app.browser.midi_effects
                else:
                    # Default to instruments if not specified
                    current_item = app.browser.instruments
                    # Don't skip the first part in this case
                    path_parts = ["instruments"] + path_parts
                
                # Navigate through the path
                for i in range(1, len(path_parts)):
                    part = path_parts[i]
                    if not part:  # Skip empty parts
                        continue
                    
                    found = False
                    for child in current_item.children:
                        if child.name.lower() == part.lower():
                            current_item = child
                            found = True
                            break
                    
                    if not found:
                        result["error"] = "Path part '{0}' not found".format(part)
                        return result
                
                # Found the item
                result["found"] = True
                result["item"] = {
                    "name": current_item.name,
                    "is_folder": current_item.is_folder,
                    "is_device": current_item.is_device,
                    "is_loadable": current_item.is_loadable,
                    "uri": current_item.uri
                }
            
            return result
        except Exception as e:
            self.log_message("Error getting browser item: " + str(e))
            self.log_message(traceback.format_exc())
            raise   
    
    
    
    def _load_browser_item(self, track_index, item_uri):
        """Load a browser item onto a track by its URI"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            track = self._song.tracks[track_index]
            
            # Access the application's browser instance instead of creating a new one
            app = self.application()
            
            # Find the browser item by URI
            item = self._find_browser_item_by_uri(app.browser, item_uri)
            
            if not item:
                raise ValueError("Browser item with URI '{0}' not found".format(item_uri))
            
            # Select the track
            self._song.view.selected_track = track
            
            # Load the item
            app.browser.load_item(item)
            
            result = {
                "loaded": True,
                "item_name": item.name,
                "track_name": track.name,
                "uri": item_uri
            }
            return result
        except Exception as e:
            self.log_message("Error loading browser item: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise
    
    def _find_browser_item_by_uri(self, browser_or_item, uri, max_depth=10, current_depth=0):
        """Find a browser item by its URI"""
        try:
            # Check if this is the item we're looking for
            if hasattr(browser_or_item, 'uri') and browser_or_item.uri == uri:
                return browser_or_item
            
            # Stop recursion if we've reached max depth
            if current_depth >= max_depth:
                return None
            
            # Check if this is a browser with root categories
            if hasattr(browser_or_item, 'instruments'):
                # Check all main categories
                categories = [
                    browser_or_item.instruments,
                    browser_or_item.sounds,
                    browser_or_item.drums,
                    browser_or_item.audio_effects,
                    browser_or_item.midi_effects
                ]
                
                for category in categories:
                    item = self._find_browser_item_by_uri(category, uri, max_depth, current_depth + 1)
                    if item:
                        return item
                
                return None
            
            # Check if this item has children
            if hasattr(browser_or_item, 'children') and browser_or_item.children:
                for child in browser_or_item.children:
                    item = self._find_browser_item_by_uri(child, uri, max_depth, current_depth + 1)
                    if item:
                        return item
            
            return None
        except Exception as e:
            self.log_message("Error finding browser item by URI: {0}".format(str(e)))
            return None
    
    # Arrangement command handlers

    def _get_arrangement_info(self, track_index):
        """Get arrangement clips and transport for one or all tracks."""
        try:
            transport = self._get_transport_info()
            tracks_data = []

            if track_index == -1:
                tracks = list(enumerate(self._song.tracks))
            else:
                if track_index < 0 or track_index >= len(self._song.tracks):
                    raise IndexError("Track index out of range")
                tracks = [(track_index, self._song.tracks[track_index])]

            for idx, track in tracks:
                clips = []
                for ci, clip in enumerate(track.arrangement_clips):
                    clip_info = self._get_arrangement_clip_info(clip)
                    clip_info["index"] = ci
                    clips.append(clip_info)

                tracks_data.append({
                    "index": idx,
                    "name": track.name,
                    "is_midi": track.has_midi_input,
                    "is_audio": track.has_audio_input,
                    "arrangement_clips": clips,
                    "clip_count": len(clips),
                })

            return {"transport": transport, "tracks": tracks_data}
        except Exception as e:
            self.log_message("Error getting arrangement info: " + str(e))
            raise

    def _get_cue_points(self):
        """Get all cue points."""
        try:
            cue_points = []
            for cp in self._song.cue_points:
                cue_points.append({"name": cp.name, "time": cp.time})
            return {"cue_points": cue_points}
        except Exception as e:
            self.log_message("Error getting cue points: " + str(e))
            raise

    def _set_song_time(self, time):
        """Set playback position."""
        try:
            self._song.current_song_time = time
            return {"time": self._song.current_song_time}
        except Exception as e:
            self.log_message("Error setting song time: " + str(e))
            raise

    def _set_arrangement_loop(self, enabled, start=None, length=None):
        """Set arrangement loop state and region."""
        try:
            self._song.loop = enabled
            if start is not None:
                self._song.loop_start = start
            if length is not None:
                self._song.loop_length = length
            return {
                "enabled": self._song.loop,
                "start": self._song.loop_start,
                "length": self._song.loop_length,
            }
        except Exception as e:
            self.log_message("Error setting arrangement loop: " + str(e))
            raise

    def _jump_to_cue(self, direction=None, name=None):
        """Jump to cue point by direction or name."""
        try:
            if direction == "next":
                self._song.jump_to_next_cue()
                return {"direction": "next", "time": self._song.current_song_time}
            elif direction == "prev":
                self._song.jump_to_prev_cue()
                return {"direction": "prev", "time": self._song.current_song_time}
            elif name:
                for cp in self._song.cue_points:
                    if cp.name == name:
                        cp.jump()
                        return {"name": cp.name, "time": cp.time}
                raise ValueError("Cue point '{0}' not found".format(name))
            else:
                raise ValueError("Provide direction ('next'/'prev') or name")
        except Exception as e:
            self.log_message("Error jumping to cue: " + str(e))
            raise

    def _create_cue_point(self, time, name=""):
        """Create a cue point at the given time."""
        try:
            # Check if cue already exists at this position
            for cp in self._song.cue_points:
                if abs(cp.time - time) < 0.01:
                    raise ValueError("Cue point already exists at this position: " + cp.name)
            self._song.current_song_time = time
            self._song.set_or_delete_cue()
            return {"time": time, "name": name}
        except Exception as e:
            self.log_message("Error creating cue point: " + str(e))
            raise

    def _delete_cue_point(self, time):
        """Delete a cue point at the given time."""
        try:
            found = False
            for cp in self._song.cue_points:
                if abs(cp.time - time) < 0.01:
                    found = True
                    break
            if not found:
                raise ValueError("No cue point at this position")
            self._song.current_song_time = time
            self._song.set_or_delete_cue()
            return {"deleted": True}
        except Exception as e:
            self.log_message("Error deleting cue point: " + str(e))
            raise

    def _validate_not_return_or_master(self, track_index):
        """Raise if track is a return or master track."""
        track = self._song.tracks[track_index]
        # Return tracks and master track are separate in the Live API,
        # but if accessed via tracks list they are regular tracks.
        # Check by comparing against return_tracks and master_track.
        for rt in self._song.return_tracks:
            if track == rt:
                raise ValueError("Cannot create arrangement clips on return track '{0}'".format(track.name))
        if track == self._song.master_track:
            raise ValueError("Cannot create arrangement clips on master track")

    def _create_arrangement_clip(self, track_index, position, length):
        """Create MIDI clip in arrangement."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            self._validate_not_return_or_master(track_index)
            track = self._song.tracks[track_index]
            overlapped = self._check_overlap(track, position, length)
            track.create_midi_clip(position, length)
            # Find the newly created clip
            result = {"start_time": position, "length": length, "is_midi": True}
            for clip in track.arrangement_clips:
                if abs(clip.start_time - position) < 0.01:
                    result = self._get_arrangement_clip_info(clip)
                    break
            result["overlapped_clips"] = overlapped
            return result
        except Exception as e:
            self.log_message("Error creating arrangement clip: " + str(e))
            raise

    def _create_arrangement_audio_clip(self, track_index, position, file_path):
        """Create audio clip in arrangement from file."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            self._validate_not_return_or_master(track_index)
            track = self._song.tracks[track_index]
            track.create_audio_clip(file_path, position)
            # Find the newly created clip
            result = {"start_time": position, "file_path": file_path, "is_audio": True}
            for clip in track.arrangement_clips:
                if abs(clip.start_time - position) < 0.01:
                    result = self._get_arrangement_clip_info(clip)
                    break
            return result
        except Exception as e:
            self.log_message("Error creating arrangement audio clip: " + str(e))
            raise

    def _duplicate_to_arrangement(self, track_index, clip_index, destination_time):
        """Duplicate a session clip to arrangement."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip slot index out of range")
            slot = track.clip_slots[clip_index]
            if not slot.has_clip:
                raise ValueError("No clip in slot {0}".format(clip_index))
            clip = slot.clip
            track.duplicate_clip_to_arrangement(clip, destination_time)
            # Find the duplicated clip
            result = {"start_time": destination_time, "duplicated": True}
            for arr_clip in track.arrangement_clips:
                if abs(arr_clip.start_time - destination_time) < 0.01:
                    result = self._get_arrangement_clip_info(arr_clip)
                    result["duplicated"] = True
                    break
            return result
        except Exception as e:
            self.log_message("Error duplicating to arrangement: " + str(e))
            raise

    def _add_notes_to_arrangement_clip(self, track_index, clip_index, notes):
        """Add MIDI notes to an arrangement clip."""
        try:
            track, clip = self._resolve_arrangement_clip(track_index, clip_index)
            if not clip.is_midi_clip:
                raise ValueError("Clip is not a MIDI clip")
            live_notes = []
            for note in notes:
                pitch = note.get("pitch", 60)
                start_time = note.get("start_time", 0.0)
                duration = note.get("duration", 0.25)
                velocity = note.get("velocity", 100)
                mute = note.get("mute", False)
                live_notes.append((pitch, start_time, duration, velocity, mute))
            clip.set_notes(tuple(live_notes))
            return {"note_count": len(notes)}
        except Exception as e:
            self.log_message("Error adding notes to arrangement clip: " + str(e))
            raise

    def _delete_arrangement_clip(self, track_index, clip_index=None, clip_name=None):
        """Delete an arrangement clip."""
        try:
            track, clip = self._resolve_arrangement_clip(track_index, clip_index, clip_name)
            track.delete_clip(clip)
            return {"deleted": True}
        except Exception as e:
            self.log_message("Error deleting arrangement clip: " + str(e))
            raise

    def _set_arrangement_clip_property(self, track_index, clip_index, property_name, value):
        """Set a property on an arrangement clip."""
        try:
            ALLOWED = ("name", "muted", "color", "looping", "loop_start", "loop_end",
                       "gain", "pitch_coarse", "pitch_fine", "warping", "warp_mode")
            if property_name not in ALLOWED:
                raise ValueError("Property '{0}' not allowed. Allowed: {1}".format(
                    property_name, ", ".join(ALLOWED)))
            track, clip = self._resolve_arrangement_clip(track_index, clip_index)
            setattr(clip, property_name, value)
            return {"property": property_name, "value": getattr(clip, property_name)}
        except Exception as e:
            self.log_message("Error setting arrangement clip property: " + str(e))
            raise

    def _set_view(self, view_name):
        """Switch Ableton view."""
        try:
            app = self.application()
            app.view.show_view(view_name)
            return {"visible": app.view.is_view_visible(view_name)}
        except Exception as e:
            self.log_message("Error setting view: " + str(e))
            raise

    def _control_arrangement_view(self, action, track_index=0):
        """Dispatch arrangement view control actions."""
        try:
            app = self.application()
            if action == "zoom_in":
                app.view.zoom_view(1, "Arranger", False)
            elif action == "zoom_out":
                app.view.zoom_view(0, "Arranger", False)
            elif action == "scroll_right":
                app.view.scroll_view(1, "Arranger", False)
            elif action == "scroll_left":
                app.view.scroll_view(0, "Arranger", False)
            elif action == "follow_on":
                self._song.view.follow_song = True
            elif action == "follow_off":
                self._song.view.follow_song = False
            elif action == "collapse_track":
                if track_index < 0 or track_index >= len(self._song.tracks):
                    raise IndexError("Track index out of range")
                self._song.tracks[track_index].view.is_collapsed = True
            elif action == "expand_track":
                if track_index < 0 or track_index >= len(self._song.tracks):
                    raise IndexError("Track index out of range")
                self._song.tracks[track_index].view.is_collapsed = False
            else:
                raise ValueError("Unknown action: " + action)
            return {"action": action, "done": True}
        except Exception as e:
            self.log_message("Error controlling arrangement view: " + str(e))
            raise

    def _manage_clip_automation(self, track_index, clip_index, action, parameter_name=""):
        """Create or clear automation envelopes."""
        try:
            track, clip = self._resolve_arrangement_clip(track_index, clip_index)
            if action == "clear_all":
                clip.clear_all_envelopes()
                return {"action": "clear_all", "done": True}
            # Find the parameter
            param = None
            # Check mixer device first
            mixer = track.mixer_device
            for p in [mixer.volume, mixer.panning]:
                if p.name.lower() == parameter_name.lower():
                    param = p
                    break
            # Check sends
            if param is None:
                for send in mixer.sends:
                    if send.name.lower() == parameter_name.lower():
                        param = send
                        break
            # Check track devices
            if param is None:
                for device in track.devices:
                    for p in device.parameters:
                        if p.name.lower() == parameter_name.lower():
                            param = p
                            break
                    if param:
                        break
            if param is None:
                raise ValueError("Parameter '{0}' not found on track '{1}'".format(
                    parameter_name, track.name))
            if action == "create":
                clip.create_automation_envelope(param)
                return {"action": "create", "parameter": param.name, "done": True}
            elif action == "clear":
                clip.clear_envelope(param)
                return {"action": "clear", "parameter": param.name, "done": True}
            else:
                raise ValueError("Unknown action: " + action)
        except Exception as e:
            self.log_message("Error managing clip automation: " + str(e))
            raise

    # Helper methods

    def _get_device_type(self, device):
        """Get the type of a device"""
        try:
            # Simple heuristic - in a real implementation you'd look at the device class
            if device.can_have_drum_pads:
                return "drum_machine"
            elif device.can_have_chains:
                return "rack"
            elif "instrument" in device.class_display_name.lower():
                return "instrument"
            elif "audio_effect" in device.class_name.lower():
                return "audio_effect"
            elif "midi_effect" in device.class_name.lower():
                return "midi_effect"
            else:
                return "unknown"
        except:
            return "unknown"
    
    def get_browser_tree(self, category_type="all"):
        """
        Get a simplified tree of browser categories.
        
        Args:
            category_type: Type of categories to get ('all', 'instruments', 'sounds', etc.)
            
        Returns:
            Dictionary with the browser tree structure
        """
        try:
            # Access the application's browser instance instead of creating a new one
            app = self.application()
            if not app:
                raise RuntimeError("Could not access Live application")
                
            # Check if browser is available
            if not hasattr(app, 'browser') or app.browser is None:
                raise RuntimeError("Browser is not available in the Live application")
            
            # Log available browser attributes to help diagnose issues
            browser_attrs = [attr for attr in dir(app.browser) if not attr.startswith('_')]
            self.log_message("Available browser attributes: {0}".format(browser_attrs))
            
            result = {
                "type": category_type,
                "categories": [],
                "available_categories": browser_attrs
            }
            
            # Helper function to process a browser item and its children
            def process_item(item, depth=0):
                if not item:
                    return None
                
                result = {
                    "name": item.name if hasattr(item, 'name') else "Unknown",
                    "is_folder": hasattr(item, 'children') and bool(item.children),
                    "is_device": hasattr(item, 'is_device') and item.is_device,
                    "is_loadable": hasattr(item, 'is_loadable') and item.is_loadable,
                    "uri": item.uri if hasattr(item, 'uri') else None,
                    "children": []
                }
                
                
                return result
            
            # Process based on category type and available attributes
            if (category_type == "all" or category_type == "instruments") and hasattr(app.browser, 'instruments'):
                try:
                    instruments = process_item(app.browser.instruments)
                    if instruments:
                        instruments["name"] = "Instruments"  # Ensure consistent naming
                        result["categories"].append(instruments)
                except Exception as e:
                    self.log_message("Error processing instruments: {0}".format(str(e)))
            
            if (category_type == "all" or category_type == "sounds") and hasattr(app.browser, 'sounds'):
                try:
                    sounds = process_item(app.browser.sounds)
                    if sounds:
                        sounds["name"] = "Sounds"  # Ensure consistent naming
                        result["categories"].append(sounds)
                except Exception as e:
                    self.log_message("Error processing sounds: {0}".format(str(e)))
            
            if (category_type == "all" or category_type == "drums") and hasattr(app.browser, 'drums'):
                try:
                    drums = process_item(app.browser.drums)
                    if drums:
                        drums["name"] = "Drums"  # Ensure consistent naming
                        result["categories"].append(drums)
                except Exception as e:
                    self.log_message("Error processing drums: {0}".format(str(e)))
            
            if (category_type == "all" or category_type == "audio_effects") and hasattr(app.browser, 'audio_effects'):
                try:
                    audio_effects = process_item(app.browser.audio_effects)
                    if audio_effects:
                        audio_effects["name"] = "Audio Effects"  # Ensure consistent naming
                        result["categories"].append(audio_effects)
                except Exception as e:
                    self.log_message("Error processing audio_effects: {0}".format(str(e)))
            
            if (category_type == "all" or category_type == "midi_effects") and hasattr(app.browser, 'midi_effects'):
                try:
                    midi_effects = process_item(app.browser.midi_effects)
                    if midi_effects:
                        midi_effects["name"] = "MIDI Effects"
                        result["categories"].append(midi_effects)
                except Exception as e:
                    self.log_message("Error processing midi_effects: {0}".format(str(e)))
            
            # Try to process other potentially available categories
            for attr in browser_attrs:
                if attr not in ['instruments', 'sounds', 'drums', 'audio_effects', 'midi_effects'] and \
                   (category_type == "all" or category_type == attr):
                    try:
                        item = getattr(app.browser, attr)
                        if hasattr(item, 'children') or hasattr(item, 'name'):
                            category = process_item(item)
                            if category:
                                category["name"] = attr.capitalize()
                                result["categories"].append(category)
                    except Exception as e:
                        self.log_message("Error processing {0}: {1}".format(attr, str(e)))
            
            self.log_message("Browser tree generated for {0} with {1} root categories".format(
                category_type, len(result['categories'])))
            return result
            
        except Exception as e:
            self.log_message("Error getting browser tree: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise
    
    def get_browser_items_at_path(self, path):
        """
        Get browser items at a specific path.
        
        Args:
            path: Path in the format "category/folder/subfolder"
                 where category is one of: instruments, sounds, drums, audio_effects, midi_effects
                 or any other available browser category
                 
        Returns:
            Dictionary with items at the specified path
        """
        try:
            # Access the application's browser instance instead of creating a new one
            app = self.application()
            if not app:
                raise RuntimeError("Could not access Live application")
                
            # Check if browser is available
            if not hasattr(app, 'browser') or app.browser is None:
                raise RuntimeError("Browser is not available in the Live application")
            
            # Log available browser attributes to help diagnose issues
            browser_attrs = [attr for attr in dir(app.browser) if not attr.startswith('_')]
            self.log_message("Available browser attributes: {0}".format(browser_attrs))
                
            # Parse the path
            path_parts = path.split("/")
            if not path_parts:
                raise ValueError("Invalid path")
            
            # Determine the root category
            root_category = path_parts[0].lower()
            current_item = None
            
            # Check standard categories first
            if root_category == "instruments" and hasattr(app.browser, 'instruments'):
                current_item = app.browser.instruments
            elif root_category == "sounds" and hasattr(app.browser, 'sounds'):
                current_item = app.browser.sounds
            elif root_category == "drums" and hasattr(app.browser, 'drums'):
                current_item = app.browser.drums
            elif root_category == "audio_effects" and hasattr(app.browser, 'audio_effects'):
                current_item = app.browser.audio_effects
            elif root_category == "midi_effects" and hasattr(app.browser, 'midi_effects'):
                current_item = app.browser.midi_effects
            else:
                # Try to find the category in other browser attributes
                found = False
                for attr in browser_attrs:
                    if attr.lower() == root_category:
                        try:
                            current_item = getattr(app.browser, attr)
                            found = True
                            break
                        except Exception as e:
                            self.log_message("Error accessing browser attribute {0}: {1}".format(attr, str(e)))
                
                if not found:
                    # If we still haven't found the category, return available categories
                    return {
                        "path": path,
                        "error": "Unknown or unavailable category: {0}".format(root_category),
                        "available_categories": browser_attrs,
                        "items": []
                    }
            
            # Navigate through the path
            for i in range(1, len(path_parts)):
                part = path_parts[i]
                if not part:  # Skip empty parts
                    continue
                
                if not hasattr(current_item, 'children'):
                    return {
                        "path": path,
                        "error": "Item at '{0}' has no children".format('/'.join(path_parts[:i])),
                        "items": []
                    }
                
                found = False
                for child in current_item.children:
                    if hasattr(child, 'name') and child.name.lower() == part.lower():
                        current_item = child
                        found = True
                        break
                
                if not found:
                    return {
                        "path": path,
                        "error": "Path part '{0}' not found".format(part),
                        "items": []
                    }
            
            # Get items at the current path
            items = []
            if hasattr(current_item, 'children'):
                for child in current_item.children:
                    item_info = {
                        "name": child.name if hasattr(child, 'name') else "Unknown",
                        "is_folder": hasattr(child, 'children') and bool(child.children),
                        "is_device": hasattr(child, 'is_device') and child.is_device,
                        "is_loadable": hasattr(child, 'is_loadable') and child.is_loadable,
                        "uri": child.uri if hasattr(child, 'uri') else None
                    }
                    items.append(item_info)
            
            result = {
                "path": path,
                "name": current_item.name if hasattr(current_item, 'name') else "Unknown",
                "uri": current_item.uri if hasattr(current_item, 'uri') else None,
                "is_folder": hasattr(current_item, 'children') and bool(current_item.children),
                "is_device": hasattr(current_item, 'is_device') and current_item.is_device,
                "is_loadable": hasattr(current_item, 'is_loadable') and current_item.is_loadable,
                "items": items
            }
            
            self.log_message("Retrieved {0} items at path: {1}".format(len(items), path))
            return result
            
        except Exception as e:
            self.log_message("Error getting browser items at path: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise
