@echo off
title Building VRChat Proximity App
echo ===============================================
echo VRChat Proximity App - Standalone Builder
echo ===============================================
echo.
echo This will create a standalone .exe file that
echo can run without Python installation.
echo.
echo Building process will:
echo 1. Install PyInstaller if needed
echo 2. Install all dependencies
echo 3. Build standalone executable
echo 4. Create portable package
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul
echo.

python build_standalone.py

echo.
echo Build process completed!
echo Check the dist/VRChatProximityApp/ folder for your executable.
echo.
pause
