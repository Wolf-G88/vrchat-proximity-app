#!/usr/bin/env python3
"""
Debug Test - Let's see exactly what's happening
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.proximity_engine import ProximityEngine, VisibilitySettings, UserPosition

def test_proximity_engine():
    """Test the proximity engine directly"""
    print("🔍 Testing Proximity Engine Directly")
    print("-" * 40)
    
    # Create engine
    settings = VisibilitySettings(sight_distance=10.0, fade_distance=2.0)
    engine = ProximityEngine(settings)
    
    print(f"✅ Engine created with sight distance: {settings.sight_distance}m")
    
    # Set local user
    local_user = UserPosition("local", "TestUser", 0.0, 0.0, 0.0)
    engine.set_local_user_position(local_user)
    print(f"✅ Local user set at origin: {local_user.x}, {local_user.y}, {local_user.z}")
    
    # Add test users at different distances
    test_users = [
        ("alice", "Alice", 5.0, 0.0, 0.0),   # Within sight distance
        ("bob", "Bob", 15.0, 0.0, 0.0),     # Outside sight distance
        ("charlie", "Charlie", 8.0, 0.0, 0.0),  # At edge of sight distance
    ]
    
    for user_id, username, x, y, z in test_users:
        user = UserPosition(user_id, username, x, y, z)
        engine.update_user_position(user)
        distance = engine.calculate_distance(user)
        engine.update_visibility_state(user_id, distance)
        
        visibility = engine.get_user_visibility(user_id)
        print(f"👤 {username}: Distance={distance:.1f}m, Visibility={visibility.visibility_alpha:.1%}, State={visibility.state.value}")
    
    # Get stats
    stats = engine.get_stats()
    print(f"\n📊 Engine Stats:")
    print(f"   Total users: {stats['total_users']}")
    print(f"   Visible users: {stats['visible_users']}")
    print(f"   Hidden users: {stats['hidden_users']}")
    
    return True

def test_simple_gui():
    """Test if PyQt6 is working"""
    print("\n🖥️  Testing PyQt6 GUI")
    print("-" * 40)
    
    try:
        from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
        from PyQt6.QtCore import Qt
        
        app = QApplication(sys.argv)
        
        window = QWidget()
        window.setWindowTitle("VRChat Proximity - Debug Test")
        window.setGeometry(100, 100, 400, 200)
        
        layout = QVBoxLayout()
        
        label = QLabel("✅ PyQt6 is working!\n\nThis proves the GUI system works.\nClose this window to continue.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 14px; padding: 20px;")
        
        layout.addWidget(label)
        window.setLayout(layout)
        
        window.show()
        
        print("✅ GUI window opened successfully")
        print("💡 You should see a test window - close it to continue")
        
        app.exec()
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

def main():
    """Main debug test"""
    print("🔍 VRChat Proximity App - Debug Test")
    print("=" * 50)
    
    # Test 1: Core proximity engine
    try:
        engine_works = test_proximity_engine()
        if engine_works:
            print("✅ Proximity engine is working perfectly!")
        else:
            print("❌ Proximity engine has issues")
    except Exception as e:
        print(f"❌ Proximity engine failed: {e}")
        return
    
    # Test 2: GUI system
    try:
        gui_works = test_simple_gui()
        if gui_works:
            print("\n✅ GUI system is working!")
        else:
            print("\n❌ GUI system has issues")
    except Exception as e:
        print(f"\n❌ GUI test failed: {e}")
        return
    
    print("\n🎉 All core systems are working!")
    print("The issue might be in the animation or data display.")
    print("Let's check the VRChat integration next...")

if __name__ == "__main__":
    main()
