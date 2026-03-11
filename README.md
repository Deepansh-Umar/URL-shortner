# Smart URL Shortener

A high-performance URL shortening service built with Flask, PostgreSQL, and Redis. Features include REST APIs, Redis caching, rate limiting, and comprehensive click analytics.

## Features

- **URL Shortening**: Generate short URLs with custom codes or auto-generated codes
- **Redis Caching**: Fast lookups with intelligent cache invalidation
- **Rate Limiting**: Prevent abuse with configurable rate limits
- **Click Analytics**: Track clicks, unique visitors, referrers, and geographic data
- **URL Expiration**: Set expiration dates for short URLs
- **REST API**: Clean JSON API with comprehensive endpoints
- **Docker Support**: Easy deployment with Docker Compose

## Tech Stack

- **Backend**: Flask 2.3.3
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Rate Limiting**: Flask-Limiter
- **Deployment**: Docker & Docker Compose
- **Python**: 3.11

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Local Development

1. **Clone and setup**:
```bash
git clone <repository-url>
cd url-shortener
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Environment setup**:
```bash
cp .env.example .env
# Edit .env with your database and Redis credentials
```

4. **Initialize database**:
```bash
python init_db.py
```

5. **Run the application**:
```bash
python run.py
```

The service will be available at `http://localhost:5000`

### Docker Deployment

1. **Build and run with Docker Compose**:
```bash
docker-compose up --build
```

This will start:
- Flask web server on port 5000
- PostgreSQL database on port 5432
- Redis cache on port 6379

## API Endpoints

### Create Short URL
```http
POST /api/shorten
Content-Type: application/json

{
  "url": "https://example.com/very/long/url",
  "custom_code": "mylink",  // Optional
  "expires_in_days": 30      // Optional
}
```

### Redirect to Original URL
```http
GET /<short_code>
```

### Get URL Information
```http
GET /api/info/<short_code>
```

### Get URL Analytics
```http
GET /api/analytics/<short_code>
```

### Delete URL
```http
DELETE /api/delete/<short_code>
```

### Health Check
```http
GET /health
```

## API Examples

### Create a Short URL
```bash
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'
```

Response:
```json
{
  "id": 1,
  "original_url": "https://www.google.com",
  "short_code": "abc123",
  "short_url": "http://localhost:5000/abc123",
  "created_at": "2024-01-01T12:00:00",
  "expires_at": null,
  "click_count": 0,
  "is_active": true
}
```

### Get Analytics
```bash
curl http://localhost:5000/api/analytics/abc123
```

Response:
```json
{
  "url_info": {...},
  "total_clicks": 25,
  "unique_visitors": 18,
  "clicks_by_day": {
    "2024-01-01": 15,
    "2024-01-02": 10
  },
  "top_referers": {
    "twitter.com": 8,
    "facebook.com": 5
  },
  "recent_analytics": [...]
}
```

## Configuration

The application uses the following environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://username:password@localhost:5432/url_shortener` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `SECRET_KEY` | `dev-secret-key` | Flask secret key |
| `RATE_LIMIT_PER_MINUTE` | `100 per minute` | Rate limiting configuration |
| `CACHE_EXPIRE_SECONDS` | `300` | Redis cache TTL |
| `BASE_URL` | `http://localhost:5000` | Base URL for short links |

## Database Schema

### URLs Table
- `id`: Primary key
- `original_url`: Original long URL
- `short_code`: Unique short code
- `created_at`: Creation timestamp
- `expires_at`: Expiration timestamp (optional)
- `click_count`: Total click count
- `is_active`: Active status

### Analytics Table
- `id`: Primary key
- `url_id`: Foreign key to URLs
- `ip_address`: Visitor IP address
- `user_agent`: Browser user agent
- `referer`: HTTP referer
- `country`: Country code (optional)
- `city`: City name (optional)
- `clicked_at`: Click timestamp

## Performance Features

### Redis Caching
- URL lookups cached for 5 minutes (configurable)
- Click counts cached in Redis for performance
- Analytics summaries cached to reduce database load

### Rate Limiting
- 10 requests per minute for URL creation
- 30 requests per minute for analytics/info endpoints
- Configurable limits per endpoint

### Database Optimization
- Indexed short_code column for fast lookups
- Efficient analytics queries with proper joins
- Connection pooling via SQLAlchemy

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Database Migrations
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Monitoring
- Health check endpoint: `/health`
- Application logs available in Docker containers
- Redis monitoring via Redis CLI
- PostgreSQL monitoring via psql

## License

This project is licensed under the MIT License.
