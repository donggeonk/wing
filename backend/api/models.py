"""
Pydantic models for request/response validation
These define the API contract between frontend and backend
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ========== Chat Models ==========

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=5000, description="User's message")
    session_id: Optional[str] = Field(default="default", description="Session identifier for conversation tracking")

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="Assistant's response")
    success: bool = Field(..., description="Whether the request was successful")
    error: Optional[str] = Field(None, description="Error message if request failed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

# ========== Portfolio Models ==========

class Position(BaseModel):
    """Individual stock position"""
    symbol: str
    qty: float
    market_value: float
    cost_basis: float
    unrealized_pl: float
    unrealized_plpc: float
    current_price: float
    avg_entry_price: float

class PortfolioResponse(BaseModel):
    """Portfolio summary response"""
    total_equity: float
    cash: float
    buying_power: float
    positions: List[Position]
    total_positions: int
    total_unrealized_pl: float
    cash_percentage: float
    invested_percentage: float
    success: bool

class AccountResponse(BaseModel):
    """Account information response"""
    account_number: str
    status: str
    currency: str
    buying_power: float
    cash: float
    portfolio_value: float
    equity: float
    last_equity: float
    multiplier: str
    success: bool

# ========== Market Data Models ==========

class StockSnapshot(BaseModel):
    """Stock market snapshot"""
    symbol: str
    current_price: float
    daily_open: float
    daily_high: float
    daily_low: float
    daily_close: float
    previous_close: float
    volume: int
    change: float
    change_percent: float
    success: bool

class HistoricalStats(BaseModel):
    """Historical statistics response"""
    symbol: str
    period_days: int
    average_close: float
    period_high: float
    period_low: float
    average_volume: float
    start_date: str
    end_date: str
    success: bool

class StockComparison(BaseModel):
    """Stock comparison response"""
    symbols: List[str]
    period_days: int
    data: Dict[str, Any]
    success: bool

# ========== Trading Models ==========

class MarketOrderRequest(BaseModel):
    """Request to place a market order"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL)")
    qty: float = Field(..., gt=0, description="Quantity to trade")
    side: str = Field(..., pattern="^(buy|sell)$", description="Order side: buy or sell")

class LimitOrderRequest(BaseModel):
    """Request to place a limit order"""
    symbol: str
    qty: float = Field(..., gt=0)
    side: str = Field(..., pattern="^(buy|sell)$")
    limit_price: float = Field(..., gt=0, description="Limit price")

class StopOrderRequest(BaseModel):
    """Request to place a stop order"""
    symbol: str
    qty: float = Field(..., gt=0)
    side: str = Field(..., pattern="^(buy|sell)$")
    stop_price: float = Field(..., gt=0, description="Stop price")

class OrderResponse(BaseModel):
    """Order execution response"""
    success: bool
    order_id: Optional[str] = None
    symbol: Optional[str] = None
    qty: Optional[float] = None
    side: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None

class OrderListResponse(BaseModel):
    """List of orders response"""
    orders: List[Dict[str, Any]]
    count: int
    success: bool

# ========== News Models ==========

class NewsRequest(BaseModel):
    """Request for news"""
    symbol: str
    days: int = Field(default=7, ge=1, le=30, description="Days to look back")
    limit: int = Field(default=5, ge=1, le=20, description="Max articles to return")

class NewsArticle(BaseModel):
    """Single news article"""
    headline: str
    summary: str
    source: str
    url: str
    published_at: str

class NewsResponse(BaseModel):
    """News articles response"""
    symbol: str
    articles: List[NewsArticle]
    count: int
    success: bool

# ========== Generic Models ==========

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str

class ErrorResponse(BaseModel):
    """Generic error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)