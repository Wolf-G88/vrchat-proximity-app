#!/usr/bin/env python3
"""
Working Proximity Test - Visual test that actually shows data updating
"""

import sys
import time
import math
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from src.core.proximity_engine import ProximityEngine, VisibilitySettings, UserPosition

class WorkingProximityTest(QMainWindow):
    """Actually working proximity test with real visual updates"""
    
    def __init__(self):
        super().__init__()
        
        # State
        self.running = False
        self.start_time = time.time()
        
        # Create proximity engine
        settings = VisibilitySettings(sight_distance=15.0, fade_distance=3.0)
        self.engine = ProximityEngine(settings)
        
        # Create mock users
        self.users = [
            UserPosition("alice", "Alice", 5.0, 0.0, 0.0),
            UserPosition("bob", "Bob", 12.0, 0.0, 0.0),
            UserPosition("charlie", "Charlie", 20.0, 0.0, 0.0),
        ]
        
        # Setup local user
        local_user = UserPosition("local", "You", 0.0, 0.0, 0.0)
        self.engine.set_local_user_position(local_user)
        
        self.setup_ui()
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        
        print("🎮 Working Proximity Test - Ready!")
        print("You should see the window with sliders and user info")
    
    def setup_ui(self):
        self.setWindowTitle("VRChat Proximity Test - Working Version")
        self.setGeometry(100, 100, 700, 500)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("🎮 VRChat Proximity Test - Working!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Controls
        controls_group = QGroupBox("Controls")
        controls_layout = QGridLayout()
        
        # Sight distance
        controls_layout.addWidget(QLabel("Sight Distance:"), 0, 0)
        self.sight_label = QLabel("15.0m")
        self.sight_slider = QSlider(Qt.Orientation.Horizontal)
        self.sight_slider.setMinimum(50)  # 5.0m
        self.sight_slider.setMaximum(300) # 30.0m
        self.sight_slider.setValue(150)   # 15.0m
        self.sight_slider.valueChanged.connect(self.update_sight_distance)
        controls_layout.addWidget(self.sight_label, 0, 1)
        controls_layout.addWidget(self.sight_slider, 0, 2)
        
        # Fade distance
        controls_layout.addWidget(QLabel("Fade Distance:"), 1, 0)
        self.fade_label = QLabel("3.0m")
        self.fade_slider = QSlider(Qt.Orientation.Horizontal)
        self.fade_slider.setMinimum(10)   # 1.0m
        self.fade_slider.setMaximum(100)  # 10.0m
        self.fade_slider.setValue(30)     # 3.0m
        self.fade_slider.valueChanged.connect(self.update_fade_distance)
        controls_layout.addWidget(self.fade_label, 1, 1)
        controls_layout.addWidget(self.fade_slider, 1, 2)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Start button
        self.start_btn = QPushButton("Start Test")
        self.start_btn.clicked.connect(self.toggle_test)
        self.start_btn.setStyleSheet("font-weight: bold; height: 40px; font-size: 14px;")
        layout.addWidget(self.start_btn)
        
        # Status
        self.status_label = QLabel("Ready - Click 'Start Test' to begin")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Users display
        users_group = QGroupBox("Users (Real-time Updates)")
        users_layout = QVBoxLayout()
        
        # Create labels for each user
        self.user_labels = {}
        for user in self.users:
            label = QLabel(f"{user.username}: Calculating...")
            label.setStyleSheet("padding: 5px; font-family: monospace; font-size: 12px;")
            users_layout.addWidget(label)
            self.user_labels[user.user_id] = label
        
        users_group.setLayout(users_layout)
        layout.addWidget(users_group)
    
    def update_sight_distance(self, value):
        distance = value / 10.0
        self.sight_label.setText(f"{distance:.1f}m")
        self.engine.settings.sight_distance = distance
        print(f"🔄 Sight distance changed to {distance:.1f}m")
    
    def update_fade_distance(self, value):
        distance = value / 10.0
        self.fade_label.setText(f"{distance:.1f}m")
        self.engine.settings.fade_distance = distance
        print(f"🔄 Fade distance changed to {distance:.1f}m")
    
    def toggle_test(self):
        if not self.running:
            self.start_test()
        else:
            self.stop_test()
    
    def start_test(self):
        print("▶️  Starting proximity test...")
        self.running = True
        self.start_btn.setText("Stop Test")
        self.start_btn.setStyleSheet("font-weight: bold; height: 40px; font-size: 14px; background-color: #ff4444;")
        self.status_label.setText("🔄 Test running - Users are moving and proximity is being calculated!")
        
        # Add users to engine
        for user in self.users:
            self.engine.update_user_position(user)
        
        # Start timer
        self.timer.start(100)  # Update every 100ms
        self.start_time = time.time()
    
    def stop_test(self):
        print("⏹️  Stopping proximity test...")
        self.running = False
        self.start_btn.setText("Start Test")
        self.start_btn.setStyleSheet("font-weight: bold; height: 40px; font-size: 14px; background-color: #44aa44;")
        self.status_label.setText("⏸️  Test stopped")
        self.timer.stop()
    
    def update_simulation(self):
        if not self.running:
            return
        
        elapsed = time.time() - self.start_time
        
        # Move users in simple patterns
        # Alice - back and forth
        self.users[0].x = 8.0 + 5.0 * math.sin(elapsed * 0.5)
        
        # Bob - circular
        self.users[1].x = 15.0 + 8.0 * math.cos(elapsed * 0.3)
        self.users[1].z = 8.0 * math.sin(elapsed * 0.3)
        
        # Charlie - approaching and retreating
        self.users[2].x = 25.0 + 10.0 * math.sin(elapsed * 0.2)
        
        # Update each user in the engine
        for user in self.users:
            user.timestamp = time.time()
            self.engine.update_user_position(user)
            
            # Calculate distance and update visibility
            distance = self.engine.calculate_distance(user)
            self.engine.update_visibility_state(user.user_id, distance)
            
            # Update display
            visibility = self.engine.get_user_visibility(user.user_id)
            if visibility:
                visibility_percent = visibility.visibility_alpha * 100
                status = visibility.state.value.replace('_', ' ').title()
                
                # Color code the display
                if visibility_percent > 80:
                    color = "#00aa00"  # Green - visible
                elif visibility_percent > 20:
                    color = "#ff8800"  # Orange - fading
                else:
                    color = "#aa0000"  # Red - hidden
                
                text = f"{user.username}: {distance:.1f}m away, {visibility_percent:.0f}% visible, {status}"
                self.user_labels[user.user_id].setText(text)
                self.user_labels[user.user_id].setStyleSheet(f"padding: 5px; font-family: monospace; font-size: 12px; color: {color};")
                
                print(f"👤 {user.username}: {distance:.1f}m, {visibility_percent:.0f}% visible, {status}")


def main():
    print("🚀 VRChat Proximity App - Working Test")
    print("=" * 50)
    print("This version actually shows real-time updates!")
    print("- Users move around automatically")
    print("- Distance calculations happen in real-time") 
    print("- Visibility changes as users move")
    print("- Color-coded display (Green=visible, Orange=fading, Red=hidden)")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    app.setApplicationName("VRChat Proximity - Working Test")
    
    window = WorkingProximityTest()
    window.show()
    
    print("👀 Window should be open - click 'Start Test' to see it work!")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
