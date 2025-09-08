#!/usr/bin/env python3
"""
VRChat Hybrid Proximity Engine
Ultra-fast proximity detection using Zig + Go + Python
"""

import asyncio
import json
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk
import websocket
import requests
from typing import Dict, List, Optional
import ctypes
import os
import sys
from pathlib import Path

class HybridProximityEngine:
    def __init__(self):
        self.running = False
        self.go_process = None
        self.zig_lib = None
        self.websocket_client = None
        self.detection_data = []
        self.stats = {}
        
        # GUI components
        self.root = None
        self.status_vars = {}
        
        # Performance tracking
        self.frame_count = 0
        self.detection_count = 0
        self.last_fps_time = time.time()
        self.fps = 0
        
        # Initialize hybrid system
        self.setup_hybrid_system()

    def setup_hybrid_system(self):
        """Initialize the hybrid Zig+Go+Python system"""
        print("Setting up hybrid proximity engine...")
        
        # Compile Zig module if needed
        self.compile_zig_module()
        
        # Load Zig library
        self.load_zig_library()
        
        # Prepare Go module
        self.prepare_go_module()

    def compile_zig_module(self):
        """Compile the Zig vision processing module"""
        zig_file = Path("fast_vision.zig")
        lib_file = Path("fast_vision.dll")
        
        if not zig_file.exists():
            raise FileNotFoundError("fast_vision.zig not found")
        
        # Check if we need to recompile
        if lib_file.exists() and lib_file.stat().st_mtime > zig_file.stat().st_mtime:
            print("Zig module is up to date")
            return
        
        print("Compiling Zig module for maximum performance...")
        
        try:
            # Compile Zig to shared library with optimizations
            cmd = [
                "zig", "build-lib",
                str(zig_file),
                "-dynamic",
                "-O", "ReleaseFast",  # Maximum optimization
                "--name", "fast_vision",
                "-target", "x86_64-windows"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✓ Zig module compiled successfully")
            else:
                print(f"✗ Zig compilation failed: {result.stderr}")
                # Fallback to slower Python implementation
                print("Falling back to Python-only mode")
                
        except subprocess.TimeoutExpired:
            print("✗ Zig compilation timed out")
        except FileNotFoundError:
            print("✗ Zig compiler not found, install from https://ziglang.org/")
            print("Falling back to Python-only mode")

    def load_zig_library(self):
        """Load the compiled Zig library"""
        lib_file = Path("fast_vision.dll")
        
        if not lib_file.exists():
            print("No Zig library found, using Python fallback")
            return
        
        try:
            self.zig_lib = ctypes.CDLL(str(lib_file))
            
            # Define function signatures
            self.zig_lib.zig_capture_screen.argtypes = [
                ctypes.POINTER(ctypes.c_uint32),  # width
                ctypes.POINTER(ctypes.c_uint32),  # height
                ctypes.POINTER(ctypes.POINTER(ctypes.c_uint8))  # data
            ]
            self.zig_lib.zig_capture_screen.restype = ctypes.c_bool
            
            print("✓ Zig library loaded successfully")
            
        except Exception as e:
            print(f"✗ Failed to load Zig library: {e}")
            self.zig_lib = None

    def prepare_go_module(self):
        """Prepare the Go networking module"""
        go_file = Path("fast_network.go")
        
        if not go_file.exists():
            print("✗ fast_network.go not found")
            return
        
        print("Preparing Go networking module...")
        
        # Create go.mod if it doesn't exist
        if not Path("go.mod").exists():
            subprocess.run(["go", "mod", "init", "vrchat-proximity"], cwd=".")
            subprocess.run(["go", "mod", "tidy"], cwd=".")

    def start_go_engine(self):
        """Start the Go performance engine"""
        try:
            print("Starting Go performance engine...")
            
            # Build and run Go module
            self.go_process = subprocess.Popen(
                ["go", "run", "fast_network.go"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give Go process time to start
            time.sleep(2)
            
            if self.go_process.poll() is None:
                print("✓ Go engine started successfully")
                return True
            else:
                stdout, stderr = self.go_process.communicate()
                print(f"✗ Go engine failed to start: {stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Failed to start Go engine: {e}")
            return False

    def connect_websocket(self):
        """Connect to Go engine via WebSocket"""
        try:
            def on_message(ws, message):
                try:
                    data = json.loads(message)
                    if data.get('type') == 'detections':
                        self.detection_data = data.get('detections', [])
                        self.frame_count = data.get('frame_count', 0)
                        self.update_gui_data()
                except json.JSONDecodeError:
                    pass

            def on_error(ws, error):
                print(f"WebSocket error: {error}")

            def on_close(ws, close_status_code, close_msg):
                print("WebSocket connection closed")

            def on_open(ws):
                print("✓ WebSocket connected to Go engine")

            self.websocket_client = websocket.WebSocketApp(
                "ws://localhost:8080/ws",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            # Start WebSocket in separate thread
            websocket_thread = threading.Thread(
                target=self.websocket_client.run_forever,
                daemon=True
            )
            websocket_thread.start()
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to connect WebSocket: {e}")
            return False

    def get_engine_stats(self):
        """Get statistics from Go engine"""
        try:
            response = requests.get("http://localhost:8080/status", timeout=1)
            if response.status_code == 200:
                self.stats = response.json()
                return self.stats
        except requests.RequestException:
            pass
        return {}

    def get_engine_metrics(self):
        """Get detailed metrics from Go engine"""
        try:
            response = requests.get("http://localhost:8080/metrics", timeout=1)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return {}

    def setup_gui(self):
        """Setup the Python GUI coordinator"""
        self.root = tk.Tk()
        self.root.title("VRChat Hybrid Proximity Engine (Zig + Go + Python)")
        self.root.geometry("1000x700")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main control tab
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Detection Control")
        self.setup_main_tab(main_frame)
        
        # Performance tab
        perf_frame = ttk.Frame(notebook)
        notebook.add(perf_frame, text="Performance Metrics")
        self.setup_performance_tab(perf_frame)
        
        # Detection results tab
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Detection Results")
        self.setup_results_tab(results_frame)

    def setup_main_tab(self, parent):
        """Setup main control tab"""
        # Control buttons
        control_frame = ttk.LabelFrame(parent, text="Engine Control")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_button = ttk.Button(
            control_frame, 
            text="Start Hybrid Engine", 
            command=self.start_engine,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.stop_button = ttk.Button(
            control_frame, 
            text="Stop Engine", 
            command=self.stop_engine,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Status display
        status_frame = ttk.LabelFrame(parent, text="Engine Status")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_vars['engine_status'] = tk.StringVar(value="Stopped")
        self.status_vars['go_status'] = tk.StringVar(value="Not Running")
        self.status_vars['zig_status'] = tk.StringVar(value="Not Loaded")
        
        ttk.Label(status_frame, text="Engine:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Label(status_frame, textvariable=self.status_vars['engine_status']).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(status_frame, text="Go Backend:").grid(row=1, column=0, sticky=tk.W, padx=5)
        ttk.Label(status_frame, textvariable=self.status_vars['go_status']).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(status_frame, text="Zig Vision:").grid(row=2, column=0, sticky=tk.W, padx=5)
        ttk.Label(status_frame, textvariable=self.status_vars['zig_status']).grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Detection summary
        detection_frame = ttk.LabelFrame(parent, text="Detection Summary")
        detection_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.detection_listbox = tk.Listbox(detection_frame, height=15)
        self.detection_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(detection_frame, orient=tk.VERTICAL, command=self.detection_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.detection_listbox.config(yscrollcommand=scrollbar.set)

    def setup_performance_tab(self, parent):
        """Setup performance metrics tab"""
        # Real-time metrics
        metrics_frame = ttk.LabelFrame(parent, text="Real-time Performance")
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_vars['frames_processed'] = tk.StringVar(value="0")
        self.status_vars['total_detections'] = tk.StringVar(value="0")
        self.status_vars['avg_process_time'] = tk.StringVar(value="0.0 ms")
        self.status_vars['fps'] = tk.StringVar(value="0")
        self.status_vars['cpu_usage'] = tk.StringVar(value="0%")
        self.status_vars['memory_usage'] = tk.StringVar(value="0 MB")
        
        row = 0
        for label, var in [
            ("Frames Processed:", self.status_vars['frames_processed']),
            ("Total Detections:", self.status_vars['total_detections']),
            ("Avg Process Time:", self.status_vars['avg_process_time']),
            ("FPS:", self.status_vars['fps']),
            ("CPU Usage:", self.status_vars['cpu_usage']),
            ("Memory Usage:", self.status_vars['memory_usage'])
        ]:
            ttk.Label(metrics_frame, text=label).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(metrics_frame, textvariable=var, font=("Consolas", 10)).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            row += 1
        
        # System info
        system_frame = ttk.LabelFrame(parent, text="System Information")
        system_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.system_info = tk.Text(system_frame, height=10, width=80)
        self.system_info.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_results_tab(self, parent):
        """Setup detection results tab"""
        # Detailed detection data
        results_frame = ttk.LabelFrame(parent, text="Detailed Detection Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for structured data
        columns = ("Object", "Confidence", "Type", "Distance", "Category", "Area")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100, anchor=tk.CENTER)
        
        self.results_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars for treeview
        tree_scrollbar_y = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.config(yscrollcommand=tree_scrollbar_y.set)

    def start_engine(self):
        """Start the hybrid engine"""
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Update status
        self.status_vars['engine_status'].set("Starting...")
        
        # Start Go backend
        if self.start_go_engine():
            self.status_vars['go_status'].set("Running")
            
            # Connect WebSocket
            time.sleep(1)  # Give Go engine time to start
            if self.connect_websocket():
                self.status_vars['engine_status'].set("Running")
                print("✓ Hybrid engine started successfully")
                
                # Update Zig status
                if self.zig_lib:
                    self.status_vars['zig_status'].set("Loaded & Active")
                else:
                    self.status_vars['zig_status'].set("Fallback Mode")
                
                # Start GUI update loop
                self.start_gui_updates()
            else:
                self.status_vars['engine_status'].set("WebSocket Failed")
        else:
            self.status_vars['engine_status'].set("Failed to Start")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def stop_engine(self):
        """Stop the hybrid engine"""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Close WebSocket
        if self.websocket_client:
            self.websocket_client.close()
        
        # Stop Go process
        if self.go_process:
            self.go_process.terminate()
            self.go_process = None
        
        # Update status
        self.status_vars['engine_status'].set("Stopped")
        self.status_vars['go_status'].set("Stopped")
        
        print("Hybrid engine stopped")

    def start_gui_updates(self):
        """Start GUI update loop"""
        def update_loop():
            if self.running:
                self.update_performance_metrics()
                self.root.after(1000, update_loop)  # Update every second
        
        update_loop()

    def update_gui_data(self):
        """Update GUI with latest detection data"""
        if not self.root:
            return
        
        # Update detection list
        self.detection_listbox.delete(0, tk.END)
        
        for i, detection in enumerate(self.detection_data):
            bbox = detection.get('bbox', {})
            confidence = detection.get('confidence', 0)
            det_type = detection.get('type', 'unknown')
            distance = detection.get('distance', 0)
            category = detection.get('category', 'Unknown')
            
            summary = f"Object {i+1}: {category} ({distance:.1f}m) - {det_type} [{confidence:.2f}]"
            self.detection_listbox.insert(tk.END, summary)
        
        # Update results tree
        self.results_tree.delete(*self.results_tree.get_children())
        
        for i, detection in enumerate(self.detection_data):
            self.results_tree.insert("", tk.END, values=(
                f"Avatar_{i+1}",
                f"{detection.get('confidence', 0):.3f}",
                detection.get('type', 'unknown'),
                f"{detection.get('distance', 0):.1f}m",
                detection.get('category', 'Unknown'),
                f"{detection.get('area', 0):.0f}px"
            ))

    def update_performance_metrics(self):
        """Update performance metrics from Go engine"""
        stats = self.get_engine_stats()
        
        if stats:
            self.status_vars['frames_processed'].set(f"{stats.get('frames_processed', 0):,}")
            self.status_vars['total_detections'].set(f"{stats.get('total_detections', 0):,}")
            self.status_vars['avg_process_time'].set(f"{stats.get('avg_process_time', 0):.2f} ms")
            self.status_vars['fps'].set(f"{stats.get('target_fps', 0)}")
            self.status_vars['cpu_usage'].set(f"{stats.get('cpu_usage', 0)}%")
            
            # Update system info
            metrics = self.get_engine_metrics()
            if metrics:
                system_info = f"""System Performance Metrics:

Memory Usage:
  Allocated: {metrics.get('memory', {}).get('alloc_mb', 0):.2f} MB
  System: {metrics.get('memory', {}).get('sys_mb', 0):.2f} MB
  GC Cycles: {metrics.get('memory', {}).get('gc_cycles', 0)}
  Heap Objects: {metrics.get('memory', {}).get('heap_objects', 0):,}

Performance:
  FPS: {metrics.get('performance', {}).get('frames_per_sec', 0):.1f}
  Detections/sec: {metrics.get('performance', {}).get('detections_per_sec', 0):.1f}
  Process Time: {metrics.get('performance', {}).get('avg_process_time', 0):.2f} ms

System:
  Goroutines: {metrics.get('system', {}).get('goroutines', 0)}
  CPU Cores: {metrics.get('system', {}).get('cpu_cores', 0)}
  OS: {metrics.get('system', {}).get('os', 'unknown')}
  Architecture: {metrics.get('system', {}).get('arch', 'unknown')}
"""
                self.system_info.delete(1.0, tk.END)
                self.system_info.insert(1.0, system_info)

    def run(self):
        """Run the hybrid proximity engine"""
        print("VRChat Hybrid Proximity Engine")
        print("===============================")
        print("Ultra-fast detection using Zig + Go + Python")
        print("- Zig: Computer vision processing")
        print("- Go: High-performance networking & concurrency")  
        print("- Python: GUI coordination")
        print("===============================")
        
        self.setup_gui()
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.stop_engine()


if __name__ == "__main__":
    engine = HybridProximityEngine()
    engine.run()
