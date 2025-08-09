"""
Main Scraper Manager - Google Search Only
Simplified for quota management and reliability
"""

import logging
from typing import List, Dict
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .search_scraper import SearchScraper
from config.country_manager import country_manager

logger = logging.getLogger(__name__)

class ScraperManager:
    """Manages Google Search scraper for event discovery"""
    
    def __init__(self):
        self.search_scraper = SearchScraper()
    
    def scrape_all_events(self, country: str = "Nigeria") -> Dict[str, List[Dict]]:
        """
        Scrape events from Google Search only
        """
        logger.info(f"🚀 Starting Google Search event scraping for {country}")
        
        results = {
            'search_engines': [],
            'total_events': 0,
            'sources_used': ['Google Search']
        }
        
        try:
            # Google Search Results Only
            logger.info("📊 Scraping Google Search...")
            search_events = self.search_scraper.search_events(country)
            results['search_engines'] = search_events
            logger.info(f"✅ Found {len(search_events)} Google Search events")
            
        except Exception as e:
            logger.error(f"❌ Google Search scraping failed: {e}")
        
        # Calculate totals
        total = len(results['search_engines'])
        results['total_events'] = total
        
        logger.info(f"🎉 SCRAPING COMPLETE! Total events found: {total}")
        logger.info(f"📊 Google Search Events: {len(results['search_engines'])}")
        
        return results
    
    def get_events_by_source(self, source: str, country: str = "Nigeria") -> List[Dict]:
        """Get events from Google Search (only available source)"""
        
        if source.lower() in ['search', 'search_engines', 'google']:
            return self.search_scraper.search_events(country)
        else:
            logger.warning(f"Only Google Search available. Requested: {source}")
            return self.search_scraper.search_events(country)
    
    def get_events_by_platform(self, platform: str, country: str = "Nigeria") -> List[Dict]:
        """Get events from Google Search (only available platform)"""
        
        # All requests redirect to Google Search
        logger.info(f"Platform '{platform}' requested - using Google Search")
        return self.search_scraper.search_events(country)
