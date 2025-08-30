# VRChat Proximity Visibility App

A cross-platform standalone application that integrates with VRChat to provide proximity-based user visibility control. Users can adjust their "sight distance" to only see other users when they get within a specified range, with real-time adjustment capabilities both on desktop and in VR.

## ✨ Features

- **🌍 Cross-Platform Support**: Windows, Linux, and VR headset compatibility
- **🎮 VRChat Integration**: Seamless integration via OSC (Open Sound Control) API
- **📏 Dynamic Sight Distance**: Adjustable visibility range from 1-50 meters on a graduated scale
- **⚡ Real-Time Updates**: Instant on-the-fly adjustment of sight distance settings
- **🥽 SteamVR Integration**: Native VR overlay with controller support for in-VR adjustments
- **💾 Persistent Settings**: Save and load user preferences with multiple presets
- **🎛️ Advanced Controls**: Fade distance, update rates, and performance optimization
- **📊 User Tracking**: Real-time user list with distance and visibility status
- **🔧 Debug Tools**: Built-in debugging and performance monitoring

## 🏗️ Architecture

The application consists of several key components:

1. **VRChat Integration Layer**: Communicates with VRChat via OSC API
2. **Proximity Detection Engine**: Advanced distance calculations with fade zones
3. **Visibility Control System**: Smart user show/hide with smooth transitions
4. **Desktop UI**: PyQt6-based interface with sliders, presets, and monitoring
5. **VR Overlay**: SteamVR overlay with controller input support
6. **Configuration Management**: YAML-based settings with automatic backups
7. **Cross-Platform Runtime**: Handles Windows/Linux/VR platform differences

## 📋 Requirements

### System Requirements
- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), or compatible VR headsets
- **Python**: 3.8 or higher
- **VRChat**: Latest version with OSC enabled
- **SteamVR**: For VR functionality (optional)
- **Memory**: 512MB RAM minimum
- **Storage**: 100MB available space

### VRChat Setup
1. Enable OSC in VRChat settings
2. Ensure ports 9000/9001 are available for OSC communication
3. Launch VRChat before starting the proximity app

## 🚀 Installation

### Option 1: Quick Install (Recommended)
```bash
# Clone the repository
git clone https://github.com/vrchat-proximity/vrchat-proximity-app.git
cd vrchat-proximity-app

# Install dependencies
pip install -r requirements.txt

# For VR support (optional)
pip install openvr>=1.21.4

# Run the application
python main.py
```

### Option 2: Development Setup
```bash
# Clone and setup development environment
git clone https://github.com/vrchat-proximity/vrchat-proximity-app.git
cd vrchat-proximity-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install all dependencies including dev tools
pip install -r requirements.txt
pip install -e .[dev,vr]

# Run tests
pytest tests/

# Run the application
python main.py
```

### Option 3: Packaged Installation
```bash
# Install via pip (when published)
pip install vrchat-proximity-app

# Run
vrchat-proximity
```

## 📖 Usage

### First Time Setup
1. **Launch VRChat** and ensure OSC is enabled in settings
2. **Run the application** using `python main.py`
3. **Click "Start"** to begin proximity detection
4. **Adjust sight distance** using the slider (1-50 meters)
5. **Fine-tune fade distance** for smooth transitions

### Desktop Interface
- **Sight Distance Slider**: Main control for visibility range
- **Fade Distance Slider**: Controls transition zone size
- **Presets Dropdown**: Quick access to saved configurations
- **Status Tab**: Monitor connection and user statistics
- **Users Tab**: Real-time list of tracked users and their visibility
- **Advanced Tab**: Fine-tune performance and behavior settings

### VR Interface (SteamVR Required)
1. **Enable VR Overlay** in settings
2. **Press Menu button** on either controller to toggle overlay
3. **Use touchpad** for fine distance control:
   - **Horizontal**: Adjust sight distance
   - **Vertical**: Adjust fade distance
4. **Controller bindings** (configurable):
   - **Left Trigger**: Decrease sight distance
   - **Right Grip**: Increase sight distance

### Presets System
- **Default**: Standard 10m sight, 2m fade
- **Close Range**: 5m sight for intimate conversations
- **Long Range**: 25m sight for large spaces
- **Performance**: Optimized settings for lower-end systems
- **Custom**: Create and save your own configurations

### Configuration
Settings are automatically saved to:
- **Windows**: `%APPDATA%/VRChatProximityApp/settings.yaml`
- **Linux**: `~/.config/VRChatProximityApp/settings.yaml`

## 🔧 Advanced Configuration

### OSC Settings
```yaml
vrchat_osc:
  receive_port: 9001  # Port to receive from VRChat
  send_port: 9000     # Port to send to VRChat
  host: "127.0.0.1"   # Usually localhost
  enable_position_tracking: true
```

### VR Settings
```yaml
vr:
  enable_vr_overlay: true
  overlay_width: 0.3        # Overlay size in meters
  overlay_distance: 1.0     # Distance from user
  controller_binding_left: "trigger"
  controller_binding_right: "grip"
  haptic_feedback: true
```

### Performance Tuning
```yaml
visibility:
  update_rate: 0.1          # Update frequency (seconds)
  fade_duration: 1.0        # Fade transition time
  enable_distance_scaling: true
  distance_multiplier: 1.0  # Global distance scaling
```

## 🐛 Troubleshooting

### Common Issues

**"VRChat not connecting"**
- Ensure VRChat OSC is enabled
- Check firewall isn't blocking ports 9000/9001
- Restart both VRChat and the proximity app

**"No users showing up"**
- Verify you're in a populated VRChat instance
- Check that other users have position data available
- Try adjusting sight distance to maximum (50m)

**"VR overlay not appearing"**
- Ensure SteamVR is running
- Check that OpenVR is installed (`pip install openvr`)
- Verify VR overlay is enabled in settings

**"Application crashes on startup"**
- Check Python version (3.8+ required)
- Verify all dependencies are installed
- Check log files in data directory

### Debug Mode
Run with debug logging:
```bash
python main.py --log-level DEBUG
```

Log files are saved to:
- **Windows**: `%APPDATA%/VRChatProximityApp/logs/`
- **Linux**: `~/.local/share/VRChatProximityApp/logs/`

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/

# Run specific test file
pytest tests/test_proximity_engine.py -v
```

## 🛠️ Development

### Project Structure
```
vrchat-proximity-app/
├── src/
│   ├── core/           # Proximity detection engine
│   ├── integration/    # VRChat OSC & SteamVR
│   ├── ui/            # PyQt6 desktop interface
│   └── config/        # Settings management
├── tests/             # Unit tests
├── main.py           # Application entry point
├── requirements.txt  # Python dependencies
└── setup.py         # Installation script
```

### Key Components

**ProximityEngine** (`src/core/proximity_engine.py`)
- Core distance calculations and visibility state management
- Efficient user tracking with fade zones
- Configurable update rates and scaling

**VRChat Integration** (`src/integration/vrchat_osc.py`)
- OSC communication with VRChat
- User position tracking and visibility control
- Real-time parameter updates

**Desktop UI** (`src/ui/main_window.py`)
- PyQt6-based interface with modern design
- Real-time sliders, user lists, and status monitoring
- System tray integration

**VR Overlay** (`src/integration/steamvr_overlay.py`)
- SteamVR overlay with controller input
- In-VR proximity adjustments
- Haptic feedback support

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings to all functions
- Format with Black: `black src/`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- VRChat team for the OSC API
- OpenVR/SteamVR for VR integration capabilities
- PyQt team for the excellent GUI framework
- The VRChat community for feedback and testing

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/vrchat-proximity/vrchat-proximity-app/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vrchat-proximity/vrchat-proximity-app/discussions)
- **Discord**: [VRChat Proximity Community](https://discord.gg/vrchat-proximity)

---

**Made with ❤️ for the VRChat community**
