"""
Market Data Models for Stock Market Dashboard
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from .base import BaseSchema, TimestampMixin


class Exchange(str, Enum):
    """Stock exchanges"""
    NSE = "NSE"
    BSE = "BSE"
    NFO = "NFO"
    BFO = "BFO"
    MCX = "MCX"


class SymbolType(str, Enum):
    """Symbol types"""
    STOCK = "stock"
    INDEX = "index"
    FUTURE = "future"
    OPTION = "option"
    COMMODITY = "commodity"
    FOREX = "forex"
    CRYPTO = "crypto"


class MarketStatus(str, Enum):
    """Market status"""
    CLOSED = "closed"
    OPEN = "open"
    PRE_OPEN = "pre_open"
    POST_CLOSE = "post_close"
    HOLIDAY = "holiday"


class Quote(BaseSchema):
    """Stock quote model"""
    symbol: str
    exchange: Exchange
    symbol_type: SymbolType = SymbolType.STOCK
    
    # Price data
    last_price: float
    open: float
    high: float
    low: float
    close: float
    previous_close: float
    
    # Volume data
    volume: int
    average_volume: int
    
    # Change metrics
    change: float
    change_percent: float
    
    # 52-week data
    week_52_high: float
    week_52_low: float
    
    # Time data
    timestamp: datetime
    trade_time: datetime
    
    # Additional info
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None
    spread: Optional[float] = None


class OHLCV(BaseSchema):
    """OHLCV (Open, High, Low, Close, Volume) model"""
    symbol: str
    exchange: Exchange
    timeframe: str = "1D"  # 1D, 1W, 1M, 1Y, etc.
    
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    timestamp: datetime


class HistoricalData(BaseSchema):
    """Historical price data"""
    symbol: str
    exchange: Exchange
    timeframe: str
    data: List[OHLCV]
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "RELIANCE",
                "exchange": "NSE",
                "timeframe": "1D",
                "data": []
            }
        }


class ScreenerCriteria(BaseSchema):
    """Stock screener criteria"""
    exchange: Optional[Exchange] = None
    symbol_type: Optional[SymbolType] = None
    
    # Price filters
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    
    # Volume filters
    min_volume: Optional[int] = None
    max_volume: Optional[int] = None
    
    # Change filters
    min_change_percent: Optional[float] = None
    max_change_percent: Optional[float] = None
    
    # 52-week filters
    near_52w_high: Optional[bool] = None
    near_52w_low: Optional[bool] = None
    
    # Market cap filters
    min_market_cap: Optional[float] = None
    max_market_cap: Optional[float] = None
    
    # Sector/Industry filters
    sectors: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    
    # Technical indicators
    rsi_min: Optional[float] = None
    rsi_max: Optional[float] = None
    macd_signal: Optional[str] = None  # bullish, bearish, neutral
    
    # Sorting
    sort_by: str = "change_percent"
    sort_order: str = "desc"  # asc or desc
    
    # Pagination
    limit: int = 50
    offset: int = 0


class ScreenerResult(BaseSchema):
    """Screener result"""
    symbol: str
    exchange: Exchange
    symbol_type: SymbolType
    last_price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    
    # Technical indicators
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    
    # Moving averages
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    
    # Score
    score: float = 0.0


class MarketStatusResponse(BaseSchema):
    """Market status response"""
    exchange: Exchange
    status: MarketStatus
    open_time: datetime
    close_time: datetime
    next_open_time: datetime
    next_close_time: datetime
    is_holiday: bool = False
    holiday_name: Optional[str] = None


class MarketCalendar(BaseSchema):
    """Market calendar"""
    exchange: Exchange
    date: datetime
    is_trading_day: bool
    is_holiday: bool
    holiday_name: Optional[str] = None
    market_open: datetime
    market_close: datetime
