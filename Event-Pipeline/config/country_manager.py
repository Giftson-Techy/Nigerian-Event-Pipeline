"""
Country Configuration Manager
Handles country-specific event search settings
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class CountryManager:
    """Manages country-specific search configurations"""
    
    def __init__(self):
        self.country_configs = {
            'Nigeria': {
                'search_terms': [
                    # Major Cities Comprehensive Coverage
                    'events in Lagos Nigeria', 'Lagos events today', 'Lagos business conference', 'Lagos tech events',
                    'events in Abuja Nigeria', 'Abuja events today', 'Abuja government events', 'Abuja networking',
                    'events in Kano Nigeria', 'Kano events', 'Kano business expo', 'Kano cultural festival',
                    'events in Ibadan Nigeria', 'Ibadan events', 'Ibadan university events', 'Ibadan conference',
                    'events in Port Harcourt Nigeria', 'Port Harcourt events', 'Port Harcourt oil gas conference',
                    'events in Benin City Nigeria', 'Benin City events', 'Benin cultural events',
                    'events in Enugu Nigeria', 'Enugu events', 'Enugu business conference', 'Enugu coal city events',
                    'events in Kaduna Nigeria', 'Kaduna events', 'Kaduna northern conference',
                    'events in Jos Nigeria', 'Jos events', 'Jos plateau events', 'Jos mining conference',
                    'events in Calabar Nigeria', 'Calabar events', 'Calabar carnival', 'Calabar tourism',
                    'events in Warri Nigeria', 'Warri events', 'Warri delta conference',
                    'events in Aba Nigeria', 'Aba events', 'Aba business expo',
                    'events in Onitsha Nigeria', 'Onitsha events', 'Onitsha trade fair',
                    'events in Uyo Nigeria', 'Uyo events', 'Uyo Akwa Ibom events',
                    'events in Maiduguri Nigeria', 'Maiduguri events', 'Maiduguri Borno events',
                    
                    # State-Level Events
                    'events Lagos state Nigeria', 'events Kano state Nigeria', 'events Rivers state Nigeria',
                    'events Oyo state Nigeria', 'events Kaduna state Nigeria', 'events Plateau state Nigeria',
                    'events Cross River state Nigeria', 'events Enugu state Nigeria', 'events Delta state Nigeria',
                    
                    # Multi-City and Nationwide Events
                    'events across Nigeria', 'Nigerian events 2025', 'nationwide events Nigeria',
                    'events Lagos Abuja Kano', 'pan-Nigeria conference', 'Nigeria tour events',
                    'multi-city events Nigeria', 'events all Nigeria cities',
                    
                    # Event Types Across Nigeria
                    'Nigerian tech conferences', 'Nigerian business summit', 'Nigerian cultural festivals',
                    'Nigerian music events', 'Nigerian art exhibitions', 'Nigerian startup events',
                    'Nigerian academic conferences', 'Nigerian trade fairs', 'Nigerian networking events',
                    'Nigerian entertainment events', 'Nigerian sports events', 'Nigerian religious events',
                    
                    # Regional and Zonal Events
                    'events northern Nigeria', 'events southern Nigeria', 'events western Nigeria',
                    'events eastern Nigeria', 'events middle belt Nigeria', 'events south south Nigeria',
                    'events north central Nigeria', 'events north east Nigeria', 'events north west Nigeria',
                    'events south east Nigeria', 'events south west Nigeria'
                ],
                'cities': [
                    # All Major Nigerian Cities (50+ cities for comprehensive coverage)
                    'Lagos', 'Abuja', 'Kano', 'Ibadan', 'Port Harcourt', 'Benin City', 'Maiduguri',
                    'Zaria', 'Aba', 'Jos', 'Ilorin', 'Onitsha', 'Kaduna', 'Enugu', 'Warri',
                    'Calabar', 'Uyo', 'Sokoto', 'Owerri', 'Abeokuta', 'Bauchi', 'Akure',
                    'Makurdi', 'Minna', 'Ikeja', 'Yenagoa', 'Jalingo', 'Lafia', 'Ado-Ekiti',
                    'Gombe', 'Abakaliki', 'Osogbo', 'Katsina', 'Birnin Kebbi', 'Dutse',
                    'Asaba', 'Awka', 'Damaturu', 'Gusau', 'Lokoja', 'Nsukka', 'Ile-Ife',
                    'Ogbomoso', 'Ondo', 'Ekpoma', 'Umuahia', 'Afikpo', 'Orlu', 'Sapele',
                    'Agbor', 'Okene', 'Offa', 'Ejigbo', 'Gboko', 'Keffi', 'Pankshin'
                ],
                'popular_venues': [
                    'Eko Hotel Lagos', 'Landmark Centre Lagos', 'Transcorp Hilton Abuja', 'Oriental Hotel Lagos',
                    'Shehu Musa Yar\'Adua Centre Abuja', 'Nike Art Gallery Lagos', 'National Theatre Lagos',
                    'International Conference Centre Abuja', 'Lagos Continental Hotel', 'Sheraton Lagos',
                    'Nicon Luxury Abuja', 'Hotel Presidential Port Harcourt', 'Golden Tulip Port Harcourt'
                ],
                'local_sites': [
                    'nairaland.com', 'bellanaija.com', 'pulse.ng', 'vanguardngr.com', 'punchng.com',
                    'thenationonlineng.net', 'dailytrust.com', 'premiumtimesng.com', 'thisdaylive.com',
                    'channelstv.com', 'legit.ng', 'nollywoodreporter.com', 'techcabal.com'
                ],
                'time_zone': 'Africa/Lagos',
                'currency': 'NGN'
            },
            'United States': {
                'search_terms': [
                    'events in USA', 'New York events', 'Los Angeles events', 'Chicago events',
                    'US concerts', 'American festivals', 'US conferences', 'NYC events',
                    'California events', 'Texas events', 'Florida events', 'US tech events'
                ],
                'cities': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'],
                'popular_venues': ['Madison Square Garden', 'Hollywood Bowl', 'Staples Center'],
                'local_sites': ['eventbrite.com', 'meetup.com', 'facebook.com/events'],
                'time_zone': 'America/New_York',
                'currency': 'USD'
            },
            'United Kingdom': {
                'search_terms': [
                    'events in UK', 'London events', 'Manchester events', 'Birmingham events',
                    'UK concerts', 'British festivals', 'UK conferences', 'London shows',
                    'Edinburgh events', 'Glasgow events', 'UK tech events', 'British cultural events'
                ],
                'cities': ['London', 'Birmingham', 'Manchester', 'Leeds', 'Glasgow', 'Sheffield', 'Bradford', 'Liverpool', 'Edinburgh', 'Bristol'],
                'popular_venues': ['O2 Arena', 'Royal Albert Hall', 'Wembley Stadium'],
                'local_sites': ['eventbrite.co.uk', 'meetup.com', 'timeout.com'],
                'time_zone': 'Europe/London',
                'currency': 'GBP'
            },
            'Canada': {
                'search_terms': [
                    'events in Canada', 'Toronto events', 'Vancouver events', 'Montreal events',
                    'Canadian concerts', 'Canada festivals', 'Canadian conferences', 'Calgary events',
                    'Ottawa events', 'Edmonton events', 'Canadian tech events', 'Quebec events'
                ],
                'cities': ['Toronto', 'Montreal', 'Vancouver', 'Calgary', 'Ottawa', 'Edmonton', 'Mississauga', 'Winnipeg', 'Quebec City', 'Hamilton'],
                'popular_venues': ['Rogers Centre', 'Bell Centre', 'Scotiabank Arena'],
                'local_sites': ['eventbrite.ca', 'meetup.com', 'narcity.com'],
                'time_zone': 'America/Toronto',
                'currency': 'CAD'
            },
            'Australia': {
                'search_terms': [
                    'events in Australia', 'Sydney events', 'Melbourne events', 'Brisbane events',
                    'Australian concerts', 'Australia festivals', 'Australian conferences', 'Perth events',
                    'Adelaide events', 'Gold Coast events', 'Australian tech events', 'Aussie events'
                ],
                'cities': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Gold Coast', 'Newcastle', 'Canberra', 'Sunshine Coast', 'Wollongong'],
                'popular_venues': ['Sydney Opera House', 'Rod Laver Arena', 'Suncorp Stadium'],
                'local_sites': ['eventbrite.com.au', 'meetup.com', 'timeout.com'],
                'time_zone': 'Australia/Sydney',
                'currency': 'AUD'
            }
        }
        
        # Load current settings
        self.available_countries = os.getenv('SEARCH_COUNTRIES', 'Nigeria,United States').split(',')
        self.default_country = os.getenv('DEFAULT_COUNTRY', 'Nigeria').strip()
        self.include_global = os.getenv('INCLUDE_GLOBAL_EVENTS', 'true').lower() == 'true'
        
        # Current active country
        self.current_country = self.default_country
    
    def get_available_countries(self) -> List[str]:
        """Get list of available countries"""
        return [country.strip() for country in self.available_countries]
    
    def set_current_country(self, country: str) -> bool:
        """Set the current country for searches"""
        if country in self.country_configs:
            self.current_country = country
            return True
        return False
    
    def get_current_country(self) -> str:
        """Get the current active country"""
        return self.current_country
    
    def get_country_search_terms(self, country: str = None) -> List[str]:
        """Get search terms for a specific country"""
        country = country or self.current_country
        
        if country in self.country_configs:
            terms = self.country_configs[country]['search_terms'].copy()
            
            # Add global events if enabled
            if self.include_global:
                global_terms = [
                    'upcoming events', 'concerts this week', 'festivals 2025',
                    'conferences events', 'workshops seminars', 'tech conferences',
                    'business networking events', 'live music events', 'art exhibitions'
                ]
                terms.extend(global_terms)
            
            return terms
        
        return ['upcoming events', 'concerts', 'festivals', 'conferences']
    
    def get_country_cities(self, country: str = None) -> List[str]:
        """Get major cities for a country"""
        country = country or self.current_country
        return self.country_configs.get(country, {}).get('cities', [])
    
    def get_country_info(self, country: str = None) -> Dict:
        """Get complete country information"""
        country = country or self.current_country
        return self.country_configs.get(country, {})
    
    def get_localized_search_queries(self, base_query: str, country: str = None) -> List[str]:
        """Generate localized search queries for a country"""
        country = country or self.current_country
        country_info = self.get_country_info(country)
        
        queries = []
        
        # Add country-specific query
        queries.append(f"{base_query} in {country}")
        
        # Add city-specific queries for major cities
        cities = country_info.get('cities', [])[:5]  # Top 5 cities
        for city in cities:
            queries.append(f"{base_query} in {city}")
        
        # Add the base query
        queries.append(base_query)
        
        return queries
    
    def update_country_list(self, countries: List[str]):
        """Update the list of available countries"""
        self.available_countries = countries
        
        # Update .env file
        env_path = '.env'
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                content = f.read()
            
            # Update SEARCH_COUNTRIES line
            import re
            pattern = r'SEARCH_COUNTRIES=.*'
            replacement = f"SEARCH_COUNTRIES={','.join(countries)}"
            
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
            else:
                content += f"\nSEARCH_COUNTRIES={','.join(countries)}"
            
            with open(env_path, 'w') as f:
                f.write(content)

# Global instance
country_manager = CountryManager()
