#!/bin/bash
# LYRA 3.0 Raspberry Pi 5 Package Builder
# Creates a deployable package for Raspberry Pi 5

set -e

echo "============================================================"
echo "🍓 LYRA 3.0 - Raspberry Pi 5 Package Builder"
echo "============================================================"

# Create package directory
PACKAGE_DIR="LYRA3.0-Pi5-Package"
PACKAGE_DATE=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="LYRA3.0-Pi5-${PACKAGE_DATE}"

echo "📦 Creating package: $PACKAGE_NAME"

# Clean and create package directory
rm -rf $PACKAGE_DIR
mkdir -p $PACKAGE_DIR

# Copy core files
echo "📁 Copying core files..."
cp -r core/ $PACKAGE_DIR/
cp -r gui/ $PACKAGE_DIR/
cp -r config/ $PACKAGE_DIR/ 2>/dev/null || mkdir -p $PACKAGE_DIR/config

# Copy Pi5-specific files
echo "🍓 Copying Pi5-specific files..."
cp main-pi5.py $PACKAGE_DIR/
cp requirements-pi5.txt $PACKAGE_DIR/
cp install-pi5.sh $PACKAGE_DIR/
cp deploy-pi5.sh $PACKAGE_DIR/
cp pi5-analysis.md $PACKAGE_DIR/

# Copy documentation
echo "📋 Copying documentation..."
cp README.md $PACKAGE_DIR/
cp DEPLOYMENT.md $PACKAGE_DIR/ 2>/dev/null || echo "DEPLOYMENT.md not found"

# Create Pi5-specific README
echo "📝 Creating Pi5 README..."
cat > $PACKAGE_DIR/README-Pi5.md << 'EOL'
# 🍓 LYRA 3.0 - Raspberry Pi 5 Edition

## Quick Installation

1. **Transfer to Pi5:**
   ```bash
   scp -r LYRA3.0-Pi5-Package/ pi@[PI_IP]:/tmp/lyra_transfer/
   ```

2. **Install on Pi5:**
   ```bash
   ssh pi@[PI_IP]
   cd /tmp/lyra_transfer
   chmod +x install-pi5.sh
   sudo ./install-pi5.sh
   ```

3. **Access LYRA:**
   - URL: `http://[PI_IP]:5000`
   - Local: `http://localhost:5000`

## Pi5-Specific Features

- ✅ **GPIO Control** - Direct hardware control
- ✅ **Camera Integration** - Pi Camera module support
- ✅ **I2C/SPI** - Sensor communication
- ✅ **Hardware Monitoring** - Temperature, CPU, GPU
- ✅ **Auto-optimization** - Performance tuning
- ✅ **Systemd Service** - Auto-start on boot

## Hardware Requirements

- **Raspberry Pi 5** (8GB RAM recommended)
- **MicroSD Card** (32GB+ Class 10)
- **Power Supply** (5V 5A USB-C)
- **Camera Module** (optional)
- **GPIO Devices** (optional)

## Pin Configuration

### TRINETRA Motor Control
- Pin 18: Left Motor Forward
- Pin 19: Left Motor Backward  
- Pin 20: Right Motor Forward
- Pin 21: Right Motor Backward

### Sensors
- Pin 23: Ultrasonic Trigger
- Pin 24: Ultrasonic Echo

## Service Management

```bash
# Start LYRA
sudo systemctl start lyra3.service

# Stop LYRA  
sudo systemctl stop lyra3.service

# View logs
journalctl -u lyra3.service -f

# Check status
sudo systemctl status lyra3.service
```

## Troubleshooting

### Common Issues
1. **GPIO Permission**: Add user to gpio group
2. **Camera Not Found**: Enable camera interface
3. **I2C Issues**: Enable I2C interface
4. **Performance**: Check CPU temperature

### Debug Commands
```bash
# Check GPIO
gpio readall

# Test camera
libcamera-hello

# Check I2C devices
i2cdetect -y 1

# Monitor temperature
vcgencmd measure_temp
```

## Performance Optimization

The installer automatically optimizes:
- CPU governor to performance mode
- GPU memory split (128MB)
- I/O scheduler optimization
- Log rotation for SD card health

---

**🤖 LYRA 3.0 Pi5** - *AI-powered robotics control on Raspberry Pi* 🍓
EOL

# Create version file
echo "📋 Creating version file..."
cat > $PACKAGE_DIR/VERSION << EOL
LYRA 3.0 - Raspberry Pi 5 Edition
Build Date: $(date)
Platform: ARM64 (Raspberry Pi 5)
Architecture: aarch64
Python: 3.11+
Features: GPIO, Camera, I2C, Hardware Monitoring
EOL

# Create installation verification script
echo "🔍 Creating verification script..."
cat > $PACKAGE_DIR/verify-installation.sh << 'EOL'
#!/bin/bash
# LYRA 3.0 Pi5 Installation Verification

echo "🔍 LYRA 3.0 Pi5 Installation Verification"
echo "========================================"

# Check if LYRA directory exists
if [ -d "/home/pi/LYRA3.0" ]; then
    echo "✅ LYRA directory found"
else
    echo "❌ LYRA directory not found"
fi

# Check if virtual environment exists
if [ -d "/home/pi/LYRA3.0/lyra_env" ]; then
    echo "✅ Python virtual environment found"
else
    echo "❌ Python virtual environment not found"
fi

# Check if service is enabled
if systemctl is-enabled lyra3.service &>/dev/null; then
    echo "✅ LYRA service is enabled"
else
    echo "❌ LYRA service is not enabled"
fi

# Check if service is running
if systemctl is-active lyra3.service &>/dev/null; then
    echo "✅ LYRA service is running"
else
    echo "⚠️ LYRA service is not running"
fi

# Check GPIO support
if [ -c "/dev/gpiochip0" ]; then
    echo "✅ GPIO support available"
else
    echo "❌ GPIO support not available"
fi

# Check I2C support
if [ -c "/dev/i2c-1" ]; then
    echo "✅ I2C support available"
else
    echo "❌ I2C support not available"
fi

# Check camera support
if [ -e "/dev/video0" ] || [ -e "/base/soc/i2c0mux/i2c@1/imx708@1a" ]; then
    echo "✅ Camera support available"
else
    echo "⚠️ Camera support not detected"
fi

# Check if port 5000 is listening
if netstat -tuln 2>/dev/null | grep -q ":5000 "; then
    echo "✅ LYRA web server is listening on port 5000"
else
    echo "⚠️ LYRA web server is not listening on port 5000"
fi

echo ""
echo "🌐 Try accessing LYRA at: http://$(hostname -I | awk '{print $1}'):5000"
echo "📊 Check logs with: journalctl -u lyra3.service -f"
EOL

chmod +x $PACKAGE_DIR/verify-installation.sh

# Create quick setup script
echo "⚡ Creating quick setup script..."
cat > $PACKAGE_DIR/quick-setup.sh << 'EOL'
#!/bin/bash
# LYRA 3.0 Pi5 Quick Setup (No system packages)

echo "⚡ LYRA 3.0 Pi5 Quick Setup"
echo "=========================="

# Check if running on Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "❌ This must be run on a Raspberry Pi"
    exit 1
fi

# Create LYRA directory
mkdir -p ~/LYRA3.0
cd ~/LYRA3.0

# Copy files
cp -r ../LYRA3.0-Pi5-Package/* .

# Create virtual environment
python3 -m venv lyra_env
source lyra_env/bin/activate

# Install basic dependencies
pip install --upgrade pip
pip install Flask Flask-SocketIO psutil

# Create basic directories
mkdir -p config logs

echo "✅ Basic setup complete!"
echo "🚀 Run: ./start-lyra.sh"
EOL

chmod +x $PACKAGE_DIR/quick-setup.sh

# Create compressed package
echo "🗜️ Creating compressed package..."
tar -czf "${PACKAGE_NAME}.tar.gz" $PACKAGE_DIR/

# Create zip package for Windows users
if command -v zip &> /dev/null; then
    zip -r "${PACKAGE_NAME}.zip" $PACKAGE_DIR/
fi

# Generate checksums
echo "🔒 Generating checksums..."
if command -v sha256sum &> /dev/null; then
    sha256sum "${PACKAGE_NAME}.tar.gz" > "${PACKAGE_NAME}.tar.gz.sha256"
    [ -f "${PACKAGE_NAME}.zip" ] && sha256sum "${PACKAGE_NAME}.zip" > "${PACKAGE_NAME}.zip.sha256"
fi

# Package complete
echo "============================================================"
echo "✅ LYRA 3.0 Pi5 Package Created Successfully!"
echo "============================================================"
echo ""
echo "📦 Package Files:"
echo "  📁 Directory: $PACKAGE_DIR/"
echo "  🗜️ Archive: ${PACKAGE_NAME}.tar.gz"
[ -f "${PACKAGE_NAME}.zip" ] && echo "  📦 Zip: ${PACKAGE_NAME}.zip"
echo ""
echo "📋 Package Contents:"
echo "  🤖 Pi5-optimized backend (main-pi5.py)"
echo "  🍓 Hardware integration (pi5_hardware.py)"
echo "  🎨 JARVIS GUI interface"
echo "  📦 Pi5 requirements (requirements-pi5.txt)"
echo "  🔧 Auto-installer (install-pi5.sh)"
echo "  📋 Documentation and guides"
echo ""
echo "🚀 To deploy on Raspberry Pi 5:"
echo "  1. Transfer: scp ${PACKAGE_NAME}.tar.gz pi@[PI_IP]:/tmp/"
echo "  2. Extract: tar -xzf ${PACKAGE_NAME}.tar.gz"
echo "  3. Install: sudo ./install-pi5.sh"
echo ""
echo "🎯 Package size: $(du -sh ${PACKAGE_NAME}.tar.gz 2>/dev/null | cut -f1 || echo 'Unknown')"
echo "============================================================"
