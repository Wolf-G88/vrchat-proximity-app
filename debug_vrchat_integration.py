#!/usr/bin/env python3
"""
VRChat OSC Integration Diagnostics - Debug and test VRChat connectivity
This tool helps diagnose connection issues with VRChat OSC
"""

import sys
import asyncio
import time
import socket
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.integration.vrchat_osc import VRChatOSCConfig, VRChatOSCClient
from src.core.proximity_engine import ProximityEngine, UserPosition, VisibilitySettings
from pythonosc import udp_client
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc import dispatcher
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VRChatDiagnostics:
    """Comprehensive VRChat OSC diagnostics"""
    
    def __init__(self):
        self.results = {}
    
    def check_network_connectivity(self):
        """Test basic network connectivity for OSC ports"""
        print("🔍 Testing Network Connectivity...")
        
        # Test if ports are available
        ports_to_test = [9000, 9001]
        for port in ports_to_test:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind(('127.0.0.1', port))
                sock.close()
                print(f"  ✅ Port {port}: Available")
                self.results[f'port_{port}_available'] = True
            except OSError as e:
                print(f"  ❌ Port {port}: In use or blocked - {e}")
                self.results[f'port_{port}_available'] = False
    
    def test_osc_send(self):
        """Test sending OSC messages"""
        print("📤 Testing OSC Message Sending...")
        
        try:
            client = udp_client.SimpleUDPClient("127.0.0.1", 9000)
            
            # Send test messages
            test_messages = [
                ("/ping", [time.time()]),
                ("/test/diagnostic", ["hello_vrchat"]),
                ("/avatar/parameters/test", [1.0])
            ]
            
            for address, args in test_messages:
                try:
                    client.send_message(address, args)
                    print(f"  ✅ Sent: {address} {args}")
                except Exception as e:
                    print(f"  ❌ Failed to send {address}: {e}")
                    
            self.results['osc_send_working'] = True
            
        except Exception as e:
            print(f"  ❌ OSC Client creation failed: {e}")
            self.results['osc_send_working'] = False
    
    def test_osc_receive(self):
        """Test receiving OSC messages"""
        print("📥 Testing OSC Message Reception...")
        
        received_messages = []
        
        def message_handler(address, *args):
            received_messages.append((address, args))
            print(f"  📨 Received: {address} {args}")
        
        try:
            # Set up receiver
            disp = dispatcher.Dispatcher()
            disp.map("/*", message_handler)  # Catch all messages
            
            server = ThreadingOSCUDPServer(("127.0.0.1", 9001), disp)
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            
            print("  🎧 OSC Server listening on port 9001...")
            
            # Send test messages to ourselves
            time.sleep(0.5)  # Let server start up
            client = udp_client.SimpleUDPClient("127.0.0.1", 9001)
            
            test_messages = [
                ("/test/echo", ["diagnostic_test"]),
                ("/user/test_user/position", [1.0, 2.0, 3.0]),
                ("/avatar/parameters/proximity_test", [0.5])
            ]
            
            for address, args in test_messages:
                client.send_message(address, args)
                time.sleep(0.1)
            
            time.sleep(1.0)  # Wait for messages to arrive
            
            server.shutdown()
            server_thread.join(timeout=2.0)
            
            if received_messages:
                print(f"  ✅ Successfully received {len(received_messages)} messages")
                self.results['osc_receive_working'] = True
            else:
                print("  ❌ No messages received")
                self.results['osc_receive_working'] = False
                
        except Exception as e:
            print(f"  ❌ OSC Server test failed: {e}")
            self.results['osc_receive_working'] = False
    
    async def test_vrchat_integration(self):
        """Test the full VRChat integration"""
        print("🎮 Testing VRChat Integration...")
        
        # Create proximity engine
        settings = VisibilitySettings()
        proximity_engine = ProximityEngine(settings)
        
        # Create OSC client
        config = VRChatOSCConfig()
        osc_client = VRChatOSCClient(config, proximity_engine)
        
        # Add some callbacks for testing
        message_count = {'position': 0, 'user': 0, 'parameter': 0}
        
        def on_position_update(position):
            message_count['position'] += 1
            print(f"  📍 Position update: {position.username} at ({position.x:.1f}, {position.y:.1f}, {position.z:.1f})")
        
        def on_user_event(event_type, user_id, username):
            message_count['user'] += 1
            print(f"  👤 User event: {event_type} - {username} ({user_id})")
        
        def on_parameter_change(param_name, value):
            message_count['parameter'] += 1
            print(f"  ⚙️ Parameter: {param_name} = {value}")
        
        osc_client.register_position_callback(on_position_update)
        osc_client.register_user_callback(on_user_event)
        osc_client.register_parameter_callback(on_parameter_change)
        
        try:
            # Connect to VRChat OSC
            await osc_client.connect()
            
            if osc_client.connected:
                print("  ✅ VRChat OSC connection established")
                
                # Set a local user
                osc_client.set_local_user_id("diagnostic_user")
                
                # Send some test data to ourselves
                test_client = udp_client.SimpleUDPClient("127.0.0.1", 9001)
                
                # Simulate VRChat sending data
                print("  📤 Sending test data to integration...")
                
                test_messages = [
                    ("/tracking/head/position", [5.0, 1.8, 2.0]),
                    ("/user/test_user_1/join", ["TestUser1"]),
                    ("/user/test_user_1/position", [10.0, 1.8, 5.0]),
                    ("/avatar/parameters/test_param", [0.75]),
                    ("/user/test_user_2/join", ["TestUser2"]),
                    ("/user/test_user_2/position", [15.0, 1.8, -3.0]),
                ]
                
                for address, args in test_messages:
                    test_client.send_message(address, args)
                    await asyncio.sleep(0.1)
                
                # Wait for messages to be processed
                await asyncio.sleep(2.0)
                
                # Check results
                print(f"  📊 Messages processed:")
                print(f"     Position updates: {message_count['position']}")
                print(f"     User events: {message_count['user']}")
                print(f"     Parameter changes: {message_count['parameter']}")
                
                # Test visibility commands
                print("  🔍 Testing visibility commands...")
                osc_client.send_visibility_command("test_user_1", True, 0.8)
                osc_client.send_visibility_command("test_user_2", False, 0.0)
                
                # Get status
                status = osc_client.get_connection_status()
                print(f"  📋 Connection Status:")
                print(f"     Connected: {status['connected']}")
                print(f"     Local User: {status['local_user_id']}")
                print(f"     Tracked Users: {status['tracked_users_count']}")
                print(f"     Server Running: {status['server_running']}")
                
                self.results['vrchat_integration_working'] = True
                
            else:
                print("  ❌ Failed to establish VRChat OSC connection")
                self.results['vrchat_integration_working'] = False
                
        except Exception as e:
            print(f"  ❌ VRChat integration test failed: {e}")
            logger.exception("VRChat integration error:")
            self.results['vrchat_integration_working'] = False
            
        finally:
            try:
                await osc_client.disconnect()
            except:
                pass
    
    def generate_report(self):
        """Generate a diagnostic report"""
        print("\n" + "="*60)
        print("🔬 DIAGNOSTIC REPORT")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        
        print(f"Tests Run: {total_tests}")
        print(f"Tests Passed: {passed_tests}")
        print(f"Tests Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "N/A")
        
        print("\nDetailed Results:")
        for test_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        print("\n" + "="*60)
        print("💡 RECOMMENDATIONS")
        print("="*60)
        
        if not self.results.get('port_9000_available', True):
            print("⚠️  Port 9000 is in use. Check if VRChat is running or another OSC application is using this port.")
            
        if not self.results.get('port_9001_available', True):
            print("⚠️  Port 9001 is in use. Another application might be listening on VRChat's OSC input port.")
            
        if not self.results.get('osc_send_working', True):
            print("⚠️  OSC message sending failed. Check network permissions and firewall settings.")
            
        if not self.results.get('osc_receive_working', True):
            print("⚠️  OSC message reception failed. Check if port 9001 is accessible.")
            
        if not self.results.get('vrchat_integration_working', True):
            print("⚠️  VRChat integration has issues. Check the detailed logs above for specific errors.")
            
        if all(self.results.values()):
            print("🎉 All tests passed! Your VRChat OSC integration should work correctly.")
        else:
            print("🔧 Some tests failed. Address the issues above before using VRChat integration.")

async def main():
    """Main diagnostic routine"""
    print("🧪 VRChat OSC Integration Diagnostics")
    print("="*50)
    print("This tool will test your VRChat OSC connectivity")
    print("and help identify any integration issues.")
    print("="*50)
    print()
    
    diagnostics = VRChatDiagnostics()
    
    # Run diagnostic tests
    diagnostics.check_network_connectivity()
    print()
    
    diagnostics.test_osc_send()
    print()
    
    diagnostics.test_osc_receive()
    print()
    
    await diagnostics.test_vrchat_integration()
    print()
    
    # Generate final report
    diagnostics.generate_report()
    
    print("\n🏁 Diagnostic complete!")
    print("If all tests passed, your VRChat integration should work.")
    print("If tests failed, please address the recommended fixes.")

if __name__ == "__main__":
    asyncio.run(main())
