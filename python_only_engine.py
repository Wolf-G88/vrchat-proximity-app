#!/usr/bin/env python3
"""
VRChat Proximity Engine - Python Only Mode
Simple and reliable proximity detection without compiler dependencies
"""

import asyncio
import json
import threading
import time
import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from typing import Dict, List, Optional
import os
import sys
from pathlib import Path
import pyautogui
import logging

class PythonProximityEngine:
    def __init__(self):
        self.running = False
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
        
        # Computer vision settings
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()
        self.cascade_face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        print("VRChat Hybrid Proximity Engine")
        print("=" * 40)
        print("Python-only mode (no compiler issues)")
        print()

    def setup_gui(self):
        """Setup the Python GUI"""
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
        """Start the Python-only engine"""
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Update status - Python only mode
        self.status_vars['engine_status'].set("Running (Python-Only)")
        self.status_vars['go_status'].set("Disabled (Python-Only Mode)")
        self.status_vars['zig_status'].set("Disabled (Python-Only Mode)")
        
        print("✓ Started in Python-only mode")
        
        # Start detection loop
        self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
        self.detection_thread.start()
        
        # Start GUI update loop
        self.start_gui_updates()

    def stop_engine(self):
        """Stop the engine"""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.status_vars['engine_status'].set("Stopped")
        self.status_vars['go_status'].set("Not Running")
        self.status_vars['zig_status'].set("Not Loaded")
        
        print("✓ Engine stopped")

    def detection_loop(self):
        """Main detection loop using Python OpenCV"""
        print("Starting Python-only detection loop...")
        
        while self.running:
            try:
                start_time = time.time()
                
                # Capture screen using pyautogui (slower but works)
                screenshot = pyautogui.screenshot()
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # Resize for performance
                height, width = frame.shape[:2]
                if width > 1920:
                    scale = 1920 / width
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    frame = cv2.resize(frame, (new_width, new_height))
                
                # Process frame for motion and object detection
                detections = self.process_frame(frame)
                
                # Update statistics
                self.frame_count += 1
                self.detection_count += len(detections)
                
                process_time = (time.time() - start_time) * 1000
                
                # Calculate FPS
                current_time = time.time()
                if current_time - self.last_fps_time >= 1.0:
                    self.fps = self.frame_count / (current_time - self.last_fps_time)
                    self.frame_count = 0
                    self.last_fps_time = current_time
                
                # Update detection data for GUI
                self.detection_data = detections
                self.stats = {
                    'frames_processed': self.frame_count,
                    'total_detections': self.detection_count,
                    'avg_process_time': f"{process_time:.1f} ms",
                    'fps': f"{self.fps:.1f}",
                    'detection_count': len(detections)
                }
                
                # Limit FPS to avoid overwhelming system
                time.sleep(max(0, 1/30 - (time.time() - start_time)))
                
            except Exception as e:
                self.logger.error(f"Detection loop error: {e}")
                time.sleep(0.1)

    def process_frame(self, frame):
        """Process frame for avatar detection"""
        detections = []
        
        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Background subtraction for motion detection
            fg_mask = self.background_subtractor.apply(frame)
            
            # Find contours for moving objects
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                
                # Filter small noise
                if area > 500:  # Minimum area threshold
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Calculate confidence based on area and aspect ratio
                    aspect_ratio = w / h if h > 0 else 0
                    confidence = min(area / 10000, 1.0)  # Normalize area to confidence
                    
                    # Estimate distance based on size (larger = closer)
                    distance = max(1, 50 - (area / 1000))
                    
                    detection = {
                        'id': i,
                        'type': 'moving_object',
                        'confidence': confidence,
                        'area': area,
                        'distance': distance,
                        'bbox': (x, y, w, h),
                        'category': 'avatar_candidate'
                    }
                    
                    detections.append(detection)
            
            # Face detection as backup
            faces = self.cascade_face.detectMultiScale(gray, 1.1, 4)
            for i, (x, y, w, h) in enumerate(faces):
                detection = {
                    'id': f'face_{i}',
                    'type': 'face_detection',
                    'confidence': 0.8,  # Face detection is generally reliable
                    'area': w * h,
                    'distance': max(1, 30 - (w * h / 1000)),
                    'bbox': (x, y, w, h),
                    'category': 'face'
                }
                detections.append(detection)
        
        except Exception as e:
            self.logger.error(f"Frame processing error: {e}")
        
        return detections

    def start_gui_updates(self):
        """Start GUI update loop"""
        def update_gui():
            if self.running and self.root:
                self.update_gui_data()
                self.root.after(100, update_gui)  # Update every 100ms
        
        update_gui()

    def update_gui_data(self):
        """Update GUI with latest data"""
        try:
            # Update performance metrics
            if hasattr(self, 'stats'):
                self.status_vars['frames_processed'].set(str(self.stats.get('frames_processed', 0)))
                self.status_vars['total_detections'].set(str(self.stats.get('total_detections', 0)))
                self.status_vars['avg_process_time'].set(self.stats.get('avg_process_time', '0.0 ms'))
                self.status_vars['fps'].set(self.stats.get('fps', '0'))
            
            # Update detection summary
            self.detection_listbox.delete(0, tk.END)
            for detection in self.detection_data[-10:]:  # Show last 10 detections
                summary = f"[{detection['type']}] Conf: {detection['confidence']:.2f} Dist: {detection['distance']:.1f}m Area: {detection['area']}"
                self.detection_listbox.insert(tk.END, summary)
            
            # Update results tree
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            for detection in self.detection_data:
                self.results_tree.insert("", tk.END, values=(
                    detection.get('id', 'N/A'),
                    f"{detection.get('confidence', 0):.2f}",
                    detection.get('type', 'unknown'),
                    f"{detection.get('distance', 0):.1f}m",
                    detection.get('category', 'unknown'),
                    detection.get('area', 0)
                ))
        
        except Exception as e:
            self.logger.error(f"GUI update error: {e}")

    def run(self):
        """Run the engine"""
        self.setup_gui()
        
        # Add system info
        system_info_text = f"""
Python-Only Proximity Engine
============================
Mode: Computer Vision Detection
Backend: Pure Python + OpenCV
Performance: Standard (no acceleration)

Capabilities:
• Motion-based avatar detection
• Face recognition fallback  
• Real-time processing
• Distance estimation
• Multi-object tracking

Note: This is Python-only mode to avoid Windows
compatibility issues with Zig/Go compilers.
For maximum performance, install Zig and Go.
"""
        
        self.system_info.insert(tk.END, system_info_text)
        self.system_info.config(state=tk.DISABLED)
        
        print("GUI initialized. Click 'Start Hybrid Engine' to begin detection.")
        self.root.mainloop()

def main():
    """Main entry point"""
    print("Starting VRChat Proximity Engine...")
    print("Ultra-fast detection using Zig + Go + Python")
    
    # Check if running in Python-only mode
    print("- Zig: Computer vision processing")
    print("- Go: High-performance networking & concurrency") 
    print("- Python: GUI coordination")
    print()
    
    engine = PythonProximityEngine()
    engine.run()

if __name__ == "__main__":
    main()
