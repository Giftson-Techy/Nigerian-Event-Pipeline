#!/usr/bin/env python3
"""
Event Pipeline - Nigerian Event Discovery
Automated event discovery from multiple sources
"""

import os
import sys
import threading
import time
from dotenv import load_dotenv
from flask import Flask

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scheduler import EventScheduler
from web.app import create_app
from database.db_manager import DatabaseManager

def main():
    """Main application entry point"""
    # Load environment variables
    load_dotenv()
    
    print("🚀 Starting Event Pipeline...")
    
    # Initialize database
    db_manager = DatabaseManager()
    db_manager.initialize_database()
    print("✅ Database initialized")
    
    # Create Flask app
    app = create_app()
    
    # Initialize and start scheduler
    scheduler = EventScheduler()
    scheduler_thread = threading.Thread(target=scheduler.start, daemon=True)
    scheduler_thread.start()
    print("✅ Event scheduler started (runs every 15 minutes)")
    
    # Run initial scrape (skip in cloud for faster startup)
    if os.environ.get('PORT'):
        # Running on cloud platform - skip initial scrape for faster startup
        print("☁️ Cloud deployment detected - skipping initial scrape")
        print("📅 Scheduler will run automatically in background")
    else:
        # Running locally - do initial scrape
        print("🔍 Running initial event scrape...")
        scheduler.run_pipeline()
    
    # Start web server (cloud-optimized)
    port = int(os.environ.get('PORT', os.getenv('FLASK_PORT', 5000)))
    host = '0.0.0.0'  # Required for cloud hosting
    
    if os.environ.get('PORT'):
        print(f"☁️ Starting Nigerian Event Pipeline on Render (port {port})")
        print("🌍 Global access ready!")
        print("📱 Mobile-optimized dashboard!")
    else:
        print(f"🌐 Starting web server on http://{host}:{port}")
        print(f"📱 Local access: http://localhost:{port}")
        print("📊 View your events dashboard at the URLs above")
        print("\n💡 For mobile access from anywhere:")
        print("   🔥 Best: Setup Cloudflare Tunnel (run: python setup_cloudflare_tunnel.py)")
        print("   ⚡ Quick: Setup ngrok (run: python setup_ngrok.py)")
    
    app.run(host=host, port=port, debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')

if __name__ == "__main__":
    main()
