# VRChat Hybrid Proximity Engine

A high-performance proximity detection system for VRChat that bypasses OSC limitations using computer vision and real-time avatar tracking.

## 🚀 Features

- **Universal Compatibility** - Works with any VRChat world, no OSC required
- **Real-time Detection** - Computer vision-based avatar proximity tracking
- **Multiple Modes** - Python-only (reliable) or Hybrid (Zig + Go + Python for max performance)
- **Professional GUI** - Multi-tabbed interface with real-time metrics
- **Easy Installation** - One-click installer with dependency management
- **Cross-platform** - Windows support with Linux/Mac compatibility planned

## 📦 Quick Install

### Option 1: Simple Python Installer (Recommended)
```bash
python simple_working_installer.py
```
- ✅ No compiler dependencies
- ✅ Works on any Windows system
- ✅ Professional GUI installer
- ✅ Creates shortcuts automatically

### Option 2: Batch Installer (Fallback)
```bash
SIMPLE_INSTALL.bat
```
- Reliable fallback if GUI installer has issues
- Copies files and installs dependencies via command line

## 🎯 How It Works

The engine uses computer vision to detect avatars in VRChat by:

1. **Screen Capture** - Captures VRChat window frames
2. **Motion Detection** - Identifies moving objects (avatars)
3. **Object Classification** - Distinguishes avatars from background
4. **Distance Estimation** - Calculates proximity based on object size
5. **Real-time Updates** - Provides live proximity data

## 📋 System Requirements

- Windows 10/11 (64-bit)
- Python 3.7+ 
- 4GB RAM minimum, 8GB recommended
- DirectX compatible graphics card
- VRChat running in windowed or borderless mode

## 🔧 Installation

### Automatic Installation
1. Download the repository
2. Run `python simple_working_installer.py`
3. Click "INSTALL NOW" 
4. Launch from desktop shortcut or Start Menu

### Manual Installation
```bash
# Install Python dependencies
pip install opencv-python numpy pyautogui websocket-client requests PyYAML Pillow

# Run the engine
python python_only_engine.py
```

## 🖥️ Usage

### Python-Only Mode (Default)
- Reliable and compatible with all Windows systems
- Uses pure Python + OpenCV for detection
- Standard performance, no compiler requirements

```bash
python python_only_engine.py
```

### Hybrid Mode (Advanced)
- Maximum performance with Zig + Go acceleration
- Requires Zig and Go compilers installed
- Ultra-fast processing for high-end systems

```bash
# Install compilers first
choco install zig golang

# Build and run hybrid system
python hybrid_proximity_engine.py
```

## 📁 Project Structure

```
vrchat-proximity-app/
├── python_only_engine.py          # Main Python-only engine
├── hybrid_proximity_engine.py     # Full hybrid engine (Zig+Go+Python)
├── simple_working_installer.py    # GUI installer
├── SIMPLE_INSTALL.bat             # Batch installer fallback
├── fast_vision.zig                # Zig computer vision module
├── fast_network.go                # Go networking backend
├── standalone_proximity_detector.py # Alternative detector
├── build_hybrid.bat               # Build script for hybrid mode
├── config/                        # Configuration presets
├── installer/                     # Installer components
└── docs/                          # Documentation
```

## ⚙️ Configuration

The engine supports multiple configuration presets:

- **Default Settings** - Balanced performance and accuracy
- **Close Range** - Optimized for small spaces (8m range)
- **Long Range** - Wide area detection (100m range)

Edit configuration files in the `config/` folder after installation.

## 🎮 VRChat Setup

1. Launch VRChat in **windowed** or **borderless windowed** mode
2. Start the Proximity Engine
3. Click "Start Hybrid Engine"
4. The engine will automatically detect VRChat and begin tracking

## 📊 Performance Metrics

The GUI provides real-time monitoring:

- **Frames Processed** - Total frames analyzed
- **Total Detections** - Avatar detections made
- **FPS** - Processing frame rate
- **Average Process Time** - Per-frame processing duration
- **Detection Confidence** - Accuracy of avatar identification

## 🔍 Detection Results

View detailed detection data including:
- Object type and confidence score
- Estimated distance from viewer
- Bounding box area
- Classification category
- Real-time proximity alerts

## 🚧 Troubleshooting

### Common Issues

**"Engine Failed to Start"**
- Use Python-only mode: `python python_only_engine.py`
- Check if VRChat is running and visible

**"No detections appearing"**
- Ensure VRChat is in windowed mode
- Move around in VRChat to trigger motion detection
- Check Performance Metrics tab for processing stats

**"Installer buttons not visible"**
- Update installer: `python simple_working_installer.py`
- Use batch fallback: `SIMPLE_INSTALL.bat`

**"OpenCV errors"**
- Install Visual C++ Redistributables
- Reinstall with: `pip install --upgrade opencv-python`

### Performance Optimization

**For better performance:**
- Use hybrid mode with Zig + Go compilers
- Close unnecessary background applications
- Run VRChat in borderless windowed mode
- Ensure graphics drivers are updated

**For stability:**
- Use Python-only mode
- Lower detection sensitivity in config
- Increase detection threshold values

## 🧰 Development

### Building from Source

```bash
# Clone repository
git clone https://github.com/wolfking/vrchat-proximity-engine.git
cd vrchat-proximity-engine

# Install development dependencies
pip install -r requirements.txt

# Build hybrid components (optional)
zig build-lib fast_vision.zig -dynamic -O ReleaseFast
go mod tidy && go build fast_network.go

# Run development version
python python_only_engine.py
```

### Architecture

- **Python Layer** - GUI, coordination, configuration management
- **Zig Module** - Ultra-fast computer vision processing (optional)
- **Go Backend** - High-performance networking and concurrency (optional)
- **OpenCV** - Core computer vision algorithms

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🆘 Support

- **Issues** - Report bugs via GitHub Issues
- **Discussions** - Feature requests and general discussion
- **Wiki** - Detailed documentation and tutorials

## 🎖️ Acknowledgments

- OpenCV team for computer vision libraries
- Zig community for performance optimization techniques
- Go team for excellent concurrency primitives
- VRChat community for testing and feedback

---

## 📈 Roadmap

### v2.0 Planned Features
- [ ] Machine learning avatar classification
- [ ] Multi-monitor support  
- [ ] Linux and macOS compatibility
- [ ] Plugin system for custom detectors
- [ ] Integration with VRChat SDK
- [ ] Advanced proximity zones and alerts
- [ ] Performance profiling tools
- [ ] Automated testing suite

### Current Status: v1.0 - **Production Ready**
✅ Python-only mode stable and tested  
✅ Professional installer working  
✅ Real-time detection functional  
✅ GUI with performance metrics complete  
✅ Windows compatibility verified  

---

**Made with ❤️ for the VRChat community**
