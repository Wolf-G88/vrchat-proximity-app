@echo off
title VRChat Proximity App - Test Mode
echo ===============================================
echo VRChat Proximity App - Test Mode
echo ===============================================
echo.
echo This will run the app in TEST MODE with mock users.
echo No VRChat required - perfect for testing!
echo.
echo Test features:
echo - Proximity sliders and controls
echo - Mock users moving around automatically
echo - Real-time distance calculations
echo - User visibility changes
echo - All UI features
echo.
echo Press any key to start test mode...
pause >nul
echo.

python test_mode.py

echo.
echo Test completed. Press any key to exit...
pause
