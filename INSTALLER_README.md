# VRChat Proximity Engine - Professional Installer

This directory contains everything needed to create professional Windows installers for the VRChat Hybrid Proximity Engine.

## 🚀 Quick Start

**Option 1: Easy Way (Recommended)**
```cmd
BUILD_INSTALLER.bat
```
Choose option 1 for NSIS installer - it's the easiest and works great.

**Option 2: Build Specific Type**
```cmd
cd installer
build_nsis.bat     # For EXE installer
build_msi.bat      # For MSI installer  
```

## 📦 Installer Types

### NSIS Installer (Recommended)
- **File:** `VRChatProximityEngine-1.0.0-Setup.exe`
- **Size:** ~5-10 MB
- **Easy to build:** Only needs NSIS
- **Professional:** Modern UI with license, components, progress
- **Universal:** Works on all Windows versions

**Install NSIS:**
```cmd
choco install nsis
```
Or download from: https://nsis.sourceforge.io/

### WiX MSI Installer (Advanced)
- **File:** `VRChatProximityEngine.msi`  
- **Size:** ~8-15 MB
- **Enterprise-ready:** Official MSI package
- **Complex:** Requires WiX Toolset
- **Corporate:** Better for IT deployments

**Install WiX:**
```cmd
choco install wixtoolset
```
Or download from: https://github.com/wixtoolset/wix3/releases

## 🎯 What Gets Installed

Both installers include:

### Core Application
- `hybrid_proximity_engine.py` - Main hybrid engine
- `fast_vision.zig` - Ultra-fast computer vision
- `fast_network.go` - High-performance networking
- `standalone_proximity_detector.py` - Python fallback
- `build_hybrid.bat` - Build script
- `RUN_HYBRID_ENGINE.bat` - Launcher

### Documentation & Examples  
- `README.md` - User guide
- `PROJECT_STATUS.md` - Feature status
- Configuration presets (close/long range)
- Example Python scripts

### System Integration
- **Start Menu:** VRChat Proximity Engine folder with shortcuts
- **Desktop:** Quick launch shortcut
- **Registry:** Proper Windows integration
- **File associations:** `.vrprox` config files
- **Uninstaller:** Clean removal support
- **Dependencies:** Auto-install Python packages

### Installation Features
- **Automatic dependency detection**
- **Python package installation** 
- **Zig/Go compilation** (if available)
- **Graceful fallbacks** if tools missing
- **Professional progress dialogs**
- **License agreement**
- **Component selection**
- **Admin privileges handling**

## 🛠️ Build Requirements

### For NSIS Installer:
- **NSIS 3.0+** (https://nsis.sourceforge.io/)
- Windows (any version)

### For MSI Installer:
- **WiX Toolset v3.11+** (https://github.com/wixtoolset/wix3/)
- Windows 7+ with .NET Framework

### Optional (for full features):
- **Zig compiler** (maximum performance)
- **Go 1.21+** (high-speed networking)
- **Python 3.8+** (required for users)

## 📁 Directory Structure

```
installer/
├── VRChatProximityEngine.wxs    # WiX MSI source
├── VRChatProximity.nsi          # NSIS script  
├── build_msi.bat               # MSI builder
├── build_nsis.bat              # NSIS builder
├── config/                     # Default configs
│   ├── default_settings.yaml
│   ├── preset_close_range.yaml
│   └── preset_long_range.yaml
├── examples/                   # Example code
│   ├── basic_usage.py
│   └── advanced_configuration.py
├── icons/                      # App icons (ICO)
├── images/                     # Installer graphics (BMP)
├── license/                    # License files
└── output/                     # Built installers
```

## ⚙️ Customization

### Change Version
Edit the installer scripts:
- **NSIS:** Modify `VERSIONMAJOR`, `VERSIONMINOR` in `VRChatProximity.nsi`
- **WiX:** Update `Version` attribute in `VRChatProximityEngine.wxs`

### Custom Graphics
Replace files in `images/` and `icons/`:
- `app_icon.ico` - Application icon (32x32, 48x48, 256x256)
- `header.bmp` - Installer header (150x57)
- `welcome.bmp` - Welcome page image (164x314)

### Modify Installation
- **Add files:** Update file lists in installer scripts
- **Change shortcuts:** Modify shortcut sections  
- **Registry entries:** Update registry sections
- **Dependencies:** Modify dependency installation

## 🎉 Distribution

Once built, your installers are ready for distribution:

### NSIS Installer
- **File:** `VRChatProximityEngine-1.0.0-Setup.exe`
- **Sharing:** Upload to GitHub releases, website, etc.
- **Signing:** Use `signtool` for code signing (optional)

### MSI Installer  
- **File:** `VRChatProximityEngine.msi`
- **Enterprise:** Deploy via Group Policy, SCCM
- **Signing:** MSI signing recommended for corporate use

## 🔧 Troubleshooting

### NSIS Build Fails
- Ensure NSIS is installed and in PATH
- Check file paths in `.nsi` script
- Verify all referenced files exist

### MSI Build Fails
- Install WiX Toolset properly
- Check `candle.exe` and `light.exe` are in PATH
- Verify XML syntax in `.wxs` file

### Missing Dependencies
- Python packages auto-install during installation
- Zig/Go are optional - app works without them
- Build scripts create fallback files

### Installation Issues
- Run installer as Administrator
- Check Windows version compatibility
- Verify Python 3.8+ is installed

## 📈 Professional Features

### Security
- Code signing support
- Admin privilege handling
- Safe uninstallation
- Registry cleanup

### User Experience  
- Modern installer UI
- Progress indicators
- Component selection
- License agreement
- Professional branding

### Enterprise Ready
- MSI for corporate deployment
- Unattended installation support
- Registry-based configuration
- Proper Add/Remove Programs entry

---

## 🏆 Success!

Your VRChat Hybrid Proximity Engine now has professional Windows installers that:

✅ **Work universally** - Compatible with all Windows versions  
✅ **Install cleanly** - Proper system integration  
✅ **Uninstall completely** - No leftover files  
✅ **Look professional** - Modern installer UI  
✅ **Handle dependencies** - Auto-install requirements  
✅ **Support enterprise** - MSI for IT departments  
✅ **Enable easy distribution** - Ready for sharing  

**Your proximity engine is now ready for professional distribution!**
