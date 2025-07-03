"""
LYRA 3.0 Voice Input
Handles voice recognition and processing
"""

import logging
import threading
import time
try:
    import speech_recognition as sr
    import pyaudio
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("Warning: speech_recognition or pyaudio not available. Voice input will be disabled.")

class VoiceInput:
    """
    Handles voice recognition and audio input for LYRA 3.0
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active = False
        self.listening = False
        self.continuous_listening = False
        self.recognizer = None
        self.microphone = None
        self.listen_thread = None
        self.on_speech_callback = None
        self.wake_words = ['hi lyra', 'hey lyra', 'lyra', 'hello lyra', 'hi lira', 'hey lira', 'lira']
        self.command_mode = False
        self._init_speech_recognition()
    
    def _init_speech_recognition(self):
        """Initialize speech recognition components"""
        if SPEECH_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                
                # Adjust for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    
                self.logger.info("Speech recognition initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize speech recognition: {e}")
                self.recognizer = None
                self.microphone = None
        else:
            self.logger.warning("Speech recognition not available")
    
    def set_speech_callback(self, callback):
        """Set callback function for when speech is recognized"""
        self.on_speech_callback = callback
    
    def start_listening(self):
        """Start voice recognition and processing"""
        if not SPEECH_AVAILABLE or not self.recognizer:
            self.logger.warning("Speech recognition not available")
            return
            
        self.active = True
        self.listening = True
        self.logger.info("Voice recognition started")
        
        # Start listening in a separate thread
        self.listen_thread = threading.Thread(target=self._listen_continuously)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
    def stop_listening(self):
        """Stop voice recognition"""
        self.active = False
        self.listening = False
        self.logger.info("Voice recognition stopped")
        
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2)
    
    def _listen_continuously(self):
        """Continuously listen for speech with wake word detection"""
        while self.listening and self.active:
            try:
                with self.microphone as source:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Try to recognize speech
                try:
                    text = self.recognizer.recognize_google(audio)
                    self.logger.info(f"Recognized speech: {text}")
                    
                    # Check for wake words or if already in command mode
                    if self._contains_wake_word(text.lower()):
                        self.logger.info(f"Wake word detected in: {text}")
                        self.command_mode = True
                        # Remove wake word from command
                        command = self._remove_wake_words(text.lower()).strip()
                        if command:  # If there's a command after wake word
                            self.logger.info(f"Processing command: {command}")
                            if self.on_speech_callback:
                                self.on_speech_callback(command)
                        else:
                            # Just wake word, send greeting
                            self.logger.info("Wake word detected, sending greeting")
                            if self.on_speech_callback:
                                self.on_speech_callback("wake_word_greeting")
                    elif self.command_mode:
                        # Already in command mode, process the command
                        self.logger.info(f"Command mode active, processing: {text}")
                        if self.on_speech_callback:
                            self.on_speech_callback(text)
                        # Exit command mode after processing
                        self.command_mode = False
                    elif not self.continuous_listening:
                        # If not in continuous mode, process all speech
                        if self.on_speech_callback:
                            self.on_speech_callback(text)
                    
                except sr.UnknownValueError:
                    # Speech was unintelligible
                    pass
                except sr.RequestError as e:
                    self.logger.error(f"Speech recognition error: {e}")
                    
            except sr.WaitTimeoutError:
                # No speech detected, continue listening
                pass
            except Exception as e:
                self.logger.error(f"Listening error: {e}")
                time.sleep(1)
    
    def _contains_wake_word(self, text):
        """Check if text contains wake words"""
        return any(wake_word in text for wake_word in self.wake_words)
    
    def _remove_wake_words(self, text):
        """Remove wake words from text to get the actual command"""
        for wake_word in self.wake_words:
            text = text.replace(wake_word, '').strip()
        return text
    
    def start_continuous_listening(self):
        """Start continuous listening with wake word detection"""
        self.continuous_listening = True
        self.start_listening()
        self.logger.info("Continuous listening started with wake word detection")
    
    def stop_continuous_listening(self):
        """Stop continuous listening"""
        self.continuous_listening = False
        self.command_mode = False
        self.stop_listening()
        self.logger.info("Continuous listening stopped")
    
    def process_audio_data(self, audio_data):
        """Process audio data for speech-to-text"""
        if not self.active:
            self.logger.warning("Voice recognition is not active")
            return ''
        
        if not SPEECH_AVAILABLE or not self.recognizer:
            return ''
            
        try:
            # Convert audio data to text using Google Speech Recognition
            text = self.recognizer.recognize_google(audio_data)
            self.logger.debug(f"Processed audio data to text: {text}")
            return text
        except sr.UnknownValueError:
            self.logger.debug("Could not understand audio")
            return ''
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition service error: {e}")
            return ''
    
    def is_listening(self):
        """Check if currently listening"""
        return self.listening and self.active

