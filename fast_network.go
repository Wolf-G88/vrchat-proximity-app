package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net"
	"net/http"
	"runtime"
	"sync"
	"sync/atomic"
	"time"
	"unsafe"

	"github.com/gorilla/websocket"
	"github.com/shirou/gopsutil/v3/process"
)

// #cgo CFLAGS: -I.
// #cgo LDFLAGS: -L. -lfast_vision
// #include <stdint.h>
// #include <stdbool.h>
//
// // Zig function declarations
// bool zig_capture_screen(uint32_t* width, uint32_t* height, uint8_t** data);
// bool zig_detect_motion(uint8_t* current_data, uint8_t* previous_data, uint32_t width, uint32_t height, void** detections, uint32_t* count);
//
// typedef struct {
//     int32_t x, y, width, height;
// } BoundingBox;
//
// typedef struct {
//     BoundingBox bbox;
//     float confidence;
//     uint8_t detection_type;
//     float area;
// } Detection;
import "C"

// Detection represents a detected object
type Detection struct {
	BBox       BoundingBox `json:"bbox"`
	Confidence float32     `json:"confidence"`
	Type       string      `json:"type"`
	Area       float32     `json:"area"`
	Distance   float32     `json:"distance"`
	Category   string      `json:"category"`
}

// BoundingBox represents object bounds
type BoundingBox struct {
	X      int32 `json:"x"`
	Y      int32 `json:"y"`
	Width  int32 `json:"width"`
	Height int32 `json:"height"`
}

// ProximityEngine handles high-performance detection
type ProximityEngine struct {
	running          atomic.Bool
	frameCount       atomic.Int64
	detectionsCount  atomic.Int64
	processTime      atomic.Int64 // microseconds
	clients          sync.Map     // WebSocket clients
	detectionChan    chan []Detection
	screenCaptureCtx context.Context
	cancelCapture    context.CancelFunc
	
	// Performance monitoring
	cpuUsage    atomic.Int64
	memoryUsage atomic.Int64
	
	// Configuration
	targetFPS       int
	detectionBuffer []Detection
	bufferMutex     sync.RWMutex
}

// NewProximityEngine creates a new high-performance engine
func NewProximityEngine() *ProximityEngine {
	ctx, cancel := context.WithCancel(context.Background())
	
	return &ProximityEngine{
		detectionChan:    make(chan []Detection, 100), // Buffered channel
		screenCaptureCtx: ctx,
		cancelCapture:    cancel,
		targetFPS:        30, // Default 30 FPS
		detectionBuffer:  make([]Detection, 0, 100),
	}
}

// Start begins the detection engine
func (pe *ProximityEngine) Start() error {
	if pe.running.Load() {
		return fmt.Errorf("engine already running")
	}
	
	pe.running.Store(true)
	
	// Start performance monitoring
	go pe.monitorPerformance()
	
	// Start screen capture and detection
	go pe.captureAndDetectLoop()
	
	// Start WebSocket server for real-time updates
	go pe.startWebSocketServer()
	
	// Start detection processing
	go pe.processDetections()
	
	log.Println("Proximity Engine started with", runtime.NumCPU(), "CPU cores")
	return nil
}

// Stop halts the detection engine
func (pe *ProximityEngine) Stop() {
	if !pe.running.Load() {
		return
	}
	
	pe.running.Store(false)
	pe.cancelCapture()
	close(pe.detectionChan)
	
	log.Println("Proximity Engine stopped")
}

// captureAndDetectLoop runs the main detection loop
func (pe *ProximityEngine) captureAndDetectLoop() {
	ticker := time.NewTicker(time.Duration(1000/pe.targetFPS) * time.Millisecond)
	defer ticker.Stop()
	
	var previousFrame *C.uint8_t
	var previousWidth, previousHeight C.uint32_t
	
	for {
		select {
		case <-pe.screenCaptureCtx.Done():
			return
		case <-ticker.C:
			if !pe.running.Load() {
				return
			}
			
			// Capture screen using Zig
			startTime := time.Now()
			detections := pe.captureAndDetect(previousFrame, previousWidth, previousHeight)
			processingTime := time.Since(startTime)
			
			// Update metrics
			pe.frameCount.Add(1)
			pe.detectionsCount.Add(int64(len(detections)))
			pe.processTime.Store(processingTime.Microseconds())
			
			// Send detections to processing channel
			if len(detections) > 0 {
				select {
				case pe.detectionChan <- detections:
				default:
					// Drop frame if channel is full to prevent blocking
					log.Println("Detection channel full, dropping frame")
				}
			}
		}
	}
}

// captureAndDetect performs screen capture and detection using Zig
func (pe *ProximityEngine) captureAndDetect(previousFrame *C.uint8_t, prevWidth, prevHeight C.uint32_t) []Detection {
	var width, height C.uint32_t
	var data *C.uint8_t
	
	// Capture screen using Zig function
	if !C.zig_capture_screen(&width, &height, &data) {
		return nil
	}
	
	var detections []Detection
	
	// If we have a previous frame, run motion detection
	if previousFrame != nil && prevWidth == width && prevHeight == height {
		var zigDetections *C.Detection
		var count C.uint32_t
		
		if C.zig_detect_motion(data, previousFrame, width, height, 
			(*unsafe.Pointer)(unsafe.Pointer(&zigDetections)), &count) {
			
			// Convert C detections to Go structs
			detections = pe.convertCDetections(zigDetections, int(count), int32(width), int32(height))
		}
	}
	
	// Store current frame for next iteration
	// Note: In production, we'd need proper memory management
	previousFrame = data
	
	return detections
}

// convertCDetections converts C Detection structs to Go
func (pe *ProximityEngine) convertCDetections(cDetections *C.Detection, count int, frameWidth, frameHeight int32) []Detection {
	if count == 0 {
		return nil
	}
	
	// Create slice from C array
	detections := make([]Detection, count)
	cArray := (*[1000]C.Detection)(unsafe.Pointer(cDetections))[:count:count]
	
	for i, cDet := range cArray {
		detections[i] = Detection{
			BBox: BoundingBox{
				X:      int32(cDet.bbox.x),
				Y:      int32(cDet.bbox.y),
				Width:  int32(cDet.bbox.width),
				Height: int32(cDet.bbox.height),
			},
			Confidence: float32(cDet.confidence),
			Type:       pe.getDetectionTypeString(uint8(cDet.detection_type)),
			Area:       float32(cDet.area),
		}
		
		// Estimate distance and category
		detections[i].Distance, detections[i].Category = pe.estimateDistance(detections[i], frameWidth, frameHeight)
	}
	
	return detections
}

// getDetectionTypeString converts detection type to string
func (pe *ProximityEngine) getDetectionTypeString(detType uint8) string {
	switch detType {
	case 0:
		return "motion"
	case 1:
		return "color"
	case 2:
		return "shape"
	default:
		return "unknown"
	}
}

// estimateDistance calculates distance based on object size
func (pe *ProximityEngine) estimateDistance(detection Detection, frameWidth, frameHeight int32) (float32, string) {
	// Calculate avatar height ratio
	heightRatio := float32(detection.BBox.Height) / float32(frameHeight)
	
	var distance float32
	var category string
	
	switch {
	case heightRatio > 0.8:
		distance = 1.0
		category = "Very Close"
	case heightRatio > 0.4:
		distance = 3.0
		category = "Close"
	case heightRatio > 0.2:
		distance = 10.0
		category = "Medium"
	case heightRatio > 0.1:
		distance = 25.0
		category = "Far"
	default:
		distance = 50.0
		category = "Very Far"
	}
	
	// Adjust based on position (objects at bottom might be closer)
	bottomRatio := float32(detection.BBox.Y+detection.BBox.Height) / float32(frameHeight)
	if bottomRatio > 0.8 {
		distance *= 0.7 // Closer than estimated
	}
	
	return distance, category
}

// processDetections handles detection results
func (pe *ProximityEngine) processDetections() {
	for detections := range pe.detectionChan {
		pe.bufferMutex.Lock()
		pe.detectionBuffer = detections
		pe.bufferMutex.Unlock()
		
		// Broadcast to WebSocket clients
		pe.broadcastDetections(detections)
	}
}

// WebSocket upgrader
var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // Allow all origins in development
	},
}

// WebSocket client structure
type Client struct {
	conn   *websocket.Conn
	send   chan []byte
	engine *ProximityEngine
}

// startWebSocketServer starts the WebSocket server for real-time updates
func (pe *ProximityEngine) startWebSocketServer() {
	http.HandleFunc("/ws", pe.handleWebSocket)
	http.HandleFunc("/status", pe.handleStatus)
	http.HandleFunc("/metrics", pe.handleMetrics)
	
	log.Println("WebSocket server starting on :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Printf("WebSocket server error: %v", err)
	}
}

// handleWebSocket handles new WebSocket connections
func (pe *ProximityEngine) handleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("WebSocket upgrade error: %v", err)
		return
	}
	
	client := &Client{
		conn:   conn,
		send:   make(chan []byte, 256),
		engine: pe,
	}
	
	pe.clients.Store(client, true)
	
	// Start client goroutines
	go client.writePump()
	go client.readPump()
}

// writePump sends messages to WebSocket client
func (c *Client) writePump() {
	ticker := time.NewTicker(54 * time.Second)
	defer func() {
		ticker.Stop()
		c.conn.Close()
	}()
	
	for {
		select {
		case message, ok := <-c.send:
			c.conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if !ok {
				c.conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}
			
			if err := c.conn.WriteMessage(websocket.TextMessage, message); err != nil {
				return
			}
			
		case <-ticker.C:
			c.conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if err := c.conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}

// readPump handles messages from WebSocket client
func (c *Client) readPump() {
	defer func() {
		c.engine.clients.Delete(c)
		c.conn.Close()
	}()
	
	c.conn.SetReadLimit(512)
	c.conn.SetReadDeadline(time.Now().Add(60 * time.Second))
	c.conn.SetPongHandler(func(string) error {
		c.conn.SetReadDeadline(time.Now().Add(60 * time.Second))
		return nil
	})
	
	for {
		_, _, err := c.conn.ReadMessage()
		if err != nil {
			break
		}
	}
}

// broadcastDetections sends detections to all connected clients
func (pe *ProximityEngine) broadcastDetections(detections []Detection) {
	if len(detections) == 0 {
		return
	}
	
	message := map[string]interface{}{
		"type":        "detections",
		"timestamp":   time.Now().Unix(),
		"count":       len(detections),
		"detections":  detections,
		"frame_count": pe.frameCount.Load(),
	}
	
	data, err := json.Marshal(message)
	if err != nil {
		log.Printf("JSON marshal error: %v", err)
		return
	}
	
	pe.clients.Range(func(key, value interface{}) bool {
		client := key.(*Client)
		select {
		case client.send <- data:
		default:
			// Remove slow client
			pe.clients.Delete(client)
			close(client.send)
		}
		return true
	})
}

// handleStatus provides status endpoint
func (pe *ProximityEngine) handleStatus(w http.ResponseWriter, r *http.Request) {
	pe.bufferMutex.RLock()
	currentDetections := len(pe.detectionBuffer)
	pe.bufferMutex.RUnlock()
	
	status := map[string]interface{}{
		"running":            pe.running.Load(),
		"frames_processed":   pe.frameCount.Load(),
		"total_detections":   pe.detectionsCount.Load(),
		"current_detections": currentDetections,
		"avg_process_time":   float64(pe.processTime.Load()) / 1000.0, // ms
		"target_fps":         pe.targetFPS,
		"cpu_cores":          runtime.NumCPU(),
		"goroutines":         runtime.NumGoroutine(),
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(status)
}

// handleMetrics provides detailed metrics
func (pe *ProximityEngine) handleMetrics(w http.ResponseWriter, r *http.Request) {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	
	metrics := map[string]interface{}{
		"memory": map[string]interface{}{
			"alloc_mb":      float64(m.Alloc) / 1024 / 1024,
			"sys_mb":        float64(m.Sys) / 1024 / 1024,
			"gc_cycles":     m.NumGC,
			"heap_objects":  m.HeapObjects,
		},
		"performance": map[string]interface{}{
			"frames_per_sec":     pe.calculateFPS(),
			"detections_per_sec": pe.calculateDetectionRate(),
			"avg_process_time":   float64(pe.processTime.Load()) / 1000.0,
			"cpu_usage":          pe.cpuUsage.Load(),
		},
		"system": map[string]interface{}{
			"goroutines":     runtime.NumGoroutine(),
			"cpu_cores":      runtime.NumCPU(),
			"os":            runtime.GOOS,
			"arch":          runtime.GOARCH,
		},
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(metrics)
}

// calculateFPS calculates current frames per second
func (pe *ProximityEngine) calculateFPS() float64 {
	// Simple FPS calculation - could be more sophisticated
	frameCount := pe.frameCount.Load()
	if frameCount < 30 {
		return 0
	}
	return float64(pe.targetFPS) // Approximation
}

// calculateDetectionRate calculates detections per second
func (pe *ProximityEngine) calculateDetectionRate() float64 {
	totalDetections := pe.detectionsCount.Load()
	frameCount := pe.frameCount.Load()
	if frameCount == 0 {
		return 0
	}
	return float64(totalDetections) / (float64(frameCount) / float64(pe.targetFPS))
}

// monitorPerformance monitors system performance
func (pe *ProximityEngine) monitorPerformance() {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-pe.screenCaptureCtx.Done():
			return
		case <-ticker.C:
			// Monitor CPU usage
			if processes, err := process.Processes(); err == nil {
				for _, p := range processes {
					if name, err := p.Name(); err == nil && name == "vrchat_proximity" {
						if cpu, err := p.CPUPercent(); err == nil {
							pe.cpuUsage.Store(int64(cpu))
						}
						if mem, err := p.MemoryInfo(); err == nil {
							pe.memoryUsage.Store(int64(mem.RSS))
						}
						break
					}
				}
			}
		}
	}
}

// GetCurrentDetections returns current detection buffer
func (pe *ProximityEngine) GetCurrentDetections() []Detection {
	pe.bufferMutex.RLock()
	defer pe.bufferMutex.RUnlock()
	
	// Return copy to prevent race conditions
	result := make([]Detection, len(pe.detectionBuffer))
	copy(result, pe.detectionBuffer)
	return result
}

// SetTargetFPS sets the target frames per second
func (pe *ProximityEngine) SetTargetFPS(fps int) {
	pe.targetFPS = fps
	log.Printf("Target FPS set to %d", fps)
}

// GetStats returns engine statistics
func (pe *ProximityEngine) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"running":           pe.running.Load(),
		"frames_processed":  pe.frameCount.Load(),
		"total_detections":  pe.detectionsCount.Load(),
		"avg_process_time":  float64(pe.processTime.Load()) / 1000.0,
		"cpu_usage":         pe.cpuUsage.Load(),
		"memory_usage_mb":   float64(pe.memoryUsage.Load()) / 1024 / 1024,
		"target_fps":        pe.targetFPS,
	}
}

// Main function for testing
func main() {
	fmt.Println("VRChat Fast Proximity Engine (Go + Zig)")
	fmt.Println("=======================================")
	
	engine := NewProximityEngine()
	
	if err := engine.Start(); err != nil {
		log.Fatalf("Failed to start engine: %v", err)
	}
	
	// Keep running
	select {}
}
