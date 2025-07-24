#!/usr/bin/env python3
"""
Test Enhanced Ableton Integration

Comprehensive testing of the real-time Ableton Live integration system.

Usage:
    python test_ableton_integration.py

Requirements:
    - Ableton Live running with MCP Remote Script installed
    - AbletonMCP control surface configured in Ableton preferences
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AbletonIntegrationTester:
    """Comprehensive tester for Ableton integration"""
    
    def __init__(self):
        """Initialize the tester"""
        self.ableton = None
        self.test_results = {}
        
    async def run_all_tests(self):
        """Run all integration tests"""
        print("🎛️ ENHANCED ABLETON INTEGRATION TEST SUITE")
        print("=" * 60)
        
        try:
            # Initialize integration
            await self._test_initialization()
            
            # Connection tests
            await self._test_connection()
            
            # Command tests
            await self._test_commands()
            
            # Generation tests
            await self._test_generation()
            
            # Monitoring tests
            await self._test_monitoring()
            
            # Print summary
            self._print_test_summary()
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            return False
        
        finally:
            # Cleanup
            if self.ableton:
                self.ableton.disconnect()
    
    async def _test_initialization(self):
        """Test initialization of enhanced integration"""
        print("\n🔧 Testing initialization...")
        
        try:
            from music_intelligence.ableton_integration import EnhancedAbletonIntegration
            self.ableton = EnhancedAbletonIntegration()
            
            # Test status callback
            self.ableton.add_status_callback(self._status_callback)
            
            self.test_results["initialization"] = True
            print("✅ Initialization successful")
            
        except Exception as e:
            self.test_results["initialization"] = False
            print(f"❌ Initialization failed: {e}")
            raise
    
    async def _test_connection(self):
        """Test connection capabilities"""
        print("\n🔌 Testing connection...")
        
        # Test connection
        try:
            connected = await self.ableton.connect()
            self.test_results["connection"] = connected
            
            if connected:
                print("✅ Connection successful")
                
                # Test connection info
                info = self.ableton.get_connection_info()
                print(f"   📊 Status: {info['status']}")
                print(f"   🌐 Host: {info['host']}:{info['port']}")
                print(f"   📡 Monitoring: {info['monitoring_active']}")
                
                # Test session summary
                summary = self.ableton.get_session_summary()
                print(f"   🎵 Session: {summary['track_count']} tracks, {summary['tempo']} BPM")
                print(f"   ▶️ Playing: {summary['is_playing']}")
                
            else:
                print("❌ Connection failed")
                print("💡 Make sure:")
                print("   - Ableton Live is running")
                print("   - AbletonMCP Remote Script is installed")
                print("   - Control Surface is set to 'AbletonMCP'")
                
        except Exception as e:
            self.test_results["connection"] = False
            print(f"❌ Connection test failed: {e}")
    
    async def _test_commands(self):
        """Test basic command execution"""
        print("\n🎛️ Testing commands...")
        
        if not self.test_results.get("connection"):
            print("⏭️ Skipping command tests (no connection)")
            return
        
        try:
            # Test session info command
            print("   📊 Testing session info...")
            test_results = await self.ableton.test_connection()
            
            if test_results["command_test"]:
                print("   ✅ Command execution working")
                session_info = test_results.get("session_info", {})
                print(f"      Tracks: {len(session_info.get('tracks', []))}")
                print(f"      Scenes: {len(session_info.get('scenes', []))}")
                print(f"      Tempo: {session_info.get('tempo', 'Unknown')}")
            else:
                print("   ❌ Command execution failed")
            
            self.test_results["commands"] = test_results["command_test"]
            
        except Exception as e:
            self.test_results["commands"] = False
            print(f"❌ Command test failed: {e}")
    
    async def _test_generation(self):
        """Test track generation capabilities"""
        print("\n🎵 Testing track generation...")
        
        if not self.test_results.get("commands"):
            print("⏭️ Skipping generation tests (commands not working)")
            return
        
        try:
            # Create a simple test brief
            test_brief = {
                "style": "house",
                "bpm": 125,
                "key": "Am",
                "track_elements": ["kick", "bass"],
                "length_minutes": 2.0
            }
            
            print(f"   🎨 Generating test track: {test_brief['style']} at {test_brief['bpm']} BPM")
            
            # Track progress
            progress_updates = []
            def progress_callback(message, progress):
                progress_updates.append((message, progress))
                print(f"      📈 {progress*100:.0f}%: {message}")
            
            # Generate track
            actions = await self.ableton.generate_track_from_brief(test_brief, progress_callback)
            
            if actions:
                print(f"   ✅ Generation successful: {len(actions)} actions performed")
                for action in actions[-3:]:  # Show last 3 actions
                    print(f"      • {action.description}")
                
                self.test_results["generation"] = True
            else:
                print("   ❌ No actions generated")
                self.test_results["generation"] = False
                
        except Exception as e:
            self.test_results["generation"] = False
            print(f"❌ Generation test failed: {e}")
    
    async def _test_monitoring(self):
        """Test real-time monitoring"""
        print("\n👁️ Testing monitoring...")
        
        if not self.test_results.get("connection"):
            print("⏭️ Skipping monitoring tests (no connection)")
            return
        
        try:
            # Test monitoring start/stop
            print("   🔍 Starting monitoring...")
            self.ableton.start_monitoring()
            
            # Wait a bit for monitoring to work
            print("   ⏱️ Monitoring for 3 seconds...")
            await asyncio.sleep(3)
            
            # Check if monitoring is active
            if self.ableton.monitoring_active:
                print("   ✅ Monitoring active")
                
                # Get current state
                state = self.ableton.state
                print(f"      🎵 Current tempo: {state.tempo}")
                print(f"      📊 Track count: {state.track_count}")
                print(f"      🕒 Last updated: {state.last_updated}")
                
                self.test_results["monitoring"] = True
            else:
                print("   ❌ Monitoring not active")
                self.test_results["monitoring"] = False
            
            # Stop monitoring
            self.ableton.stop_monitoring()
            print("   ⏹️ Monitoring stopped")
            
        except Exception as e:
            self.test_results["monitoring"] = False
            print(f"❌ Monitoring test failed: {e}")
    
    def _status_callback(self, status, state):
        """Callback for status changes during testing"""
        from music_intelligence.ableton_integration import ConnectionStatus
        
        status_messages = {
            ConnectionStatus.CONNECTED: "🟢 Connected",
            ConnectionStatus.DISCONNECTED: "🔴 Disconnected", 
            ConnectionStatus.CONNECTING: "🟡 Connecting",
            ConnectionStatus.RECONNECTING: "🟡 Reconnecting",
            ConnectionStatus.ERROR: "🔴 Error"
        }
        
        message = status_messages.get(status, f"Unknown: {status}")
        print(f"   📡 Status change: {message}")
    
    def _print_test_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        print(f"\n📈 Overall: {passed_tests}/{total_tests} tests passed")
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} {test_name.replace('_', ' ').title()}")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! Enhanced Ableton integration is working perfectly.")
        elif passed_tests > 0:
            print(f"\n⚠️ {total_tests - passed_tests} test(s) failed. Check Ableton setup.")
        else:
            print("\n❌ All tests failed. Ableton Live integration not working.")
        
        print("\n💡 If tests failed:")
        print("   1. Make sure Ableton Live is running")
        print("   2. Install AbletonMCP Remote Script")
        print("   3. Set Control Surface to 'AbletonMCP'")
        print("   4. Check that port 9877 is not blocked")


async def run_interactive_test():
    """Run interactive test with user prompts"""
    print("🎛️ INTERACTIVE ABLETON INTEGRATION TEST")
    print("=" * 50)
    
    # Ask user about setup
    print("\n📋 Pre-flight checklist:")
    
    ableton_running = input("✓ Is Ableton Live running? (y/n): ").lower() == 'y'
    if not ableton_running:
        print("❌ Please start Ableton Live first")
        return
    
    script_installed = input("✓ Is AbletonMCP Remote Script installed? (y/n): ").lower() == 'y'
    if not script_installed:
        print("❌ Please install the AbletonMCP Remote Script")
        print("   See INSTALLATION.md for instructions")
        return
    
    control_surface = input("✓ Is Control Surface set to 'AbletonMCP'? (y/n): ").lower() == 'y'
    if not control_surface:
        print("❌ Please configure Ableton preferences:")
        print("   Preferences → Link, Tempo & MIDI → Control Surface: AbletonMCP")
        return
    
    print("\n✅ Setup looks good! Running tests...")
    
    # Run the tests
    tester = AbletonIntegrationTester()
    await tester.run_all_tests()


async def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Enhanced Ableton Integration")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Run interactive test with setup checks")
    parser.add_argument("--quick", "-q", action="store_true",
                       help="Run quick connection test only")
    
    args = parser.parse_args()
    
    if args.interactive:
        await run_interactive_test()
    elif args.quick:
        # Quick test
        print("🚀 Quick Ableton connection test...")
        from music_intelligence.ableton_integration import EnhancedAbletonIntegration
        
        ableton = EnhancedAbletonIntegration()
        test_results = await ableton.test_connection()
        
        if test_results["command_test"]:
            print("✅ Ableton Live connected and working!")
            session = test_results.get("session_info", {})
            print(f"   📊 {len(session.get('tracks', []))} tracks, {session.get('tempo', 'Unknown')} BPM")
        else:
            print("❌ Ableton Live connection failed")
            if test_results.get("error"):
                print(f"   Error: {test_results['error']}")
        
        ableton.disconnect()
    else:
        # Full test suite
        tester = AbletonIntegrationTester()
        await tester.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1) 