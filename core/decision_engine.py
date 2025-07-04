"""
LYRA 3.0 Decision Engine
Core AI logic for processing commands and making decisions

This module implements the Logical Yielding Response Algorithm (LYRA) Decision Engine,
which serves as the brain of the LYRA 3.0 system. It handles:
- Natural language processing for command interpretation
- Intent recognition using regex patterns
- Response generation for different command categories
- Integration with AI learning system for knowledge queries
- Device control commands for TRINETRA (UGV) and KRAIT-3 (UAV)
- System management and status reporting

The engine processes commands through a pipeline:
1. Command normalization (cleanup and standardization)
2. Intent extraction (categorization of command type)
3. Entity extraction (parameters, numbers, coordinates, etc.)
4. Response generation based on intent and entities
5. Optional learning system integration for knowledge retention
"""

import logging
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from .ai_learning import AILearningSystem

class DecisionEngine:
    """
    Logical Yielding Response Algorithm (LYRA) Decision Engine
    Handles command processing, intent recognition, and response generation
    """
    
    def __init__(self, context_manager):
        self.context_manager = context_manager
        self.logger = logging.getLogger(__name__)
        self.command_patterns = self._load_command_patterns()
        self.learning_enabled = True
        self.ai_learning = AILearningSystem()
        
    def _load_command_patterns(self) -> Dict[str, Any]:
        """Load command patterns for NLP processing"""
        return {
            'system_control': {
                'patterns': [
                    r'(?:status|health|system|check)',
                    r'(?:temperature|cpu|memory|disk)',
                    r'(?:mode|switch|change).+(?:defense|home|night|manual)'
                ],
                'actions': ['get_system_status', 'change_mode', 'system_check']
            },
            'trinetra_control': {
                'patterns': [
                    r'(?:trinetra|ground|bot|ugv)',
                    r'(?:move|forward|backward|left|right|stop)',
                    r'(?:camera|stream|snapshot|record)',
                    r'(?:patrol|scout|search)',
                    r'(?:sensor|gas|fire|motion)'
                ],
                'actions': ['trinetra_move', 'trinetra_camera', 'trinetra_mission', 'trinetra_sensors']
            },
            'krait3_control': {
                'patterns': [
                    r'(?:krait|uav|drone|air|fly)',
                    r'(?:launch|takeoff|land|hover|return)',
                    r'(?:altitude|height|up|down)',
                    r'(?:waypoint|navigate|goto|coordinates)',
                    r'(?:mission|reconnaissance|surveillance)'
                ],
                'actions': ['krait3_flight', 'krait3_navigation', 'krait3_mission']
            },
            'voice_control': {
                'patterns': [
                    r'(?:listen|start|voice|speech)',
                    r'(?:stop|quiet|silence)',
                    r'(?:repeat|say|speak)',
                    r'(?:volume|loud|quiet)'
                ],
                'actions': ['voice_start', 'voice_stop', 'voice_repeat', 'voice_volume']
            },
            'general': {
                'patterns': [
                    r'(?:hello|hi|hey|greetings)',
                    r'(?:help|assist|support)',
                    r'(?:thank|thanks)',
                    r'(?:goodbye|bye|exit|quit)'
                ],
                'actions': ['greeting', 'help', 'acknowledge', 'goodbye']
            }
        }
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process a command using LYRA's decision engine
        
        Args:
            command: Text command to process
            
        Returns:
            Dictionary containing response and actions
        """
        try:
            self.logger.info(f"Processing command: {command}")
            
            # Normalize command
            normalized_command = self._normalize_command(command)
            
            # Extract intent and entities
            intent = self._extract_intent(normalized_command)
            entities = self._extract_entities(normalized_command)
            
            # Generate response based on intent
            response = self._generate_response(intent, entities, normalized_command)
            
            # Log for learning
            if self.learning_enabled:
                self._log_interaction(command, intent, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            return {
                'status': 'error',
                'message': 'Command processing failed',
                'error': str(e),
                'timestamp': str(datetime.now())
            }
    
    def _normalize_command(self, command: str) -> str:
        """Normalize command text for processing"""
        # Convert to lowercase
        normalized = command.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove punctuation (except for important ones)
        normalized = re.sub(r'[^\w\s\-\.]', '', normalized)
        
        return normalized
    
    def _extract_intent(self, command: str) -> str:
        """Extract intent from normalized command"""
        for intent_category, data in self.command_patterns.items():
            for pattern in data['patterns']:
                if re.search(pattern, command, re.IGNORECASE):
                    self.logger.debug(f"Intent matched: {intent_category}")
                    return intent_category
        
        return 'general'
    
    def _extract_entities(self, command: str) -> Dict[str, Any]:
        """Extract entities from command"""
        entities = {}
        
        # Extract numbers
        numbers = re.findall(r'\d+', command)
        if numbers:
            entities['numbers'] = [int(n) for n in numbers]
        
        # Extract directions
        directions = re.findall(r'(?:forward|backward|left|right|up|down|north|south|east|west)', command)
        if directions:
            entities['directions'] = directions
        
        # Extract coordinates
        coords = re.findall(r'(-?\d+\.?\d*),\s*(-?\d+\.?\d*)', command)
        if coords:
            entities['coordinates'] = [(float(lat), float(lon)) for lat, lon in coords]
        
        return entities
    
    def _generate_response(self, intent: str, entities: Dict[str, Any], command: str) -> Dict[str, Any]:
        """Generate response based on intent and entities"""
        
        if intent == 'system_control':
            return self._handle_system_control(entities, command)
        
        elif intent == 'trinetra_control':
            return self._handle_trinetra_control(entities, command)
        
        elif intent == 'krait3_control':
            return self._handle_krait3_control(entities, command)
        
        elif intent == 'voice_control':
            return self._handle_voice_control(entities, command)
        
        elif intent == 'general':
            return self._handle_general(entities, command)
        
        else:
            return {
                'status': 'unknown',
                'message': 'Intent not recognized',
                'intent': intent,
                'suggestion': 'Try asking for help or status',
                'timestamp': str(datetime.now())
            }
    
    def _handle_system_control(self, entities: Dict[str, Any], command: str) -> Dict[str, Any]:
        """Handle system control commands"""
        if 'status' in command or 'health' in command:
            return {
                'status': 'success',
                'action': 'get_system_status',
                'message': 'Retrieving system status',
                'timestamp': str(datetime.now())
            }
        
        elif 'mode' in command:
            mode = None
            if 'defense' in command:
                mode = 'defense'
            elif 'home' in command:
                mode = 'home'
            elif 'night' in command:
                mode = 'night'
            elif 'manual' in command:
                mode = 'manual'
            
            if mode:
                return {
                    'status': 'success',
                    'action': 'change_mode',
                    'data': {'mode': mode},
                    'message': f'Switching to {mode} mode',
                    'timestamp': str(datetime.now())
                }
        
        return {
            'status': 'success',
            'action': 'system_check',
            'message': 'System check initiated',
            'timestamp': str(datetime.now())
        }
    
    def _handle_trinetra_control(self, entities: Dict[str, Any], command: str) -> Dict[str, Any]:
        """Handle TRINETRA ground bot commands"""
        if any(move in command for move in ['move', 'forward', 'backward', 'left', 'right']):
            direction = None
            if 'forward' in command:
                direction = 'forward'
            elif 'backward' in command:
                direction = 'backward'
            elif 'left' in command:
                direction = 'left'
            elif 'right' in command:
                direction = 'right'
            elif 'stop' in command:
                direction = 'stop'
            
            return {
                'status': 'success',
                'action': 'trinetra_move',
                'data': {'direction': direction},
                'message': f'TRINETRA moving {direction}',
                'timestamp': str(datetime.now())
            }
        
        elif any(cam in command for cam in ['camera', 'stream', 'snapshot']):
            return {
                'status': 'success',
                'action': 'trinetra_camera',
                'data': {'action': 'snapshot' if 'snapshot' in command else 'stream'},
                'message': 'TRINETRA camera activated',
                'timestamp': str(datetime.now())
            }
        
        elif 'patrol' in command:
            return {
                'status': 'success',
                'action': 'trinetra_mission',
                'data': {'mission': 'patrol'},
                'message': 'TRINETRA patrol mode activated',
                'timestamp': str(datetime.now())
            }
        
        return {
            'status': 'success',
            'action': 'trinetra_status',
            'message': 'TRINETRA status requested',
            'timestamp': str(datetime.now())
        }
    
    def _handle_krait3_control(self, entities: Dict[str, Any], command: str) -> Dict[str, Any]:
        """Handle KRAIT-3 UAV commands"""
        if any(flight in command for flight in ['launch', 'takeoff', 'land', 'hover', 'return']):
            action = None
            if 'launch' in command or 'takeoff' in command:
                action = 'takeoff'
            elif 'land' in command:
                action = 'land'
            elif 'hover' in command:
                action = 'hover'
            elif 'return' in command:
                action = 'return'
            
            return {
                'status': 'success',
                'action': 'krait3_flight',
                'data': {'action': action},
                'message': f'KRAIT-3 {action} command executed',
                'timestamp': str(datetime.now())
            }
        
        elif 'waypoint' in command or 'navigate' in command:
            coords = entities.get('coordinates', [])
            return {
                'status': 'success',
                'action': 'krait3_navigation',
                'data': {'coordinates': coords},
                'message': 'KRAIT-3 navigation initiated',
                'timestamp': str(datetime.now())
            }
        
        return {
            'status': 'success',
            'action': 'krait3_status',
            'message': 'KRAIT-3 status requested',
            'timestamp': str(datetime.now())
        }
    
    def _handle_voice_control(self, entities: Dict[str, Any], command: str) -> Dict[str, Any]:
        """Handle voice control commands"""
        if 'listen' in command or 'start' in command:
            return {
                'status': 'success',
                'action': 'voice_start',
                'message': 'Voice recognition started',
                'timestamp': str(datetime.now())
            }
        
        elif 'stop' in command or 'quiet' in command:
            return {
                'status': 'success',
                'action': 'voice_stop',
                'message': 'Voice recognition stopped',
                'timestamp': str(datetime.now())
            }
        
        return {
            'status': 'success',
            'action': 'voice_status',
            'message': 'Voice system status',
            'timestamp': str(datetime.now())
        }
    
    def _handle_general(self, entities: Dict[str, Any], command: str) -> Dict[str, Any]:
        """Handle general commands with AI learning integration"""
        if any(greeting in command for greeting in ['hello', 'hi', 'hey']):
            return {
                'status': 'success',
                'action': 'greeting',
                'message': 'Hello Commander. LYRA 3.0 is ready for your commands.',
                'timestamp': str(datetime.now())
            }
        
        elif 'help' in command:
            return {
                'status': 'success',
                'action': 'help',
                'message': 'Available commands: system status, TRINETRA control, KRAIT-3 control, voice commands, ask about anything',
                'commands': [
                    'system status - Get system health',
                    'TRINETRA move forward - Control ground bot',
                    'KRAIT-3 launch - Control UAV',
                    'start listening - Voice recognition',
                    'what is [topic] - Learn about topics',
                    'weather in [city] - Get weather info',
                    'knowledge stats - See what I have learned'
                ],
                'timestamp': str(datetime.now())
            }
        
        elif any(thanks in command for thanks in ['thank', 'thanks']):
            return {
                'status': 'success',
                'action': 'acknowledge',
                'message': 'You are welcome, Commander.',
                'timestamp': str(datetime.now())
            }
        
        elif any(bye in command for bye in ['goodbye', 'bye', 'exit']):
            return {
                'status': 'success',
                'action': 'goodbye',
                'message': 'Goodbye Commander. LYRA 3.0 standing by.',
                'timestamp': str(datetime.now())
            }
        
        # AI Learning integration for questions
        elif any(question in command for question in ['what is', 'tell me about', 'explain', 'who is', 'where is']):
            return self._handle_knowledge_query(command)
        
        elif 'weather' in command:
            return self._handle_weather_query(command)
        
        elif 'knowledge stats' in command or 'what do you know' in command:
            return self._handle_knowledge_stats()
        
        # Try to find answer in knowledge base
        search_results = self.ai_learning.search_local_knowledge(command)
        if search_results:
            best_result = search_results[0]
            return {
                'status': 'success',
                'action': 'knowledge_recall',
                'message': f"I found this in my knowledge base: {best_result['data'].get('summary', str(best_result['data'])[:200])}",
                'data': best_result['data'],
                'timestamp': str(datetime.now())
            }
        
        return {
            'status': 'success',
            'action': 'default',
            'message': 'Command received. I can help with system control, or you can ask me questions to help me learn.',
            'suggestion': 'Try asking "what is artificial intelligence" or "help" for available commands',
            'timestamp': str(datetime.now())
        }
    
    def _handle_knowledge_query(self, command: str) -> Dict[str, Any]:
        """Handle knowledge queries using AI learning system"""
        # Extract the topic from the command
        topic = command.lower()
        for prefix in ['what is', 'tell me about', 'explain', 'who is', 'where is']:
            if prefix in topic:
                topic = topic.replace(prefix, '').strip()
                break
        
        if not topic:
            return {
                'status': 'error',
                'message': 'Please specify what you would like to know about.',
                'timestamp': str(datetime.now())
            }
        
        # Search and learn about the topic
        result = self.ai_learning.search_and_learn(topic)
        
        # Learn from this conversation
        self.ai_learning.learn_from_conversation(command, result.get('message', ''))
        
        return {
            'status': result['status'],
            'action': 'knowledge_query',
            'message': result['message'],
            'data': result.get('data', {}),
            'source': result.get('source', 'unknown'),
            'timestamp': str(datetime.now())
        }
    
    def _handle_weather_query(self, command: str) -> Dict[str, Any]:
        """Handle weather queries"""
        # Extract city from command
        city = 'London'  # Default
        words = command.split()
        if 'in' in words:
            try:
                city_index = words.index('in') + 1
                if city_index < len(words):
                    city = words[city_index]
            except:
                pass
        
        result = self.ai_learning.get_weather_info(city)
        
        return {
            'status': result['status'],
            'action': 'weather_query',
            'message': result['message'],
            'data': result.get('data', {}),
            'timestamp': str(datetime.now())
        }
    
    def _handle_knowledge_stats(self) -> Dict[str, Any]:
        """Handle knowledge statistics query"""
        stats = self.ai_learning.get_knowledge_stats()
        
        if 'error' in stats:
            message = f"Error getting knowledge stats: {stats['error']}"
        else:
            message = f"I have learned {stats['total_entries']} things so far. Sources: {', '.join(stats['sources'].keys()) if stats['sources'] else 'None yet'}."
        
        return {
            'status': 'success',
            'action': 'knowledge_stats',
            'message': message,
            'data': stats,
            'timestamp': str(datetime.now())
        }
    
    def _log_interaction(self, command: str, intent: str, response: Dict[str, Any]):
        """Log interaction for learning purposes"""
        interaction = {
            'command': command,
            'intent': intent,
            'response': response,
            'timestamp': str(datetime.now())
        }
        
        # This would typically save to a database or learning system
        self.logger.debug(f"Logged interaction: {interaction}")
    
    def add_custom_pattern(self, category: str, pattern: str, action: str):
        """Add custom command pattern for learning"""
        if category not in self.command_patterns:
            self.command_patterns[category] = {'patterns': [], 'actions': []}
        
        self.command_patterns[category]['patterns'].append(pattern)
        if action not in self.command_patterns[category]['actions']:
            self.command_patterns[category]['actions'].append(action)
        
        self.logger.info(f"Added custom pattern: {category} - {pattern}")
    
    def enable_learning(self, enabled: bool = True):
        """Enable or disable learning mode"""
        self.learning_enabled = enabled
        self.logger.info(f"Learning mode: {'enabled' if enabled else 'disabled'}")
