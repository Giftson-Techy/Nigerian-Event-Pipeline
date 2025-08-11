"""
Search Engine Scraper - Google, Bing, and other search engines
"""

import requests
from bs4 import BeautifulSoup
import time
import os
import logging
import sys
from typing import List, Dict
from urllib.parse import urlencode, urlparse, unquote
import re
from datetime import datetime, timedelta
import base64

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.country_manager import country_manager

logger = logging.getLogger(__name__)

class SearchScraper:
    """Scrapes search engines for upcoming events"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.delay = int(os.getenv('REQUEST_DELAY', 2))
        self.max_events = int(os.getenv('MAX_EVENTS_PER_SOURCE', 50))
        
        # Get country-specific event queries
        self.event_queries = country_manager.get_country_search_terms()
        
        # Base event queries for fallback
        self.base_queries = [
            "upcoming events",
            "concerts this week", 
            "festivals 2025",
            "conferences events",
            "workshops seminars"
        ]
    
    def set_country(self, country: str) -> bool:
        """Set the country for event searches"""
        if country_manager.set_current_country(country):
            self.event_queries = country_manager.get_country_search_terms()
            logger.info(f"Updated search queries for {country}")
            return True
        return False
    
    def get_current_country(self) -> str:
        """Get the current search country"""
        return country_manager.get_current_country()
    
    def scrape_google_search(self, query: str) -> List[Dict]:
        """Scrape Google search results for events"""
        events = []
        
        try:
            # Use Google Custom Search API if available
            google_api_key = os.getenv('GOOGLE_API_KEY')
            google_cse_id = os.getenv('GOOGLE_CSE_ID')
            
            if google_api_key and google_cse_id:
                events.extend(self._google_cse_search(query, google_api_key, google_cse_id))
            else:
                # Fallback to web scraping (be careful about rate limits)
                events.extend(self._google_web_search(query))
            
        except Exception as e:
            logger.error(f"Error scraping Google for '{query}': {e}")
        
        return events
    
    def _google_cse_search(self, query: str, api_key: str, cse_id: str) -> List[Dict]:
        """Use Google Custom Search Engine API with smart caching and quota management"""
        events = []
        
        try:
            # Import cache system and quota manager
            from utils.api_cache import api_cache
            from utils.quota_manager import quota_manager
            
            # Add Nigeria-specific terms to the query
            nigeria_query = f"{query} Nigeria Lagos Abuja"
            
            # Check cache first
            cached_result = api_cache.get(nigeria_query, 'search')
            if cached_result:
                # Use cached results - no API call needed!
                result = cached_result
                logger.info(f"📦 Using cached result for: {query}")
            else:
                # Check quota before making API call
                if not quota_manager.can_make_calls(1):
                    logger.warning(f"🚫 Quota exhausted! Cannot search for: {query}")
                    return events
                
                # Make API call and cache result
                from googleapiclient.discovery import build
                logger.info(f"🔍 Making Google API call for: {query}")
                
                service = build("customsearch", "v1", developerKey=api_key)
                result = service.cse().list(
                    q=nigeria_query,
                    cx=cse_id,
                    num=10,
                    gl='ng',  # Geolocation bias towards Nigeria
                    cr='countryNG'  # Country restrict to Nigeria
                ).execute()
                
                # Cache the result for future use
                api_cache.set(nigeria_query, result, 'search')
            
            for item in result.get('items', []):
                # Apply country filtering to Google CSE results
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                full_text = title + ' ' + snippet
                
                # Only include events relevant to current country
                if self._is_event_related(full_text) and self._is_country_relevant(full_text):
                    event = {
                        'title': title,
                        'description': snippet,
                        'url': item.get('link', ''),
                        'source': 'Google Search',
                        'location': self._extract_location(snippet),
                        'event_date': self._extract_date(snippet),
                        'category': self._categorize_event(full_text),
                        'search_country': country_manager.get_current_country()
                    }
                    events.append(event)
                
        except Exception as e:
            logger.error(f"Google CSE API error: {e}")
        
        return events
    
    def _google_web_search(self, query: str) -> List[Dict]:
        """Scrape Google search results directly"""
        events = []
        
        try:
            search_url = f"https://www.google.com/search?{urlencode({'q': query + ' events'})}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find search result containers
            search_results = soup.find_all('div', {'class': 'g'})
            
            for result in search_results[:10]:  # Limit to first 10 results
                try:
                    title_elem = result.find('h3')
                    link_elem = result.find('a')
                    desc_elem = result.find('span', {'class': 'st'}) or result.find('div', {'class': 'VwiC3b'})
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        url = link_elem.get('href', '')
                        description = desc_elem.get_text(strip=True) if desc_elem else ''
                        
                        # Filter for event-related content AND country relevance
                        full_text = title + ' ' + description
                        if self._is_event_related(full_text) and self._is_country_relevant(full_text):
                            # Decode redirect URL to get actual destination
                            actual_url = self._decode_redirect_url(url)
                            
                            event = {
                                'title': title,
                                'description': description,
                                'url': actual_url,
                                'source': 'Google Search',
                                'location': self._extract_location(description),
                                'event_date': self._extract_date(description),
                                'category': self._categorize_event(full_text),
                                'search_country': country_manager.get_current_country()
                            }
                            events.append(event)
                            
                except Exception as e:
                    logger.warning(f"Error parsing search result: {e}")
                    continue
            
            time.sleep(self.delay)
            
        except Exception as e:
            logger.error(f"Error scraping Google search: {e}")
        
        return events
    
    def scrape_bing_search(self, query: str) -> List[Dict]:
        """Scrape Bing search results for events"""
        events = []
        
        try:
            search_url = f"https://www.bing.com/search?{urlencode({'q': query + ' events'})}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find search result containers
            search_results = soup.find_all('li', {'class': 'b_algo'})
            
            for result in search_results[:10]:
                try:
                    title_elem = result.find('h2')
                    link_elem = result.find('a')
                    desc_elem = result.find('p') or result.find('div', {'class': 'b_caption'})
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        url = link_elem.get('href', '')
                        description = desc_elem.get_text(strip=True) if desc_elem else ''
                        
                        full_text = title + ' ' + description
                        if self._is_event_related(full_text) and self._is_country_relevant(full_text):
                            # Decode redirect URL to get actual destination
                            actual_url = self._decode_redirect_url(url)
                            
                            event = {
                                'title': title,
                                'description': description,
                                'url': actual_url,
                                'source': 'Bing Search',
                                'location': self._extract_location(description),
                                'event_date': self._extract_date(description),
                                'category': self._categorize_event(full_text),
                                'search_country': country_manager.get_current_country()
                            }
                            events.append(event)
                            
                except Exception as e:
                    logger.warning(f"Error parsing Bing result: {e}")
                    continue
            
            time.sleep(self.delay)
            
        except Exception as e:
            logger.error(f"Error scraping Bing search: {e}")
        
        return events
    
    def _decode_redirect_url(self, url: str) -> str:
        """Decode Bing/Google redirect URLs to get the actual destination"""
        try:
            # Handle Bing redirect URLs
            if 'bing.com/ck/a' in url:
                # Extract the 'u' parameter which contains the base64 encoded URL
                if '&u=' in url:
                    encoded_part = url.split('&u=')[1].split('&')[0]
                    try:
                        # Remove 'a1' prefix if present
                        if encoded_part.startswith('a1'):
                            encoded_part = encoded_part[2:]
                        
                        # Add padding if needed for base64
                        missing_padding = len(encoded_part) % 4
                        if missing_padding:
                            encoded_part += '=' * (4 - missing_padding)
                        
                        # Decode from base64
                        decoded_bytes = base64.b64decode(encoded_part)
                        decoded_url = decoded_bytes.decode('utf-8')
                        return decoded_url
                    except Exception as decode_error:
                        # If base64 fails, try URL decoding
                        try:
                            decoded_url = unquote(encoded_part)
                            if decoded_url.startswith('http'):
                                return decoded_url
                        except:
                            pass
            
            # Handle Google redirect URLs
            if 'google.com/url' in url:
                if 'url=' in url:
                    actual_url = unquote(url.split('url=')[1].split('&')[0])
                    return actual_url
            
            # For other redirect patterns, try to extract HTTP URLs
            if 'http' in url:
                # Look for http/https patterns in the URL
                import re
                http_match = re.search(r'https?://[^\s&]+', unquote(url))
                if http_match:
                    return http_match.group(0)
            
            # Return original URL if no redirect pattern found
            return url
            
        except Exception as e:
            logger.warning(f"Error decoding redirect URL: {e}")
            return url

    def _is_event_related(self, text: str) -> bool:
        event_keywords = [
            'event', 'concert', 'festival', 'conference', 'workshop', 'seminar',
            'meetup', 'show', 'performance', 'exhibition', 'fair', 'party',
            'gathering', 'celebration', 'ceremony', 'competition', 'tournament'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in event_keywords)
    
    def _is_country_relevant(self, text: str, target_country: str = None) -> bool:
        """Check if event is relevant to the target country"""
        target_country = target_country or country_manager.get_current_country()
        
        # Get country-specific information
        country_info = country_manager.get_country_info(target_country)
        text_lower = text.lower()
        
        # Define country-specific keywords
        if target_country == 'Nigeria':
            # Nigerian keywords that MUST be present
            nigerian_keywords = [
                'nigeria', 'nigerian', 'lagos', 'abuja', 'kano', 'ibadan', 
                'port harcourt', 'benin city', 'maiduguri', 'zaria', 'aba', 'jos',
                'naira', 'nollywood', 'afrobeat', 'west africa', 'ng', '.ng',
                'kaduna', 'calabar', 'enugu', 'warri', 'onitsha', 'owerri'
            ]
            
            # First check for Nigerian keywords
            has_nigerian_content = any(keyword in text_lower for keyword in nigerian_keywords)
            
            # Exclude obviously non-Nigerian locations (STRICT)
            exclude_keywords = [
                'mogadishu', 'somalia', 'kenya', 'south africa', 'ghana', 'uganda',
                'usa', 'america', 'united states', 'uk', 'britain', 'london', 'new york',
                'los angeles', 'chicago', 'canada', 'toronto', 'australia', 'sydney',
                'india', 'pakistan', 'bangladesh', 'dubai', 'egypt', 'morocco',
                'zimbabwe', 'botswana', 'zambia', 'malawi', 'tanzania', 'ethiopia'
            ]
            
            # If contains excluded keywords, reject immediately
            if any(keyword in text_lower for keyword in exclude_keywords):
                return False
                
            # For Nigeria, require explicit Nigerian content
            return has_nigerian_content
                
        elif target_country == 'United States':
            us_keywords = ['usa', 'america', 'united states', 'new york', 'los angeles', 'chicago', 'houston', 'phoenix']
            if any(keyword in text_lower for keyword in us_keywords):
                return True
                
        elif target_country == 'United Kingdom':
            uk_keywords = ['uk', 'britain', 'england', 'london', 'manchester', 'birmingham', 'liverpool']
            if any(keyword in text_lower for keyword in uk_keywords):
                return True
                
        # Check for cities mentioned in country info
        cities = country_info.get('cities', [])
        if any(city.lower() in text_lower for city in cities):
            return True
        
        # Default: reject if no country indicators found (STRICT MODE)
        return False
    
    def _extract_location(self, text: str) -> str:
        """Extract location from text"""
        # Simple location extraction patterns
        location_patterns = [
            r'(?i)(?:in|at|@)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?i)([A-Z][a-z]+,\s*[A-Z]{2})',
            r'(?i)([A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd))'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ''
    
    def _extract_date(self, text: str) -> str:
        """Extract date from text"""
        # Simple date extraction patterns
        date_patterns = [
            r'(?i)(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:,\s*\d{4})?',
            r'(?i)\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'(?i)(?:today|tomorrow|this\s+(?:week|weekend|month))',
            r'(?i)(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        
        return ''
    
    def _categorize_event(self, text: str) -> str:
        """Categorize event based on content"""
        categories = {
            'Music': ['concert', 'music', 'band', 'singer', 'album', 'tour', 'festival'],
            'Technology': ['tech', 'technology', 'startup', 'coding', 'developer', 'AI', 'software'],
            'Business': ['business', 'networking', 'conference', 'summit', 'corporate'],
            'Arts': ['art', 'gallery', 'exhibition', 'museum', 'painting', 'sculpture'],
            'Sports': ['sports', 'game', 'match', 'tournament', 'championship', 'athletic'],
            'Food': ['food', 'restaurant', 'culinary', 'cooking', 'chef', 'tasting'],
            'Education': ['workshop', 'seminar', 'training', 'course', 'lecture', 'class'],
            'Entertainment': ['comedy', 'theater', 'show', 'performance', 'entertainment']
        }
        
        text_lower = text.lower()
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return 'General'
    
    def scrape_all(self) -> List[Dict]:
        """Scrape all search engines for events using prioritized queries"""
        all_events = []
        
        current_country = self.get_current_country()
        logger.info(f"Starting search engine scraping for {current_country}...")
        
        # Import prioritized query manager
        try:
            from utils.prioritized_queries import query_manager
            
            # Get prioritized queries with smart quota management
            prioritized_queries = query_manager.get_comprehensive_queries(max_calls=25)
            
            logger.info(f"🎯 Using {len(prioritized_queries)} prioritized queries")
            
            for query_obj in prioritized_queries:
                query = query_obj['query']
                priority = query_obj['priority']
                
                logger.info(f"🔍 {priority.upper()}: {query}")
                
                # Google search using API
                google_events = self.scrape_google_search(query)
                if google_events:
                    # Tag events with priority and source
                    for event in google_events:
                        event['priority'] = priority
                        event['source'] = 'Google Search'
                    all_events.extend(google_events)
                
                # Small delay between queries
                time.sleep(0.5)
                
                # Break if we have enough events
                if len(all_events) > 100:
                    logger.info(f"✅ Found {len(all_events)} events, stopping search")
                    break
                    
        except ImportError:
            logger.warning("Prioritized queries not available, using fallback queries")
            # Fallback to basic queries
            queries_to_use = self.event_queries[:8]  # Limit to 8 queries
            
            for query in queries_to_use:
                logger.info(f"Searching for: {query}")
                
                # Google search
                google_events = self.scrape_google_search(query)
                all_events.extend(google_events)
                
                # Bing search
                bing_events = self.scrape_bing_search(query)
                all_events.extend(bing_events)
                
                # Rate limiting
                time.sleep(self.delay)
                
                if len(all_events) >= self.max_events:
                    break
        
        # Remove duplicates based on URL
        unique_events = []
        seen_urls = set()
        
        for event in all_events:
            url = event.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                # Add country info to event
                event['search_country'] = current_country
                unique_events.append(event)
        
        logger.info(f"Found {len(unique_events)} unique events from search engines for {current_country}")
        return unique_events[:self.max_events]
