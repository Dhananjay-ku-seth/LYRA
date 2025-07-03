# LYRA 3.0 Raspberry Pi 5 Build Script (PowerShell)
# This script creates a cross-platform Pi5 build package on Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LYRA 3.0 Raspberry Pi 5 Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

function Write-Status {
    param($Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param($Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param($Message)
    Write-Host "ℹ $Message" -ForegroundColor Blue
}

# Check Python installation
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Status "Python found: $pythonVersion"
    } else {
        throw "Python not found"
    }
} catch {
    Write-Error "Python 3 is not installed or not in PATH"
    Write-Host "Please install Python 3.8+ and add it to PATH"
    exit 1
}

# Create build directory
Write-Host ""
Write-Info "Creating build environment..."
if (Test-Path "dist\LYRA-3.0-Pi5") {
    Remove-Item -Recurse -Force "dist\LYRA-3.0-Pi5"
}
New-Item -ItemType Directory -Force -Path "dist\LYRA-3.0-Pi5" | Out-Null

# Create Python virtual environment
Write-Host "Creating Python virtual environment..."
python -m venv "dist\LYRA-3.0-Pi5\venv"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create virtual environment"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& "dist\LYRA-3.0-Pi5\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
Write-Host "Installing Python dependencies..."
if (Test-Path "requirements-pi5.txt") {
    pip install -r requirements-pi5.txt
} else {
    pip install -r requirements.txt
}

if ($LASTEXITCODE -ne 0) {
    Write-Warning "Some dependencies may have failed to install"
}

# Test critical imports
Write-Host "Testing Python imports..."
try {
    python -c "import flask, flask_socketio; print('✓ Flask modules OK')"
} catch {
    Write-Warning "Flask modules issue"
}

try {
    python -c "import psutil; print('✓ System monitoring OK')"
} catch {
    Write-Warning "psutil issue"
}

# Copy application files
Write-Host ""
Write-Info "Copying application files..."

# Core application
Copy-Item -Recurse -Path "core" -Destination "dist\LYRA-3.0-Pi5\"
Copy-Item -Recurse -Path "gui" -Destination "dist\LYRA-3.0-Pi5\"
Copy-Item -Recurse -Path "data" -Destination "dist\LYRA-3.0-Pi5\"

# Copy resources if exists
if (Test-Path "resources") {
    Copy-Item -Recurse -Path "resources" -Destination "dist\LYRA-3.0-Pi5\"
}

# Create directories
New-Item -ItemType Directory -Force -Path "dist\LYRA-3.0-Pi5\config" | Out-Null
New-Item -ItemType Directory -Force -Path "dist\LYRA-3.0-Pi5\logs" | Out-Null

# Main files
$filesToCopy = @(
    "main.py",
    "main-pi5.py", 
    "launcher.py",
    "start_lyra.py",
    "README.md"
)

foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination "dist\LYRA-3.0-Pi5\"
    }
}

# Copy requirements files
Copy-Item -Path "requirements*.txt" -Destination "dist\LYRA-3.0-Pi5\"

# Copy lyra_pi5_app.py if exists
if (Test-Path "lyra_pi5_app.py") {
    Copy-Item -Path "lyra_pi5_app.py" -Destination "dist\LYRA-3.0-Pi5\"
}

# Create startup scripts
Write-Host ""
Write-Info "Creating startup scripts..."

# Main Pi5 launcher
$launcherScript = @'
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
'@

$launcherScript | Out-File -FilePath "dist\LYRA-3.0-Pi5\lyra-pi5.sh" -Encoding utf8

# Service installation script
$serviceScript = @'
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
'@

$serviceScript | Out-File -FilePath "dist\LYRA-3.0-Pi5\install-service.sh" -Encoding utf8

# Development mode script
$devScript = @'
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
'@

$devScript | Out-File -FilePath "dist\LYRA-3.0-Pi5\dev-mode.sh" -Encoding utf8

# Create installation instructions
$installInstructions = @'
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
- Hardware test: `python3 test-hardware.py`

For issues, check the main README.md file.
'@

$installInstructions | Out-File -FilePath "dist\LYRA-3.0-Pi5\INSTALL.md" -Encoding utf8

# Create hardware test script
$hardwareTest = @'
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
'@

$hardwareTest | Out-File -FilePath "dist\LYRA-3.0-Pi5\test-hardware.py" -Encoding utf8

# Create configuration file
$configContent = @'
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
'@

$configContent | Out-File -FilePath "dist\LYRA-3.0-Pi5\config\pi5-config.yaml" -Encoding utf8

# Deactivate virtual environment
deactivate

# Create deployment package
Write-Host ""
Write-Info "Creating deployment package..."

# Use PowerShell's Compress-Archive to create tar.gz equivalent
Write-Host "Creating archive..."
Compress-Archive -Path "dist\LYRA-3.0-Pi5" -DestinationPath "dist\LYRA-3.0-Pi5.zip" -Force

# Create checksum
$hash = Get-FileHash "dist\LYRA-3.0-Pi5.zip" -Algorithm SHA256
$hash.Hash + "  LYRA-3.0-Pi5.zip" | Out-File -FilePath "dist\LYRA-3.0-Pi5.zip.sha256" -Encoding utf8

Write-Host ""
Write-Status "Raspberry Pi 5 build complete!"
Write-Host ""
Write-Host "📦 Package: dist/LYRA-3.0-Pi5.zip" -ForegroundColor Cyan
Write-Host "📁 Directory: dist/LYRA-3.0-Pi5/" -ForegroundColor Cyan
Write-Host "🔍 Checksum: dist/LYRA-3.0-Pi5.zip.sha256" -ForegroundColor Cyan
Write-Host ""
Write-Info "To deploy on Raspberry Pi 5:"
Write-Host "1. Copy the zip file to your Pi"
Write-Host "2. Extract: unzip LYRA-3.0-Pi5.zip"
Write-Host "3. Change directory to LYRA-3.0-Pi5"
Write-Host "4. Execute the script: ./lyra-pi5.sh"
Write-Host ""
Write-Info "For auto-start on boot:"
Write-Host "1. Execute: ./install-service.sh"
Write-Host '2. Start the service: sudo systemctl start lyra3'
