"""
Event Scheduler - Automated pipeline execution every 15 minutes
"""

import schedule
import time
import threading
import sys
import os
from datetime import datetime
import logging

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.search_scraper import SearchScraper
from database.db_manager import DatabaseManager
from config.country_manager import country_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EventScheduler:
    """Manages automated event discovery pipeline - Google Search Only"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.search_scraper = SearchScraper()
        self.running = False
    
    def run_pipeline(self):
        """Execute the complete event discovery pipeline"""
        current_country = country_manager.get_current_country()
        logger.info(f"🔄 Starting event discovery pipeline for {current_country}...")
        start_time = datetime.now()
        
        total_events = 0
        
        try:
            # Ensure search scraper uses current country
            self.search_scraper.set_country(current_country)
            
            # Google Search scraping (ONLY SOURCE)
            logger.info(f"🔍 Scraping Google Search for {current_country} events...")
            search_events = self.search_scraper.scrape_all()
            total_events += len(search_events)
            self.db_manager.save_events(search_events)
            logger.info(f"✅ Found {len(search_events)} events from Google Search")
            
            # Clean old events
            self.db_manager.cleanup_old_events()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"🎉 Pipeline completed for {current_country}! Found {total_events} total events in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {str(e)}")
    
    def start(self):
        """Start the scheduler"""
        self.running = True
        
        # Schedule pipeline to run every 15 minutes
        schedule.every(15).minutes.do(self.run_pipeline)
        
        logger.info("⏰ Scheduler started - pipeline will run every 15 minutes")
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("🛑 Scheduler stopped")
