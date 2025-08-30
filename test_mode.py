#!/usr/bin/env python3
"""
Test Mode for VRChat Proximity App - Can run without VRChat
This creates mock users to test the proximity system
"""

import sys
import asyncio
import random
import time
import math
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.proximity_engine import ProximityEngine, VisibilitySettings, UserPosition
from src.ui.main_window import MainWindow
from src.config.settings import get_config_manager

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

class MockVRChatIntegration:
    """Mock VRChat integration for testing"""
    
    def __init__(self, proximity_engine):
        self.proximity_engine = proximity_engine
        self.running = False
        self.mock_users = []
        self.local_user_id = "test_local_user"
        
        # Create mock users at different distances
        self.create_mock_users()
    
    def create_mock_users(self):
        """Create mock users for testing"""
        user_configs = [
            ("alice", "Alice", 5.0, 0.0, 0.0),      # Close user
            ("bob", "Bob", 12.0, 2.0, 1.0),         # Medium distance
            ("charlie", "Charlie", 25.0, -1.0, 3.0), # Far user
            ("diana", "Diana", 8.0, 4.0, -2.0),     # Close-medium
            ("eve", "Eve", 35.0, 10.0, 5.0),        # Very far
            ("frank", "Frank", 3.0, 1.0, 0.0),      # Very close
        ]
        
        for user_id, username, x, y, z in user_configs:
            user = UserPosition(user_id, username, x, y, z)
            self.mock_users.append(user)
    
    async def start(self):
        """Start mock integration"""
        self.running = True
        
        # Set local user position
        local_pos = UserPosition(self.local_user_id, "TestUser", 0.0, 0.0, 0.0)
        self.proximity_engine.set_local_user_position(local_pos)
        
        # Add mock users
        for user in self.mock_users:
            self.proximity_engine.update_user_position(user)
        
        # Start animation loop
        asyncio.create_task(self.animate_users())
        
        print("🎭 Mock VRChat integration started!")
        print(f"📍 Created {len(self.mock_users)} mock users for testing")
        print("🎮 Users will move around to test proximity detection")
    
    async def stop(self):
        """Stop mock integration"""
        self.running = False
        print("🛑 Mock VRChat integration stopped")
    
    async def animate_users(self):
        """Animate mock users to test proximity changes"""
        start_time = time.time()
        
        while self.running:
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Animate users in different patterns
            for i, user in enumerate(self.mock_users):
                # Each user follows a different movement pattern
                if i == 0:  # Alice - circular motion close to origin
                    radius = 8.0
                    angle = elapsed * 0.3 + i
                    user.x = radius * math.cos(angle)
                    user.z = radius * math.sin(angle)
                elif i == 1:  # Bob - figure-8 pattern
                    user.x = 15.0 * math.sin(elapsed * 0.2)
                    user.z = 8.0 * math.sin(elapsed * 0.4)
                elif i == 2:  # Charlie - slow orbit
                    radius = 30.0
                    angle = elapsed * 0.1
                    user.x = radius * math.cos(angle)
                    user.z = radius * math.sin(angle)
                elif i == 3:  # Diana - random walk
                    user.x += random.uniform(-0.5, 0.5)
                    user.z += random.uniform(-0.5, 0.5)
                    # Keep within bounds
                    user.x = max(-40, min(40, user.x))
                    user.z = max(-40, min(40, user.z))
                elif i == 4:  # Eve - approaching and retreating
                    distance = 20.0 + 15.0 * math.sin(elapsed * 0.15)
                    angle = elapsed * 0.05
                    user.x = distance * math.cos(angle)
                    user.z = distance * math.sin(angle)
                elif i == 5:  # Frank - close orbiter
                    radius = 4.0 + 2.0 * math.sin(elapsed * 0.5)
                    angle = elapsed * 0.8
                    user.x = radius * math.cos(angle)
                    user.z = radius * math.sin(angle)
                
                # Update timestamp
                user.timestamp = current_time
                
                # Update in proximity engine
                self.proximity_engine.update_user_position(user)
            
            await asyncio.sleep(0.1)  # 10 FPS updates


class TestMainWindow(MainWindow):
    """Main window with test mode integration"""
    
    def __init__(self):
        super().__init__()
        
        # Replace VRChat integration with mock
        self.vrchat_integration = MockVRChatIntegration(self.proximity_engine)
        
        # Add test mode indicator
        self.setWindowTitle("VRChat Proximity App - TEST MODE")
        
        # Create test controls
        self.setup_test_mode_ui()
        
        # Setup test animation timer
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self.update_test_display)
        self.test_timer.start(100)  # Update every 100ms
    
    def setup_test_mode_ui(self):
        """Add test mode specific UI elements"""
        # You could add test-specific controls here
        pass
    
    def update_test_display(self):
        """Update display with test information"""
        # This gets called by the parent class's timer already
        pass


def main():
    """Test mode entry point"""
    print("🧪 VRChat Proximity App - TEST MODE")
    print("=" * 50)
    print("This mode creates mock users to test proximity detection")
    print("without requiring VRChat to be running.")
    print()
    print("Features to test:")
    print("- Proximity sliders (adjust sight/fade distance)")
    print("- User list showing distances and visibility")
    print("- Status monitoring")
    print("- Preset system")
    print("- Settings persistence")
    print()
    print("Mock users will move around automatically to")
    print("demonstrate proximity-based visibility changes.")
    print("=" * 50)
    print()
    
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("VRChat Proximity App - Test Mode")
    app.setApplicationVersion("1.0.0-test")
    app.setOrganizationName("VRChat Proximity")
    
    # Create test window
    window = TestMainWindow()
    window.show()
    
    # Start the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
