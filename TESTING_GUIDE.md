# VRChat Proximity App - Testing Guide

You now have **multiple ways to test the VRChat Proximity App**! Here are all your options:

## 🚀 Quick Testing Options

### 1. **Test Mode (Recommended for Initial Testing)**
Test the app **without VRChat** using mock users that move around automatically:
```batch
# Double-click this file:
TEST_APP.bat

# Or run directly:
python test_mode.py
```

**What you'll see:**
- 6 mock users moving in different patterns
- Real-time proximity detection
- Users appearing/disappearing based on sight distance
- All UI features working (sliders, presets, user list, etc.)

### 2. **Development Mode (Python Required)**
Run the full app in development mode:
```batch
# Install dependencies first:
pip install -r requirements.txt

# Run the main app:
python main.py
```

**Requirements:**
- VRChat running with OSC enabled
- Join a world with other users

### 3. **Standalone Executable**
Create a **portable .exe** that runs without Python installation:
```batch
# Double-click this file to build:
BUILD_STANDALONE.bat

# Or run the build script:
python build_standalone.py
```

**Result:** Get a standalone executable in `dist/VRChatProximityApp/`

## 📋 Testing Checklist

### Core Functionality
- [ ] **Proximity Detection**: Adjust sight distance slider (1-50m)
- [ ] **Fade Distance**: Control smooth user transitions
- [ ] **Real-time Updates**: Changes happen instantly
- [ ] **User List**: See all tracked users with distances
- [ ] **Status Monitor**: Connection and performance stats

### Interface Testing
- [ ] **Main Controls**: Sight and fade distance sliders
- [ ] **Preset System**: Save, load, delete custom presets
- [ ] **Settings Tabs**: Status, Users, Advanced tabs
- [ ] **System Tray**: Minimize to tray functionality
- [ ] **Window Persistence**: Window size/position saved

### Advanced Features
- [ ] **Settings Persistence**: Configurations saved between sessions
- [ ] **Debug Information**: Enable debug tab in advanced settings
- [ ] **Performance Monitoring**: Update rates and processing times
- [ ] **Error Handling**: App recovers from connection issues

## 🎮 VRChat Integration Testing

### Prerequisites
1. **Enable OSC in VRChat**:
   - Settings → OSC → Enable
   - Restart VRChat after enabling

2. **Join Populated World**:
   - Find a world with multiple users
   - Public worlds or populated hangouts work best

### Testing Steps
1. **Start VRChat** and join a world with users
2. **Run the proximity app** (`python main.py`)
3. **Click "Start"** in the app
4. **Watch the Status tab** - should show "Connected" 
5. **Check Users tab** - should list detected users
6. **Adjust sight distance** and see users appear/disappear
7. **Test presets** - try "Close Range", "Long Range", etc.

### Troubleshooting VRChat Connection
- **"Not Connected"**: Check OSC is enabled in VRChat
- **"No Users"**: Try a different world or check user positions
- **"Connection Failed"**: Restart both VRChat and the app

## 🔧 Build Testing

### Testing the Standalone Build
After running `BUILD_STANDALONE.bat`:

1. **Navigate to**: `dist/VRChatProximityApp/`
2. **Run**: `launch.bat` or `VRChatProximityApp.exe`
3. **Verify**: App starts without Python installation
4. **Test**: All features work the same as development mode

### Distribution Testing
1. **Copy** the entire `dist/VRChatProximityApp/` folder
2. **Move** to a different PC (or different folder)
3. **Run** and verify it works without any installation

## 🧪 Test Mode Details

The test mode creates 6 mock users with different movement patterns:

- **Alice**: Circular orbit (close range)
- **Bob**: Figure-8 pattern (medium range)  
- **Charlie**: Slow large orbit (far range)
- **Diana**: Random walk (variable distance)
- **Eve**: Approaching/retreating (dynamic range)
- **Frank**: Fast close orbit (very close)

**Test Scenarios:**
- Set sight distance to **5m** - see only close users
- Set sight distance to **15m** - see medium-distance users appear
- Set sight distance to **30m** - see most users
- Watch fade transitions as users cross boundaries
- Try different presets and see immediate changes

## 📊 Performance Testing

### Monitor Performance
- **Status Tab**: Check update rates and processing time
- **User Count**: Test with different numbers of users
- **Update Rate**: Adjust in Advanced settings (0.05-1.0 seconds)
- **Memory Usage**: Check in Task Manager

### Optimization Testing
- **Performance Preset**: Test optimized settings
- **Update Rate**: Increase to 0.2s for better performance
- **Distance Scaling**: Test with different world scales
- **Fade Duration**: Reduce for faster transitions

## 🎯 Success Criteria

The app is working correctly if:

✅ **UI Responsive**: All sliders and controls work smoothly  
✅ **Real-time Updates**: Changes happen immediately  
✅ **Proximity Detection**: Users appear/disappear at correct distances  
✅ **Smooth Transitions**: Users fade in/out gradually  
✅ **Settings Persist**: Configuration saved between sessions  
✅ **Error Recovery**: App handles connection issues gracefully  
✅ **Cross-Platform**: Works on Windows (Linux compatible)  
✅ **Standalone**: Executable runs without Python  

## 🆘 Getting Help

If you encounter issues:

1. **Check Logs**: Located in `%APPDATA%/VRChatProximityApp/logs/`
2. **Enable Debug**: Set `show_debug_info: true` in settings
3. **Test Mode First**: Use test mode to isolate VRChat issues
4. **Check Dependencies**: Ensure all requirements installed
5. **Restart Components**: Try restarting VRChat and the app

## 🎉 You're Ready!

With these testing options, you can thoroughly validate the VRChat Proximity App:

- **Quick Test**: Use test mode for immediate feedback
- **Full Test**: Connect to VRChat for real-world testing  
- **Distribution Test**: Build standalone for easy sharing

**Happy Testing!** 🚀
