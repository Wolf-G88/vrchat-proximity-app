const std = @import("std");
const print = std.debug.print;
const ArrayList = std.ArrayList;
const Allocator = std.mem.Allocator;
const c = @cImport({
    @cInclude("windows.h");
    @cInclude("wingdi.h");
});

// Structures for detection results
const BoundingBox = struct {
    x: i32,
    y: i32,
    width: i32,
    height: i32,
};

const Detection = struct {
    bbox: BoundingBox,
    confidence: f32,
    detection_type: u8, // 0=motion, 1=color, 2=shape
    area: f32,
};

const DetectionResult = struct {
    detections: []Detection,
    count: u32,
    processing_time_ms: f64,
};

// Fast image structure
const Image = struct {
    data: []u8,
    width: u32,
    height: u32,
    channels: u32,
    
    const Self = @This();
    
    pub fn init(allocator: Allocator, width: u32, height: u32, channels: u32) !Self {
        const size = width * height * channels;
        return Self{
            .data = try allocator.alloc(u8, size),
            .width = width,
            .height = height,
            .channels = channels,
        };
    }
    
    pub fn deinit(self: *Self, allocator: Allocator) void {
        allocator.free(self.data);
    }
    
    pub fn getPixel(self: *const Self, x: u32, y: u32, channel: u32) u8 {
        const index = (y * self.width + x) * self.channels + channel;
        return if (index < self.data.len) self.data[index] else 0;
    }
    
    pub fn setPixel(self: *Self, x: u32, y: u32, channel: u32, value: u8) void {
        const index = (y * self.width + x) * self.channels + channel;
        if (index < self.data.len) {
            self.data[index] = value;
        }
    }
    
    // Convert BGR to grayscale (optimized)
    pub fn toGrayscale(self: *const Self, allocator: Allocator) !Image {
        var gray = try Image.init(allocator, self.width, self.height, 1);
        
        var i: usize = 0;
        var gray_i: usize = 0;
        
        while (i < self.data.len) : (i += 3) {
            // Fast BGR to gray conversion: 0.299*R + 0.587*G + 0.114*B
            // Using integer math for speed: (77*R + 150*G + 29*B) >> 8
            const b = @as(u32, self.data[i]);
            const g = @as(u32, self.data[i + 1]);
            const r = @as(u32, self.data[i + 2]);
            
            gray.data[gray_i] = @intCast((29 * b + 150 * g + 77 * r) >> 8);
            gray_i += 1;
        }
        
        return gray;
    }
};

// Ultra-fast Windows screen capture
pub fn captureVRChatWindow(allocator: Allocator, window_title: []const u8) !?Image {
    // Find VRChat window
    const hwnd = findWindowByTitle(window_title) orelse return null;
    
    // Get window rect
    var rect: c.RECT = undefined;
    if (c.GetWindowRect(hwnd, &rect) == 0) return null;
    
    const width = @as(u32, @intCast(rect.right - rect.left));
    const height = @as(u32, @intCast(rect.bottom - rect.top));
    
    // Create device contexts
    const hdcWindow = c.GetDC(hwnd);
    const hdcMemDC = c.CreateCompatibleDC(hdcWindow);
    
    // Create bitmap
    const hbmScreen = c.CreateCompatibleBitmap(hdcWindow, @as(c_int, @intCast(width)), @as(c_int, @intCast(height)));
    _ = c.SelectObject(hdcMemDC, hbmScreen);
    
    // Copy screen to bitmap
    _ = c.BitBlt(hdcMemDC, 0, 0, @as(c_int, @intCast(width)), @as(c_int, @intCast(height)), hdcWindow, 0, 0, c.SRCCOPY);
    
    // Get bitmap data
    var bitmap_info = std.mem.zeroes(c.BITMAPINFO);
    bitmap_info.bmiHeader.biSize = @sizeOf(c.BITMAPINFOHEADER);
    bitmap_info.bmiHeader.biWidth = @as(c_long, @intCast(width));
    bitmap_info.bmiHeader.biHeight = -@as(c_long, @intCast(height)); // Top-down DIB
    bitmap_info.bmiHeader.biPlanes = 1;
    bitmap_info.bmiHeader.biBitCount = 24;
    bitmap_info.bmiHeader.biCompression = c.BI_RGB;
    
    var image = try Image.init(allocator, width, height, 3);
    
    _ = c.GetDIBits(hdcMemDC, hbmScreen, 0, height, image.data.ptr, &bitmap_info, c.DIB_RGB_COLORS);
    
    // Cleanup
    _ = c.DeleteObject(hbmScreen);
    _ = c.DeleteDC(hdcMemDC);
    _ = c.ReleaseDC(hwnd, hdcWindow);
    
    return image;
}

fn findWindowByTitle(title: []const u8) ?c.HWND {
    const title_w = std.unicode.utf8ToUtf16LeStringLiteral(title) catch return null;
    return c.FindWindowW(null, title_w);
}

// Ultra-fast motion detection using SIMD when possible
pub fn detectMotion(allocator: Allocator, current: *const Image, previous: *const Image, threshold: u8) ![]Detection {
    if (current.width != previous.width or current.height != previous.height) {
        return error.ImageSizeMismatch;
    }
    
    const timer = std.time.Timer.start() catch unreachable;
    
    // Convert to grayscale for faster processing
    var current_gray = try current.toGrayscale(allocator);
    defer current_gray.deinit(allocator);
    
    var previous_gray = try previous.toGrayscale(allocator);
    defer previous_gray.deinit(allocator);
    
    // Create difference image
    var diff_image = try Image.init(allocator, current.width, current.height, 1);
    defer diff_image.deinit(allocator);
    
    // Fast absolute difference calculation
    for (0..current_gray.data.len) |i| {
        const diff = if (current_gray.data[i] > previous_gray.data[i])
            current_gray.data[i] - previous_gray.data[i]
        else
            previous_gray.data[i] - current_gray.data[i];
        
        diff_image.data[i] = if (diff > threshold) 255 else 0;
    }
    
    // Fast connected component analysis for motion blobs
    var detections = ArrayList(Detection).init(allocator);
    defer detections.deinit();
    
    var visited = try allocator.alloc(bool, diff_image.data.len);
    defer allocator.free(visited);
    @memset(visited, false);
    
    for (0..current.height) |y| {
        for (0..current.width) |x| {
            const index = y * current.width + x;
            if (!visited[index] and diff_image.data[index] == 255) {
                var blob = try floodFill(allocator, &diff_image, visited, @intCast(x), @intCast(y));
                
                if (blob.area > 500 and blob.area < 50000) { // Filter by size
                    const confidence = @min(blob.area / 10000.0, 1.0);
                    try detections.append(Detection{
                        .bbox = blob.bbox,
                        .confidence = @floatCast(confidence),
                        .detection_type = 0, // motion
                        .area = blob.area,
                    });
                }
            }
        }
    }
    
    const processing_time = @as(f64, @floatFromInt(timer.read())) / 1000000.0; // Convert to ms
    print("Motion detection processed in {d:.2} ms\n", .{processing_time});
    
    return detections.toOwnedSlice();
}

const Blob = struct {
    bbox: BoundingBox,
    area: f32,
};

// Fast flood fill for connected components
fn floodFill(allocator: Allocator, image: *const Image, visited: []bool, start_x: i32, start_y: i32) !Blob {
    var stack = ArrayList(struct { x: i32, y: i32 }).init(allocator);
    defer stack.deinit();
    
    try stack.append(.{ .x = start_x, .y = start_y });
    
    var min_x = start_x;
    var max_x = start_x;
    var min_y = start_y;
    var max_y = start_y;
    var area: f32 = 0;
    
    while (stack.items.len > 0) {
        const point = stack.pop();
        const x = point.x;
        const y = point.y;
        
        if (x < 0 or x >= image.width or y < 0 or y >= image.height) continue;
        
        const index = @as(usize, @intCast(y * @as(i32, @intCast(image.width)) + x));
        if (index >= visited.len or visited[index] or image.data[index] == 0) continue;
        
        visited[index] = true;
        area += 1;
        
        // Update bounding box
        min_x = @min(min_x, x);
        max_x = @max(max_x, x);
        min_y = @min(min_y, y);
        max_y = @max(max_y, y);
        
        // Add neighbors
        try stack.append(.{ .x = x + 1, .y = y });
        try stack.append(.{ .x = x - 1, .y = y });
        try stack.append(.{ .x = x, .y = y + 1 });
        try stack.append(.{ .x = x, .y = y - 1 });
    }
    
    return Blob{
        .bbox = BoundingBox{
            .x = min_x,
            .y = min_y,
            .width = max_x - min_x + 1,
            .height = max_y - min_y + 1,
        },
        .area = area,
    };
}

// Fast HSV color space conversion and detection
pub fn detectColorObjects(allocator: Allocator, image: *const Image) ![]Detection {
    const timer = std.time.Timer.start() catch unreachable;
    
    var detections = ArrayList(Detection).init(allocator);
    defer detections.deinit();
    
    // Skin tone detection (optimized HSV ranges)
    const skin_ranges = [_]struct { h_min: u8, h_max: u8, s_min: u8, s_max: u8, v_min: u8, v_max: u8 }{
        .{ .h_min = 0, .h_max = 20, .s_min = 20, .s_max = 255, .v_min = 70, .v_max = 255 },
        .{ .h_min = 160, .h_max = 180, .s_min = 20, .s_max = 255, .v_min = 70, .v_max = 255 },
    };
    
    var mask = try Image.init(allocator, image.width, image.height, 1);
    defer mask.deinit(allocator);
    
    for (skin_ranges) |range| {
        @memset(mask.data, 0);
        
        // Fast BGR to HSV conversion and masking
        var i: usize = 0;
        var mask_i: usize = 0;
        while (i < image.data.len) : (i += 3) {
            const b = image.data[i];
            const g = image.data[i + 1];
            const r = image.data[i + 2];
            
            // Fast HSV conversion (approximation for speed)
            const max_val = @max(@max(r, g), b);
            const min_val = @min(@min(r, g), b);
            const diff = max_val - min_val;
            
            const v = max_val;
            const s = if (max_val == 0) 0 else @as(u8, @intCast((diff * 255) / max_val));
            
            var h: u8 = 0;
            if (diff != 0) {
                if (max_val == r) {
                    h = @intCast(((g -% b) * 43) / diff); // 43 ≈ 255/6
                } else if (max_val == g) {
                    h = @intCast(85 + ((b -% r) * 43) / diff); // 85 ≈ 255/3
                } else {
                    h = @intCast(171 + ((r -% g) * 43) / diff); // 171 ≈ 2*255/3
                }
            }
            
            // Check if pixel matches skin range
            if ((h >= range.h_min and h <= range.h_max) and
                (s >= range.s_min and s <= range.s_max) and
                (v >= range.v_min and v <= range.v_max)) {
                mask.data[mask_i] = 255;
            }
            
            mask_i += 1;
        }
        
        // Find contours in mask (simplified version)
        var visited = try allocator.alloc(bool, mask.data.len);
        defer allocator.free(visited);
        @memset(visited, false);
        
        for (0..image.height) |y| {
            for (0..image.width) |x| {
                const index = y * image.width + x;
                if (!visited[index] and mask.data[index] == 255) {
                    var blob = try floodFill(allocator, &mask, visited, @intCast(x), @intCast(y));
                    
                    if (blob.area > 200 and blob.area < 20000) {
                        const confidence = @min(blob.area / 5000.0, 0.8);
                        try detections.append(Detection{
                            .bbox = blob.bbox,
                            .confidence = @floatCast(confidence),
                            .detection_type = 1, // color
                            .area = blob.area,
                        });
                    }
                }
            }
        }
    }
    
    const processing_time = @as(f64, @floatFromInt(timer.read())) / 1000000.0;
    print("Color detection processed in {d:.2} ms\n", .{processing_time});
    
    return detections.toOwnedSlice();
}

// C-compatible exports for Python integration
export fn zig_capture_screen(width: *u32, height: *u32, data: **u8) bool {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    
    if (captureVRChatWindow(allocator, "VRChat")) |image_opt| {
        if (image_opt) |image| {
            width.* = image.width;
            height.* = image.height;
            data.* = image.data.ptr;
            return true;
        }
    } else |_| {}
    
    return false;
}

export fn zig_detect_motion(current_data: [*]u8, previous_data: [*]u8, width: u32, height: u32, detections: **Detection, count: *u32) bool {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    
    const current = Image{
        .data = current_data[0..width * height * 3],
        .width = width,
        .height = height,
        .channels = 3,
    };
    
    const previous = Image{
        .data = previous_data[0..width * height * 3],
        .width = width,
        .height = height,
        .channels = 3,
    };
    
    if (detectMotion(allocator, &current, &previous, 30)) |results| {
        detections.* = results.ptr;
        count.* = @intCast(results.len);
        return true;
    } else |_| {
        return false;
    }
}

// Build script integration
pub fn main() !void {
    print("Fast Vision Zig Module - Ready for compilation\n");
}
