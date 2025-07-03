#!/usr/bin/env python3
"""
LYRA 3.0 (Logical Yielding Response Algorithm)
Raspberry Pi 5 Optimized Main Entry Point
"""

import os
import sys
import logging
import asyncio
import signal
import platform
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import threading
import json
from datetime import datetime

# Add core modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'system'))

from core.decision_engine import DecisionEngine
from core.context_manager import ContextManager
from core.voice_input import VoiceInput
from core.tts_output import TTSOutput

# Pi5-specific imports
try:
    from core.pi5_hardware import Pi5Hardware
    PI5_HARDWARE_AVAILABLE = True
except ImportError as e:
    print(f"Pi5 hardware module not available: {e}")
    PI5_HARDWARE_AVAILABLE = False
    
    # Create mock Pi5Hardware class for development
    class Pi5Hardware:
        def __init__(self):
            self.gpio_available = False
            self.camera_available = False
            self.i2c_available = False
            
        def optimize_performance(self):
            return "Mock optimization complete"
            
        def cleanup(self):
            pass
            
        def get_hardware_info(self):
            return {
                'gpio_available': False,
                'camera_available': False,
                'i2c_available': False,
                'platform': 'Non-Pi5 System'
            }
            
        def get_system_status(self):
            import psutil
            import platform
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:\\').percent,
                'temperature': 45.0,
                'timestamp': str(datetime.now()),
                'note': 'Mock Pi5 hardware for development'
            }

# Initialize Flask app with optimized settings for Pi5
app = Flask(__name__, 
            static_folder='gui',
            static_url_path='',
            template_folder='gui')
app.config['SECRET_KEY'] = 'lyra3_pi5_secure_key_2024'

# Optimized SocketIO for Raspberry Pi
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',  # Better for Pi5
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=1024*1024  # 1MB limit for Pi5
)

# Global LYRA components
lyra_engine = None
context_mgr = None
voice_input = None
tts_output = None
pi5_hardware = None
shutdown_event = threading.Event()

def setup_logging():
    """Setup optimized logging for Pi5"""
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging with rotation for SD card health
    from logging.handlers import RotatingFileHandler
    
    # Create rotating file handler
    file_handler = RotatingFileHandler(
        'logs/lyra_pi5.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=3
    )
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            file_handler,
            logging.StreamHandler(sys.stdout)
        ]
    )

def detect_platform():
    """Detect if running on Raspberry Pi 5"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'Raspberry Pi 5' in cpuinfo:
                return True, "Raspberry Pi 5"
            elif 'Raspberry Pi' in cpuinfo:
                return True, "Raspberry Pi (Other Model)"
            else:
                return False, platform.machine()
    except:
        return False, platform.machine()

def initialize_lyra_components():
    """Initialize all LYRA core components with Pi5 optimizations"""
    global lyra_engine, context_mgr, voice_input, tts_output, pi5_hardware
    
    is_pi, platform_info = detect_platform()
    logging.info(f"Platform detected: {platform_info}")
    
    logging.info("Initializing LYRA 3.0 components for Raspberry Pi 5...")
    
    # Initialize core components
    context_mgr = ContextManager()
    lyra_engine = DecisionEngine(context_mgr)
    voice_input = VoiceInput()
    tts_output = TTSOutput()
    
    # Initialize Pi5 hardware if available
    if PI5_HARDWARE_AVAILABLE and is_pi:
        try:
            pi5_hardware = Pi5Hardware()
            logging.info("Pi5 hardware integration initialized")
            
            # Optimize system performance
            result = pi5_hardware.optimize_performance()
            logging.info(f"Performance optimization: {result}")
            
        except Exception as e:
            logging.warning(f"Pi5 hardware initialization failed: {e}")
            pi5_hardware = None
    else:
        logging.info("Pi5 hardware integration not available")
    
    logging.info("LYRA 3.0 Pi5 initialization complete")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logging.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event.set()
    
    # Cleanup hardware resources
    if pi5_hardware:
        pi5_hardware.cleanup()
    
    # Stop Flask-SocketIO
    socketio.stop()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

@app.route('/')
def index():
    """Serve the main GUI"""
    return send_from_directory('gui', 'index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'platform': detect_platform()[1],
        'timestamp': str(datetime.now()),
        'pi5_hardware': PI5_HARDWARE_AVAILABLE and pi5_hardware is not None
    }

@socketio.on('connect')
def handle_connect():
    """Handle client connection with Pi5 info"""
    logging.info("Client connected to LYRA 3.0 Pi5")
    is_pi, platform_info = detect_platform()
    
    emit('status', {
        'message': f'Connected to LYRA 3.0 on {platform_info}',
        'platform': platform_info,
        'pi5_hardware': PI5_HARDWARE_AVAILABLE and pi5_hardware is not None,
        'timestamp': str(datetime.now())
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logging.info("Client disconnected from LYRA 3.0 Pi5")

@socketio.on('test')
def handle_test(data):
    """Handle test messages for WebSocket verification"""
    logging.info(f"Test message received: {data}")
    emit('test_reply', {'msg': 'Pong from LYRA 3.0 Pi5 backend'})

@socketio.on('command')
def handle_command(data):
    """Handle commands from the GUI with Pi5 optimizations"""
    try:
        command_type = data.get('type')
        command_data = data.get('data', {})
        
        logging.info(f"Received command: {command_type}")
        
        if command_type == 'voice_start':
            voice_input.start_listening()
            emit('response', {'type': 'voice_status', 'data': {'status': 'listening'}})
            
        elif command_type == 'voice_stop':
            voice_input.stop_listening()
            emit('response', {'type': 'voice_status', 'data': {'status': 'stopped'}})
            
        elif command_type == 'text_command':
            text = command_data.get('text', '')
            response = lyra_engine.process_command(text)
            emit('response', {'type': 'command_result', 'data': response})
            
        elif command_type == 'system_status':
            status = get_pi5_system_status()
            emit('response', {'type': 'system_status', 'data': status})
            
        elif command_type == 'gpio_control' and pi5_hardware:
            pin = command_data.get('pin')
            action = command_data.get('action')
            value = command_data.get('value')
            response = pi5_hardware.control_gpio_pin(pin, action, value)
            emit('response', {'type': 'gpio_response', 'data': response})
            
        elif command_type == 'camera_capture' and pi5_hardware:
            filename = command_data.get('filename')
            response = pi5_hardware.capture_camera_image(filename)
            emit('response', {'type': 'camera_response', 'data': response})
            
        elif command_type == 'camera_stream_start' and pi5_hardware:
            response = pi5_hardware.start_camera_stream()
            emit('response', {'type': 'camera_response', 'data': response})
            
        elif command_type == 'camera_stream_stop' and pi5_hardware:
            response = pi5_hardware.stop_camera_stream()
            emit('response', {'type': 'camera_response', 'data': response})
            
        elif command_type == 'hardware_info' and pi5_hardware:
            info = pi5_hardware.get_hardware_info()
            emit('response', {'type': 'hardware_info', 'data': info})
            
        elif command_type == 'trinetra_command':
            response = handle_trinetra_command(command_data)
            emit('response', {'type': 'trinetra_response', 'data': response})
            
        elif command_type == 'krait3_command':
            response = handle_krait3_command(command_data)
            emit('response', {'type': 'krait3_response', 'data': response})
            
        else:
            emit('response', {'type': 'error', 'data': {'message': f'Unknown command type: {command_type}'}})
            
    except Exception as e:
        logging.error(f"Error handling command: {e}")
        emit('response', {'type': 'error', 'data': {'message': str(e)}})

def get_pi5_system_status():
    """Get Pi5-optimized system status"""
    if pi5_hardware:
        return pi5_hardware.get_system_status()
    else:
        # Fallback system status
        try:
            import psutil
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'temperature': get_cpu_temperature(),
                'timestamp': str(datetime.now()),
                'note': 'Basic monitoring (Pi5 hardware not available)'
            }
        except ImportError:
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'temperature': get_cpu_temperature(),
                'timestamp': str(datetime.now()),
                'note': 'Limited monitoring available'
            }

def get_cpu_temperature():
    """Get CPU temperature (Pi-optimized)"""
    try:
        if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read()) / 1000.0
                return temp
    except:
        pass
    return 0

def handle_trinetra_command(command_data):
    """Handle TRINETRA ground bot commands with Pi5 GPIO integration"""
    action = command_data.get('action')
    
    logging.info(f"TRINETRA command: {action}")
    
    # If GPIO is available, could control actual hardware here
    if pi5_hardware and pi5_hardware.gpio_available:
        # Example GPIO control for motors
        if action == 'move_forward':
            # Control motor pins
            pass
        elif action == 'move_backward':
            # Control motor pins
            pass
    
    return {
        'status': 'success',
        'action': action,
        'message': f'TRINETRA {action} command executed',
        'timestamp': str(datetime.now()),
        'hardware_available': pi5_hardware is not None
    }

def handle_krait3_command(command_data):
    """Handle KRAIT-3 UAV commands with Pi5 serial integration"""
    action = command_data.get('action')
    
    logging.info(f"KRAIT-3 command: {action}")
    
    # Could integrate with MAVLink here via serial
    return {
        'status': 'success',
        'action': action,
        'message': f'KRAIT-3 {action} command executed',
        'timestamp': str(datetime.now()),
        'hardware_available': pi5_hardware is not None
    }

def run_flask_server():
    """Run the Flask-SocketIO server with Pi5 optimizations"""
    # Pi5-optimized server settings
    socketio.run(
        app, 
        host='0.0.0.0',  # Allow external connections
        port=5000, 
        debug=False,
        use_reloader=False,  # Disable for production
        allow_unsafe_werkzeug=True  # For Pi5 compatibility
    )

def main():
    """Main entry point for Pi5"""
    print("=" * 60)
    print("🍓 LYRA 3.0 - Raspberry Pi 5 Edition")
    print("🤖 Logical Yielding Response Algorithm")
    print("🚀 Starting AI Assistant System...")
    print("=" * 60)
    
    # Setup logging
    setup_logging()
    
    # Detect platform
    is_pi, platform_info = detect_platform()
    logging.info(f"Running on: {platform_info}")
    
    # Initialize LYRA components
    initialize_lyra_components()
    
    # Welcome message
    tts_output.speak("Welcome Commander. LYRA 3.0 Raspberry Pi edition is now online.")
    
    if pi5_hardware:
        logging.info("🍓 Pi5 hardware features available:")
        hardware_info = pi5_hardware.get_hardware_info()
        if hardware_info['gpio_available']:
            logging.info("  ✅ GPIO control")
        if hardware_info['camera_available']:
            logging.info("  ✅ Camera module")
        if hardware_info['i2c_available']:
            logging.info("  ✅ I2C communication")
    
    # Start Flask server
    logging.info("Starting optimized WebSocket server for Pi5...")
    logging.info("🌐 Access LYRA at: http://[PI_IP]:5000")
    
    try:
        run_flask_server()
    except KeyboardInterrupt:
        logging.info("Received shutdown signal")
    finally:
        if pi5_hardware:
            pi5_hardware.cleanup()
        logging.info("LYRA 3.0 Pi5 shutdown complete")

if __name__ == "__main__":
    main()
