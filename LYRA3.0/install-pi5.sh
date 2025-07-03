#!/bin/bash
# LYRA 3.0 Raspberry Pi 5 Installation Script
# Comprehensive setup for production deployment

set -e  # Exit on any error

echo "============================================================"
echo "🍓 LYRA 3.0 - Raspberry Pi 5 Installation"
echo "🤖 Logical Yielding Response Algorithm"
echo "============================================================"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "❌ This script is designed for Raspberry Pi systems"
    exit 1
fi

# Get Pi model
PI_MODEL=$(grep "Model" /proc/cpuinfo | cut -d: -f2 | xargs)
echo "📱 Detected: $PI_MODEL"

# Update system
echo "🔄 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    cmake \
    build-essential \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    libtiff5-dev \
    libopenjp2-7-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python3-tk \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    pkg-config \
    libgpiod-dev \
    i2c-tools \
    libcamera-apps \
    espeak-ng \
    python3-pyqt5 \
    python3-pyqt5.qtwebengine \
    pyqt5-dev-tools \
    qttools5-dev-tools

# Enable I2C and Camera
echo "🔧 Enabling I2C and Camera interfaces..."
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_camera 0

# Create LYRA user and directory
echo "👤 Setting up LYRA user environment..."
LYRA_USER=${SUDO_USER:-$USER}
LYRA_HOME="/home/$LYRA_USER/LYRA3.0"

# Create LYRA directory
sudo -u $LYRA_USER mkdir -p $LYRA_HOME
cd $LYRA_HOME

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
sudo -u $LYRA_USER python3 -m venv lyra_env
sudo -u $LYRA_USER $LYRA_HOME/lyra_env/bin/pip install --upgrade pip

# Copy LYRA files (assuming they're in current directory)
echo "📁 Installing LYRA 3.0 files..."
sudo -u $LYRA_USER cp -r /tmp/lyra_transfer/* $LYRA_HOME/ 2>/dev/null || {
    echo "⚠️ Please copy LYRA 3.0 files to $LYRA_HOME manually"
}

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f "$LYRA_HOME/requirements-pi5.txt" ]; then
    sudo -u $LYRA_USER $LYRA_HOME/lyra_env/bin/pip install -r $LYRA_HOME/requirements-pi5.txt
else
    echo "⚠️ requirements-pi5.txt not found, installing basic dependencies..."
    sudo -u $LYRA_USER $LYRA_HOME/lyra_env/bin/pip install \
        Flask==2.3.3 \
        Flask-SocketIO==5.3.6 \
        psutil==5.9.5 \
        gpiozero \
        RPi.GPIO \
        picamera2 \
        numpy \
        pandas \
        pyyaml \
        cryptography
fi

# Set up directories
echo "📂 Creating directories..."
sudo -u $LYRA_USER mkdir -p $LYRA_HOME/{config,logs,upload,captures}

# Create configuration file
echo "⚙️ Creating configuration..."
sudo -u $LYRA_USER cat > $LYRA_HOME/config/pi5-config.json << 'EOL'
{
    "pi5_settings": {
        "gpio_enabled": true,
        "camera_enabled": true,
        "i2c_enabled": true,
        "performance_mode": true,
        "auto_optimize": true
    },
    "trinetra": {
        "motor_pins": {
            "left_forward": 18,
            "left_backward": 19,
            "right_forward": 20,
            "right_backward": 21
        },
        "sensor_pins": {
            "ultrasonic_trigger": 23,
            "ultrasonic_echo": 24
        }
    },
    "krait3": {
        "serial_port": "/dev/ttyUSB0",
        "baud_rate": 57600,
        "mavlink_enabled": true
    },
    "system": {
        "log_level": "INFO",
        "max_log_size": "10MB",
        "temp_threshold": 80,
        "auto_shutdown_temp": 85
    }
}
EOL

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/lyra3.service > /dev/null << EOL
[Unit]
Description=LYRA 3.0 AI Assistant - Raspberry Pi 5 Edition
Documentation=https://github.com/lyra-ai/lyra3.0
After=network.target multi-user.target
Wants=network.target

[Service]
Type=simple
User=$LYRA_USER
Group=$LYRA_USER
WorkingDirectory=$LYRA_HOME
Environment=PATH=$LYRA_HOME/lyra_env/bin
ExecStart=$LYRA_HOME/lyra_env/bin/python3 $LYRA_HOME/main-pi5.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lyra3

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=$LYRA_HOME

[Install]
WantedBy=multi-user.target
EOL

# Create boot configuration optimizations
echo "⚡ Optimizing boot configuration..."
sudo tee -a /boot/config.txt > /dev/null << 'EOL'

# LYRA 3.0 Optimizations
# GPU memory split for better graphics performance
gpu_mem=128

# Enable I2C
dtparam=i2c_arm=on

# Enable SPI
dtparam=spi=on

# Camera settings
camera_auto_detect=1
dtoverlay=camera

# Performance settings
arm_freq=2400
over_voltage=6
temp_limit=80

# Audio settings
dtparam=audio=on
EOL

# Set up log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/lyra3 > /dev/null << EOL
$LYRA_HOME/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    su $LYRA_USER $LYRA_USER
}
EOL

# Create startup script
echo "🚀 Creating startup script..."
sudo -u $LYRA_USER tee $LYRA_HOME/start-lyra.sh > /dev/null << EOL
#!/bin/bash
# LYRA 3.0 Startup Script

echo "🍓 Starting LYRA 3.0 on Raspberry Pi 5..."

# Activate virtual environment
source $LYRA_HOME/lyra_env/bin/activate

# Check system status
echo "📊 System Status:"
echo "  CPU Temperature: \$(vcgencmd measure_temp | cut -d= -f2)"
echo "  Memory Usage: \$(free -h | awk '/^Mem:/ {print \$3"/"\$2}')"
echo "  Disk Usage: \$(df -h / | awk 'NR==2 {print \$5}')"

# Start LYRA
cd $LYRA_HOME
python3 main-pi5.py
EOL

chmod +x $LYRA_HOME/start-lyra.sh

# Create shutdown script
echo "🛑 Creating shutdown script..."
sudo -u $LYRA_USER tee $LYRA_HOME/stop-lyra.sh > /dev/null << EOL
#!/bin/bash
# LYRA 3.0 Shutdown Script

echo "🛑 Stopping LYRA 3.0..."
sudo systemctl stop lyra3.service
echo "✅ LYRA 3.0 stopped"
EOL

chmod +x $LYRA_HOME/stop-lyra.sh

# Set proper permissions
echo "🔒 Setting permissions..."
sudo chown -R $LYRA_USER:$LYRA_USER $LYRA_HOME
sudo chmod -R 755 $LYRA_HOME

# Enable and start service
echo "🔧 Enabling LYRA service..."
sudo systemctl daemon-reload
sudo systemctl enable lyra3.service

# Create desktop shortcut
echo "🖥️ Creating desktop shortcuts..."
sudo -u $LYRA_USER mkdir -p /home/$LYRA_USER/Desktop
sudo -u $LYRA_USER tee /home/$LYRA_USER/Desktop/LYRA3.desktop > /dev/null << EOL
[Desktop Entry]
Version=1.0
Type=Application
Name=LYRA 3.0
Comment=AI Assistant Dashboard
Exec=/usr/bin/chromium-browser --app=http://localhost:5000 --disable-web-security
Icon=/usr/share/pixmaps/chromium-browser.png
Path=$LYRA_HOME
Terminal=false
StartupNotify=true
Categories=System;
EOL

chmod +x /home/$LYRA_USER/Desktop/LYRA3.desktop

# Installation complete
echo "============================================================"
echo "✅ LYRA 3.0 Installation Complete!"
echo "============================================================"
echo ""
echo "📋 Installation Summary:"
echo "  📍 Location: $LYRA_HOME"
echo "  👤 User: $LYRA_USER"
echo "  🔧 Service: lyra3.service"
echo "  🌐 URL: http://localhost:5000"
echo ""
echo "🚀 Quick Commands:"
echo "  Start:    sudo systemctl start lyra3.service"
echo "  Stop:     sudo systemctl stop lyra3.service"
echo "  Status:   sudo systemctl status lyra3.service"
echo "  Logs:     journalctl -u lyra3.service -f"
echo ""
echo "⚠️ IMPORTANT: Reboot required for optimal performance"
echo "   Run: sudo reboot"
echo ""
echo "🎯 After reboot, access LYRA at: http://[PI_IP]:5000"
echo "============================================================"

# Ask for reboot
read -p "🔄 Reboot now for optimal performance? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Rebooting in 10 seconds..."
    sleep 10
    sudo reboot
else
    echo "ℹ️ Remember to reboot later for optimal performance"
    echo "🚀 You can start LYRA manually with: sudo systemctl start lyra3.service"
fi
