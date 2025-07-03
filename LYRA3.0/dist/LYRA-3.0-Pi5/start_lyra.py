#!/usr/bin/env python3
"""
LYRA 3.0 Enhanced Startup Script
Starts LYRA with monitoring and error recovery
"""

import os
import sys
import time
import subprocess
import threading
import logging
from datetime import datetime

# Add core modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

def setup_startup_logging():
    """Setup logging for startup script"""
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - STARTUP - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/startup.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'psutil', 'pyttsx3', 'SpeechRecognition', 'pyaudio',
        'flask', 'flask-socketio', 'python-socketio'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        logging.error(f"Missing dependencies: {', '.join(missing)}")
        logging.info("Installing missing dependencies...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + missing)
            logging.info("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install dependencies: {e}")
            return False
    
    return True

def check_audio_devices():
    """Check if audio devices are available"""
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        
        # Check for input devices
        input_devices = 0
        output_devices = 0
        
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices += 1
            if info['maxOutputChannels'] > 0:
                output_devices += 1
        
        p.terminate()
        
        logging.info(f"Audio devices found: {input_devices} input, {output_devices} output")
        
        if input_devices == 0:
            logging.warning("No microphone detected - voice input will be disabled")
        if output_devices == 0:
            logging.warning("No speakers detected - TTS may not work")
            
        return input_devices > 0 or output_devices > 0
        
    except Exception as e:
        logging.error(f"Audio device check failed: {e}")
        return False

def test_core_components():
    """Test if core LYRA components can be imported"""
    try:
        from core.decision_engine import DecisionEngine
        from core.context_manager import ContextManager
        from core.voice_input import VoiceInput
        from core.tts_output import TTSOutput
        
        # Quick initialization test
        context_mgr = ContextManager()
        engine = DecisionEngine(context_mgr)
        voice_input = VoiceInput()
        tts_output = TTSOutput()
        
        logging.info("✅ Core components test passed")
        return True
        
    except Exception as e:
        logging.error(f"❌ Core components test failed: {e}")
        return False

def monitor_system_health():
    """Monitor system health in background"""
    while True:
        try:
            import psutil
            
            # Check CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 90:
                logging.warning(f"High CPU usage: {cpu_percent}%")
            if memory_percent > 85:
                logging.warning(f"High memory usage: {memory_percent}%")
            
            # Check internet connection
            try:
                import urllib.request
                urllib.request.urlopen('http://www.google.com', timeout=5)
            except:
                logging.warning("Internet connection lost")
            
            time.sleep(60)  # Check every minute
            
        except Exception as e:
            logging.error(f"Health monitoring error: {e}")
            time.sleep(60)

def start_electron_gui():
    """Start the Electron GUI if available"""
    try:
        if os.path.exists('electron-main.js') and os.path.exists('package.json'):
            logging.info("Starting Electron GUI...")
            subprocess.Popen(['npm', 'start'], cwd=os.getcwd())
            return True
    except Exception as e:
        logging.warning(f"Could not start Electron GUI: {e}")
    
    return False

def main():
    """Main startup function"""
    print("=" * 80)
    print("🤖 LYRA 3.0 - Enhanced Startup")
    print("🚀 Logical Yielding Response Algorithm")
    print("=" * 80)
    
    setup_startup_logging()
    
    logging.info("Starting LYRA 3.0 system...")
    
    # Pre-flight checks
    logging.info("Running pre-flight checks...")
    
    if not check_dependencies():
        logging.error("❌ Dependency check failed")
        return False
    
    if not check_audio_devices():
        logging.warning("⚠️ Audio device issues detected")
    
    if not test_core_components():
        logging.error("❌ Core component test failed")
        return False
    
    logging.info("✅ All pre-flight checks passed")
    
    # Start health monitoring in background
    health_thread = threading.Thread(target=monitor_system_health, daemon=True)
    health_thread.start()
    logging.info("🔍 System health monitoring started")
    
    # Try to start Electron GUI
    gui_started = start_electron_gui()
    if gui_started:
        logging.info("🖥️ Electron GUI started")
    else:
        logging.info("🌐 GUI available at http://localhost:5000")
    
    # Start main LYRA system
    try:
        logging.info("🎯 Starting LYRA core system...")
        
        # Import and run main LYRA
        import main
        main.main()
        
    except KeyboardInterrupt:
        logging.info("🛑 LYRA shutdown requested by user")
        return True
    except Exception as e:
        logging.error(f"❌ LYRA system error: {e}")
        logging.info("🔄 Attempting restart in 5 seconds...")
        time.sleep(5)
        return main()  # Restart

if __name__ == "__main__":
    try:
        success = main()
        if success:
            logging.info("✅ LYRA shutdown complete")
        else:
            logging.error("❌ LYRA failed to start")
            sys.exit(1)
    except Exception as e:
        logging.error(f"❌ Startup script error: {e}")
        sys.exit(1)
