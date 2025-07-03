# LYRA 3.0 Deployment Guide 🚀

**Complete deployment instructions for LYRA 3.0 AI Assistant System**

## 🏃‍♂️ Quick Start

### Automated Installation (Recommended)

```bash
# Download and run the installer
python install-lyra.py
```

### Manual Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   npm install  # For GUI (optional)
   ```

2. **Start LYRA:**
   ```bash
   python start_lyra.py
   ```

3. **Access the interface:**
   - Web: http://localhost:5000
   - Voice: Say "Hi LYRA" to activate

## 📦 Build System

### Windows Build

```cmd
# Create portable Windows package
build-windows.bat

# Output: dist/LYRA-3.0-Windows-Portable.zip
```

### Raspberry Pi 5 Build

```bash
# Create Pi5 deployment package
./build-pi5.sh

# Output: dist/LYRA-3.0-Pi5.tar.gz
```

## 🖥️ Platform-Specific Deployment

### Windows 10/11

#### Prerequisites
- Python 3.8+ (download from python.org)
- Node.js 16+ (optional, for Electron GUI)

#### Installation Steps

1. **Automated Installation:**
   ```cmd
   python install-lyra.py
   ```

2. **Manual Installation:**
   ```cmd
   # Create virtual environment
   python -m venv venv
   venv\Scripts\activate.bat
   
   # Install dependencies
   pip install -r requirements.txt
   npm install
   
   # Start LYRA
   python start_lyra.py
   ```

3. **Portable Deployment:**
   ```cmd
   # Build portable package
   build-windows.bat
   
   # Extract and run
   cd dist\LYRA-3.0-Windows
   LYRA-3.0.bat
   ```

#### Voice Setup (Windows)
- Ensure microphone permissions are enabled
- Check Windows audio settings for default devices
- Install Microsoft Visual C++ Redistributable if needed

### Raspberry Pi 5 (8GB Recommended)

#### Prerequisites
```bash
# System update
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv git -y

# Optional: GPIO and camera support
sudo apt install python3-gpiozero python3-picamera2 -y
```

#### Installation Steps

1. **Quick Installation:**
   ```bash
   # Download and extract
   tar -xzf LYRA-3.0-Pi5.tar.gz
   cd LYRA-3.0-Pi5
   
   # Run LYRA
   ./lyra-pi5.sh
   ```

2. **System Service Installation:**
   ```bash
   # Install as system service
   ./install-service.sh
   
   # Start service
   sudo systemctl start lyra3
   
   # Check status
   sudo systemctl status lyra3
   ```

3. **Development Mode:**
   ```bash
   # Debug mode with verbose output
   ./dev-mode.sh
   ```

#### Pi5-Specific Features
- ✅ GPIO control for robotics
- ✅ Camera module support (CSI)
- ✅ I2C/SPI communication
- ✅ Hardware monitoring
- ✅ Optimized performance settings

### Linux (Ubuntu/Debian)

#### Prerequisites
```bash
# System dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm -y

# Audio support
sudo apt install alsa-utils pulseaudio espeak -y
```

#### Installation
```bash
# Clone or extract LYRA
git clone <repository> lyra3.0
cd lyra3.0

# Install and run
python3 install-lyra.py

# Start LYRA
./start-lyra.sh
```

## 🌐 Production Deployment

### Web Server Configuration

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name lyra.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Apache Configuration
```apache
<VirtualHost *:80>
    ServerName lyra.yourdomain.com
    ProxyPreserveHost On
    ProxyRequests Off
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    
    # WebSocket support
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteCond %{HTTP:Connection} upgrade [NC]
    RewriteRule .* ws://127.0.0.1:5000%{REQUEST_URI} [P]
</VirtualHost>
```

### Systemd Service (Linux)

```ini
# /etc/systemd/system/lyra3.service
[Unit]
Description=LYRA 3.0 AI Assistant System
After=network.target

[Service]
Type=simple
User=lyra
WorkingDirectory=/opt/lyra3.0
ExecStart=/opt/lyra3.0/venv/bin/python start_lyra.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable lyra3.service
sudo systemctl start lyra3.service
```

## 🐳 Docker Deployment

### Basic Docker Setup

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "start_lyra.py"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  lyra:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    environment:
      - LYRA_HOST=0.0.0.0
      - LYRA_PORT=5000
    restart: unless-stopped
```

Build and run:
```bash
docker-compose up -d
```

## ⚙️ Configuration

### Environment Variables

```bash
# Core settings
LYRA_HOST=127.0.0.1
LYRA_PORT=5000
LYRA_DEBUG=false

# Voice settings
LYRA_VOICE_ENABLED=true
LYRA_TTS_RATE=150
LYRA_TTS_VOLUME=0.9

# Hardware settings (Pi5)
LYRA_GPIO_ENABLED=true
LYRA_CAMERA_ENABLED=true
```

### Configuration Files

#### Main Configuration (`config/main-config.json`)
```json
{
  "system": {
    "platform": "windows",
    "version": "3.0.0"
  },
  "voice": {
    "enabled": true,
    "wake_words": ["hi lyra", "hey lyra"],
    "tts_rate": 150,
    "tts_volume": 0.9
  },
  "network": {
    "host": "127.0.0.1",
    "port": 5000,
    "debug": false
  }
}
```

#### Pi5 Configuration (`config/pi5-config.yaml`)
```yaml
system:
  platform: "raspberry-pi-5"
  auto_optimize: true
  gpu_memory: 128

hardware:
  gpio_enabled: true
  camera_enabled: true
  i2c_enabled: true

performance:
  max_cpu_percent: 80
  memory_limit_mb: 6144
```

## 🔧 Troubleshooting

### Common Issues

#### Voice Recognition Not Working
```bash
# Check audio devices
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

# Test microphone
python test_components.py

# Windows: Check microphone permissions
# Linux: Install audio packages
sudo apt install alsa-utils pulseaudio
```

#### TTS Not Speaking
```bash
# Test TTS
python debug_audio.py

# Windows: Check audio output devices
# Linux: Configure audio
sudo apt install espeak
```

#### Permission Denied (Linux)
```bash
# GPIO permissions (Pi)
sudo usermod -a -G gpio $USER

# Audio permissions
sudo usermod -a -G audio $USER

# Reboot after group changes
sudo reboot
```

#### Port Already in Use
```bash
# Find process using port 5000
sudo netstat -tulpn | grep :5000
# or
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>
```

### Hardware-Specific Issues

#### Raspberry Pi 5
```bash
# Enable I2C/SPI
sudo raspi-config
# Interface Options → I2C/SPI → Enable

# GPU memory for camera
echo 'gpu_mem=128' | sudo tee -a /boot/config.txt

# Audio configuration
sudo raspi-config
# Advanced Options → Audio → Force 3.5mm jack
```

#### Windows Audio Issues
```cmd
# Check Windows audio services
services.msc

# Restart audio service
net stop audiosrv
net start audiosrv

# Check audio devices in Control Panel
```

### Log Analysis

#### View Logs
```bash
# Application logs
tail -f logs/lyra_system.log

# System service logs (Linux)
journalctl -u lyra3 -f

# Docker logs
docker-compose logs -f lyra
```

#### Debug Mode
```bash
# Start in debug mode
python start_lyra.py --debug

# Or use debug script
python debug_audio.py
```

## 📊 Performance Optimization

### System Requirements

#### Minimum Requirements
- **CPU:** 2 cores, 1.5GHz
- **RAM:** 4GB
- **Storage:** 8GB free space
- **Network:** 100Mbps

#### Recommended Requirements
- **CPU:** 4 cores, 2.5GHz
- **RAM:** 8GB (16GB for Pi5)
- **Storage:** 32GB SSD
- **Network:** 1Gbps

### Performance Tuning

#### Python Optimization
```bash
# Use Python 3.11+ for better performance
python3.11 -m venv venv

# Install optimized packages
pip install --upgrade pip setuptools wheel
```

#### Pi5 Optimization
```bash
# CPU governor
echo 'performance' | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# GPU memory split
sudo raspi-config
# Advanced Options → Memory Split → 128
```

## 🔐 Security

### Production Security

#### Reverse Proxy
- Use Nginx/Apache with SSL
- Configure firewall rules
- Enable rate limiting

#### Authentication
```python
# Add to config
"security": {
  "enable_auth": true,
  "jwt_secret": "your-secret-key",
  "session_timeout": 3600
}
```

#### Network Security
```bash
# Firewall configuration
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 📚 Additional Resources

- [README.md](README.md) - Basic usage and features
- [API Documentation](docs/API.md) - REST and WebSocket APIs
- [Hardware Integration](docs/HARDWARE.md) - Robotics and IoT
- [Contributing](CONTRIBUTING.md) - Development guidelines

## 🆘 Support

For issues and support:

1. Check [Troubleshooting](#troubleshooting) section
2. Run diagnostic: `python test_components.py`
3. Check logs: `tail -f logs/lyra_system.log`
4. Create issue with system info and logs

---

**LYRA 3.0** - Logical Yielding Response Algorithm  
*Advanced AI Assistant for Robotics and Automation*
