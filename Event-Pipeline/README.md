# Event Pipeline

An automated event discovery pipeline that crawls search engines, social media APIs, and news sites to find upcoming events with **country-specific filtering**.

## Features

- **🇳🇬 Nigeria-focused by default**: Optimized for Nigerian events (Lagos, Abuja, etc.)
- **🌍 Multi-country support**: Switch between Nigeria, US, UK, Canada, Australia
- **🔍 Smart filtering**: Removes non-relevant geographic results
- **Multi-source scraping**: Google Search, Bing, news sites, social media
- **Automated scheduling**: Runs every 15 minutes
- **Clickable links**: Web interface with direct links to events
- **Data persistence**: SQLite database for storing events
- **Duplicate detection**: Prevents duplicate events
- **Real-time updates**: Live web dashboard

## Quick Start (Nigeria Events)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the pipeline (Nigeria is default):
```bash
python main.py
```

3. View Nigerian events at: http://localhost:5000

4. Change countries via the dropdown in the web interface or:
```bash
python country_config.py
```

## Configuration

### API Keys (Optional)
Create `.env` file for enhanced results:
```
TWITTER_BEARER_TOKEN=your_token
GOOGLE_API_KEY=your_key
GOOGLE_CSE_ID=your_cse_id
FACEBOOK_ACCESS_TOKEN=your_token
EVENTBRITE_TOKEN=your_token
```

### Country Settings
The pipeline is pre-configured for Nigeria with:
- **Nigerian search terms**: "Lagos events", "Abuja conferences", "Nigerian concerts"
- **Major cities**: Lagos, Abuja, Kano, Ibadan, Port Harcourt
- **Geographic filtering**: Excludes events from other countries
- **Local context**: Nigerian venues, time zones, currency

## Structure

- `scrapers/` - Web scraping modules with country filtering
- `apis/` - Social media API integrations
- `database/` - Database models and operations
- `web/` - Web interface with country selection
- `config/` - Country management and settings
- `scheduler.py` - Automated scheduling
- `main.py` - Entry point

## Country Management

### Available Countries
- 🇳🇬 **Nigeria** (Default) - Lagos, Abuja, Kano, Ibadan, Port Harcourt
- 🇺🇸 United States - NYC, LA, Chicago, Houston, Phoenix
- 🇬🇧 United Kingdom - London, Manchester, Birmingham, Leeds
- 🇨🇦 Canada - Toronto, Montreal, Vancouver, Calgary
- 🇦🇺 Australia - Sydney, Melbourne, Brisbane, Perth

### Change Country
1. **Web Interface**: Use dropdown in dashboard header
2. **Command Line**: `python country_config.py`
3. **API**: `POST /api/set-country {"country": "Nigeria"}`

### Nigerian Event Types
The pipeline searches for:
- 🎵 Concerts and music events in Lagos/Abuja
- 🏢 Business conferences and networking
- 💻 Tech events and startup meetups
- 🎨 Cultural festivals and art exhibitions
- 🍽️ Food festivals and social events
- 🎭 Entertainment and nightlife events

## Troubleshooting

### Getting Non-Nigerian Events?
1. Check current country: Visit `/countries` page
2. Clear database: `del events.db` and restart
3. Run cleanup: `python cleanup_database.py`

### No Events Found?
1. Check internet connection
2. Wait for 15-minute pipeline cycle
3. Force refresh: Restart `python main.py`
