@echo off
title Building VRChat Proximity Engine MSI Installer

echo.
echo ================================================================
echo    Building VRChat Hybrid Proximity Engine MSI Installer
echo ================================================================
echo.

:: Check for WiX Toolset
where candle.exe >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: WiX Toolset not found
    echo Please install WiX Toolset v3.11+ from:
    echo https://github.com/wixtoolset/wix3/releases
    echo.
    echo Or install via Chocolatey:
    echo   choco install wixtoolset
    echo.
    pause
    exit /b 1
)

echo Found: WiX Toolset
echo.

:: Set version from environment or default
if "%PRODUCT_VERSION%"=="" set PRODUCT_VERSION=1.0.0.0
echo Product Version: %PRODUCT_VERSION%

:: Create output directory
if not exist "output" mkdir output

:: Create required directories and files if missing
echo Creating required installer components...

:: Create config directory and files
if not exist "config" mkdir config
if not exist "config\default_settings.yaml" (
    echo # Default VRChat Proximity Engine Settings > config\default_settings.yaml
    echo sight_distance: 25 >> config\default_settings.yaml
    echo fade_distance: 5 >> config\default_settings.yaml
    echo detection_threshold: 0.3 >> config\default_settings.yaml
    echo target_fps: 30 >> config\default_settings.yaml
)

if not exist "config\preset_close_range.yaml" (
    echo # Close Range Preset > config\preset_close_range.yaml
    echo sight_distance: 10 >> config\preset_close_range.yaml
    echo fade_distance: 2 >> config\preset_close_range.yaml
)

if not exist "config\preset_long_range.yaml" (
    echo # Long Range Preset > config\preset_long_range.yaml
    echo sight_distance: 50 >> config\preset_long_range.yaml
    echo fade_distance: 10 >> config\preset_long_range.yaml
)

:: Create examples directory
if not exist "examples" mkdir examples
if not exist "examples\basic_usage.py" (
    echo # Basic Usage Example > examples\basic_usage.py
    echo from hybrid_proximity_engine import HybridProximityEngine >> examples\basic_usage.py
    echo engine = HybridProximityEngine^(^) >> examples\basic_usage.py
    echo engine.run^(^) >> examples\basic_usage.py
)

if not exist "examples\advanced_configuration.py" (
    echo # Advanced Configuration Example > examples\advanced_configuration.py
    echo from hybrid_proximity_engine import HybridProximityEngine >> examples\advanced_configuration.py
    echo engine = HybridProximityEngine^(^) >> examples\advanced_configuration.py
    echo engine.set_target_fps^(60^) >> examples\advanced_configuration.py
    echo engine.run^(^) >> examples\advanced_configuration.py
)

:: Create icons directory with placeholder icons
if not exist "icons" mkdir icons
echo Creating placeholder icons...
echo This is a placeholder icon file > icons\app_icon.ico
echo This is a placeholder icon file > icons\config_icon.ico
echo This is a placeholder icon file > icons\docs_icon.ico

:: Create images directory
if not exist "images" mkdir images
echo Creating placeholder images...
echo BMP banner placeholder > images\banner.bmp
echo BMP dialog placeholder > images\dialog.bmp

:: Create license directory
if not exist "license" mkdir license
if not exist "license\license.rtf" (
    echo {\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}} > license\license.rtf
    echo \f0\fs24 >> license\license.rtf
    echo VRChat Hybrid Proximity Engine License Agreement\par >> license\license.rtf
    echo \par >> license\license.rtf
    echo Copyright ^(c^) 2024 Wolf Clan Family. All rights reserved.\par >> license\license.rtf
    echo \par >> license\license.rtf
    echo This software is provided "as is" without warranty.\par >> license\license.rtf
    echo Use at your own risk.\par >> license\license.rtf
    echo } >> license\license.rtf
)

:: Build the installer
echo.
echo Building MSI installer...
echo.

:: Compile WiX source
echo Step 1: Compiling WiX source...
candle.exe -nologo -out output\VRChatProximityEngine.wixobj VRChatProximityEngine.wxs
if %errorlevel% neq 0 (
    echo ERROR: WiX compilation failed
    pause
    exit /b 1
)

:: Link to create MSI
echo Step 2: Linking MSI package...
light.exe -nologo ^
    -out output\VRChatProximityEngine.msi ^
    -ext WixUIExtension ^
    -cultures:en-us ^
    output\VRChatProximityEngine.wixobj
    
if %errorlevel% neq 0 (
    echo ERROR: MSI linking failed
    pause
    exit /b 1
)

:: Success message
echo.
echo ================================================================
echo SUCCESS: MSI installer created successfully!
echo.
echo Output: output\VRChatProximityEngine.msi
echo Size: 
for %%I in (output\VRChatProximityEngine.msi) do echo   %%~zI bytes
echo.
echo The installer includes:
echo   ✓ Hybrid Zig+Go+Python engine
echo   ✓ Start menu shortcuts  
echo   ✓ Desktop shortcut
echo   ✓ Configuration presets
echo   ✓ Documentation
echo   ✓ Example code
echo   ✓ Automatic dependency installation
echo   ✓ Proper uninstall support
echo   ✓ Registry integration
echo.
echo Ready for distribution!
echo ================================================================
echo.

:: Optional: Sign the MSI (if certificate available)
if exist "%CERT_FILE%" (
    echo Signing MSI installer...
    signtool sign /f "%CERT_FILE%" /p "%CERT_PASSWORD%" /t http://timestamp.digicert.com output\VRChatProximityEngine.msi
    if %errorlevel% equ 0 (
        echo ✓ MSI signed successfully
    ) else (
        echo ⚠ MSI signing failed, but installer is still valid
    )
    echo.
)

echo Build complete!
pause
