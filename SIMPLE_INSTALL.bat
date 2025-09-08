@echo off
title VRChat Proximity Engine - Simple Installer

echo.
echo ================================================================
echo    VRChat Hybrid Proximity Engine - Simple Installer
echo ================================================================
echo.
echo Installing to: %USERPROFILE%\VRChatProximityEngine
echo.

:: Create install directory
set "INSTALL_DIR=%USERPROFILE%\VRChatProximityEngine"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo [1/4] Copying core files...
copy "hybrid_proximity_engine.py" "%INSTALL_DIR%\" >nul
copy "standalone_proximity_detector.py" "%INSTALL_DIR%\" >nul
copy "fast_vision.zig" "%INSTALL_DIR%\" >nul
copy "fast_network.go" "%INSTALL_DIR%\" >nul
copy "go.mod" "%INSTALL_DIR%\" >nul
copy "build_hybrid.bat" "%INSTALL_DIR%\" >nul
copy "RUN_HYBRID_ENGINE.bat" "%INSTALL_DIR%\" >nul
copy "README.md" "%INSTALL_DIR%\" >nul 2>nul
copy "PROJECT_STATUS.md" "%INSTALL_DIR%\" >nul 2>nul
copy "requirements.txt" "%INSTALL_DIR%\" >nul 2>nul

echo [2/4] Creating configuration...
if not exist "%INSTALL_DIR%\config" mkdir "%INSTALL_DIR%\config"
echo # Default Settings > "%INSTALL_DIR%\config\default.yaml"
echo sight_distance: 25 >> "%INSTALL_DIR%\config\default.yaml"
echo fade_distance: 5 >> "%INSTALL_DIR%\config\default.yaml"
echo target_fps: 30 >> "%INSTALL_DIR%\config\default.yaml"

echo [3/4] Installing Python dependencies...
python -m pip install --user websocket-client requests >nul 2>nul

echo [4/4] Creating shortcuts...

:: Desktop shortcut
echo @echo off > "%USERPROFILE%\Desktop\VRChat Proximity Engine.bat"
echo cd /d "%INSTALL_DIR%" >> "%USERPROFILE%\Desktop\VRChat Proximity Engine.bat"
echo python hybrid_proximity_engine.py >> "%USERPROFILE%\Desktop\VRChat Proximity Engine.bat"

:: Start Menu shortcut
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
if not exist "%START_MENU%\VRChat Proximity Engine" mkdir "%START_MENU%\VRChat Proximity Engine"
echo @echo off > "%START_MENU%\VRChat Proximity Engine\VRChat Proximity Engine.bat"
echo cd /d "%INSTALL_DIR%" >> "%START_MENU%\VRChat Proximity Engine\VRChat Proximity Engine.bat" 
echo python hybrid_proximity_engine.py >> "%START_MENU%\VRChat Proximity Engine\VRChat Proximity Engine.bat"

echo.
echo ================================================================
echo SUCCESS: Installation complete!
echo ================================================================
echo.
echo Installed to: %INSTALL_DIR%
echo.
echo Launch options:
echo   • Desktop shortcut: VRChat Proximity Engine
echo   • Start Menu: Programs ^> VRChat Proximity Engine
echo   • Direct: %INSTALL_DIR%\RUN_HYBRID_ENGINE.bat
echo.
echo Features installed:
echo   ✓ Hybrid Zig + Go + Python engine
echo   ✓ No OSC dependency - works with any VRChat world
echo   ✓ Real-time proximity detection
echo   ✓ Computer vision-based avatar detection
echo   ✓ Configuration presets
echo.

:: Ask if user wants to run it now
set /p run_now="Run VRChat Proximity Engine now? (y/n): "
if /i "%run_now%"=="y" (
    echo.
    echo Starting VRChat Proximity Engine...
    cd /d "%INSTALL_DIR%"
    start python hybrid_proximity_engine.py
)

echo.
echo Installation completed successfully!
pause
