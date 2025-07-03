"""
LYRA 3.0 TTS Output
Handles text-to-speech and voice output
"""

import logging
import threading
import queue
import time
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("Warning: pyttsx3 not available. TTS will be disabled.")

class TTSOutput:
    """
    Handles text-to-speech and voice output for LYRA 3.0
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.voice_settings = {
            'rate': 150,  # Words per minute
            'volume': 0.9,  # Volume level (0.0 to 1.0)
            'voice': 'default'  # Voice type
        }
        self.engine = None
        self.speaking = False
        self.speech_queue = queue.Queue()
        self.worker_thread = None
        self.running = True
        self._init_tts_engine()
        self._start_worker_thread()
    
    def _init_tts_engine(self):
        """Initialize TTS engine"""
        if TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', self.voice_settings['rate'])
                self.engine.setProperty('volume', self.voice_settings['volume'])
                
                # Set to a female voice if available
                voices = self.engine.getProperty('voices')
                if voices:
                    # Try to find a female voice
                    for voice in voices:
                        if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                            self.engine.setProperty('voice', voice.id)
                            break
                    else:
                        # Use the first available voice
                        self.engine.setProperty('voice', voices[0].id)
                
                self.logger.info("TTS engine initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize TTS engine: {e}")
                self.engine = None
        else:
            self.logger.warning("TTS not available - pyttsx3 not installed")
    
    def _start_worker_thread(self):
        """Start the TTS worker thread"""
        self.worker_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.worker_thread.start()
        
    def _tts_worker(self):
        """Worker thread that processes TTS queue"""
        while self.running:
            try:
                # Get text from queue with timeout
                text = self.speech_queue.get(timeout=1)
                
                if text is None:  # Shutdown signal
                    break
                    
                if self.engine and TTS_AVAILABLE:
                    try:
                        self.speaking = True
                        self.engine.say(text)
                        self.engine.runAndWait()
                        self.speaking = False
                        self.logger.debug(f"TTS completed for: {text[:50]}...")
                    except Exception as e:
                        self.logger.error(f"TTS worker error: {e}")
                        self.speaking = False
                        print(f"🎙️ LYRA: {text}")  # Fallback to console
                else:
                    print(f"🎙️ LYRA: {text}")  # Console output fallback
                    
                self.speech_queue.task_done()
                
            except queue.Empty:
                # No speech to process, continue
                continue
            except Exception as e:
                self.logger.error(f"TTS worker thread error: {e}")
                time.sleep(0.1)
    
    def speak(self, text: str, priority: str = 'normal'):
        """Convert text to speech and play it"""
        if not text:
            return
        
        self.logger.info(f"Speaking: {text}")
        
        try:
            # Add text to speech queue
            if priority == 'high':
                # For high priority, clear queue and add immediately
                while not self.speech_queue.empty():
                    try:
                        self.speech_queue.get_nowait()
                        self.speech_queue.task_done()
                    except queue.Empty:
                        break
            
            self.speech_queue.put(text)
            
        except Exception as e:
            self.logger.error(f"TTS queue error: {e}")
            print(f"🎙️ LYRA: {text}")  # Fallback to console
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.engine and TTS_AVAILABLE:
            try:
                self.engine.stop()
            except:
                pass
        
        # Clear queue
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break
    
    def shutdown(self):
        """Shutdown TTS system"""
        self.running = False
        self.speech_queue.put(None)  # Signal worker to stop
        if self.worker_thread:
            self.worker_thread.join(timeout=2)
    
    def set_voice_settings(self, settings: dict):
        """Update voice settings"""
        self.voice_settings.update(settings)
        self.logger.debug(f"Voice settings updated: {self.voice_settings}")
    
    def get_voice_settings(self) -> dict:
        """Get current voice settings"""
        return self.voice_settings.copy()
