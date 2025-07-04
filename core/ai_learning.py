"""
LYRA 3.0 AI Learning System
Handles learning from web APIs and building knowledge base

This module provides LYRA with the ability to:
- Learn new information from external APIs (Wikipedia, OpenWeatherMap, etc.)
- Build and maintain a local knowledge base
- Search and retrieve stored knowledge
- Learn from conversations and user interactions
- Provide statistics and insights about learned knowledge
"""

# Core Python libraries for functionality
import logging          # For system logging and debugging
import json            # For JSON data handling and storage
import os              # For file system operations
import requests        # For HTTP API calls to external services
import time            # For timing and delays (if needed)
from datetime import datetime  # For timestamping learned information
from typing import Dict, Any, List, Optional  # For type hints and better code clarity

class AILearningSystem:
    """
    AI Learning System for LYRA 3.0
    
    This class provides LYRA with intelligent learning capabilities by:
    - Integrating with free external APIs (Wikipedia, OpenWeatherMap, WorldBank)
    - Building and maintaining a persistent local knowledge base
    - Learning from user conversations and storing context
    - Providing search functionality across stored knowledge
    - Managing API configurations and rate limiting
    
    The system is designed to work offline-first, using cached knowledge when
    available and only reaching out to external APIs when new information is needed.
    """
    
    def __init__(self):
        """
        Initialize the AI Learning System
        
        Sets up:
        - Logger for debugging and monitoring
        - Knowledge base file path and storage
        - API configurations for external services
        - Loads existing knowledge from persistent storage
        """
        # Initialize logging for this component
        self.logger = logging.getLogger(__name__)
        
        # File path for persistent knowledge storage
        self.knowledge_base_file = 'data/knowledge_base.json'
        
        # Global flag to enable/disable learning functionality
        self.learning_enabled = True
        
        # In-memory knowledge base dictionary
        self.knowledge_base = {}
        
        # Configuration for external API services
        self.api_configs = {
            'wikipedia': {
                'base_url': 'https://en.wikipedia.org/api/rest_v1/page/summary/',
                'enabled': True  # Free API, no key required
            },
            'openweather': {
                'base_url': 'http://api.openweathermap.org/data/2.5/weather',
                'api_key': None,  # Users can add their own key
                'enabled': False  # Disabled until API key is provided
            },
            'worldbank': {
                'base_url': 'http://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD',
                'enabled': True  # Free API for economic data
            }
        }
        
        # Load any existing knowledge from persistent storage
        self._load_knowledge_base()
        
    def _load_knowledge_base(self):
        """
        Load existing knowledge base from persistent storage file
        
        This method:
        - Creates the data directory if it doesn't exist
        - Loads the JSON knowledge base file if it exists
        - Initializes an empty knowledge base if no file exists
        - Handles any file system or JSON parsing errors gracefully
        
        The knowledge base is stored as a JSON file for human readability
        and easy debugging/inspection of learned information.
        """
        try:
            # Ensure the data directory exists for storing knowledge base
            os.makedirs(os.path.dirname(self.knowledge_base_file), exist_ok=True)
            
            # Check if knowledge base file already exists
            if os.path.exists(self.knowledge_base_file):
                # Load existing knowledge from JSON file
                with open(self.knowledge_base_file, 'r', encoding='utf-8') as f:
                    self.knowledge_base = json.load(f)
                # Log successful loading with entry count
                self.logger.info(f"Loaded knowledge base with {len(self.knowledge_base)} entries")
            else:
                # Initialize empty knowledge base for new installation
                self.knowledge_base = {}
                self.logger.info("Created new knowledge base")
        except Exception as e:
            # Handle any errors in file operations or JSON parsing
            self.logger.error(f"Failed to load knowledge base: {e}")
            # Fallback to empty knowledge base to prevent system failure
            self.knowledge_base = {}
    
    def _save_knowledge_base(self):
        """
        Save current knowledge base to persistent storage file
        
        This method:
        - Writes the in-memory knowledge base to a JSON file
        - Uses UTF-8 encoding to support international characters
        - Formats JSON with indentation for human readability
        - Handles any file system errors gracefully
        
        The knowledge base is saved after each learning operation
        to ensure data persistence across system restarts.
        """
        try:
            # Write knowledge base to JSON file with proper formatting
            with open(self.knowledge_base_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
            # Log successful save operation
            self.logger.debug("Knowledge base saved successfully")
        except Exception as e:
            # Log any errors during save operation
            self.logger.error(f"Failed to save knowledge base: {e}")
    
    def search_and_learn(self, query: str) -> Dict[str, Any]:
        """
        Primary method for searching and learning new information
        
        This method implements LYRA's core learning behavior:
        1. First checks local knowledge base for existing information
        2. If not found locally, searches external APIs (Wikipedia first)
        3. Stores newly learned information in the knowledge base
        4. Returns structured response with status and learned data
        
        Args:
            query (str): The search query or topic to learn about
            
        Returns:
            Dict[str, Any]: Structured response containing:
                - status: 'success', 'not_found', or 'error'
                - source: Where the information came from
                - data: The actual learned information
                - message: Human-readable summary for the user
        """
        try:
            # First, check if we already have knowledge about this topic
            existing_knowledge = self._search_knowledge_base(query)
            if existing_knowledge:
                self.logger.info(f"Found existing knowledge for: {query}")
                return {
                    'status': 'success',
                    'source': 'knowledge_base',
                    'data': existing_knowledge,
                    'message': f"I already know about {query}. {existing_knowledge.get('summary', '')[:200]}..."
                }
            
            # If not in local knowledge, search Wikipedia as primary source
            wiki_result = self._search_wikipedia(query)
            if wiki_result and wiki_result['status'] == 'success':
                # Store newly learned information in knowledge base
                self._store_knowledge(query, wiki_result['data'], 'wikipedia')
                return {
                    'status': 'success',
                    'source': 'wikipedia',
                    'data': wiki_result['data'],
                    'message': f"I learned about {query} from Wikipedia. {wiki_result['data'].get('extract', '')[:200]}..."
                }
            
            # If Wikipedia search fails, return not found status
            # In future versions, this could try other APIs
            return {
                'status': 'not_found',
                'message': f"I couldn't find information about '{query}'. Let me remember this query for future learning."
            }
            
        except Exception as e:
            # Handle any unexpected errors during the search process
            self.logger.error(f"Error in search_and_learn: {e}")
            return {
                'status': 'error',
                'message': f"I encountered an error while searching for '{query}': {str(e)}"
            }
    
    def _search_knowledge_base(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Search the local knowledge base for existing information
        
        This method implements a two-tier search strategy:
        1. First tries exact key matching (case-insensitive)
        2. Then tries partial matching in both directions
        
        Args:
            query (str): The search query to look for
            
        Returns:
            Optional[Dict[str, Any]]: The knowledge entry if found, None otherwise
        """
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()
        
        # First attempt: Direct/exact match in knowledge base keys
        if query_lower in self.knowledge_base:
            return self.knowledge_base[query_lower]
        
        # Second attempt: Partial matching in both directions
        # This catches cases where the query is a substring of a stored key
        # or where a stored key is a substring of the query
        for key, value in self.knowledge_base.items():
            if query_lower in key or key in query_lower:
                return value
        
        # No match found in knowledge base
        return None
    
    def _search_wikipedia(self, query: str) -> Dict[str, Any]:
        """
        Search Wikipedia for information using their REST API
        
        This method:
        - Uses Wikipedia's REST API v1 for page summaries
        - Converts search queries to Wikipedia-compatible format
        - Extracts key information (title, summary, URL)
        - Handles HTTP errors and timeouts gracefully
        - Returns structured data ready for knowledge storage
        
        Args:
            query (str): The topic to search for on Wikipedia
            
        Returns:
            Dict[str, Any]: Response with status and data/error information
        """
        try:
            # Check if Wikipedia API is enabled in configuration
            if not self.api_configs['wikipedia']['enabled']:
                return {'status': 'disabled'}
            
            # Clean up query for Wikipedia URL format (spaces become underscores)
            clean_query = query.replace(' ', '_')
            # Construct full API URL for Wikipedia page summary
            url = f"{self.api_configs['wikipedia']['base_url']}{clean_query}"
            
            # Make HTTP request to Wikipedia with 10-second timeout
            response = requests.get(url, timeout=10)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse JSON response from Wikipedia API
                data = response.json()
                return {
                    'status': 'success',
                    'data': {
                        # Extract page title
                        'title': data.get('title', ''),
                        # Extract full page summary/content
                        'extract': data.get('extract', ''),
                        # Create truncated summary for quick display (max 300 chars)
                        'summary': data.get('extract', '')[:300] + '...' if len(data.get('extract', '')) > 300 else data.get('extract', ''),
                        # Extract Wikipedia page URL for reference
                        'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                        # Add timestamp when this information was retrieved
                        'timestamp': str(datetime.now())
                    }
                }
            else:
                # Wikipedia returned non-200 status (likely page not found)
                return {'status': 'not_found'}
                
        except Exception as e:
            # Handle any network errors, JSON parsing errors, or other exceptions
            self.logger.error(f"Wikipedia search error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _store_knowledge(self, query: str, data: Dict[str, Any], source: str):
        """
        Store learned information in the knowledge base
        
        This method:
        - Normalizes the query key to lowercase for consistent storage
        - Merges the learned data with metadata (source, timestamp, access count)
        - Saves the updated knowledge base to persistent storage
        - Tracks when and where the information was learned
        
        Args:
            query (str): The search query that led to this knowledge
            data (Dict[str, Any]): The structured data learned from the API
            source (str): The source of the information (e.g., 'wikipedia', 'openweather')
        """
        try:
            # Normalize the query key to lowercase for consistent storage and retrieval
            key = query.lower()
            
            # Store the knowledge with metadata about the learning process
            self.knowledge_base[key] = {
                **data,  # Spread the learned data (title, extract, summary, etc.)
                'source': source,  # Track where this information came from
                'learned_at': str(datetime.now()),  # When was this learned
                'access_count': 1  # Track how often this knowledge is accessed
            }
            
            # Persist the updated knowledge base to file storage
            self._save_knowledge_base()
            
            # Log successful storage for debugging and monitoring
            self.logger.info(f"Stored knowledge about '{query}' from {source}")
            
        except Exception as e:
            # Handle any errors during storage process
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
