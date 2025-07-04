#!/usr/bin/env python3
"""
Debug audio and TTS issues
"""

import pyttsx3
import sys
import time

def test_pyttsx3():
    """Test pyttsx3 TTS engine"""
    print("🔧 Testing pyttsx3 TTS engine...")
    
    try:
        engine = pyttsx3.init()
        print("✅ pyttsx3 engine initialized")
        
        # Check voices
        voices = engine.getProperty('voices')
        print(f"📢 Available voices: {len(voices) if voices else 0}")
        
        if voices:
            for i, voice in enumerate(voices):
                print(f"  {i}: {voice.name} - {voice.id}")
        
        # Check current settings
        rate = engine.getProperty('rate')
        volume = engine.getProperty('volume')
        current_voice = engine.getProperty('voice')
        
        print(f"🎚️ Current settings:")
        print(f"  Rate: {rate}")
        print(f"  Volume: {volume}")
        print(f"  Voice: {current_voice}")
        
        # Test speech
        print("🎤 Testing speech output...")
        engine.say("This is a test of the pyttsx3 text to speech engine. Can you hear me?")
        engine.runAndWait()
        
        print("✅ Speech test completed")
        
        # Test different volume levels
        print("🔊 Testing volume levels...")
        for vol in [0.5, 0.7, 1.0]:
            engine.setProperty('volume', vol)
            engine.say(f"Volume level is now {vol}")
            engine.runAndWait()
            time.sleep(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_windows_tts():
    """Test Windows TTS directly"""
    print("\n🔧 Testing Windows TTS directly...")
    
    try:
        import comtypes.client
        
        # Create SAPI voice object
        voice = comtypes.client.CreateObject("SAPI.SpVoice")
        
        # Test speech
        print("🎤 Testing Windows SAPI speech...")
        voice.Speak("This is a test of Windows Speech API. Can you hear this?")
        
        print("✅ Windows SAPI test completed")
        
    except Exception as e:
        print(f"❌ Windows SAPI Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 LYRA Audio Debug Tool")
    print("=" * 50)
    
    # Test pyttsx3
    success1 = test_pyttsx3()
    
    # Test Windows TTS
    success2 = test_windows_tts()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ All tests passed - TTS should be working")
        print("💡 If you can't hear audio, check:")
        print("   - Windows sound settings")
        print("   - Default playback device")
        print("   - Volume levels")
        print("   - Audio drivers")
    else:
        print("❌ Some tests failed - TTS may not be working properly")
