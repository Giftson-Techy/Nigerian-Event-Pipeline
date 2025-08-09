"""
Comprehensive Nigerian Cities and States Configuration
Covers all 36 states plus FCT for complete event discovery
"""

# All 36 Nigerian States plus FCT
NIGERIAN_STATES = [
    'Lagos', 'Kano', 'Kaduna', 'Oyo', 'Rivers', 'Bayelsa', 'Katsina', 'Cross River',
    'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Benue', 'Borno', 'Delta',
    'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'Gombe', 'Imo', 'Jigawa', 'Kebbi', 'Kogi',
    'Kwara', 'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun', 'Plateau', 'Sokoto',
    'Taraba', 'Yobe', 'Zamfara', 'FCT'  # Federal Capital Territory (Abuja)
]

# Major Nigerian Cities (Population > 500k)
MAJOR_NIGERIAN_CITIES = [
    'Lagos', 'Kano', 'Ibadan', 'Abuja', 'Port Harcourt', 'Benin City', 'Maiduguri',
    'Zaria', 'Aba', 'Jos', 'Ilorin', 'Onitsha', 'Kaduna', 'Enugu', 'Warri',
    'Calabar', 'Uyo', 'Sokoto', 'Owerri', 'Abeokuta', 'Bauchi', 'Akure',
    'Makurdi', 'Minna', 'Effon Alaaye', 'Ikeja', 'Yenagoa', 'Jalingo',
    'Lafia', 'Ado-Ekiti', 'Gombe', 'Abakaliki', 'Osogbo', 'Katsina',
    'Birnin Kebbi', 'Dutse', 'Asaba', 'Awka', 'Damaturu', 'Gusau'
]

# Economic/Commercial Hubs
NIGERIAN_COMMERCIAL_HUBS = [
    'Lagos', 'Abuja', 'Port Harcourt', 'Kano', 'Ibadan', 'Kaduna', 'Enugu',
    'Warri', 'Aba', 'Onitsha', 'Jos', 'Calabar', 'Benin City', 'Maiduguri'
]

# University Towns (High event activity)
NIGERIAN_UNIVERSITY_CITIES = [
    'Nsukka', 'Ile-Ife', 'Zaria', 'Ilorin', 'Benin City', 'Jos', 'Akure',
    'Makurdi', 'Minna', 'Ogbomoso', 'Ondo', 'Ekpoma', 'Awka', 'Umuahia'
]

# Popular Event Keywords by Region
REGIONAL_EVENT_KEYWORDS = {
    'Lagos': ['tech conference', 'business summit', 'music festival', 'art exhibition', 'fashion show'],
    'Abuja': ['government event', 'diplomatic reception', 'policy conference', 'networking'],
    'Port Harcourt': ['oil gas conference', 'energy summit', 'business forum'],
    'Kano': ['trade fair', 'cultural festival', 'business expo', 'agricultural show'],
    'Enugu': ['coal city events', 'eastern conference', 'cultural celebration'],
    'Calabar': ['carnival', 'cultural festival', 'tourism event', 'hospitality conference'],
    'Jos': ['plateau events', 'mining conference', 'cultural gathering'],
    'Kaduna': ['northern conference', 'textile expo', 'agricultural fair'],
    'Ibadan': ['university event', 'academic conference', 'yoruba cultural event'],
    'Warri': ['oil gas event', 'delta conference', 'energy forum']
}

def get_comprehensive_nigerian_search_terms():
    """Generate comprehensive search terms covering all Nigerian locations"""
    terms = []
    
    # Basic Nigerian search terms
    base_terms = [
        'events', 'conference', 'summit', 'festival', 'concert', 'exhibition',
        'workshop', 'seminar', 'meetup', 'networking', 'business', 'cultural'
    ]
    
    # Add terms for major cities
    for city in MAJOR_NIGERIAN_CITIES[:20]:  # Top 20 cities
        for term in base_terms[:6]:  # Top 6 event types
            terms.append(f"{term} in {city}")
            terms.append(f"{city} {term}")
            terms.append(f"{term} {city} Nigeria")
    
    # Add state-level terms
    for state in NIGERIAN_STATES[:15]:  # Top 15 states
        terms.append(f"events in {state} state Nigeria")
        terms.append(f"{state} state events")
    
    # Add regional and cultural terms
    regional_terms = [
        'events Lagos Abuja Kano Port Harcourt',
        'Nigerian events 2025',
        'events across Nigeria',
        'nationwide events Nigeria',
        'multi-city events Nigeria',
        'Nigeria tour events',
        'all Nigeria events',
        'pan-Nigeria conference'
    ]
    terms.extend(regional_terms)
    
    return terms

def get_social_media_nigerian_queries():
    """Get comprehensive social media search queries for all Nigerian locations"""
    queries = []
    
    # LinkedIn Professional Events (by major cities)
    linkedin_cities = MAJOR_NIGERIAN_CITIES[:12]
    for city in linkedin_cities:
        queries.extend([
            f"site:linkedin.com {city} events conference networking 2025",
            f"site:linkedin.com {city} business meetup professional",
            f"site:linkedin.com Nigeria {city} events"
        ])
    
    # Facebook Events (by regions)
    facebook_regions = ['Lagos', 'Abuja', 'Port Harcourt', 'Kano', 'Ibadan', 'Enugu', 'Calabar', 'Jos']
    for region in facebook_regions:
        queries.extend([
            f"site:facebook.com {region} events concerts festivals",
            f"site:facebook.com Nigeria {region} events happening",
            f"site:facebook.com {region} weekend events"
        ])
    
    # Instagram Events (visual content)
    instagram_cities = ['Lagos', 'Abuja', 'Port Harcourt', 'Calabar', 'Enugu', 'Ibadan']
    for city in instagram_cities:
        queries.extend([
            f"site:instagram.com {city} events today weekend",
            f"site:instagram.com Nigeria {city} concerts festivals",
            f"site:instagram.com {city} events happening now"
        ])
    
    # Twitter/X (real-time updates)
    twitter_hashtags = ['#LagosEvents', '#AbujaEvents', '#NigerianEvents', '#NaijaEvents', '#9jaEvents']
    for hashtag in twitter_hashtags:
        queries.append(f"site:twitter.com {hashtag} events Nigeria")
    
    # Add multi-city searches
    queries.extend([
        "site:linkedin.com Nigeria events conference business networking",
        "site:facebook.com Nigeria events festivals concerts nationwide",
        "site:instagram.com Nigeria events cultural festivals music",
        "site:twitter.com Nigeria events #NigerianEvents #NaijaEvents",
        "site:eventbrite.com Nigeria events Lagos Abuja Port Harcourt",
        "site:nairaland.com events Lagos Abuja Kano Ibadan nationwide"
    ])
    
    return queries

def get_nigerian_news_search_terms():
    """Get news-specific search terms for Nigerian events"""
    return [
        'upcoming events Nigeria',
        'Nigerian events calendar',
        'events Lagos Abuja this week',
        'Nigerian concerts festivals 2025',
        'business conferences Nigeria',
        'cultural events Nigeria',
        'tech events Nigeria',
        'Nigerian entertainment events',
        'events across Nigerian cities',
        'nationwide events Nigeria'
    ]
