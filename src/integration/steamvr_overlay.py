"""
SteamVR Overlay Integration - Provides in-VR interface for proximity controls
"""

import logging
import asyncio
import time
import ctypes
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass
import numpy as np

try:
    import openvr
    VR_AVAILABLE = True
except ImportError:
    VR_AVAILABLE = False
    openvr = None

from ..core.proximity_engine import ProximityEngine, VisibilitySettings
from ..config.settings import VRSettings

logger = logging.getLogger(__name__)


@dataclass
class OverlaySettings:
    """Settings for VR overlay configuration"""
    width_meters: float = 0.3
    distance_meters: float = 1.0
    alpha: float = 0.8
    anchor_type: str = "world"  # "world", "hand_left", "hand_right", "dashboard"
    auto_show_distance: float = 0.5  # Auto-show overlay when controllers are close


class SteamVROverlay:
    """SteamVR overlay for in-VR proximity controls"""
    
    def __init__(self, proximity_engine: ProximityEngine, vr_settings: VRSettings):
        self.proximity_engine = proximity_engine
        self.vr_settings = vr_settings
        
        # VR system state
        self.vr_system: Optional[Any] = None
        self.overlay_handle: Optional[int] = None
        self.is_initialized = False
        self.is_visible = False
        
        # Controller tracking
        self.controller_indices: Dict[str, int] = {}  # left/right -> device index
        self.controller_poses: Dict[int, Any] = {}
        self.last_button_states: Dict[int, Dict[str, bool]] = {}
        
        # Overlay content
        self.overlay_texture: Optional[Any] = None
        self.content_needs_update = True
        
        # Settings control
        self.sight_distance = 10.0
        self.fade_distance = 2.0
        self.ui_mode = "sliders"  # "sliders", "presets", "status"
        
        # Callbacks
        self.settings_change_callbacks: List[Callable] = []
        
    def initialize(self) -> bool:
        """Initialize SteamVR and create overlay"""
        if not VR_AVAILABLE:
            logger.error("OpenVR not available - VR overlay disabled")
            return False
        
        try:
            # Initialize OpenVR
            openvr.init(openvr.VRApplication_Overlay)
            self.vr_system = openvr.VRSystem()
            
            if not self.vr_system:
                logger.error("Failed to initialize VR system")
                return False
            
            # Create overlay
            overlay_key = "vrchat.proximity.control"
            overlay_name = "VRChat Proximity Controls"
            
            error, self.overlay_handle = openvr.VROverlay().createOverlay(overlay_key, overlay_name)
            if error != openvr.VROverlayError_None:
                logger.error(f"Failed to create VR overlay: {error}")
                return False
            
            # Configure overlay properties
            overlay = openvr.VROverlay()
            
            # Set overlay size
            overlay.setOverlayWidthInMeters(self.overlay_handle, self.vr_settings.overlay_width)
            
            # Set overlay alpha
            overlay.setOverlayAlpha(self.overlay_handle, self.vr_settings.overlay_alpha)
            
            # Set overlay color (white by default)
            overlay.setOverlayColor(self.overlay_handle, 1.0, 1.0, 1.0)
            
            # Enable mouse interaction
            overlay.setOverlayFlag(self.overlay_handle, openvr.VROverlayFlags_SendVRSmoothScrollEvents, True)
            overlay.setOverlayFlag(self.overlay_handle, openvr.VROverlayFlags_SendVRTouchpadEvents, True)
            
            # Set input method
            overlay.setOverlayInputMethod(self.overlay_handle, openvr.VROverlayInputMethod_Mouse)
            
            # Find controllers
            self._detect_controllers()
            
            # Create initial overlay texture
            self._create_overlay_texture()
            
            self.is_initialized = True
            logger.info("SteamVR overlay initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize SteamVR overlay: {e}")
            return False
    
    def shutdown(self):
        """Shutdown VR overlay and cleanup"""
        try:
            if self.overlay_handle is not None:
                openvr.VROverlay().destroyOverlay(self.overlay_handle)
                self.overlay_handle = None
            
            if VR_AVAILABLE and self.vr_system:
                openvr.shutdown()
                self.vr_system = None
            
            self.is_initialized = False
            logger.info("SteamVR overlay shutdown")
            
        except Exception as e:
            logger.error(f"Error shutting down VR overlay: {e}")
    
    def _detect_controllers(self):
        """Detect and track VR controllers"""
        if not self.vr_system:
            return
        
        self.controller_indices.clear()
        
        # Scan for controller devices
        for device_id in range(openvr.k_unMaxTrackedDeviceCount):
            device_class = self.vr_system.getTrackedDeviceClass(device_id)
            
            if device_class == openvr.TrackedDeviceClass_Controller:
                # Determine if it's left or right controller
                role = self.vr_system.getControllerRoleForTrackedDeviceIndex(device_id)
                
                if role == openvr.TrackedControllerRole_LeftHand:
                    self.controller_indices["left"] = device_id
                    logger.info(f"Found left controller at device {device_id}")
                elif role == openvr.TrackedControllerRole_RightHand:
                    self.controller_indices["right"] = device_id
                    logger.info(f"Found right controller at device {device_id}")
        
        # Initialize button state tracking
        for device_id in self.controller_indices.values():
            self.last_button_states[device_id] = {}
    
    def _create_overlay_texture(self):
        """Create overlay texture with current UI content"""
        try:
            # Create a simple texture with current proximity settings
            # In a full implementation, this would render actual UI elements
            
            width, height = 512, 512
            
            # Create RGBA texture data
            texture_data = np.zeros((height, width, 4), dtype=np.uint8)
            
            # Fill background
            texture_data[:, :, :3] = [40, 40, 40]  # Dark gray background
            texture_data[:, :, 3] = 255  # Full alpha
            
            # Add some simple UI elements (rectangles and text areas)
            # This is a placeholder - real implementation would use proper rendering
            
            # Title bar
            texture_data[0:50, :, :3] = [80, 80, 80]
            
            # Sight distance slider area
            slider_y = 100
            texture_data[slider_y:slider_y+30, 50:450, :3] = [60, 60, 60]
            
            # Slider position based on current sight distance
            slider_pos = int(50 + (self.sight_distance / 50.0) * 400)
            texture_data[slider_y:slider_y+30, slider_pos-5:slider_pos+5, :3] = [76, 175, 80]  # Green
            
            # Fade distance slider area
            fade_y = 150
            texture_data[fade_y:fade_y+30, 50:450, :3] = [60, 60, 60]
            
            # Fade slider position
            fade_pos = int(50 + (self.fade_distance / 10.0) * 400)
            texture_data[fade_y:fade_y+30, fade_pos-5:fade_pos+5, :3] = [255, 152, 0]  # Orange
            
            # Status area
            status_y = 250
            texture_data[status_y:status_y+100, 50:450, :3] = [30, 30, 30]
            
            # Convert to VR texture format
            texture = openvr.Texture_t()
            texture.handle = texture_data.ctypes.data_as(ctypes.c_void_p).value
            texture.eType = openvr.TextureType_DirectX
            texture.eColorSpace = openvr.ColorSpace_Gamma
            
            # Set overlay texture
            if self.overlay_handle is not None:
                error = openvr.VROverlay().setOverlayTexture(self.overlay_handle, texture)
                if error != openvr.VROverlayError_None:
                    logger.error(f"Failed to set overlay texture: {error}")
                else:
                    logger.debug("Updated overlay texture")
            
        except Exception as e:
            logger.error(f"Failed to create overlay texture: {e}")
    
    def show_overlay(self):
        """Show the VR overlay"""
        if not self.is_initialized or self.overlay_handle is None:
            return
        
        try:
            error = openvr.VROverlay().showOverlay(self.overlay_handle)
            if error == openvr.VROverlayError_None:
                self.is_visible = True
                logger.debug("VR overlay shown")
            else:
                logger.error(f"Failed to show overlay: {error}")
        except Exception as e:
            logger.error(f"Error showing overlay: {e}")
    
    def hide_overlay(self):
        """Hide the VR overlay"""
        if not self.is_initialized or self.overlay_handle is None:
            return
        
        try:
            error = openvr.VROverlay().hideOverlay(self.overlay_handle)
            if error == openvr.VROverlayError_None:
                self.is_visible = False
                logger.debug("VR overlay hidden")
            else:
                logger.error(f"Failed to hide overlay: {error}")
        except Exception as e:
            logger.error(f"Error hiding overlay: {e}")
    
    def set_overlay_position(self, position_type: str = "world"):
        """Set overlay position and orientation"""
        if not self.is_initialized or self.overlay_handle is None:
            return
        
        try:
            overlay = openvr.VROverlay()
            
            if position_type == "dashboard":
                # Attach to dashboard
                error = overlay.setOverlayFlag(self.overlay_handle, openvr.VROverlayFlags_ShowDashboard, True)
                
            elif position_type == "world":
                # Position in world space
                transform = openvr.HmdMatrix34_t()
                # Position overlay 1 meter in front of user
                transform.m = [[1.0, 0.0, 0.0, 0.0],
                              [0.0, 1.0, 0.0, 1.5],
                              [0.0, 0.0, 1.0, -self.vr_settings.overlay_distance]]
                
                error = overlay.setOverlayTransformAbsolute(
                    self.overlay_handle, 
                    openvr.TrackingUniverseStanding, 
                    transform
                )
                
            elif position_type in ["hand_left", "hand_right"]:
                # Attach to controller
                hand = position_type.split('_')[1]
                if hand in self.controller_indices:
                    device_index = self.controller_indices[hand]
                    
                    # Create transform relative to controller
                    transform = openvr.HmdMatrix34_t()
                    transform.m = [[1.0, 0.0, 0.0, 0.0],
                                  [0.0, 1.0, 0.0, 0.0],
                                  [0.0, 0.0, 1.0, 0.2]]  # 20cm in front of controller
                    
                    error = overlay.setOverlayTransformTrackedDeviceRelative(
                        self.overlay_handle, device_index, transform
                    )
                else:
                    logger.warning(f"Controller {hand} not found")
                    return
            
            if error != openvr.VROverlayError_None:
                logger.error(f"Failed to set overlay position: {error}")
            else:
                logger.debug(f"Set overlay position to {position_type}")
                
        except Exception as e:
            logger.error(f"Error setting overlay position: {e}")
    
    def update_controller_input(self):
        """Update controller input and handle interactions"""
        if not self.is_initialized or not self.vr_system:
            return
        
        try:
            for hand, device_id in self.controller_indices.items():
                # Get controller state
                result, controller_state = self.vr_system.getControllerState(device_id)
                
                if not result:
                    continue
                
                # Check button presses
                current_buttons = {}
                
                # Trigger button
                trigger_pressed = (controller_state.rAxis[1].x > 0.5)  # Trigger axis
                current_buttons["trigger"] = trigger_pressed
                
                # Grip button  
                grip_pressed = bool(controller_state.ulButtonPressed & (1 << openvr.k_EButton_Grip))
                current_buttons["grip"] = grip_pressed
                
                # Menu button
                menu_pressed = bool(controller_state.ulButtonPressed & (1 << openvr.k_EButton_ApplicationMenu))
                current_buttons["menu"] = menu_pressed
                
                # Touchpad
                touchpad_pressed = bool(controller_state.ulButtonPressed & (1 << openvr.k_EButton_SteamVR_Touchpad))
                touchpad_x = controller_state.rAxis[0].x
                touchpad_y = controller_state.rAxis[0].y
                
                current_buttons["touchpad"] = touchpad_pressed
                
                # Check for button state changes
                last_buttons = self.last_button_states.get(device_id, {})
                
                # Handle button press events
                if trigger_pressed and not last_buttons.get("trigger", False):
                    self._handle_button_press(hand, "trigger")
                
                if grip_pressed and not last_buttons.get("grip", False):
                    self._handle_button_press(hand, "grip")
                
                if menu_pressed and not last_buttons.get("menu", False):
                    self._handle_button_press(hand, "menu")
                
                if touchpad_pressed and not last_buttons.get("touchpad", False):
                    self._handle_touchpad_press(hand, touchpad_x, touchpad_y)
                
                # Update button states
                self.last_button_states[device_id] = current_buttons
                
                # Handle haptic feedback
                if self.vr_settings.haptic_feedback:
                    if any(current_buttons.values()) and not any(last_buttons.values()):
                        self._trigger_haptic_feedback(device_id, 0.1, 1000)  # 100ms, 1000 Hz
        
        except Exception as e:
            logger.error(f"Error updating controller input: {e}")
    
    def _handle_button_press(self, hand: str, button: str):
        """Handle button press events"""
        logger.debug(f"Button press: {hand} {button}")
        
        if button == "menu":
            # Toggle overlay visibility
            if self.is_visible:
                self.hide_overlay()
            else:
                self.show_overlay()
        
        elif button == self.vr_settings.controller_binding_left and hand == "left":
            # Decrease sight distance
            self.sight_distance = max(1.0, self.sight_distance - 1.0)
            self._update_proximity_settings()
            
        elif button == self.vr_settings.controller_binding_right and hand == "right":
            # Increase sight distance
            self.sight_distance = min(50.0, self.sight_distance + 1.0)
            self._update_proximity_settings()
    
    def _handle_touchpad_press(self, hand: str, x: float, y: float):
        """Handle touchpad press events"""
        logger.debug(f"Touchpad press: {hand} ({x:.2f}, {y:.2f})")
        
        # Use touchpad for fine-grained sight distance control
        if abs(x) > 0.3:  # Horizontal movement
            if x > 0:
                self.sight_distance = min(50.0, self.sight_distance + 0.5)
            else:
                self.sight_distance = max(1.0, self.sight_distance - 0.5)
            self._update_proximity_settings()
        
        if abs(y) > 0.3:  # Vertical movement
            if y > 0:
                self.fade_distance = min(10.0, self.fade_distance + 0.2)
            else:
                self.fade_distance = max(0.5, self.fade_distance - 0.2)
            self._update_proximity_settings()
    
    def _trigger_haptic_feedback(self, device_id: int, duration: float, frequency: int):
        """Trigger haptic feedback on controller"""
        try:
            if self.vr_system:
                # Convert duration to microseconds
                duration_us = int(duration * 1000000)
                self.vr_system.triggerHapticPulse(device_id, 0, duration_us)
        except Exception as e:
            logger.error(f"Failed to trigger haptic feedback: {e}")
    
    def _update_proximity_settings(self):
        """Update proximity engine settings and notify callbacks"""
        try:
            current_settings = self.proximity_engine.settings
            current_settings.sight_distance = self.sight_distance
            current_settings.fade_distance = self.fade_distance
            
            self.proximity_engine.update_settings(current_settings)
            
            # Update overlay texture to reflect changes
            self.content_needs_update = True
            
            # Notify callbacks
            for callback in self.settings_change_callbacks:
                try:
                    callback(current_settings)
                except Exception as e:
                    logger.error(f"Error in settings callback: {e}")
            
            logger.info(f"Updated proximity settings: sight={self.sight_distance:.1f}m, fade={self.fade_distance:.1f}m")
            
        except Exception as e:
            logger.error(f"Failed to update proximity settings: {e}")
    
    def register_settings_callback(self, callback: Callable):
        """Register callback for settings changes"""
        self.settings_change_callbacks.append(callback)
    
    def set_settings(self, sight_distance: float, fade_distance: float):
        """Set proximity settings from external source"""
        self.sight_distance = sight_distance
        self.fade_distance = fade_distance
        self.content_needs_update = True
    
    async def update_loop(self):
        """Main update loop for VR overlay"""
        logger.info("Starting VR overlay update loop")
        
        while self.is_initialized:
            try:
                # Update controller input
                self.update_controller_input()
                
                # Update overlay content if needed
                if self.content_needs_update:
                    self._create_overlay_texture()
                    self.content_needs_update = False
                
                # Check for auto-show/hide based on controller proximity
                if self.vr_settings.auto_hide_desktop_ui:
                    self._check_auto_visibility()
                
                # Small sleep to prevent overwhelming the system
                await asyncio.sleep(0.05)  # 20 FPS update rate
                
            except Exception as e:
                logger.error(f"Error in VR overlay update loop: {e}")
                await asyncio.sleep(1.0)
    
    def _check_auto_visibility(self):
        """Check if overlay should auto-show/hide based on controller proximity"""
        try:
            if not self.controller_indices:
                return
            
            # Get controller positions and check if they're close to each other
            # This could indicate the user wants to adjust settings
            
            poses = []
            for device_id in self.controller_indices.values():
                result, pose = self.vr_system.getDeviceToAbsoluteTrackingPose(
                    openvr.TrackingUniverseStanding, 0.0, openvr.k_unMaxTrackedDeviceCount
                )
                
                if result == openvr.VRInitError_None and device_id < len(pose):
                    device_pose = pose[device_id]
                    if device_pose.bPoseIsValid:
                        poses.append(device_pose)
            
            if len(poses) >= 2:
                # Calculate distance between controllers
                pos1 = poses[0].mDeviceToAbsoluteTracking.m[0:3][3]  # Translation component
                pos2 = poses[1].mDeviceToAbsoluteTracking.m[0:3][3]
                
                distance = np.linalg.norm([pos1[i] - pos2[i] for i in range(3)])
                
                # Auto-show if controllers are close
                if distance < self.vr_settings.auto_show_distance and not self.is_visible:
                    self.show_overlay()
                elif distance > self.vr_settings.auto_show_distance * 1.5 and self.is_visible:
                    # Hide with some hysteresis
                    self.hide_overlay()
        
        except Exception as e:
            logger.debug(f"Error in auto-visibility check: {e}")


class VRIntegrationManager:
    """High-level manager for VR integration"""
    
    def __init__(self, proximity_engine: ProximityEngine, vr_settings: VRSettings):
        self.proximity_engine = proximity_engine
        self.vr_settings = vr_settings
        self.overlay = SteamVROverlay(proximity_engine, vr_settings)
        self.running = False
        self.update_task: Optional[asyncio.Task] = None
    
    async def start(self) -> bool:
        """Start VR integration"""
        if not VR_AVAILABLE:
            logger.warning("OpenVR not available - VR integration disabled")
            return False
        
        if not self.vr_settings.enable_vr_overlay:
            logger.info("VR overlay disabled in settings")
            return False
        
        try:
            if not self.overlay.initialize():
                logger.error("Failed to initialize VR overlay")
                return False
            
            # Start update loop
            self.update_task = asyncio.create_task(self.overlay.update_loop())
            self.running = True
            
            # Show overlay if configured
            if self.vr_settings.enable_vr_overlay:
                self.overlay.set_overlay_position("world")
                # Don't auto-show initially, let user trigger with menu button
            
            logger.info("VR integration started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start VR integration: {e}")
            return False
    
    async def stop(self):
        """Stop VR integration"""
        self.running = False
        
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
        
        self.overlay.shutdown()
        logger.info("VR integration stopped")
    
    def update_settings(self, sight_distance: float, fade_distance: float):
        """Update proximity settings from external source"""
        self.overlay.set_settings(sight_distance, fade_distance)
    
    def register_settings_callback(self, callback: Callable):
        """Register callback for VR settings changes"""
        self.overlay.register_settings_callback(callback)
    
    def get_status(self) -> Dict[str, Any]:
        """Get VR integration status"""
        return {
            'vr_available': VR_AVAILABLE,
            'initialized': self.overlay.is_initialized,
            'overlay_visible': self.overlay.is_visible,
            'running': self.running,
            'controllers_found': len(self.overlay.controller_indices),
            'controller_devices': list(self.overlay.controller_indices.keys())
        }
