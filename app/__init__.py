from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
import redis
import os

db = SQLAlchemy()
migrate = Migrate()
redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[app.config.get('RATE_LIMIT_PER_MINUTE', '100 per minute')]
    )
    limiter.init_app(app)
    
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app
