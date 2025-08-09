"""
Database Manager - SQLite database operations for events
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for events"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv('DATABASE_PATH', 'events.db')
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def initialize_database(self):
        """Create database tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    url TEXT NOT NULL,
                    source TEXT NOT NULL,
                    location TEXT,
                    event_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    hash TEXT UNIQUE NOT NULL,
                    category TEXT,
                    image_url TEXT,
                    price TEXT,
                    organizer TEXT
                )
            ''')
            
            # Index for faster searches
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_hash ON events(hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_source ON events(source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date)')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def generate_event_hash(self, event: Dict) -> str:
        """Generate unique hash for event to prevent duplicates"""
        content = f"{event.get('title', '')}{event.get('url', '')}{event.get('event_date', '')}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def save_events(self, events: List[Dict]) -> int:
        """Save events to database, avoiding duplicates"""
        if not events:
            return 0
        
        saved_count = 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for event in events:
                try:
                    # Generate hash for duplicate detection
                    event_hash = self.generate_event_hash(event)
                    
                    # Check if event already exists
                    cursor.execute('SELECT id FROM events WHERE hash = ?', (event_hash,))
                    if cursor.fetchone():
                        continue  # Skip duplicate
                    
                    # Insert new event
                    cursor.execute('''
                        INSERT INTO events (
                            title, description, url, source, location, 
                            event_date, hash, category, image_url, price, organizer
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        event.get('title', ''),
                        event.get('description', ''),
                        event.get('url', ''),
                        event.get('source', ''),
                        event.get('location', ''),
                        event.get('event_date', ''),
                        event_hash,
                        event.get('category', ''),
                        event.get('image_url', ''),
                        event.get('price', ''),
                        event.get('organizer', '')
                    ))
                    saved_count += 1
                    
                except sqlite3.Error as e:
                    logger.error(f"Error saving event: {e}")
                    continue
            
            conn.commit()
        
        logger.info(f"Saved {saved_count} new events to database")
        return saved_count
    
    def get_all_events(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all events from database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM events 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            columns = [description[0] for description in cursor.description]
            events = []
            
            for row in cursor.fetchall():
                event = dict(zip(columns, row))
                events.append(event)
            
            return events
    
    def get_events_by_source(self, source: str) -> List[Dict]:
        """Get events from specific source"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM events 
                WHERE source = ? 
                ORDER BY created_at DESC
            ''', (source,))
            
            columns = [description[0] for description in cursor.description]
            events = []
            
            for row in cursor.fetchall():
                event = dict(zip(columns, row))
                events.append(event)
            
            return events
    
    def search_events(self, query: str) -> List[Dict]:
        """Search events by title or description"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM events 
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY created_at DESC
            ''', (f'%{query}%', f'%{query}%'))
            
            columns = [description[0] for description in cursor.description]
            events = []
            
            for row in cursor.fetchall():
                event = dict(zip(columns, row))
                events.append(event)
            
            return events
    
    def cleanup_old_events(self, days: int = 30):
        """Remove events older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM events 
                WHERE created_at < ?
            ''', (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old events")
    
    def get_event_count(self) -> int:
        """Get total number of events"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM events')
            return cursor.fetchone()[0]
    
    def get_sources_summary(self) -> List[Dict]:
        """Get summary of events by source"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT source, COUNT(*) as count, MAX(created_at) as last_updated
                FROM events 
                GROUP BY source 
                ORDER BY count DESC
            ''')
            
            sources = []
            for row in cursor.fetchall():
                sources.append({
                    'source': row[0],
                    'count': row[1],
                    'last_updated': row[2]
                })
            
            return sources
