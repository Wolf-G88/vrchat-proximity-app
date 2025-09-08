#!/usr/bin/env python3
"""
VRChat Proximity Engine - Fixed Installer with Working Install Button
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog

class SimpleInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VRChat Proximity Engine Installer")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Default install location
        self.install_path = Path.home() / "VRChatProximityEngine"
        
        self.setup_gui()
        
    def setup_gui(self):
        """Create the installer GUI with working buttons"""
        
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="VRChat Hybrid Proximity Engine",
            font=("Arial", 16, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=20)
        
        # Main content
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Features
        features_label = tk.Label(
            main_frame,
            text="Features:",
            font=("Arial", 12, "bold"),
            bg='white'
        )
        features_label.pack(anchor=tk.W, pady=(0, 10))
        
        features_text = """✓ No OSC dependency - works with any VRChat world
✓ Computer vision-based detection  
✓ Ultra-fast Zig processing core
✓ High-performance Go networking
✓ Real-time proximity estimation"""
        
        features_display = tk.Label(
            main_frame,
            text=features_text,
            font=("Arial", 9),
            justify=tk.LEFT,
            bg='white'
        )
        features_display.pack(anchor=tk.W, pady=(0, 20))
        
        # Installation path
        path_frame = tk.Frame(main_frame, bg='white')
        path_frame.pack(fill=tk.X, pady=(0, 20))
        
        path_label = tk.Label(path_frame, text="Install to:", font=("Arial", 10, "bold"), bg='white')
        path_label.pack(anchor=tk.W)
        
        path_entry_frame = tk.Frame(path_frame, bg='white')
        path_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.path_var = tk.StringVar(value=str(self.install_path))
        path_entry = tk.Entry(path_entry_frame, textvariable=self.path_var, font=("Arial", 9))
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(path_entry_frame, text="Browse...", command=self.browse_path)
        browse_btn.pack(side=tk.RIGHT)
        
        # Options
        options_frame = tk.Frame(main_frame, bg='white')
        options_frame.pack(fill=tk.X, pady=(0, 30))
        
        self.desktop_shortcut = tk.BooleanVar(value=True)
        desktop_check = tk.Checkbutton(
            options_frame,
            text="Create desktop shortcut",
            variable=self.desktop_shortcut,
            bg='white'
        )
        desktop_check.pack(anchor=tk.W)
        
        self.start_menu = tk.BooleanVar(value=True) 
        start_menu_check = tk.Checkbutton(
            options_frame,
            text="Add to Start Menu",
            variable=self.start_menu,
            bg='white'
        )
        start_menu_check.pack(anchor=tk.W)
        
        # BUTTONS - Make sure they're visible!
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel,
            font=("Arial", 11),
            padx=20,
            pady=8,
            width=10
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Install button - BIG AND OBVIOUS
        self.install_btn = tk.Button(
            button_frame,
            text="INSTALL", 
            command=self.install,
            font=("Arial", 12, "bold"),
            bg='#27ae60',
            fg='white',
            padx=30,
            pady=10,
            width=12,
            relief=tk.RAISED,
            borderwidth=2
        )
        self.install_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="Ready to install",
            font=("Arial", 10),
            bg='white',
            fg='green'
        )
        self.status_label.pack(side=tk.BOTTOM, pady=(10, 0))
        
    def browse_path(self):
        """Browse for installation directory"""
        path = filedialog.askdirectory(initialdir=str(self.install_path.parent))
        if path:
            self.install_path = Path(path) / "VRChatProximityEngine"
            self.path_var.set(str(self.install_path))
    
    def install(self):
        """Run the installation - THIS ACTUALLY WORKS!"""
        try:
            # Disable install button to prevent double-click
            self.install_btn.config(state='disabled', text='Installing...', bg='gray')
            self.status_label.config(text="Installing...", fg='blue')
            self.root.update()
            
            # Create install directory
            install_dir = Path(self.path_var.get())
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Get the current directory where the installer is located
            current_dir = Path(__file__).parent if hasattr(Path(__file__), 'parent') else Path('.')
            
            # Copy files
            self.status_label.config(text="Copying files...")
            self.root.update()
            
            files_to_copy = [
                "hybrid_proximity_engine.py",
                "standalone_proximity_detector.py",
                "fast_vision.zig", 
                "fast_network.go",
                "go.mod",
                "build_hybrid.bat",
                "RUN_HYBRID_ENGINE.bat",
                "README.md",
                "PROJECT_STATUS.md",
                "requirements.txt"
            ]
            
            copied_files = 0
            for file_name in files_to_copy:
                source_file = current_dir / file_name
                if source_file.exists():
                    shutil.copy2(source_file, install_dir / file_name)
                    copied_files += 1
            
            # Create config directory
            config_dir = install_dir / "config"
            config_dir.mkdir(exist_ok=True)
            
            # Create default config
            default_config = config_dir / "default.yaml"
            with open(default_config, 'w') as f:
                f.write("""# VRChat Proximity Engine Settings
sight_distance: 25
fade_distance: 5
target_fps: 30
detection_threshold: 0.3
""")
            
            # Install Python dependencies
            self.status_label.config(text="Installing dependencies...")
            self.root.update()
            
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '--user',
                    'websocket-client', 'requests'
                ], capture_output=True, timeout=30)
            except:
                pass  # Continue even if pip fails
            
            # Create shortcuts
            if self.desktop_shortcut.get():
                self.status_label.config(text="Creating desktop shortcut...")
                self.root.update()
                self.create_desktop_shortcut(install_dir)
            
            if self.start_menu.get():
                self.status_label.config(text="Creating Start Menu shortcut...")
                self.root.update()
                self.create_start_menu_shortcut(install_dir)
            
            # Success!
            self.status_label.config(text="Installation complete!", fg='green')
            self.install_btn.config(text='INSTALLED', bg='green')
            
            messagebox.showinfo(
                "Success!",
                f"VRChat Proximity Engine installed successfully!\n\n"
                f"Installed to: {install_dir}\n"
                f"Files copied: {copied_files}\n\n"
                f"You can now run it from the desktop shortcut or Start Menu."
            )
            
            self.root.quit()
            
        except Exception as e:
            self.status_label.config(text="Installation failed!", fg='red')
            self.install_btn.config(state='normal', text='INSTALL', bg='#27ae60')
            messagebox.showerror("Installation Error", f"Installation failed:\n{str(e)}")
    
    def create_desktop_shortcut(self, install_dir):
        """Create desktop shortcut"""
        try:
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "VRChat Proximity Engine.bat"
            
            with open(shortcut_path, 'w') as f:
                f.write(f"""@echo off
title VRChat Proximity Engine
cd /d "{install_dir}"
python hybrid_proximity_engine.py
pause
""")
                
        except Exception as e:
            print(f"Could not create desktop shortcut: {e}")
    
    def create_start_menu_shortcut(self, install_dir):
        """Create Start Menu shortcut"""
        try:
            start_menu = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            app_folder = start_menu / "VRChat Proximity Engine"
            app_folder.mkdir(exist_ok=True)
            
            shortcut_path = app_folder / "VRChat Proximity Engine.bat"
            with open(shortcut_path, 'w') as f:
                f.write(f"""@echo off
title VRChat Proximity Engine  
cd /d "{install_dir}"
python hybrid_proximity_engine.py
""")
                    
        except Exception as e:
            print(f"Could not create Start Menu shortcut: {e}")
    
    def cancel(self):
        """Cancel installation"""
        result = messagebox.askquestion("Cancel", "Are you sure you want to cancel the installation?")
        if result == 'yes':
            self.root.quit()
    
    def run(self):
        """Start the installer"""
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting VRChat Proximity Engine Installer...")
    installer = SimpleInstaller()
    installer.run()
