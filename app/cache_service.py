import json
from app import redis_client
from config import Config
from app.models import URL

class CacheService:
    @staticmethod
    def get_url_from_cache(short_code):
        try:
            cached_data = redis_client.get(f'url:{short_code}')
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
    
    @staticmethod
    def cache_url(url_data, expire_seconds=None):
        try:
            expire = expire_seconds or Config.CACHE_EXPIRE_SECONDS
            redis_client.setex(
                f"url:{url_data['short_code']}", 
                expire, 
                json.dumps(url_data)
            )
        except Exception as e:
            print(f"Cache set error: {e}")
    
    @staticmethod
    def invalidate_cache(short_code):
        try:
            redis_client.delete(f'url:{short_code}')
        except Exception as e:
            print(f"Cache invalidate error: {e}")
    
    @staticmethod
    def increment_click_count(short_code):
        try:
            redis_client.incr(f'clicks:{short_code}')
            redis_client.expire(f'clicks:{short_code}', Config.CACHE_EXPIRE_SECONDS)
        except Exception as e:
            print(f"Click count increment error: {e}")
    
    @staticmethod
    def get_cached_click_count(short_code):
        try:
            count = redis_client.get(f'clicks:{short_code}')
            return int(count) if count else None
        except Exception as e:
            print(f"Get cached click count error: {e}")
        return None
    
    @staticmethod
    def cache_analytics_summary(url_id, summary_data, expire_seconds=300):
        try:
            redis_client.setex(
                f'analytics:{url_id}',
                expire_seconds,
                json.dumps(summary_data)
            )
        except Exception as e:
            print(f"Cache analytics summary error: {e}")
    
    @staticmethod
    def get_cached_analytics_summary(url_id):
        try:
            cached_data = redis_client.get(f'analytics:{url_id}')
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"Get cached analytics summary error: {e}")
        return None
