#!/usr/bin/env python3
"""
LYRA 3.0 Native Desktop Application for Raspberry Pi 5
Creates a native desktop app similar to Windows version
"""

import sys
import os
import json
import threading
import time
from datetime import datetime

# Add core modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    PYQT_AVAILABLE = True
except ImportError:
    print("PyQt5 not available, using Tkinter fallback")
    import tkinter as tk
    from tkinter import ttk, messagebox
    import webbrowser
    PYQT_AVAILABLE = False

from core.decision_engine import DecisionEngine
from core.context_manager import ContextManager
from core.tts_output import TTSOutput

# Pi5-specific imports
try:
    from core.pi5_hardware import Pi5Hardware
    PI5_HARDWARE_AVAILABLE = True
except ImportError:
    PI5_HARDWARE_AVAILABLE = False

class LyraPi5App:
    """
    Native LYRA 3.0 Desktop Application for Raspberry Pi 5
    """
    
    def __init__(self):
        self.backend_process = None
        self.hardware = None
        self.context_mgr = None
        self.decision_engine = None
        self.tts_output = None
        
        # Initialize LYRA components
        self.init_lyra_components()
        
        if PYQT_AVAILABLE:
            self.init_pyqt_app()
        else:
            self.init_tkinter_app()
    
    def init_lyra_components(self):
        """Initialize LYRA backend components"""
        try:
            self.context_mgr = ContextManager()
            self.decision_engine = DecisionEngine(self.context_mgr)
            self.tts_output = TTSOutput()
            
            if PI5_HARDWARE_AVAILABLE:
                self.hardware = Pi5Hardware()
                print("✅ Pi5 hardware integration loaded")
            else:
                print("⚠️ Pi5 hardware integration not available")
                
        except Exception as e:
            print(f"❌ Error initializing LYRA components: {e}")
    
    def init_pyqt_app(self):
        """Initialize PyQt5 application (preferred)"""
        self.app = QApplication(sys.argv)
        self.create_pyqt_window()
    
    def create_pyqt_window(self):
        """Create PyQt5 main window"""
        self.window = QMainWindow()
        self.window.setWindowTitle("🤖 LYRA 3.0 - Raspberry Pi 5 Edition")
        self.window.setGeometry(100, 100, 1200, 800)
        
        # Set window icon
        self.window.setWindowIcon(QIcon.fromTheme("computer"))
        
        # Create central widget
        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = self.create_header_widget()
        layout.addWidget(header)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_home_tab()
        self.create_system_tab()
        self.create_hardware_tab()
        self.create_settings_tab()
        
        # Status bar
        self.status_bar = self.window.statusBar()
        self.status_bar.showMessage("🍓 LYRA 3.0 Pi5 Ready")
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Start backend server in thread
        self.start_backend_server()
        
        # Show window
        self.window.show()
    
    def create_header_widget(self):
        """Create header with LYRA branding"""
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a1a1a, stop:1 #2a2a2a); border-bottom: 2px solid #00d4ff;")
        
        layout = QHBoxLayout(header)
        
        # LYRA title
        title_label = QLabel("🤖 LYRA 3.0")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00d4ff; padding: 10px;")
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Raspberry Pi 5 Edition")
        subtitle_label.setStyleSheet("font-size: 12px; color: #b0b0b0; padding: 10px;")
        layout.addWidget(subtitle_label)
        
        layout.addStretch()
        
        # System info
        self.system_info_label = QLabel("Loading...")
        self.system_info_label.setStyleSheet("font-size: 11px; color: #888888; padding: 10px;")
        layout.addWidget(self.system_info_label)
        
        # Update system info
        self.update_system_info()
        
        return header
    
    def create_home_tab(self):
        """Create home tab with main controls"""
        home_widget = QWidget()
        layout = QGridLayout(home_widget)
        
        # LYRA Core visualization
        core_group = QGroupBox("🤖 LYRA Core")
        core_group.setStyleSheet("QGroupBox { font-weight: bold; color: #00d4ff; }")
        core_layout = QVBoxLayout(core_group)
        
        # Status display
        self.status_display = QTextEdit()
        self.status_display.setMaximumHeight(100)
        self.status_display.setReadOnly(True)
        self.status_display.setPlainText("🍓 LYRA 3.0 Raspberry Pi Edition\n✅ System Online\n🤖 Ready for commands")
        core_layout.addWidget(self.status_display)
        
        layout.addWidget(core_group, 0, 0, 1, 2)
        
        # Voice control
        voice_group = QGroupBox("🎙️ Voice Control")
        voice_group.setStyleSheet("QGroupBox { font-weight: bold; color: #00ff88; }")
        voice_layout = QHBoxLayout(voice_group)
        
        self.voice_start_btn = QPushButton("🎤 Start Listening")
        self.voice_start_btn.clicked.connect(self.start_voice_listening)
        self.voice_start_btn.setStyleSheet("QPushButton { background: #00ff88; color: black; font-weight: bold; padding: 10px; border-radius: 5px; }")
        voice_layout.addWidget(self.voice_start_btn)
        
        self.voice_stop_btn = QPushButton("🛑 Stop")
        self.voice_stop_btn.clicked.connect(self.stop_voice_listening)
        self.voice_stop_btn.setEnabled(False)
        voice_layout.addWidget(self.voice_stop_btn)
        
        layout.addWidget(voice_group, 1, 0)
        
        # Text commands
        text_group = QGroupBox("⌨️ Text Commands")
        text_group.setStyleSheet("QGroupBox { font-weight: bold; color: #00d4ff; }")
        text_layout = QVBoxLayout(text_group)
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command...")
        self.command_input.returnPressed.connect(self.process_text_command)
        text_layout.addWidget(self.command_input)
        
        send_btn = QPushButton("📤 Send Command")
        send_btn.clicked.connect(self.process_text_command)
        send_btn.setStyleSheet("QPushButton { background: #00d4ff; color: black; font-weight: bold; padding: 8px; border-radius: 5px; }")
        text_layout.addWidget(send_btn)
        
        layout.addWidget(text_group, 1, 1)
        
        # Mode control
        mode_group = QGroupBox("⚙️ Operation Mode")
        mode_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ff8800; }")
        mode_layout = QHBoxLayout(mode_group)
        
        modes = ["🏠 Home", "🛡️ Defense", "🌙 Night", "🔧 Manual"]
        self.mode_buttons = []
        
        for mode in modes:
            btn = QPushButton(mode)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, m=mode: self.change_mode(m))
            btn.setStyleSheet("QPushButton { padding: 8px; border-radius: 5px; } QPushButton:checked { background: #ff8800; color: black; font-weight: bold; }")
            mode_layout.addWidget(btn)
            self.mode_buttons.append(btn)
        
        # Set home mode as default
        self.mode_buttons[0].setChecked(True)
        
        layout.addWidget(mode_group, 2, 0, 1, 2)
        
        self.tab_widget.addTab(home_widget, "🏠 Home")
    
    def create_system_tab(self):
        """Create system control tab"""
        system_widget = QWidget()
        layout = QHBoxLayout(system_widget)
        
        # TRINETRA control
        trinetra_group = QGroupBox("🚗 TRINETRA Ground Bot")
        trinetra_group.setStyleSheet("QGroupBox { font-weight: bold; color: #00ff88; }")
        trinetra_layout = QGridLayout(trinetra_group)
        
        # Movement controls
        move_forward = QPushButton("⬆️")
        move_forward.clicked.connect(lambda: self.control_trinetra("forward"))
        trinetra_layout.addWidget(move_forward, 0, 1)
        
        move_left = QPushButton("⬅️")
        move_left.clicked.connect(lambda: self.control_trinetra("left"))
        trinetra_layout.addWidget(move_left, 1, 0)
        
        stop_btn = QPushButton("🛑")
        stop_btn.clicked.connect(lambda: self.control_trinetra("stop"))
        stop_btn.setStyleSheet("QPushButton { background: #ff4444; color: white; font-weight: bold; }")
        trinetra_layout.addWidget(stop_btn, 1, 1)
        
        move_right = QPushButton("➡️")
        move_right.clicked.connect(lambda: self.control_trinetra("right"))
        trinetra_layout.addWidget(move_right, 1, 2)
        
        move_backward = QPushButton("⬇️")
        move_backward.clicked.connect(lambda: self.control_trinetra("backward"))
        trinetra_layout.addWidget(move_backward, 2, 1)
        
        # Camera controls
        camera_btn = QPushButton("📷 Capture")
        camera_btn.clicked.connect(self.capture_image)
        trinetra_layout.addWidget(camera_btn, 3, 0, 1, 3)
        
        layout.addWidget(trinetra_group)
        
        # KRAIT-3 control
        krait_group = QGroupBox("🚁 KRAIT-3 UAV")
        krait_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ff8800; }")
        krait_layout = QVBoxLayout(krait_group)
        
        flight_buttons = [
            ("🚀 Launch", lambda: self.control_krait3("launch")),
            ("⏸️ Hover", lambda: self.control_krait3("hover")),
            ("🏠 Return", lambda: self.control_krait3("return")),
            ("🚨 Emergency Land", lambda: self.control_krait3("emergency_land"))
        ]
        
        for btn_text, btn_action in flight_buttons:
            btn = QPushButton(btn_text)
            btn.clicked.connect(btn_action)
            if "Emergency" in btn_text:
                btn.setStyleSheet("QPushButton { background: #ff4444; color: white; font-weight: bold; padding: 10px; }")
            else:
                btn.setStyleSheet("QPushButton { padding: 10px; }")
            krait_layout.addWidget(btn)
        
        layout.addWidget(krait_group)
        
        self.tab_widget.addTab(system_widget, "🤖 System")
    
    def create_hardware_tab(self):
        """Create Pi5 hardware control tab"""
        hardware_widget = QWidget()
        layout = QVBoxLayout(hardware_widget)
        
        if self.hardware:
            # Hardware info
            info_group = QGroupBox("🍓 Pi5 Hardware Status")
            info_group.setStyleSheet("QGroupBox { font-weight: bold; color: #00d4ff; }")
            info_layout = QVBoxLayout(info_group)
            
            self.hardware_info_display = QTextEdit()
            self.hardware_info_display.setMaximumHeight(150)
            self.hardware_info_display.setReadOnly(True)
            info_layout.addWidget(self.hardware_info_display)
            
            refresh_btn = QPushButton("🔄 Refresh Hardware Info")
            refresh_btn.clicked.connect(self.refresh_hardware_info)
            info_layout.addWidget(refresh_btn)
            
            layout.addWidget(info_group)
            
            # GPIO control
            gpio_group = QGroupBox("🔌 GPIO Control")
            gpio_group.setStyleSheet("QGroupBox { font-weight: bold; color: #00ff88; }")
            gpio_layout = QGridLayout(gpio_group)
            
            # LED controls (example)
            for i, pin in enumerate([18, 19, 20, 21]):
                led_btn = QPushButton(f"💡 LED {pin}")
                led_btn.setCheckable(True)
                led_btn.clicked.connect(lambda checked, p=pin: self.control_gpio_led(p, checked))
                gpio_layout.addWidget(led_btn, i // 2, i % 2)
            
            layout.addWidget(gpio_group)
            
            # Update hardware info
            self.refresh_hardware_info()
        else:
            no_hw_label = QLabel("⚠️ Pi5 Hardware integration not available")
            no_hw_label.setAlignment(Qt.AlignCenter)
            no_hw_label.setStyleSheet("font-size: 16px; color: #ff8800; padding: 50px;")
            layout.addWidget(no_hw_label)
        
        self.tab_widget.addTab(hardware_widget, "🍓 Hardware")
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # Voice settings
        voice_group = QGroupBox("🎙️ Voice Settings")
        voice_layout = QFormLayout(voice_group)
        
        self.voice_rate_slider = QSlider(Qt.Horizontal)
        self.voice_rate_slider.setRange(50, 300)
        self.voice_rate_slider.setValue(150)
        voice_layout.addRow("Speech Rate:", self.voice_rate_slider)
        
        self.voice_volume_slider = QSlider(Qt.Horizontal)
        self.voice_volume_slider.setRange(0, 100)
        self.voice_volume_slider.setValue(90)
        voice_layout.addRow("Volume:", self.voice_volume_slider)
        
        layout.addWidget(voice_group)
        
        # System settings
        system_group = QGroupBox("⚙️ System Settings")
        system_layout = QFormLayout(system_group)
        
        self.auto_start_cb = QCheckBox("Auto-start on boot")
        system_layout.addRow(self.auto_start_cb)
        
        self.full_screen_cb = QCheckBox("Start in fullscreen")
        system_layout.addRow(self.full_screen_cb)
        
        layout.addWidget(system_group)
        
        # About
        about_group = QGroupBox("ℹ️ About")
        about_layout = QVBoxLayout(about_group)
        
        about_text = QLabel("""
🤖 LYRA 3.0 - Raspberry Pi 5 Edition
🍓 Optimized for ARM64 architecture
🎯 AI-powered robotics control system
        """)
        about_text.setStyleSheet("padding: 20px; font-size: 12px;")
        about_layout.addWidget(about_text)
        
        layout.addWidget(about_group)
        
        self.tab_widget.addTab(settings_widget, "⚙️ Settings")
    
    def apply_dark_theme(self):
        """Apply dark theme similar to JARVIS"""
        dark_style = """
            QMainWindow { background-color: #0a0a0a; }
            QWidget { background-color: #1a1a1a; color: #ffffff; }
            QTabWidget::pane { border: 1px solid #333333; background-color: #1a1a1a; }
            QTabBar::tab { background-color: #2a2a2a; color: #b0b0b0; padding: 8px 16px; margin: 2px; }
            QTabBar::tab:selected { background-color: #00d4ff; color: #000000; font-weight: bold; }
            QGroupBox { border: 2px solid #333333; border-radius: 5px; margin: 10px; padding-top: 10px; }
            QPushButton { background-color: #2a2a2a; border: 1px solid #555555; padding: 8px; border-radius: 5px; }
            QPushButton:hover { background-color: #3a3a3a; border-color: #00d4ff; }
            QPushButton:pressed { background-color: #4a4a4a; }
            QLineEdit { background-color: #2a2a2a; border: 1px solid #555555; padding: 8px; border-radius: 5px; }
            QTextEdit { background-color: #2a2a2a; border: 1px solid #555555; border-radius: 5px; }
            QSlider::groove:horizontal { height: 8px; background: #555555; border-radius: 4px; }
            QSlider::handle:horizontal { background: #00d4ff; width: 18px; border-radius: 9px; }
        """
        self.app.setStyleSheet(dark_style)
    
    def start_backend_server(self):
        """Start backend server in thread"""
        def run_backend():
            try:
                from main_pi5 import run_flask_server
                run_flask_server()
            except Exception as e:
                print(f"Backend server error: {e}")
        
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
    
    def update_system_info(self):
        """Update system information display"""
        try:
            if self.hardware:
                status = self.hardware.get_system_status()
                info_text = f"CPU: {status.get('cpu_percent', 0):.1f}% | RAM: {status.get('memory_percent', 0):.1f}% | Temp: {status.get('cpu_temp', 0):.1f}°C"
            else:
                info_text = "Pi5 hardware not available"
            
            self.system_info_label.setText(info_text)
            
            # Schedule next update
            QTimer.singleShot(5000, self.update_system_info)
        except:
            pass
    
    def start_voice_listening(self):
        """Start voice listening"""
        self.voice_start_btn.setEnabled(False)
        self.voice_stop_btn.setEnabled(True)
        self.status_display.append("🎤 Voice listening started...")
        self.tts_output.speak("Voice recognition activated")
    
    def stop_voice_listening(self):
        """Stop voice listening"""
        self.voice_start_btn.setEnabled(True)
        self.voice_stop_btn.setEnabled(False)
        self.status_display.append("🛑 Voice listening stopped")
    
    def process_text_command(self):
        """Process text command"""
        command = self.command_input.text().strip()
        if command:
            self.status_display.append(f"👤 User: {command}")
            
            # Process with decision engine
            if self.decision_engine:
                response = self.decision_engine.process_command(command)
                self.status_display.append(f"🤖 LYRA: {response.get('message', 'Command processed')}")
                
                # Speak response
                if self.tts_output:
                    self.tts_output.speak(response.get('message', 'Command executed'))
            
            self.command_input.clear()
    
    def change_mode(self, mode):
        """Change operation mode"""
        # Uncheck other buttons
        for btn in self.mode_buttons:
            if btn.text() != mode:
                btn.setChecked(False)
        
        mode_name = mode.split()[1]  # Extract mode name
        self.status_display.append(f"⚙️ Mode changed to: {mode_name}")
        self.tts_output.speak(f"Switched to {mode_name} mode")
    
    def control_trinetra(self, action):
        """Control TRINETRA ground bot"""
        self.status_display.append(f"🚗 TRINETRA: {action}")
        self.tts_output.speak(f"TRINETRA moving {action}")
        
        # GPIO control if available
        if self.hardware and action != "stop":
            # Example GPIO control (customize pins as needed)
            pin_map = {"forward": 18, "backward": 19, "left": 20, "right": 21}
            if action in pin_map:
                self.hardware.control_gpio_pin(pin_map[action], "set_output", True)
                QTimer.singleShot(1000, lambda: self.hardware.control_gpio_pin(pin_map[action], "set_output", False))
    
    def control_krait3(self, action):
        """Control KRAIT-3 UAV"""
        self.status_display.append(f"🚁 KRAIT-3: {action}")
        self.tts_output.speak(f"KRAIT-3 {action}")
    
    def capture_image(self):
        """Capture image from camera"""
        if self.hardware:
            result = self.hardware.capture_camera_image()
            if result.get('status') == 'success':
                self.status_display.append(f"📷 Image captured: {result['filename']}")
                self.tts_output.speak("Image captured successfully")
            else:
                self.status_display.append("❌ Camera capture failed")
        else:
            self.status_display.append("📷 Camera simulation - image captured")
    
    def control_gpio_led(self, pin, state):
        """Control GPIO LED"""
        if self.hardware:
            result = self.hardware.control_gpio_pin(pin, "set_output", state)
            status = "ON" if state else "OFF"
            self.status_display.append(f"💡 LED Pin {pin}: {status}")
        else:
            self.status_display.append(f"💡 LED Pin {pin} simulation: {'ON' if state else 'OFF'}")
    
    def refresh_hardware_info(self):
        """Refresh hardware information"""
        if self.hardware:
            info = self.hardware.get_hardware_info()
            status = self.hardware.get_system_status()
            
            info_text = f"""🍓 Raspberry Pi 5 Hardware Status:
Model: {info.get('model', 'Unknown')}
GPIO: {'✅ Available' if info.get('gpio_available') else '❌ Not available'}
Camera: {'✅ Available' if info.get('camera_available') else '❌ Not available'}
I2C: {'✅ Available' if info.get('i2c_available') else '❌ Not available'}

System Status:
CPU Usage: {status.get('cpu_percent', 0):.1f}%
Memory Usage: {status.get('memory_percent', 0):.1f}%
CPU Temperature: {status.get('cpu_temp', 0):.1f}°C
GPU Temperature: {status.get('gpu_temp', 0):.1f}°C
CPU Frequency: {status.get('cpu_freq', 0):.0f} MHz
"""
            self.hardware_info_display.setPlainText(info_text)
    
    def init_tkinter_app(self):
        """Fallback Tkinter interface"""
        self.root = tk.Tk()
        self.root.title("🤖 LYRA 3.0 - Raspberry Pi 5")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # Main label
        title_label = tk.Label(self.root, text="🤖 LYRA 3.0 - Raspberry Pi 5", 
                              font=('Arial', 16, 'bold'), fg='#00d4ff', bg='#1a1a1a')
        title_label.pack(pady=20)
        
        # Command entry
        self.tk_command_var = tk.StringVar()
        command_entry = tk.Entry(self.root, textvariable=self.tk_command_var, 
                               font=('Arial', 12), width=50)
        command_entry.pack(pady=10)
        command_entry.bind('<Return>', self.tk_process_command)
        
        # Send button
        send_btn = tk.Button(self.root, text="Send Command", 
                           command=self.tk_process_command,
                           font=('Arial', 12), bg='#00d4ff', fg='black')
        send_btn.pack(pady=5)
        
        # Output area
        self.tk_output = tk.Text(self.root, height=15, width=80, 
                               font=('Arial', 10), bg='#2a2a2a', fg='white')
        self.tk_output.pack(pady=10, padx=20)
        
        # Add initial message
        self.tk_output.insert(tk.END, "🍓 LYRA 3.0 Raspberry Pi Edition\n✅ System Online\n🤖 Ready for commands\n\n")
        
        # Open web interface button
        web_btn = tk.Button(self.root, text="🌐 Open Web Interface", 
                          command=self.open_web_interface,
                          font=('Arial', 12), bg='#00ff88', fg='black')
        web_btn.pack(pady=5)
    
    def tk_process_command(self, event=None):
        """Process command in Tkinter interface"""
        command = self.tk_command_var.get().strip()
        if command:
            self.tk_output.insert(tk.END, f"👤 User: {command}\n")
            
            if self.decision_engine:
                response = self.decision_engine.process_command(command)
                self.tk_output.insert(tk.END, f"🤖 LYRA: {response.get('message', 'Command processed')}\n\n")
                
                if self.tts_output:
                    self.tts_output.speak(response.get('message', 'Command executed'))
            
            self.tk_command_var.set("")
            self.tk_output.see(tk.END)
    
    def open_web_interface(self):
        """Open web interface in browser"""
        webbrowser.open('http://localhost:5000')
    
    def run(self):
        """Run the application"""
        try:
            if PYQT_AVAILABLE:
                # Start system tray if available
                if QSystemTrayIcon.isSystemTrayAvailable():
                    self.create_system_tray()
                
                sys.exit(self.app.exec_())
            else:
                self.root.mainloop()
        except KeyboardInterrupt:
            print("\n🛑 LYRA 3.0 shutting down...")
            if self.hardware:
                self.hardware.cleanup()
    
    def create_system_tray(self):
        """Create system tray icon"""
        self.tray_icon = QSystemTrayIcon(self.window)
        self.tray_icon.setIcon(QIcon.fromTheme("computer"))
        
        # Tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show LYRA", self.window)
        show_action.triggered.connect(self.window.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", self.window)
        quit_action.triggered.connect(self.app.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

def main():
    """Main entry point"""
    print("🍓 Starting LYRA 3.0 Native Desktop Application for Pi5...")
    
    app = LyraPi5App()
    app.run()

if __name__ == "__main__":
    main()
