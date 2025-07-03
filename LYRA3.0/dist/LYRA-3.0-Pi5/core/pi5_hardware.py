"""
LYRA 3.0 - Raspberry Pi 5 Hardware Integration
Handles GPIO, Camera, I2C, SPI, and hardware monitoring
"""

import logging
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

class Pi5Hardware:
    """
    Raspberry Pi 5 hardware integration and monitoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gpio_available = False
        self.camera_available = False
        self.i2c_available = False
        self.hardware_info = {}
        
        # Initialize hardware components
        self._init_gpio()
        self._init_camera()
        self._init_i2c()
        self._detect_hardware()
        
    def _init_gpio(self):
        """Initialize GPIO support"""
        try:
            import gpiozero
            import RPi.GPIO as GPIO
            self.gpiozero = gpiozero
            self.GPIO = GPIO
            self.gpio_available = True
            self.logger.info("GPIO support initialized")
        except ImportError:
            self.logger.warning("GPIO libraries not available (not on Raspberry Pi)")
        except Exception as e:
            self.logger.error(f"GPIO initialization failed: {e}")
    
    def _init_camera(self):
        """Initialize camera support"""
        try:
            from picamera2 import Picamera2
            self.camera = Picamera2()
            self.camera_available = True
            self.logger.info("Camera support initialized")
        except ImportError:
            self.logger.warning("Camera library not available")
        except Exception as e:
            self.logger.error(f"Camera initialization failed: {e}")
    
    def _init_i2c(self):
        """Initialize I2C support"""
        try:
            import smbus2
            self.i2c = smbus2.SMBus(1)  # I2C bus 1
            self.i2c_available = True
            self.logger.info("I2C support initialized")
        except ImportError:
            self.logger.warning("I2C library not available")
        except Exception as e:
            self.logger.error(f"I2C initialization failed: {e}")
    
    def _detect_hardware(self):
        """Detect available hardware components"""
        self.hardware_info = {
            'gpio_available': self.gpio_available,
            'camera_available': self.camera_available,
            'i2c_available': self.i2c_available,
            'cpu_temp_available': os.path.exists('/sys/class/thermal/thermal_zone0/temp'),
            'gpu_temp_available': os.path.exists('/opt/vc/bin/vcgencmd'),
            'model': self._get_pi_model(),
            'memory': self._get_memory_info(),
            'timestamp': str(datetime.now())
        }
        
    def _get_pi_model(self) -> str:
        """Get Raspberry Pi model information"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('Model'):
                        return line.split(':')[1].strip()
            return "Unknown Pi Model"
        except:
            return "Not a Raspberry Pi"
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = {}
                for line in f:
                    if line.startswith(('MemTotal', 'MemFree', 'MemAvailable')):
                        key, value = line.split(':')
                        meminfo[key.strip()] = value.strip()
                return meminfo
        except:
            return {}
    
    def get_cpu_temperature(self) -> float:
        """Get CPU temperature"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read()) / 1000.0
                return temp
        except:
            return 0.0
    
    def get_gpu_temperature(self) -> float:
        """Get GPU temperature"""
        try:
            import subprocess
            result = subprocess.run(['/opt/vc/bin/vcgencmd', 'measure_temp'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                temp_str = result.stdout.strip()
                temp = float(temp_str.replace('temp=', '').replace("'C", ''))
                return temp
        except:
            pass
        return 0.0
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            import psutil
            
            status = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'cpu_temp': self.get_cpu_temperature(),
                'gpu_temp': self.get_gpu_temperature(),
                'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
                'boot_time': psutil.boot_time(),
                'timestamp': str(datetime.now())
            }
            
            # Add GPIO status if available
            if self.gpio_available:
                status['gpio_status'] = 'Available'
            
            # Add camera status if available
            if self.camera_available:
                status['camera_status'] = 'Available'
                
            return status
            
        except Exception as e:
            self.logger.error(f"System status error: {e}")
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'cpu_temp': self.get_cpu_temperature(),
                'error': str(e),
                'timestamp': str(datetime.now())
            }
    
    def control_gpio_pin(self, pin: int, action: str, value: Any = None) -> Dict[str, Any]:
        """Control GPIO pins"""
        if not self.gpio_available:
            return {'status': 'error', 'message': 'GPIO not available'}
        
        try:
            if action == 'set_output':
                led = self.gpiozero.LED(pin)
                if value:
                    led.on()
                else:
                    led.off()
                return {'status': 'success', 'pin': pin, 'action': action, 'value': value}
                
            elif action == 'read_input':
                button = self.gpiozero.Button(pin)
                return {'status': 'success', 'pin': pin, 'value': button.is_pressed}
                
            elif action == 'pwm':
                pwm_device = self.gpiozero.PWMOutputDevice(pin)
                pwm_device.value = float(value) / 100.0  # Convert percentage to 0-1
                return {'status': 'success', 'pin': pin, 'pwm_value': value}
                
        except Exception as e:
            self.logger.error(f"GPIO control error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def capture_camera_image(self, filename: str = None) -> Dict[str, Any]:
        """Capture image from camera"""
        if not self.camera_available:
            return {'status': 'error', 'message': 'Camera not available'}
        
        try:
            if not filename:
                filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            # Configure and capture
            self.camera.configure(self.camera.create_still_configuration())
            self.camera.start()
            self.camera.capture_file(filename)
            self.camera.stop()
            
            return {
                'status': 'success',
                'filename': filename,
                'timestamp': str(datetime.now())
            }
            
        except Exception as e:
            self.logger.error(f"Camera capture error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def start_camera_stream(self) -> Dict[str, Any]:
        """Start camera streaming"""
        if not self.camera_available:
            return {'status': 'error', 'message': 'Camera not available'}
        
        try:
            self.camera.configure(self.camera.create_preview_configuration())
            self.camera.start()
            return {'status': 'success', 'message': 'Camera stream started'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def stop_camera_stream(self) -> Dict[str, Any]:
        """Stop camera streaming"""
        if not self.camera_available:
            return {'status': 'error', 'message': 'Camera not available'}
        
        try:
            self.camera.stop()
            return {'status': 'success', 'message': 'Camera stream stopped'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def read_i2c_device(self, address: int, register: int = None) -> Dict[str, Any]:
        """Read from I2C device"""
        if not self.i2c_available:
            return {'status': 'error', 'message': 'I2C not available'}
        
        try:
            if register is not None:
                data = self.i2c.read_byte_data(address, register)
            else:
                data = self.i2c.read_byte(address)
            
            return {
                'status': 'success',
                'address': hex(address),
                'register': hex(register) if register else None,
                'data': data
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def optimize_performance(self) -> Dict[str, Any]:
        """Optimize system performance for LYRA"""
        optimizations = []
        
        try:
            # Set CPU governor to performance mode
            os.system("echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor")
            optimizations.append("CPU governor set to performance")
            
            # Increase GPU memory split for graphics
            # Note: This requires a reboot to take effect
            os.system("echo 'gpu_mem=128' | sudo tee -a /boot/config.txt")
            optimizations.append("GPU memory increased")
            
            # Set I/O scheduler to noop for better performance
            os.system("echo noop | sudo tee /sys/block/mmcblk0/queue/scheduler")
            optimizations.append("I/O scheduler optimized")
            
            return {
                'status': 'success',
                'optimizations': optimizations,
                'note': 'Some changes require reboot'
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware information"""
        return self.hardware_info
    
    def cleanup(self):
        """Clean up hardware resources"""
        try:
            if self.camera_available and hasattr(self, 'camera'):
                self.camera.stop()
                self.camera.close()
            
            if self.gpio_available and hasattr(self, 'GPIO'):
                self.GPIO.cleanup()
                
            if self.i2c_available and hasattr(self, 'i2c'):
                self.i2c.close()
                
            self.logger.info("Hardware cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Hardware cleanup error: {e}")
