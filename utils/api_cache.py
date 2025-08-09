#!/usr/bin/env python3
"""
API Cache Manager - Smart caching to reduce API calls
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class APICache:
    """Smart caching system to reduce Google API calls"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Cache durations (in hours)
        self.cache_durations = {
            'search': 2,        # Search results cache for 2 hours
            'social': 4,        # Social media cache for 4 hours  
            'news': 1,          # News cache for 1 hour
        }
    
    def _get_cache_key(self, query: str, query_type: str = 'search') -> str:
        """Generate cache key from query"""
        query_hash = hashlib.md5(f"{query}_{query_type}".encode()).hexdigest()
        return f"{query_type}_{query_hash}.json"
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get full path to cache file"""
        return os.path.join(self.cache_dir, cache_key)
    
    def get(self, query: str, query_type: str = 'search') -> Optional[Dict[Any, Any]]:
        """Get cached result if valid"""
        cache_key = self._get_cache_key(query, query_type)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid
            cached_time = datetime.fromisoformat(cache_data.get('timestamp', ''))
            cache_duration = timedelta(hours=self.cache_durations.get(query_type, 2))
            
            if datetime.now() - cached_time < cache_duration:
                print(f"📦 Using cached result for: {query[:50]}...")
                return cache_data.get('results')
            else:
                # Cache expired, remove it
                os.remove(cache_path)
                return None
                
        except (json.JSONDecodeError, ValueError, KeyError):
            # Invalid cache file, remove it
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return None
    
    def set(self, query: str, results: Dict[Any, Any], query_type: str = 'search') -> None:
        """Cache search results"""
        cache_key = self._get_cache_key(query, query_type)
        cache_path = self._get_cache_path(cache_key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'query_type': query_type,
            'results': results
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Cached result for: {query[:50]}...")
        except Exception as e:
            print(f"⚠️  Failed to cache result: {e}")
    
    def clear_expired(self) -> int:
        """Clear all expired cache files"""
        cleared = 0
        if not os.path.exists(self.cache_dir):
            return cleared
        
        for filename in os.listdir(self.cache_dir):
            if not filename.endswith('.json'):
                continue
                
            cache_path = os.path.join(self.cache_dir, filename)
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cache_data.get('timestamp', ''))
                query_type = cache_data.get('query_type', 'search')
                cache_duration = timedelta(hours=self.cache_durations.get(query_type, 2))
                
                if datetime.now() - cached_time >= cache_duration:
                    os.remove(cache_path)
                    cleared += 1
                    
            except (json.JSONDecodeError, ValueError, KeyError):
                # Invalid cache file, remove it
                os.remove(cache_path)
                cleared += 1
        
        if cleared > 0:
            print(f"🧹 Cleared {cleared} expired cache files")
        return cleared
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        stats = {'total': 0, 'valid': 0, 'expired': 0}
        
        if not os.path.exists(self.cache_dir):
            return stats
        
        for filename in os.listdir(self.cache_dir):
            if not filename.endswith('.json'):
                continue
            
            stats['total'] += 1
            cache_path = os.path.join(self.cache_dir, filename)
            
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cache_data.get('timestamp', ''))
                query_type = cache_data.get('query_type', 'search')
                cache_duration = timedelta(hours=self.cache_durations.get(query_type, 2))
                
                if datetime.now() - cached_time < cache_duration:
                    stats['valid'] += 1
                else:
                    stats['expired'] += 1
                    
            except (json.JSONDecodeError, ValueError, KeyError):
                stats['expired'] += 1
        
        return stats

# Global cache instance
api_cache = APICache()
