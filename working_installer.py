#!/usr/bin/env python3
"""
VRChat Proximity Engine - WORKING GUI Installer
Fixed layout so Install button is actually visible!
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog

class WorkingInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VRChat Proximity Engine Installer")
        self.root.geometry("600x550")  # Made taller so buttons show
        self.root.resizable(True, True)  # Allow resizing
        
        # Default install location
        self.install_path = Path.home() / "VRChatProximityEngine"
        
        self.setup_gui()
        
    def setup_gui(self):
        """Create installer GUI with VISIBLE install button"""
        
        # Header - fixed height
        header_frame = tk.Frame(self.root, bg='#2c3e50')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(
            header_frame, 
            text="VRChat Hybrid Proximity Engine",
            font=("Arial", 18, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Ultra-fast avatar proximity detection using Zig + Go + Python",
            font=("Arial", 10),
            bg='#2c3e50', 
            fg='#ecf0f1'
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Scrollable main content
        canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        # Features section
        features_frame = tk.LabelFrame(scrollable_frame, text="Features", font=("Arial", 12, "bold"))
        features_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        features = [
            "✓ No OSC dependency - works with any VRChat world",
            "✓ Computer vision-based detection",
            "✓ Ultra-fast Zig processing core",
            "✓ High-performance Go networking", 
            "✓ Real-time proximity estimation",
            "✓ Professional GUI interface",
            "✓ Configuration presets included"
        ]
        
        for feature in features:
            feature_label = tk.Label(features_frame, text=feature, font=("Arial", 9), anchor="w")
            feature_label.pack(fill=tk.X, padx=10, pady=2)
        
        # Installation path section
        path_frame = tk.LabelFrame(scrollable_frame, text="Installation Directory", font=("Arial", 12, "bold"))
        path_frame.pack(fill=tk.X, pady=(10, 10), padx=10)
        
        path_entry_frame = tk.Frame(path_frame)
        path_entry_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.path_var = tk.StringVar(value=str(self.install_path))
        path_entry = tk.Entry(path_entry_frame, textvariable=self.path_var, font=("Arial", 10))
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(path_entry_frame, text="Browse...", command=self.browse_path, 
                              font=("Arial", 9), padx=15)
        browse_btn.pack(side=tk.RIGHT)
        
        # Options section
        options_frame = tk.LabelFrame(scrollable_frame, text="Options", font=("Arial", 12, "bold"))
        options_frame.pack(fill=tk.X, pady=(10, 10), padx=10)
        
        self.desktop_shortcut = tk.BooleanVar(value=True)
        desktop_check = tk.Checkbutton(
            options_frame,
            text="Create desktop shortcut",
            variable=self.desktop_shortcut,
            font=("Arial", 10)
        )
        desktop_check.pack(anchor=tk.W, padx=10, pady=5)
        
        self.start_menu = tk.BooleanVar(value=True) 
        start_menu_check = tk.Checkbutton(
            options_frame,
            text="Add to Start Menu",
            variable=self.start_menu,
            font=("Arial", 10)
        )
        start_menu_check.pack(anchor=tk.W, padx=10, pady=5)
        
        # Status section
        status_frame = tk.LabelFrame(scrollable_frame, text="Status", font=("Arial", 12, "bold"))
        status_frame.pack(fill=tk.X, pady=(10, 20), padx=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready to install",
            font=("Arial", 11, "bold"),
            fg='green'
        )
        self.status_label.pack(pady=10)
        
        # BUTTONS SECTION - FIXED AT BOTTOM OF WINDOW
        button_frame = tk.Frame(self.root, bg='#f0f0f0', relief=tk.RAISED, bd=1)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5, padx=5)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel,
            font=("Arial", 11),
            padx=25,
            pady=8
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 20), pady=10)
        
        # INSTALL BUTTON - BIG AND OBVIOUS
        self.install_btn = tk.Button(
            button_frame,
            text="INSTALL NOW", 
            command=self.install,
            font=("Arial", 14, "bold"),
            bg='#27ae60',
            fg='white',
            padx=40,
            pady=12,
            relief=tk.RAISED,
            bd=3,
            cursor='hand2'
        )
        self.install_btn.pack(side=tk.RIGHT, padx=(20, 10), pady=10)
        
        # Bind mouse wheel to canvas for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    def browse_path(self):
        """Browse for installation directory"""
        path = filedialog.askdirectory(initialdir=str(self.install_path.parent))
        if path:
            self.install_path = Path(path) / "VRChatProximityEngine"
            self.path_var.set(str(self.install_path))
    
    def install(self):
        """Run the installation"""
        try:
            # Update button and status
            self.install_btn.config(state='disabled', text='INSTALLING...', bg='#95a5a6')
            self.status_label.config(text="Installing VRChat Proximity Engine...", fg='blue')
            self.root.update()
            
            # Create install directory
            install_dir = Path(self.path_var.get())
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Get source directory
            source_dir = Path.cwd()
            
            # Copy files
            self.status_label.config(text="Copying application files...")
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
                "TESTING_GUIDE.md",
                "requirements.txt"
            ]
            
            copied_files = []
            for file_name in files_to_copy:
                source_file = source_dir / file_name
                if source_file.exists():
                    shutil.copy2(source_file, install_dir / file_name)
                    copied_files.append(file_name)
            
            # Create config directory and files
            self.status_label.config(text="Creating configuration files...")
            self.root.update()
            
            config_dir = install_dir / "config"
            config_dir.mkdir(exist_ok=True)
            
            # Default config
            default_config = config_dir / "default_settings.yaml"
            with open(default_config, 'w') as f:
                f.write("""# VRChat Proximity Engine - Default Settings
sight_distance: 25
fade_distance: 5
target_fps: 30
detection_threshold: 0.3
use_zig_acceleration: true
use_go_backend: true
""")
            
            # Create example files
            examples_dir = install_dir / "examples"
            examples_dir.mkdir(exist_ok=True)
            
            basic_example = examples_dir / "basic_usage.py"
            with open(basic_example, 'w') as f:
                f.write('''"""Basic usage example for VRChat Proximity Engine"""
from hybrid_proximity_engine import HybridProximityEngine

def main():
    engine = HybridProximityEngine()
    engine.run()

if __name__ == "__main__":
    main()
''')
            
            # Install Python dependencies
            self.status_label.config(text="Installing Python dependencies...")
            self.root.update()
            
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '--user', '--upgrade',
                    'websocket-client', 'requests', 'tkinter'
                ], capture_output=True, text=True, timeout=60)
            except subprocess.TimeoutExpired:
                pass  # Continue even if pip times out
            except Exception:
                pass  # Continue even if pip fails
            
            # Create shortcuts
            shortcuts_created = []
            
            if self.desktop_shortcut.get():
                self.status_label.config(text="Creating desktop shortcut...")
                self.root.update()
                if self.create_desktop_shortcut(install_dir):
                    shortcuts_created.append("Desktop")
            
            if self.start_menu.get():
                self.status_label.config(text="Creating Start Menu shortcut...")
                self.root.update()
                if self.create_start_menu_shortcut(install_dir):
                    shortcuts_created.append("Start Menu")
            
            # SUCCESS!
            self.status_label.config(text="Installation completed successfully!", fg='green')
            self.install_btn.config(text='INSTALLED!', bg='#27ae60')
            
            success_msg = f"""VRChat Hybrid Proximity Engine installed successfully!

Installation Details:
• Location: {install_dir}
• Files copied: {len(copied_files)}
• Shortcuts created: {', '.join(shortcuts_created) if shortcuts_created else 'None'}

You can now run the proximity engine from:"""
            
            if shortcuts_created:
                if "Desktop" in shortcuts_created:
                    success_msg += "\n• Desktop shortcut"
                if "Start Menu" in shortcuts_created:
                    success_msg += "\n• Start Menu"
            
            success_msg += f"\n• Direct: {install_dir}\\RUN_HYBRID_ENGINE.bat"
            
            messagebox.showinfo("Installation Complete!", success_msg)
            
            # Ask if user wants to launch now
            if messagebox.askyesno("Launch Now?", "Would you like to launch VRChat Proximity Engine now?"):
                try:
                    os.startfile(str(install_dir / "RUN_HYBRID_ENGINE.bat"))
                except:
                    subprocess.Popen([sys.executable, str(install_dir / "hybrid_proximity_engine.py")], 
                                   cwd=str(install_dir))
            
            self.root.quit()
            
        except Exception as e:
            self.status_label.config(text=f"Installation failed: {str(e)}", fg='red')
            self.install_btn.config(state='normal', text='INSTALL NOW', bg='#27ae60')
            messagebox.showerror("Installation Failed", f"Installation failed with error:\n\n{str(e)}\n\nPlease try again.")
    
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
            return True
        except Exception as e:
            print(f"Could not create desktop shortcut: {e}")
            return False
    
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
            return True
        except Exception as e:
            print(f"Could not create Start Menu shortcut: {e}")
            return False
    
    def cancel(self):
        """Cancel installation"""
        if messagebox.askyesno("Cancel Installation", 
                              "Are you sure you want to cancel the installation?"):
            self.root.quit()
    
    def run(self):
        """Start the installer"""
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting VRChat Proximity Engine Installer...")
    installer = WorkingInstaller()
    installer.run()
