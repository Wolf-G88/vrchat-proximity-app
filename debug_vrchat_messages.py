#!/usr/bin/env python3
"""
VRChat OSC Message Capture - See what messages VRChat actually sends
This tool captures and analyzes real OSC messages from VRChat
"""

import sys
import time
import threading
from pathlib import Path
from collections import defaultdict, Counter

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pythonosc import dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

class VRChatMessageCapture:
    """Captures and analyzes VRChat OSC messages"""
    
    def __init__(self):
        self.messages = []
        self.message_counts = Counter()
        self.address_patterns = defaultdict(list)
        self.server = None
        self.server_thread = None
        
    def start_capture(self, duration=30):
        """Start capturing VRChat OSC messages"""
        print(f"🎧 Starting VRChat OSC message capture for {duration} seconds...")
        print("📝 This will show you exactly what messages VRChat sends")
        print("🎮 Make sure VRChat is running and OSC is enabled")
        print()
        
        # Set up message handler
        disp = dispatcher.Dispatcher()
        disp.map("/*", self._handle_message)  # Catch ALL messages
        
        # Start server
        self.server = ThreadingOSCUDPServer(("127.0.0.1", 9001), disp)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        
        print(f"✅ Listening on port 9001...")
        
        # Capture for specified duration
        time.sleep(duration)
        
        # Stop server
        self.server.shutdown()
        if self.server_thread:
            self.server_thread.join(timeout=2.0)
        
        print(f"\n📊 Capture complete! Received {len(self.messages)} messages")
        
    def _handle_message(self, address, *args):
        """Handle incoming OSC message"""
        timestamp = time.time()
        self.messages.append({
            'timestamp': timestamp,
            'address': address,
            'args': args
        })
        self.message_counts[address] += 1
        
        # Group similar addresses
        address_pattern = self._get_address_pattern(address)
        self.address_patterns[address_pattern].append((address, args))
        
        # Print interesting messages immediately
        if self._is_interesting_message(address):
            print(f"🔍 {address}: {args}")
    
    def _get_address_pattern(self, address):
        """Get pattern for address (group similar addresses)"""
        parts = address.split('/')
        if len(parts) >= 3 and parts[1] == 'avatar' and parts[2] == 'parameters':
            return "/avatar/parameters/*"
        elif len(parts) >= 2 and parts[1] == 'tracking':
            return "/tracking/*"
        elif len(parts) >= 2 and parts[1] == 'user':
            return "/user/*"
        elif len(parts) >= 2 and parts[1] == 'chatbox':
            return "/chatbox/*"
        else:
            return address
    
    def _is_interesting_message(self, address):
        """Check if message is potentially interesting for user detection"""
        interesting_patterns = [
            '/user/',
            '/tracking/',
            '/instance/',
            '/world/',
            '/chatbox/',
            '/vrc',  # VRC-specific messages
        ]
        
        return any(pattern in address.lower() for pattern in interesting_patterns)
    
    def analyze_messages(self):
        """Analyze captured messages"""
        if not self.messages:
            print("❌ No messages captured!")
            print("💡 Make sure:")
            print("   1. VRChat is running")
            print("   2. OSC is enabled in VRChat settings")
            print("   3. You're in a world with other users")
            return
        
        print("\n" + "="*60)
        print("📈 MESSAGE ANALYSIS")
        print("="*60)
        
        print(f"Total messages: {len(self.messages)}")
        print(f"Unique addresses: {len(self.message_counts)}")
        print(f"Time span: {self.messages[-1]['timestamp'] - self.messages[0]['timestamp']:.1f} seconds")
        
        print("\n🏷️  ADDRESS PATTERNS:")
        for pattern, messages in sorted(self.address_patterns.items(), key=lambda x: len(x[1]), reverse=True):
            count = len(messages)
            if count > 5:  # Only show patterns with multiple messages
                print(f"  {pattern}: {count} messages")
                # Show a few examples
                for addr, args in messages[:3]:
                    print(f"    Example: {addr} {args}")
                if len(messages) > 3:
                    print(f"    ... and {len(messages) - 3} more")
        
        print("\n🔥 TOP MESSAGE ADDRESSES:")
        for address, count in self.message_counts.most_common(15):
            print(f"  {address}: {count}")
        
        print("\n🎯 USER/TRACKING RELATED MESSAGES:")
        user_messages = [msg for msg in self.messages if 
                        'user' in msg['address'].lower() or 
                        'tracking' in msg['address'].lower() or
                        'instance' in msg['address'].lower() or
                        'world' in msg['address'].lower()]
        
        if user_messages:
            print(f"Found {len(user_messages)} potentially relevant messages:")
            for msg in user_messages[:10]:  # Show first 10
                print(f"  {msg['address']}: {msg['args']}")
        else:
            print("❌ No user/tracking messages found!")
            print("💡 This might explain why user detection isn't working")
        
        print("\n🧩 RECOMMENDATIONS:")
        
        # Check for avatar parameters (indicates VRChat is sending data)
        avatar_params = [addr for addr in self.message_counts.keys() if '/avatar/parameters/' in addr]
        if avatar_params:
            print("✅ Avatar parameters detected - VRChat OSC is working")
            print(f"   Found {len(avatar_params)} different parameters")
        else:
            print("❌ No avatar parameters detected - OSC might not be enabled")
        
        # Check for tracking data
        tracking_msgs = [addr for addr in self.message_counts.keys() if '/tracking/' in addr]
        if tracking_msgs:
            print("✅ Tracking data detected")
        else:
            print("❌ No tracking data - this is needed for position detection")
        
        # Check for user data
        user_msgs = [addr for addr in self.message_counts.keys() if '/user/' in addr]
        if user_msgs:
            print("✅ User messages detected")
        else:
            print("❌ No user messages - VRChat doesn't send other users' data automatically")
            print("💡 You might need to request this data or use a different approach")
        
        # Check chatbox (can indicate other users talking)
        chatbox_msgs = [addr for addr in self.message_counts.keys() if 'chatbox' in addr.lower()]
        if chatbox_msgs:
            print("✅ Chatbox messages detected - other users might be talking")
        
        print("\n🔧 NEXT STEPS:")
        if not user_msgs and not tracking_msgs:
            print("1. Enable OSC in VRChat Settings > OSC > Enable")
            print("2. Try joining a world with other users")
            print("3. Move around or interact to trigger more messages")
            print("4. Check if VRChat has user position sharing options")
        else:
            print("1. Update OSC integration to handle the detected message patterns")
            print("2. Focus on the message types that are actually being sent")

def main():
    """Main diagnostic routine"""
    print("🎮 VRChat OSC Message Capture Tool")
    print("=" * 50)
    print("This tool captures real OSC messages from VRChat")
    print("to help debug user detection issues.")
    print()
    
    capture_time = 30
    try:
        duration_input = input(f"Capture duration in seconds (default {capture_time}): ").strip()
        if duration_input:
            capture_time = int(duration_input)
    except ValueError:
        pass
    
    print()
    capture = VRChatMessageCapture()
    
    try:
        capture.start_capture(capture_time)
        capture.analyze_messages()
        
        print("\n💾 SAVE MESSAGES TO FILE?")
        save = input("Save captured messages to file? (y/N): ").strip().lower()
        if save.startswith('y'):
            filename = f"vrchat_messages_{int(time.time())}.txt"
            with open(filename, 'w') as f:
                f.write(f"VRChat OSC Messages Captured at {time.ctime()}\n")
                f.write(f"Total messages: {len(capture.messages)}\n\n")
                
                for msg in capture.messages:
                    f.write(f"{msg['timestamp']}: {msg['address']} {msg['args']}\n")
            
            print(f"💾 Messages saved to {filename}")
            
    except KeyboardInterrupt:
        print("\n⏹️  Capture interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n🏁 Diagnostic complete!")

if __name__ == "__main__":
    main()
