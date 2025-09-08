@echo off
title Installing Chocolatey Package Manager

echo.
echo ================================================================
echo    Installing Chocolatey Package Manager
echo ================================================================
echo.
echo Chocolatey will make it super easy to install development tools:
echo   - NSIS (for building installers)
echo   - WiX Toolset (for MSI installers)  
echo   - Zig compiler (for ultra-fast processing)
echo   - Go compiler (for high-performance networking)
echo   - Git, Python, Node.js, and more!
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script needs to run as Administrator
    echo.
    echo Please:
    echo 1. Right-click on this script
    echo 2. Select "Run as administrator"
    echo 3. Click "Yes" when prompted
    echo.
    pause
    exit /b 1
)

echo Running as Administrator - good!
echo.

:: Check if Chocolatey is already installed
choco --version >nul 2>&1
if %errorLevel% equ 0 (
    echo Chocolatey is already installed!
    choco --version
    goto install_tools
)

echo Installing Chocolatey...
echo.

:: Install Chocolatey
powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"

if %errorLevel% neq 0 (
    echo.
    echo ERROR: Chocolatey installation failed
    pause
    exit /b 1
)

:: Refresh PATH
call refreshenv

echo.
echo ✓ Chocolatey installed successfully!
echo.

:install_tools
echo.
echo Now installing development tools...
echo.

:: Install NSIS for building installers
echo Installing NSIS (installer builder)...
choco install nsis -y

:: Install WiX Toolset for MSI installers  
echo Installing WiX Toolset (MSI builder)...
choco install wixtoolset -y

:: Install Zig compiler (optional, for maximum performance)
echo Installing Zig (ultra-fast compiler)...
choco install zig -y

:: Install Go compiler (optional, for networking performance)
echo Installing Go (high-performance language)...
choco install golang -y

:: Install Git (useful for version control)
echo Installing Git (version control)...
choco install git -y

echo.
echo ================================================================
echo SUCCESS: All tools installed!
echo ================================================================
echo.
echo Chocolatey and development tools are now ready:
echo   ✓ Chocolatey package manager
echo   ✓ NSIS (for EXE installers)
echo   ✓ WiX Toolset (for MSI installers)
echo   ✓ Zig compiler (ultra-fast processing)
echo   ✓ Go compiler (high-performance networking)
echo   ✓ Git (version control)
echo.
echo You can now build professional installers!
echo.
echo Next steps:
echo   1. Close and reopen your terminal/PowerShell
echo   2. Run: BUILD_INSTALLER.bat
echo   3. Choose option 1 (NSIS) for easiest installer
echo.
echo ================================================================
pause
