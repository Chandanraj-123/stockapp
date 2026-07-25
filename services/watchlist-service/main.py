"""
Watchlist Service
Enterprise-grade watchlist service for Stock Market Dashboard
Manages user watchlists and symbols
"""

import os
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared_libs.utils import get_app_config, setup_logging
from shared_libs.models import (
    HealthCheckResponse,
    ErrorResponse,
    WatchlistCreate,
    WatchlistUpdate,
    WatchlistWithItems,
    WatchlistItemCreate,
    WatchlistItemUpdate,
    ResponseModel,
    PaginatedResponse,
)


# Initialize configuration
config = get_app_config()

# Initialize logger
logger = setup_logging(
    service_name="watchlist-service",
    level=config.log_level,
    log_dir=config.log_dir,
    use_json=True
)


class WatchlistService:
    """Watchlist Service"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Stock Market Dashboard - Watchlist Service",
            description="Enterprise-grade watchlist service for Stock Market Dashboard",
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
        
        # In-memory storage (replace with database in production)
        self.watchlists: Dict[str, Dict[str, Any]] = {}
        self.watchlist_items: Dict[str, Dict[str, Any]] = {}
    
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
        self.app.include_router(api_router, prefix="/api/v1/watchlists")
    
    def _create_api_router(self):
        """Create the API router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        # Watchlist endpoints
        router.post("/")(self.create_watchlist)
        router.get("/")(self.list_watchlists)
        router.get("/{watchlist_id}")(self.get_watchlist)
        router.put("/{watchlist_id}")(self.update_watchlist)
        router.delete("/{watchlist_id}")(self.delete_watchlist)
        
        # Watchlist item endpoints
        router.post("/{watchlist_id}/items")(self.add_watchlist_item)
        router.get("/{watchlist_id}/items")(self.list_watchlist_items)
        router.get("/{watchlist_id}/items/{item_id}")(self.get_watchlist_item)
        router.put("/{watchlist_id}/items/{item_id}")(self.update_watchlist_item)
        router.delete("/{watchlist_id}/items/{item_id}")(self.delete_watchlist_item)
        
        return router
    
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
    
    async def create_watchlist(self, watchlist_data: WatchlistCreate, user_id: str = "default"):
        """Create a new watchlist"""
        watchlist_id = str(uuid4())
        watchlist = {
            "id": watchlist_id,
            "user_id": user_id,
            "name": watchlist_data.name,
            "description": watchlist_data.description,
            "is_public": watchlist_data.is_public,
            "is_default": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        self.watchlists[watchlist_id] = watchlist
        
        logger.info(f"Watchlist created: {watchlist['name']} by user {user_id}")
        
        return ResponseModel(
            success=True,
            data=watchlist,
            message="Watchlist created successfully"
        )
    
    async def list_watchlists(self, user_id: str = "default"):
        """List all watchlists for a user"""
        user_watchlists = [
            wl for wl in self.watchlists.values() 
            if wl.get("user_id") == user_id
        ]
        
        return PaginatedResponse(
            items=user_watchlists,
            total=len(user_watchlists),
            page=1,
            page_size=len(user_watchlists),
            total_pages=1
        )
    
    async def get_watchlist(self, watchlist_id: str):
        """Get a watchlist by ID"""
        watchlist = self.watchlists.get(watchlist_id)
        if not watchlist:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        
        # Get items for this watchlist
        items = [
            item for item in self.watchlist_items.values() 
            if item.get("watchlist_id") == watchlist_id
        ]
        
        watchlist_with_items = {
            **watchlist,
            "items": items
        }
        
        return ResponseModel(
            success=True,
            data=watchlist_with_items
        )
    
    async def update_watchlist(self, watchlist_id: str, watchlist_data: WatchlistUpdate):
        """Update a watchlist"""
        watchlist = self.watchlists.get(watchlist_id)
        if not watchlist:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        
        # Update fields
        if watchlist_data.name:
            watchlist["name"] = watchlist_data.name
        if watchlist_data.description is not None:
            watchlist["description"] = watchlist_data.description
        if watchlist_data.is_public is not None:
            watchlist["is_public"] = watchlist_data.is_public
        if watchlist_data.is_default is not None:
            watchlist["is_default"] = watchlist_data.is_default
        
        watchlist["updated_at"] = datetime.utcnow()
        
        logger.info(f"Watchlist updated: {watchlist['name']}")
        
        return ResponseModel(
            success=True,
            data=watchlist,
            message="Watchlist updated successfully"
        )
    
    async def delete_watchlist(self, watchlist_id: str):
        """Delete a watchlist"""
        watchlist = self.watchlists.get(watchlist_id)
        if not watchlist:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        
        # Delete all items in the watchlist
        for item_id, item in list(self.watchlist_items.items()):
            if item.get("watchlist_id") == watchlist_id:
                del self.watchlist_items[item_id]
        
        # Delete the watchlist
        del self.watchlists[watchlist_id]
        
        logger.info(f"Watchlist deleted: {watchlist['name']}")
        
        return ResponseModel(
            success=True,
            message="Watchlist deleted successfully"
        )
    
    async def add_watchlist_item(self, watchlist_id: str, item_data: WatchlistItemCreate):
        """Add an item to a watchlist"""
        watchlist = self.watchlists.get(watchlist_id)
        if not watchlist:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        
        item_id = str(uuid4())
        item = {
            "id": item_id,
            "watchlist_id": watchlist_id,
            "symbol": item_data.symbol,
            "exchange": item_data.exchange,
            "symbol_type": item_data.symbol_type,
            "display_name": item_data.display_name,
            "color": item_data.color,
            "position": len([i for i in self.watchlist_items.values() if i.get("watchlist_id") == watchlist_id]),
            "alert_price_above": item_data.alert_price_above,
            "alert_price_below": item_data.alert_price_below,
            "alert_change_percent": item_data.alert_change_percent,
            "notes": item_data.notes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        self.watchlist_items[item_id] = item
        
        logger.info(f"Watchlist item added: {item['symbol']} to watchlist {watchlist_id}")
        
        return ResponseModel(
            success=True,
            data=item,
            message="Watchlist item added successfully"
        )
    
    async def list_watchlist_items(self, watchlist_id: str):
        """List all items in a watchlist"""
        watchlist = self.watchlists.get(watchlist_id)
        if not watchlist:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        
        items = [
            item for item in self.watchlist_items.values() 
            if item.get("watchlist_id") == watchlist_id
        ]
        
        return PaginatedResponse(
            items=items,
            total=len(items),
            page=1,
            page_size=len(items),
            total_pages=1
        )
    
    async def get_watchlist_item(self, watchlist_id: str, item_id: str):
        """Get a watchlist item"""
        item = self.watchlist_items.get(item_id)
        if not item or item.get("watchlist_id") != watchlist_id:
            raise HTTPException(status_code=404, detail="Watchlist item not found")
        
        return ResponseModel(
            success=True,
            data=item
        )
    
    async def update_watchlist_item(self, watchlist_id: str, item_id: str, item_data: WatchlistItemUpdate):
        """Update a watchlist item"""
        item = self.watchlist_items.get(item_id)
        if not item or item.get("watchlist_id") != watchlist_id:
            raise HTTPException(status_code=404, detail="Watchlist item not found")
        
        # Update fields
        if item_data.symbol:
            item["symbol"] = item_data.symbol
        if item_data.exchange:
            item["exchange"] = item_data.exchange
        if item_data.symbol_type:
            item["symbol_type"] = item_data.symbol_type
        if item_data.display_name is not None:
            item["display_name"] = item_data.display_name
        if item_data.color is not None:
            item["color"] = item_data.color
        if item_data.position is not None:
            item["position"] = item_data.position
        if item_data.alert_price_above is not None:
            item["alert_price_above"] = item_data.alert_price_above
        if item_data.alert_price_below is not None:
            item["alert_price_below"] = item_data.alert_price_below
        if item_data.alert_change_percent is not None:
            item["alert_change_percent"] = item_data.alert_change_percent
        if item_data.notes is not None:
            item["notes"] = item_data.notes
        
        item["updated_at"] = datetime.utcnow()
        
        logger.info(f"Watchlist item updated: {item['symbol']}")
        
        return ResponseModel(
            success=True,
            data=item,
            message="Watchlist item updated successfully"
        )
    
    async def delete_watchlist_item(self, watchlist_id: str, item_id: str):
        """Delete a watchlist item"""
        item = self.watchlist_items.get(item_id)
        if not item or item.get("watchlist_id") != watchlist_id:
            raise HTTPException(status_code=404, detail="Watchlist item not found")
        
        del self.watchlist_items[item_id]
        
        logger.info(f"Watchlist item deleted: {item['symbol']}")
        
        return ResponseModel(
            success=True,
            message="Watchlist item deleted successfully"
        )
    
    async def health_check(self):
        """Health check endpoint"""
        return HealthCheckResponse(
            service="watchlist-service",
            version="1.0.0",
            dependencies={
                "database": "healthy",
                "cache": "healthy"
            }
        )
    
    async def root(self):
        """Root endpoint"""
        return {
            "service": "watchlist-service",
            "version": "1.0.0",
            "description": "Watchlist Service for Stock Market Dashboard",
            "docs": "/docs",
            "health": "/health"
        }


# Create and run the Watchlist Service
def create_app() -> FastAPI:
    """Create the Watchlist Service FastAPI application"""
    watchlist_service = WatchlistService()
    return watchlist_service.app


if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    
    logger.info("Starting Watchlist Service...")
    logger.info(f"Service URL: {config.service.url}")
    
    uvicorn.run(
        app,
        host=config.service.host,
        port=config.service.port,
        reload=config.service.debug,
        workers=config.service.workers if not config.service.debug else 1,
        log_level=config.log_level.lower()
    )
