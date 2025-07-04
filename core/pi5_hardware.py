"""
LYRA 3.0 - Raspberry Pi 5 Hardware Integration
Handles GPIO, Camera, I2C, SPI, and hardware monitoring
"""

import logging
import os
import json
import cv2
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
from threading import Thread, Lock

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
        
        # Object detection variables
        self.yolo_model = None
        self.detection_active = False
        self.detection_thread = None
        self.detection_lock = Lock()
        self.latest_detections = []
        self.detection_stats = {
            'total_frames': 0,
            'avg_inference_time': 0,
            'last_detection_time': None
        }
        
        # Initialize hardware components
        self._init_gpio()
        self._init_camera()
        self._init_i2c()
        self._init_yolo()
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
    
    def _init_yolo(self):
        """Initialize YOLO object detection model"""
        try:
            from ultralytics import YOLO
            model_path = "models/LYRA1.0/gen1/runs/detect/train7/weights/best.pt"
            
            # Check if model file exists
            if os.path.exists(model_path):
                self.yolo_model = YOLO(model_path)
                self.logger.info(f"YOLO model loaded from {model_path}")
            else:
                self.logger.warning(f"YOLO model not found at {model_path}")
                
        except ImportError:
            self.logger.warning("Ultralytics YOLO library not available")
        except Exception as e:
            self.logger.error(f"YOLO initialization failed: {e}")
    
    def _detect_hardware(self):
        """Detect available hardware components"""
        self.hardware_info = {
            'gpio_available': self.gpio_available,
            'camera_available': self.camera_available,
            'i2c_available': self.i2c_available,
            'yolo_available': self.yolo_model is not None,
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
            
            # Add YOLO detection status
            if self.yolo_model is not None:
                status['yolo_status'] = 'Available'
                status['detection_active'] = self.detection_active
                status['detection_stats'] = self.detection_stats.copy()
                
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
    
    def run_object_detection(self, source=0, confidence=0.5, show_preview=False) -> Dict[str, Any]:
        """Run object detection on camera feed or image"""
        if self.yolo_model is None:
            return {'status': 'error', 'message': 'YOLO model not available'}
        
        try:
            # Run inference
            results = self.yolo_model(source, conf=confidence, verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        detection = {
                            'class': result.names[int(box.cls[0])],
                            'confidence': float(box.conf[0]),
                            'bbox': box.xywh[0].tolist(),  # [x_center, y_center, width, height]
                            'xyxy': box.xyxy[0].tolist()   # [x1, y1, x2, y2]
                        }
                        detections.append(detection)
            
            # Update detection stats
            with self.detection_lock:
                self.latest_detections = detections
                self.detection_stats['total_frames'] += 1
                self.detection_stats['last_detection_time'] = str(datetime.now())
            
            return {
                'status': 'success',
                'detections': detections,
                'timestamp': str(datetime.now())
            }
            
        except Exception as e:
            self.logger.error(f"Object detection error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def start_continuous_detection(self, camera_index=0, confidence=0.5) -> Dict[str, Any]:
        """Start continuous object detection in a separate thread"""
        if self.yolo_model is None:
            return {'status': 'error', 'message': 'YOLO model not available'}
        
        if self.detection_active:
            return {'status': 'error', 'message': 'Detection already active'}
        
        try:
            self.detection_active = True
            self.detection_thread = Thread(
                target=self._detection_loop,
                args=(camera_index, confidence),
                daemon=True
            )
            self.detection_thread.start()
            
            return {'status': 'success', 'message': 'Continuous detection started'}
            
        except Exception as e:
            self.detection_active = False
            return {'status': 'error', 'message': str(e)}
    
    def stop_continuous_detection(self) -> Dict[str, Any]:
        """Stop continuous object detection"""
        if not self.detection_active:
            return {'status': 'error', 'message': 'Detection not active'}
        
        try:
            self.detection_active = False
            if self.detection_thread and self.detection_thread.is_alive():
                self.detection_thread.join(timeout=5)
            
            return {'status': 'success', 'message': 'Continuous detection stopped'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _detection_loop(self, camera_index, confidence):
        """Main detection loop for continuous detection"""
        cap = None
        try:
            cap = cv2.VideoCapture(camera_index)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            frame_count = 0
            total_inference_time = 0
            
            while self.detection_active:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                start_time = cv2.getTickCount()
                
                # Run detection on frame
                results = self.yolo_model(frame, conf=confidence, verbose=False)
                
                end_time = cv2.getTickCount()
                inference_time = (end_time - start_time) / cv2.getTickFrequency() * 1000
                
                # Process results
                detections = []
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            detection = {
                                'class': result.names[int(box.cls[0])],
                                'confidence': float(box.conf[0]),
                                'bbox': box.xywh[0].tolist(),
                                'xyxy': box.xyxy[0].tolist()
                            }
                            detections.append(detection)
                
                # Update stats
                frame_count += 1
                total_inference_time += inference_time
                
                with self.detection_lock:
                    self.latest_detections = detections
                    self.detection_stats['total_frames'] = frame_count
                    self.detection_stats['avg_inference_time'] = total_inference_time / frame_count
                    self.detection_stats['last_detection_time'] = str(datetime.now())
                
                # Small delay to prevent excessive CPU usage
                cv2.waitKey(1)
                
        except Exception as e:
            self.logger.error(f"Detection loop error: {e}")
        finally:
            if cap:
                cap.release()
            self.detection_active = False
    
    def get_latest_detections(self) -> Dict[str, Any]:
        """Get the latest detection results"""
        with self.detection_lock:
            return {
                'status': 'success',
                'detections': self.latest_detections.copy(),
                'stats': self.detection_stats.copy(),
                'timestamp': str(datetime.now())
            }
    
    def detect_objects_in_image(self, image_path: str, confidence=0.5) -> Dict[str, Any]:
        """Detect objects in a specific image file"""
        if self.yolo_model is None:
            return {'status': 'error', 'message': 'YOLO model not available'}
        
        if not os.path.exists(image_path):
            return {'status': 'error', 'message': f'Image file not found: {image_path}'}
        
        try:
            results = self.yolo_model(image_path, conf=confidence, verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        detection = {
                            'class': result.names[int(box.cls[0])],
                            'confidence': float(box.conf[0]),
                            'bbox': box.xywh[0].tolist(),
                            'xyxy': box.xyxy[0].tolist()
                        }
                        detections.append(detection)
            
            return {
                'status': 'success',
                'image_path': image_path,
                'detections': detections,
                'timestamp': str(datetime.now())
            }
            
        except Exception as e:
            self.logger.error(f"Image detection error: {e}")
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
            # Stop object detection if active
            if self.detection_active:
                self.stop_continuous_detection()
            
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
