#!/usr/bin/env python3
"""
VRChat Proximity Engine - ACTUALLY WORKING Installer
The Install button WILL be visible this time!
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog

def create_installer():
    """Create a simple installer window with VISIBLE Install button"""
    
    root = tk.Tk()
    root.title("VRChat Proximity Engine Installer")
    root.geometry("520x620")  # Better sizing
    root.resizable(False, False)
    
    # Header
    header_frame = tk.Frame(root, bg='#2c3e50', height=100)
    header_frame.pack(fill=tk.X)
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(
        header_frame,
        text="VRChat Hybrid Proximity Engine",
        font=("Arial", 16, "bold"),
        bg='#2c3e50',
        fg='white'
    )
    title_label.pack(pady=(20, 5))
    
    subtitle_label = tk.Label(
        header_frame,
        text="Ultra-fast avatar proximity detection",
        font=("Arial", 10),
        bg='#2c3e50',
        fg='#ecf0f1'
    )
    subtitle_label.pack(pady=(0, 20))
    
    # Main content frame
    main_frame = tk.Frame(root, bg='white')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Features
    features_label = tk.Label(main_frame, text="Features:", font=("Arial", 12, "bold"), bg='white')
    features_label.pack(anchor=tk.W, pady=(0, 10))
    
    features = [
        "✓ No OSC dependency - works with any VRChat world",
        "✓ Computer vision-based detection",
        "✓ Ultra-fast processing",
        "✓ Real-time proximity estimation"
    ]
    
    for feature in features:
        feature_label = tk.Label(main_frame, text=feature, font=("Arial", 9), bg='white', anchor='w')
        feature_label.pack(fill=tk.X, pady=2)
    
    # Install path
    tk.Label(main_frame, text="", bg='white').pack(pady=10)  # Spacer
    
    path_label = tk.Label(main_frame, text="Install to:", font=("Arial", 10, "bold"), bg='white')
    path_label.pack(anchor=tk.W)
    
    install_path = tk.StringVar(value=str(Path.home() / "VRChatProximityEngine"))
    
    path_frame = tk.Frame(main_frame, bg='white')
    path_frame.pack(fill=tk.X, pady=(5, 10))
    
    path_entry = tk.Entry(path_frame, textvariable=install_path, font=("Arial", 9))
    path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    
    def browse_path():
        path = filedialog.askdirectory()
        if path:
            install_path.set(str(Path(path) / "VRChatProximityEngine"))
    
    browse_btn = tk.Button(path_frame, text="Browse...", command=browse_path)
    browse_btn.pack(side=tk.RIGHT)
    
    # Options
    desktop_shortcut = tk.BooleanVar(value=True)
    start_menu = tk.BooleanVar(value=True)
    
    options_frame = tk.Frame(main_frame, bg='white')
    options_frame.pack(fill=tk.X, pady=10)
    
    desktop_check = tk.Checkbutton(options_frame, text="Create desktop shortcut", 
                                  variable=desktop_shortcut, bg='white')
    desktop_check.pack(anchor=tk.W)
    
    start_menu_check = tk.Checkbutton(options_frame, text="Add to Start Menu", 
                                     variable=start_menu, bg='white')
    start_menu_check.pack(anchor=tk.W)
    
    # Status
    status_label = tk.Label(main_frame, text="Ready to install", font=("Arial", 10, "bold"), 
                           fg='green', bg='white')
    status_label.pack(pady=20)
    
    # BUTTONS - ABSOLUTELY POSITIONED AT BOTTOM
    button_frame = tk.Frame(root, bg='#f0f0f0', height=80)
    button_frame.pack(fill=tk.X, side=tk.BOTTOM)
    button_frame.pack_propagate(False)
    
    def cancel_install():
        if messagebox.askyesno("Cancel", "Cancel installation?"):
            root.quit()
    
    def install():
        try:
            install_btn.config(state='disabled', text='Installing...', bg='gray')
            status_label.config(text="Installing...", fg='blue')
            root.update()
            
            # Create install directory
            install_dir = Path(install_path.get())
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files
            source_dir = Path.cwd()
            files_to_copy = [
                "hybrid_proximity_engine.py",
                "standalone_proximity_detector.py",
                "fast_vision.zig",
                "fast_network.go", 
                "go.mod",
                "build_hybrid.bat",
                "RUN_HYBRID_ENGINE.bat",
                "README.md"
            ]
            
            copied = 0
            for file_name in files_to_copy:
                source_file = source_dir / file_name
                if source_file.exists():
                    shutil.copy2(source_file, install_dir / file_name)
                    copied += 1
            
            # Create config
            config_dir = install_dir / "config"
            config_dir.mkdir(exist_ok=True)
            
            with open(config_dir / "default.yaml", 'w') as f:
                f.write("sight_distance: 25\nfade_distance: 5\ntarget_fps: 30\n")
            
            # Install deps
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '--user',
                              'websocket-client', 'requests'], capture_output=True, timeout=30)
            except:
                pass
            
            # Create shortcuts
            if desktop_shortcut.get():
                desktop = Path.home() / "Desktop"
                with open(desktop / "VRChat Proximity Engine.bat", 'w') as f:
                    f.write(f'@echo off\ncd /d "{install_dir}"\npython hybrid_proximity_engine.py\npause\n')
            
            if start_menu.get():
                start_menu_dir = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/VRChat Proximity Engine"
                start_menu_dir.mkdir(parents=True, exist_ok=True)
                with open(start_menu_dir / "VRChat Proximity Engine.bat", 'w') as f:
                    f.write(f'@echo off\ncd /d "{install_dir}"\npython hybrid_proximity_engine.py\n')
            
            status_label.config(text="Installation complete!", fg='green')
            install_btn.config(text='INSTALLED!', bg='green')
            
            messagebox.showinfo("Success!", 
                f"VRChat Proximity Engine installed successfully!\n\n"
                f"Location: {install_dir}\n"
                f"Files copied: {copied}\n\n"
                f"You can run it from the desktop shortcut or Start Menu.")
            
            if messagebox.askyesno("Launch?", "Launch VRChat Proximity Engine now?"):
                subprocess.Popen([sys.executable, str(install_dir / "hybrid_proximity_engine.py")], 
                               cwd=str(install_dir))
            
            root.quit()
            
        except Exception as e:
            status_label.config(text=f"Failed: {e}", fg='red')
            install_btn.config(state='normal', text='INSTALL', bg='#27ae60')
            messagebox.showerror("Error", f"Installation failed:\n{e}")
    
    # Cancel button - better positioning
    cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel_install, 
                          font=("Arial", 11), padx=25, pady=10)
    cancel_btn.place(x=280, y=20)  # Adjusted position
    
    # INSTALL BUTTON - PROPERLY POSITIONED
    install_btn = tk.Button(button_frame, text="INSTALL", command=install,
                           font=("Arial", 12, "bold"), bg='#27ae60', fg='white',
                           padx=35, pady=12, relief=tk.RAISED, bd=2, cursor='hand2')
    install_btn.place(x=380, y=15)  # Better fit positioning
    
    # Run the installer
    root.mainloop()

if __name__ == "__main__":
    create_installer()
