@echo off
echo VRChat Hybrid Proximity Engine Build Script
echo ==========================================

:: Check for required tools
echo Checking for required tools...

where zig >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Zig compiler not found
    echo Please install from https://ziglang.org/
    echo Continuing with Python fallback mode...
) else (
    echo Found: Zig compiler
)

where go >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Go compiler not found
    echo Please install from https://golang.org/
    pause
    exit /b 1
) else (
    echo Found: Go compiler
)

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    echo Please install Python 3.8+
    pause
    exit /b 1
) else (
    echo Found: Python
)

:: Install Python dependencies
echo.
echo Installing Python dependencies...
pip install websocket-client requests

:: Initialize Go module
echo.
echo Initializing Go module...
if not exist "go.mod" (
    go mod init vrchat-proximity
    go mod tidy
    go get github.com/gorilla/websocket
    go get github.com/shirou/gopsutil/v3/process
)

:: Compile Zig module (if available)
echo.
echo Compiling Zig vision module...
if exist "fast_vision.zig" (
    zig build-lib fast_vision.zig -dynamic -O ReleaseFast --name fast_vision -target x86_64-windows
    if %errorlevel% equ 0 (
        echo SUCCESS: Zig module compiled
    ) else (
        echo WARNING: Zig compilation failed, using fallback mode
    )
) else (
    echo WARNING: fast_vision.zig not found
)

:: Test Go module
echo.
echo Testing Go module compilation...
go build fast_network.go
if %errorlevel% equ 0 (
    echo SUCCESS: Go module compiled
    del fast_network.exe >nul 2>nul
) else (
    echo ERROR: Go module compilation failed
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Build complete! Run with:
echo   python hybrid_proximity_engine.py
echo ==========================================
pause
