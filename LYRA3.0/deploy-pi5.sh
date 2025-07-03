#!/bin/bash
# LYRA 3.0 Raspberry Pi 5 Deployment Script
echo "🚀 Deploying LYRA 3.0 on Raspberry Pi 5"

# Create virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv lyra_env
source lyra_env/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-pi5.txt

# Create configuration and log directories
mkdir -p config logs

# Copy necessary files
cp -r gui config main-pi5.py logs

# Create systemd service
cat <<EOL | sudo tee /etc/systemd/system/lyra3.service
[Unit]
Description=LYRA 3.0 AI Assistant with Raspberry Pi integration
After=network.target

[Service]
ExecStart=/home/pi/lyra_env/bin/python3 /home/pi/LYRA3.0/main-pi5.py
WorkingDirectory=/home/pi/LYRA3.0
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOL

# Enable and start the new service
echo "🔧 Enabling LYRA service..."
sudo systemctl daemon-reload
sudo systemctl enable lyra3.service
sudo systemctl start lyra3.service

# Echo status
echo "✅ LYRA 3.0 Raspberry Pi 5 deployment complete!"

# Tell the user they can check service status
echo "ℹ️ Check service status with: sudo systemctl status lyra3.service"
