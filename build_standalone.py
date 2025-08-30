#!/usr/bin/env python3
"""
Build script to create standalone executable for VRChat Proximity App
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} is available")
        return True
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install PyInstaller: {e}")
            return False

def install_dependencies():
    """Install all required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"🧹 Cleaning {dir_name}/")
            shutil.rmtree(dir_path)
    
    # Clean .pyc files
    for pyc_file in Path(".").rglob("*.pyc"):
        pyc_file.unlink()
    
    print("✅ Build directories cleaned")

def build_executable():
    """Build the standalone executable"""
    print("🔨 Building standalone executable...")
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm", 
        "build_standalone.spec"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("✅ Build completed successfully!")
            return True
        else:
            print(f"❌ Build failed with return code {result.returncode}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_portable_package():
    """Create a portable package with launcher and documentation"""
    print("📦 Creating portable package...")
    
    dist_dir = Path("dist")
    app_dir = dist_dir / "VRChatProximityApp"
    
    if not app_dir.exists():
        print("❌ Built application not found")
        return False
    
    # Create portable launcher script
    launcher_script = app_dir / "launch.bat"
    with open(launcher_script, "w") as f:
        f.write("""@echo off
title VRChat Proximity App
echo ============================================
echo VRChat Proximity Visibility App v1.0.0
echo ============================================
echo.
echo Starting application...
echo Make sure VRChat is running with OSC enabled!
echo.

VRChatProximityApp.exe

echo.
echo Application closed. Press any key to exit...
pause >nul
""")
    
    # Create quick setup guide
    setup_guide = app_dir / "QUICK_START.txt"
    with open(setup_guide, "w") as f:
        f.write("""VRChat Proximity App - Quick Start Guide
========================================

REQUIREMENTS:
1. VRChat must be running
2. OSC must be enabled in VRChat settings (Settings > OSC > Enabled)

SETUP STEPS:
1. Start VRChat and join a world with other users
2. Double-click launch.bat (or VRChatProximityApp.exe directly)
3. Click the "Start" button in the app
4. Adjust the "Sight Distance" slider to control visibility range
5. Users beyond your sight distance will be hidden

FEATURES:
- Sight Distance: How far you can see other users (1-50 meters)
- Fade Distance: Smooth transition zone for appearing/disappearing users
- Presets: Quick settings for different scenarios
- Status Tab: Monitor connection and user statistics
- Users Tab: See all tracked users and their visibility status

TROUBLESHOOTING:
- Make sure VRChat OSC is enabled
- Ensure no firewall is blocking ports 9000/9001
- Try restarting both VRChat and this app if connection fails
- Check the logs folder for detailed error information

VR USERS:
- Install SteamVR for VR overlay support
- Press menu button on VR controller to toggle overlay
- Use touchpad for fine distance control

For more help, see README.md or visit the project page.
""")
    
    # Copy important files
    files_to_copy = ["README.md", "PROJECT_STATUS.md"]
    for filename in files_to_copy:
        src = Path(filename)
        if src.exists():
            shutil.copy2(src, app_dir / filename)
    
    print(f"✅ Portable package created in: {app_dir}")
    return True

def main():
    """Main build process"""
    print("🚀 VRChat Proximity App - Standalone Build Process")
    print("=" * 50)
    
    # Check system
    print(f"🖥️  Platform: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print()
    
    # Step 1: Check PyInstaller
    if not check_pyinstaller():
        sys.exit(1)
    
    # Step 2: Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Step 3: Clean previous builds
    clean_build_dirs()
    
    # Step 4: Build executable
    if not build_executable():
        sys.exit(1)
    
    # Step 5: Create portable package
    if not create_portable_package():
        sys.exit(1)
    
    print("\n🎉 BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print(f"📁 Executable location: dist/VRChatProximityApp/")
    print(f"🚀 Run: dist/VRChatProximityApp/launch.bat")
    print("\n💡 Tips:")
    print("- Make sure VRChat is running with OSC enabled")
    print("- The entire dist/VRChatProximityApp/ folder is portable")
    print("- You can copy this folder to any Windows PC and run it")
    print("\nEnjoy your VRChat proximity control! 🎮")

if __name__ == "__main__":
    main()
