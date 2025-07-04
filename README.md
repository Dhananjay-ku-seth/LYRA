# LYRA 3.0 - Logical Yielding Response Algorithm

🤖 **Advanced AI Assistant & Control Dashboard for Raspberry Pi 5**

LYRA 3.0 is a fully offline AI-based assistant designed to control and monitor two smart systems: TRINETRA (ground surveillance UGV) and KRAIT-3 (autonomous tiltrotor UAV). The system features a JARVIS-inspired animated interface with multilingual support and modular architecture.

## 🚀 Features

### 🏠 **Home Tab - JARVIS Core UI**
- Animated LYRA core with pulsing rings and responsive eye
- Live system indicators (RAM, CPU, temperature, status LEDs)
- Operation modes: Defense/Home/Night/Manual
- Voice controls with TTS feedback
- Real-time text command interface

### 🤖 **System Tab - Device Control Hub**
- **TRINETRA Ground Bot Control:**
  - Movement controls (Forward/Reverse/Rotate)
  - ESP32-CAM live stream display
  - Gimbal control and snapshot capture
  - Sensor readouts (Gas, Fire, IR, GPS)
  - Mission mode toggle (Patrol, Manual)

- **KRAIT-3 Tiltrotor UAV Control:**
  - Flight controls (Launch/Hover/Return/Abort)
  - Multiple flight modes (Manual, Auto, Waypoint Nav)
  - Pixhawk telemetry (Altitude, Battery, GPS, Heading)
  - Mission planner with offline maps
  - Payload actions (Drop, Capture, Scout)

### 📁 **Data & Config Upload Tab**
- Secure file upload with SHA256 validation
- Support for training data (text, CSV, logs, audio)
- Configuration file upload (.lyra-config.json/yaml)
- Real-time upload queue management

### 📊 **Logs & Diagnostics Tab**
- Real-time system log display
- Hardware diagnostics and health monitoring
- Export functionality for logs and reports
- Auto-diagnostics for all connected modules

### ⚙️ **Settings Tab**
- Multi-language support (English, Hindi, Custom)
- Voice settings (Type, Rate, Volume)
- Theme selection (Neon Dark, Tactical Grey, Light)
- Security settings (Face recognition, Master passphrase)

## 🛠️ Technology Stack

- **Backend:** Python (Flask-SocketIO)
- **Frontend:** HTML5, CSS3, JavaScript (WebSocket)
- **AI Engine:** Custom NLP with spaCy/NLTK
- **Communication:** MQTT, UART, MAVLink protocols
- **Security:** AES-256 encryption, SHA256 validation
- **Hardware:** Raspberry Pi 5 (8GB RAM) optimized

## 📦 Installation

### Prerequisites
- Raspberry Pi 5 with 8GB RAM
- Python 3.8+
- Node.js (for Electron - optional)

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd LYRA3.0
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize configuration:
```bash
mkdir -p config logs upload/train_data
```

4. Run the system:
```bash
python main.py
```

5. Open web interface:
   - Navigate to `http://localhost:5000`
   - Or open `gui/index.html` in a modern browser

## 🚀 Quick Start

1. **Start LYRA 3.0:**
   ```bash
   python main.py
   ```

2. **Test WebSocket Connection:**
   - Open browser console
   - Look for "WebSocket test successful" message

3. **Try Voice Commands:**
   - Click "Start Listening" in the Home tab
   - Say commands like "system status" or "hello LYRA"

4. **Control Devices:**
   - Switch to System tab
   - Use movement controls for TRINETRA
   - Test flight controls for KRAIT-3

## 🔧 Configuration

### Device Configuration
Edit `config/lyra-config.json`:
```json
{
  "trinetra": {
    "uart_port": "/dev/ttyUSB0",
    "baud_rate": 115200,
    "camera_stream": "http://192.168.1.100:8080/stream"
  },
  "krait3": {
    "mavlink_connection": "udp:127.0.0.1:14550",
    "mission_altitude": 50
  }
}
```

### Voice Settings
```json
{
  "voice": {
    "language": "en",
    "rate": 150,
    "volume": 0.9,
    "voice_type": "neutral"
  }
}
```

## 🌟 Advanced Features

### Multi-Modal Input
- Voice commands (STT with Vosk/Whisper)
- Text input with NLP processing
- Sensor-triggered automation

### Learning Capabilities
- Custom command pattern recognition
- User preference adaptation
- Voice/face recognition training

### Security Features
- Offline operation (no cloud dependency)
- Face authentication with OpenCV
- Encrypted log storage
- Signed update verification

## 🔌 Hardware Integration

### TRINETRA (Ground Bot)
- ESP32-CAM for video streaming
- Sensors: Gas, Fire, Motion, GPS
- UART communication protocol
- Gimbal-mounted camera system

### KRAIT-3 (UAV)
- Pixhawk flight controller
- MAVLink protocol communication
- Autonomous navigation capabilities
- Payload management system

## 📝 Development

### Project Structure
```
LYRA3.0/
├── main.py                 # Main entry point
├── core/                   # AI engine components
│   ├── decision_engine.py  # Command processing
│   ├── context_manager.py  # State management
│   ├── voice_input.py      # STT processing
│   └── tts_output.py       # TTS output
├── gui/                    # Frontend interface
│   ├── index.html          # Main dashboard
│   ├── style.css           # JARVIS styling
│   └── main.js             # WebSocket logic
├── config/                 # Configuration files
├── logs/                   # System logs
└── requirements.txt        # Python dependencies
```

### Adding Custom Commands
1. Edit `core/decision_engine.py`
2. Add new patterns to `command_patterns`
3. Implement handler function
4. Test with voice/text input

## 🔧 Troubleshooting

### Common Issues
1. **WebSocket Connection Failed:**
   - Check if port 5000 is available
   - Verify Flask-SocketIO installation

2. **Voice Recognition Not Working:**
   - Install voice dependencies: `pip install vosk pyttsx3`
   - Check microphone permissions

3. **Device Communication Issues:**
   - Verify UART/USB connections
   - Check device configuration in config files

### Debug Mode
```bash
python main.py --debug
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by JARVIS from Iron Man
- Built for advanced robotics and AI applications
- Designed for offline, secure operation

---

**LYRA 3.0** - *Bringing AI-powered control to the next level* 🚀
