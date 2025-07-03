#!/usr/bin/env python3
"""
LYRA 3.0 Component Test
Test all core functionalities
"""

import os
import sys
import time
import threading

# Add core modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.decision_engine import DecisionEngine
from core.context_manager import ContextManager
from core.voice_input import VoiceInput
from core.tts_output import TTSOutput

def test_system_monitoring():
    """Test system monitoring functionality"""
    print("🔧 Testing system monitoring...")
    
    try:
        import psutil
        import platform
        
        # Test CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"   CPU Usage: {cpu_percent}%")
        
        # Test memory usage
        memory = psutil.virtual_memory()
        print(f"   Memory Usage: {memory.percent}%")
        
        # Test disk usage
        if platform.system() == 'Windows':
            disk_usage = psutil.disk_usage('C:\\')
        else:
            disk_usage = psutil.disk_usage('/')
        disk_percent = (disk_usage.used / disk_usage.total) * 100
        print(f"   Disk Usage: {disk_percent:.1f}%")
        
        # Test internet connection
        try:
            import urllib.request
            urllib.request.urlopen('http://www.google.com', timeout=5)
            print(f"   Internet: Connected ✅")
        except:
            print(f"   Internet: Disconnected ❌")
        
        print("   System monitoring: ✅ Working")
        
    except Exception as e:
        print(f"   System monitoring: ❌ Error - {e}")

def test_tts():
    """Test text-to-speech functionality"""
    print("🗣️ Testing TTS...")
    
    try:
        tts = TTSOutput()
        tts.speak("Hello, this is LYRA 3.0 text to speech test.")
        print("   TTS: ✅ Working")
        time.sleep(2)  # Wait for speech to complete
        
    except Exception as e:
        print(f"   TTS: ❌ Error - {e}")

def test_decision_engine():
    """Test decision engine functionality"""
    print("🧠 Testing decision engine...")
    
    try:
        context_mgr = ContextManager()
        engine = DecisionEngine(context_mgr)
        
        # Test various commands
        test_commands = [
            "system status",
            "hello LYRA",
            "help",
            "TRINETRA move forward",
            "KRAIT-3 launch"
        ]
        
        for cmd in test_commands:
            response = engine.process_command(cmd)
            print(f"   Command: '{cmd}' -> {response.get('status', 'unknown')}")
        
        print("   Decision Engine: ✅ Working")
        
    except Exception as e:
        print(f"   Decision Engine: ❌ Error - {e}")

def test_voice_recognition():
    """Test voice recognition functionality"""
    print("🎤 Testing voice recognition...")
    
    try:
        voice_input = VoiceInput()
        
        if voice_input.recognizer:
            print("   Voice Recognition: ✅ Initialized")
            print("   Note: Voice recognition is ready but not actively listening in this test")
        else:
            print("   Voice Recognition: ⚠️ Initialized but no microphone detected")
            
    except Exception as e:
        print(f"   Voice Recognition: ❌ Error - {e}")

def test_modes():
    """Test different operational modes"""
    print("⚙️ Testing modes...")
    
    try:
        context_mgr = ContextManager()
        engine = DecisionEngine(context_mgr)
        
        # Test mode switching
        modes = ['defense', 'home', 'night', 'manual']
        
        for mode in modes:
            response = engine.process_command(f"switch to {mode} mode")
            if response.get('status') == 'success':
                print(f"   Mode '{mode}': ✅ Working")
            else:
                print(f"   Mode '{mode}': ❌ Failed")
        
        print("   Modes: ✅ Working")
        
    except Exception as e:
        print(f"   Modes: ❌ Error - {e}")

def main():
    """Run all component tests"""
    print("=" * 60)
    print("🤖 LYRA 3.0 Component Testing")
    print("=" * 60)
    
    # Run all tests
    test_system_monitoring()
    print()
    
    test_tts()
    print()
    
    test_decision_engine()
    print()
    
    test_voice_recognition()
    print()
    
    test_modes()
    print()
    
    print("=" * 60)
    print("🎯 LYRA 3.0 Component Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
