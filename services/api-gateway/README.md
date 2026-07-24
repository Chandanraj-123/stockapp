# API Gateway Service

## Overview

The API Gateway is the main entry point for the Stock Market Dashboard microservices platform. It routes incoming requests to the appropriate microservices and provides a unified API interface.

## Features

- **Request Routing**: Routes HTTP requests to appropriate microservices
- **Load Balancing**: Distributes traffic across service instances
- **Authentication**: Handles JWT token validation
- **Rate Limiting**: Protects services from abuse
- **CORS**: Handles Cross-Origin Resource Sharing
- **WebSocket Proxy**: Forwards WebSocket connections to services
- **Health Checks**: Monitors service health
- **Documentation**: Provides unified API documentation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        API Gateway                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Auth       │  │  Market     │  │   Request Router          │  │
│  │  Service    │  │  Data      │  │                           │  │
│  │             │  │  Service   │  │  ┌─────────────────────┐  │  │
│  └─────────────┘  └─────────────┘  │   │ /api/v1/*           │  │  │
│        ▲                ▲            │   │ /ws/quotes          │  │  │
│        │                │            │   └─────────────────────┘  │  │
│  ┌─────────────┐  ┌─────────────┐  └─────────────────────────┘  │
│  │  User       │  │  Watchlist  │                                      │
│  │  Service    │  │  Service   │                                      │
│  └─────────────┘  └─────────────┘                                      │
└─────────────────────────────────────────────────────────────┘
```

## Services Routed

| Service | Port | Description |
|---------|------|-------------|
| auth-service | 8001 | Authentication and user management |
| user-service | 8002 | User profile and preferences |
| market-data-service | 8003 | Real-time and historical market data |
| watchlist-service | 8004 | User watchlists and symbols |
| screener-service | 8005 | Stock screening and filtering |
| trading-service | 8007 | Order management and trading |
| alert-service | 8008 | Price alerts and notifications |
| portfolio-service | 8006 | Portfolio management |
| notification-service | 8009 | User notifications |
| news-service | 8010 | Market news and sentiment |
| reporting-service | 8012 | Reports and analytics |
| admin-dashboard | 8014 | Admin interface |

## API Endpoints

### Health Check
- `GET /health` - Service health check
- `GET /` - Service information

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user

### Users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/{user_id}` - Get user
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Market Data
- `GET /api/v1/market/quotes` - Get quotes
- `GET /api/v1/market/quotes/{symbol}` - Get quote for symbol
- `GET /api/v1/market/ohlcv` - Get OHLCV data
- `GET /api/v1/market/ohlcv/{symbol}` - Get OHLCV for symbol
- `GET /api/v1/market/status` - Get market status
- `GET /api/v1/market/calendar` - Get market calendar
- `WS /ws/quotes` - WebSocket for live quotes

### Watchlists
- `POST /api/v1/watchlists/` - Create watchlist
- `GET /api/v1/watchlists/` - List watchlists
- `GET /api/v1/watchlists/{watchlist_id}` - Get watchlist
- `PUT /api/v1/watchlists/{watchlist_id}` - Update watchlist
- `DELETE /api/v1/watchlists/{watchlist_id}` - Delete watchlist
- `POST /api/v1/watchlists/{watchlist_id}/items` - Add item
- `GET /api/v1/watchlists/{watchlist_id}/items` - List items

### Screener
- `POST /api/v1/screener/` - Run screener
- `GET /api/v1/screener/presets` - Get presets
- `POST /api/v1/screener/presets` - Save preset
- `DELETE /api/v1/screener/presets/{preset_id}` - Delete preset

### Trading
- `POST /api/v1/trading/orders` - Create order
- `GET /api/v1/trading/orders` - List orders
- `GET /api/v1/trading/orders/{order_id}` - Get order
- `POST /api/v1/trading/gtt` - Create GTT order
- `GET /api/v1/trading/gtt` - List GTT orders
- `POST /api/v1/trading/trades` - Record trade
- `GET /api/v1/trading/trades` - List trades

### Alerts
- `POST /api/v1/alerts/` - Create alert
- `GET /api/v1/alerts/` - List alerts
- `GET /api/v1/alerts/{alert_id}` - Get alert
- `PUT /api/v1/alerts/{alert_id}` - Update alert
- `DELETE /api/v1/alerts/{alert_id}` - Delete alert

### Portfolio
- `POST /api/v1/portfolio/` - Create portfolio
- `GET /api/v1/portfolio/` - List portfolios
- `GET /api/v1/portfolio/{portfolio_id}` - Get portfolio
- `POST /api/v1/portfolio/{portfolio_id}/items` - Add item
- `GET /api/v1/portfolio/{portfolio_id}/items` - List items

### Notifications
- `GET /api/v1/notifications/` - List notifications
- `GET /api/v1/notifications/{notification_id}` - Get notification
- `PUT /api/v1/notifications/{notification_id}/read` - Mark as read
- `DELETE /api/v1/notifications/{notification_id}` - Delete notification

### News
- `GET /api/v1/news/` - Get news
- `GET /api/v1/news/{symbol}` - Get news for symbol
- `GET /api/v1/news/sentiment` - Get sentiment
- `GET /api/v1/news/sentiment/{symbol}` - Get sentiment for symbol

### Reports
- `GET /api/v1/reports/portfolio-performance` - Portfolio performance
- `GET /api/v1/reports/trade-history` - Trade history
- `GET /api/v1/reports/tax-report` - Tax report
- `POST /api/v1/reports/export` - Export report

### Admin
- `GET /api/v1/admin/users` - List all users
- `GET /api/v1/admin/metrics` - Get metrics
- `GET /api/v1/admin/health` - Health check

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVICE_NAME` | api-gateway | Service name |
| `SERVICE_HOST` | 0.0.0.0 | Host to bind |
| `SERVICE_PORT` | 8000 | Port to bind |
| `SERVICE_DEBUG` | false | Enable debug mode |
| `LOG_LEVEL` | INFO | Logging level |
| `LOG_DIR` | /app/logs | Log directory |
| `ENABLE_WEBSOCKET` | true | Enable WebSocket support |
| `ENABLE_CACHE` | true | Enable caching |
| `ENABLE_CORS` | true | Enable CORS |
| `CORS_ORIGINS` | http://localhost:3000,http://localhost:8080 | Allowed origins |

## Running the Service

### Development

```bash
# Install dependencies
poetry install

# Run the service
poetry run python main.py

# Or with uvicorn directly
poetry run uvicorn main:app --reload --port 8000
```

### Production

```bash
# Build the Docker image
docker build -t api-gateway .

# Run the container
docker run -p 8000:8000 api-gateway

# Or with docker-compose
docker-compose up -d api-gateway
```

## Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=api_gateway --cov-report=html
```

## Dependencies

- Python 3.12+
- FastAPI
- Uvicorn
- httpx
- pydantic
- structlog

## License

MIT
