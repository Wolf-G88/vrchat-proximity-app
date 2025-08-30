#!/usr/bin/env python3
"""
Simple Test for VRChat Proximity App - Basic functionality test
"""

import sys
import time
import math
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

from src.core.proximity_engine import ProximityEngine, VisibilitySettings, UserPosition, VisibilityState

class SimpleProximityTest(QMainWindow):
    """Simple test window for proximity functionality"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize proximity engine
        settings = VisibilitySettings()
        self.proximity_engine = ProximityEngine(settings)
        
        # Mock users
        self.mock_users = []
        self.create_mock_users()
        
        # Animation state
        self.start_time = time.time()
        self.is_running = False
        
        # Setup UI
        self.setup_ui()
        
        # Setup timers
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_users)
        
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_display)
        self.ui_timer.start(100)  # Update UI every 100ms
        
        print("🎮 Simple Proximity Test Ready!")
        print("Click 'Start Test' to see animated users")
    
    def setup_ui(self):
        """Setup simple UI"""
        self.setWindowTitle("VRChat Proximity App - Simple Test")
        self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # Left panel - controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Sight distance control
        controls_group = QGroupBox("Proximity Controls")
        controls_layout = QVBoxLayout()
        
        # Sight distance
        sight_label = QLabel("Sight Distance: 10.0m")
        self.sight_slider = QSlider(Qt.Orientation.Horizontal)
        self.sight_slider.setMinimum(10)  # 1.0m * 10
        self.sight_slider.setMaximum(500)  # 50.0m * 10
        self.sight_slider.setValue(100)  # 10.0m * 10
        self.sight_slider.valueChanged.connect(
            lambda v: self.update_sight_distance(v / 10.0, sight_label)
        )
        
        controls_layout.addWidget(sight_label)
        controls_layout.addWidget(self.sight_slider)
        
        # Fade distance  
        fade_label = QLabel("Fade Distance: 2.0m")
        self.fade_slider = QSlider(Qt.Orientation.Horizontal)
        self.fade_slider.setMinimum(5)   # 0.5m * 10
        self.fade_slider.setMaximum(100) # 10.0m * 10
        self.fade_slider.setValue(20)   # 2.0m * 10
        self.fade_slider.valueChanged.connect(
            lambda v: self.update_fade_distance(v / 10.0, fade_label)
        )
        
        controls_layout.addWidget(fade_label)
        controls_layout.addWidget(self.fade_slider)
        
        controls_group.setLayout(controls_layout)
        left_layout.addWidget(controls_group)
        
        # Control buttons
        self.start_btn = QPushButton("Start Test")
        self.start_btn.clicked.connect(self.toggle_test)
        self.start_btn.setStyleSheet("QPushButton { font-weight: bold; height: 40px; }")
        left_layout.addWidget(self.start_btn)
        
        # Status
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Ready to test")
        self.users_label = QLabel("Users: 0 total, 0 visible")
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.users_label)
        
        status_group.setLayout(status_layout)
        left_layout.addWidget(status_group)
        
        left_layout.addStretch()
        left_panel.setMaximumWidth(300)
        
        # Right panel - user table
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(QLabel("User List (distances and visibility)"))
        
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["Username", "Distance", "Visibility", "Status"])
        self.user_table.setAlternatingRowColors(True)
        
        right_layout.addWidget(self.user_table)
        
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)
    
    def create_mock_users(self):
        """Create mock users at different distances"""
        users = [
            ("Alice", 3.0, 0.0, 0.0),      # Very close
            ("Bob", 8.0, 2.0, 1.0),       # Close  
            ("Charlie", 15.0, -1.0, 3.0), # Medium
            ("Diana", 25.0, 4.0, -2.0),   # Far
            ("Eve", 40.0, 10.0, 5.0),     # Very far
        ]
        
        for username, x, y, z in users:
            user = UserPosition(f"user_{username.lower()}", username, x, y, z)
            self.mock_users.append(user)
    
    def update_sight_distance(self, value: float, label: QLabel):
        """Update sight distance"""
        label.setText(f"Sight Distance: {value:.1f}m")
        self.proximity_engine.settings.sight_distance = value
        
    def update_fade_distance(self, value: float, label: QLabel):
        """Update fade distance"""
        label.setText(f"Fade Distance: {value:.1f}m")
        self.proximity_engine.settings.fade_distance = value
    
    def toggle_test(self):
        """Start/stop the test"""
        if not self.is_running:
            self.start_test()
        else:
            self.stop_test()
    
    def start_test(self):
        """Start the proximity test"""
        # Set local user position at origin
        local_user = UserPosition("local", "TestUser", 0.0, 0.0, 0.0)
        self.proximity_engine.set_local_user_position(local_user)
        
        # Add all mock users
        for user in self.mock_users:
            self.proximity_engine.update_user_position(user)
        
        self.is_running = True
        self.start_btn.setText("Stop Test")
        self.start_btn.setStyleSheet("QPushButton { font-weight: bold; height: 40px; background-color: #F44336; }")
        self.status_label.setText("Test running - users are moving!")
        
        # Start animation
        self.animation_timer.start(100)  # 10 FPS
        
    def stop_test(self):
        """Stop the proximity test"""
        self.is_running = False
        self.start_btn.setText("Start Test")
        self.start_btn.setStyleSheet("QPushButton { font-weight: bold; height: 40px; background-color: #4CAF50; }")
        self.status_label.setText("Test stopped")
        
        # Stop animation
        self.animation_timer.stop()
    
    def animate_users(self):
        """Animate users moving around"""
        if not self.is_running:
            return
        
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Animate each user differently
        for i, user in enumerate(self.mock_users):
            if i == 0:  # Alice - close circle
                radius = 5.0 + 3.0 * math.sin(elapsed * 0.3)
                angle = elapsed * 0.5
                user.x = radius * math.cos(angle)
                user.z = radius * math.sin(angle)
            elif i == 1:  # Bob - figure 8
                user.x = 12.0 * math.sin(elapsed * 0.2)
                user.z = 6.0 * math.sin(elapsed * 0.4)
            elif i == 2:  # Charlie - slow orbit
                radius = 20.0 + 8.0 * math.sin(elapsed * 0.1)
                angle = elapsed * 0.15
                user.x = radius * math.cos(angle)
                user.z = radius * math.sin(angle)
            elif i == 3:  # Diana - approaching/retreating
                distance = 30.0 + 20.0 * math.sin(elapsed * 0.1)
                user.x = distance
                user.z = 2.0 * math.sin(elapsed * 0.3)
            elif i == 4:  # Eve - far orbit
                radius = 35.0 + 15.0 * math.cos(elapsed * 0.05)
                angle = elapsed * 0.08
                user.x = radius * math.cos(angle)
                user.z = radius * math.sin(angle)
            
            user.timestamp = current_time
            
            # Update in proximity engine
            self.proximity_engine.update_user_position(user)
            
            # Calculate distance and update visibility
            if self.proximity_engine.local_user:
                distance = self.proximity_engine.calculate_distance(user)
                self.proximity_engine.update_visibility_state(user.user_id, distance)
    
    def update_display(self):
        """Update the UI display"""
        if not self.is_running:
            return
        
        # Update status
        total_users = len(self.proximity_engine.users)
        visible_users = len(self.proximity_engine.get_visible_users())
        self.users_label.setText(f"Users: {total_users} total, {visible_users} visible")
        
        # Update user table
        visibility_states = self.proximity_engine.visibility_states
        self.user_table.setRowCount(len(visibility_states))
        
        for row, (user_id, visibility) in enumerate(visibility_states.items()):
            # Find username
            username = "Unknown"
            for user in self.mock_users:
                if user.user_id == user_id:
                    username = user.username
                    break
            
            # Username
            self.user_table.setItem(row, 0, QTableWidgetItem(username))
            
            # Distance
            distance_text = f"{visibility.distance:.1f}m" if visibility.distance != float('inf') else "Unknown"
            self.user_table.setItem(row, 1, QTableWidgetItem(distance_text))
            
            # Visibility percentage
            visibility_percent = f"{visibility.visibility_alpha * 100:.0f}%"
            vis_item = QTableWidgetItem(visibility_percent)
            
            # Color code visibility
            if visibility.visibility_alpha > 0.8:
                vis_item.setForeground(QColor("#4CAF50"))  # Green - fully visible
            elif visibility.visibility_alpha > 0.2:
                vis_item.setForeground(QColor("#FF9800"))  # Orange - fading
            else:
                vis_item.setForeground(QColor("#F44336"))  # Red - hidden
            
            self.user_table.setItem(row, 2, vis_item)
            
            # Status
            status_text = visibility.state.value.replace('_', ' ').title()
            self.user_table.setItem(row, 3, QTableWidgetItem(status_text))


def main():
    """Main function"""
    print("🧪 VRChat Proximity App - Simple Test")
    print("=" * 50)
    print("This is a simplified test of the proximity system.")
    print("Features:")
    print("- Adjustable sight and fade distance sliders")
    print("- 5 mock users moving in different patterns") 
    print("- Real-time distance and visibility calculations")
    print("- Color-coded user table showing visibility states")
    print("=" * 50)
    print()
    
    app = QApplication(sys.argv)
    app.setApplicationName("VRChat Proximity App - Simple Test")
    
    window = SimpleProximityTest()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
