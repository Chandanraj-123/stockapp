"""
Trading Models for Stock Market Dashboard
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from .base import BaseSchema, TimestampMixin
from .market_data import Exchange, SymbolType


class OrderType(str, Enum):
    """Order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"


class OrderSide(str, Enum):
    """Order side"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    """Order status"""
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class GTTType(str, Enum):
    """GTT (Good Till Trigger) types"""
    SINGLE = "single"
    OCO = "oco"  # One Cancels Other
    

class GTTStatus(str, Enum):
    """GTT status"""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    EXECUTED = "executed"


class AlertType(str, Enum):
    """Alert types"""
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    CHANGE_ABOVE = "change_above"
    CHANGE_BELOW = "change_below"
    VOLUME_ABOVE = "volume_above"
    VOLUME_BELOW = "volume_below"
    RSI_ABOVE = "rsi_above"
    RSI_BELOW = "rsi_below"
    CUSTOM = "custom"  # Custom condition


class AlertStatus(str, Enum):
    """Alert status"""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    CANCELLED = "cancelled"


class Alert(BaseSchema):
    """Alert model"""
    symbol: str
    exchange: Exchange
    symbol_type: SymbolType = SymbolType.STOCK
    
    alert_type: AlertType
    condition_value: float  # The threshold value
    
    # For custom alerts
    custom_condition: Optional[str] = None
    
    # Notification settings
    notify_email: bool = True
    notify_push: bool = True
    notify_sms: bool = False
    
    # Status
    status: AlertStatus = AlertStatus.ACTIVE
    triggered_at: Optional[datetime] = None
    triggered_price: Optional[float] = None
    
    # Repeat settings
    repeat: bool = False
    repeat_interval: Optional[str] = None  # daily, weekly, etc.


class AlertCreate(BaseSchema):
    """Alert creation model"""
    symbol: str
    exchange: Exchange
    symbol_type: SymbolType = SymbolType.STOCK
    
    alert_type: AlertType
    condition_value: float
    
    custom_condition: Optional[str] = None
    
    notify_email: bool = True
    notify_push: bool = True
    notify_sms: bool = False
    
    repeat: bool = False
    repeat_interval: Optional[str] = None


class AlertUpdate(BaseSchema):
    """Alert update model"""
    symbol: Optional[str] = None
    exchange: Optional[Exchange] = None
    symbol_type: Optional[SymbolType] = None
    
    alert_type: Optional[AlertType] = None
    condition_value: Optional[float] = None
    
    custom_condition: Optional[str] = None
    
    notify_email: Optional[bool] = None
    notify_push: Optional[bool] = None
    notify_sms: Optional[bool] = None
    
    status: Optional[AlertStatus] = None
    repeat: Optional[bool] = None
    repeat_interval: Optional[str] = None


class GTTOrder(BaseSchema):
    """GTT (Good Till Trigger) Order model"""
    symbol: str
    exchange: Exchange
    symbol_type: SymbolType = SymbolType.STOCK
    
    # Trigger conditions
    trigger_price: float
    trigger_condition: str = "above"  # above or below
    
    # Order to execute when triggered
    order_type: OrderType
    order_side: OrderSide
    quantity: int
    limit_price: Optional[float] = None  # For limit orders
    
    # GTT type
    gtt_type: GTTType = GTTType.SINGLE
    
    # For OCO orders
    oco_leg2_trigger_price: Optional[float] = None
    oco_leg2_order_type: Optional[OrderType] = None
    oco_leg2_order_side: Optional[OrderSide] = None
    oco_leg2_quantity: Optional[int] = None
    oco_leg2_limit_price: Optional[float] = None
    
    # Status
    status: GTTStatus = GTTStatus.ACTIVE
    triggered_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    
    # Expiry
    expiry_date: Optional[datetime] = None
    
    # Notes
    notes: Optional[str] = Field(None, max_length=1000)


class GTTOrderCreate(BaseSchema):
    """GTT Order creation model"""
    symbol: str
    exchange: Exchange
    symbol_type: SymbolType = SymbolType.STOCK
    
    trigger_price: float
    trigger_condition: str = "above"
    
    order_type: OrderType
    order_side: OrderSide
    quantity: int
    limit_price: Optional[float] = None
    
    gtt_type: GTTType = GTTType.SINGLE
    
    oco_leg2_trigger_price: Optional[float] = None
    oco_leg2_order_type: Optional[OrderType] = None
    oco_leg2_order_side: Optional[OrderSide] = None
    oco_leg2_quantity: Optional[int] = None
    oco_leg2_limit_price: Optional[float] = None
    
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=1000)


class GTTOrderUpdate(BaseSchema):
    """GTT Order update model"""
    symbol: Optional[str] = None
    exchange: Optional[Exchange] = None
    symbol_type: Optional[SymbolType] = None
    
    trigger_price: Optional[float] = None
    trigger_condition: Optional[str] = None
    
    order_type: Optional[OrderType] = None
    order_side: Optional[OrderSide] = None
    quantity: Optional[int] = None
    limit_price: Optional[float] = None
    
    gtt_type: Optional[GTTType] = None
    
    oco_leg2_trigger_price: Optional[float] = None
    oco_leg2_order_type: Optional[OrderType] = None
    oco_leg2_order_side: Optional[OrderSide] = None
    oco_leg2_quantity: Optional[int] = None
    oco_leg2_limit_price: Optional[float] = None
    
    status: Optional[GTTStatus] = None
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=1000)


class PortfolioItem(BaseSchema):
    """Portfolio item model"""
    symbol: str
    exchange: Exchange
    symbol_type: SymbolType = SymbolType.STOCK
    
    # Holdings
    quantity: float
    average_price: float
    
    # Current market data
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    
    # P&L
    investment_value: float
    current_value_total: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None
    
    # Day P&L
    day_profit_loss: Optional[float] = None
    day_profit_loss_percent: Optional[float] = None
    
    # Purchase info
    purchase_date: datetime
    purchase_notes: Optional[str] = Field(None, max_length=1000)


class Portfolio(BaseSchema):
    """Portfolio model"""
    name: str
    description: Optional[str] = None
    items: List[PortfolioItem]
    
    # Aggregate metrics
    total_investment: float
    total_current_value: Optional[float] = None
    total_profit_loss: Optional[float] = None
    total_profit_loss_percent: Optional[float] = None
    
    # Cash balance
    cash_balance: float = 0.0
    
    # Performance metrics
    day_change: Optional[float] = None
    day_change_percent: Optional[float] = None


class Trade(BaseSchema, TimestampMixin):
    """Trade model"""
    symbol: str
    exchange: Exchange
    symbol_type: SymbolType = SymbolType.STOCK
    
    order_type: OrderType
    order_side: OrderSide
    quantity: float
    price: float
    
    # Fees
    brokerage: float = 0.0
    taxes: float = 0.0
    total_charges: float = 0.0
    
    # Status
    status: str = "completed"
    
    # Notes
    notes: Optional[str] = Field(None, max_length=1000)
    
    # Reference
    order_id: Optional[str] = None
    trade_id: Optional[str] = None
