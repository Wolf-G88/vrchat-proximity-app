@echo off
title VRChat Proximity Engine Installer

echo.
echo Installing VRChat Hybrid Proximity Engine...
echo.

python "C:\Users\Wolf King\vrchat-proximity-app\installer_output\VRChatProximityEngine_Installer.py"

if %errorlevel% equ 0 (
    echo.
    echo Installation completed successfully!
    echo You can now run the proximity engine from:
    echo   Desktop shortcut: VRChat Proximity Engine
    echo   Start menu: Programs ^> VRChat Proximity Engine
    echo.
) else (
    echo.
    echo Installation failed. Please check the error messages above.
)

pause
