# LYRA 3.0 - Raspberry Pi 5 Build Script
# This script creates a deployment package for Raspberry Pi 5

Write-Host "LYRA 3.0 - Raspberry Pi 5 Build Script" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Check if running on Windows
if ($env:OS -ne "Windows_NT") {
    Write-Error "This script must be run on Windows to create Pi5 deployment package"
    exit 1
}

# Create dist directory if it doesn't exist
$distDir = "dist"
if (!(Test-Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir
}

# Create Pi5 build directory
$buildDir = "$distDir\LYRA-3.0-Pi5"
if (Test-Path $buildDir) {
    Write-Host "Removing existing build directory..." -ForegroundColor Yellow
    Remove-Item -Path $buildDir -Recurse -Force
}
New-Item -ItemType Directory -Path $buildDir

Write-Host "Creating Raspberry Pi 5 deployment package..." -ForegroundColor Cyan

# Copy core application files
Write-Host "Copying core files..." -ForegroundColor Yellow
Copy-Item -Path "core" -Destination "$buildDir\core" -Recurse -Force
Copy-Item -Path "data" -Destination "$buildDir\data" -Recurse -Force
Copy-Item -Path "gui" -Destination "$buildDir\gui" -Recurse -Force
Copy-Item -Path "config" -Destination "$buildDir\config" -Recurse -Force

# Copy Python scripts
Write-Host "Copying Python scripts..." -ForegroundColor Yellow
Copy-Item -Path "main.py" -Destination "$buildDir\main.py"
Copy-Item -Path "main-pi5.py" -Destination "$buildDir\main-pi5.py"
Copy-Item -Path "start_lyra.py" -Destination "$buildDir\start_lyra.py"
Copy-Item -Path "test_tts.py" -Destination "$buildDir\test_tts.py"

# Copy configuration files
Write-Host "Copying configuration files..." -ForegroundColor Yellow
Copy-Item -Path "requirements.txt" -Destination "$buildDir\requirements.txt"
Copy-Item -Path "package.json" -Destination "$buildDir\package.json"
if (Test-Path "README.md") { Copy-Item -Path "README.md" -Destination "$buildDir\README.md" }
if (Test-Path "DEPLOYMENT-NEW.md") { Copy-Item -Path "DEPLOYMENT-NEW.md" -Destination "$buildDir\DEPLOYMENT.md" }

# Create Pi5-specific startup script
Write-Host "Creating Pi5 startup script..." -ForegroundColor Yellow
$startupScript = '#!/bin/bash
# LYRA 3.0 Startup Script for Raspberry Pi 5

echo "Starting LYRA 3.0 on Raspberry Pi 5..."

# Set working directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start LYRA
echo "Launching LYRA 3.0..."
python3 main-pi5.py'

$startupScript | Out-File -FilePath "$buildDir\start-lyra-pi5.sh" -Encoding UTF8

# Create installation script for Pi5
Write-Host "Creating Pi5 installation script..." -ForegroundColor Yellow
$installScript = '#!/bin/bash
# LYRA 3.0 Installation Script for Raspberry Pi 5

echo "LYRA 3.0 - Raspberry Pi 5 Installation"
echo "====================================="

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
echo "Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv portaudio19-dev libasound2-dev libpulse-dev espeak espeak-data libespeak1 libespeak-dev festival speech-dispatcher nodejs npm git curl wget

# Install Python audio libraries
echo "Installing Python audio dependencies..."
sudo apt install -y python3-pyaudio python3-pydub

# Set executable permissions
chmod +x start-lyra-pi5.sh

# Create desktop shortcut if running with GUI
if [ "$DISPLAY" != "" ]; then
    echo "Creating desktop shortcut..."
    cat > ~/Desktop/LYRA-3.0.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=LYRA 3.0
Comment=LYRA Voice Assistant
Exec=$(pwd)/start-lyra-pi5.sh
Icon=$(pwd)/gui/icon.png
Terminal=true
Categories=Utility;AudioVideo;
EOF
    chmod +x ~/Desktop/LYRA-3.0.desktop
fi

echo "Installation complete!"
echo "Run ./start-lyra-pi5.sh to start LYRA 3.0"'

$installScript | Out-File -FilePath "$buildDir\install-pi5.sh" -Encoding UTF8

# Create README for Pi5 deployment
Write-Host "Creating Pi5 README..." -ForegroundColor Yellow
$pi5Readme = '# LYRA 3.0 - Raspberry Pi 5 Deployment Package

This package contains LYRA 3.0 configured for Raspberry Pi 5 deployment.

## Quick Start

1. Copy this entire folder to your Raspberry Pi 5
2. Run the installation script:
   ```bash
   chmod +x install-pi5.sh
   ./install-pi5.sh
   ```
3. Start LYRA:
   ```bash
   ./start-lyra-pi5.sh
   ```

## Manual Installation

If you prefer to install manually:

1. Install system dependencies:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3 python3-pip python3-venv portaudio19-dev libasound2-dev libpulse-dev espeak espeak-data libespeak1 libespeak-dev festival speech-dispatcher nodejs npm
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Run LYRA:
   ```bash
   python3 main-pi5.py
   ```

## Configuration

- Audio settings can be configured in `config/audio.json`
- Voice settings are in `config/voice.json`
- System settings are in `config/system.json`

## Troubleshooting

- If audio does not work, check ALSA/PulseAudio configuration
- For permission issues, ensure user is in audio group: sudo usermod -a -G audio $USER
- Check microphone permissions and device access

## Support

For issues and documentation, see DEPLOYMENT.md'

$pi5Readme | Out-File -FilePath "$buildDir\README-PI5.md" -Encoding UTF8

# Copy build scripts for reference
Write-Host "Copying build scripts..." -ForegroundColor Yellow
if (Test-Path "build-pi5.sh") { Copy-Item -Path "build-pi5.sh" -Destination "$buildDir\build-pi5.sh" }

# Create deployment package
Write-Host "Creating deployment package..." -ForegroundColor Cyan
$zipPath = "$distDir\LYRA-3.0-Pi5-Portable.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

try {
    Compress-Archive -Path "$buildDir\*" -DestinationPath $zipPath -CompressionLevel Optimal
    Write-Host "Pi5 deployment package created successfully!" -ForegroundColor Green
    Write-Host "Package location: $zipPath" -ForegroundColor Green
} catch {
    Write-Error "Failed to create ZIP package: $($_.Exception.Message)"
    exit 1
}

# Display completion message
Write-Host "" -ForegroundColor White
Write-Host "LYRA 3.0 Pi5 Build Complete!" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green
Write-Host "Build directory: $buildDir" -ForegroundColor White
Write-Host "ZIP package: $zipPath" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "Next steps for Pi5 deployment:" -ForegroundColor Yellow
Write-Host "1. Copy the ZIP file to your Raspberry Pi 5" -ForegroundColor White
Write-Host "2. Extract the ZIP file" -ForegroundColor White
Write-Host "3. Run: chmod +x install-pi5.sh && ./install-pi5.sh" -ForegroundColor White
Write-Host "4. Start LYRA: ./start-lyra-pi5.sh" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "Build completed successfully!" -ForegroundColor Green
