#!/usr/bin/env python3
"""
VRChat Proximity Engine - Environment Setup
Automatically sets up the environment for GitHub users
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("VRChat Hybrid Proximity Engine - Environment Setup")
    print("=" * 60)
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    
    # Install Python dependencies
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--user', '--upgrade',
            'websocket-client', 'requests', 'PyQt6', 'numpy', 'opencv-python', 'PyYAML'
        ], check=True, capture_output=True)
        print("✅ Python dependencies installed")
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install Python dependencies")
        print("Manual install: pip install websocket-client requests PyQt6 numpy opencv-python PyYAML")
    
    # Check for optional compilers
    print("\n🔍 Checking for optional performance components...")
    
    # Check for Go
    try:
        result = subprocess.run(['go', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Go compiler found - high-performance networking available")
            try_compile_go()
        else:
            print("⚠️  Go compiler not found - using Python networking fallback")
            print("   Install Go from https://golang.org/ for better performance")
    except FileNotFoundError:
        print("⚠️  Go compiler not found - using Python networking fallback")
        print("   Install Go from https://golang.org/ for better performance")
    
    # Check for Zig
    try:
        result = subprocess.run(['zig', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Zig compiler found - ultra-fast vision processing available")
            try_compile_zig()
        else:
            print("⚠️  Zig compiler not found - using Python OpenCV fallback")
            print("   Install Zig from https://ziglang.org/ for maximum performance")
    except FileNotFoundError:
        print("⚠️  Zig compiler not found - using Python OpenCV fallback")  
        print("   Install Zig from https://ziglang.org/ for maximum performance")
    
    # Create config directory
    create_default_config()
    
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Start VRChat and make sure it's visible on screen")
    print("2. Run: python hybrid_proximity_engine.py")
    print("3. Click 'Start Hybrid Engine' in the GUI")
    print("4. Enjoy proximity detection in any VRChat world!")
    print()
    print("No OSC setup required - just visual detection! 🚀")
    print()
    
    return True

def try_compile_go():
    """Try to compile the Go networking module"""
    try:
        # Initialize Go module if needed
        if not Path("go.mod").exists():
            subprocess.run(["go", "mod", "init", "vrchat-proximity"], cwd=".", check=True)
            subprocess.run(["go", "mod", "tidy"], cwd=".", check=True)
        
        # Try to compile
        result = subprocess.run(["go", "build", "fast_network.go"], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Go module compiled successfully")
            # Clean up executable
            exe_file = Path("fast_network.exe")
            if exe_file.exists():
                exe_file.unlink()
        else:
            print("  ⚠️  Go compilation failed - using fallback")
    except Exception as e:
        print(f"  ⚠️  Go setup failed: {e}")

def try_compile_zig():
    """Try to compile the Zig vision module"""
    try:
        result = subprocess.run([
            "zig", "build-lib", "fast_vision.zig", 
            "-dynamic", "-O", "ReleaseFast", 
            "--name", "fast_vision"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ Zig module compiled successfully")
        else:
            print("  ⚠️  Zig compilation failed - using fallback")
    except Exception as e:
        print(f"  ⚠️  Zig setup failed: {e}")

def create_default_config():
    """Create default configuration files"""
    print("\n📁 Creating configuration files...")
    
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Default settings
    default_config = config_dir / "default_settings.yaml"
    if not default_config.exists():
        with open(default_config, 'w') as f:
            f.write("""# VRChat Proximity Engine - Default Settings
sight_distance: 25
fade_distance: 5
target_fps: 30
detection_threshold: 0.3
use_zig_acceleration: true
use_go_backend: true
log_level: INFO
""")
    
    # Close range preset
    close_config = config_dir / "preset_close_range.yaml"
    if not close_config.exists():
        with open(close_config, 'w') as f:
            f.write("""# Close Range Preset - For small rooms/intimate spaces
sight_distance: 8
fade_distance: 2
detection_threshold: 0.4
target_fps: 60
""")
    
    # Long range preset
    long_config = config_dir / "preset_long_range.yaml"
    if not long_config.exists():
        with open(long_config, 'w') as f:
            f.write("""# Long Range Preset - For large worlds/events  
sight_distance: 100
fade_distance: 20
detection_threshold: 0.2
target_fps: 30
""")
    
    # Examples directory
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    basic_example = examples_dir / "basic_usage.py"
    if not basic_example.exists():
        with open(basic_example, 'w') as f:
            f.write('''"""Basic usage example for VRChat Proximity Engine"""
from hybrid_proximity_engine import HybridProximityEngine

def main():
    # Create and start the engine
    engine = HybridProximityEngine()
    engine.run()

if __name__ == "__main__":
    main()
''')
    
    print("✅ Configuration files created")

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)
