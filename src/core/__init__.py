"""
Core proximity detection and visibility management
"""

from .proximity_engine import (
    ProximityEngine,
    VisibilitySettings,
    UserPosition,
    UserVisibility,
    VisibilityState
)

__all__ = [
    "ProximityEngine",
    "VisibilitySettings", 
    "UserPosition",
    "UserVisibility",
    "VisibilityState"
]
