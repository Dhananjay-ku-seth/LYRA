#!/usr/bin/env python3
"""
Test TTS functionality to debug speech issues
"""

import sys
import os
import logging

# Add core modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.tts_output import TTSOutput

def test_tts():
    """Test TTS functionality"""
    print("🔧 Testing TTS functionality...")
    
    # Setup logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Initialize TTS
    tts = TTSOutput()
    
    # Test basic speech
    print("🎤 Testing basic speech...")
    tts.speak("Hello, this is a TTS test.")
    
    # Wait a moment
    import time
    time.sleep(3)
    
    # Test longer speech
    print("🎤 Testing longer speech...")
    tts.speak("LYRA 3.0 text to speech system is now being tested. Can you hear this message clearly?")
    
    time.sleep(5)
    
    # Test command response
    print("🎤 Testing command response...")
    tts.speak("Hello Commander. LYRA 3.0 is ready for your commands.")
    
    time.sleep(3)
    
    print("✅ TTS test completed!")

if __name__ == "__main__":
    test_tts()
