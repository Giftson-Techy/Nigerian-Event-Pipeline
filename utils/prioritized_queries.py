#!/usr/bin/env python3
"""
Prioritized Query Manager - Smart query prioritization for quota management
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class PrioritizedQueryManager:
    """Manages prioritized queries for optimal quota usage"""
    
    def __init__(self):
        # TIER 1: URGENT - Most important events (Priority: urgent)
        self.urgent_queries = [
            {"query": "events today Nigeria", "priority": "urgent", "type": "search"},
            {"query": "conferences this week Lagos", "priority": "urgent", "type": "search"},
            {"query": "business events Abuja today", "priority": "urgent", "type": "search"},
            {"query": "tech conferences Lagos 2025", "priority": "urgent", "type": "search"},
            {"query": "Nigeria summit today", "priority": "urgent", "type": "search"},
            {"query": "site:bellanaija.com events Lagos", "priority": "urgent", "type": "search"},
            {"query": "site:pulse.ng conferences Nigeria", "priority": "urgent", "type": "search"}
        ]
        
        # TIER 2: HIGH - Major cities and important events (Priority: high)
        self.high_priority_queries = [
            {"query": "Lagos business events", "priority": "high", "type": "search"},
            {"query": "Abuja conferences", "priority": "high", "type": "search"},
            {"query": "Port Harcourt events", "priority": "high", "type": "search"},
            {"query": "Nigeria oil gas conference", "priority": "high", "type": "search"},
            {"query": "Nigerian banking summit", "priority": "high", "type": "search"},
            {"query": "Lagos tech startup events", "priority": "high", "type": "search"},
            {"query": "site:vanguardngr.com events Nigeria", "priority": "high", "type": "search"},
            {"query": "site:premiumtimesng.com conferences Lagos", "priority": "high", "type": "search"},
            {"query": "site:thenationonlineng.net business events", "priority": "high", "type": "search"},
            {"query": "site:punchng.com summit Nigeria", "priority": "high", "type": "search"},
            {"query": "site:dailytrust.com conferences Abuja", "priority": "high", "type": "search"}
        ]
        
        # TIER 3: MEDIUM - Regional centers (Priority: medium)
        self.medium_priority_queries = [
            {"query": "Kaduna business events", "priority": "medium", "type": "search"},
            {"query": "Enugu conferences", "priority": "medium", "type": "search"},
            {"query": "Benin City events", "priority": "medium", "type": "search"},
            {"query": "Jos tech events", "priority": "medium", "type": "search"},
            {"query": "Warri oil events", "priority": "medium", "type": "search"},
            {"query": "Calabar conferences", "priority": "medium", "type": "search"},
            {"query": "Ilorin business summit", "priority": "medium", "type": "search"},
            {"query": "Maiduguri events", "priority": "medium", "type": "search"},
            {"query": "Aba trade events", "priority": "medium", "type": "search"},
            {"query": "Onitsha commerce events", "priority": "medium", "type": "search"}
        ]
        
        # TIER 4: LOW - Smaller cities and specific topics (Priority: low)
        self.low_priority_queries = [
            {"query": "Sokoto events", "priority": "low", "type": "search"},
            {"query": "Bauchi conferences", "priority": "low", "type": "search"},
            {"query": "Gombe business events", "priority": "low", "type": "search"},
            {"query": "Yola tech events", "priority": "low", "type": "search"},
            {"query": "Akure events", "priority": "low", "type": "search"},
            {"query": "Nigeria agriculture events", "priority": "low", "type": "search"},
            {"query": "Nigerian education summit", "priority": "low", "type": "search"},
            {"query": "Nigeria health conference", "priority": "low", "type": "search"},
            {"query": "Nigerian arts festival", "priority": "low", "type": "search"},
            {"query": "Nigeria sports events", "priority": "low", "type": "search"}
        ]
        
        # SOCIAL MEDIA QUERIES (Priority: social)
        self.social_media_queries = [
            {"query": "site:linkedin.com Lagos events", "priority": "social", "type": "social"},
            {"query": "site:facebook.com Abuja conferences", "priority": "social", "type": "social"},
            {"query": "site:twitter.com Nigeria business events", "priority": "social", "type": "social"},
            {"query": "site:instagram.com Lagos tech events", "priority": "social", "type": "social"},
            {"query": "site:eventbrite.com Nigeria conferences", "priority": "social", "type": "social"},
            {"query": "site:meetup.com Lagos tech meetup", "priority": "social", "type": "social"},
            {"query": "site:linkedin.com Nigeria summit", "priority": "social", "type": "social"},
            {"query": "site:facebook.com Port Harcourt events", "priority": "social", "type": "social"},
            {"query": "\"Nigeria event\" site:linkedin.com OR site:facebook.com", "priority": "social", "type": "social"},
            {"query": "\"Lagos conference\" site:twitter.com OR site:instagram.com", "priority": "social", "type": "social"},
            {"query": "\"Abuja summit\" site:linkedin.com", "priority": "social", "type": "social"},
            {"query": "\"Nigerian business event\" site:facebook.com", "priority": "social", "type": "social"},
            {"query": "site:nairaland.com events Lagos", "priority": "social", "type": "social"},
            {"query": "site:nairaland.com conferences Nigeria", "priority": "social", "type": "social"}
        ]
        
        # NIGERIAN MEDIA SITES - Specific news/event sites (Priority: media)
        self.nigerian_media_queries = [
            {"query": "site:bellanaija.com events OR conferences OR summit", "priority": "media", "type": "media"},
            {"query": "site:pulse.ng business events OR tech conference", "priority": "media", "type": "media"},
            {"query": "site:vanguardngr.com Lagos events OR Abuja conference", "priority": "media", "type": "media"},
            {"query": "site:premiumtimesng.com Nigeria summit OR business event", "priority": "media", "type": "media"},
            {"query": "site:thenationonlineng.net conferences OR events Nigeria", "priority": "media", "type": "media"},
            {"query": "site:punchng.com Lagos business OR tech events", "priority": "media", "type": "media"},
            {"query": "site:dailytrust.com Abuja events OR Northern Nigeria", "priority": "media", "type": "media"},
            {"query": "site:leadership.ng events OR conferences Nigeria", "priority": "media", "type": "media"},
            {"query": "site:businessday.ng Lagos summit OR investment", "priority": "media", "type": "media"},
            {"query": "site:guardian.ng Nigeria events OR conferences", "priority": "media", "type": "media"}
        ]
    
    def get_all_queries(self) -> List[Dict]:
        """Get all queries combined"""
        return (self.urgent_queries + 
                self.high_priority_queries + 
                self.medium_priority_queries + 
                self.low_priority_queries + 
                self.social_media_queries +
                self.nigerian_media_queries)
    
    def get_queries_by_priority(self, priority: str) -> List[Dict]:
        """Get queries by specific priority level"""
        priority_map = {
            'urgent': self.urgent_queries,
            'high': self.high_priority_queries,
            'medium': self.medium_priority_queries,
            'low': self.low_priority_queries,
            'social': self.social_media_queries,
            'media': self.nigerian_media_queries
        }
        return priority_map.get(priority, [])
    
    def get_comprehensive_queries(self, max_calls: int) -> List[Dict]:
        """Get prioritized queries for comprehensive pipeline"""
        all_queries = self.get_all_queries()
        
        # Sort by priority weight
        priority_weights = {'urgent': 6, 'high': 5, 'media': 4, 'medium': 3, 'social': 2, 'low': 1}
        sorted_queries = sorted(all_queries, 
                              key=lambda x: priority_weights.get(x['priority'], 0), 
                              reverse=True)
        
        selected = sorted_queries[:max_calls]
        
        logger.info(f"🎯 Comprehensive: Selected {len(selected)} queries from {len(all_queries)} total")
        
        # Log breakdown by priority
        breakdown = {}
        for q in selected:
            priority = q['priority']
            breakdown[priority] = breakdown.get(priority, 0) + 1
        
        logger.info(f"📊 Priority breakdown: {breakdown}")
        return selected
    
    def get_quick_queries(self, max_calls: int) -> List[Dict]:
        """Get urgent queries for quick updates"""
        # Only urgent and high priority for quick runs
        quick_queries = self.urgent_queries + self.high_priority_queries[:max_calls-len(self.urgent_queries)]
        
        selected = quick_queries[:max_calls]
        logger.info(f"⚡ Quick: Selected {len(selected)} urgent/high priority queries")
        return selected
    
    def get_social_queries(self, max_calls: int) -> List[Dict]:
        """Get social media queries"""
        selected = self.social_media_queries[:max_calls]
        logger.info(f"📱 Social: Selected {len(selected)} social media queries")
        return selected
    
    def get_media_queries(self, max_calls: int) -> List[Dict]:
        """Get Nigerian media site queries"""
        selected = self.nigerian_media_queries[:max_calls]
        logger.info(f"📰 Media: Selected {len(selected)} Nigerian media queries")
        return selected
    
    def get_query_stats(self) -> Dict:
        """Get statistics about available queries"""
        all_queries = self.get_all_queries()
        stats = {
            'total_queries': len(all_queries),
            'urgent': len(self.urgent_queries),
            'high': len(self.high_priority_queries),
            'medium': len(self.medium_priority_queries),
            'low': len(self.low_priority_queries),
            'social': len(self.social_media_queries),
            'media': len(self.nigerian_media_queries)
        }
        return stats

# Global query manager instance
query_manager = PrioritizedQueryManager()
