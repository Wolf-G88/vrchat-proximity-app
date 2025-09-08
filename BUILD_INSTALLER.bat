@echo off
title VRChat Proximity Engine - Installer Builder

echo.
echo ================================================================
echo    VRChat Hybrid Proximity Engine - Installer Builder
echo ================================================================
echo.
echo Choose your installer type:
echo.
echo [1] NSIS Installer (Recommended)
echo     - Creates professional EXE installer
echo     - Easier to build and distribute
echo     - Smaller file size
echo     - Works on all Windows versions
echo.
echo [2] WiX MSI Installer (Advanced)  
echo     - Creates official MSI package
echo     - Enterprise-friendly
echo     - More complex to build
echo     - Requires WiX Toolset
echo.
echo [3] Both installers
echo.
echo [4] Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto build_nsis
if "%choice%"=="2" goto build_msi
if "%choice%"=="3" goto build_both
if "%choice%"=="4" goto exit
goto invalid_choice

:build_nsis
echo.
echo Building NSIS installer...
cd installer
call build_nsis.bat
goto done

:build_msi
echo.
echo Building WiX MSI installer...
cd installer
call build_msi.bat
goto done

:build_both
echo.
echo Building both installers...
cd installer
echo.
echo === Building NSIS Installer ===
call build_nsis.bat
echo.
echo === Building MSI Installer ===
call build_msi.bat
goto done

:invalid_choice
echo.
echo Invalid choice. Please select 1, 2, 3, or 4.
pause
goto start

:done
echo.
echo ================================================================
echo Installer build process completed!
echo.
echo Your installer(s) are ready in the installer directory:
if exist "installer\VRChatProximityEngine-1.0.0-Setup.exe" echo   ✓ NSIS: VRChatProximityEngine-1.0.0-Setup.exe
if exist "installer\output\VRChatProximityEngine.msi" echo   ✓ MSI:  VRChatProximityEngine.msi
echo.
echo Distribution ready!
echo ================================================================
pause
goto exit

:exit
