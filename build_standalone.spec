# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get the application directory
app_dir = Path(__file__).parent

block_cipher = None

# Define the main analysis
a = Analysis(
    ['main.py'],
    pathex=[str(app_dir)],
    binaries=[],
    datas=[
        # Include configuration files and templates
        (str(app_dir / 'src'), 'src'),
        # Include any icon files if they exist
    ],
    hiddenimports=[
        # Core application modules
        'src.core.proximity_engine',
        'src.integration.vrchat_osc',
        'src.integration.steamvr_overlay',
        'src.ui.main_window',
        'src.config.settings',
        
        # PyQt6 modules
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        
        # OSC modules
        'pythonosc.udp_client',
        'pythonosc.dispatcher',
        'pythonosc.server',
        'pythonosc.osc_message',
        
        # Other dependencies
        'numpy',
        'yaml',
        'platformdirs',
        'psutil',
        'asyncio',
        'logging',
        'threading',
        'queue',
        'time',
        'json',
        'dataclasses',
        'typing',
        'pathlib',
        
        # Optional VR support
        'openvr',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
        'notebook',
        'tkinter',
        'wx',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filter out duplicate binaries
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VRChatProximityApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want console window for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',  # We'll create this
    icon=None,  # Add icon path here if available
)

# Create app bundle for better organization (Windows)
if sys.platform == 'win32':
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='VRChatProximityApp'
    )
