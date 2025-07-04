"""
LYRA 3.0 Mode Manager
Handles different operational modes (Home, Defense, Night, Manual)
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

class ModeManager:
    """
    Manages LYRA 3.0 operational modes
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_mode = 'home'
        self.mode_configs = {
            'home': {
                'name': 'Home Mode',
                'description': 'Standard home automation and assistance',
                'voice_sensitivity': 0.7,
                'auto_responses': True,
                'security_level': 'low',
                'features': ['voice_control', 'web_search', 'smart_home', 'entertainment']
            },
            'defense': {
                'name': 'Defense Mode',
                'description': 'High security and surveillance mode',
                'voice_sensitivity': 0.9,
                'auto_responses': False,
                'security_level': 'high',
                'features': ['voice_control', 'surveillance', 'intrusion_detection', 'emergency_alerts']
            },
            'night': {
                'name': 'Night Mode',
                'description': 'Quiet mode with reduced responsiveness',
                'voice_sensitivity': 0.5,
                'auto_responses': False,
                'security_level': 'medium',
                'features': ['voice_control', 'emergency_only', 'quiet_responses']
            },
            'manual': {
                'name': 'Manual Mode',
                'description': 'Direct control mode with minimal automation',
                'voice_sensitivity': 0.8,
                'auto_responses': False,
                'security_level': 'medium',
                'features': ['voice_control', 'manual_control', 'system_monitoring']
            }
        }
        self.mode_history = []
        
    def set_mode(self, mode: str) -> Dict[str, Any]:
        """Set the operational mode"""
        if mode not in self.mode_configs:
            return {
                'status': 'error',
                'message': f'Unknown mode: {mode}. Available modes: {list(self.mode_configs.keys())}'
            }
        
        previous_mode = self.current_mode
        self.current_mode = mode
        
        # Log mode change
        self.mode_history.append({
            'from_mode': previous_mode,
            'to_mode': mode,
            'timestamp': str(datetime.now())
        })
        
        self.logger.info(f"Mode changed from {previous_mode} to {mode}")
        
        return {
            'status': 'success',
            'message': f'Switched to {self.mode_configs[mode]["name"]}',
            'previous_mode': previous_mode,
            'current_mode': mode,
            'mode_config': self.mode_configs[mode]
        }
    
    def get_current_mode(self) -> Dict[str, Any]:
        """Get current mode information"""
        return {
            'current_mode': self.current_mode,
            'config': self.mode_configs[self.current_mode],
            'timestamp': str(datetime.now())
        }
    
    def get_all_modes(self) -> Dict[str, Any]:
        """Get all available modes"""
        return {
            'modes': self.mode_configs,
            'current_mode': self.current_mode
        }
    
    def get_mode_features(self, mode: Optional[str] = None) -> list:
        """Get features available in a specific mode"""
        target_mode = mode or self.current_mode
        if target_mode in self.mode_configs:
            return self.mode_configs[target_mode]['features']
        return []
    
    def is_feature_available(self, feature: str, mode: Optional[str] = None) -> bool:
        """Check if a feature is available in the current or specified mode"""
        target_mode = mode or self.current_mode
        features = self.get_mode_features(target_mode)
        return feature in features
    
    def get_voice_sensitivity(self, mode: Optional[str] = None) -> float:
        """Get voice sensitivity for the current or specified mode"""
        target_mode = mode or self.current_mode
        if target_mode in self.mode_configs:
            return self.mode_configs[target_mode]['voice_sensitivity']
        return 0.7  # Default
    
    def should_auto_respond(self, mode: Optional[str] = None) -> bool:
        """Check if auto responses are enabled in the current or specified mode"""
        target_mode = mode or self.current_mode
        if target_mode in self.mode_configs:
            return self.mode_configs[target_mode]['auto_responses']
        return True  # Default
    
    def get_security_level(self, mode: Optional[str] = None) -> str:
        """Get security level for the current or specified mode"""
        target_mode = mode or self.current_mode
        if target_mode in self.mode_configs:
            return self.mode_configs[target_mode]['security_level']
        return 'medium'  # Default
    
    def get_mode_recommendations(self, time_of_day: Optional[str] = None) -> Dict[str, Any]:
        """Get mode recommendations based on time of day or other factors"""
        recommendations = []
        
        if time_of_day:
            hour = int(time_of_day.split(':')[0]) if ':' in time_of_day else 12
            
            if 22 <= hour or hour <= 6:  # Night time
                recommendations.append({
                    'mode': 'night',
                    'reason': 'Night time - reduced sensitivity recommended'
                })
            elif 8 <= hour <= 18:  # Day time
                recommendations.append({
                    'mode': 'home',
                    'reason': 'Daytime - standard home mode recommended'
                })
        
        return {
            'current_mode': self.current_mode,
            'recommendations': recommendations,
            'timestamp': str(datetime.now())
        }
    
    def get_mode_history(self, limit: int = 10) -> list:
        """Get recent mode change history"""
        return self.mode_history[-limit:] if self.mode_history else []
    
    def customize_mode(self, mode: str, config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Customize mode configuration"""
        if mode not in self.mode_configs:
            return {
                'status': 'error',
                'message': f'Mode {mode} not found'
            }
        
        # Update configuration
        for key, value in config_updates.items():
            if key in self.mode_configs[mode]:
                self.mode_configs[mode][key] = value
                self.logger.info(f"Updated {mode} mode: {key} = {value}")
        
        return {
            'status': 'success',
            'message': f'Mode {mode} customized successfully',
            'updated_config': self.mode_configs[mode]
        }
