"""
VRChat OSC Integration - Handles communication with VRChat via Open Sound Control
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from pythonosc import udp_client, dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.osc_message import OscMessage
import threading
import socket

from ..core.proximity_engine import UserPosition, ProximityEngine

logger = logging.getLogger(__name__)


@dataclass
class VRChatOSCConfig:
    """Configuration for VRChat OSC connection"""
    receive_port: int = 9001  # Port to receive data from VRChat
    send_port: int = 9000     # Port to send data to VRChat
    host: str = "127.0.0.1"   # VRChat host (usually localhost)
    enable_position_tracking: bool = True
    enable_avatar_parameters: bool = True
    parameter_prefix: str = "/avatar/parameters/"
    position_update_rate: float = 0.1  # How often to request position updates


class VRChatOSCClient:
    """Handles OSC communication with VRChat"""
    
    def __init__(self, config: VRChatOSCConfig, proximity_engine: ProximityEngine):
        self.config = config
        self.proximity_engine = proximity_engine
        
        # OSC client for sending data to VRChat
        self.client = udp_client.SimpleUDPClient(config.host, config.send_port)
        
        # OSC server for receiving data from VRChat
        self.dispatcher = dispatcher.Dispatcher()
        self.server: Optional[ThreadingOSCUDPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        
        # State tracking
        self.connected = False
        self.local_user_id: Optional[str] = None
        self.tracked_users: Dict[str, Dict[str, Any]] = {}
        self.last_position_request = 0.0
        
        # Callbacks
        self.position_callbacks: List[Callable] = []
        self.user_callbacks: List[Callable] = []
        self.parameter_callbacks: List[Callable] = []
        
        self._setup_osc_handlers()
    
    def _setup_osc_handlers(self):
        """Set up OSC message handlers"""
        # Avatar position tracking
        self.dispatcher.map("/tracking/head/position", self._handle_head_position)
        self.dispatcher.map("/tracking/head/rotation", self._handle_head_rotation)
        
        # User data
        self.dispatcher.map("/user/*/position", self._handle_user_position)
        self.dispatcher.map("/user/*/join", self._handle_user_join)
        self.dispatcher.map("/user/*/leave", self._handle_user_leave)
        
        # Avatar parameters
        self.dispatcher.map("/avatar/parameters/*", self._handle_avatar_parameter)
        
        # Instance/world info
        self.dispatcher.map("/instance/users", self._handle_instance_users)
        self.dispatcher.map("/world/scale", self._handle_world_scale)
        
        # Visibility control responses
        self.dispatcher.map("/visibility/*", self._handle_visibility_response)
        
        logger.info("OSC handlers configured")
    
    def _handle_head_position(self, address: str, *args):
        """Handle local user head position updates"""
        if len(args) >= 3:
            x, y, z = float(args[0]), float(args[1]), float(args[2])
            
            if self.local_user_id:
                position = UserPosition(
                    user_id=self.local_user_id,
                    username="LocalUser",
                    x=x, y=y, z=z,
                    timestamp=time.time()
                )
                self.proximity_engine.set_local_user_position(position)
                
                # Notify callbacks
                for callback in self.position_callbacks:
                    try:
                        callback(position)
                    except Exception as e:
                        logger.error(f"Error in position callback: {e}")
    
    def _handle_head_rotation(self, address: str, *args):
        """Handle local user head rotation updates"""
        if len(args) >= 4:  # Quaternion rotation
            # Convert quaternion to Y rotation for simplicity
            # This is a simplified conversion - in production, use proper quaternion math
            y_rotation = float(args[1])  # Approximate Y rotation from quaternion
            
            if self.local_user_id and self.proximity_engine.local_user:
                self.proximity_engine.local_user.rotation_y = y_rotation
    
    def _handle_user_position(self, address: str, *args):
        """Handle other users' position updates"""
        # Extract user ID from address like /user/usr_12345/position
        parts = address.split('/')
        if len(parts) >= 3 and len(args) >= 3:
            user_id = parts[2]
            x, y, z = float(args[0]), float(args[1]), float(args[2])
            
            username = self.tracked_users.get(user_id, {}).get('username', f'User_{user_id[:8]}')
            
            position = UserPosition(
                user_id=user_id,
                username=username,
                x=x, y=y, z=z,
                timestamp=time.time()
            )
            
            self.proximity_engine.update_user_position(position)
    
    def _handle_user_join(self, address: str, *args):
        """Handle user joining the instance"""
        parts = address.split('/')
        if len(parts) >= 3:
            user_id = parts[2]
            username = args[0] if args else f"User_{user_id[:8]}"
            
            self.tracked_users[user_id] = {
                'username': str(username),
                'join_time': time.time()
            }
            
            logger.info(f"User joined: {username} ({user_id})")
            
            # Notify callbacks
            for callback in self.user_callbacks:
                try:
                    callback('join', user_id, username)
                except Exception as e:
                    logger.error(f"Error in user callback: {e}")
    
    def _handle_user_leave(self, address: str, *args):
        """Handle user leaving the instance"""
        parts = address.split('/')
        if len(parts) >= 3:
            user_id = parts[2]
            username = self.tracked_users.get(user_id, {}).get('username', user_id)
            
            self.tracked_users.pop(user_id, None)
            self.proximity_engine.remove_user(user_id)
            
            logger.info(f"User left: {username} ({user_id})")
            
            # Notify callbacks
            for callback in self.user_callbacks:
                try:
                    callback('leave', user_id, username)
                except Exception as e:
                    logger.error(f"Error in user callback: {e}")
    
    def _handle_avatar_parameter(self, address: str, *args):
        """Handle avatar parameter updates"""
        if args:
            parameter_name = address.replace(self.config.parameter_prefix, "")
            value = args[0]
            
            # Notify callbacks
            for callback in self.parameter_callbacks:
                try:
                    callback(parameter_name, value)
                except Exception as e:
                    logger.error(f"Error in parameter callback: {e}")
    
    def _handle_instance_users(self, address: str, *args):
        """Handle instance user list updates"""
        if args:
            try:
                # Expecting JSON string with user list
                user_data = json.loads(str(args[0]))
                for user in user_data:
                    user_id = user.get('id')
                    username = user.get('displayName', f'User_{user_id[:8]}')
                    if user_id and user_id not in self.tracked_users:
                        self.tracked_users[user_id] = {
                            'username': username,
                            'join_time': time.time()
                        }
                        logger.info(f"Discovered existing user: {username} ({user_id})")
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error parsing instance users: {e}")
    
    def _handle_world_scale(self, address: str, *args):
        """Handle world scale updates"""
        if args:
            try:
                scale = float(args[0])
                self.proximity_engine.set_world_scale(scale)
                logger.info(f"World scale updated to: {scale}")
            except ValueError:
                logger.error(f"Invalid world scale value: {args[0]}")
    
    def _handle_visibility_response(self, address: str, *args):
        """Handle responses to visibility control commands"""
        logger.debug(f"Visibility response: {address} - {args}")
    
    async def connect(self):
        """Connect to VRChat OSC"""
        try:
            # Start OSC server for receiving data
            self.server = ThreadingOSCUDPServer(
                (self.config.host, self.config.receive_port),
                self.dispatcher
            )
            
            self.server_thread = threading.Thread(
                target=self.server.serve_forever,
                daemon=True
            )
            self.server_thread.start()
            
            # Test connection by sending a ping
            self.client.send_message("/ping", [time.time()])
            
            self.connected = True
            logger.info(f"Connected to VRChat OSC on {self.config.host}:{self.config.send_port}")
            logger.info(f"Listening on port {self.config.receive_port}")
            
            # Request initial data
            await self._request_initial_data()
            
        except Exception as e:
            logger.error(f"Failed to connect to VRChat OSC: {e}")
            self.connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from VRChat OSC"""
        self.connected = False
        
        if self.server:
            self.server.shutdown()
            self.server = None
        
        if self.server_thread:
            self.server_thread.join(timeout=5.0)
            self.server_thread = None
        
        logger.info("Disconnected from VRChat OSC")
    
    async def _request_initial_data(self):
        """Request initial data from VRChat"""
        current_time = time.time()
        
        # Request user list
        self.client.send_message("/instance/users/request", [])
        
        # Request world information
        self.client.send_message("/world/info/request", [])
        
        # Enable position tracking
        if self.config.enable_position_tracking:
            self.client.send_message("/tracking/enable", [True])
        
        self.last_position_request = current_time
        logger.info("Requested initial data from VRChat")
    
    def send_visibility_command(self, user_id: str, visible: bool, alpha: float = 1.0):
        """Send visibility control command to VRChat"""
        if not self.connected:
            return
        
        try:
            # Send visibility command
            self.client.send_message(f"/user/{user_id}/visible", [visible])
            
            # Send alpha/opacity if supported
            if visible and alpha < 1.0:
                self.client.send_message(f"/user/{user_id}/alpha", [alpha])
            
            logger.debug(f"Sent visibility command for {user_id}: visible={visible}, alpha={alpha}")
            
        except Exception as e:
            logger.error(f"Error sending visibility command: {e}")
    
    def set_avatar_parameter(self, parameter: str, value: Any):
        """Set an avatar parameter"""
        if not self.connected:
            return
        
        try:
            address = f"{self.config.parameter_prefix}{parameter}"
            self.client.send_message(address, [value])
            logger.debug(f"Set avatar parameter {parameter} = {value}")
        except Exception as e:
            logger.error(f"Error setting avatar parameter: {e}")
    
    def register_position_callback(self, callback: Callable):
        """Register a callback for position updates"""
        self.position_callbacks.append(callback)
    
    def register_user_callback(self, callback: Callable):
        """Register a callback for user join/leave events"""
        self.user_callbacks.append(callback)
    
    def register_parameter_callback(self, callback: Callable):
        """Register a callback for avatar parameter changes"""
        self.parameter_callbacks.append(callback)
    
    def set_local_user_id(self, user_id: str):
        """Set the local user ID"""
        self.local_user_id = user_id
        logger.info(f"Set local user ID: {user_id}")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        return {
            'connected': self.connected,
            'local_user_id': self.local_user_id,
            'tracked_users_count': len(self.tracked_users),
            'server_running': self.server is not None,
            'config': asdict(self.config)
        }
    
    async def update_loop(self):
        """Main update loop for OSC operations"""
        while self.connected:
            try:
                current_time = time.time()
                
                # Request position updates periodically
                if (self.config.enable_position_tracking and 
                    current_time - self.last_position_request > self.config.position_update_rate):
                    
                    # Request position data for all tracked users
                    for user_id in self.tracked_users.keys():
                        self.client.send_message(f"/user/{user_id}/position/request", [])
                    
                    self.last_position_request = current_time
                
                await asyncio.sleep(0.1)  # Small sleep to prevent overwhelming
                
            except Exception as e:
                logger.error(f"Error in OSC update loop: {e}")
                await asyncio.sleep(1.0)


class VRChatIntegration:
    """High-level VRChat integration wrapper"""
    
    def __init__(self, proximity_engine: ProximityEngine, config: Optional[VRChatOSCConfig] = None):
        self.proximity_engine = proximity_engine
        self.config = config or VRChatOSCConfig()
        self.osc_client = VRChatOSCClient(self.config, proximity_engine)
        
        # Set up visibility callback
        self.proximity_engine.register_visibility_callback(self._on_visibility_change)
        
        self.running = False
        self.update_task: Optional[asyncio.Task] = None
    
    async def _on_visibility_change(self, visibility_states: Dict[str, Any]):
        """Handle visibility state changes from proximity engine"""
        for user_id, vis in visibility_states.items():
            visible = vis.visibility_alpha > 0.0
            alpha = vis.visibility_alpha
            
            self.osc_client.send_visibility_command(user_id, visible, alpha)
    
    async def start(self):
        """Start VRChat integration"""
        if self.running:
            return
        
        try:
            await self.osc_client.connect()
            self.update_task = asyncio.create_task(self.osc_client.update_loop())
            self.running = True
            logger.info("VRChat integration started")
        except Exception as e:
            logger.error(f"Failed to start VRChat integration: {e}")
            raise
    
    async def stop(self):
        """Stop VRChat integration"""
        self.running = False
        
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
        
        await self.osc_client.disconnect()
        logger.info("VRChat integration stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        osc_status = self.osc_client.get_connection_status()
        
        return {
            'running': self.running,
            'osc': osc_status,
            'proximity_engine': self.proximity_engine.get_stats()
        }
