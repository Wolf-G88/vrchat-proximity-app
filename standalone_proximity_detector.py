#!/usr/bin/env python3
"""
VRChat Standalone Proximity Detector
Uses computer vision to detect avatars and estimate proximity without OSC
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
import threading
import time
import json
import os
from datetime import datetime
import win32gui
import win32ui
import win32con
import win32api
from PIL import Image, ImageTk
import math

class VRChatProximityDetector:
    def __init__(self):
        self.running = False
        self.vrchat_window = None
        self.detected_objects = {}
        self.proximity_threshold = 100  # pixels - adjust based on testing
        self.detection_history = []
        self.frame_count = 0
        
        # CV settings
        self.tracker = cv2.TrackerCSRT_create()
        self.trackers = []
        self.detection_confidence = 0.3
        
        # GUI setup
        self.setup_gui()
        
        # Load or create detection profiles
        self.load_detection_profiles()

    def find_vrchat_window(self):
        """Find VRChat window handle"""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if "VRChat" in window_title:
                    windows.append((hwnd, window_title))
            return True

        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if windows:
            # Return the first VRChat window found
            return windows[0][0]
        return None

    def capture_vrchat_screen(self):
        """Capture VRChat window content"""
        if not self.vrchat_window:
            self.vrchat_window = self.find_vrchat_window()
            if not self.vrchat_window:
                return None

        try:
            # Get window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(self.vrchat_window)
            width = right - left
            height = bottom - top

            # Capture window content
            hwndDC = win32gui.GetWindowDC(self.vrchat_window)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

            # Convert to numpy array
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
            
            # Cleanup
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(self.vrchat_window, hwndDC)
            
            return np.array(im)

        except Exception as e:
            print(f"Screen capture error: {e}")
            self.vrchat_window = None  # Reset window handle
            return None

    def detect_avatars(self, frame):
        """Detect avatars and objects in frame using multiple methods"""
        if frame is None:
            return []
        
        detections = []
        
        # Method 1: Motion detection for moving avatars
        if hasattr(self, 'previous_frame'):
            motion_detections = self.detect_motion_objects(frame, self.previous_frame)
            detections.extend(motion_detections)
        
        # Method 2: Color-based detection for common avatar colors
        color_detections = self.detect_color_objects(frame)
        detections.extend(color_detections)
        
        # Method 3: Shape detection for humanoid figures
        shape_detections = self.detect_humanoid_shapes(frame)
        detections.extend(shape_detections)
        
        # Store current frame for next motion detection
        self.previous_frame = frame.copy()
        
        return self.merge_detections(detections)

    def detect_motion_objects(self, current_frame, previous_frame):
        """Detect moving objects (likely avatars)"""
        # Convert to grayscale
        gray1 = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate frame difference
        diff = cv2.absdiff(gray1, gray2)
        
        # Apply threshold and morphological operations
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5,5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 50000:  # Filter by size - adjust as needed
                x, y, w, h = cv2.boundingRect(contour)
                # Check aspect ratio to filter human-like shapes
                aspect_ratio = float(w) / h
                if 0.2 < aspect_ratio < 2.0:  # Rough human proportions
                    confidence = min(area / 10000, 1.0)  # Simple confidence based on size
                    detections.append({
                        'bbox': (x, y, w, h),
                        'confidence': confidence,
                        'type': 'motion',
                        'center': (x + w//2, y + h//2),
                        'area': area
                    })
        
        return detections

    def detect_color_objects(self, frame):
        """Detect objects based on common avatar colors"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        detections = []
        
        # Define color ranges for common avatar elements
        color_ranges = [
            # Skin tones
            {'name': 'skin1', 'lower': np.array([0, 20, 70]), 'upper': np.array([20, 255, 255])},
            {'name': 'skin2', 'lower': np.array([160, 20, 70]), 'upper': np.array([180, 255, 255])},
            # Bright clothing colors
            {'name': 'bright', 'lower': np.array([0, 50, 100]), 'upper': np.array([180, 255, 255])},
        ]
        
        for color_range in color_ranges:
            # Create mask for color range
            mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
            
            # Clean up mask
            kernel = np.ones((3,3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 200 < area < 20000:
                    x, y, w, h = cv2.boundingRect(contour)
                    confidence = min(area / 5000, 0.8)
                    detections.append({
                        'bbox': (x, y, w, h),
                        'confidence': confidence,
                        'type': 'color',
                        'center': (x + w//2, y + h//2),
                        'area': area,
                        'color': color_range['name']
                    })
        
        return detections

    def detect_humanoid_shapes(self, frame):
        """Detect humanoid shapes using contour analysis"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 1000 < area < 100000:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                
                # Check if it could be a humanoid shape
                if 0.3 < aspect_ratio < 1.5 and h > w:  # Taller than wide
                    # Calculate solidity (how "solid" the shape is)
                    hull = cv2.convexHull(contour)
                    hull_area = cv2.contourArea(hull)
                    solidity = float(area) / hull_area if hull_area > 0 else 0
                    
                    if solidity > 0.5:  # Reasonably solid shape
                        confidence = min(solidity, 0.9)
                        detections.append({
                            'bbox': (x, y, w, h),
                            'confidence': confidence,
                            'type': 'shape',
                            'center': (x + w//2, y + h//2),
                            'area': area,
                            'aspect_ratio': aspect_ratio,
                            'solidity': solidity
                        })
        
        return detections

    def merge_detections(self, detections):
        """Merge overlapping detections from different methods"""
        if not detections:
            return []
        
        # Sort by confidence
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        merged = []
        for detection in detections:
            overlaps = False
            for merged_det in merged:
                if self.calculate_overlap(detection['bbox'], merged_det['bbox']) > 0.3:
                    overlaps = True
                    # Update with higher confidence detection
                    if detection['confidence'] > merged_det['confidence']:
                        merged_det.update(detection)
                    break
            
            if not overlaps:
                merged.append(detection)
        
        return merged

    def calculate_overlap(self, bbox1, bbox2):
        """Calculate overlap ratio between two bounding boxes"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calculate intersection
        x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        intersection = x_overlap * y_overlap
        
        # Calculate union
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0

    def estimate_distance(self, detection, frame_shape):
        """Estimate distance based on avatar size and position"""
        bbox = detection['bbox']
        x, y, w, h = bbox
        
        # Basic distance estimation based on size
        # Larger objects are closer, smaller objects are farther
        frame_height = frame_shape[0]
        avatar_height_ratio = h / frame_height
        
        # Estimate distance (this is very rough and would need calibration)
        if avatar_height_ratio > 0.8:
            distance_category = "Very Close"
            distance_estimate = 1
        elif avatar_height_ratio > 0.4:
            distance_category = "Close"
            distance_estimate = 3
        elif avatar_height_ratio > 0.2:
            distance_category = "Medium"
            distance_estimate = 10
        elif avatar_height_ratio > 0.1:
            distance_category = "Far"
            distance_estimate = 25
        else:
            distance_category = "Very Far"
            distance_estimate = 50
        
        # Adjust based on position (things at bottom of screen might be closer)
        bottom_ratio = (y + h) / frame_height
        if bottom_ratio > 0.8:  # Near bottom of screen
            distance_estimate *= 0.7  # Closer than estimated
        
        return distance_category, distance_estimate

    def process_frame(self):
        """Main processing loop for each frame"""
        frame = self.capture_vrchat_screen()
        if frame is None:
            return
        
        self.frame_count += 1
        
        # Detect avatars/objects
        detections = self.detect_avatars(frame)
        
        # Process each detection
        current_objects = {}
        for i, detection in enumerate(detections):
            object_id = f"avatar_{i}"
            
            # Estimate distance
            distance_cat, distance_est = self.estimate_distance(detection, frame.shape)
            
            current_objects[object_id] = {
                'bbox': detection['bbox'],
                'confidence': detection['confidence'],
                'distance_category': distance_cat,
                'distance_estimate': distance_est,
                'detection_type': detection['type'],
                'timestamp': time.time(),
                'frame': self.frame_count
            }
        
        # Update detected objects
        self.detected_objects = current_objects
        
        # Update GUI
        self.update_gui(frame, detections)
        
        # Log interesting events
        if len(detections) > 0:
            self.log_detection_event(detections)

    def update_gui(self, frame, detections):
        """Update GUI with current detections"""
        try:
            # Update object list
            self.object_listbox.delete(0, tk.END)
            
            for i, (obj_id, obj_data) in enumerate(self.detected_objects.items()):
                status_text = f"{obj_id}: {obj_data['distance_category']} (~{obj_data['distance_estimate']}m) - {obj_data['confidence']:.2f}"
                self.object_listbox.insert(tk.END, status_text)
            
            # Update counters
            self.detection_count_var.set(f"Objects Detected: {len(detections)}")
            self.frame_count_var.set(f"Frames Processed: {self.frame_count}")
            
            # Show preview if enabled
            if self.show_preview_var.get():
                self.update_preview(frame, detections)
                
        except Exception as e:
            print(f"GUI update error: {e}")

    def update_preview(self, frame, detections):
        """Update preview window with detection boxes"""
        if frame is None:
            return
        
        # Draw detection boxes
        preview_frame = frame.copy()
        for detection in detections:
            x, y, w, h = detection['bbox']
            confidence = detection['confidence']
            
            # Choose color based on confidence
            if confidence > 0.7:
                color = (0, 255, 0)  # Green for high confidence
            elif confidence > 0.4:
                color = (0, 255, 255)  # Yellow for medium confidence
            else:
                color = (0, 0, 255)  # Red for low confidence
            
            # Draw bounding box
            cv2.rectangle(preview_frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw confidence and type
            label = f"{detection.get('type', 'unknown')}: {confidence:.2f}"
            cv2.putText(preview_frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Resize for display
        height, width = preview_frame.shape[:2]
        display_width = 400
        display_height = int((display_width / width) * height)
        preview_resized = cv2.resize(preview_frame, (display_width, display_height))
        
        # Convert to PhotoImage and display
        preview_rgb = cv2.cvtColor(preview_resized, cv2.COLOR_BGR2RGB)
        preview_pil = Image.fromarray(preview_rgb)
        preview_photo = ImageTk.PhotoImage(preview_pil)
        
        self.preview_label.configure(image=preview_photo)
        self.preview_label.image = preview_photo  # Keep a reference

    def log_detection_event(self, detections):
        """Log detection events for analysis"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'frame': self.frame_count,
            'detection_count': len(detections),
            'detections': []
        }
        
        for detection in detections:
            event['detections'].append({
                'bbox': detection['bbox'],
                'confidence': detection['confidence'],
                'type': detection['type'],
                'area': detection.get('area', 0)
            })
        
        self.detection_history.append(event)
        
        # Keep only last 1000 events to prevent memory issues
        if len(self.detection_history) > 1000:
            self.detection_history = self.detection_history[-1000:]

    def setup_gui(self):
        """Set up the GUI interface"""
        self.root = tk.Tk()
        self.root.title("VRChat Standalone Proximity Detector")
        self.root.geometry("800x600")
        
        # Create main frames
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Control buttons
        self.start_button = ttk.Button(control_frame, text="Start Detection", command=self.start_detection)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_detection, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Settings
        self.show_preview_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Show Preview", variable=self.show_preview_var).pack(side=tk.LEFT, padx=10)
        
        # Status display
        self.detection_count_var = tk.StringVar(value="Objects Detected: 0")
        ttk.Label(status_frame, textvariable=self.detection_count_var).pack(side=tk.LEFT)
        
        self.frame_count_var = tk.StringVar(value="Frames Processed: 0")
        ttk.Label(status_frame, textvariable=self.frame_count_var).pack(side=tk.LEFT, padx=20)
        
        # Main content area
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Object list
        ttk.Label(left_frame, text="Detected Objects:").pack(anchor=tk.W)
        self.object_listbox = tk.Listbox(left_frame, height=15)
        self.object_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Preview window
        ttk.Label(right_frame, text="Detection Preview:").pack(anchor=tk.W)
        self.preview_label = ttk.Label(right_frame, text="No preview available")
        self.preview_label.pack(fill=tk.BOTH, expand=True, pady=5)

    def start_detection(self):
        """Start the detection process"""
        self.running = True
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self.detection_loop, daemon=True)
        self.processing_thread.start()

    def stop_detection(self):
        """Stop the detection process"""
        self.running = False
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)

    def detection_loop(self):
        """Main detection loop running in separate thread"""
        while self.running:
            try:
                self.process_frame()
                time.sleep(0.1)  # ~10 FPS - adjust as needed
            except Exception as e:
                print(f"Detection loop error: {e}")
                time.sleep(1)

    def load_detection_profiles(self):
        """Load detection profiles from file"""
        # Placeholder for future profile system
        pass

    def run(self):
        """Start the application"""
        print("VRChat Standalone Proximity Detector")
        print("====================================")
        print("This app detects avatars using computer vision")
        print("Make sure VRChat is visible on screen when running")
        print("====================================")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.running = False


if __name__ == "__main__":
    app = VRChatProximityDetector()
    app.run()
