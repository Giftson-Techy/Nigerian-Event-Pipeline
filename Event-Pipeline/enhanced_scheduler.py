"""
Enhanced Event Scheduler - Now with Smart Quota Management!
Stays within Google's 100 API calls/day limit with intelligent prioritization
"""

import schedule
import time
import threading
import sys
import os
from datetime import datetime
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.search_scraper import SearchScraper
from scrapers.news_scraper import NewsScraper  
from scrapers.social_media_scraper import SocialMediaScraper
from database.db_manager import DatabaseManager
from config.country_manager import country_manager
from utils.quota_manager import quota_manager
from utils.prioritized_queries import query_manager

logger = logging.getLogger(__name__)

class EnhancedEventScheduler:
    """Enhanced event scheduler with smart quota management and prioritization"""
    
    def __init__(self):
        self.search_scraper = SearchScraper()
        self.news_scraper = NewsScraper()
        self.social_media_scraper = SocialMediaScraper()
        self.db_manager = DatabaseManager()
        self.running = False
        
        # Get initial quota status
        quota_status = quota_manager.get_quota_status()
        
        logger.info("🚀 Enhanced Nigerian Event Pipeline initialized!")
        logger.info("🆕 Features: Search + News + Social Media + Smart Caching + Quota Management")
        logger.info(f"🎯 Target Country: {country_manager.get_current_country()}")
        logger.info(f"📊 Daily Quota: {quota_status['calls_used']}/90 used ({quota_status['percentage_used']:.1f}%)")
        logger.info(f"📈 Available queries: {query_manager.get_query_stats()}")
    
    def run_comprehensive_pipeline(self):
        """Run comprehensive pipeline with quota-aware query selection"""
        start_time = datetime.now()
        current_country = country_manager.get_current_country()
        
        # Check quota status
        quota_status = quota_manager.get_quota_status()
        if not quota_status['can_make_calls']:
            logger.warning("🚫 Daily quota exhausted! Skipping comprehensive pipeline.")
            return
        
        # Get quota allocation for comprehensive run
        allocation = quota_manager.distribute_daily_quota()
        max_search_calls = allocation.get('comprehensive', 5)
        
        logger.info("=" * 80)
        logger.info(f"🔄 QUOTA-MANAGED COMPREHENSIVE PIPELINE for {current_country}")
        logger.info(f"📊 Quota available: {quota_status['calls_remaining']}/90 calls")
        logger.info(f"🎯 This run budget: {max_search_calls} API calls")
        logger.info("=" * 80)
        
        total_events = 0
        sources_summary = {}
        api_calls_made = 0
        
        try:
            # 1. PRIORITIZED Search Engines (Google/Bing) - QUOTA MANAGED!
            logger.info(f"🔍 Running {max_search_calls} prioritized searches...")
            
            # Get prioritized queries that fit our quota
            selected_queries = query_manager.get_comprehensive_queries(max_search_calls)
            
            search_events = []
            for query_info in selected_queries:
                if not quota_manager.can_make_calls(1):
                    logger.warning("🚫 Quota exhausted during search phase!")
                    break
                
                query = query_info['query']
                try:
                    if query_info.get('type') == 'social':
                        # Use social media scraper for social queries
                        events = self.social_media_scraper.scrape_google_social_search(query)
                    else:
                        # Use regular search scraper
                        events = self.search_scraper.scrape_google_search(query)
                    
                    if events:
                        search_events.extend(events)
                        
                    # Record the API call
                    quota_manager.record_api_call(query, query_info.get('type', 'search'))
                    api_calls_made += 1
                    
                    # Small delay to be respectful
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Search error for '{query}': {e}")
                    continue
            
            if search_events:
                saved_search = self.db_manager.save_events(search_events)
                total_events += len(search_events)
                sources_summary['Search Engines'] = f"{len(search_events)} found, {saved_search} new"
                logger.info(f"✅ Search: {len(search_events)} events, {saved_search} new saved")
            
            # 2. News Sites (No API quota needed - RSS feeds)
            logger.info(f"📰 Scraping news sites for {current_country}...")
            news_events = self.news_scraper.scrape_all()
            if news_events:
                saved_news = self.db_manager.save_events(news_events)
                total_events += len(news_events)
                sources_summary['News Sites'] = f"{len(news_events)} found, {saved_news} new"
                logger.info(f"✅ News: {len(news_events)} events, {saved_news} new saved")
            
            # 3. Cache Status Report
            try:
                cache_stats = self.get_cache_status()
                logger.info(f"📊 Cache: {cache_stats['valid']} valid, {cache_stats['expired']} expired")
            except:
                pass
                
        except Exception as e:
            logger.error(f"❌ Comprehensive pipeline error: {e}")
        
        # Final summary with quota usage
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        final_quota = quota_manager.get_quota_status()
        
        logger.info("=" * 80)
        logger.info(f"🎉 COMPREHENSIVE PIPELINE COMPLETE!")
        logger.info(f"⏱️  Duration: {duration:.1f} seconds")
        logger.info(f"📊 Total events discovered: {total_events}")
        logger.info(f"🔥 API calls made: {api_calls_made}")
        logger.info(f"📈 Quota remaining: {final_quota['calls_remaining']}/90 ({100-final_quota['percentage_used']:.1f}% left)")
        for source, summary in sources_summary.items():
            logger.info(f"   📍 {source}: {summary}")
        logger.info("=" * 80)
    
    def run_quick_search(self):
        """Quick search for urgent events - quota managed"""
        quota_status = quota_manager.get_quota_status()
        if not quota_status['can_make_calls']:
            logger.warning("🚫 Daily quota exhausted! Skipping quick search.")
            return
        
        # Allocate 2-3 calls for quick search
        allocation = quota_manager.distribute_daily_quota()
        max_calls = min(3, allocation.get('quick', 2))
        
        logger.info(f"⚡ Quick search update (budget: {max_calls} calls)...")
        
        # Get urgent queries only
        urgent_queries = query_manager.get_quick_queries(max_calls)
        
        total_new = 0
        api_calls_made = 0
        
        for query_info in urgent_queries:
            if not quota_manager.can_make_calls(1):
                logger.warning("🚫 Quota exhausted during quick search!")
                break
                
            query = query_info['query']
            try:
                events = self.search_scraper.scrape_google_search(query)
                if events:
                    saved = self.db_manager.save_events(events)
                    total_new += saved
                
                # Record the API call
                quota_manager.record_api_call(query, 'quick')
                api_calls_made += 1
                
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                logger.error(f"Quick search error for '{query}': {e}")
                continue
        
        final_quota = quota_manager.get_quota_status()
        logger.info(f"⚡ Quick search: {total_new} new events, {api_calls_made} API calls")
        logger.info(f"📈 Quota remaining: {final_quota['calls_remaining']}/90")
    
    def run_social_media_update(self):
        """Social media focused update - quota managed"""
        quota_status = quota_manager.get_quota_status()
        if not quota_status['can_make_calls']:
            logger.warning("� Daily quota exhausted! Skipping social media update.")
            return
        
        # Allocate 2-4 calls for social media
        allocation = quota_manager.distribute_daily_quota()
        max_calls = min(4, allocation.get('social', 2))
        
        logger.info(f"📱 Social media update (budget: {max_calls} calls)...")
        
        # Get social media queries
        social_queries = query_manager.get_social_queries(max_calls)
        
        total_new = 0
        api_calls_made = 0
        
        for query_info in social_queries:
            if not quota_manager.can_make_calls(1):
                logger.warning("🚫 Quota exhausted during social media update!")
                break
                
            query = query_info['query']
            try:
                events = self.social_media_scraper.scrape_google_social_search(query)
                if events:
                    saved = self.db_manager.save_events(events)
                    total_new += saved
                
                # Record the API call
                quota_manager.record_api_call(query, 'social')
                api_calls_made += 1
                
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                logger.error(f"Social media search error for '{query}': {e}")
                continue
        
        final_quota = quota_manager.get_quota_status()
        logger.info(f"📱 Social media: {total_new} new events, {api_calls_made} API calls")
        logger.info(f"📈 Quota remaining: {final_quota['calls_remaining']}/90")
    
    def cleanup_cache(self):
        """Clean up expired cache files to save space"""
        try:
            from utils.api_cache import api_cache
            cleared = api_cache.clear_expired()
            stats = api_cache.get_cache_stats()
            
            logger.info(f"🧹 Cache cleanup: {cleared} expired files removed")
            logger.info(f"📊 Cache stats: {stats['valid']} valid, {stats['expired']} expired, {stats['total']} total")
            
        except Exception as e:
            logger.error(f"❌ Cache cleanup error: {e}")
    
    def get_cache_status(self):
        """Get current cache status for monitoring"""
        try:
            from utils.api_cache import api_cache
            return api_cache.get_cache_stats()
        except Exception as e:
            logger.error(f"❌ Cache status error: {e}")
            return {'total': 0, 'valid': 0, 'expired': 0}

    def start_enhanced_scheduler(self):
        """Start the enhanced automated scheduler with smart quota management"""
        quota_status = quota_manager.get_quota_status()
        query_stats = query_manager.get_query_stats()
        
        logger.info("🤖 ENHANCED NIGERIAN EVENT PIPELINE STARTING!")
        logger.info("🆕 NOW WITH QUOTA MANAGEMENT + SMART PRIORITIZATION!")
        logger.info(f"🎯 Target: {country_manager.get_current_country()}")
        logger.info("📅 Schedule (QUOTA-OPTIMIZED):")
        logger.info("  🔄 Comprehensive pipeline: Every 2 hours (5-15 API calls)")
        logger.info("  ⚡ Quick search updates: Every 1 hour (2-3 API calls)") 
        logger.info("  📱 Social media updates: Every 1.5 hours (2-4 API calls)")
        logger.info("  🧹 Cache cleanup: Every 6 hours")
        logger.info(f"� Daily Quota: {quota_status['calls_used']}/90 used ({quota_status['percentage_used']:.1f}%)")
        logger.info(f"📈 Available queries: {query_stats['total_queries']} total")
        logger.info(f"   🚨 Urgent: {query_stats['urgent']}, 🔥 High: {query_stats['high']}")
        logger.info(f"   📊 Medium: {query_stats['medium']}, 📱 Social: {query_stats['social']}")
        logger.info("💾 Smart caching + quota management = sustainable 24/7 operation!")
        logger.info("=" * 80)
        
        # CONSERVATIVE Schedule to stay within 90 calls/day
        # 2 hours = 12 comprehensive runs/day * 8 calls = 96 calls
        # 1 hour = 24 quick runs/day * 2 calls = 48 calls  
        # 1.5 hours = 16 social runs/day * 3 calls = 48 calls
        # We'll dynamically adjust based on remaining quota
        
        schedule.every(2).hours.do(self.run_comprehensive_pipeline)     # 12 runs/day
        schedule.every(1).hours.do(self.run_quick_search)              # 24 runs/day
        schedule.every(90).minutes.do(self.run_social_media_update)    # 16 runs/day
        
        # Add cache cleanup schedule
        schedule.every(6).hours.do(self.cleanup_cache)                 # Clean expired cache every 6 hours
        
        # Initial run
        logger.info("🚀 Running initial comprehensive discovery...")
        self.run_comprehensive_pipeline()
        
        self.running = True
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("⏹️ Enhanced scheduler stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Enhanced scheduler error: {e}")
            self.running = False

def run_enhanced_pipeline():
    """Run the enhanced event pipeline"""
    scheduler = EnhancedEventScheduler()
    scheduler.start_enhanced_scheduler()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('event_pipeline.log'),
            logging.StreamHandler()
        ]
    )
    
    run_enhanced_pipeline()
