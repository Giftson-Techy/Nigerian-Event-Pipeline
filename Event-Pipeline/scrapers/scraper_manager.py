"""
Main Scraper Manager - Coordinates all event scraping activities
"""

import logging
from typing import List, Dict
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .search_scraper import SearchScraper
from .news_scraper import NewsScraper
from .social_media_scraper import SocialMediaScraper
from config.country_manager import country_manager

logger = logging.getLogger(__name__)

class ScraperManager:
    """Manages all scrapers and coordinates event discovery"""
    
    def __init__(self):
        self.search_scraper = SearchScraper()
        self.news_scraper = NewsScraper()
        self.social_media_scraper = SocialMediaScraper()
    
    def scrape_all_events(self, country: str = "Nigeria") -> Dict[str, List[Dict]]:
        """
        Scrape events from all available sources
        """
        logger.info(f"🚀 Starting comprehensive event scraping for {country}")
        
        results = {
            'search_engines': [],
            'news_sites': [],
            'social_media': [],
            'total_events': 0,
            'sources_used': []
        }
        
        try:
            # 1. Search Engine Results (Google, Bing)
            logger.info("📊 Scraping search engines...")
            search_events = self.search_scraper.search_events(country)
            results['search_engines'] = search_events
            results['sources_used'].append('Search Engines')
            logger.info(f"✅ Found {len(search_events)} search engine events")
            
        except Exception as e:
            logger.error(f"❌ Search engine scraping failed: {e}")
        
        try:
            # 2. News Sites
            logger.info("📰 Scraping news sites...")
            news_events = self.news_scraper.scrape_all_news(country)
            results['news_sites'] = news_events
            results['sources_used'].append('News Sites')
            logger.info(f"✅ Found {len(news_events)} news site events")
            
        except Exception as e:
            logger.error(f"❌ News site scraping failed: {e}")
        
        try:
            # 3. Social Media Platforms (NEW!)
            logger.info("📱 Scraping social media platforms...")
            social_events = self.social_media_scraper.scrape_all_social_media(country)
            results['social_media'] = social_events
            results['sources_used'].append('Social Media')
            logger.info(f"✅ Found {len(social_events)} social media events")
            
        except Exception as e:
            logger.error(f"❌ Social media scraping failed: {e}")
        
        # Calculate totals
        total = len(results['search_engines']) + len(results['news_sites']) + len(results['social_media'])
        results['total_events'] = total
        
        logger.info(f"🎉 SCRAPING COMPLETE! Total events found: {total}")
        logger.info(f"📊 Breakdown: Search={len(results['search_engines'])}, News={len(results['news_sites'])}, Social={len(results['social_media'])}")
        
        return results
    
    def get_events_by_source(self, source: str, country: str = "Nigeria") -> List[Dict]:
        """Get events from a specific source"""
        
        if source.lower() in ['search', 'search_engines', 'google', 'bing']:
            return self.search_scraper.search_events(country)
        
        elif source.lower() in ['news', 'news_sites']:
            return self.news_scraper.scrape_all_news(country)
        
        elif source.lower() in ['social', 'social_media', 'facebook', 'linkedin', 'instagram']:
            return self.social_media_scraper.scrape_all_social_media(country)
        
        else:
            logger.warning(f"Unknown source: {source}")
            return []
    
    def get_events_by_platform(self, platform: str, country: str = "Nigeria") -> List[Dict]:
        """Get events from a specific platform"""
        
        platform_mapping = {
            'linkedin': lambda: [e for e in self.social_media_scraper.scrape_all_social_media(country) if e.get('platform') == 'LinkedIn'],
            'facebook': lambda: [e for e in self.social_media_scraper.scrape_all_social_media(country) if e.get('platform') == 'Facebook'],
            'instagram': lambda: [e for e in self.social_media_scraper.scrape_all_social_media(country) if e.get('platform') == 'Instagram'],
            'twitter': lambda: [e for e in self.social_media_scraper.scrape_all_social_media(country) if e.get('platform') == 'Twitter/X'],
            'eventbrite': lambda: [e for e in self.social_media_scraper.scrape_all_social_media(country) if e.get('platform') == 'Eventbrite'],
            'google': lambda: self.search_scraper.search_events(country),
            'news': lambda: self.news_scraper.scrape_all_news(country)
        }
        
        if platform.lower() in platform_mapping:
            return platform_mapping[platform.lower()]()
        else:
            logger.warning(f"Unknown platform: {platform}")
            return []
