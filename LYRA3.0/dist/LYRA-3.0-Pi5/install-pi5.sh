#!/bin/bash
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
echo "Run ./start-lyra-pi5.sh to start LYRA 3.0"
