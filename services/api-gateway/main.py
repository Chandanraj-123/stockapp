"""
API Gateway Service
Enterprise-grade API Gateway for Stock Market Dashboard
Routes requests to appropriate microservices
"""

import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import json

from shared_libs.utils import get_app_config, setup_logging
from shared_libs.models import (
    HealthCheckResponse,
    ErrorResponse,
    ResponseModel,
)
from shared_libs.contracts import SERVICE_ENDPOINTS


# Initialize configuration
config = get_app_config()

# Initialize logger
logger = setup_logging(
    service_name="api-gateway",
    level=config.log_level,
    log_dir=config.log_dir,
    use_json=True
)

# Security
security = HTTPBearer()


class APIGateway:
    """API Gateway for routing requests to microservices"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Stock Market Dashboard - API Gateway",
            description="Enterprise-grade API Gateway for Stock Market Dashboard",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json"
        )
        
        # Setup CORS
        self._setup_cors()
        
        # Setup routes
        self._setup_routes()
        
        # Setup exception handlers
        self._setup_exception_handlers()
        
        # HTTP client for forwarding requests
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(config.service.timeout, connect=10),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )
    
    def _setup_cors(self):
        """Setup CORS middleware"""
        if config.enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=config.cors_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            logger.info("CORS middleware enabled")
    
    def _setup_routes(self):
        """Setup all API routes"""
        # Health check
        self.app.get("/health")(self.health_check)
        self.app.get("/")(self.root)
        
        # API routes
        api_router = self._create_api_router()
        self.app.include_router(api_router, prefix="/api/v1")
        
        # WebSocket routes
        self._setup_websocket_routes()
    
    def _create_api_router(self):
        """Create the main API router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        # Authentication routes
        router.include_router(self._create_auth_router(), prefix="/auth", tags=["Authentication"])
        
        # User routes
        router.include_router(self._create_user_router(), prefix="/users", tags=["Users"])
        
        # Market Data routes
        router.include_router(self._create_market_data_router(), prefix="/market", tags=["Market Data"])
        
        # Watchlist routes
        router.include_router(self._create_watchlist_router(), prefix="/watchlists", tags=["Watchlists"])
        
        # Screener routes
        router.include_router(self._create_screener_router(), prefix="/screener", tags=["Screener"])
        
        # Trading routes
        router.include_router(self._create_trading_router(), prefix="/trading", tags=["Trading"])
        
        # Alert routes
        router.include_router(self._create_alert_router(), prefix="/alerts", tags=["Alerts"])
        
        # Portfolio routes
        router.include_router(self._create_portfolio_router(), prefix="/portfolio", tags=["Portfolio"])
        
        # Notification routes
        router.include_router(self._create_notification_router(), prefix="/notifications", tags=["Notifications"])
        
        # News routes
        router.include_router(self._create_news_router(), prefix="/news", tags=["News"])
        
        # Reports routes
        router.include_router(self._create_reports_router(), prefix="/reports", tags=["Reports"])
        
        # Admin routes
        router.include_router(self._create_admin_router(), prefix="/admin", tags=["Admin"])
        
        return router
    
    def _create_auth_router(self):
        """Create authentication router"""
        from fastapi import APIRouter, Depends
        
        router = APIRouter()
        
        @router.post("/login")
        async def login(request: Request):
            return await self._forward_request(request, "auth-service", "/api/v1/auth/login")
        
        @router.post("/refresh")
        async def refresh(request: Request):
            return await self._forward_request(request, "auth-service", "/api/v1/auth/refresh")
        
        @router.post("/logout")
        async def logout(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
            return await self._forward_request(request, "auth-service", "/api/v1/auth/logout")
        
        @router.get("/me")
        async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
            return await self._forward_request(request, "auth-service", "/api/v1/auth/me")
        
        return router
    
    def _create_user_router(self):
        """Create user router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        @router.post("/")
        async def create_user(request: Request):
            return await self._forward_request(request, "user-service", "/api/v1/users/")
        
        @router.get("/")
        async def list_users(request: Request):
            return await self._forward_request(request, "user-service", "/api/v1/users/")
        
        @router.get("/{user_id}")
        async def get_user(request: Request, user_id: str):
            return await self._forward_request(request, "user-service", f"/api/v1/users/{user_id}")
        
        @router.put("/{user_id}")
        async def update_user(request: Request, user_id: str):
            return await self._forward_request(request, "user-service", f"/api/v1/users/{user_id}")
        
        @router.delete("/{user_id}")
        async def delete_user(request: Request, user_id: str):
            return await self._forward_request(request, "user-service", f"/api/v1/users/{user_id}")
        
        return router
    
    def _create_market_data_router(self):
        """Create market data router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        @router.get("/quotes")
        async def get_quotes(request: Request):
            return await self._forward_request(request, "market-data-service", "/api/v1/market/quotes")
        
        @router.get("/quotes/{symbol}")
        async def get_quote(request: Request, symbol: str):
            return await self._forward_request(request, "market-data-service", f"/api/v1/market/quotes/{symbol}")
        
        @router.get("/ohlcv")
        async def get_ohlcv(request: Request):
            return await self._forward_request(request, "market-data-service", "/api/v1/market/ohlcv")
        
        @router.get("/ohlcv/{symbol}")
        async def get_ohlcv_symbol(request: Request, symbol: str):
            return await self._forward_request(request, "market-data-service", f"/api/v1/market/ohlcv/{symbol}")
        
        @router.get("/status")
        async def get_market_status(request: Request):
            return await self._forward_request(request, "market-data-service", "/api/v1/market/status")
        
        @router.get("/calendar")
        async def get_market_calendar(request: Request):
            return await self._forward_request(request, "market-data-service", "/api/v1/market/calendar")
        
        return router
    
    def _create_watchlist_router(self):
        """Create watchlist router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        @router.post("/")
        async def create_watchlist(request: Request):
            return await self._forward_request(request, "watchlist-service", "/api/v1/watchlists/")
        
        @router.get("/")
        async def list_watchlists(request: Request):
            return await self._forward_request(request, "watchlist-service", "/api/v1/watchlists/")
        
        @router.get("/{watchlist_id}")
        async def get_watchlist(request: Request, watchlist_id: str):
            return await self._forward_request(request, "watchlist-service", f"/api/v1/watchlists/{watchlist_id}")
        
        @router.put("/{watchlist_id}")
        async def update_watchlist(request: Request, watchlist_id: str):
            return await self._forward_request(request, "watchlist-service", f"/api/v1/watchlists/{watchlist_id}")
        
        @router.delete("/{watchlist_id}")
        async def delete_watchlist(request: Request, watchlist_id: str):
            return await self._forward_request(request, "watchlist-service", f"/api/v1/watchlists/{watchlist_id}")
        
        @router.post("/{watchlist_id}/items")
        async def add_watchlist_item(request: Request, watchlist_id: str):
            return await self._forward_request(request, "watchlist-service", f"/api/v1/watchlists/{watchlist_id}/items")
        
        @router.get("/{watchlist_id}/items")
        async def list_watchlist_items(request: Request, watchlist_id: str):
            return await self._forward_request(request, "watchlist-service", f"/api/v1/watchlists/{watchlist_id}/items")
        
        @router.get("/{watchlist_id}/items/{item_id}")
        async def get_watchlist_item(request: Request, watchlist_id: str, item_id: str):
            return await self._forward_request(request, "watchlist-service", f"/api/v1/watchlists/{watchlist_id}/items/{item_id}")
        
        @router.put("/{watchlist_id}/items/{item_id}")
        async def update_watchlist_item(request: Request, watchlist_id: str, item_id: str):
            return await self._forward_request(request, "watchlist-service", f"/api/v1/watchlists/{watchlist_id}/items/{item_id}")
        
        @router.delete("/{watchlist_id}/items/{item_id}")
        async def delete_watchlist_item(request: Request, watchlist_id: str, item_id: str):
            return await self._forward_request(request, "watchlist-service", f"/api/v1/watchlists/{watchlist_id}/items/{item_id}")
        
        return router
    
    def _create_screener_router(self):
        """Create screener router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        @router.post("/")
        async def run_screener(request: Request):
            return await self._forward_request(request, "screener-service", "/api/v1/screener/")
        
        @router.get("/presets")
        async def get_presets(request: Request):
            return await self._forward_request(request, "screener-service", "/api/v1/screener/presets")
        
        @router.post("/presets")
        async def save_preset(request: Request):
            return await self._forward_request(request, "screener-service", "/api/v1/screener/presets")
        
        @router.delete("/presets/{preset_id}")
        async def delete_preset(request: Request, preset_id: str):
            return await self._forward_request(request, "screener-service", f"/api/v1/screener/presets/{preset_id}")
        
        return router
    
    def _create_trading_router(self):
        """Create trading router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        @router.post("/orders")
        async def create_order(request: Request):
            return await self._forward_request(request, "trading-service", "/api/v1/trading/orders")
        
        @router.get("/orders")
        async def list_orders(request: Request):
            return await self._forward_request(request, "trading-service", "/api/v1/trading/orders")
        
        @router.get("/orders/{order_id}")
        async def get_order(request: Request, order_id: str):
            return await self._forward_request(request, "trading-service", f"/api/v1/trading/orders/{order_id}")
        
        @router.post("/gtt")
        async def create_gtt(request: Request):
            return await self._forward_request(request, "trading-service", "/api/v1/trading/gtt")
        
        @router.get("/gtt")
        async def list_gtt(request: Request):
            return await self._forward_request(request, "trading-service", "/api/v1/trading/gtt")
        
        @router.get("/gtt/{gtt_id}")
        async def get_gtt(request: Request, gtt_id: str):
            return await self._forward_request(request, "trading-service", f"/api/v1/trading/gtt/{gtt_id}")
        
        @router.post("/trades")
        async def record_trade(request: Request):
            return await self._forward_request(request, "trading-service", "/api/v1/trading/trades")
        
        @router.get("/trades")
        async def list_trades(request: Request):
            return await self._forward_request(request, "trading-service", "/api/v1/trading/trades")
        
        return router
    
    def _create_alert_router(self):
        """Create alert router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        @router.post("/")
        async def create_alert(request: Request):
            return await self._forward_request(request, "alert-service", "/api/v1/alerts/")
        
        @router.get("/")
        async def list_alerts(request: Request):
            return await self._forward_request(request, "alert-service", "/api/v1/alerts/")
        
        @router.get("/{alert_id}")
        async def get_alert(request: Request, alert_id: str):
            return await self._forward_request(request, "alert-service", f"/api/v1/alerts/{alert_id}")
        
        @router.put("/{alert_id}")
        async def update_alert(request: Request, alert_id: str):
            return await self._forward_request(request, "alert-service", f"/api/v1/alerts/{alert_id}")
        
        @router.delete("/{alert_id}")
        async def delete_alert(request: Request, alert_id: str):
            return await self._forward_request(request, "alert-service", f"/api/v1/alerts/{alert_id}")
        
        return router
    
    def _create_portfolio_router(self):
        """Create portfolio router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        @router.post("/")
        async def create_portfolio(request: Request):
            return await self._forward_request(request, "portfolio-service", "/api/v1/portfolio/")
        
        @router.get("/")
        async def list_portfolios(request: Request):
            return await self._forward_request(request, "portfolio-service", "/api/v1/portfolio/")
        
        @router.get("/{portfolio_id}")
        async def get_portfolio(request: Request, portfolio_id: str):
            return await self._forward_request(request, "portfolio-service", f"/api/v1/portfolio/{portfolio_id}")
        
        @router.post("/{portfolio_id}/items")
        async def add_portfolio_item(request: Request, portfolio_id: str):
            return await self._forward_request(request, "portfolio-service", f"/api/v1/portfolio/{portfolio_id}/items")
        
        @router.get("/{portfolio_id}/items")
        async def list_portfolio_items(request: Request, portfolio_id: str):
            return await self._forward_request(request, "portfolio-service", f"/api/v1/portfolio/{portfolio_id}/items")
        
        return router
    
    def _create_notification_router(self):
        """Create notification router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        @router.get("/")
        async def list_notifications(request: Request):
            return await self._forward_request(request, "notification-service", "/api/v1/notifications/")
        
        @router.get("/{notification_id}")
        async def get_notification(request: Request, notification_id: str):
            return await self._forward_request(request, "notification-service", f"/api/v1/notifications/{notification_id}")
        
        @router.put("/{notification_id}/read")
        async def mark_notification_read(request: Request, notification_id: str):
            return await self._forward_request(request, "notification-service", f"/api/v1/notifications/{notification_id}/read")
        
        @router.delete("/{notification_id}")
        async def delete_notification(request: Request, notification_id: str):
            return await self._forward_request(request, "notification-service", f"/api/v1/notifications/{notification_id}")
        
        return router
    
    def _create_news_router(self):
        """Create news router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        @router.get("/")
        async def get_news(request: Request):
            return await self._forward_request(request, "news-service", "/api/v1/news/")
        
        @router.get("/{symbol}")
        async def get_news_symbol(request: Request, symbol: str):
            return await self._forward_request(request, "news-service", f"/api/v1/news/{symbol}")
        
        @router.get("/sentiment")
        async def get_sentiment(request: Request):
            return await self._forward_request(request, "news-service", "/api/v1/news/sentiment")
        
        @router.get("/sentiment/{symbol}")
        async def get_sentiment_symbol(request: Request, symbol: str):
            return await self._forward_request(request, "news-service", f"/api/v1/news/sentiment/{symbol}")
        
        return router
    
    def _create_reports_router(self):
        """Create reports router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        @router.get("/portfolio-performance")
        async def get_portfolio_performance(request: Request):
            return await self._forward_request(request, "reporting-service", "/api/v1/reports/portfolio-performance")
        
        @router.get("/trade-history")
        async def get_trade_history(request: Request):
            return await self._forward_request(request, "reporting-service", "/api/v1/reports/trade-history")
        
        @router.get("/tax-report")
        async def get_tax_report(request: Request):
            return await self._forward_request(request, "reporting-service", "/api/v1/reports/tax-report")
        
        @router.post("/export")
        async def export_report(request: Request):
            return await self._forward_request(request, "reporting-service", "/api/v1/reports/export")
        
        return router
    
    def _create_admin_router(self):
        """Create admin router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        @router.get("/users")
        async def list_all_users(request: Request):
            return await self._forward_request(request, "admin-dashboard", "/api/v1/admin/users")
        
        @router.get("/metrics")
        async def get_metrics(request: Request):
            return await self._forward_request(request, "admin-dashboard", "/api/v1/admin/metrics")
        
        @router.get("/health")
        async def admin_health_check(request: Request):
            return await self._forward_request(request, "admin-dashboard", "/api/v1/admin/health")
        
        return router
    
    def _setup_websocket_routes(self):
        """Setup WebSocket routes"""
        if config.enable_websocket:
            @self.app.websocket("/ws/quotes")
            async def websocket_quotes(websocket):
                await self._handle_websocket(websocket, "market-data-service", "/ws/quotes")
    
    async def _handle_websocket(self, websocket, service_name: str, service_path: str):
        """Handle WebSocket connections by proxying to the appropriate service"""
        try:
            # Get service endpoint
            service_config = SERVICE_ENDPOINTS.get(service_name)
            if not service_config:
                await websocket.close(code=1003, reason="Service not found")
                return
            
            service_url = f"ws://{service_config['host']}:{service_config['port']}{service_path}"
            
            # Connect to service WebSocket
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", service_url) as response:
                    if response.status_code != 101:
                        await websocket.close(code=1003, reason="Service unavailable")
                        return
                    
                    # Accept connection
                    await websocket.accept()
                    
                    # Forward messages between client and service
                    async for message in websocket.iter_text():
                        # Forward client message to service
                        # In a real implementation, we'd need to handle the WebSocket connection properly
                        pass
                        
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await websocket.close(code=1011, reason="Internal error")
    
    async def _forward_request(self, request: Request, service_name: str, path: str):
        """Forward request to the appropriate microservice"""
        try:
            # Get service endpoint
            service_config = SERVICE_ENDPOINTS.get(service_name)
            if not service_config:
                raise HTTPException(status_code=503, detail=f"Service {service_name} not available")
            
            # Build service URL
            service_url = f"http://{service_config['host']}:{service_config['port']}{path}"
            
            # Prepare request data
            method = request.method
            headers = dict(request.headers)
            
            # Remove hop-by-hop headers
            hop_by_hop = ["host", "connection", "content-length", "content-type"]
            for header in hop_by_hop:
                headers.pop(header, None)
            
            # Forward the request
            async with httpx.AsyncClient(timeout=config.service.timeout) as client:
                if method == "GET":
                    response = await client.get(service_url, headers=headers, params=request.query_params)
                elif method == "POST":
                    body = await request.body()
                    response = await client.post(service_url, headers=headers, content=body)
                elif method == "PUT":
                    body = await request.body()
                    response = await client.put(service_url, headers=headers, content=body)
                elif method == "DELETE":
                    response = await client.delete(service_url, headers=headers)
                elif method == "PATCH":
                    body = await request.body()
                    response = await client.patch(service_url, headers=headers, content=body)
                else:
                    raise HTTPException(status_code=405, detail="Method not allowed")
                
                # Return the response
                return JSONResponse(
                    content=response.json(),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
        except httpx.ConnectTimeout:
            logger.error(f"Connection timeout to {service_name}")
            raise HTTPException(status_code=504, detail="Service timeout")
        except httpx.ConnectError:
            logger.error(f"Connection error to {service_name}")
            raise HTTPException(status_code=503, detail="Service unavailable")
        except Exception as e:
            logger.error(f"Error forwarding request to {service_name}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    def _setup_exception_handlers(self):
        """Setup exception handlers"""
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content=ErrorResponse(
                    error=exc.detail,
                    code=exc.status_code
                ).model_dump()
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            logger.exception(f"Unexpected error: {exc}")
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error="Internal server error",
                    code=500,
                    details={"message": str(exc)}
                ).model_dump()
            )
    
    async def health_check(self):
        """Health check endpoint"""
        return HealthCheckResponse(
            service="api-gateway",
            version="1.0.0",
            dependencies={
                "auth-service": "healthy",
                "user-service": "healthy",
                "market-data-service": "healthy",
                "watchlist-service": "healthy",
                "screener-service": "healthy",
                "trading-service": "healthy",
                "alert-service": "healthy",
                "portfolio-service": "healthy",
                "notification-service": "healthy",
                "news-service": "healthy",
                "reporting-service": "healthy",
                "admin-dashboard": "healthy",
            }
        )
    
    async def root(self):
        """Root endpoint"""
        return {
            "service": "api-gateway",
            "version": "1.0.0",
            "description": "Stock Market Dashboard - API Gateway",
            "docs": "/docs",
            "health": "/health"
        }


# Create and run the API Gateway
def create_app() -> FastAPI:
    """Create the API Gateway FastAPI application"""
    gateway = APIGateway()
    return gateway.app


if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    
    logger.info("Starting API Gateway service...")
    logger.info(f"Service URL: {config.service.url}")
    
    uvicorn.run(
        app,
        host=config.service.host,
        port=config.service.port,
        reload=config.service.debug,
        workers=config.service.workers if not config.service.debug else 1,
        log_level=config.log_level.lower()
    )
