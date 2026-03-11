from datetime import datetime
from app import db
from flask import current_app
import shortuuid

class URL(db.Model):
    __tablename__ = 'urls'
    
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.Text, nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    click_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    analytics = db.relationship('Analytics', backref='url', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<URL {self.short_code}>'
    
    @staticmethod
    def generate_short_code(length=6):
        return shortuuid.random(length=length).lower()
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_url': self.original_url,
            'short_code': self.short_code,
            'short_url': f"{current_app.config['BASE_URL']}/{self.short_code}",
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'click_count': self.click_count,
            'is_active': self.is_active
        }

class Analytics(db.Model):
    __tablename__ = 'analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey('urls.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.Text, nullable=True)
    referer = db.Column(db.Text, nullable=True)
    country = db.Column(db.String(2), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Analytics {self.id} for URL {self.url_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'url_id': self.url_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'referer': self.referer,
            'country': self.country,
            'city': self.city,
            'clicked_at': self.clicked_at.isoformat()
        }
