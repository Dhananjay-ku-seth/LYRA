#!/usr/bin/env python3
"""
LYRA 3.0 (Logical Yielding Response Algorithm)
Main entry point for the AI assistant system
"""

import os
import sys
import logging
import asyncio
from flask import Flask, render_template
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

# Initialize Flask app for WebSocket communication with Electron
app = Flask(__name__)
app.config['SECRET_KEY'] = 'lyra3_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global LYRA components
lyra_engine = None
context_mgr = None
voice_input = None
tts_output = None

def setup_logging():
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/lyra_system.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def initialize_lyra_components():
    """Initialize all LYRA core components"""
    global lyra_engine, context_mgr, voice_input, tts_output
    
    logging.info("Initializing LYRA 3.0 components...")
    
    # Initialize core components
    context_mgr = ContextManager()
    lyra_engine = DecisionEngine(context_mgr)
    voice_input = VoiceInput()
    tts_output = TTSOutput()
    
    # Set up voice input callback to process speech
    voice_input.set_speech_callback(handle_voice_command)
    
    # Start continuous listening immediately
    voice_input.start_continuous_listening()
    
    logging.info("LYRA 3.0 initialization complete")
    logging.info("Continuous voice listening active - say 'Hi LYRA' or 'LYRA' to activate")

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logging.info("Client connected to LYRA 3.0")
    emit('status', {'message': 'Connected to LYRA 3.0', 'timestamp': str(datetime.now())})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logging.info("Client disconnected from LYRA 3.0")

@socketio.on('test')
def handle_test(data):
    """Handle test messages for WebSocket verification"""
    logging.info(f"Test message received: {data}")
    emit('test_reply', {'msg': 'Pong from LYRA 3.0 backend'})

@socketio.on('command')
def handle_command(data):
    """Handle commands from the GUI"""
    try:
        command_type = data.get('type')
        command_data = data.get('data', {})
        
        logging.info(f"Received command: {command_type}")
        
        if command_type == 'voice_start':
            # Start voice recognition
            voice_input.start_listening()
            emit('response', {'type': 'voice_status', 'data': {'status': 'listening'}})
            
        elif command_type == 'voice_stop':
            # Stop voice recognition
            voice_input.stop_listening()
            emit('response', {'type': 'voice_status', 'data': {'status': 'stopped'}})
            
        elif command_type == 'text_command':
            # Process text command with voice response
            text = command_data.get('text', '')
            response = handle_text_command_with_voice(text)
            emit('response', {'type': 'command_result', 'data': response})
            
        elif command_type == 'system_status':
            # Get system status
            status = get_system_status()
            emit('response', {'type': 'system_status', 'data': status})
            
        elif command_type == 'trinetra_command':
            # Handle TRINETRA commands
            response = handle_trinetra_command(command_data)
            emit('response', {'type': 'trinetra_response', 'data': response})
            
        elif command_type == 'krait3_command':
            # Handle KRAIT-3 commands
            response = handle_krait3_command(command_data)
            emit('response', {'type': 'krait3_response', 'data': response})
            
        else:
            emit('response', {'type': 'error', 'data': {'message': f'Unknown command type: {command_type}'}})
            
    except Exception as e:
        logging.error(f"Error handling command: {e}")
        emit('response', {'type': 'error', 'data': {'message': str(e)}})

def get_system_status():
    """Get current system status"""
    try:
        import psutil
        import platform
        
        # Get disk usage for the current drive (Windows)
        if platform.system() == 'Windows':
            disk_usage = psutil.disk_usage('C:\\')
        else:
            disk_usage = psutil.disk_usage('/')
            
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': (disk_usage.used / disk_usage.total) * 100,
            'temperature': get_cpu_temperature(),
            'network_connected': check_internet_connection(),
            'timestamp': str(datetime.now())
        }
    except ImportError:
        return {
            'cpu_percent': 0,
            'memory_percent': 0,
            'disk_percent': 0,
            'temperature': 0,
            'network_connected': False,
            'timestamp': str(datetime.now()),
            'note': 'psutil not installed'
        }

def get_cpu_temperature():
    """Get CPU temperature (cross-platform)"""
    try:
        import psutil
        import platform
        
        # Try to get temperature sensors (Linux/Raspberry Pi)
        if hasattr(psutil, 'sensors_temperatures'):
            temps = psutil.sensors_temperatures()
            if temps:
                # Get the first available temperature
                for name, entries in temps.items():
                    if entries:
                        return entries[0].current
        
        # Windows specific temperature monitoring
        if platform.system() == 'Windows':
            try:
                import wmi
                w = wmi.WMI(namespace="root\\wmi")
                temperature_info = w.MSAcpi_ThermalZoneTemperature()[0]
                temp_celsius = (temperature_info.CurrentTemperature / 10.0) - 273.15
                return temp_celsius
            except:
                # Alternative Windows method using Open Hardware Monitor
                try:
                    import subprocess
                    result = subprocess.run(['wmic', 'path', 'Win32_PerfRawData_Counters_ThermalZoneInformation', 'get', 'Temperature'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and result.stdout:
                        lines = result.stdout.strip().split('\n')
                        for line in lines[1:]:  # Skip header
                            if line.strip() and line.strip() != "Temperature":
                                temp_value = int(line.strip())
                                if temp_value > 0:
                                    return (temp_value / 10.0) - 273.15
                except:
                    pass
        
        # Fallback for Raspberry Pi
        if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read()) / 1000.0
                return temp
                
        # Mock temperature for demonstration (40-60°C range)
        import random
        return round(40 + random.random() * 20, 1)
        
    except Exception as e:
        logging.debug(f"Temperature reading failed: {e}")
        # Return mock temperature for demo
        import random
        return round(40 + random.random() * 20, 1)

def check_internet_connection():
    """Check if internet connection is available"""
    try:
        import urllib.request
        urllib.request.urlopen('http://www.google.com', timeout=5)
        return True
    except Exception:
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except Exception:
            return False

def handle_voice_command(text):
    """Handle voice commands received from speech recognition"""
    global lyra_engine, tts_output
    
    if text and lyra_engine and tts_output:
        logging.info(f"Processing voice command: {text}")
        
        # Handle special wake word greeting
        if text == "wake_word_greeting":
            response = {
                'status': 'success',
                'action': 'wake_greeting',
                'message': 'Yes Commander, I am listening. How can I assist you?',
                'timestamp': str(datetime.now())
            }
            logging.info(f"Wake word greeting response: {response['message']}")
            tts_output.speak(response['message'])
        else:
            # Process command through LYRA decision engine
            response = lyra_engine.process_command(text)
            
            # Speak the response
            if 'message' in response:
                logging.info(f"Speaking response: {response['message']}")
                tts_output.speak(response['message'])
            else:
                logging.warning(f"No message in response: {response}")
        
        # Send response to GUI if connected
        try:
            socketio.emit('response', {
                'type': 'voice_command_result', 
                'data': {
                    'command': text,
                    'response': response
                }
            })
        except Exception as e:
            logging.debug(f"Could not send to GUI: {e}")

def handle_text_command_with_voice(text):
    """Handle text commands and respond with voice"""
    global lyra_engine, tts_output
    
    if text and lyra_engine:
        logging.info(f"Processing text command: {text}")
        
        # Process command through LYRA decision engine
        response = lyra_engine.process_command(text)
        
        # Speak the response if TTS is available
        if tts_output and 'message' in response:
            tts_output.speak(response['message'])
        
        return response
    
    return {'status': 'error', 'message': 'Command processing failed'}

def handle_trinetra_command(command_data):
    """Handle TRINETRA ground bot commands"""
    action = command_data.get('action')
    
    # Placeholder for TRINETRA integration
    logging.info(f"TRINETRA command: {action}")
    
    return {
        'status': 'success',
        'action': action,
        'message': f'TRINETRA {action} command executed',
        'timestamp': str(datetime.now())
    }

def handle_krait3_command(command_data):
    """Handle KRAIT-3 UAV commands"""
    action = command_data.get('action')
    
    # Placeholder for KRAIT-3 integration
    logging.info(f"KRAIT-3 command: {action}")
    
    return {
        'status': 'success',
        'action': action,
        'message': f'KRAIT-3 {action} command executed',
        'timestamp': str(datetime.now())
    }

@app.route('/')
def index():
    """Serve the main GUI page"""
    try:
        with open('gui/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
        <head><title>LYRA 3.0 Backend Running</title></head>
        <body>
            <h1>LYRA 3.0 Backend is Running</h1>
            <p>WebSocket server active on port 5000</p>
            <p>GUI files not found. Please check gui/ directory.</p>
        </body>
        </html>
        """

@app.route('/style.css')
def serve_css():
    """Serve CSS file"""
    try:
        with open('gui/style.css', 'r', encoding='utf-8') as f:
            content = f.read()
        response = app.response_class(content, mimetype='text/css')
        return response
    except FileNotFoundError:
        return "/* CSS file not found */", 404

@app.route('/main.js')
def serve_js():
    """Serve JavaScript file"""
    try:
        with open('gui/main.js', 'r', encoding='utf-8') as f:
            content = f.read()
        response = app.response_class(content, mimetype='application/javascript')
        return response
    except FileNotFoundError:
        return "// JS file not found", 404

def run_flask_server():
    """Run the Flask-SocketIO server"""
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)

def main():
    """Main entry point"""
    print("=" * 60)
    print("🤖 LYRA 3.0 - Logical Yielding Response Algorithm")
    print("🚀 Starting AI Assistant System...")
    print("=" * 60)
    
    # Setup logging
    setup_logging()
    
    # Initialize LYRA components
    initialize_lyra_components()
    
    # Welcome message
    tts_output.speak("Welcome Commander. LYRA 3.0 system is now online.")
    
    # Start Flask server for GUI communication
    logging.info("Starting WebSocket server on port 5000...")
    run_flask_server()

if __name__ == "__main__":
    main()
