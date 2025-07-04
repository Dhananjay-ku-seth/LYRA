#!/usr/bin/env python3
"""
LYRA 3.0 Master Installer and Updater
Handles installation, updates, and dependency management
"""

import os
import sys
import subprocess
import platform
import json
import urllib.request
import shutil
from pathlib import Path

class LyraInstaller:
    def __init__(self):
        self.system = platform.system()
        self.machine = platform.machine()
        self.python_version = sys.version_info
        self.current_dir = Path(__file__).parent
        self.errors = []
        
    def print_header(self):
        print("=" * 60)
        print("🤖 LYRA 3.0 - Installation & Update System")
        print("🚀 Logical Yielding Response Algorithm")
        print("=" * 60)
        print(f"System: {self.system} {self.machine}")
        print(f"Python: {sys.version}")
        print()
        
    def check_system_requirements(self):
        """Check if system meets minimum requirements"""
        print("🔍 Checking system requirements...")
        
        # Check Python version
        if self.python_version < (3, 8):
            self.errors.append("Python 3.8+ required")
            return False
            
        # Check available disk space (minimum 2GB)
        try:
            free_space = shutil.disk_usage(self.current_dir).free
            if free_space < 2 * 1024 * 1024 * 1024:  # 2GB
                self.errors.append("Insufficient disk space (need 2GB+)")
        except:
            pass
            
        print("✅ System requirements check passed")
        return True
        
    def install_python_dependencies(self):
        """Install Python dependencies"""
        print("📦 Installing Python dependencies...")
        
        # Determine requirements file
        if self.system == "Linux" and "raspberry" in platform.platform().lower():
            requirements_file = "requirements-pi5.txt"
        else:
            requirements_file = "requirements.txt"
            
        if not os.path.exists(requirements_file):
            self.errors.append(f"Requirements file {requirements_file} not found")
            return False
            
        try:
            # Create virtual environment if it doesn't exist
            venv_path = self.current_dir / "venv"
            if not venv_path.exists():
                print("Creating virtual environment...")
                subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
                
            # Determine activation script
            if self.system == "Windows":
                activate_script = venv_path / "Scripts" / "activate.bat"
                pip_path = venv_path / "Scripts" / "pip.exe"
                python_path = venv_path / "Scripts" / "python.exe"
            else:
                activate_script = venv_path / "bin" / "activate"
                pip_path = venv_path / "bin" / "pip"
                python_path = venv_path / "bin" / "python"
                
            # Upgrade pip first
            subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)
            
            # Install requirements
            subprocess.run([str(pip_path), "install", "-r", requirements_file], check=True)
            
            print("✅ Python dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Failed to install Python dependencies: {e}")
            return False
            
    def install_nodejs_dependencies(self):
        """Install Node.js dependencies for Electron GUI"""
        print("📦 Installing Node.js dependencies...")
        
        if not os.path.exists("package.json"):
            print("⚠️ No package.json found - skipping Node.js installation")
            return True
            
        try:
            # Check if npm is available
            subprocess.run(["npm", "--version"], check=True, capture_output=True)
            
            # Install dependencies
            subprocess.run(["npm", "install"], check=True)
            
            print("✅ Node.js dependencies installed successfully")
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ Node.js not found - GUI will use web interface only")
            return True
            
    def test_installation(self):
        """Test the installation"""
        print("🧪 Testing installation...")
        
        # Test Python imports
        test_modules = [
            ("flask", "Flask web framework"),
            ("flask_socketio", "WebSocket support"),
            ("psutil", "System monitoring"),
        ]
        
        # Optional modules (won't fail installation)
        optional_modules = [
            ("pyttsx3", "Text-to-speech"),
            ("speech_recognition", "Voice recognition"),
            ("pyaudio", "Audio processing"),
        ]
        
        all_passed = True
        
        for module, description in test_modules:
            try:
                __import__(module)
                print(f"✅ {description}")
            except ImportError:
                print(f"❌ {description}")
                self.errors.append(f"Required module {module} not available")
                all_passed = False
                
        for module, description in optional_modules:
            try:
                __import__(module)
                print(f"✅ {description}")
            except ImportError:
                print(f"⚠️ {description} (optional)")
                
        return all_passed
        
    def create_shortcuts(self):
        """Create desktop shortcuts and start scripts"""
        print("🔗 Creating shortcuts...")
        
        try:
            if self.system == "Windows":
                self.create_windows_shortcuts()
            elif self.system == "Linux":
                self.create_linux_shortcuts()
            else:
                print("⚠️ Shortcut creation not supported on this platform")
                
            print("✅ Shortcuts created")
            return True
            
        except Exception as e:
            print(f"⚠️ Could not create shortcuts: {e}")
            return True  # Non-critical
            
    def create_windows_shortcuts(self):
        """Create Windows shortcuts"""
        # Create start script
        start_script = self.current_dir / "Start-LYRA.bat"
        with open(start_script, 'w') as f:
            f.write(f"""@echo off
title LYRA 3.0 - AI Assistant
cd /d "{self.current_dir}"
call venv\\Scripts\\activate.bat
python start_lyra.py
pause
""")
            
        # Create GUI script
        gui_script = self.current_dir / "Start-LYRA-GUI.bat"
        with open(gui_script, 'w') as f:
            f.write(f"""@echo off
title LYRA 3.0 - GUI
cd /d "{self.current_dir}"
start "LYRA Backend" Start-LYRA.bat
timeout /t 5 /nobreak
npm start
""")
            
    def create_linux_shortcuts(self):
        """Create Linux shortcuts"""
        # Create start script
        start_script = self.current_dir / "start-lyra.sh"
        with open(start_script, 'w') as f:
            f.write(f"""#!/bin/bash
cd "{self.current_dir}"
source venv/bin/activate
python3 start_lyra.py
""")
        os.chmod(start_script, 0o755)
        
        # Create desktop entry
        desktop_file = Path.home() / "Desktop" / "LYRA-3.0.desktop"
        with open(desktop_file, 'w') as f:
            f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name=LYRA 3.0
Comment=AI Assistant System
Exec={start_script}
Icon={self.current_dir}/resources/icon.png
Terminal=true
Categories=Development;Science;
""")
        os.chmod(desktop_file, 0o755)
        
    def setup_voice_system(self):
        """Setup voice recognition and TTS"""
        print("🎤 Setting up voice system...")
        
        if self.system == "Windows":
            print("ℹ️ Windows voice system uses built-in SAPI")
            return True
        elif self.system == "Linux":
            return self.setup_linux_voice()
        else:
            print("⚠️ Voice system setup not supported on this platform")
            return True
            
    def setup_linux_voice(self):
        """Setup Linux voice system"""
        try:
            # Check for espeak
            subprocess.run(["which", "espeak"], check=True, capture_output=True)
            print("✅ espeak found")
        except subprocess.CalledProcessError:
            print("⚠️ Consider installing espeak for better TTS: sudo apt install espeak")
            
        try:
            # Check for ALSA
            subprocess.run(["which", "aplay"], check=True, capture_output=True)
            print("✅ ALSA audio system found")
        except subprocess.CalledProcessError:
            print("⚠️ Consider installing ALSA: sudo apt install alsa-utils")
            
        return True
        
    def create_config_files(self):
        """Create default configuration files"""
        print("⚙️ Creating configuration files...")
        
        # Create config directory
        config_dir = self.current_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Create main config
        main_config = {
            "system": {
                "platform": self.system.lower(),
                "version": "3.0.0",
                "installation_date": str(Path.cwd()),
            },
            "voice": {
                "enabled": True,
                "wake_words": ["hi lyra", "hey lyra", "lyra"],
                "tts_rate": 150,
                "tts_volume": 0.9
            },
            "network": {
                "host": "127.0.0.1",
                "port": 5000,
                "debug": False
            }
        }
        
        config_file = config_dir / "main-config.json"
        with open(config_file, 'w') as f:
            json.dump(main_config, f, indent=4)
            
        print("✅ Configuration files created")
        return True
        
    def run_installation(self):
        """Run the complete installation process"""
        self.print_header()
        
        if not self.check_system_requirements():
            print("❌ System requirements not met:")
            for error in self.errors:
                print(f"   - {error}")
            return False
            
        steps = [
            ("Installing Python dependencies", self.install_python_dependencies),
            ("Installing Node.js dependencies", self.install_nodejs_dependencies),
            ("Testing installation", self.test_installation),
            ("Setting up voice system", self.setup_voice_system),
            ("Creating configuration files", self.create_config_files),
            ("Creating shortcuts", self.create_shortcuts),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            if not step_func():
                print(f"❌ {step_name} failed")
                break
        else:
            self.print_success()
            return True
            
        print("\n❌ Installation failed:")
        for error in self.errors:
            print(f"   - {error}")
        return False
        
    def print_success(self):
        """Print success message with next steps"""
        print("\n" + "=" * 60)
        print("🎉 LYRA 3.0 Installation Complete!")
        print("=" * 60)
        print()
        print("🚀 To start LYRA:")
        
        if self.system == "Windows":
            print("   Double-click: Start-LYRA.bat")
            print("   Or run: python start_lyra.py")
        else:
            print("   Run: ./start-lyra.sh")
            print("   Or: python3 start_lyra.py")
            
        print()
        print("🌐 Web interface will be available at:")
        print("   http://localhost:5000")
        print()
        print("🎤 Voice commands:")
        print("   Say 'Hi LYRA' or 'Hey LYRA' to activate")
        print()
        print("📚 Documentation:")
        print("   Check README.md for detailed usage instructions")
        print()
        
def main():
    """Main installation entry point"""
    installer = LyraInstaller()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode - just check installation
        installer.print_header()
        installer.test_installation()
    else:
        # Full installation
        success = installer.run_installation()
        sys.exit(0 if success else 1)
        
if __name__ == "__main__":
    main()
