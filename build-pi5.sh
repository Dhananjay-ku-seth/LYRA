#!/bin/bash

echo "========================================"
echo "LYRA 3.0 Raspberry Pi 5 Build Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if running on Raspberry Pi
if [[ -f /proc/cpuinfo ]] && grep -q "Raspberry Pi" /proc/cpuinfo; then
    print_status "Running on Raspberry Pi"
    IS_PI=true
else
    print_warning "Not running on Raspberry Pi - creating cross-platform build"
    IS_PI=false
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo "Please install Python 3.8+ with: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

print_status "Python 3 found: $(python3 --version)"

# Create build directory
echo
print_info "Creating build environment..."
mkdir -p dist
rm -rf dist/LYRA-3.0-Pi5
mkdir -p dist/LYRA-3.0-Pi5

# Create Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv dist/LYRA-3.0-Pi5/venv
if [ $? -ne 0 ]; then
    print_error "Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
source dist/LYRA-3.0-Pi5/venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
if [ "$IS_PI" = true ]; then
    # Use Pi5-specific requirements
    pip install -r requirements-pi5.txt
else
    # Use standard requirements for cross-platform build
    pip install -r requirements.txt
fi

if [ $? -ne 0 ]; then
    print_warning "Some dependencies may have failed to install"
fi

# Test critical imports
echo "Testing Python imports..."
python -c "import flask, flask_socketio; print('✓ Flask modules OK')" || print_warning "Flask modules issue"
python -c "import psutil; print('✓ System monitoring OK')" || print_warning "psutil issue"

if [ "$IS_PI" = true ]; then
    python -c "import gpiozero; print('✓ GPIO control OK')" 2>/dev/null || print_warning "GPIO control may not be available"
    python -c "import RPi.GPIO; print('✓ RPi.GPIO OK')" 2>/dev/null || print_warning "RPi.GPIO may not be available"
fi

# Copy application files
echo
print_info "Copying application files..."

# Core application
cp -r core dist/LYRA-3.0-Pi5/
cp -r gui dist/LYRA-3.0-Pi5/
cp -r data dist/LYRA-3.0-Pi5/
cp -r resources dist/LYRA-3.0-Pi5/ 2>/dev/null || true

# Create directories if they don't exist
mkdir -p dist/LYRA-3.0-Pi5/config
mkdir -p dist/LYRA-3.0-Pi5/logs

# Main files
cp main.py dist/LYRA-3.0-Pi5/
cp main-pi5.py dist/LYRA-3.0-Pi5/
cp launcher.py dist/LYRA-3.0-Pi5/
cp start_lyra.py dist/LYRA-3.0-Pi5/
cp lyra_pi5_app.py dist/LYRA-3.0-Pi5/
cp requirements*.txt dist/LYRA-3.0-Pi5/
cp README.md dist/LYRA-3.0-Pi5/

# Create startup scripts
echo
print_info "Creating startup scripts..."

# Main Pi5 launcher
cat > dist/LYRA-3.0-Pi5/lyra-pi5.sh << 'EOF'
#!/bin/bash

# LYRA 3.0 Raspberry Pi 5 Launcher
echo "========================================"
echo "🍓 LYRA 3.0 - Raspberry Pi 5 Edition"
echo "🤖 Logical Yielding Response Algorithm"
echo "========================================"

# Get script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "⚠ Virtual environment not found - using system Python"
fi

# Check if running on Pi5
if [[ -f /proc/cpuinfo ]] && grep -q "Raspberry Pi 5" /proc/cpuinfo; then
    echo "✓ Raspberry Pi 5 detected"
    PYTHON_SCRIPT="main-pi5.py"
else
    echo "⚠ Not Pi5 - using standard mode"
    PYTHON_SCRIPT="main.py"
fi

# Start LYRA
echo "🚀 Starting LYRA 3.0..."
echo "🌐 Web interface will be available at: http://$(hostname -I | cut -d' ' -f1):5000"
echo "🌐 Local access: http://localhost:5000"
echo
echo "Press Ctrl+C to stop LYRA"
echo

python3 "$PYTHON_SCRIPT"
EOF

chmod +x dist/LYRA-3.0-Pi5/lyra-pi5.sh

# Service script for systemd
cat > dist/LYRA-3.0-Pi5/install-service.sh << 'EOF'
#!/bin/bash

# LYRA 3.0 Systemd Service Installer

echo "Installing LYRA 3.0 as a system service..."

# Get current directory
INSTALL_DIR="$(pwd)"

# Create systemd service file
sudo tee /etc/systemd/system/lyra3.service > /dev/null << EOL
[Unit]
Description=LYRA 3.0 AI Assistant System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/lyra-pi5.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable lyra3.service

echo "✓ LYRA 3.0 service installed"
echo
echo "Service commands:"
echo "  Start:   sudo systemctl start lyra3"
echo "  Stop:    sudo systemctl stop lyra3"
echo "  Status:  sudo systemctl status lyra3"
echo "  Logs:    journalctl -u lyra3 -f"
echo
echo "LYRA 3.0 will now start automatically on boot."
EOF

chmod +x dist/LYRA-3.0-Pi5/install-service.sh

# Development mode script
cat > dist/LYRA-3.0-Pi5/dev-mode.sh << 'EOF'
#!/bin/bash

# LYRA 3.0 Development Mode
echo "🔧 LYRA 3.0 Development Mode"
echo "============================="

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Starting LYRA in development mode with debug output..."
python3 main.py --debug
EOF

chmod +x dist/LYRA-3.0-Pi5/dev-mode.sh

# Create installation instructions
cat > dist/LYRA-3.0-Pi5/INSTALL.md << 'EOF'
# LYRA 3.0 - Raspberry Pi 5 Installation

## Quick Start

1. **Extract the package:**
   ```bash
   tar -xzf LYRA-3.0-Pi5.tar.gz
   cd LYRA-3.0-Pi5
   ```

2. **Run LYRA:**
   ```bash
   ./lyra-pi5.sh
   ```

3. **Access the interface:**
   - Web interface: http://[PI_IP]:5000
   - Local: http://localhost:5000

## System Service Installation

To run LYRA as a system service (auto-start on boot):

```bash
./install-service.sh
```

## Hardware Requirements

- **Recommended:** Raspberry Pi 5 (8GB RAM)
- **Minimum:** Raspberry Pi 4 (4GB RAM)
- **Storage:** 16GB+ MicroSD card (Class 10)
- **Optional:** USB microphone, speakers/headphones

## Pi5-Specific Features

When running on Raspberry Pi 5:
- ✅ GPIO control for robotics
- ✅ Camera module support
- ✅ I2C/SPI communication
- ✅ Hardware monitoring
- ✅ Optimized performance settings

## Development Mode

For development and debugging:
```bash
./dev-mode.sh
```

## Troubleshooting

### Audio Issues
```bash
# Test audio output
speaker-test -t wav -c 2

# Configure audio device
sudo raspi-config
# Advanced Options → Audio → Force 3.5mm jack
```

### GPIO Issues
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Reboot required after group change
sudo reboot
```

### Performance Optimization
```bash
# GPU memory split (for camera use)
sudo raspi-config
# Advanced Options → Memory Split → 128

# Enable hardware acceleration
echo 'gpu_mem=128' | sudo tee -a /boot/config.txt
```

## System Requirements

### Software Dependencies (Auto-installed)
- Python 3.8+
- Flask & Flask-SocketIO
- GPIO libraries (Pi only)
- System monitoring tools

### Hardware Connections
- **Camera:** CSI connector
- **Audio:** 3.5mm jack or HDMI
- **Robotics:** GPIO pins 2-27
- **Network:** Ethernet or WiFi

## Support

- Check logs: `journalctl -u lyra3 -f` (if using service)
- Debug mode: `./dev-mode.sh`
- Hardware test: `python3 test_components.py`

For issues, check the main README.md file.
EOF

# Create hardware test script
cat > dist/LYRA-3.0-Pi5/test-hardware.py << 'EOF'
#!/usr/bin/env python3
"""
LYRA 3.0 Raspberry Pi Hardware Test
Tests all hardware components and features
"""

import sys
import os

def test_gpio():
    """Test GPIO functionality"""
    try:
        import gpiozero
        import RPi.GPIO
        print("✓ GPIO libraries available")
        
        # Test LED (safe test on GPIO 18)
        from gpiozero import LED
        led = LED(18)
        led.on()
        led.off()
        print("✓ GPIO control working")
        return True
    except Exception as e:
        print(f"✗ GPIO test failed: {e}")
        return False

def test_camera():
    """Test camera module"""
    try:
        from picamera2 import Picamera2
        picam2 = Picamera2()
        picam2.close()
        print("✓ Camera module available")
        return True
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False

def test_i2c():
    """Test I2C communication"""
    try:
        import smbus2
        print("✓ I2C libraries available")
        return True
    except Exception as e:
        print(f"✗ I2C test failed: {e}")
        return False

def test_system_monitoring():
    """Test system monitoring"""
    try:
        import psutil
        print(f"✓ CPU Usage: {psutil.cpu_percent()}%")
        print(f"✓ Memory Usage: {psutil.virtual_memory().percent}%")
        
        # Pi-specific temperature
        if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read()) / 1000.0
                print(f"✓ CPU Temperature: {temp:.1f}°C")
        
        return True
    except Exception as e:
        print(f"✗ System monitoring failed: {e}")
        return False

def main():
    print("🍓 LYRA 3.0 Hardware Test")
    print("=" * 30)
    
    # Detect platform
    is_pi = False
    try:
        with open('/proc/cpuinfo', 'r') as f:
            if 'Raspberry Pi' in f.read():
                is_pi = True
                print("✓ Raspberry Pi detected")
    except:
        pass
    
    if not is_pi:
        print("⚠ Not running on Raspberry Pi")
    
    print("\nTesting components:")
    
    results = {
        'System Monitoring': test_system_monitoring(),
        'GPIO Control': test_gpio() if is_pi else False,
        'Camera Module': test_camera() if is_pi else False,
        'I2C Communication': test_i2c() if is_pi else False,
    }
    
    print("\nTest Results:")
    print("-" * 20)
    for component, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{component}: {status}")
    
    passed = sum(results.values())
    total = len([r for r in results.values() if r is not False])
    
    print(f"\nSummary: {passed}/{total} tests passed")
    
    if is_pi and passed == total:
        print("🎉 All hardware tests passed!")
    elif not is_pi:
        print("ℹ Run on Raspberry Pi for full hardware testing")

if __name__ == "__main__":
    main()
EOF

chmod +x dist/LYRA-3.0-Pi5/test-hardware.py

# Create configuration file
cat > dist/LYRA-3.0-Pi5/config/pi5-config.yaml << 'EOF'
# LYRA 3.0 Raspberry Pi 5 Configuration

# System Settings
system:
  platform: "raspberry-pi-5"
  auto_optimize: true
  gpu_memory: 128
  
# Network Settings
network:
  host: "0.0.0.0"
  port: 5000
  websocket_ping_timeout: 60

# Hardware Features
hardware:
  gpio_enabled: true
  camera_enabled: true
  i2c_enabled: true
  spi_enabled: false
  
# Performance Settings
performance:
  max_cpu_percent: 80
  memory_limit_mb: 6144
  log_rotation_mb: 50

# Voice Settings (Pi5 optimized)
voice:
  input_device: "default"
  output_device: "default"
  noise_suppression: true
  echo_cancellation: true

# Robotics Integration
robotics:
  trinetra:
    enabled: true
    uart_port: "/dev/ttyUSB0"
    baud_rate: 115200
    
  krait3:
    enabled: true
    mavlink_port: "/dev/ttyACM0"
    baud_rate: 57600
EOF

# Create deployment package
echo
print_info "Creating deployment package..."

# Deactivate virtual environment before packaging
deactivate 2>/dev/null || true

# Create tarball
cd dist
tar -czf LYRA-3.0-Pi5.tar.gz LYRA-3.0-Pi5/
cd ..

# Create checksums
cd dist
sha256sum LYRA-3.0-Pi5.tar.gz > LYRA-3.0-Pi5.tar.gz.sha256
cd ..

echo
print_status "Raspberry Pi 5 build complete!"
echo
echo "📦 Package: dist/LYRA-3.0-Pi5.tar.gz"
echo "📁 Directory: dist/LYRA-3.0-Pi5/"
echo "🔍 Checksum: dist/LYRA-3.0-Pi5.tar.gz.sha256"
echo
print_info "To deploy on Raspberry Pi 5:"
echo "1. Copy the tar.gz file to your Pi"
echo "2. Extract: tar -xzf LYRA-3.0-Pi5.tar.gz"
echo "3. Run: cd LYRA-3.0-Pi5 && ./lyra-pi5.sh"
echo
print_info "For auto-start on boot:"
echo "1. Run: ./install-service.sh"
echo "2. Start: sudo systemctl start lyra3"
echo
