#!/bin/bash
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
python3 main-pi5.py
