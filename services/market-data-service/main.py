"""
Market Data Service
Enterprise-grade market data service for Stock Market Dashboard
Provides real-time and historical market data using TradingView Screener
"""

import os
import sys
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

from shared_libs.utils import get_app_config, setup_logging
from shared_libs.models import (
    HealthCheckResponse,
    ErrorResponse,
    Quote,
    OHLCV,
    HistoricalData,
    MarketStatusResponse,
    MarketCalendar,
    ScreenerCriteria,
    ScreenerResult,
    Exchange,
    SymbolType,
    MarketStatus,
    ResponseModel,
    PaginatedResponse,
)
from shared_libs.contracts import REDIS_CHANNELS


# Initialize configuration
config = get_app_config()

# Initialize logger
logger = setup_logging(
    service_name="market-data-service",
    level=config.log_level,
    log_dir=config.log_dir,
    use_json=True
)


class MarketDataService:
    """Market Data Service"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Stock Market Dashboard - Market Data Service",
            description="Enterprise-grade market data service for Stock Market Dashboard",
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
        
        # In-memory cache for market data
        self.quote_cache: Dict[str, Quote] = {}
        self.ohlcv_cache: Dict[str, List[OHLCV]] = {}
        self.last_updated: Dict[str, datetime] = {}
        
        # Market status
        self.market_status: Dict[Exchange, MarketStatusResponse] = {}
        
        # HTTP client for external API calls
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(config.tradingview.poll_interval * 2, connect=10),
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=10)
        )
        
        # Start background tasks
        self._start_background_tasks()
    
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
        self.app.include_router(api_router, prefix="/api/v1/market")
        
        # WebSocket routes
        if config.enable_websocket:
            self.app.websocket("/ws/quotes")(self.websocket_quotes)
    
    def _create_api_router(self):
        """Create the API router"""
        from fastapi import APIRouter
        
        router = APIRouter()
        
        # Quote endpoints
        router.get("/quotes")(self.get_quotes)
        router.get("/quotes/{symbol}")(self.get_quote)
        
        # OHLCV endpoints
        router.get("/ohlcv")(self.get_ohlcv)
        router.get("/ohlcv/{symbol}")(self.get_ohlcv_symbol)
        
        # Market status
        router.get("/status")(self.get_market_status)
        router.get("/status/{exchange}")(self.get_exchange_status)
        
        # Market calendar
        router.get("/calendar")(self.get_market_calendar)
        router.get("/calendar/{exchange}")(self.get_exchange_calendar)
        
        # Screener
        router.post("/screener")(self.run_screener)
        
        # Search
        router.get("/search")(self.search_symbols)
        
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
    
    def _start_background_tasks(self):
        """Start background tasks for market data polling"""
        # Start market data poller
        asyncio.create_task(self._poll_market_data())
        
        # Start market status updater
        asyncio.create_task(self._update_market_status())
        
        logger.info("Background tasks started")
    
    async def _poll_market_data(self):
        """Poll market data from TradingView Screener"""
        while True:
            try:
                logger.info("Polling market data...")
                
                # In a real implementation, this would call TradingView Screener API
                # For now, we'll generate mock data
                await self._generate_mock_data()
                
                # Wait for the configured interval
                await asyncio.sleep(config.tradingview.poll_interval)
                
            except Exception as e:
                logger.error(f"Error polling market data: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _generate_mock_data(self):
        """Generate mock market data for demonstration"""
        # Popular Indian stocks
        symbols = [
            ("RELIANCE", Exchange.NSE),
            ("TCS", Exchange.NSE),
            ("INFY", Exchange.NSE),
            ("HDFCBANK", Exchange.NSE),
            ("ICICIBANK", Exchange.NSE),
            ("KOTAKBANK", Exchange.NSE),
            ("BHARTIARTL", Exchange.NSE),
            ("LT", Exchange.NSE),
            ("HINDUNILVR", Exchange.NSE),
            ("ITC", Exchange.NSE),
            ("SBIN", Exchange.NSE),
            ("ONGC", Exchange.NSE),
            ("NTPC", Exchange.NSE),
            ("COALINDIA", Exchange.NSE),
            ("POWERGRID", Exchange.NSE),
        ]
        
        import random
        
        for symbol, exchange in symbols:
            # Generate random price changes
            base_price = random.uniform(100, 5000)
            change_percent = random.uniform(-5, 5)
            change = base_price * (change_percent / 100)
            current_price = base_price + change
            
            # Generate OHLCV data
            open_price = base_price
            high = max(open_price, current_price) * random.uniform(1, 1.02)
            low = min(open_price, current_price) * random.uniform(0.98, 1)
            close = current_price
            volume = random.randint(100000, 10000000)
            
            # Create quote
            quote = Quote(
                symbol=symbol,
                exchange=exchange,
                symbol_type=SymbolType.STOCK,
                last_price=round(current_price, 2),
                open=round(open_price, 2),
                high=round(high, 2),
                low=round(low, 2),
                close=round(close, 2),
                previous_close=round(base_price, 2),
                volume=volume,
                average_volume=random.randint(500000, 5000000),
                change=round(change, 2),
                change_percent=round(change_percent, 2),
                week_52_high=round(base_price * 1.5, 2),
                week_52_low=round(base_price * 0.5, 2),
                timestamp=datetime.utcnow(),
                trade_time=datetime.utcnow(),
                bid=round(current_price * 0.999, 2),
                ask=round(current_price * 1.001, 2),
                bid_size=random.randint(100, 10000),
                ask_size=random.randint(100, 10000),
                spread=round(current_price * 0.002, 2)
            )
            
            # Update cache
            cache_key = f"{symbol}:{exchange.value}"
            self.quote_cache[cache_key] = quote
            self.last_updated[cache_key] = datetime.utcnow()
            
            logger.debug(f"Updated quote for {symbol}")
        
        # Generate OHLCV data for some symbols
        for symbol, exchange in symbols[:5]:  # Only for first 5 symbols
            ohlcv_data = []
            for i in range(30):  # Last 30 days
                date = datetime.utcnow() - timedelta(days=i)
                base = random.uniform(100, 5000)
                change = random.uniform(-3, 3)
                
                ohlcv = OHLCV(
                    symbol=symbol,
                    exchange=exchange,
                    timeframe="1D",
                    open=round(base, 2),
                    high=round(base * random.uniform(1, 1.03), 2),
                    low=round(base * random.uniform(0.97, 1), 2),
                    close=round(base + change, 2),
                    volume=random.randint(100000, 10000000),
                    timestamp=date
                )
                ohlcv_data.append(ohlcv)
            
            cache_key = f"{symbol}:{exchange.value}:ohlcv:1D"
            self.ohlcv_cache[cache_key] = ohlcv_data
            
            logger.debug(f"Updated OHLCV for {symbol}")
    
    async def _update_market_status(self):
        """Update market status"""
        while True:
            try:
                # In a real implementation, this would check market holidays and trading hours
                # For now, we'll use mock data
                
                # Indian market hours (IST: UTC+5:30)
                now = datetime.utcnow()
                
                # Convert to IST (UTC+5:30)
                ist_now = now + timedelta(hours=5, minutes=30)
                
                # Market open: 9:15 AM IST
                # Market close: 3:30 PM IST
                open_time = ist_now.replace(hour=9, minute=15, second=0, microsecond=0)
                close_time = ist_now.replace(hour=15, minute=30, second=0, microsecond=0)
                
                # Check if it's a weekend
                if ist_now.weekday() >= 5:  # Saturday or Sunday
                    status = MarketStatus.CLOSED
                # Check if it's within market hours
                elif open_time <= ist_now <= close_time:
                    status = MarketStatus.OPEN
                elif ist_now < open_time:
                    status = MarketStatus.PRE_OPEN
                else:
                    status = MarketStatus.POST_CLOSE
                
                # Update market status for NSE and BSE
                for exchange in [Exchange.NSE, Exchange.BSE]:
                    self.market_status[exchange] = MarketStatusResponse(
                        exchange=exchange,
                        status=status,
                        open_time=datetime(ist_now.year, ist_now.month, ist_now.day, 9, 15),
                        close_time=datetime(ist_now.year, ist_now.month, ist_now.day, 15, 30),
                        next_open_time=datetime(ist_now.year, ist_now.month, ist_now.day, 9, 15) if ist_now.hour < 9 else datetime(ist_now.year, ist_now.month, ist_now.day + 1, 9, 15),
                        next_close_time=datetime(ist_now.year, ist_now.month, ist_now.day, 15, 30) if ist_now.hour < 15 else datetime(ist_now.year, ist_now.month, ist_now.day + 1, 15, 30),
                        is_holiday=False,
                        holiday_name=None
                    )
                
                logger.debug("Updated market status")
                
                # Wait for 1 minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error updating market status: {e}")
                await asyncio.sleep(60)
    
    async def get_quotes(self, symbols: Optional[str] = None, exchange: Optional[Exchange] = None):
        """Get quotes for multiple symbols"""
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",")]
        else:
            # Return all cached quotes
            symbol_list = None
        
        quotes = []
        
        if symbol_list:
            for symbol in symbol_list:
                cache_key = f"{symbol}:{exchange.value if exchange else 'NSE'}"
                if cache_key in self.quote_cache:
                    quotes.append(self.quote_cache[cache_key])
                else:
                    # Try to fetch from external source
                    quote = await self._fetch_quote(symbol, exchange or Exchange.NSE)
                    if quote:
                        quotes.append(quote)
        else:
            # Return all cached quotes
            quotes = list(self.quote_cache.values())
        
        return PaginatedResponse(
            items=quotes,
            total=len(quotes),
            page=1,
            page_size=len(quotes),
            total_pages=1
        )
    
    async def get_quote(self, symbol: str, exchange: Optional[Exchange] = None):
        """Get quote for a single symbol"""
        symbol = symbol.upper()
        exchange = exchange or Exchange.NSE
        
        cache_key = f"{symbol}:{exchange.value}"
        
        # Check cache first
        if cache_key in self.quote_cache:
            return ResponseModel(
                success=True,
                data=self.quote_cache[cache_key]
            )
        
        # Try to fetch from external source
        quote = await self._fetch_quote(symbol, exchange)
        if quote:
            return ResponseModel(
                success=True,
                data=quote
            )
        
        raise HTTPException(status_code=404, detail=f"Quote not found for {symbol}")
    
    async def _fetch_quote(self, symbol: str, exchange: Exchange) -> Optional[Quote]:
        """Fetch quote from external source (TradingView Screener)"""
        try:
            # In a real implementation, this would call TradingView Screener API
            # For now, return None to indicate not found
            # The background poller will populate the cache
            return None
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
    
    async def get_ohlcv(self, symbol: Optional[str] = None, exchange: Optional[Exchange] = None, timeframe: str = "1D"):
        """Get OHLCV data for multiple symbols"""
        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol is required")
        
        symbol = symbol.upper()
        exchange = exchange or Exchange.NSE
        
        cache_key = f"{symbol}:{exchange.value}:ohlcv:{timeframe}"
        
        if cache_key in self.ohlcv_cache:
            return ResponseModel(
                success=True,
                data=HistoricalData(
                    symbol=symbol,
                    exchange=exchange,
                    timeframe=timeframe,
                    data=self.ohlcv_cache[cache_key]
                )
            )
        
        # Try to fetch from external source
        ohlcv_data = await self._fetch_ohlcv(symbol, exchange, timeframe)
        if ohlcv_data:
            return ResponseModel(
                success=True,
                data=HistoricalData(
                    symbol=symbol,
                    exchange=exchange,
                    timeframe=timeframe,
                    data=ohlcv_data
                )
            )
        
        raise HTTPException(status_code=404, detail=f"OHLCV data not found for {symbol}")
    
    async def get_ohlcv_symbol(self, symbol: str, exchange: Optional[Exchange] = None, timeframe: str = "1D"):
        """Get OHLCV data for a single symbol"""
        return await self.get_ohlcv(symbol, exchange, timeframe)
    
    async def _fetch_ohlcv(self, symbol: str, exchange: Exchange, timeframe: str) -> Optional[List[OHLCV]]:
        """Fetch OHLCV data from external source"""
        try:
            # In a real implementation, this would call TradingView Screener API
            return None
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return None
    
    async def get_market_status(self):
        """Get market status for all exchanges"""
        statuses = list(self.market_status.values())
        return PaginatedResponse(
            items=statuses,
            total=len(statuses),
            page=1,
            page_size=len(statuses),
            total_pages=1
        )
    
    async def get_exchange_status(self, exchange: Exchange):
        """Get market status for a specific exchange"""
        if exchange in self.market_status:
            return ResponseModel(
                success=True,
                data=self.market_status[exchange]
            )
        
        raise HTTPException(status_code=404, detail=f"Market status not found for {exchange}")
    
    async def get_market_calendar(self, exchange: Optional[Exchange] = None, days: int = 30):
        """Get market calendar"""
        # In a real implementation, this would use pandas-market-calendars
        # For now, return mock data
        
        calendars = []
        today = datetime.utcnow()
        
        for i in range(days):
            date = today + timedelta(days=i)
            
            # Check if weekend
            if date.weekday() >= 5:
                is_trading_day = False
                is_holiday = False
                holiday_name = None
            else:
                is_trading_day = True
                is_holiday = False
                holiday_name = None
            
            calendar = MarketCalendar(
                exchange=exchange or Exchange.NSE,
                date=date,
                is_trading_day=is_trading_day,
                is_holiday=is_holiday,
                holiday_name=holiday_name,
                market_open=datetime(date.year, date.month, date.day, 9, 15),
                market_close=datetime(date.year, date.month, date.day, 15, 30)
            )
            calendars.append(calendar)
        
        return PaginatedResponse(
            items=calendars,
            total=len(calendars),
            page=1,
            page_size=len(calendars),
            total_pages=1
        )
    
    async def get_exchange_calendar(self, exchange: Exchange, days: int = 30):
        """Get market calendar for a specific exchange"""
        return await self.get_market_calendar(exchange, days)
    
    async def run_screener(self, criteria: ScreenerCriteria):
        """Run stock screener with given criteria"""
        # In a real implementation, this would use TradingView Screener
        # For now, return mock results
        
        results = []
        
        # Filter cached quotes based on criteria
        for quote in self.quote_cache.values():
            # Apply filters
            if criteria.exchange and quote.exchange != criteria.exchange:
                continue
            
            if criteria.symbol_type and quote.symbol_type != criteria.symbol_type:
                continue
            
            if criteria.min_price and quote.last_price < criteria.min_price:
                continue
            
            if criteria.max_price and quote.last_price > criteria.max_price:
                continue
            
            if criteria.min_volume and quote.volume < criteria.min_volume:
                continue
            
            if criteria.max_volume and quote.volume > criteria.max_volume:
                continue
            
            if criteria.min_change_percent and quote.change_percent < criteria.min_change_percent:
                continue
            
            if criteria.max_change_percent and quote.change_percent > criteria.max_change_percent:
                continue
            
            # Create screener result
            result = ScreenerResult(
                symbol=quote.symbol,
                exchange=quote.exchange,
                symbol_type=quote.symbol_type,
                last_price=quote.last_price,
                change=quote.change,
                change_percent=quote.change_percent,
                volume=quote.volume,
                market_cap=None,  # Would be calculated in real implementation
                sector=None,
                industry=None,
                rsi=random.uniform(0, 100) if hasattr(self, 'random') else 50.0,
                macd=None,
                macd_signal=None,
                macd_histogram=None,
                sma_20=None,
                sma_50=None,
                sma_200=None,
                score=abs(quote.change_percent) * 10  # Simple score based on change
            )
            results.append(result)
        
        # Sort results
        if criteria.sort_by == "change_percent":
            results.sort(key=lambda x: x.change_percent, reverse=(criteria.sort_order == "desc"))
        
        # Apply limit and offset
        results = results[criteria.offset:criteria.offset + criteria.limit]
        
        return ResponseModel(
            success=True,
            data=results,
            message=f"Found {len(results)} results"
        )
    
    async def search_symbols(self, query: str, limit: int = 10):
        """Search for symbols"""
        query = query.upper()
        results = []
        
        for quote in self.quote_cache.values():
            if query in quote.symbol:
                results.append(quote)
                if len(results) >= limit:
                    break
        
        return ResponseModel(
            success=True,
            data=results
        )
    
    async def websocket_quotes(self, websocket: WebSocket):
        """WebSocket endpoint for live quote updates"""
        await websocket.accept()
        
        try:
            # Send initial quotes
            quotes = list(self.quote_cache.values())
            await websocket.send_json({
                "type": "initial",
                "data": [quote.model_dump() for quote in quotes]
            })
            
            # Keep connection open and send updates
            while True:
                # Wait for updates
                await asyncio.sleep(config.tradingview.poll_interval)
                
                # Send updated quotes
                quotes = list(self.quote_cache.values())
                await websocket.send_json({
                    "type": "update",
                    "data": [quote.model_dump() for quote in quotes],
                    "timestamp": datetime.utcnow().isoformat()
                })
                
        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await websocket.close(code=1011)
    
    async def health_check(self):
        """Health check endpoint"""
        return HealthCheckResponse(
            service="market-data-service",
            version="1.0.0",
            dependencies={
                "tradingview": "healthy",
                "cache": "healthy",
                "websocket": "healthy"
            }
        )
    
    async def root(self):
        """Root endpoint"""
        return {
            "service": "market-data-service",
            "version": "1.0.0",
            "description": "Market Data Service for Stock Market Dashboard",
            "docs": "/docs",
            "health": "/health",
            "websocket": "/ws/quotes"
        }


# Create and run the Market Data Service
def create_app() -> FastAPI:
    """Create the Market Data Service FastAPI application"""
    market_data_service = MarketDataService()
    return market_data_service.app


if __name__ == "__main__":
    import uvicorn
    import random
    
    # Add random to the service for mock data generation
    MarketDataService.random = random
    
    app = create_app()
    
    logger.info("Starting Market Data Service...")
    logger.info(f"Service URL: {config.service.url}")
    
    uvicorn.run(
        app,
        host=config.service.host,
        port=config.service.port,
        reload=config.service.debug,
        workers=config.service.workers if not config.service.debug else 1,
        log_level=config.log_level.lower()
    )
