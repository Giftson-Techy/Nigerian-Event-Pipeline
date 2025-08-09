#!/usr/bin/env python3
"""
Event Pipeline - Mai    print(f"🌐 Starting web server on http://{host}:{port}")
    print(f"📱 Local access: http://localhost:{port}")
    print(f"📱 Network access: http://10.233.205.205:{port}")
    print("📊 View your events dashboard at the URLs above")
    print("\n💡 For mobile access from anywhere:")
    print("   🆓 FREE: Register at cloudflare.com → Get FREE tunnel URL")
    print("   ⚡ Quick: Register at ngrok.com → Get FREE tunnel URL") Point
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
    
    # Run initial scrape
    print("🔍 Running initial event scrape...")
    scheduler.run_pipeline()
    
    # Start web server (accessible from network for mobile access)
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')  # 0.0.0.0 allows network access
    
    print(f"🌐 Starting web server on http://{host}:{port}")
    print(f"📱 Local access: http://localhost:{port}")
    print(f"� Network access: http://YOUR_LOCAL_IP:{port}")
    print("�📊 View your events dashboard at the URLs above")
    print("\n💡 For mobile access from anywhere:")
    print("   🔥 Best: Setup Cloudflare Tunnel (run: python setup_cloudflare_tunnel.py)")
    print("   ⚡ Quick: Setup ngrok (run: python setup_ngrok.py)")
    
    app.run(host=host, port=port, debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')

if __name__ == "__main__":
    main()
