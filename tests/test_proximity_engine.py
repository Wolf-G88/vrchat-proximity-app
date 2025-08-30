"""
Tests for the proximity engine
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.proximity_engine import (
    ProximityEngine, VisibilitySettings, UserPosition, 
    UserVisibility, VisibilityState
)


class TestUserPosition:
    """Test UserPosition class"""
    
    def test_distance_calculation(self):
        """Test distance calculation between users"""
        user1 = UserPosition("user1", "User1", 0.0, 0.0, 0.0)
        user2 = UserPosition("user2", "User2", 3.0, 4.0, 0.0)
        
        distance = user1.distance_to(user2)
        assert distance == 5.0  # 3-4-5 triangle
    
    def test_2d_distance_calculation(self):
        """Test 2D distance calculation (ignoring Y axis)"""
        user1 = UserPosition("user1", "User1", 0.0, 10.0, 0.0)
        user2 = UserPosition("user2", "User2", 3.0, 20.0, 4.0)
        
        distance_2d = user1.distance_to_2d(user2)
        assert distance_2d == 5.0  # Y difference ignored
    
    def test_stale_detection(self):
        """Test stale position detection"""
        # Fresh position
        user = UserPosition("user1", "User1", 0.0, 0.0, 0.0)
        assert not user.is_stale(5.0)
        
        # Old position
        old_time = time.time() - 10.0
        user.timestamp = old_time
        assert user.is_stale(5.0)


class TestVisibilitySettings:
    """Test VisibilitySettings class"""
    
    def test_default_settings(self):
        """Test default visibility settings"""
        settings = VisibilitySettings()
        assert settings.sight_distance == 10.0
        assert settings.fade_distance == 2.0
        assert settings.use_vertical_distance == True
        assert settings.fade_duration == 1.0
    
    def test_effective_sight_distance(self):
        """Test effective sight distance calculation"""
        settings = VisibilitySettings(sight_distance=10.0, distance_multiplier=2.0)
        
        # Without scaling
        settings.enable_distance_scaling = False
        assert settings.get_effective_sight_distance(3.0) == 20.0
        
        # With scaling
        settings.enable_distance_scaling = True
        assert settings.get_effective_sight_distance(3.0) == 60.0


class TestProximityEngine:
    """Test ProximityEngine class"""
    
    def test_initialization(self):
        """Test proximity engine initialization"""
        settings = VisibilitySettings()
        engine = ProximityEngine(settings)
        
        assert engine.settings == settings
        assert engine.local_user is None
        assert len(engine.users) == 0
        assert len(engine.visibility_states) == 0
    
    def test_local_user_position(self):
        """Test setting local user position"""
        settings = VisibilitySettings()
        engine = ProximityEngine(settings)
        
        local_pos = UserPosition("local", "LocalUser", 5.0, 2.0, 1.0)
        engine.set_local_user_position(local_pos)
        
        assert engine.local_user == local_pos
    
    def test_user_position_update(self):
        """Test updating user positions"""
        settings = VisibilitySettings()
        engine = ProximityEngine(settings)
        
        user_pos = UserPosition("user1", "TestUser", 10.0, 5.0, 2.0)
        engine.update_user_position(user_pos)
        
        assert "user1" in engine.users
        assert engine.users["user1"] == user_pos
        assert "user1" in engine.visibility_states
    
    def test_distance_calculation(self):
        """Test distance calculation between users"""
        settings = VisibilitySettings()
        engine = ProximityEngine(settings)
        
        # Set local user
        local_pos = UserPosition("local", "Local", 0.0, 0.0, 0.0)
        engine.set_local_user_position(local_pos)
        
        # Add remote user
        remote_pos = UserPosition("remote", "Remote", 3.0, 4.0, 0.0)
        
        distance = engine.calculate_distance(remote_pos)
        assert distance == 5.0
    
    def test_visibility_state_update(self):
        """Test visibility state updates based on distance"""
        settings = VisibilitySettings(sight_distance=10.0, fade_distance=2.0)
        engine = ProximityEngine(settings)
        
        # Initialize user
        engine.visibility_states["user1"] = UserVisibility("user1")
        
        # Test visible range
        changed = engine.update_visibility_state("user1", 5.0)
        vis = engine.visibility_states["user1"]
        assert changed
        assert vis.state == VisibilityState.VISIBLE
        assert vis.visibility_alpha == 1.0
        
        # Test fade range
        changed = engine.update_visibility_state("user1", 9.0)
        vis = engine.visibility_states["user1"]
        assert vis.state in [VisibilityState.FADING_IN, VisibilityState.FADING_OUT]
        assert 0.0 < vis.visibility_alpha < 1.0
        
        # Test hidden range
        changed = engine.update_visibility_state("user1", 15.0)
        vis = engine.visibility_states["user1"]
        assert vis.state == VisibilityState.HIDDEN
        assert vis.visibility_alpha == 0.0
    
    def test_visible_users_filter(self):
        """Test getting visible users filter"""
        settings = VisibilitySettings()
        engine = ProximityEngine(settings)
        
        # Add users with different visibility states
        engine.visibility_states["user1"] = UserVisibility("user1")
        engine.visibility_states["user1"].visibility_alpha = 1.0
        
        engine.visibility_states["user2"] = UserVisibility("user2")
        engine.visibility_states["user2"].visibility_alpha = 0.5
        
        engine.visibility_states["user3"] = UserVisibility("user3")
        engine.visibility_states["user3"].visibility_alpha = 0.0
        
        visible_users = engine.get_visible_users()
        assert len(visible_users) == 2
        assert "user1" in visible_users
        assert "user2" in visible_users
        assert "user3" not in visible_users
    
    def test_world_scale_update(self):
        """Test world scale updates"""
        settings = VisibilitySettings()
        engine = ProximityEngine(settings)
        
        engine.set_world_scale(2.5)
        assert engine.world_scale == 2.5
    
    def test_settings_update(self):
        """Test settings updates"""
        settings = VisibilitySettings()
        engine = ProximityEngine(settings)
        
        new_settings = VisibilitySettings(sight_distance=15.0, fade_distance=3.0)
        engine.update_settings(new_settings)
        
        assert engine.settings.sight_distance == 15.0
        assert engine.settings.fade_distance == 3.0
    
    def test_user_removal(self):
        """Test user removal"""
        settings = VisibilitySettings()
        engine = ProximityEngine(settings)
        
        # Add user
        user_pos = UserPosition("user1", "TestUser", 10.0, 5.0, 2.0)
        engine.update_user_position(user_pos)
        
        assert "user1" in engine.users
        assert "user1" in engine.visibility_states
        
        # Remove user
        engine.remove_user("user1")
        
        assert "user1" not in engine.users
        assert "user1" not in engine.visibility_states
    
    def test_statistics(self):
        """Test engine statistics"""
        settings = VisibilitySettings(sight_distance=20.0)
        engine = ProximityEngine(settings)
        engine.set_world_scale(1.5)
        
        # Add some users
        for i in range(3):
            user_pos = UserPosition(f"user{i}", f"User{i}", float(i), 0.0, 0.0)
            engine.update_user_position(user_pos)
        
        # Set one as visible
        engine.visibility_states["user1"].visibility_alpha = 0.8
        
        stats = engine.get_stats()
        assert stats["total_users"] == 3
        assert stats["visible_users"] == 1
        assert stats["hidden_users"] == 2
        assert stats["sight_distance"] == 30.0  # 20.0 * 1.5 world scale
        assert stats["world_scale"] == 1.5


@pytest.mark.asyncio
class TestProximityEngineAsync:
    """Test async functionality of proximity engine"""
    
    async def test_start_stop(self):
        """Test starting and stopping the engine"""
        settings = VisibilitySettings(update_rate=0.01)  # Fast update for testing
        engine = ProximityEngine(settings)
        
        # Test start
        await engine.start()
        assert engine.running
        assert engine.update_task is not None
        
        # Small delay to let it run
        await asyncio.sleep(0.05)
        
        # Test stop
        await engine.stop()
        assert not engine.running
    
    async def test_callback_registration(self):
        """Test visibility callback registration"""
        settings = VisibilitySettings()
        engine = ProximityEngine(settings)
        
        callback_called = False
        callback_data = None
        
        def test_callback(visibility_states):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = visibility_states
        
        engine.register_visibility_callback(test_callback)
        
        # Simulate visibility change
        engine.visibility_states["user1"] = UserVisibility("user1")
        
        # This would normally be called by the update loop
        test_callback(engine.visibility_states)
        
        assert callback_called
        assert "user1" in callback_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
