"""
Enhanced Ableton Live Integration for Chat-leton GPT

Real-time connection monitoring, MIDI generation, and bi-directional communication
with Ableton Live through the existing MCP Remote Script.
"""

import asyncio
import json
import logging
import socket
import time
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
import queue

logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    """Ableton connection status states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting" 
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


@dataclass
class AbletonState:
    """Current Ableton Live session state"""
    is_playing: bool = False
    tempo: float = 120.0
    time_signature: Tuple[int, int] = (4, 4)
    current_song_time: float = 0.0
    track_count: int = 0
    scene_count: int = 0
    current_track_index: int = -1
    current_scene_index: int = -1
    tracks: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class GenerationAction:
    """Represents an action to be performed in Ableton"""
    action_type: str
    params: Dict[str, Any]
    description: str
    estimated_duration: float = 1.0
    callback: Optional[Callable] = None


class EnhancedAbletonIntegration:
    """
    Enhanced Ableton Live integration with real-time monitoring and generation
    """
    
    def __init__(self, host: str = "localhost", port: int = 11999):
        """Initialize the enhanced Ableton integration"""
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None
        self.status = ConnectionStatus.DISCONNECTED
        self.state = AbletonState()
        
        # Monitoring and feedback
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.status_callbacks: List[Callable] = []
        self.action_queue = queue.Queue()
        
        # Connection management
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 2.0
        
        # Generation tracking
        self.pending_actions: List[GenerationAction] = []
        self.completed_actions: List[GenerationAction] = []
        
        logger.info("Enhanced Ableton Integration initialized")
    
    # ========================================================================
    # CONNECTION MANAGEMENT
    # ========================================================================
    
    async def connect(self) -> bool:
        """Connect to Ableton Live with enhanced error handling"""
        if self.status == ConnectionStatus.CONNECTED:
            return True
        
        self.status = ConnectionStatus.CONNECTING
        self._notify_status_change()
        
        try:
            logger.info(f"Connecting to Ableton Live at {self.host}:{self.port}")
            
            # Create socket with timeout
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10.0)
            
            # Connect
            self.sock.connect((self.host, self.port))
            
            # Test connection with a simple command
            test_response = await self._send_command_async("get_session_info")
            
            if test_response and test_response.get("status") == "success":
                self.status = ConnectionStatus.CONNECTED
                self.reconnect_attempts = 0
                logger.info("✅ Successfully connected to Ableton Live")
                
                # Update initial state
                await self._update_session_state(test_response.get("result", {}))
                
                # Start monitoring if not already active
                if not self.monitoring_active:
                    self.start_monitoring()
                
                self._notify_status_change()
                return True
            else:
                raise Exception("Failed to get valid response from Ableton")
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to Ableton: {e}")
            self.status = ConnectionStatus.ERROR
            self.sock = None
            self._notify_status_change()
            return False
    
    def disconnect(self):
        """Disconnect from Ableton Live"""
        logger.info("Disconnecting from Ableton Live")
        
        # Stop monitoring
        self.stop_monitoring()
        
        # Close socket
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                logger.warning(f"Error closing socket: {e}")
            finally:
                self.sock = None
        
        self.status = ConnectionStatus.DISCONNECTED
        self._notify_status_change()
    
    async def ensure_connection(self) -> bool:
        """Ensure we have a valid connection, reconnect if needed"""
        if self.status == ConnectionStatus.CONNECTED and self.sock:
            # Test connection
            try:
                test_response = await self._send_command_async("get_session_info", timeout=3.0)
                if test_response and test_response.get("status") == "success":
                    return True
            except Exception:
                pass
        
        # Connection is not valid, try to reconnect
        return await self.connect()
    
    async def reconnect(self) -> bool:
        """Reconnect to Ableton with retry logic"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error("❌ Max reconnection attempts reached")
            self.status = ConnectionStatus.ERROR
            self._notify_status_change()
            return False
        
        self.status = ConnectionStatus.RECONNECTING
        self.reconnect_attempts += 1
        self._notify_status_change()
        
        logger.info(f"🔄 Reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
        
        # Wait before reconnecting
        await asyncio.sleep(self.reconnect_delay)
        
        # Try to connect
        if await self.connect():
            return True
        
        # Failed, try again
        return await self.reconnect()
    
    # ========================================================================
    # COMMAND EXECUTION
    # ========================================================================
    
    async def _send_command_async(self, command_type: str, params: Dict[str, Any] = None, timeout: float = 15.0) -> Dict[str, Any]:
        """Send command to Ableton asynchronously with timeout"""
        if not self.sock:
            raise ConnectionError("Not connected to Ableton")
        
        command = {
            "type": command_type,
            "params": params or {}
        }
        
        try:
            # Send command
            command_json = json.dumps(command)
            logger.debug(f"🎛️ Sending: {command_type}")
            
            self.sock.sendall(command_json.encode('utf-8'))
            
            # Set timeout and receive response
            self.sock.settimeout(timeout)
            
            # Receive response in chunks
            response_data = await self._receive_response_async()
            
            # Parse response
            response = json.loads(response_data.decode('utf-8'))
            
            if response.get("status") == "error":
                raise Exception(response.get("message", "Unknown Ableton error"))
            
            logger.debug(f"✅ Response: {command_type} success")
            return response
            
        except socket.timeout:
            logger.error(f"⏰ Timeout sending {command_type}")
            raise Exception(f"Timeout executing {command_type}")
        except Exception as e:
            logger.error(f"❌ Error sending {command_type}: {e}")
            raise Exception(f"Failed to execute {command_type}: {str(e)}")
    
    async def _receive_response_async(self, buffer_size: int = 8192) -> bytes:
        """Receive complete response asynchronously"""
        chunks = []
        
        while True:
            chunk = self.sock.recv(buffer_size)
            if not chunk:
                break
            
            chunks.append(chunk)
            
            # Check if we have complete JSON
            try:
                data = b''.join(chunks)
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                continue
        
        if chunks:
            return b''.join(chunks)
        else:
            raise Exception("No data received from Ableton")
    
    # ========================================================================
    # HIGH-LEVEL MUSIC GENERATION
    # ========================================================================
    
    async def generate_track_from_brief(self, brief: Dict[str, Any], progress_callback: Callable = None) -> List[GenerationAction]:
        """
        Generate a complete track in Ableton from a creative brief
        
        Args:
            brief: Creative brief with style, bpm, key, elements, etc.
            progress_callback: Function to call with progress updates
            
        Returns:
            List of completed actions
        """
        logger.info(f"🎵 Generating track: {brief.get('style', 'Unknown')} at {brief.get('bpm', 120)} BPM")
        
        # Ensure connection
        if not await self.ensure_connection():
            raise Exception("Could not connect to Ableton Live")
        
        actions = []
        
        try:
            # 1. Set basic project settings
            if progress_callback:
                progress_callback("Setting project parameters...", 0.1)
            
            # Set BPM
            if brief.get('bpm'):
                action = await self._create_action("set_tempo", {"tempo": brief['bpm']}, 
                                                 f"Set BPM to {brief['bpm']}")
                actions.append(action)
            
            # 2. Create tracks for each element
            if progress_callback:
                progress_callback("Creating tracks...", 0.2)
            
            track_elements = brief.get('track_elements', ['kick', 'bass', 'hi_hats'])
            
            for i, element in enumerate(track_elements):
                track_name = f"{brief.get('style', 'Track')} {element.title()}"
                action = await self._create_action("create_midi_track", {"name": track_name}, 
                                                 f"Create {element} track")
                actions.append(action)
                
                if progress_callback:
                    progress = 0.2 + (0.4 * (i + 1) / len(track_elements))
                    progress_callback(f"Created {element} track", progress)
            
            # 3. Generate MIDI content
            if progress_callback:
                progress_callback("Generating MIDI content...", 0.6)
            
            await self._generate_midi_content(brief, actions, progress_callback)
            
            # 4. Apply plugin recommendations  
            if progress_callback:
                progress_callback("Applying plugins and effects...", 0.8)
            
            await self._apply_plugin_recommendations(brief, actions)
            
            # 5. Final adjustments
            if progress_callback:
                progress_callback("Finalizing arrangement...", 0.9)
            
            await self._finalize_arrangement(brief, actions)
            
            if progress_callback:
                progress_callback("Track generation complete!", 1.0)
            
            logger.info(f"✅ Track generation complete: {len(actions)} actions performed")
            return actions
            
        except Exception as e:
            logger.error(f"❌ Track generation failed: {e}")
            raise Exception(f"Track generation failed: {str(e)}")
    
    async def _create_action(self, action_type: str, params: Dict[str, Any], description: str) -> GenerationAction:
        """Create and execute a generation action"""
        action = GenerationAction(
            action_type=action_type,
            params=params,
            description=description
        )
        
        try:
            # Execute the action
            start_time = time.time()
            response = await self._send_command_async(action_type, params)
            duration = time.time() - start_time
            
            action.estimated_duration = duration
            self.completed_actions.append(action)
            
            logger.info(f"✅ {description} (took {duration:.2f}s)")
            return action
            
        except Exception as e:
            logger.error(f"❌ Failed: {description} - {e}")
            raise
    
    async def _generate_midi_content(self, brief: Dict[str, Any], actions: List[GenerationAction], progress_callback: Callable = None):
        """Generate MIDI content based on the brief"""
        style = brief.get('style', 'house')
        key = brief.get('key', 'C')
        bpm = brief.get('bpm', 120)
        
        # Basic MIDI patterns based on style
        patterns = self._get_style_patterns(style, key, bpm)
        
        # Get current tracks
        session_info = await self._send_command_async("get_session_info")
        tracks = session_info.get("result", {}).get("tracks", [])
        
        for i, track in enumerate(tracks[-len(brief.get('track_elements', [])):]): # Get recently created tracks
            track_index = track.get("index", i)
            element_name = brief.get('track_elements', ['element'])[i] if i < len(brief.get('track_elements', [])) else 'element'
            
            if element_name in patterns:
                # Create clip
                clip_action = await self._create_action(
                    "create_clip",
                    {"track_index": track_index, "clip_slot": 0, "length": 4.0},
                    f"Create {element_name} clip"
                )
                actions.append(clip_action)
                
                # Add MIDI notes
                notes = patterns[element_name]
                if notes:
                    notes_action = await self._create_action(
                        "add_notes_to_clip",
                        {
                            "track_index": track_index,
                            "clip_slot": 0,
                            "notes": notes
                        },
                        f"Add {element_name} MIDI pattern"
                    )
                    actions.append(notes_action)
            
            if progress_callback:
                progress = 0.6 + (0.2 * (i + 1) / len(tracks))
                progress_callback(f"Generated {element_name} MIDI", progress)
    
    def _get_style_patterns(self, style: str, key: str = "C", bpm: int = 120) -> Dict[str, List[Dict]]:
        """Get MIDI patterns for a specific style"""
        
        # Convert key to MIDI note (C=60, C#=61, etc.)
        key_offset = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4,
            'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9,
            'A#': 10, 'Bb': 10, 'B': 11
        }.get(key, 0)
        
        base_note = 60 + key_offset  # Middle C + key offset
        
        patterns = {
            "kick": [
                {"pitch": 36, "start": 0.0, "duration": 0.25, "velocity": 100},  # Beat 1
                {"pitch": 36, "start": 1.0, "duration": 0.25, "velocity": 90},   # Beat 2
                {"pitch": 36, "start": 2.0, "duration": 0.25, "velocity": 100},  # Beat 3
                {"pitch": 36, "start": 3.0, "duration": 0.25, "velocity": 90},   # Beat 4
            ],
            "bass": [
                {"pitch": base_note - 24, "start": 0.0, "duration": 0.5, "velocity": 80},   # Root note
                {"pitch": base_note - 19, "start": 1.0, "duration": 0.5, "velocity": 75},   # Fifth
                {"pitch": base_note - 24, "start": 2.0, "duration": 0.5, "velocity": 80},   # Root
                {"pitch": base_note - 17, "start": 3.0, "duration": 0.5, "velocity": 75},   # Seventh
            ],
            "hi_hats": [
                {"pitch": 42, "start": 0.5, "duration": 0.125, "velocity": 60},   # Off-beat
                {"pitch": 42, "start": 1.5, "duration": 0.125, "velocity": 60},   # Off-beat
                {"pitch": 42, "start": 2.5, "duration": 0.125, "velocity": 60},   # Off-beat
                {"pitch": 42, "start": 3.5, "duration": 0.125, "velocity": 60},   # Off-beat
            ]
        }
        
        # Style-specific modifications
        if style == "afro_house":
            # Add syncopated kick pattern
            patterns["kick"].append({"pitch": 36, "start": 1.75, "duration": 0.25, "velocity": 70})
            
        elif style == "progressive_house":
            # Simpler, more driving pattern
            patterns["kick"] = [
                {"pitch": 36, "start": 0.0, "duration": 0.25, "velocity": 100},
                {"pitch": 36, "start": 1.0, "duration": 0.25, "velocity": 100}, 
                {"pitch": 36, "start": 2.0, "duration": 0.25, "velocity": 100},
                {"pitch": 36, "start": 3.0, "duration": 0.25, "velocity": 100},
            ]
        
        return patterns
    
    async def _apply_plugin_recommendations(self, brief: Dict[str, Any], actions: List[GenerationAction]):
        """Apply plugin recommendations based on the brief"""
        # This would integrate with our StockPluginExpert
        # For now, just log what we would do
        style = brief.get('style', 'house')
        logger.info(f"🎛️ Would apply {style} plugin recommendations")
        
        # TODO: Integrate with StockPluginExpert to get actual plugin settings
        # and load them into Ableton
    
    async def _finalize_arrangement(self, brief: Dict[str, Any], actions: List[GenerationAction]):
        """Finalize the arrangement"""
        # Set project to loop the created clips
        logger.info("🎼 Finalizing arrangement")
        
        # TODO: Set up arrangement view, loop points, etc.
    
    # ========================================================================
    # STATE MONITORING
    # ========================================================================
    
    def start_monitoring(self):
        """Start monitoring Ableton state in background"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("🔍 Started Ableton state monitoring")
    
    def stop_monitoring(self):
        """Stop monitoring Ableton state"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        logger.info("⏹️ Stopped Ableton state monitoring")
    
    def _monitor_loop(self):
        """Background thread for monitoring Ableton state"""
        while self.monitoring_active:
            try:
                if self.status == ConnectionStatus.CONNECTED and self.sock:
                    # Get current session info
                    response = self._send_command_sync("get_session_info")
                    if response and response.get("status") == "success":
                        asyncio.run(self._update_session_state(response.get("result", {})))
                
                time.sleep(1.0)  # Check every second
                
            except Exception as e:
                logger.debug(f"Monitor loop error: {e}")
                time.sleep(2.0)  # Wait longer on error
    
    def _send_command_sync(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Synchronous version for background thread"""
        if not self.sock:
            return None
        
        try:
            command = {"type": command_type, "params": params or {}}
            self.sock.sendall(json.dumps(command).encode('utf-8'))
            
            self.sock.settimeout(5.0)
            chunks = []
            
            while True:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
                
                try:
                    data = b''.join(chunks)
                    return json.loads(data.decode('utf-8'))
                except json.JSONDecodeError:
                    continue
                    
        except Exception:
            return None
    
    async def _update_session_state(self, session_data: Dict[str, Any]):
        """Update internal session state and notify callbacks"""
        try:
            # Update state
            self.state.is_playing = session_data.get("is_playing", False)
            self.state.tempo = session_data.get("tempo", 120.0)
            self.state.current_song_time = session_data.get("current_song_time", 0.0)
            self.state.track_count = len(session_data.get("tracks", []))
            self.state.scene_count = len(session_data.get("scenes", []))
            self.state.tracks = session_data.get("tracks", [])
            self.state.last_updated = datetime.now()
            
            # Notify state change
            self._notify_state_change()
            
        except Exception as e:
            logger.error(f"Error updating session state: {e}")
    
    # ========================================================================
    # CALLBACKS AND NOTIFICATIONS
    # ========================================================================
    
    def add_status_callback(self, callback: Callable):
        """Add callback for connection status changes"""
        self.status_callbacks.append(callback)
    
    def remove_status_callback(self, callback: Callable):
        """Remove status callback"""
        if callback in self.status_callbacks:
            self.status_callbacks.remove(callback)
    
    def _notify_status_change(self):
        """Notify all callbacks of status change"""
        for callback in self.status_callbacks:
            try:
                callback(self.status, self.state)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")
    
    def _notify_state_change(self):
        """Notify callbacks of state change"""
        # For now, same as status change
        # Could be separate in the future
        pass
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get current connection information"""
        return {
            "status": self.status.value,
            "host": self.host,
            "port": self.port,
            "reconnect_attempts": self.reconnect_attempts,
            "monitoring_active": self.monitoring_active,
            "last_updated": self.state.last_updated.isoformat() if self.state.last_updated else None
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current Ableton session"""
        return {
            "is_playing": self.state.is_playing,
            "tempo": self.state.tempo,
            "track_count": self.state.track_count,
            "scene_count": self.state.scene_count,
            "current_song_time": self.state.current_song_time,
            "tracks": [
                {
                    "name": track.get("name", f"Track {track.get('index', 0)}"),
                    "type": track.get("type", "unknown"),
                    "is_armed": track.get("is_armed", False),
                    "is_muted": track.get("is_muted", False)
                }
                for track in self.state.tracks
            ]
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection and return diagnostic info"""
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "host": self.host,
            "port": self.port,
            "socket_test": False,
            "command_test": False,
            "session_info": None,
            "error": None
        }
        
        try:
            # Test socket connection
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.settimeout(5.0)
            test_sock.connect((self.host, self.port))
            test_sock.close()
            test_results["socket_test"] = True
            
            # Test command execution
            if await self.ensure_connection():
                response = await self._send_command_async("get_session_info", timeout=5.0)
                if response and response.get("status") == "success":
                    test_results["command_test"] = True
                    test_results["session_info"] = response.get("result")
                    
        except Exception as e:
            test_results["error"] = str(e)
        
        return test_results 