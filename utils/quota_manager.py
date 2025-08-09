#!/usr/bin/env python3
"""
Quota Manager - Smart Google API quota management
Ensures we never exceed 100 calls per day
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class QuotaManager:
    """Manages Google API quota to stay within 100 calls/day limit"""
    
    def __init__(self, quota_file: str = "quota_tracking.json"):
        self.quota_file = quota_file
        self.daily_limit = 100  # Google free tier limit
        self.safety_buffer = 10  # Keep 10 calls as buffer
        self.usable_quota = self.daily_limit - self.safety_buffer  # 90 calls
        
        # Priority levels for different query types
        self.priority_weights = {
            'urgent': 1.0,      # Highest priority (today's events, conferences)
            'high': 0.8,        # High priority (major cities, business events)
            'medium': 0.6,      # Medium priority (smaller cities, specific topics)
            'low': 0.4,         # Low priority (very specific or niche events)
            'social': 0.3       # Social media (can be cached longer)
        }
        
        self.load_quota_data()
    
    def load_quota_data(self) -> Dict:
        """Load today's quota usage"""
        try:
            if os.path.exists(self.quota_file):
                with open(self.quota_file, 'r') as f:
                    data = json.load(f)
                
                # Check if data is from today
                last_date = datetime.fromisoformat(data.get('date', ''))
                if last_date.date() == datetime.now().date():
                    return data
            
            # Create new quota data for today
            return self.reset_daily_quota()
            
        except Exception as e:
            logger.error(f"Error loading quota data: {e}")
            return self.reset_daily_quota()
    
    def reset_daily_quota(self) -> Dict:
        """Reset quota for new day"""
        quota_data = {
            'date': datetime.now().isoformat(),
            'calls_used': 0,
            'calls_remaining': self.usable_quota,
            'query_history': []
        }
        self.save_quota_data(quota_data)
        logger.info(f"🔄 New day! Reset quota: {self.usable_quota} calls available")
        return quota_data
    
    def save_quota_data(self, data: Dict) -> None:
        """Save quota data to file"""
        try:
            with open(self.quota_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving quota data: {e}")
    
    def get_quota_status(self) -> Dict:
        """Get current quota status"""
        data = self.load_quota_data()
        return {
            'calls_used': data['calls_used'],
            'calls_remaining': data['calls_remaining'],
            'percentage_used': (data['calls_used'] / self.usable_quota) * 100,
            'can_make_calls': data['calls_remaining'] > 0
        }
    
    def can_make_calls(self, num_calls: int) -> bool:
        """Check if we can make specified number of calls"""
        status = self.get_quota_status()
        return status['calls_remaining'] >= num_calls
    
    def record_api_call(self, query: str, query_type: str = 'search') -> bool:
        """Record an API call and update quota"""
        data = self.load_quota_data()
        
        if data['calls_remaining'] <= 0:
            logger.warning(f"🚫 Quota exhausted! Cannot make call for: {query[:50]}")
            return False
        
        # Record the call
        data['calls_used'] += 1
        data['calls_remaining'] -= 1
        data['query_history'].append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'type': query_type
        })
        
        self.save_quota_data(data)
        
        # Log status
        percentage = (data['calls_used'] / self.usable_quota) * 100
        logger.info(f"📊 API Call #{data['calls_used']}: {query[:30]}... ({percentage:.1f}% quota used)")
        
        # Warn when approaching limit
        if data['calls_remaining'] <= 20:
            logger.warning(f"⚠️ Only {data['calls_remaining']} API calls remaining today!")
        elif data['calls_remaining'] <= 5:
            logger.error(f"🚨 CRITICAL: Only {data['calls_remaining']} API calls left!")
        
        return True
    
    def get_prioritized_queries(self, all_queries: List[Dict], max_calls: int) -> List[Dict]:
        """Get prioritized subset of queries that fit within quota"""
        # Sort by priority (urgent first)
        sorted_queries = sorted(all_queries, key=lambda x: self.priority_weights.get(x.get('priority', 'medium'), 0.5), reverse=True)
        
        # Take top queries that fit within quota
        selected = sorted_queries[:max_calls]
        
        logger.info(f"🎯 Selected {len(selected)}/{len(all_queries)} queries (quota limit: {max_calls})")
        return selected
    
    def distribute_daily_quota(self) -> Dict[str, int]:
        """Distribute daily quota across different pipeline runs"""
        status = self.get_quota_status()
        remaining = status['calls_remaining']
        
        # Calculate runs per day:
        # - Comprehensive: Every 60 min = 24 runs/day
        # - Quick: Every 30 min = 48 runs/day  
        # - Social: Every 45 min = 32 runs/day
        # Total: 104 runs/day
        
        # Allocate quota strategically
        allocation = {
            'comprehensive': max(1, remaining // 3),      # 1/3 for comprehensive
            'quick': max(1, remaining // 6),              # 1/6 for quick
            'social': max(1, remaining // 8),             # 1/8 for social
            'emergency': max(5, remaining // 10)          # Keep some for emergencies
        }
        
        # Ensure we don't exceed remaining quota
        total_allocated = sum(allocation.values())
        if total_allocated > remaining:
            # Scale down proportionally
            scale = remaining / total_allocated
            for key in allocation:
                allocation[key] = max(1, int(allocation[key] * scale))
        
        logger.info(f"📋 Daily quota allocation: {allocation}")
        return allocation

# Global quota manager instance
quota_manager = QuotaManager()
