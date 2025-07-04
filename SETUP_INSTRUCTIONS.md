# LYRA 3.0 Setup Instructions

## Overview
LYRA 3.0 is available as portable packages for both Windows and Raspberry Pi 5. Each package is self-contained with all dependencies and ready for deployment.

## Available Packages
- `LYRA-3.0-Windows-Portable.zip` - Windows deployment package
- `LYRA-3.0-Pi5-Portable.zip` - Raspberry Pi 5 deployment package

## Windows Deployment

### Prerequisites
- Windows 10 or later
- No additional software installation required (all dependencies included)

### Installation Steps
1. **Extract the package**
   ```
   Extract LYRA-3.0-Windows-Portable.zip to your desired location
   ```

2. **Start LYRA**
   ```
   Run LYRA-3.0.bat to start the system
   ```

3. **Access the interface**
   ```
   Open your web browser and navigate to: http://localhost:5000
   ```

### File Structure (Windows)
```
LYRA-3.0-Windows/
├── LYRA-3.0.bat          # Main startup script
├── core/                 # Core AI modules
├── data/                 # Knowledge base and data files
├── gui/                  # Web interface files
├── venv/                 # Python virtual environment with dependencies
├── main.py               # Main application entry point
├── start_lyra.py         # Application starter
└── install-lyra.py       # Installation utilities
```

## Raspberry Pi 5 Deployment

### Prerequisites
- Raspberry Pi 5 with Raspberry Pi OS (64-bit recommended)
- Internet connection for initial setup
- Minimum 4GB RAM, 16GB storage recommended

### Installation Steps
1. **Transfer the package**
   ```bash
   # Copy the zip file to your Raspberry Pi
   scp LYRA-3.0-Pi5-Portable.zip pi@your-pi-ip:~/
   ```

2. **Extract the package**
   ```bash
   cd ~
   unzip LYRA-3.0-Pi5-Portable.zip
   ```

3. **Install dependencies**
   ```bash
   cd LYRA-3.0-Pi5
   chmod +x install-pi5.sh
   ./install-pi5.sh
   ```

4. **Start LYRA**
   ```bash
   ./start-lyra-pi5.sh
   ```

5. **Access the interface**
   ```
   Open a web browser and navigate to: http://localhost:5000
   or from another device: http://[pi-ip-address]:5000
   ```

### File Structure (Raspberry Pi 5)
```
LYRA-3.0-Pi5/
├── start-lyra-pi5.sh     # Main startup script
├── install-pi5.sh        # Dependency installation script
├── requirements.txt      # Python dependencies
├── core/                 # Core AI modules (optimized for Pi5)
├── data/                 # Knowledge base and data files
├── gui/                  # Web interface files
├── main.py               # Main application entry point
├── README-Pi5.txt        # Pi5-specific documentation
└── install-lyra.py       # Installation utilities
```

## Troubleshooting

### Windows Issues
- **Port 5000 already in use**: Change the port in `main.py` or stop other services using port 5000
- **Antivirus blocking**: Add the LYRA folder to your antivirus exclusion list
- **Permission errors**: Run as administrator if needed

### Raspberry Pi 5 Issues
- **Permission denied**: Ensure scripts are executable with `chmod +x *.sh`
- **Missing dependencies**: Run the install script again: `./install-pi5.sh`
- **Audio issues**: Check ALSA/PulseAudio configuration for microphone and speaker access
- **Performance**: Ensure adequate cooling and power supply for optimal performance

## Configuration

### Audio Setup (Raspberry Pi 5)
The system requires microphone and speaker access. Configure audio devices:
```bash
# List audio devices
aplay -l
arecord -l

# Test microphone
arecord -d 5 test.wav && aplay test.wav
```

### Network Access
- Default port: 5000
- To access from other devices on the network, ensure firewall allows connections
- For remote access, consider setting up SSH tunneling or VPN

## Support
- Both packages are optimized for their respective platforms
- All dependencies are included and pre-configured
- The builds have been tested and are ready for production deployment

## Security Notes
- Change default passwords if any are set
- Configure firewall rules as needed for your network
- Keep the system updated with security patches
- Consider running behind a reverse proxy for external access

---

**Note**: These packages are self-contained and do not require internet connectivity for core functionality, though some features may benefit from network access.
