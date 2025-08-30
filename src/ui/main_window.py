"""
Main Desktop GUI Application
"""

import sys
import asyncio
import logging
import time
import threading
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QPushButton, QComboBox, QCheckBox, QSpinBox,
    QDoubleSpinBox, QTextEdit, QTabWidget, QGroupBox, QGridLayout,
    QProgressBar, QSystemTrayIcon, QMenu, QMessageBox, QFrame,
    QSplitter, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox,
    QFormLayout, QLineEdit, QTextBrowser, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QThread, pyqtSlot,
    QSize, QPoint, QPropertyAnimation, QEasingCurve
)
from PyQt6.QtGui import (
    QIcon, QFont, QPixmap, QPainter, QColor, QPalette,
    QAction, QKeySequence
)

from ..core.proximity_engine import ProximityEngine, VisibilitySettings, UserVisibility
from ..integration.vrchat_osc import VRChatIntegration, VRChatOSCConfig
from ..config.settings import ConfigManager, UISettings, PresetSettings, get_config_manager

logger = logging.getLogger(__name__)


class ProximitySliderWidget(QWidget):
    """Custom slider widget for proximity distance with visual feedback"""
    
    valueChanged = pyqtSignal(float)
    
    def __init__(self, label: str, min_val: float = 0.0, max_val: float = 50.0, 
                 default_val: float = 10.0, suffix: str = "m"):
        super().__init__()
        self.min_val = min_val
        self.max_val = max_val
        self.suffix = suffix
        
        layout = QVBoxLayout()
        
        # Label and value display
        header_layout = QHBoxLayout()
        self.label = QLabel(label)
        self.value_label = QLabel(f"{default_val:.1f}{suffix}")
        self.value_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        header_layout.addWidget(self.label)
        header_layout.addStretch()
        header_layout.addWidget(self.value_label)
        layout.addLayout(header_layout)
        
        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1000)
        self.slider.setValue(int((default_val - min_val) / (max_val - min_val) * 1000))
        self.slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slider)
        
        # Quick preset buttons
        preset_layout = QHBoxLayout()
        presets = [
            ("Close", min_val + (max_val - min_val) * 0.1),
            ("Near", min_val + (max_val - min_val) * 0.3),
            ("Medium", min_val + (max_val - min_val) * 0.5),
            ("Far", min_val + (max_val - min_val) * 0.8),
        ]
        
        for preset_name, preset_val in presets:
            btn = QPushButton(preset_name)
            btn.setMaximumHeight(25)
            btn.clicked.connect(lambda checked, val=preset_val: self.set_value(val))
            preset_layout.addWidget(btn)
        
        layout.addLayout(preset_layout)
        self.setLayout(layout)
    
    def _on_slider_changed(self, slider_value: int):
        # Convert slider position to actual value
        ratio = slider_value / 1000.0
        actual_value = self.min_val + ratio * (self.max_val - self.min_val)
        self.value_label.setText(f"{actual_value:.1f}{self.suffix}")
        self.valueChanged.emit(actual_value)
    
    def set_value(self, value: float):
        # Convert actual value to slider position
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        slider_pos = int(ratio * 1000)
        self.slider.setValue(slider_pos)
    
    def get_value(self) -> float:
        slider_value = self.slider.value()
        ratio = slider_value / 1000.0
        return self.min_val + ratio * (self.max_val - self.min_val)


class StatusWidget(QWidget):
    """Status display widget showing connection and user information"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Connection status
        connection_group = QGroupBox("Connection Status")
        connection_layout = QGridLayout()
        
        self.vrchat_status = QLabel("❌ Disconnected")
        self.users_count = QLabel("0 users tracked")
        self.visible_count = QLabel("0 users visible")
        
        connection_layout.addWidget(QLabel("VRChat:"), 0, 0)
        connection_layout.addWidget(self.vrchat_status, 0, 1)
        connection_layout.addWidget(QLabel("Users:"), 1, 0)
        connection_layout.addWidget(self.users_count, 1, 1)
        connection_layout.addWidget(QLabel("Visible:"), 2, 0)
        connection_layout.addWidget(self.visible_count, 2, 1)
        
        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)
        
        # Performance stats
        perf_group = QGroupBox("Performance")
        perf_layout = QGridLayout()
        
        self.update_rate = QLabel("0 Hz")
        self.processing_time = QLabel("0ms")
        
        perf_layout.addWidget(QLabel("Update Rate:"), 0, 0)
        perf_layout.addWidget(self.update_rate, 0, 1)
        perf_layout.addWidget(QLabel("Processing:"), 1, 0)
        perf_layout.addWidget(self.processing_time, 1, 1)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        self.setLayout(layout)
    
    def update_status(self, status_data: Dict[str, Any]):
        """Update status display with current data"""
        # Connection status
        if status_data.get('vrchat_connected', False):
            self.vrchat_status.setText("✅ Connected")
            self.vrchat_status.setStyleSheet("color: #4CAF50;")
        else:
            self.vrchat_status.setText("❌ Disconnected")
            self.vrchat_status.setStyleSheet("color: #F44336;")
        
        # User counts
        total_users = status_data.get('total_users', 0)
        visible_users = status_data.get('visible_users', 0)
        
        self.users_count.setText(f"{total_users} users tracked")
        self.visible_count.setText(f"{visible_users} users visible")
        
        # Performance
        update_rate = status_data.get('update_rate', 0)
        proc_time = status_data.get('processing_time', 0)
        
        self.update_rate.setText(f"{update_rate:.1f} Hz")
        self.processing_time.setText(f"{proc_time:.1f}ms")


class UserListWidget(QWidget):
    """Widget displaying list of users with their visibility status"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("User List")
        header.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        layout.addWidget(header)
        
        # User table
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["Username", "Distance", "Visibility", "Status"])
        self.user_table.setAlternatingRowColors(True)
        layout.addWidget(self.user_table)
        
        self.setLayout(layout)
    
    def update_users(self, users_data: Dict[str, Any]):
        """Update the user list with current visibility data"""
        visibility_states = users_data.get('visibility_states', {})
        user_positions = users_data.get('user_positions', {})
        
        self.user_table.setRowCount(len(visibility_states))
        
        for row, (user_id, visibility) in enumerate(visibility_states.items()):
            # Username
            username = user_positions.get(user_id, {}).get('username', f'User_{user_id[:8]}')
            self.user_table.setItem(row, 0, QTableWidgetItem(username))
            
            # Distance
            distance = f"{visibility.distance:.1f}m" if visibility.distance != float('inf') else "Unknown"
            self.user_table.setItem(row, 1, QTableWidgetItem(distance))
            
            # Visibility (alpha)
            visibility_percent = f"{visibility.visibility_alpha * 100:.0f}%"
            vis_item = QTableWidgetItem(visibility_percent)
            if visibility.visibility_alpha > 0.8:
                vis_item.setForeground(QColor("#4CAF50"))  # Green
            elif visibility.visibility_alpha > 0.2:
                vis_item.setForeground(QColor("#FF9800"))  # Orange
            else:
                vis_item.setForeground(QColor("#F44336"))  # Red
            self.user_table.setItem(row, 2, vis_item)
            
            # Status
            status = visibility.state.value.replace('_', ' ').title()
            self.user_table.setItem(row, 3, QTableWidgetItem(status))


class SettingsWidget(QWidget):
    """Advanced settings configuration widget"""
    
    settingsChanged = pyqtSignal(VisibilitySettings)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Visibility settings
        vis_group = QGroupBox("Visibility Settings")
        vis_layout = QFormLayout()
        
        self.fade_duration = QDoubleSpinBox()
        self.fade_duration.setRange(0.1, 5.0)
        self.fade_duration.setSingleStep(0.1)
        self.fade_duration.setSuffix("s")
        
        self.update_rate = QDoubleSpinBox()
        self.update_rate.setRange(0.01, 1.0)
        self.update_rate.setSingleStep(0.01)
        self.update_rate.setSuffix("s")
        
        self.use_vertical_distance = QCheckBox()
        self.enable_distance_scaling = QCheckBox()
        
        self.distance_multiplier = QDoubleSpinBox()
        self.distance_multiplier.setRange(0.1, 5.0)
        self.distance_multiplier.setSingleStep(0.1)
        
        vis_layout.addRow("Fade Duration:", self.fade_duration)
        vis_layout.addRow("Update Rate:", self.update_rate)
        vis_layout.addRow("Use Vertical Distance:", self.use_vertical_distance)
        vis_layout.addRow("Enable Distance Scaling:", self.enable_distance_scaling)
        vis_layout.addRow("Distance Multiplier:", self.distance_multiplier)
        
        vis_group.setLayout(vis_layout)
        layout.addWidget(vis_group)
        
        # Connect signals
        self.fade_duration.valueChanged.connect(self.emit_settings_changed)
        self.update_rate.valueChanged.connect(self.emit_settings_changed)
        self.use_vertical_distance.toggled.connect(self.emit_settings_changed)
        self.enable_distance_scaling.toggled.connect(self.emit_settings_changed)
        self.distance_multiplier.valueChanged.connect(self.emit_settings_changed)
        
        self.setLayout(layout)
    
    def emit_settings_changed(self):
        settings = self.get_visibility_settings()
        self.settingsChanged.emit(settings)
    
    def set_visibility_settings(self, settings: VisibilitySettings):
        """Load settings into the UI"""
        self.fade_duration.setValue(settings.fade_duration)
        self.update_rate.setValue(settings.update_rate)
        self.use_vertical_distance.setChecked(settings.use_vertical_distance)
        self.enable_distance_scaling.setChecked(settings.enable_distance_scaling)
        self.distance_multiplier.setValue(settings.distance_multiplier)
    
    def get_visibility_settings(self) -> VisibilitySettings:
        """Get current settings from the UI"""
        return VisibilitySettings(
            fade_duration=self.fade_duration.value(),
            update_rate=self.update_rate.value(),
            use_vertical_distance=self.use_vertical_distance.isChecked(),
            enable_distance_scaling=self.enable_distance_scaling.isChecked(),
            distance_multiplier=self.distance_multiplier.value()
        )


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.config_manager = get_config_manager()
        self.proximity_engine = ProximityEngine(self.config_manager.settings.visibility)
        self.vrchat_integration = VRChatIntegration(
            self.proximity_engine, 
            self.config_manager.settings.vrchat_osc
        )
        
        # UI state
        self.is_running = False
        self.status_data = {}
        
        # Setup UI
        self.setup_ui()
        self.setup_system_tray()
        self.setup_timers()
        
        # Load settings
        self.load_settings()
        
        # Setup window properties
        self.setWindowTitle("VRChat Proximity App")
        self.setMinimumSize(900, 700)
        
        # Apply UI settings
        ui_settings = self.config_manager.settings.ui
        self.resize(ui_settings.window_width, ui_settings.window_height)
        self.move(ui_settings.window_x, ui_settings.window_y)
    
    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Main controls
        controls_group = QGroupBox("Proximity Controls")
        controls_layout = QVBoxLayout()
        
        # Sight distance slider
        self.sight_distance_slider = ProximitySliderWidget(
            "Sight Distance", 1.0, 50.0, 10.0, "m"
        )
        self.sight_distance_slider.valueChanged.connect(self.on_sight_distance_changed)
        controls_layout.addWidget(self.sight_distance_slider)
        
        # Fade distance slider
        self.fade_distance_slider = ProximitySliderWidget(
            "Fade Distance", 0.5, 10.0, 2.0, "m"
        )
        self.fade_distance_slider.valueChanged.connect(self.on_fade_distance_changed)
        controls_layout.addWidget(self.fade_distance_slider)
        
        controls_group.setLayout(controls_layout)
        left_layout.addWidget(controls_group)
        
        # Presets
        presets_group = QGroupBox("Presets")
        presets_layout = QVBoxLayout()
        
        self.preset_combo = QComboBox()
        self.preset_combo.currentTextChanged.connect(self.on_preset_selected)
        presets_layout.addWidget(self.preset_combo)
        
        preset_buttons_layout = QHBoxLayout()
        self.save_preset_btn = QPushButton("Save Preset")
        self.delete_preset_btn = QPushButton("Delete Preset")
        self.save_preset_btn.clicked.connect(self.save_preset)
        self.delete_preset_btn.clicked.connect(self.delete_preset)
        preset_buttons_layout.addWidget(self.save_preset_btn)
        preset_buttons_layout.addWidget(self.delete_preset_btn)
        presets_layout.addLayout(preset_buttons_layout)
        
        presets_group.setLayout(presets_layout)
        left_layout.addWidget(presets_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_stop_btn = QPushButton("Start")
        self.start_stop_btn.clicked.connect(self.toggle_start_stop)
        self.start_stop_btn.setStyleSheet("QPushButton { font-weight: bold; height: 40px; }")
        button_layout.addWidget(self.start_stop_btn)
        
        left_layout.addLayout(button_layout)
        left_layout.addStretch()
        
        # Right panel - Tabs
        tab_widget = QTabWidget()
        
        # Status tab
        self.status_widget = StatusWidget()
        tab_widget.addTab(self.status_widget, "Status")
        
        # User list tab
        self.user_list_widget = UserListWidget()
        tab_widget.addTab(self.user_list_widget, "Users")
        
        # Settings tab
        self.settings_widget = SettingsWidget()
        self.settings_widget.settingsChanged.connect(self.on_advanced_settings_changed)
        tab_widget.addTab(self.settings_widget, "Advanced")
        
        # Debug tab (if debug info is enabled)
        if self.config_manager.settings.ui.show_debug_info:
            self.debug_text = QTextBrowser()
            self.debug_text.setFont(QFont("Consolas", 9))
            tab_widget.addTab(self.debug_text, "Debug")
        
        # Add panels to main layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(tab_widget)
        splitter.setSizes([400, 500])
        
        main_layout.addWidget(splitter)
    
    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            # Set a simple colored icon (in production, use proper icon files)
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor("#4CAF50"))
            self.tray_icon.setIcon(QIcon(pixmap))
            
            # Context menu
            tray_menu = QMenu()
            
            show_action = QAction("Show", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)
            
            start_stop_action = QAction("Start/Stop", self)
            start_stop_action.triggered.connect(self.toggle_start_stop)
            tray_menu.addAction(start_stop_action)
            
            tray_menu.addSeparator()
            
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.quit_application)
            tray_menu.addAction(quit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self.tray_icon_activated)
            
            if self.config_manager.settings.ui.minimize_to_tray:
                self.tray_icon.show()
    
    def setup_timers(self):
        """Setup update timers"""
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_display)
        self.status_timer.start(1000 // self.config_manager.settings.ui.update_frequency)
        
        # Auto-save timer
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.auto_save_settings)
        self.autosave_timer.start(30000)  # Auto-save every 30 seconds
    
    def load_settings(self):
        """Load settings into UI controls"""
        settings = self.config_manager.settings.visibility
        
        self.sight_distance_slider.set_value(settings.sight_distance)
        self.fade_distance_slider.set_value(settings.fade_distance)
        self.settings_widget.set_visibility_settings(settings)
        
        # Load presets
        self.preset_combo.clear()
        for preset in self.config_manager.settings.presets:
            self.preset_combo.addItem(preset.name)
    
    def save_settings(self):
        """Save current settings"""
        # Update visibility settings
        current_settings = VisibilitySettings(
            sight_distance=self.sight_distance_slider.get_value(),
            fade_distance=self.fade_distance_slider.get_value()
        )
        
        # Get advanced settings
        advanced_settings = self.settings_widget.get_visibility_settings()
        current_settings.fade_duration = advanced_settings.fade_duration
        current_settings.update_rate = advanced_settings.update_rate
        current_settings.use_vertical_distance = advanced_settings.use_vertical_distance
        current_settings.enable_distance_scaling = advanced_settings.enable_distance_scaling
        current_settings.distance_multiplier = advanced_settings.distance_multiplier
        
        self.config_manager.update_visibility_settings(current_settings)
        
        # Update UI settings
        ui_settings = self.config_manager.settings.ui
        ui_settings.window_width = self.width()
        ui_settings.window_height = self.height()
        ui_settings.window_x = self.x()
        ui_settings.window_y = self.y()
        self.config_manager.update_ui_settings(ui_settings)
    
    def auto_save_settings(self):
        """Auto-save settings periodically"""
        self.save_settings()
    
    def on_sight_distance_changed(self, value: float):
        """Handle sight distance slider changes"""
        if self.is_running:
            current_settings = self.proximity_engine.settings
            current_settings.sight_distance = value
            self.proximity_engine.update_settings(current_settings)
    
    def on_fade_distance_changed(self, value: float):
        """Handle fade distance slider changes"""
        if self.is_running:
            current_settings = self.proximity_engine.settings
            current_settings.fade_distance = value
            self.proximity_engine.update_settings(current_settings)
    
    def on_advanced_settings_changed(self, settings: VisibilitySettings):
        """Handle advanced settings changes"""
        if self.is_running:
            # Preserve the current sight and fade distances
            settings.sight_distance = self.sight_distance_slider.get_value()
            settings.fade_distance = self.fade_distance_slider.get_value()
            self.proximity_engine.update_settings(settings)
    
    def on_preset_selected(self, preset_name: str):
        """Handle preset selection"""
        if preset_name:
            preset = self.config_manager.get_preset(preset_name)
            if preset:
                settings = preset.visibility_settings
                self.sight_distance_slider.set_value(settings.sight_distance)
                self.fade_distance_slider.set_value(settings.fade_distance)
                self.settings_widget.set_visibility_settings(settings)
                
                if self.is_running:
                    self.proximity_engine.update_settings(settings)
    
    def save_preset(self):
        """Save current settings as a preset"""
        # This would open a dialog to get preset name
        # For now, using a simple approach
        preset_name = f"Preset_{int(time.time())}"
        
        current_settings = VisibilitySettings(
            sight_distance=self.sight_distance_slider.get_value(),
            fade_distance=self.fade_distance_slider.get_value()
        )
        
        preset = PresetSettings(
            name=preset_name,
            description=f"Sight: {current_settings.sight_distance}m, Fade: {current_settings.fade_distance}m",
            visibility_settings=current_settings,
            created_time=time.time()
        )
        
        if self.config_manager.add_preset(preset):
            self.preset_combo.addItem(preset_name)
    
    def delete_preset(self):
        """Delete the selected preset"""
        current_preset = self.preset_combo.currentText()
        if current_preset:
            reply = QMessageBox.question(
                self, 'Delete Preset',
                f'Are you sure you want to delete preset "{current_preset}"?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.config_manager.remove_preset(current_preset):
                    self.preset_combo.removeItem(self.preset_combo.currentIndex())
    
    async def start_application(self):
        """Start the proximity engine and VRChat integration"""
        try:
            await self.proximity_engine.start()
            await self.vrchat_integration.start()
            self.is_running = True
            self.start_stop_btn.setText("Stop")
            self.start_stop_btn.setStyleSheet("QPushButton { font-weight: bold; height: 40px; background-color: #F44336; }")
            logger.info("Application started")
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start application: {e}")
    
    async def stop_application(self):
        """Stop the proximity engine and VRChat integration"""
        try:
            await self.proximity_engine.stop()
            await self.vrchat_integration.stop()
            self.is_running = False
            self.start_stop_btn.setText("Start")
            self.start_stop_btn.setStyleSheet("QPushButton { font-weight: bold; height: 40px; background-color: #4CAF50; }")
            logger.info("Application stopped")
        except Exception as e:
            logger.error(f"Failed to stop application: {e}")
    
    def toggle_start_stop(self):
        """Toggle between start and stop"""
        if self.is_running:
            self._run_async_task(self.stop_application)
        else:
            self._run_async_task(self.start_application)
    
    def _run_async_task(self, async_func):
        """Helper to run async tasks safely in PyQt"""
        def run_in_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(async_func())
            except Exception as e:
                logger.error(f"Error in async task: {e}")
            finally:
                try:
                    loop.close()
                except:
                    pass
        
        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()
    
    def update_status_display(self):
        """Update the status display"""
        # Gather status data
        self.status_data = {
            'vrchat_connected': self.vrchat_integration.running if hasattr(self.vrchat_integration, 'running') else False,
            'total_users': len(self.proximity_engine.users),
            'visible_users': len(self.proximity_engine.get_visible_users()),
            'update_rate': 1.0 / self.proximity_engine.settings.update_rate if self.proximity_engine.settings.update_rate > 0 else 0,
            'processing_time': 5.0,  # Placeholder
        }
        
        # Update widgets
        self.status_widget.update_status(self.status_data)
        
        # Update user list
        users_data = {
            'visibility_states': self.proximity_engine.visibility_states,
            'user_positions': {uid: {'username': pos.username} for uid, pos in self.proximity_engine.users.items()}
        }
        self.user_list_widget.update_users(users_data)
        
        # Update debug info if available
        if hasattr(self, 'debug_text'):
            debug_info = f"""
Engine Status: {'Running' if self.is_running else 'Stopped'}
Local User Set: {self.proximity_engine.local_user is not None}
Tracked Users: {len(self.proximity_engine.users)}
Visible Users: {len(self.proximity_engine.get_visible_users())}
World Scale: {self.proximity_engine.world_scale}
Sight Distance: {self.proximity_engine.settings.sight_distance}m
Fade Distance: {self.proximity_engine.settings.fade_distance}m
Update Rate: {self.proximity_engine.settings.update_rate}s
"""
            self.debug_text.setText(debug_info.strip())
    
    def tray_icon_activated(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.config_manager.settings.ui.minimize_to_tray and QSystemTrayIcon.isSystemTrayAvailable():
            self.hide()
            event.ignore()
        else:
            self.quit_application()
            event.accept()
    
    def quit_application(self):
        """Quit the entire application"""
        self.save_settings()
        if self.is_running:
            self._run_async_task(self.stop_application)
        QApplication.quit()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("VRChat Proximity App")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("VRChat Proximity")
    
    # Create main window
    window = MainWindow()
    
    # Show window or start minimized
    config = get_config_manager()
    if config.settings.ui.start_minimized:
        window.hide()
    else:
        window.show()
    
    # Start the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
