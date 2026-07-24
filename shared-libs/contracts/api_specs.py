"""
API Specifications for Stock Market Dashboard
Enterprise-grade API contracts
"""

from typing import Dict, Any


# API Gateway Routes
API_GATEWAY_ROUTES = {
    "prefix": "/api/v1",
    "routes": {
        # Authentication
        "/auth": {
            "POST /login": "Login user",
            "POST /refresh": "Refresh access token",
            "POST /logout": "Logout user",
            "GET /me": "Get current user",
        },
        # Users
        "/users": {
            "POST /": "Create user",
            "GET /": "List users (admin)",
            "GET /{user_id}": "Get user by ID",
            "PUT /{user_id}": "Update user",
            "DELETE /{user_id}": "Delete user",
        },
        # Market Data
        "/market": {
            "GET /quotes": "Get quotes for symbols",
            "GET /quotes/{symbol}": "Get quote for symbol",
            "GET /ohlcv": "Get OHLCV data",
            "GET /ohlcv/{symbol}": "Get OHLCV for symbol",
            "GET /status": "Get market status",
            "GET /calendar": "Get market calendar",
        },
        # Watchlist
        "/watchlists": {
            "POST /": "Create watchlist",
            "GET /": "List user watchlists",
            "GET /{watchlist_id}": "Get watchlist by ID",
            "PUT /{watchlist_id}": "Update watchlist",
            "DELETE /{watchlist_id}": "Delete watchlist",
            "POST /{watchlist_id}/items": "Add item to watchlist",
            "GET /{watchlist_id}/items": "List watchlist items",
            "GET /{watchlist_id}/items/{item_id}": "Get watchlist item",
            "PUT /{watchlist_id}/items/{item_id}": "Update watchlist item",
            "DELETE /{watchlist_id}/items/{item_id}": "Remove item from watchlist",
        },
        # Screener
        "/screener": {
            "POST /": "Run screener",
            "GET /presets": "Get screener presets",
            "POST /presets": "Save screener preset",
            "DELETE /presets/{preset_id}": "Delete screener preset",
        },
        # Alerts
        "/alerts": {
            "POST /": "Create alert",
            "GET /": "List user alerts",
            "GET /{alert_id}": "Get alert by ID",
            "PUT /{alert_id}": "Update alert",
            "DELETE /{alert_id}": "Delete alert",
        },
        # GTT Orders
        "/gtt": {
            "POST /": "Create GTT order",
            "GET /": "List user GTT orders",
            "GET /{gtt_id}": "Get GTT order by ID",
            "PUT /{gtt_id}": "Update GTT order",
            "DELETE /{gtt_id}": "Cancel GTT order",
        },
        # Portfolio
        "/portfolio": {
            "POST /": "Create portfolio",
            "GET /": "List user portfolios",
            "GET /{portfolio_id}": "Get portfolio by ID",
            "PUT /{portfolio_id}": "Update portfolio",
            "DELETE /{portfolio_id}": "Delete portfolio",
            "POST /{portfolio_id}/items": "Add item to portfolio",
            "GET /{portfolio_id}/items": "List portfolio items",
            "PUT /{portfolio_id}/items/{item_id}": "Update portfolio item",
            "DELETE /{portfolio_id}/items/{item_id}": "Remove item from portfolio",
        },
        # Trades
        "/trades": {
            "POST /": "Record trade",
            "GET /": "List user trades",
            "GET /{trade_id}": "Get trade by ID",
            "PUT /{trade_id}": "Update trade",
            "DELETE /{trade_id}": "Delete trade",
        },
        # Notifications
        "/notifications": {
            "GET /": "List user notifications",
            "GET /{notification_id}": "Get notification by ID",
            "PUT /{notification_id}/read": "Mark notification as read",
            "DELETE /{notification_id}": "Delete notification",
        },
        # News & Sentiment
        "/news": {
            "GET /": "Get market news",
            "GET /{symbol}": "Get news for symbol",
            "GET /sentiment": "Get market sentiment",
            "GET /sentiment/{symbol}": "Get sentiment for symbol",
        },
        # Reports
        "/reports": {
            "GET /portfolio-performance": "Get portfolio performance report",
            "GET /trade-history": "Get trade history report",
            "GET /tax-report": "Get tax report",
            "POST /export": "Export report",
        },
        # Admin
        "/admin": {
            "GET /users": "List all users (admin)",
            "GET /metrics": "Get system metrics (admin)",
            "GET /health": "Health check",
        },
    }
}


# Service Endpoints
SERVICE_ENDPOINTS = {
    "auth-service": {
        "host": "auth-service",
        "port": 8001,
        "base_url": "/api/v1/auth",
        "endpoints": [
            {"method": "POST", "path": "/login", "description": "Login user"},
            {"method": "POST", "path": "/refresh", "description": "Refresh token"},
            {"method": "POST", "path": "/logout", "description": "Logout user"},
            {"method": "GET", "path": "/me", "description": "Get current user"},
            {"method": "POST", "path": "/validate", "description": "Validate token"},
        ]
    },
    "user-service": {
        "host": "user-service",
        "port": 8002,
        "base_url": "/api/v1/users",
        "endpoints": [
            {"method": "POST", "path": "/", "description": "Create user"},
            {"method": "GET", "path": "/", "description": "List users"},
            {"method": "GET", "path": "/{user_id}", "description": "Get user"},
            {"method": "PUT", "path": "/{user_id}", "description": "Update user"},
            {"method": "DELETE", "path": "/{user_id}", "description": "Delete user"},
            {"method": "GET", "path": "/{user_id}/preferences", "description": "Get user preferences"},
            {"method": "PUT", "path": "/{user_id}/preferences", "description": "Update user preferences"},
        ]
    },
    "market-data-service": {
        "host": "market-data-service",
        "port": 8003,
        "base_url": "/api/v1/market",
        "endpoints": [
            {"method": "GET", "path": "/quotes", "description": "Get quotes"},
            {"method": "GET", "path": "/quotes/{symbol}", "description": "Get quote"},
            {"method": "GET", "path": "/ohlcv", "description": "Get OHLCV data"},
            {"method": "GET", "path": "/ohlcv/{symbol}", "description": "Get OHLCV for symbol"},
            {"method": "GET", "path": "/status", "description": "Get market status"},
            {"method": "GET", "path": "/calendar", "description": "Get market calendar"},
            {"method": "WS", "path": "/ws/quotes", "description": "WebSocket for live quotes"},
        ]
    },
    "watchlist-service": {
        "host": "watchlist-service",
        "port": 8004,
        "base_url": "/api/v1/watchlists",
        "endpoints": [
            {"method": "POST", "path": "/", "description": "Create watchlist"},
            {"method": "GET", "path": "/", "description": "List watchlists"},
            {"method": "GET", "path": "/{watchlist_id}", "description": "Get watchlist"},
            {"method": "PUT", "path": "/{watchlist_id}", "description": "Update watchlist"},
            {"method": "DELETE", "path": "/{watchlist_id}", "description": "Delete watchlist"},
            {"method": "POST", "path": "/{watchlist_id}/items", "description": "Add item"},
            {"method": "GET", "path": "/{watchlist_id}/items", "description": "List items"},
            {"method": "GET", "path": "/{watchlist_id}/items/{item_id}", "description": "Get item"},
            {"method": "PUT", "path": "/{watchlist_id}/items/{item_id}", "description": "Update item"},
            {"method": "DELETE", "path": "/{watchlist_id}/items/{item_id}", "description": "Delete item"},
        ]
    },
    "screener-service": {
        "host": "screener-service",
        "port": 8005,
        "base_url": "/api/v1/screener",
        "endpoints": [
            {"method": "POST", "path": "/", "description": "Run screener"},
            {"method": "GET", "path": "/presets", "description": "Get presets"},
            {"method": "POST", "path": "/presets", "description": "Save preset"},
            {"method": "DELETE", "path": "/presets/{preset_id}", "description": "Delete preset"},
        ]
    },
    "portfolio-service": {
        "host": "portfolio-service",
        "port": 8006,
        "base_url": "/api/v1/portfolio",
        "endpoints": [
            {"method": "POST", "path": "/", "description": "Create portfolio"},
            {"method": "GET", "path": "/", "description": "List portfolios"},
            {"method": "GET", "path": "/{portfolio_id}", "description": "Get portfolio"},
            {"method": "PUT", "path": "/{portfolio_id}", "description": "Update portfolio"},
            {"method": "DELETE", "path": "/{portfolio_id}", "description": "Delete portfolio"},
            {"method": "POST", "path": "/{portfolio_id}/items", "description": "Add item"},
            {"method": "GET", "path": "/{portfolio_id}/items", "description": "List items"},
            {"method": "PUT", "path": "/{portfolio_id}/items/{item_id}", "description": "Update item"},
            {"method": "DELETE", "path": "/{portfolio_id}/items/{item_id}", "description": "Delete item"},
        ]
    },
    "trading-service": {
        "host": "trading-service",
        "port": 8007,
        "base_url": "/api/v1/trading",
        "endpoints": [
            {"method": "POST", "path": "/orders", "description": "Create order"},
            {"method": "GET", "path": "/orders", "description": "List orders"},
            {"method": "GET", "path": "/orders/{order_id}", "description": "Get order"},
            {"method": "PUT", "path": "/orders/{order_id}", "description": "Update order"},
            {"method": "DELETE", "path": "/orders/{order_id}", "description": "Cancel order"},
            {"method": "POST", "path": "/gtt", "description": "Create GTT order"},
            {"method": "GET", "path": "/gtt", "description": "List GTT orders"},
            {"method": "GET", "path": "/gtt/{gtt_id}", "description": "Get GTT order"},
            {"method": "PUT", "path": "/gtt/{gtt_id}", "description": "Update GTT order"},
            {"method": "DELETE", "path": "/gtt/{gtt_id}", "description": "Cancel GTT order"},
            {"method": "POST", "path": "/trades", "description": "Record trade"},
            {"method": "GET", "path": "/trades", "description": "List trades"},
        ]
    },
    "alert-service": {
        "host": "alert-service",
        "port": 8008,
        "base_url": "/api/v1/alerts",
        "endpoints": [
            {"method": "POST", "path": "/", "description": "Create alert"},
            {"method": "GET", "path": "/", "description": "List alerts"},
            {"method": "GET", "path": "/{alert_id}", "description": "Get alert"},
            {"method": "PUT", "path": "/{alert_id}", "description": "Update alert"},
            {"method": "DELETE", "path": "/{alert_id}", "description": "Delete alert"},
        ]
    },
    "notification-service": {
        "host": "notification-service",
        "port": 8009,
        "base_url": "/api/v1/notifications",
        "endpoints": [
            {"method": "POST", "path": "/", "description": "Create notification"},
            {"method": "GET", "path": "/", "description": "List notifications"},
            {"method": "GET", "path": "/{notification_id}", "description": "Get notification"},
            {"method": "PUT", "path": "/{notification_id}/read", "description": "Mark as read"},
            {"method": "DELETE", "path": "/{notification_id}", "description": "Delete notification"},
            {"method": "POST", "path": "/send", "description": "Send notification"},
        ]
    },
    "news-service": {
        "host": "news-service",
        "port": 8010,
        "base_url": "/api/v1/news",
        "endpoints": [
            {"method": "GET", "path": "/", "description": "Get news"},
            {"method": "GET", "path": "/{symbol}", "description": "Get news for symbol"},
            {"method": "GET", "path": "/sentiment", "description": "Get sentiment"},
            {"method": "GET", "path": "/sentiment/{symbol}", "description": "Get sentiment for symbol"},
        ]
    },
    "scheduler-service": {
        "host": "scheduler-service",
        "port": 8011,
        "base_url": "/api/v1/scheduler",
        "endpoints": [
            {"method": "GET", "path": "/tasks", "description": "List scheduled tasks"},
            {"method": "POST", "path": "/tasks", "description": "Create scheduled task"},
            {"method": "GET", "path": "/tasks/{task_id}", "description": "Get task"},
            {"method": "PUT", "path": "/tasks/{task_id}", "description": "Update task"},
            {"method": "DELETE", "path": "/tasks/{task_id}", "description": "Delete task"},
        ]
    },
    "reporting-service": {
        "host": "reporting-service",
        "port": 8012,
        "base_url": "/api/v1/reports",
        "endpoints": [
            {"method": "GET", "path": "/portfolio-performance", "description": "Get portfolio performance"},
            {"method": "GET", "path": "/trade-history", "description": "Get trade history"},
            {"method": "GET", "path": "/tax-report", "description": "Get tax report"},
            {"method": "POST", "path": "/export", "description": "Export report"},
        ]
    },
    "ai-service": {
        "host": "ai-service",
        "port": 8013,
        "base_url": "/api/v1/ai",
        "endpoints": [
            {"method": "POST", "path": "/analyze", "description": "Analyze stock"},
            {"method": "POST", "path": "/predict", "description": "Predict price"},
            {"method": "POST", "path": "/recommend", "description": "Get recommendations"},
            {"method": "POST", "path": "/chat", "description": "Chat with AI"},
        ]
    },
    "admin-dashboard": {
        "host": "admin-dashboard",
        "port": 8014,
        "base_url": "/api/v1/admin",
        "endpoints": [
            {"method": "GET", "path": "/users", "description": "List users"},
            {"method": "GET", "path": "/metrics", "description": "Get metrics"},
            {"method": "GET", "path": "/health", "description": "Health check"},
        ]
    },
}


# Redis Channels
REDIS_CHANNELS = {
    "quote_updates": "market:quotes:updates",
    "market_status": "market:status",
    "alert_triggered": "alerts:triggered",
    "gtt_triggered": "gtt:triggered",
    "notification": "notifications:new",
    "user_events": "users:events",
}


# Celery Task Queues
CELERY_QUEUES = {
    "high_priority": "high-priority",
    "low_priority": "low-priority",
    "historical_data": "historical-data",
    "alert_checks": "alert-checks",
    "gtt_checks": "gtt-checks",
    "notifications": "notifications",
    "reports": "reports",
    "ai_tasks": "ai-tasks",
}


# Database Schemas
DATABASE_SCHEMAS = {
    "auth": "auth",
    "users": "users",
    "market_data": "market_data",
    "watchlists": "watchlists",
    "portfolio": "portfolio",
    "trading": "trading",
    "alerts": "alerts",
    "notifications": "notifications",
    "news": "news",
    "reports": "reports",
}
