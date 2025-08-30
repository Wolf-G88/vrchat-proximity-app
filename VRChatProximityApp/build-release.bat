@echo off
echo Building VRChat Proximity App for Windows...
echo.

echo Cleaning previous builds...
dotnet clean -c Release

echo Building Release configuration...
dotnet build -c Release

echo Publishing as self-contained executable...
dotnet publish -c Release -r win-x64 --self-contained -p:PublishSingleFile=true -p:PublishTrimmed=false -p:PublishReadyToRun=true -o publish\win-x64

echo.
echo Build complete! 
echo Executable location: publish\win-x64\VRChatProximityApp.exe
echo.
pause
