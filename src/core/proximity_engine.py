"""
VRChat Proximity Engine - Core proximity detection and visibility management system
"""

import asyncio
import time
import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import logging

logger = logging.getLogger(__name__)


class VisibilityState(Enum):
    """Enumeration for user visibility states"""
    HIDDEN = "hidden"
    FADING_IN = "fading_in" 
    VISIBLE = "visible"
    FADING_OUT = "fading_out"


@dataclass
class UserPosition:
    """Represents a user's position and related data in 3D space"""
    user_id: str
    username: str
    x: float
    y: float
    z: float
    rotation_y: float = 0.0
    timestamp: float = field(default_factory=time.time)
    
    def distance_to(self, other: 'UserPosition') -> float:
        """Calculate 3D Euclidean distance to another user"""
        return math.sqrt(
            (self.x - other.x) ** 2 +
            (self.y - other.y) ** 2 + 
            (self.z - other.z) ** 2
        )
    
    def distance_to_2d(self, other: 'UserPosition') -> float:
        """Calculate 2D distance (ignoring Y axis) to another user"""
        return math.sqrt(
            (self.x - other.x) ** 2 +
            (self.z - other.z) ** 2
        )
    
    def is_stale(self, max_age: float = 5.0) -> bool:
        """Check if position data is too old to be reliable"""
        return (time.time() - self.timestamp) > max_age


@dataclass
class VisibilitySettings:
    """User-configurable visibility settings"""
    sight_distance: float = 10.0  # Base sight distance in meters
    fade_distance: float = 2.0    # Distance over which users fade in/out
    use_vertical_distance: bool = True  # Include Y-axis in calculations
    fade_duration: float = 1.0    # Time for fade transitions in seconds
    update_rate: float = 0.1      # Update frequency in seconds
    enable_distance_scaling: bool = True  # Scale based on world size
    distance_multiplier: float = 1.0     # Global distance multiplier
    
    def get_effective_sight_distance(self, world_scale: float = 1.0) -> float:
        """Get the effective sight distance considering world scale"""
        base_distance = self.sight_distance * self.distance_multiplier
        if self.enable_distance_scaling:
            return base_distance * world_scale
        return base_distance
    
    def get_fade_start_distance(self, world_scale: float = 1.0) -> float:
        """Get the distance at which fading starts"""
        sight_dist = self.get_effective_sight_distance(world_scale)
        return sight_dist - self.fade_distance


@dataclass
class UserVisibility:
    """Tracks visibility state for a specific user"""
    user_id: str
    state: VisibilityState = VisibilityState.HIDDEN
    visibility_alpha: float = 0.0  # 0.0 = invisible, 1.0 = fully visible
    distance: float = float('inf')
    fade_start_time: float = 0.0
    last_update: float = field(default_factory=time.time)


class ProximityEngine:
    """Core engine for managing proximity-based visibility"""
    
    def __init__(self, settings: VisibilitySettings):
        self.settings = settings
        self.local_user: Optional[UserPosition] = None
        self.users: Dict[str, UserPosition] = {}
        self.visibility_states: Dict[str, UserVisibility] = {}
        self.world_scale: float = 1.0
        self.running = False
        self.update_task: Optional[asyncio.Task] = None
        self._callbacks: List = []
        
    def register_visibility_callback(self, callback):
        """Register a callback to be called when visibility states change"""
        self._callbacks.append(callback)
    
    def set_local_user_position(self, position: UserPosition):
        """Update the local user's position"""
        self.local_user = position
        logger.debug(f"Updated local user position: {position.x:.2f}, {position.y:.2f}, {position.z:.2f}")
    
    def update_user_position(self, position: UserPosition):
        """Update or add a user's position"""
        self.users[position.user_id] = position
        
        # Initialize visibility state if new user
        if position.user_id not in self.visibility_states:
            self.visibility_states[position.user_id] = UserVisibility(
                user_id=position.user_id
            )
        
        logger.debug(f"Updated user {position.username} position: {position.x:.2f}, {position.y:.2f}, {position.z:.2f}")
    
    def remove_user(self, user_id: str):
        """Remove a user from tracking"""
        self.users.pop(user_id, None)
        self.visibility_states.pop(user_id, None)
        logger.info(f"Removed user {user_id} from tracking")
    
    def set_world_scale(self, scale: float):
        """Set the world scale factor for distance calculations"""
        self.world_scale = scale
        logger.info(f"Updated world scale to {scale}")
    
    def update_settings(self, settings: VisibilitySettings):
        """Update visibility settings"""
        self.settings = settings
        logger.info("Updated visibility settings")
    
    def calculate_distance(self, user_pos: UserPosition) -> float:
        """Calculate distance between local user and another user"""
        if not self.local_user:
            return float('inf')
        
        if self.settings.use_vertical_distance:
            return self.local_user.distance_to(user_pos)
        else:
            return self.local_user.distance_to_2d(user_pos)
    
    def update_visibility_state(self, user_id: str, distance: float) -> bool:
        """Update visibility state for a user based on distance. Returns True if state changed."""
        if user_id not in self.visibility_states:
            return False
        
        vis = self.visibility_states[user_id]
        old_state = vis.state
        old_alpha = vis.visibility_alpha
        
        current_time = time.time()
        sight_distance = self.settings.get_effective_sight_distance(self.world_scale)
        fade_start_distance = self.settings.get_fade_start_distance(self.world_scale)
        
        vis.distance = distance
        vis.last_update = current_time
        
        # Determine target state based on distance
        if distance <= fade_start_distance:
            target_state = VisibilityState.VISIBLE
            target_alpha = 1.0
        elif distance <= sight_distance:
            # In fade zone
            fade_progress = (sight_distance - distance) / self.settings.fade_distance
            target_alpha = max(0.0, min(1.0, fade_progress))
            if vis.state in [VisibilityState.HIDDEN, VisibilityState.FADING_IN]:
                target_state = VisibilityState.FADING_IN
            else:
                target_state = VisibilityState.FADING_OUT
        else:
            target_state = VisibilityState.HIDDEN
            target_alpha = 0.0
        
        # Handle state transitions
        if vis.state != target_state:
            vis.state = target_state
            vis.fade_start_time = current_time
            
        # Update alpha based on fade duration
        if target_state in [VisibilityState.FADING_IN, VisibilityState.FADING_OUT]:
            fade_elapsed = current_time - vis.fade_start_time
            fade_ratio = min(1.0, fade_elapsed / self.settings.fade_duration)
            
            if target_state == VisibilityState.FADING_IN:
                vis.visibility_alpha = fade_ratio * target_alpha
            else:  # FADING_OUT
                vis.visibility_alpha = (1.0 - fade_ratio) * target_alpha
            
            # Check if fade is complete
            if fade_ratio >= 1.0:
                if target_state == VisibilityState.FADING_IN:
                    vis.state = VisibilityState.VISIBLE
                else:
                    vis.state = VisibilityState.HIDDEN
                vis.visibility_alpha = target_alpha
        else:
            vis.visibility_alpha = target_alpha
        
        # Return True if state or alpha changed significantly
        return (old_state != vis.state or 
                abs(old_alpha - vis.visibility_alpha) > 0.01)
    
    async def update_loop(self):
        """Main update loop for proximity calculations"""
        logger.info("Starting proximity engine update loop")
        
        while self.running:
            try:
                if self.local_user:
                    changes_detected = False
                    
                    # Remove stale users
                    stale_users = [
                        user_id for user_id, pos in self.users.items()
                        if pos.is_stale()
                    ]
                    for user_id in stale_users:
                        self.remove_user(user_id)
                        changes_detected = True
                    
                    # Update visibility for all users
                    for user_id, user_pos in self.users.items():
                        if not user_pos.is_stale():
                            distance = self.calculate_distance(user_pos)
                            if self.update_visibility_state(user_id, distance):
                                changes_detected = True
                    
                    # Notify callbacks of changes
                    if changes_detected:
                        for callback in self._callbacks:
                            try:
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(self.visibility_states)
                                else:
                                    callback(self.visibility_states)
                            except Exception as e:
                                logger.error(f"Error in visibility callback: {e}")
                
                await asyncio.sleep(self.settings.update_rate)
                
            except Exception as e:
                logger.error(f"Error in proximity update loop: {e}")
                await asyncio.sleep(1.0)  # Longer sleep on error
    
    async def start(self):
        """Start the proximity engine"""
        if self.running:
            return
        
        self.running = True
        self.update_task = asyncio.create_task(self.update_loop())
        logger.info("Proximity engine started")
    
    async def stop(self):
        """Stop the proximity engine"""
        self.running = False
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
        logger.info("Proximity engine stopped")
    
    def get_visible_users(self) -> Dict[str, UserVisibility]:
        """Get all users that are currently visible (alpha > 0)"""
        return {
            user_id: vis for user_id, vis in self.visibility_states.items()
            if vis.visibility_alpha > 0.0
        }
    
    def get_user_visibility(self, user_id: str) -> Optional[UserVisibility]:
        """Get visibility state for a specific user"""
        return self.visibility_states.get(user_id)
    
    def get_stats(self) -> Dict:
        """Get current engine statistics"""
        visible_count = len(self.get_visible_users())
        total_users = len(self.users)
        
        return {
            'total_users': total_users,
            'visible_users': visible_count,
            'hidden_users': total_users - visible_count,
            'sight_distance': self.settings.get_effective_sight_distance(self.world_scale),
            'world_scale': self.world_scale,
            'update_rate': self.settings.update_rate,
            'local_user_set': self.local_user is not None
        }


# Utility functions for distance calculations and optimizations
def batch_distance_calculation(local_pos: UserPosition, 
                             user_positions: List[UserPosition], 
                             use_vertical: bool = True) -> np.ndarray:
    """Efficiently calculate distances to multiple users using numpy"""
    if not user_positions:
        return np.array([])
    
    # Create position arrays
    local_array = np.array([local_pos.x, local_pos.y, local_pos.z])
    user_array = np.array([[pos.x, pos.y, pos.z] for pos in user_positions])
    
    if not use_vertical:
        # Zero out Y component for 2D distance
        local_array[1] = 0
        user_array[:, 1] = 0
    
    # Calculate all distances at once
    differences = user_array - local_array
    distances = np.linalg.norm(differences, axis=1)
    
    return distances
