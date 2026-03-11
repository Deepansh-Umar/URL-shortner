import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///url_shortener.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CACHE_EXPIRE_SECONDS = int(os.environ.get('CACHE_EXPIRE_SECONDS', 300))
    RATE_LIMIT_PER_MINUTE = os.getenv('RATE_LIMIT_PER_MINUTE', '100 per minute')
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    SHORT_CODE_LENGTH = 6
