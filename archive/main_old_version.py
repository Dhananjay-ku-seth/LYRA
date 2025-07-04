#!/usr/bin/env python3
"""
LYRA (Logical Yielding Response Algorithm)
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
app.config['SECRET_KEY'] = 'lyra_secret_key_2024'
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
    
    logging.info("Initializing LYRA components...")
    
    # Initialize core components
    context_mgr = ContextManager()
    lyra_engine = DecisionEngine(context_mgr)
    voice_input = VoiceInput()
    tts_output = TTSOutput()
    
    logging.info("LYRA initialization complete")

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logging.info("Client connected to LYRA")
    emit('status', {'message': 'Connected to LYRA', 'timestamp': str(datetime.now())})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logging.info("Client disconnected from LYRA")

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
            # Process text command
            text = command_data.get('text', '')
            response = lyra_engine.process_command(text)
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
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'temperature': get_cpu_temperature(),
            'timestamp': str(datetime.now())
        }
    except ImportError:
        return {
            'cpu_percent': 0,
            'memory_percent': 0,
            'disk_percent': 0,
            'temperature': 0,
            'timestamp': str(datetime.now()),
            'note': 'psutil not installed'
        }

def get_cpu_temperature():
    """Get CPU temperature (Raspberry Pi specific)"""
    try:
        if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read()) / 1000.0
                return temp
    except:
        pass
    return 0

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
    """Serve the main page (for testing without Electron)"""
    return """
    <html>
    <head><title>LYRA Backend Running</title></head>
    <body>
        <h1>LYRA Backend is Running</h1>
        <p>WebSocket server active on port 5000</p>
        <p>Use Electron frontend to connect</p>
    </body>
    </html>
    """

def run_flask_server():
    """Run the Flask-SocketIO server"""
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)

def main():
    """Main entry point"""
    print("=" * 60)
    print("🤖 LYRA - Logical Yielding Response Algorithm")
    print("🚀 Starting AI Assistant System...")
    print("=" * 60)
    
    # Setup logging
    setup_logging()
    
    # Initialize LYRA components
    initialize_lyra_components()
    
    # Welcome message
    tts_output.speak("Welcome Commander. LYRA system is now online.")
    
    # Start Flask server for GUI communication
    logging.info("Starting WebSocket server on port 5000...")
    run_flask_server()

if __name__ == "__main__":
    main()
