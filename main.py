#!/usr/bin/env python3
"""
VRChat Proximity App - Main Entry Point
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ui.main_window import main as gui_main
from src.config.settings import get_config_manager


def setup_logging():
    """Set up application logging"""
    config = get_config_manager()
    log_level = getattr(logging, config.settings.log_level.upper(), logging.INFO)
    
    # Create logs directory
    log_dir = config.data_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Set up logging configuration
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "vrchat_proximity.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("src.core").setLevel(log_level)
    logging.getLogger("src.integration").setLevel(log_level)
    logging.getLogger("src.ui").setLevel(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("VRChat Proximity App starting up")
    logger.info(f"Log level set to: {config.settings.log_level}")


def check_dependencies():
    """Check if required dependencies are available"""
    logger = logging.getLogger(__name__)
    missing_deps = []
    
    # Check PyQt6
    try:
        import PyQt6
        logger.info(f"PyQt6 version: {PyQt6.QtCore.PYQT_VERSION_STR}")
    except ImportError:
        missing_deps.append("PyQt6")
    
    # Check numpy
    try:
        import numpy
        logger.info(f"NumPy version: {numpy.__version__}")
    except ImportError:
        missing_deps.append("numpy")
    
    # Check python-osc
    try:
        from pythonosc import udp_client
        logger.info("python-osc available")
    except ImportError:
        missing_deps.append("python-osc")
    
    # Check PyYAML
    try:
        import yaml
        logger.info("PyYAML available")
    except ImportError:
        missing_deps.append("PyYAML")
    
    # Check optional dependencies
    try:
        import openvr
        logger.info("OpenVR available - VR functionality enabled")
    except ImportError:
        logger.warning("OpenVR not available - VR functionality disabled")
    
    if missing_deps:
        logger.error(f"Missing required dependencies: {', '.join(missing_deps)}")
        print(f"\nError: Missing required dependencies: {', '.join(missing_deps)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_deps)}")
        return False
    
    return True


def print_startup_info():
    """Print application startup information"""
    config = get_config_manager()
    
    print("=" * 60)
    print("VRChat Proximity App - Proximity-Based User Visibility")
    print("=" * 60)
    print(f"Version: 1.0.0")
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Config directory: {config.config_dir}")
    print(f"Data directory: {config.data_dir}")
    print("=" * 60)
    print()


def main():
    """Main application entry point"""
    try:
        # Print startup information
        print_startup_info()
        
        # Set up logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Load configuration
        config = get_config_manager()
        logger.info("Configuration loaded successfully")
        
        # Print configuration info
        config_info = config.get_config_info()
        logger.info(f"Config file exists: {config_info['config_exists']}")
        logger.info(f"Backup count: {config_info['backup_count']}")
        
        # Start the GUI application
        logger.info("Starting GUI application")
        gui_main()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nFatal error: {e}")
        print("Check the log file for more details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
