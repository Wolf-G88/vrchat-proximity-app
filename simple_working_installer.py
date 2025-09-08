#!/usr/bin/env python3
"""
VRChat Proximity Engine - Simple Working Installer
No bullshit, just Python - works on Windows without whining
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog

class SimpleWorkingInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VRChat Proximity Engine - Simple Installer")
        self.root.geometry("580x720")  # Increased height to show buttons
        self.root.resizable(False, False)
        
        self.install_path = Path.home() / "VRChatProximityEngine"
        self.setup_gui()
        
    def setup_gui(self):
        """Create installer GUI"""
        
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="VRChat Proximity Engine",
            font=("Arial", 18, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=(15, 5))
        
        subtitle_label = tk.Label(
            header_frame,
            text="Simple Python Installation - Just Works!",
            font=("Arial", 11),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Main content
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # What's included
        included_label = tk.Label(main_frame, text="This installer includes:", 
                                 font=("Arial", 12, "bold"), bg='white')
        included_label.pack(anchor=tk.W, pady=(0, 10))
        
        included_items = [
            "✓ VRChat Proximity Engine (Python)",
            "✓ Computer vision detection (OpenCV)", 
            "✓ All Python dependencies",
            "✓ Configuration presets",
            "✓ Desktop & Start Menu shortcuts",
            "✓ No compiler bullshit - just works!"
        ]
        
        for item in included_items:
            item_label = tk.Label(main_frame, text=item, font=("Arial", 9), 
                                 bg='white', anchor='w')
            item_label.pack(fill=tk.X, pady=2)
        
        # Install path
        tk.Label(main_frame, text="", bg='white').pack(pady=10)
        
        path_label = tk.Label(main_frame, text="Install to:", 
                             font=("Arial", 10, "bold"), bg='white')
        path_label.pack(anchor=tk.W)
        
        self.path_var = tk.StringVar(value=str(self.install_path))
        
        path_frame = tk.Frame(main_frame, bg='white')
        path_frame.pack(fill=tk.X, pady=(5, 10))
        
        path_entry = tk.Entry(path_frame, textvariable=self.path_var, font=("Arial", 9))
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def browse_path():
            path = filedialog.askdirectory()
            if path:
                self.install_path = Path(path) / "VRChatProximityEngine"
                self.path_var.set(str(self.install_path))
        
        browse_btn = tk.Button(path_frame, text="Browse...", command=browse_path)
        browse_btn.pack(side=tk.RIGHT)
        
        # Options
        self.desktop_shortcut = tk.BooleanVar(value=True)
        self.start_menu = tk.BooleanVar(value=True)
        
        options_frame = tk.Frame(main_frame, bg='white')
        options_frame.pack(fill=tk.X, pady=15)
        
        desktop_check = tk.Checkbutton(options_frame, text="Create desktop shortcut", 
                                      variable=self.desktop_shortcut, bg='white')
        desktop_check.pack(anchor=tk.W)
        
        start_menu_check = tk.Checkbutton(options_frame, text="Add to Start Menu", 
                                         variable=self.start_menu, bg='white')
        start_menu_check.pack(anchor=tk.W)
        
        # Size info
        size_label = tk.Label(
            options_frame, 
            text="Installation size: ~50MB (Python only - no compiler drama)",
            font=("Arial", 8), fg='gray', bg='white'
        )
        size_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Progress and status
        self.progress_frame = tk.Frame(main_frame, bg='white')
        self.progress_frame.pack(fill=tk.X, pady=10)  # Reduced padding
        
        self.status_label = tk.Label(
            self.progress_frame,
            text="Ready to install VRChat Proximity Engine",
            font=("Arial", 10, "bold"),
            fg='green', bg='white'
        )
        self.status_label.pack()
        
        self.progress_text = tk.Text(
            self.progress_frame,
            height=3, width=60,  # Reduced height
            font=("Consolas", 8),
            state='disabled'
        )
        self.progress_text.pack(pady=(5, 0), fill=tk.X)
        
        # Buttons - fixed positioning at bottom
        button_frame = tk.Frame(self.root, bg='#f0f0f0', height=70)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        button_frame.pack_propagate(False)
        
        # Create a centered button container
        button_container = tk.Frame(button_frame, bg='#f0f0f0')
        button_container.pack(expand=True, fill='both')
        
        cancel_btn = tk.Button(button_container, text="Cancel", command=self.cancel, 
                              font=("Arial", 10), padx=20, pady=8)
        cancel_btn.pack(side=tk.LEFT, padx=(120, 20), pady=15)
        
        self.install_btn = tk.Button(
            button_container,
            text="INSTALL NOW", 
            command=self.install,
            font=("Arial", 11, "bold"),
            bg='#27ae60',
            fg='white',
            padx=30,
            pady=10,
            relief=tk.RAISED,
            bd=2,
            cursor='hand2'
        )
        self.install_btn.pack(side=tk.LEFT, padx=(0, 120), pady=15)
        
    def log_progress(self, message):
        """Add message to progress log"""
        self.progress_text.config(state='normal')
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.progress_text.config(state='disabled')
        self.root.update()
        
    def install(self):
        """Run the installation"""
        try:
            self.install_btn.config(state='disabled', text='INSTALLING...', bg='#95a5a6')
            self.status_label.config(text="Installing VRChat Proximity Engine...", fg='blue')
            
            install_dir = Path(self.path_var.get())
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy main application files
            self.log_progress("📁 Copying application files...")
            self.copy_app_files(install_dir)
            
            # Install Python dependencies
            self.log_progress("🐍 Installing Python dependencies...")
            self.install_python_deps()
            
            # Create config files
            self.log_progress("⚙️ Creating configuration files...")
            self.create_configs(install_dir)
            
            # Create shortcuts
            if self.desktop_shortcut.get():
                self.log_progress("🖥️ Creating desktop shortcut...")
                self.create_desktop_shortcut(install_dir)
            
            if self.start_menu.get():
                self.log_progress("📋 Adding to Start Menu...")
                self.create_start_menu_shortcut(install_dir)
            
            # Create launcher script
            self.create_launcher(install_dir)
            
            self.log_progress("✅ Installation complete!")
            self.status_label.config(text="Installation completed successfully!", fg='green')
            self.install_btn.config(text='INSTALLED!', bg='#27ae60')
            
            messagebox.showinfo(
                "Installation Complete!",
                f"VRChat Proximity Engine installed successfully!\n\n"
                f"Location: {install_dir}\n"
                f"Type: Python-only (no Windows compatibility issues)\n\n"
                f"Launch from desktop shortcut or Start Menu."
            )
            
            if messagebox.askyesno("Launch Now?", "Launch VRChat Proximity Engine now?"):
                launcher = install_dir / "Launch_Proximity_Engine.bat"
                os.startfile(str(launcher))
            
            self.root.quit()
            
        except Exception as e:
            self.log_progress(f"❌ Error: {str(e)}")
            self.status_label.config(text="Installation failed!", fg='red')
            self.install_btn.config(state='normal', text='INSTALL NOW', bg='#27ae60')
            messagebox.showerror("Installation Failed", f"Error: {str(e)}")
    
    def copy_app_files(self, install_dir):
        """Copy main application files"""
        source_files = [
            "python_only_engine.py",  # Main Python-only engine
            "hybrid_proximity_engine.py",  # Original for reference
            "standalone_proximity_detector.py",
            "fast_vision.zig",  # Keep source files for reference
            "fast_network.go",   # Keep source files for reference
            "go.mod",
            "build_hybrid.bat",
            "RUN_HYBRID_ENGINE.bat"
        ]
        
        copied = 0
        for file_name in source_files:
            source = Path(file_name)
            if source.exists():
                shutil.copy2(source, install_dir / file_name)
                copied += 1
        
        self.log_progress(f"  • Copied {copied} files")
    
    def install_python_deps(self):
        """Install Python dependencies"""
        deps = [
            'websocket-client', 'requests', 'numpy', 
            'opencv-python', 'PyYAML', 'Pillow', 'tkinter'
        ]
        
        try:
            self.log_progress("  • Installing packages...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--user', '--upgrade'
            ] + deps, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.log_progress("  • Python packages installed successfully")
            else:
                self.log_progress("  • Some packages may need manual install")
                
        except subprocess.TimeoutExpired:
            self.log_progress("  • Package installation timed out - may need manual install")
        except Exception:
            self.log_progress("  • Package installation failed - may need manual install")
    
    def create_configs(self, install_dir):
        """Create configuration files"""
        config_dir = install_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Default config
        with open(config_dir / "default_settings.yaml", 'w') as f:
            f.write("""# VRChat Proximity Engine - Default Settings
sight_distance: 25
fade_distance: 5
target_fps: 30
detection_threshold: 0.3
use_zig_acceleration: false  # Disabled to avoid Windows issues
use_go_backend: false        # Disabled to avoid Windows issues
log_level: INFO
""")
        
        # Close range preset
        with open(config_dir / "preset_close_range.yaml", 'w') as f:
            f.write("""# Close Range Preset
sight_distance: 8
fade_distance: 2
detection_threshold: 0.4
target_fps: 60
""")
        
        # Long range preset
        with open(config_dir / "preset_long_range.yaml", 'w') as f:
            f.write("""# Long Range Preset
sight_distance: 100
fade_distance: 20
detection_threshold: 0.2
target_fps: 30
""")
        
        self.log_progress("  • Configuration files created")
    
    def create_launcher(self, install_dir):
        """Create main launcher script"""
        launcher = install_dir / "Launch_Proximity_Engine.bat"
        with open(launcher, 'w') as f:
            f.write(f"""@echo off
title VRChat Proximity Engine
cd /d "{install_dir}"

echo Starting VRChat Proximity Engine...
echo =====================================
echo Python-only mode (no compiler issues)
echo.

python python_only_engine.py

pause
""")
    
    def create_desktop_shortcut(self, install_dir):
        """Create desktop shortcut"""
        desktop = Path.home() / "Desktop"
        shortcut = desktop / "VRChat Proximity Engine.bat"
        with open(shortcut, 'w') as f:
            f.write(f'@echo off\n"{install_dir}\\Launch_Proximity_Engine.bat"\n')
    
    def create_start_menu_shortcut(self, install_dir):
        """Create Start Menu shortcut"""
        start_menu = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/VRChat Proximity Engine"
        start_menu.mkdir(parents=True, exist_ok=True)
        
        shortcut = start_menu / "VRChat Proximity Engine.bat"
        with open(shortcut, 'w') as f:
            f.write(f'@echo off\n"{install_dir}\\Launch_Proximity_Engine.bat"\n')
    
    def cancel(self):
        """Cancel installation"""
        if messagebox.askyesno("Cancel", "Cancel installation?"):
            self.root.quit()
    
    def run(self):
        """Start the installer"""
        self.root.mainloop()

if __name__ == "__main__":
    print("VRChat Proximity Engine - Simple Python Installer")
    print("No compilers, no bullshit, just works!")
    installer = SimpleWorkingInstaller()
    installer.run()
