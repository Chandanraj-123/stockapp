"""
Watchlist Models for Stock Market Dashboard
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .base import BaseSchema, TimestampMixin
from .market_data import Exchange, SymbolType


class WatchlistBase(BaseSchema):
    """Base watchlist model"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_public: bool = False
    is_default: bool = False


class WatchlistCreate(BaseSchema):
    """Watchlist creation model"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_public: bool = False


class WatchlistUpdate(BaseSchema):
    """Watchlist update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_public: Optional[bool] = None
    is_default: Optional[bool] = None


class Watchlist(WatchlistBase, TimestampMixin):
    """Complete watchlist model"""
    id: str
    user_id: str
    items: List[dict] = []


class WatchlistPublic(BaseSchema):
    """Public watchlist model"""
    id: str
    name: str
    description: Optional[str] = None
    user_id: str
    is_public: bool
    item_count: int
    created_at: datetime
    updated_at: datetime


class WatchlistItemBase(BaseSchema):
    """Base watchlist item model"""
    symbol: str
    exchange: Exchange
    symbol_type: SymbolType = SymbolType.STOCK
    
    # Custom display settings
    display_name: Optional[str] = None
    color: Optional[str] = None  # For UI customization
    
    # Alert settings
    alert_price_above: Optional[float] = None
    alert_price_below: Optional[float] = None
    alert_change_percent: Optional[float] = None
    
    # Notes
    notes: Optional[str] = Field(None, max_length=1000)


class WatchlistItemCreate(BaseSchema):
    """Watchlist item creation model"""
    symbol: str
    exchange: Exchange
    symbol_type: SymbolType = SymbolType.STOCK
    display_name: Optional[str] = None
    color: Optional[str] = None
    alert_price_above: Optional[float] = None
    alert_price_below: Optional[float] = None
    alert_change_percent: Optional[float] = None
    notes: Optional[str] = Field(None, max_length=1000)


class WatchlistItemUpdate(BaseSchema):
    """Watchlist item update model"""
    symbol: Optional[str] = None
    exchange: Optional[Exchange] = None
    symbol_type: Optional[SymbolType] = None
    display_name: Optional[str] = None
    color: Optional[str] = None
    alert_price_above: Optional[float] = None
    alert_price_below: Optional[float] = None
    alert_change_percent: Optional[float] = None
    notes: Optional[str] = Field(None, max_length=1000)


class WatchlistItem(WatchlistItemBase, TimestampMixin):
    """Complete watchlist item model"""
    id: str
    watchlist_id: str
    position: int = 0  # For ordering within watchlist
    
    # Current market data (cached)
    current_price: Optional[float] = None
    current_change: Optional[float] = None
    current_change_percent: Optional[float] = None
    current_volume: Optional[int] = None


class WatchlistItemPublic(BaseSchema):
    """Public watchlist item model"""
    id: str
    symbol: str
    exchange: Exchange
    symbol_type: SymbolType
    display_name: Optional[str] = None
    color: Optional[str] = None
    position: int
    current_price: Optional[float] = None
    current_change: Optional[float] = None
    current_change_percent: Optional[float] = None
    current_volume: Optional[int] = None
    created_at: datetime


class WatchlistWithItems(BaseSchema):
    """Watchlist with items"""
    id: str
    name: str
    description: Optional[str] = None
    user_id: str
    is_public: bool
    is_default: bool
    items: List[WatchlistItemPublic]
    created_at: datetime
    updated_at: datetime
