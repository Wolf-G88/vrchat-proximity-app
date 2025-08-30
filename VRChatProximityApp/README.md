# VRChat Proximity Visibility Controller

A standalone Windows application that allows you to control user visibility in VRChat based on proximity distance. Only show users when they get close enough to your set sight distance, creating a more immersive and performance-friendly VRChat experience.

## Features

- **Real-time Proximity Detection**: Automatically show/hide users based on distance from your position
- **Adjustable Sight Distance**: Use the slider to set your preferred visibility range (0.1m to 50m)
- **Live User Monitoring**: See all users in the instance and track their distances in real-time
- **Visual Status Indicators**: Clear connection status and user visibility feedback
- **Standalone Executable**: No installation required - just run the .exe file

## Installation

1. Download the latest `VRChatProximityApp.exe` from the `publish/win-x64/` folder
2. Place the executable anywhere on your computer
3. Double-click to run - no additional software installation required!

## How to Use

1. **Start VRChat** and join any world/instance
2. **Enable OSC in VRChat**:
   - Go to Settings > OSC
   - Enable "Enable OSC"
   - Note the port number (default is 9001)

3. **Launch VRChat Proximity App**:
   - Run `VRChatProximityApp.exe`
   - Click the "Start" button to begin monitoring

4. **Adjust Sight Distance**:
   - Use the slider to set your preferred visibility distance
   - Users farther away will be hidden from your view
   - Changes apply instantly while running

5. **Monitor Users**:
   - View all users in the "All Users" list with their distances
   - See currently visible users in the "Visible Users" list
   - Watch real-time position and distance updates

## VRChat Integration

This application connects to VRChat through the OSC (Open Sound Control) interface:

- **Port**: Default 9001 (configurable in VRChat settings)
- **Data**: Receives your head position and tracking data
- **No Modifications**: Works with any VRChat world or avatar
- **Safe**: Read-only connection - doesn't send data to VRChat

### Current Limitations

- The demo version simulates player movement for testing purposes
- For full VRChat integration, you'll need:
  - VRChat OSC enabled and configured
  - Compatible avatar with position tracking parameters
  - Custom world setup for multi-user position sharing

## Technical Details

- **Framework**: .NET 9 WPF Application
- **Architecture**: Self-contained executable (~153MB)
- **Requirements**: Windows 10/11 x64
- **Performance**: Real-time updates every 100ms
- **Memory**: Low memory footprint with efficient user tracking

## Building from Source

If you want to build the application yourself:

```bash
# Clone/download the source code
# Navigate to the VRChatProximityApp directory
cd VRChatProximityApp

# Build the standalone executable
dotnet publish -c Release -r win-x64 --self-contained -p:PublishSingleFile=true -o publish/win-x64

# Or run the build script
build-release.bat
```

## Demo Mode

The current version runs in demo mode with simulated data:
- Shows 10 demo users placed randomly around the world
- Simulates your movement in a circular pattern
- Perfect for testing the proximity visibility mechanics

## Future Enhancements

- Direct VRChat OSC integration for real position data
- Multiple user position tracking via network sync
- Custom avatar parameter integration
- Sound/notification alerts for user visibility changes
- Settings persistence and profiles
- Advanced filtering and user management options

## Troubleshooting

**Application won't start:**
- Ensure you're running Windows 10/11 x64
- Try running as administrator
- Check Windows Defender/antivirus settings

**VRChat connection issues:**
- Verify OSC is enabled in VRChat settings
- Check that port 9001 is available
- Restart both VRChat and the proximity app

**Performance issues:**
- Close unnecessary applications
- Lower the sight distance for better performance
- Check VRChat graphics settings

## Support

This is a demonstration application. For issues or questions, please refer to the source code or VRChat OSC documentation.

---

**Note**: This application is not affiliated with VRChat Inc. Use responsibly and in accordance with VRChat's Terms of Service.
