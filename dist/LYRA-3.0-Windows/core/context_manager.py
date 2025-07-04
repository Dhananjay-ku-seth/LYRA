"""
LYRA 3.0 Context Manager
Manages system context, state, and memory
"""

import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

class ContextManager:
    """
    Manages system context, state, and memory for LYRA 3.0
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_mode = 'home'
        self.system_state = {}
        self.conversation_history = []
        self.user_preferences = {}
        self.device_states = {
            'trinetra': {'connected': False, 'status': 'offline'},
            'krait3': {'connected': False, 'status': 'offline'}
        }
        self.session_start_time = datetime.now()
        self.last_activity = datetime.now()
        
        # Load persistent data
        self._load_context()
        
    def _load_context(self):
        """Load context data from storage"""
        try:
            context_file = 'config/context.json'
            if os.path.exists(context_file):
                with open(context_file, 'r') as f:
                    data = json.load(f)
                    self.user_preferences = data.get('user_preferences', {})
                    self.device_states = data.get('device_states', self.device_states)
                    self.logger.info("Context loaded successfully")
        except Exception as e:
            self.logger.warning(f"Could not load context: {e}")
    
    def save_context(self):
        """Save context data to storage"""
        try:
            os.makedirs('config', exist_ok=True)
            context_data = {
                'user_preferences': self.user_preferences,
                'device_states': self.device_states,
                'last_saved': str(datetime.now())
            }
            
            with open('config/context.json', 'w') as f:
                json.dump(context_data, f, indent=4)
                
            self.logger.debug("Context saved successfully")
        except Exception as e:
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
