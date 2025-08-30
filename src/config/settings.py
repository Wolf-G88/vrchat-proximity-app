"""
Configuration and Settings Management System
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
from platformdirs import user_config_dir, user_data_dir
from ..core.proximity_engine import VisibilitySettings
from ..integration.vrchat_osc import VRChatOSCConfig

logger = logging.getLogger(__name__)


@dataclass
class UISettings:
    """User interface settings"""
    theme: str = "dark"
    window_width: int = 800
    window_height: int = 600
    window_x: int = 100
    window_y: int = 100
    always_on_top: bool = False
    minimize_to_tray: bool = True
    start_minimized: bool = False
    show_debug_info: bool = False
    update_frequency: int = 60  # UI update frequency in Hz


@dataclass
class VRSettings:
    """VR-specific settings"""
    enable_vr_overlay: bool = True
    overlay_width: float = 0.3
    overlay_distance: float = 1.0
    overlay_alpha: float = 0.8
    controller_binding_left: str = "trigger"
    controller_binding_right: str = "grip"
    haptic_feedback: bool = True
    auto_hide_desktop_ui: bool = True


@dataclass
class PresetSettings:
    """Individual preset configuration"""
    name: str
    description: str
    visibility_settings: VisibilitySettings
    created_time: float
    last_used: float = 0.0


@dataclass
class AppSettings:
    """Main application settings container"""
    visibility: VisibilitySettings
    vrchat_osc: VRChatOSCConfig
    ui: UISettings
    vr: VRSettings
    presets: List[PresetSettings]
    auto_start_with_vrchat: bool = True
    check_for_updates: bool = True
    send_anonymous_analytics: bool = False
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Ensure all nested dataclasses are properly initialized"""
        if not isinstance(self.visibility, VisibilitySettings):
            if isinstance(self.visibility, dict):
                self.visibility = VisibilitySettings(**self.visibility)
            else:
                self.visibility = VisibilitySettings()
        
        if not isinstance(self.vrchat_osc, VRChatOSCConfig):
            if isinstance(self.vrchat_osc, dict):
                self.vrchat_osc = VRChatOSCConfig(**self.vrchat_osc)
            else:
                self.vrchat_osc = VRChatOSCConfig()
        
        if not isinstance(self.ui, UISettings):
            if isinstance(self.ui, dict):
                self.ui = UISettings(**self.ui)
            else:
                self.ui = UISettings()
        
        if not isinstance(self.vr, VRSettings):
            if isinstance(self.vr, dict):
                self.vr = VRSettings(**self.vr)
            else:
                self.vr = VRSettings()
        
        # Convert preset dictionaries to PresetSettings objects
        converted_presets = []
        for preset in self.presets:
            if isinstance(preset, dict):
                if 'visibility_settings' in preset and isinstance(preset['visibility_settings'], dict):
                    preset['visibility_settings'] = VisibilitySettings(**preset['visibility_settings'])
                converted_presets.append(PresetSettings(**preset))
            else:
                converted_presets.append(preset)
        self.presets = converted_presets


class ConfigManager:
    """Manages application configuration and settings persistence"""
    
    def __init__(self, app_name: str = "VRChatProximityApp"):
        self.app_name = app_name
        
        # Set up directories
        self.config_dir = Path(user_config_dir(app_name))
        self.data_dir = Path(user_data_dir(app_name))
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.config_file = self.config_dir / "settings.yaml"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Current settings
        self.settings: Optional[AppSettings] = None
        
        # Load settings on initialization
        self.load_settings()
    
    def get_default_settings(self) -> AppSettings:
        """Create default application settings"""
        return AppSettings(
            visibility=VisibilitySettings(),
            vrchat_osc=VRChatOSCConfig(),
            ui=UISettings(),
            vr=VRSettings(),
            presets=[
                PresetSettings(
                    name="Default",
                    description="Default proximity settings",
                    visibility_settings=VisibilitySettings(),
                    created_time=0.0
                ),
                PresetSettings(
                    name="Close Range",
                    description="Only see users very close to you",
                    visibility_settings=VisibilitySettings(
                        sight_distance=5.0,
                        fade_distance=1.0
                    ),
                    created_time=0.0
                ),
                PresetSettings(
                    name="Long Range",
                    description="See users from far away",
                    visibility_settings=VisibilitySettings(
                        sight_distance=25.0,
                        fade_distance=5.0
                    ),
                    created_time=0.0
                ),
                PresetSettings(
                    name="Performance",
                    description="Optimized for performance",
                    visibility_settings=VisibilitySettings(
                        sight_distance=10.0,
                        fade_distance=2.0,
                        update_rate=0.2,
                        fade_duration=0.5
                    ),
                    created_time=0.0
                )
            ]
        )
    
    def load_settings(self) -> AppSettings:
        """Load settings from configuration file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                if data:
                    self.settings = AppSettings(**data)
                    logger.info(f"Loaded settings from {self.config_file}")
                else:
                    self.settings = self.get_default_settings()
                    logger.info("Config file empty, using default settings")
            else:
                self.settings = self.get_default_settings()
                logger.info("No config file found, using default settings")
        
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            logger.info("Using default settings")
            self.settings = self.get_default_settings()
        
        return self.settings
    
    def save_settings(self, backup: bool = True) -> bool:
        """Save current settings to configuration file"""
        try:
            if not self.settings:
                logger.warning("No settings to save")
                return False
            
            # Create backup if requested
            if backup and self.config_file.exists():
                self._create_backup()
            
            # Convert settings to dictionary
            settings_dict = asdict(self.settings)
            
            # Save to YAML file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(settings_dict, f, default_flow_style=False, indent=2)
            
            logger.info(f"Settings saved to {self.config_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def _create_backup(self):
        """Create a backup of the current configuration"""
        try:
            import time
            timestamp = int(time.time())
            backup_file = self.backup_dir / f"settings_backup_{timestamp}.yaml"
            
            # Copy current config to backup
            import shutil
            shutil.copy2(self.config_file, backup_file)
            
            # Keep only the last 10 backups
            backups = sorted(self.backup_dir.glob("settings_backup_*.yaml"))
            while len(backups) > 10:
                oldest = backups.pop(0)
                oldest.unlink()
            
            logger.debug(f"Created backup: {backup_file}")
        
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
    
    def update_visibility_settings(self, settings: VisibilitySettings):
        """Update visibility settings and save"""
        if self.settings:
            self.settings.visibility = settings
            self.save_settings()
    
    def update_vrchat_osc_settings(self, settings: VRChatOSCConfig):
        """Update VRChat OSC settings and save"""
        if self.settings:
            self.settings.vrchat_osc = settings
            self.save_settings()
    
    def update_ui_settings(self, settings: UISettings):
        """Update UI settings and save"""
        if self.settings:
            self.settings.ui = settings
            self.save_settings()
    
    def update_vr_settings(self, settings: VRSettings):
        """Update VR settings and save"""
        if self.settings:
            self.settings.vr = settings
            self.save_settings()
    
    def add_preset(self, preset: PresetSettings) -> bool:
        """Add a new preset"""
        if not self.settings:
            return False
        
        # Check if name already exists
        existing_names = [p.name for p in self.settings.presets]
        if preset.name in existing_names:
            logger.warning(f"Preset '{preset.name}' already exists")
            return False
        
        import time
        preset.created_time = time.time()
        self.settings.presets.append(preset)
        self.save_settings()
        
        logger.info(f"Added preset: {preset.name}")
        return True
    
    def remove_preset(self, preset_name: str) -> bool:
        """Remove a preset by name"""
        if not self.settings:
            return False
        
        original_count = len(self.settings.presets)
        self.settings.presets = [p for p in self.settings.presets if p.name != preset_name]
        
        if len(self.settings.presets) < original_count:
            self.save_settings()
            logger.info(f"Removed preset: {preset_name}")
            return True
        else:
            logger.warning(f"Preset '{preset_name}' not found")
            return False
    
    def get_preset(self, preset_name: str) -> Optional[PresetSettings]:
        """Get a preset by name"""
        if not self.settings:
            return None
        
        for preset in self.settings.presets:
            if preset.name == preset_name:
                return preset
        
        return None
    
    def apply_preset(self, preset_name: str) -> bool:
        """Apply a preset to current visibility settings"""
        preset = self.get_preset(preset_name)
        if not preset:
            logger.warning(f"Preset '{preset_name}' not found")
            return False
        
        if self.settings:
            import time
            preset.last_used = time.time()
            self.settings.visibility = preset.visibility_settings
            self.save_settings()
            logger.info(f"Applied preset: {preset_name}")
            return True
        
        return False
    
    def export_settings(self, file_path: Path) -> bool:
        """Export settings to a file"""
        try:
            if not self.settings:
                return False
            
            settings_dict = asdict(self.settings)
            
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(settings_dict, f, indent=2)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(settings_dict, f, default_flow_style=False, indent=2)
            
            logger.info(f"Settings exported to {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, file_path: Path) -> bool:
        """Import settings from a file"""
        try:
            if not file_path.exists():
                logger.error(f"Import file not found: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)
            
            if data:
                # Create backup before importing
                self._create_backup()
                
                self.settings = AppSettings(**data)
                self.save_settings(backup=False)  # Don't create another backup
                
                logger.info(f"Settings imported from {file_path}")
                return True
        
        except Exception as e:
            logger.error(f"Error importing settings: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        try:
            # Create backup before resetting
            if self.config_file.exists():
                self._create_backup()
            
            self.settings = self.get_default_settings()
            self.save_settings(backup=False)
            
            logger.info("Settings reset to defaults")
            return True
        
        except Exception as e:
            logger.error(f"Error resetting settings: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get information about configuration directories and files"""
        return {
            'config_dir': str(self.config_dir),
            'data_dir': str(self.data_dir),
            'config_file': str(self.config_file),
            'config_exists': self.config_file.exists(),
            'backup_dir': str(self.backup_dir),
            'backup_count': len(list(self.backup_dir.glob("settings_backup_*.yaml"))),
            'settings_loaded': self.settings is not None
        }


# Global config manager instance
_config_manager: Optional[ConfigManager] = None

def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_settings() -> AppSettings:
    """Get current application settings"""
    return get_config_manager().settings
