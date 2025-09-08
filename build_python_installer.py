#!/usr/bin/env python3
"""
VRChat Proximity Engine - Python Installer Builder
Creates a self-extracting installer without needing NSIS or WiX
"""

import os
import sys
import zipfile
import shutil
import base64
from pathlib import Path

def create_self_extracting_installer():
    """Create a self-extracting Python-based installer"""
    
    print("VRChat Proximity Engine - Python Installer Builder")
    print("=" * 60)
    print()
    
    # Define what to include
    files_to_include = [
        "hybrid_proximity_engine.py",
        "standalone_proximity_detector.py", 
        "fast_vision.zig",
        "fast_network.go",
        "go.mod",
        "build_hybrid.bat",
        "RUN_HYBRID_ENGINE.bat",
        "README.md",
        "PROJECT_STATUS.md",
        "TESTING_GUIDE.md",
        "requirements.txt"
    ]
    
    # Create output directory
    output_dir = Path("installer_output")
    output_dir.mkdir(exist_ok=True)
    
    # Create the installer
    installer_script = create_installer_script()
    
    # Create ZIP with all files
    zip_path = output_dir / "proximity_engine_files.zip"
    
    print("Packaging files...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_name in files_to_include:
            file_path = Path(file_name)
            if file_path.exists():
                print(f"  + {file_name}")
                zipf.write(file_path, file_name)
            else:
                print(f"  - {file_name} (not found, skipping)")
        
        # Add config examples
        create_config_examples(zipf)
    
    # Encode ZIP as base64 for embedding
    print("Creating self-extracting installer...")
    with open(zip_path, 'rb') as f:
        zip_data = base64.b64encode(f.read()).decode('ascii')
    
    # Create the final installer
    final_installer = installer_script.replace('{{ZIP_DATA}}', zip_data)
    
    installer_path = output_dir / "VRChatProximityEngine_Installer.py"
    with open(installer_path, 'w', encoding='utf-8') as f:
        f.write(final_installer)
    
    # Also create a batch file to run the installer
    batch_installer = f"""@echo off
title VRChat Proximity Engine Installer

echo.
echo Installing VRChat Hybrid Proximity Engine...
echo.

python "{installer_path.absolute()}"

if %errorlevel% equ 0 (
    echo.
    echo Installation completed successfully!
    echo You can now run the proximity engine from:
    echo   Desktop shortcut: VRChat Proximity Engine
    echo   Start menu: Programs ^> VRChat Proximity Engine
    echo.
) else (
    echo.
    echo Installation failed. Please check the error messages above.
)

pause
"""
    
    batch_path = output_dir / "VRChatProximityEngine_Installer.bat"
    with open(batch_path, 'w') as f:
        f.write(batch_installer)
    
    print()
    print("=" * 60)
    print("SUCCESS: Installer created!")
    print("=" * 60)
    print()
    print(f"Python installer: {installer_path}")
    print(f"Batch installer:  {batch_path}")
    print()
    print("To distribute:")
    print("1. Share VRChatProximityEngine_Installer.bat")
    print("2. Users just double-click to install")
    print("3. No admin rights needed!")
    print()
    
    # Clean up temporary zip
    zip_path.unlink()
    
    return installer_path, batch_path

def create_config_examples(zipf):
    """Add configuration examples to the ZIP"""
    configs = {
        "config/default_settings.yaml": """# VRChat Proximity Engine - Default Settings
sight_distance: 25
fade_distance: 5  
detection_threshold: 0.3
target_fps: 30
use_zig_acceleration: true
use_go_backend: true
""",
        "config/preset_close_range.yaml": """# Close Range Preset
sight_distance: 8
fade_distance: 2
detection_threshold: 0.4
target_fps: 60
""",
        "config/preset_long_range.yaml": """# Long Range Preset  
sight_distance: 100
fade_distance: 20
detection_threshold: 0.2
target_fps: 30
""",
        "examples/basic_usage.py": '''"""Basic usage example"""
from hybrid_proximity_engine import HybridProximityEngine

def main():
    engine = HybridProximityEngine()
    engine.run()

if __name__ == "__main__":
    main()
''',
        "examples/advanced_configuration.py": '''"""Advanced configuration example"""
from hybrid_proximity_engine import HybridProximityEngine

def main():
    engine = HybridProximityEngine()
    # engine.set_target_fps(60)  # High performance
    engine.run()

if __name__ == "__main__":
    main()
'''
    }
    
    for path, content in configs.items():
        zipf.writestr(path, content)
        print(f"  + {path} (generated)")

def create_installer_script():
    """Create the self-extracting installer script"""
    return '''#!/usr/bin/env python3
"""
VRChat Proximity Engine - Self-Extracting Installer
No admin rights required!
"""

import os
import sys
import zipfile
import base64
import shutil
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

class ProximityEngineInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VRChat Proximity Engine Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Default install location
        self.install_path = Path.home() / "VRChatProximityEngine"
        
        self.setup_gui()
        
    def setup_gui(self):
        """Create the installer GUI"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            header_frame, 
            text="VRChat Hybrid Proximity Engine",
            font=("Arial", 18, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Ultra-fast avatar proximity detection using Zig + Go + Python",
            font=("Arial", 10),
            bg='#2c3e50', 
            fg='#ecf0f1'
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Main content
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Features
        features_label = tk.Label(
            main_frame,
            text="Features:",
            font=("Arial", 12, "bold")
        )
        features_label.pack(anchor=tk.W, pady=(0, 10))
        
        features_text = """✓ No OSC dependency - works with any VRChat world
✓ Computer vision-based detection
✓ Ultra-fast Zig processing core  
✓ High-performance Go networking
✓ Real-time proximity estimation
✓ Professional GUI interface
✓ Configuration presets included"""
        
        features_display = tk.Label(
            main_frame,
            text=features_text,
            font=("Arial", 9),
            justify=tk.LEFT
        )
        features_display.pack(anchor=tk.W, pady=(0, 20))
        
        # Installation path
        path_frame = tk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(0, 20))
        
        path_label = tk.Label(path_frame, text="Install to:", font=("Arial", 10, "bold"))
        path_label.pack(anchor=tk.W)
        
        path_entry_frame = tk.Frame(path_frame)
        path_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.path_var = tk.StringVar(value=str(self.install_path))
        path_entry = tk.Entry(path_entry_frame, textvariable=self.path_var, font=("Arial", 9))
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(path_entry_frame, text="Browse...", command=self.browse_path)
        browse_btn.pack(side=tk.RIGHT)
        
        # Options
        options_frame = tk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.desktop_shortcut = tk.BooleanVar(value=True)
        desktop_check = tk.Checkbutton(
            options_frame,
            text="Create desktop shortcut",
            variable=self.desktop_shortcut
        )
        desktop_check.pack(anchor=tk.W)
        
        self.start_menu = tk.BooleanVar(value=True) 
        start_menu_check = tk.Checkbutton(
            options_frame,
            text="Add to Start Menu",
            variable=self.start_menu
        )
        start_menu_check.pack(anchor=tk.W)
        
        # Progress bar
        self.progress_frame = tk.Frame(main_frame)
        self.progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.progress_label = tk.Label(self.progress_frame, text="Ready to install")
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        install_btn = tk.Button(
            button_frame,
            text="Install", 
            command=self.install,
            font=("Arial", 11, "bold"),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=5
        )
        install_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel,
            padx=20,
            pady=5
        )
        cancel_btn.pack(side=tk.RIGHT)
        
    def browse_path(self):
        """Browse for installation directory"""
        path = filedialog.askdirectory(initialdir=self.path_var.get())
        if path:
            self.path_var.set(path)
            self.install_path = Path(path) / "VRChatProximityEngine"
    
    def install(self):
        """Run the installation"""
        try:
            self.progress_bar.start()
            self.progress_label.config(text="Installing...")
            self.root.update()
            
            # Create install directory
            install_dir = Path(self.path_var.get())
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract embedded ZIP
            self.progress_label.config(text="Extracting files...")
            self.root.update()
            
            # Decode and extract the embedded ZIP data
            zip_data = base64.b64decode('{{ZIP_DATA}}')
            zip_path = install_dir / "temp_install.zip"
            
            with open(zip_path, 'wb') as f:
                f.write(zip_data)
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(install_dir)
            
            zip_path.unlink()  # Clean up temp file
            
            # Install Python dependencies
            self.progress_label.config(text="Installing dependencies...")
            self.root.update()
            
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install',
                    'websocket-client', 'requests'
                ], capture_output=True, check=True)
            except:
                pass  # Continue even if pip install fails
            
            # Create shortcuts
            if self.desktop_shortcut.get():
                self.progress_label.config(text="Creating desktop shortcut...")
                self.root.update()
                self.create_desktop_shortcut(install_dir)
            
            if self.start_menu.get():
                self.progress_label.config(text="Adding to Start Menu...")
                self.root.update()
                self.create_start_menu_shortcut(install_dir)
            
            self.progress_bar.stop()
            self.progress_label.config(text="Installation complete!")
            
            messagebox.showinfo(
                "Success!",
                f"VRChat Proximity Engine installed successfully!\\n\\n"
                f"Installed to: {install_dir}\\n\\n"
                f"You can now run it from the desktop shortcut or Start Menu."
            )
            
            self.root.quit()
            
        except Exception as e:
            self.progress_bar.stop()
            self.progress_label.config(text="Installation failed!")
            messagebox.showerror("Error", f"Installation failed:\\n{e}")
    
    def create_desktop_shortcut(self, install_dir):
        """Create desktop shortcut"""
        try:
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "VRChat Proximity Engine.lnk"
            
            # Create a batch file that launches the engine
            launcher_path = install_dir / "Launch_Proximity_Engine.bat"
            with open(launcher_path, 'w') as f:
                f.write(f"""@echo off
cd /d "{install_dir}"
python hybrid_proximity_engine.py
pause
""")
            
            # On Windows, create a simple batch shortcut instead of .lnk
            if sys.platform == "win32":
                batch_shortcut = desktop / "VRChat Proximity Engine.bat" 
                with open(batch_shortcut, 'w') as f:
                    f.write(f"""@echo off
cd /d "{install_dir}"
python hybrid_proximity_engine.py
""")
                    
        except Exception as e:
            print(f"Could not create desktop shortcut: {e}")
    
    def create_start_menu_shortcut(self, install_dir):
        """Create Start Menu shortcut"""
        try:
            if sys.platform == "win32":
                start_menu = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
                app_folder = start_menu / "VRChat Proximity Engine"
                app_folder.mkdir(exist_ok=True)
                
                shortcut_path = app_folder / "VRChat Proximity Engine.bat"
                with open(shortcut_path, 'w') as f:
                    f.write(f"""@echo off
cd /d "{install_dir}"
python hybrid_proximity_engine.py
""")
                    
        except Exception as e:
            print(f"Could not create Start Menu shortcut: {e}")
    
    def cancel(self):
        """Cancel installation"""
        self.root.quit()
    
    def run(self):
        """Start the installer"""
        self.root.mainloop()

if __name__ == "__main__":
    installer = ProximityEngineInstaller()
    installer.run()
'''

if __name__ == "__main__":
    create_self_extracting_installer()
