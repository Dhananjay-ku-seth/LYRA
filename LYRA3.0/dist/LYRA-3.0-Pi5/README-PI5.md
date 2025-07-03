# LYRA 3.0 - Raspberry Pi 5 Deployment Package

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

For issues and documentation, see DEPLOYMENT.md
