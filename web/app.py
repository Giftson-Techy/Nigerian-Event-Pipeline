"""
Flask Web Application - Event Dashboard
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from config.country_manager import country_manager

def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    
    db_manager = DatabaseManager()
    
    @app.route('/')
    def index():
        """Main dashboard page"""
        # Get recent events
        events = db_manager.get_all_events(limit=20)
        
        # Get statistics
        total_events = db_manager.get_event_count()
        sources_summary = db_manager.get_sources_summary()
        
        # Get current country
        current_country = country_manager.get_current_country()
        
        return render_template('index.html', 
                             events=events, 
                             total_events=total_events,
                             sources_summary=sources_summary,
                             current_country=current_country)
    
    @app.route('/api/events')
    def api_events():
        """API endpoint for events"""
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        source = request.args.get('source', '')
        search = request.args.get('search', '')
        
        offset = (page - 1) * limit
        
        if search:
            events = db_manager.search_events(search)
        elif source:
            events = db_manager.get_events_by_source(source)
        else:
            events = db_manager.get_all_events(limit=limit, offset=offset)
        
        return jsonify({
            'events': events,
            'total': len(events),
            'page': page,
            'limit': limit
        })
    
    @app.route('/api/sources')
    def api_sources():
        """API endpoint for sources summary"""
        sources = db_manager.get_sources_summary()
        return jsonify(sources)
    
    @app.route('/api/stats')
    def api_stats():
        """API endpoint for statistics"""
        stats = {
            'total_events': db_manager.get_event_count(),
            'sources': db_manager.get_sources_summary()
        }
        return jsonify(stats)
    
    @app.route('/events/<source>')
    def events_by_source(source):
        """Events filtered by source"""
        # Handle Google Search to show all search engine results
        if source == 'Google Search':
            # Get both Google and Bing search results
            events = []
            google_events = db_manager.get_events_by_source('Google Search')
            bing_events = db_manager.get_events_by_source('Bing Search')
            events.extend(google_events)
            events.extend(bing_events)
            
            # Sort by creation date (newest first)
            events.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        elif source == 'Social Media':
            # Get all social media platform events
            events = []
            social_sources = ['LinkedIn (via Google)', 'Facebook (via Google)', 'Instagram (via Google)', 
                            'Twitter/X (via Google)', 'Eventbrite (via Google)', 'Meetup (via Google)', 
                            'Nairaland (via Google)', 'Social Media']
            
            for social_source in social_sources:
                platform_events = db_manager.get_events_by_source(social_source)
                events.extend(platform_events)
            
            # Sort by creation date (newest first)
            events.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        else:
            events = db_manager.get_events_by_source(source)
            
        sources_summary = db_manager.get_sources_summary()
        
        return render_template('events.html', 
                             events=events, 
                             current_source=source,
                             sources_summary=sources_summary)
    
    @app.route('/search')
    def search_events():
        """Search events"""
        query = request.args.get('q', '')
        events = db_manager.search_events(query) if query else []
        
        return render_template('search.html', 
                             events=events, 
                             query=query)
    
    @app.route('/countries')
    def country_settings():
        """Country selection page"""
        available_countries = country_manager.get_available_countries()
        current_country = country_manager.get_current_country()
        country_info = country_manager.get_country_info()
        
        return render_template('countries.html',
                             available_countries=available_countries,
                             current_country=current_country,
                             country_info=country_info)
    
    @app.route('/api/countries')
    def api_countries():
        """API endpoint for country information"""
        return jsonify({
            'available_countries': country_manager.get_available_countries(),
            'current_country': country_manager.get_current_country(),
            'country_info': country_manager.get_country_info()
        })
    
    @app.route('/api/set-country', methods=['POST'])
    def api_set_country():
        """API endpoint to set current country"""
        data = request.get_json()
        country = data.get('country', '')
        
        if country_manager.set_current_country(country):
            return jsonify({
                'success': True, 
                'message': f'Country set to {country}',
                'current_country': country
            })
        else:
            return jsonify({
                'success': False, 
                'message': f'Invalid country: {country}'
            }), 400
    
    @app.route('/set-country/<country>')
    def set_country(country):
        """Set country and redirect to dashboard"""
        if country_manager.set_current_country(country):
            flash(f'Country set to {country}. New events will be searched for this location.', 'success')
        else:
            flash(f'Invalid country: {country}', 'error')
        
        return redirect(url_for('index'))
    
    @app.route('/test-country')
    def test_country():
        """Test page for country functionality"""
        return render_template('test_country.html')
    
    return app
