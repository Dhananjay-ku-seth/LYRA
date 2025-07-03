"""
LYRA 3.0 AI Learning System
Handles learning from web APIs and building knowledge base
"""

import logging
import json
import os
import requests
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

class AILearningSystem:
    """
    AI Learning System for LYRA 3.0
    Integrates with free APIs to learn and build knowledge
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.knowledge_base_file = 'data/knowledge_base.json'
        self.learning_enabled = True
        self.knowledge_base = {}
        self.api_configs = {
            'wikipedia': {
                'base_url': 'https://en.wikipedia.org/api/rest_v1/page/summary/',
                'enabled': True
            },
            'openweather': {
                'base_url': 'http://api.openweathermap.org/data/2.5/weather',
                'api_key': None,  # Users can add their own key
                'enabled': False
            },
            'worldbank': {
                'base_url': 'http://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD',
                'enabled': True
            }
        }
        self._load_knowledge_base()
        
    def _load_knowledge_base(self):
        """Load existing knowledge base from file"""
        try:
            os.makedirs(os.path.dirname(self.knowledge_base_file), exist_ok=True)
            if os.path.exists(self.knowledge_base_file):
                with open(self.knowledge_base_file, 'r', encoding='utf-8') as f:
                    self.knowledge_base = json.load(f)
                self.logger.info(f"Loaded knowledge base with {len(self.knowledge_base)} entries")
            else:
                self.knowledge_base = {}
                self.logger.info("Created new knowledge base")
        except Exception as e:
            self.logger.error(f"Failed to load knowledge base: {e}")
            self.knowledge_base = {}
    
    def _save_knowledge_base(self):
        """Save knowledge base to file"""
        try:
            with open(self.knowledge_base_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
            self.logger.debug("Knowledge base saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save knowledge base: {e}")
    
    def search_and_learn(self, query: str) -> Dict[str, Any]:
        """
        Search for information and learn from it
        """
        try:
            # Check if we already know about this
            existing_knowledge = self._search_knowledge_base(query)
            if existing_knowledge:
                self.logger.info(f"Found existing knowledge for: {query}")
                return {
                    'status': 'success',
                    'source': 'knowledge_base',
                    'data': existing_knowledge,
                    'message': f"I already know about {query}. {existing_knowledge.get('summary', '')[:200]}..."
                }
            
            # Search Wikipedia first
            wiki_result = self._search_wikipedia(query)
            if wiki_result and wiki_result['status'] == 'success':
                # Store in knowledge base
                self._store_knowledge(query, wiki_result['data'], 'wikipedia')
                return {
                    'status': 'success',
                    'source': 'wikipedia',
                    'data': wiki_result['data'],
                    'message': f"I learned about {query} from Wikipedia. {wiki_result['data'].get('extract', '')[:200]}..."
                }
            
            # If Wikipedia fails, try other sources
            return {
                'status': 'not_found',
                'message': f"I couldn't find information about '{query}'. Let me remember this query for future learning."
            }
            
        except Exception as e:
            self.logger.error(f"Error in search_and_learn: {e}")
            return {
                'status': 'error',
                'message': f"I encountered an error while searching for '{query}': {str(e)}"
            }
    
    def _search_knowledge_base(self, query: str) -> Optional[Dict[str, Any]]:
        """Search existing knowledge base"""
        query_lower = query.lower()
        
        # Direct match
        if query_lower in self.knowledge_base:
            return self.knowledge_base[query_lower]
        
        # Partial match
        for key, value in self.knowledge_base.items():
            if query_lower in key or key in query_lower:
                return value
        
        return None
    
    def _search_wikipedia(self, query: str) -> Dict[str, Any]:
        """Search Wikipedia for information"""
        try:
            if not self.api_configs['wikipedia']['enabled']:
                return {'status': 'disabled'}
            
            # Clean up query for Wikipedia
            clean_query = query.replace(' ', '_')
            url = f"{self.api_configs['wikipedia']['base_url']}{clean_query}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'success',
                    'data': {
                        'title': data.get('title', ''),
                        'extract': data.get('extract', ''),
                        'summary': data.get('extract', '')[:300] + '...' if len(data.get('extract', '')) > 300 else data.get('extract', ''),
                        'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                        'timestamp': str(datetime.now())
                    }
                }
            else:
                return {'status': 'not_found'}
                
        except Exception as e:
            self.logger.error(f"Wikipedia search error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _store_knowledge(self, query: str, data: Dict[str, Any], source: str):
        """Store learned information in knowledge base"""
        try:
            key = query.lower()
            self.knowledge_base[key] = {
                **data,
                'source': source,
                'learned_at': str(datetime.now()),
                'access_count': 1
            }
            self._save_knowledge_base()
            self.logger.info(f"Stored knowledge about '{query}' from {source}")
        except Exception as e:
            self.logger.error(f"Failed to store knowledge: {e}")
    
    def get_weather_info(self, city: str = "London") -> Dict[str, Any]:
        """Get weather information (requires API key)"""
        try:
            if not self.api_configs['openweather']['enabled'] or not self.api_configs['openweather']['api_key']:
                return {
                    'status': 'disabled',
                    'message': 'Weather API not configured. Please add OpenWeatherMap API key.'
                }
            
            url = self.api_configs['openweather']['base_url']
            params = {
                'q': city,
                'appid': self.api_configs['openweather']['api_key'],
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                weather_info = {
                    'city': data['name'],
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'timestamp': str(datetime.now())
                }
                
                # Store in knowledge base
                self._store_knowledge(f"weather_{city.lower()}", weather_info, 'openweather')
                
                return {
                    'status': 'success',
                    'data': weather_info,
                    'message': f"Current weather in {city}: {weather_info['temperature']}°C, {weather_info['description']}"
                }
            else:
                return {'status': 'not_found', 'message': f"Weather data not found for {city}"}
                
        except Exception as e:
            self.logger.error(f"Weather API error: {e}")
            return {'status': 'error', 'message': f"Weather lookup failed: {str(e)}"}
    
    def learn_from_conversation(self, user_input: str, system_response: str):
        """Learn from user conversations"""
        try:
            conversation_key = f"conversation_{hash(user_input) % 10000}"
            conversation_data = {
                'user_input': user_input,
                'system_response': system_response,
                'timestamp': str(datetime.now()),
                'type': 'conversation'
            }
            
            self.knowledge_base[conversation_key] = conversation_data
            self._save_knowledge_base()
            
        except Exception as e:
            self.logger.error(f"Failed to learn from conversation: {e}")
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            total_entries = len(self.knowledge_base)
            sources = {}
            types = {}
            
            for entry in self.knowledge_base.values():
                source = entry.get('source', 'unknown')
                entry_type = entry.get('type', 'knowledge')
                
                sources[source] = sources.get(source, 0) + 1
                types[entry_type] = types.get(entry_type, 0) + 1
            
            return {
                'total_entries': total_entries,
                'sources': sources,
                'types': types,
                'file_size': os.path.getsize(self.knowledge_base_file) if os.path.exists(self.knowledge_base_file) else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get knowledge stats: {e}")
            return {'error': str(e)}
    
    def configure_api(self, api_name: str, config: Dict[str, Any]):
        """Configure API settings"""
        if api_name in self.api_configs:
            self.api_configs[api_name].update(config)
            self.logger.info(f"Updated configuration for {api_name}")
        else:
            self.logger.warning(f"Unknown API: {api_name}")
    
    def search_local_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Search local knowledge base for relevant information"""
        results = []
        query_lower = query.lower()
        
        for key, value in self.knowledge_base.items():
            # Check if query matches key or content
            if query_lower in key:
                results.append({'key': key, 'relevance': 'high', 'data': value})
            elif isinstance(value, dict):
                # Check in content
                content = str(value).lower()
                if query_lower in content:
                    results.append({'key': key, 'relevance': 'medium', 'data': value})
        
        # Sort by relevance
        results.sort(key=lambda x: 0 if x['relevance'] == 'high' else 1)
        
        return results[:5]  # Return top 5 results
