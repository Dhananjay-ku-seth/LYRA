#!/usr/bin/env python3
"""
LYRA 3.0 Production Launcher
Handles backend startup and dependency checking
"""

import os
import sys
import subprocess
import logging
import time
from pathlib import Path

class LyraLauncher:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.backend_dir = self.base_dir / "backend" if (self.base_dir / "backend").exists() else self.base_dir
        
    def check_python(self):
        """Check if Python is available"""
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            print(f"✅ Python: {result.stdout.strip()}")
            return True
        except Exception as e:
            print(f"❌ Python not found: {e}")
            return False
    
    def install_dependencies(self):
        """Install required Python dependencies"""
        requirements_file = self.backend_dir / "requirements.txt"
        if not requirements_file.exists():
            print("⚠️ No requirements.txt found, continuing without dependency installation")
            return True
            
        try:
            print("📦 Installing Python dependencies...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dependencies installed successfully")
                return True
            else:
                print(f"⚠️ Some dependencies failed to install: {result.stderr}")
                return True  # Continue anyway with available dependencies
        except Exception as e:
            print(f"⚠️ Dependency installation failed: {e}")
            return True  # Continue anyway
    
    def start_backend(self):
        """Start the LYRA backend server"""
        main_py = self.backend_dir / "main.py"
        if not main_py.exists():
            print(f"❌ Backend not found at {main_py}")
            return False
            
        try:
            print("🚀 Starting LYRA 3.0 backend...")
            
            # Start backend in background
            process = subprocess.Popen([
                sys.executable, str(main_py)
            ], cwd=str(self.backend_dir))
            
            # Give backend time to start
            time.sleep(3)
            
            if process.poll() is None:
                print("✅ Backend started successfully")
                return process
            else:
                print("❌ Backend failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Backend startup failed: {e}")
            return False
    
    def launch(self):
        """Main launcher function"""
        print("=" * 60)
        print("🤖 LYRA 3.0 - AI Assistant Launcher")
        print("=" * 60)
        
        # Check Python
        if not self.check_python():
            input("Press Enter to exit...")
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            print("❌ Critical dependency installation failed")
            input("Press Enter to exit...")
            return False
        
        # Start backend
        backend_process = self.start_backend()
        if not backend_process:
            print("❌ Failed to start backend")
            input("Press Enter to exit...")
            return False
        
        print("✅ LYRA 3.0 is now running!")
        print("🌐 Backend: http://localhost:5000")
        print("📋 Press Ctrl+C to stop the system")
        
        try:
            # Keep launcher running
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down LYRA 3.0...")
            backend_process.terminate()
            backend_process.wait()
            print("✅ LYRA 3.0 stopped")
        
        return True

if __name__ == "__main__":
    launcher = LyraLauncher()
    launcher.launch()
