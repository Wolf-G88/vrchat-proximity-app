@echo off
title Building VRChat Proximity Engine NSIS Installer

echo.
echo =================================================================
echo    Building VRChat Proximity Engine NSIS Installer
echo    (Easier alternative to MSI - creates professional EXE)
echo =================================================================
echo.

:: Check for NSIS
where makensis.exe >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: NSIS not found
    echo Please install NSIS 3.0+ from:
    echo https://nsis.sourceforge.io/Download
    echo.
    echo Or install via Chocolatey:
    echo   choco install nsis
    echo.
    pause
    exit /b 1
)

echo Found: NSIS
echo.

:: Create required directories if they don't exist
echo Creating installer assets...

:: Create config directory with sample files
if not exist "config" mkdir config
if not exist "config\default_settings.yaml" (
    echo # VRChat Proximity Engine - Default Settings > config\default_settings.yaml
    echo # Sight distance in meters >> config\default_settings.yaml
    echo sight_distance: 25 >> config\default_settings.yaml
    echo. >> config\default_settings.yaml
    echo # Fade distance in meters >> config\default_settings.yaml
    echo fade_distance: 5 >> config\default_settings.yaml
    echo. >> config\default_settings.yaml
    echo # Detection confidence threshold ^(0.0-1.0^) >> config\default_settings.yaml
    echo detection_threshold: 0.3 >> config\default_settings.yaml
    echo. >> config\default_settings.yaml
    echo # Target frames per second >> config\default_settings.yaml
    echo target_fps: 30 >> config\default_settings.yaml
    echo. >> config\default_settings.yaml
    echo # Enable Zig acceleration >> config\default_settings.yaml
    echo use_zig_acceleration: true >> config\default_settings.yaml
    echo. >> config\default_settings.yaml
    echo # Enable Go networking >> config\default_settings.yaml
    echo use_go_backend: true >> config\default_settings.yaml
)

if not exist "config\preset_close_range.yaml" (
    echo # Close Range Preset - For small rooms/intimate spaces > config\preset_close_range.yaml
    echo sight_distance: 8 >> config\preset_close_range.yaml
    echo fade_distance: 2 >> config\preset_close_range.yaml
    echo detection_threshold: 0.4 >> config\preset_close_range.yaml
    echo target_fps: 60 >> config\preset_close_range.yaml
)

if not exist "config\preset_long_range.yaml" (
    echo # Long Range Preset - For large worlds/events > config\preset_long_range.yaml
    echo sight_distance: 100 >> config\preset_long_range.yaml
    echo fade_distance: 20 >> config\preset_long_range.yaml
    echo detection_threshold: 0.2 >> config\preset_long_range.yaml
    echo target_fps: 30 >> config\preset_long_range.yaml
)

:: Create examples directory
if not exist "examples" mkdir examples
if not exist "examples\basic_usage.py" (
    echo """Basic usage example for VRChat Proximity Engine""" > examples\basic_usage.py
    echo. >> examples\basic_usage.py
    echo from hybrid_proximity_engine import HybridProximityEngine >> examples\basic_usage.py
    echo. >> examples\basic_usage.py
    echo def main^(^): >> examples\basic_usage.py
    echo     # Create and start the engine >> examples\basic_usage.py
    echo     engine = HybridProximityEngine^(^) >> examples\basic_usage.py
    echo     engine.run^(^) >> examples\basic_usage.py
    echo. >> examples\basic_usage.py
    echo if __name__ == "__main__": >> examples\basic_usage.py
    echo     main^(^) >> examples\basic_usage.py
)

if not exist "examples\advanced_configuration.py" (
    echo """Advanced configuration example""" > examples\advanced_configuration.py
    echo. >> examples\advanced_configuration.py
    echo from hybrid_proximity_engine import HybridProximityEngine >> examples\advanced_configuration.py
    echo. >> examples\advanced_configuration.py
    echo def main^(^): >> examples\advanced_configuration.py
    echo     # Create engine with custom settings >> examples\advanced_configuration.py
    echo     engine = HybridProximityEngine^(^) >> examples\advanced_configuration.py
    echo. >> examples\advanced_configuration.py
    echo     # Configure for high performance >> examples\advanced_configuration.py
    echo     # engine.set_target_fps^(60^) >> examples\advanced_configuration.py
    echo. >> examples\advanced_configuration.py
    echo     # Start the engine >> examples\advanced_configuration.py
    echo     engine.run^(^) >> examples\advanced_configuration.py
    echo. >> examples\advanced_configuration.py
    echo if __name__ == "__main__": >> examples\advanced_configuration.py
    echo     main^(^) >> examples\advanced_configuration.py
)

:: Create placeholder icons (NSIS can work without real ICO files)
if not exist "icons" mkdir icons
echo Creating placeholder icon files...
echo PLACEHOLDER ICO FILE > icons\app_icon.ico
echo PLACEHOLDER ICO FILE > icons\config_icon.ico
echo PLACEHOLDER ICO FILE > icons\docs_icon.ico

:: Create placeholder images  
if not exist "images" mkdir images
echo Creating placeholder image files...
echo PLACEHOLDER BMP FILE > images\header.bmp
echo PLACEHOLDER BMP FILE > images\welcome.bmp

:: Create license file
if not exist "license" mkdir license
if not exist "license\license.txt" (
    echo VRChat Hybrid Proximity Engine > license\license.txt
    echo License Agreement >> license\license.txt
    echo. >> license\license.txt
    echo Copyright ^(c^) 2024 Wolf Clan Family. All rights reserved. >> license\license.txt
    echo. >> license\license.txt
    echo This software is provided "as is" without warranty of any kind. >> license\license.txt
    echo Use at your own risk. >> license\license.txt
    echo. >> license\license.txt
    echo By installing this software, you agree to these terms. >> license\license.txt
)

:: Build the installer
echo.
echo Building NSIS installer...
echo.

makensis.exe VRChatProximity.nsi

if %errorlevel% equ 0 (
    echo.
    echo =================================================================
    echo SUCCESS: NSIS installer created successfully!
    echo.
    echo Output: VRChatProximityEngine-1.0.0-Setup.exe
    echo.
    if exist "VRChatProximityEngine-1.0.0-Setup.exe" (
        for %%I in ("VRChatProximityEngine-1.0.0-Setup.exe") do echo Size: %%~zI bytes
    )
    echo.
    echo The installer includes:
    echo   ✓ Professional Windows installer ^(EXE^)
    echo   ✓ Start menu and desktop shortcuts
    echo   ✓ Automatic Python dependency installation
    echo   ✓ Configuration presets
    echo   ✓ Example code
    echo   ✓ Proper uninstall support
    echo   ✓ Registry integration
    echo   ✓ File associations
    echo   ✓ Admin privileges handling
    echo.
    echo Ready for distribution!
    echo =================================================================
    echo.
    
    :: Optional: Test the installer
    set /p test_install="Test the installer now? (y/n): "
    if /i "%test_install%"=="y" (
        echo Testing installer...
        start VRChatProximityEngine-1.0.0-Setup.exe
    )
    
) else (
    echo.
    echo ERROR: NSIS installer build failed
    echo Check the error messages above for details
    pause
    exit /b 1
)

echo Build complete!
pause
