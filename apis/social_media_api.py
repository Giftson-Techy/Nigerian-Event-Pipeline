"""
Social Media API Integration - Twitter, Facebook, Instagram
"""

import os
import logging
import requests
from typing import List, Dict
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SocialMediaAPI:
    """Integrates with social media APIs to find event announcements"""
    
    def __init__(self):
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.facebook_access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.eventbrite_token = os.getenv('EVENTBRITE_TOKEN')
        self.max_events = int(os.getenv('MAX_EVENTS_PER_SOURCE', 50))
    
    def get_twitter_events(self) -> List[Dict]:
        """Get events from Twitter API v2"""
        events = []
        
        if not self.twitter_bearer_token:
            logger.warning("Twitter Bearer Token not configured")
            return events
        
        try:
            # Twitter API v2 search endpoint
            url = "https://api.twitter.com/2/tweets/search/recent"
            
            # Event-related search queries
            queries = [
                "event OR concert OR festival OR conference -is:retweet",
                "upcoming OR happening OR live -is:retweet",
                "tickets OR registration OR attend -is:retweet"
            ]
            
            headers = {
                'Authorization': f'Bearer {self.twitter_bearer_token}',
                'Content-Type': 'application/json'
            }
            
            for query in queries:
                params = {
                    'query': query,
                    'max_results': 50,
                    'tweet.fields': 'created_at,author_id,context_annotations,entities,public_metrics',
                    'user.fields': 'name,username,verified',
                    'expansions': 'author_id'
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Process tweets
                    for tweet in data.get('data', []):
                        if self._is_event_tweet(tweet):
                            event = self._process_tweet(tweet, data.get('includes', {}))
                            events.append(event)
                
                elif response.status_code == 429:
                    logger.warning("Twitter API rate limit exceeded")
                    break
                else:
                    logger.error(f"Twitter API error: {response.status_code}")
                    break
        
        except Exception as e:
            logger.error(f"Error fetching Twitter events: {e}")
        
        return events[:self.max_events]
    
    def get_facebook_events(self) -> List[Dict]:
        """Get events from Facebook Graph API"""
        events = []
        
        if not self.facebook_access_token:
            logger.warning("Facebook Access Token not configured")
            return events
        
        try:
            # Facebook Graph API - search for public events
            url = "https://graph.facebook.com/v18.0/search"
            
            params = {
                'q': 'events concerts festivals',
                'type': 'event',
                'access_token': self.facebook_access_token,
                'fields': 'id,name,description,start_time,end_time,place,cover,ticket_uri,event_times',
                'limit': 50
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for fb_event in data.get('data', []):
                    event = {
                        'title': fb_event.get('name', ''),
                        'description': fb_event.get('description', ''),
                        'url': f"https://facebook.com/events/{fb_event.get('id', '')}",
                        'source': 'Facebook',
                        'location': self._extract_facebook_location(fb_event.get('place', {})),
                        'event_date': fb_event.get('start_time', ''),
                        'category': self._categorize_event(fb_event.get('name', '') + ' ' + fb_event.get('description', '')),
                        'image_url': fb_event.get('cover', {}).get('source', ''),
                        'organizer': 'Facebook Event'
                    }
                    events.append(event)
            
            else:
                logger.error(f"Facebook API error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error fetching Facebook events: {e}")
        
        return events[:self.max_events]
    
    def get_eventbrite_events(self) -> List[Dict]:
        """Get events from Eventbrite API"""
        events = []
        
        if not self.eventbrite_token:
            logger.warning("Eventbrite Token not configured")
            return events
        
        try:
            # Eventbrite API - search events
            url = "https://www.eventbriteapi.com/v3/events/search/"
            
            headers = {
                'Authorization': f'Bearer {self.eventbrite_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'sort_by': 'date',
                'location.address': 'United States',  # You can make this configurable
                'expand': 'venue,organizer',
                'token': self.eventbrite_token
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for eb_event in data.get('events', []):
                    venue = eb_event.get('venue', {})
                    organizer = eb_event.get('organizer', {})
                    
                    event = {
                        'title': eb_event.get('name', {}).get('text', ''),
                        'description': eb_event.get('description', {}).get('text', ''),
                        'url': eb_event.get('url', ''),
                        'source': 'Eventbrite API',
                        'location': self._extract_eventbrite_location(venue),
                        'event_date': eb_event.get('start', {}).get('local', ''),
                        'category': eb_event.get('category', {}).get('name', 'General'),
                        'image_url': eb_event.get('logo', {}).get('url', ''),
                        'organizer': organizer.get('name', 'Eventbrite'),
                        'price': self._extract_eventbrite_price(eb_event)
                    }
                    events.append(event)
            
            else:
                logger.error(f"Eventbrite API error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error fetching Eventbrite events: {e}")
        
        return events[:self.max_events]
    
    def _is_event_tweet(self, tweet: Dict) -> bool:
        """Check if tweet is about an event"""
        text = tweet.get('text', '').lower()
        
        event_keywords = [
            'event', 'concert', 'festival', 'conference', 'workshop',
            'meetup', 'show', 'performance', 'tickets', 'join us',
            'happening', 'live', 'save the date', 'register'
        ]
        
        # Check for URLs (likely event links)
        has_url = 'entities' in tweet and 'urls' in tweet['entities']
        
        # Check for event keywords
        has_keywords = any(keyword in text for keyword in event_keywords)
        
        return has_keywords or has_url
    
    def _process_tweet(self, tweet: Dict, includes: Dict) -> Dict:
        """Process tweet data into event format"""
        text = tweet.get('text', '')
        
        # Extract URLs
        urls = []
        if 'entities' in tweet and 'urls' in tweet['entities']:
            urls = [url.get('expanded_url', url.get('url', '')) 
                   for url in tweet['entities']['urls']]
        
        # Get author info
        author_info = self._get_tweet_author(tweet.get('author_id'), includes)
        
        event = {
            'title': self._extract_event_title(text),
            'description': text[:200] + '...' if len(text) > 200 else text,
            'url': urls[0] if urls else f"https://twitter.com/i/web/status/{tweet.get('id')}",
            'source': 'Twitter',
            'location': self._extract_location(text),
            'event_date': self._extract_date(text),
            'category': self._categorize_event(text),
            'organizer': author_info.get('name', 'Twitter User'),
            'created_at': tweet.get('created_at', '')
        }
        
        return event
    
    def _get_tweet_author(self, author_id: str, includes: Dict) -> Dict:
        """Get author information from includes"""
        users = includes.get('users', [])
        for user in users:
            if user.get('id') == author_id:
                return user
        return {}
    
    def _extract_event_title(self, text: str) -> str:
        """Extract event title from tweet text"""
        # Look for patterns like "Join us for..." or "Don't miss..."
        title_patterns = [
            r'(?i)(?:join us for|don\'t miss|coming soon|announcing|excited to announce|proud to present)[\s:]+(.*?)(?:[.!]|$)',
            r'(?i)^([^#@]*?)(?:\s*#|\s*@|$)'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text)
            if match:
                title = match.group(1).strip()
                if len(title) > 10:  # Ensure it's substantial
                    return title[:100]  # Limit length
        
        # Fallback: use first part of tweet
        return text.split('\n')[0][:100]
    
    def _extract_facebook_location(self, place: Dict) -> str:
        """Extract location from Facebook place object"""
        if not place:
            return ''
        
        location_parts = []
        
        if 'name' in place:
            location_parts.append(place['name'])
        
        if 'location' in place:
            loc = place['location']
            if 'city' in loc:
                location_parts.append(loc['city'])
            if 'state' in loc:
                location_parts.append(loc['state'])
        
        return ', '.join(location_parts)
    
    def _extract_eventbrite_location(self, venue: Dict) -> str:
        """Extract location from Eventbrite venue object"""
        if not venue:
            return ''
        
        location_parts = []
        
        if 'name' in venue:
            location_parts.append(venue['name'])
        
        if 'address' in venue:
            addr = venue['address']
            if 'city' in addr:
                location_parts.append(addr['city'])
            if 'region' in addr:
                location_parts.append(addr['region'])
        
        return ', '.join(location_parts)
    
    def _extract_eventbrite_price(self, event: Dict) -> str:
        """Extract price information from Eventbrite event"""
        if 'is_free' in event and event['is_free']:
            return 'Free'
        
        # Would need additional API call to get ticket info
        return 'Check Event Page'
    
    def _extract_location(self, text: str) -> str:
        """Extract location from text"""
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
    
    def get_all_events(self) -> List[Dict]:
        """Get events from all social media sources"""
        all_events = []
        
        logger.info("Fetching events from social media APIs...")
        
        # Twitter events
        twitter_events = self.get_twitter_events()
        all_events.extend(twitter_events)
        logger.info(f"Found {len(twitter_events)} events from Twitter")
        
        # Facebook events
        facebook_events = self.get_facebook_events()
        all_events.extend(facebook_events)
        logger.info(f"Found {len(facebook_events)} events from Facebook")
        
        # Eventbrite events
        eventbrite_events = self.get_eventbrite_events()
        all_events.extend(eventbrite_events)
        logger.info(f"Found {len(eventbrite_events)} events from Eventbrite API")
        
        # Remove duplicates based on URL
        unique_events = []
        seen_urls = set()
        
        for event in all_events:
            url = event.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_events.append(event)
        
        logger.info(f"Found {len(unique_events)} unique events from social media")
        return unique_events[:self.max_events]
