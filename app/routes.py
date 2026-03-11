from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from datetime import datetime, timedelta
from app import db
from app.models import URL, Analytics
from app.cache_service import CacheService
import re
from urllib.parse import urlparse

bp = Blueprint('main', __name__)

def get_limiter():
    return current_app.extensions['limiter']

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

@bp.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    
    if not data or not data.get('url'):
        return jsonify({'error': 'URL is required'}), 400
    
    original_url = data['url'].strip()
    
    if not is_valid_url(original_url):
        return jsonify({'error': 'Invalid URL format'}), 400
    
    expires_in_days = data.get('expires_in_days')
    expires_at = None
    if expires_in_days:
        try:
            days = int(expires_in_days)
            if days > 0:
                expires_at = datetime.utcnow() + timedelta(days=days)
        except ValueError:
            return jsonify({'error': 'expires_in_days must be a positive integer'}), 400
    
    custom_code = data.get('custom_code')
    if custom_code:
        if len(custom_code) < 3 or len(custom_code) > 10:
            return jsonify({'error': 'Custom code must be between 3 and 10 characters'}), 400
        if not re.match(r'^[a-zA-Z0-9_-]+$', custom_code):
            return jsonify({'error': 'Custom code can only contain letters, numbers, hyphens, and underscores'}), 400
        
        existing_url = URL.query.filter_by(short_code=custom_code.lower()).first()
        if existing_url:
            return jsonify({'error': 'Custom code already exists'}), 409
        short_code = custom_code.lower()
    else:
        max_attempts = 10
        for _ in range(max_attempts):
            short_code = URL.generate_short_code()
            existing_url = URL.query.filter_by(short_code=short_code).first()
            if not existing_url:
                break
        else:
            return jsonify({'error': 'Unable to generate unique short code'}), 500
    
    new_url = URL(
        original_url=original_url,
        short_code=short_code,
        expires_at=expires_at
    )
    
    try:
        db.session.add(new_url)
        db.session.commit()
        
        url_data = new_url.to_dict()
        CacheService.cache_url(url_data)
        
        return jsonify(url_data), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

@bp.route('/<short_code>', methods=['GET'])
def redirect_url(short_code):
    cached_url = CacheService.get_url_from_cache(short_code)
    
    if cached_url:
        if cached_url.get('expires_at') and datetime.fromisoformat(cached_url['expires_at']) < datetime.utcnow():
            CacheService.invalidate_cache(short_code)
            return jsonify({'error': 'URL has expired'}), 410
        
        if not cached_url.get('is_active'):
            return jsonify({'error': 'URL is not active'}), 404
        
        CacheService.increment_click_count(short_code)
        _track_analytics(cached_url['id'])
        return redirect(cached_url['original_url'])
    
    url_record = URL.query.filter_by(short_code=short_code, is_active=True).first()
    
    if not url_record:
        return jsonify({'error': 'URL not found'}), 404
    
    if url_record.expires_at and url_record.expires_at < datetime.utcnow():
        return jsonify({'error': 'URL has expired'}), 410
    
    url_record.click_count += 1
    db.session.commit()
    
    url_data = url_record.to_dict()
    CacheService.cache_url(url_data)
    CacheService.increment_click_count(short_code)
    
    _track_analytics(url_record.id)
    
    return redirect(url_record.original_url)

def _track_analytics(url_id):
    try:
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        referer = request.headers.get('Referer', '')
        
        analytics = Analytics(
            url_id=url_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer
        )
        
        db.session.add(analytics)
        db.session.commit()
    except Exception as e:
        print(f"Analytics tracking error: {e}")

@bp.route('/api/analytics/<short_code>', methods=['GET'])
def get_analytics(short_code):
    url_record = URL.query.filter_by(short_code=short_code).first()
    
    if not url_record:
        return jsonify({'error': 'URL not found'}), 404
    
    cached_summary = CacheService.get_cached_analytics_summary(url_record.id)
    if cached_summary:
        return jsonify(cached_summary)
    
    analytics = Analytics.query.filter_by(url_id=url_record.id).all()
    
    total_clicks = len(analytics)
    unique_ips = len(set(a.ip_address for a in analytics))
    
    clicks_by_day = {}
    for analytic in analytics:
        day = analytic.clicked_at.strftime('%Y-%m-%d')
        clicks_by_day[day] = clicks_by_day.get(day, 0) + 1
    
    top_referers = {}
    for analytic in analytics:
        if analytic.referer:
            referer = urlparse(analytic.referer).netloc
            top_referers[referer] = top_referers.get(referer, 0) + 1
    
    summary = {
        'url_info': url_record.to_dict(),
        'total_clicks': total_clicks,
        'unique_visitors': unique_ips,
        'clicks_by_day': clicks_by_day,
        'top_referers': dict(sorted(top_referers.items(), key=lambda x: x[1], reverse=True)[:10]),
        'recent_analytics': [a.to_dict() for a in analytics[-10:]]
    }
    
    CacheService.cache_analytics_summary(url_record.id, summary)
    
    return jsonify(summary)

@bp.route('/api/info/<short_code>', methods=['GET'])
def get_url_info(short_code):
    cached_url = CacheService.get_url_from_cache(short_code)
    
    if cached_url:
        return jsonify(cached_url)
    
    url_record = URL.query.filter_by(short_code=short_code).first()
    
    if not url_record:
        return jsonify({'error': 'URL not found'}), 404
    
    url_data = url_record.to_dict()
    CacheService.cache_url(url_data)
    
    return jsonify(url_data)

@bp.route('/api/delete/<short_code>', methods=['DELETE'])
def delete_url(short_code):
    url_record = URL.query.filter_by(short_code=short_code).first()
    
    if not url_record:
        return jsonify({'error': 'URL not found'}), 404
    
    try:
        CacheService.invalidate_cache(short_code)
        db.session.delete(url_record)
        db.session.commit()
        return jsonify({'message': 'URL deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@bp.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Smart URL Shortener API',
        'endpoints': {
            'POST /api/shorten': 'Create short URL',
            'GET /<short_code>': 'Redirect to original URL',
            'GET /api/info/<short_code>': 'Get URL information',
            'GET /api/analytics/<short_code>': 'Get URL analytics',
            'DELETE /api/delete/<short_code>': 'Delete URL',
            'GET /health': 'Health check'
        }
    })
