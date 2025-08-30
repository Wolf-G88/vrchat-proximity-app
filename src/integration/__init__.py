"""
Integration modules for external services (VRChat, SteamVR)
"""

from .vrchat_osc import VRChatIntegration, VRChatOSCConfig
from .steamvr_overlay import VRIntegrationManager

__all__ = [
    "VRChatIntegration",
    "VRChatOSCConfig", 
    "VRIntegrationManager"
]
