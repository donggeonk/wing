"""
API Routes for Trading Copilot
Defines all HTTP endpoints and their handlers
"""

from alpaca.trading.client import TradingClient
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import sys
import os

# Add parent directory to path to import copilot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.models import (
    ChatRequest, ChatResponse,
    PortfolioResponse, AccountResponse,
    StockSnapshot, HistoricalStats, StockComparison,
    MarketOrderRequest, LimitOrderRequest, StopOrderRequest, OrderResponse,
    OrderListResponse, NewsRequest, NewsResponse, HealthResponse
)
from copilot import TradingAssistant
from core.config import settings

# Initialize router
router = APIRouter()

# Initialize trading assistant (singleton for now)
# TODO: Move to dependency injection for multi-user support
assistant = TradingAssistant()

# ========== Health & Status ==========

@router.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint - API info"""
    return {
        "message": "AI Trading Copilot API",
        "version": settings.API_VERSION,
        "status": "running"
    }

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION
    )

# ========== Chat Endpoints ==========

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    Sends user message to AI copilot and returns response
    """
    try:
        response = assistant.chat(request.message)
        return ChatResponse(
            response=response,
            success=True
        )
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return ChatResponse(
            response="",
            success=False,
            error=str(e)
        )

@router.post("/chat/reset", response_model=Dict[str, Any])
async def reset_chat():
    """Reset conversation history"""
    try:
        assistant.reset_conversation()
        return {"success": True, "message": "Conversation reset successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ========== Portfolio Endpoints ==========

@router.get("/portfolio")
async def get_portfolio():
    """Get complete portfolio summary"""
    try:
        trading_client = TradingClient(
            settings.ALPACA_API_KEY,
            settings.ALPACA_SECRET_KEY,
            paper=True
        )
        
        # Get account info
        account = trading_client.get_account()
        
        # Get all positions
        positions = trading_client.get_all_positions()
        
        # Format positions with safe attribute access
        formatted_positions = []
        total_unrealized_pl = 0
        
        for pos in positions:
            # Use getattr with defaults for safe access
            unrealized_pl = float(getattr(pos, 'unrealized_pl', 0) or 0)
            total_unrealized_pl += unrealized_pl
            
            formatted_positions.append({
                "symbol": getattr(pos, 'symbol', ''),
                "qty": float(getattr(pos, 'qty', 0) or 0),
                "market_value": float(getattr(pos, 'market_value', 0) or 0),
                "cost_basis": float(getattr(pos, 'cost_basis', 0) or 0),
                "unrealized_pl": unrealized_pl,
                "unrealized_plpc": float(getattr(pos, 'unrealized_plpc', 0) or 0),
                "current_price": float(getattr(pos, 'current_price', 0) or 0),
                "avg_entry_price": float(getattr(pos, 'avg_entry_price', 0) or 0)
            })
        
        total_equity = float(account.equity)
        cash = float(account.cash)
        
        return {
            "success": True,
            "total_equity": total_equity,
            "cash": cash,
            "buying_power": float(account.buying_power),
            "positions": formatted_positions,
            "total_positions": len(formatted_positions),
            "total_unrealized_pl": total_unrealized_pl,
            "cash_percentage": (cash / total_equity * 100) if total_equity > 0 else 0,
            "invested_percentage": ((total_equity - cash) / total_equity * 100) if total_equity > 0 else 0
        }
        
    except Exception as e:
        print(f"Portfolio error: {str(e)}")
        # Return default values instead of raising exception
        return {
            "success": False,
            "error": str(e),
            "total_equity": 0,
            "cash": 0,
            "buying_power": 0,
            "positions": [],
            "total_positions": 0,
            "total_unrealized_pl": 0,
            "cash_percentage": 0,
            "invested_percentage": 0
        }

@router.get("/portfolio/positions")
async def get_positions():
    """Get all portfolio positions"""
    try:
        return assistant.alpaca.get_portfolio_positions()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/account", response_model=AccountResponse)
async def get_account():
    """Get account information"""
    try:
        data = assistant.alpaca.get_account()
        return AccountResponse(
            account_number=data.get("account_number", ""),
            status=data.get("status", ""),
            currency=data.get("currency", "USD"),
            buying_power=data.get("buying_power", 0),
            cash=data.get("cash", 0),
            portfolio_value=data.get("portfolio_value", 0),
            equity=data.get("equity", 0),
            last_equity=data.get("last_equity", 0),
            multiplier=data.get("multiplier", "1"),
            success=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ========== Market Data Endpoints ==========

@router.get("/stock/{symbol}/snapshot", response_model=StockSnapshot)
async def get_stock_snapshot(symbol: str):
    """Get market snapshot for a specific stock"""
    try:
        data = assistant.alpaca.get_market_snapshot(symbol.upper())
        
        if not data.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock {symbol} not found"
            )
        
        return StockSnapshot(
            symbol=data["symbol"],
            current_price=data["current_price"],
            daily_open=data["daily_bar"]["open"],
            daily_high=data["daily_bar"]["high"],
            daily_low=data["daily_bar"]["low"],
            daily_close=data["daily_bar"]["close"],
            previous_close=data["prev_daily_bar"]["close"],
            volume=data["daily_bar"]["volume"],
            change=data["change"],
            change_percent=data["change_percent"],
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/stock/{symbol}/quote")
async def get_stock_quote(symbol: str):
    """Get latest quote for a stock"""
    try:
        return assistant.alpaca.get_latest_quote(symbol.upper())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/stock/{symbol}/stats", response_model=HistoricalStats)
async def get_historical_stats(symbol: str, days: int = 30):
    """Get historical statistics for a stock"""
    try:
        data = assistant.alpaca.get_historical_stats(symbol.upper(), days)
        return HistoricalStats(
            symbol=data["symbol"],
            period_days=data["period_days"],
            average_close=data["average_close"],
            period_high=data["period_high"],
            period_low=data["period_low"],
            average_volume=data["average_volume"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            success=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/stock/compare", response_model=StockComparison)
async def compare_stocks(symbols: list[str], days: int = 30):
    """Compare multiple stocks"""
    try:
        data = assistant.alpaca.compare_stocks(symbols, days)
        return StockComparison(
            symbols=symbols,
            period_days=days,
            data=data,
            success=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ========== Trading Endpoints ==========

@router.post("/order/market", response_model=OrderResponse)
async def place_market_order(order: MarketOrderRequest):
    """Place a market order"""
    try:
        result = assistant.trading.place_market_order(
            symbol=order.symbol.upper(),
            qty=order.qty,
            side=order.side
        )
        return OrderResponse(**result)
    except Exception as e:
        return OrderResponse(
            success=False,
            error=str(e)
        )

@router.post("/order/limit", response_model=OrderResponse)
async def place_limit_order(order: LimitOrderRequest):
    """Place a limit order"""
    try:
        result = assistant.trading.place_limit_order(
            symbol=order.symbol.upper(),
            qty=order.qty,
            side=order.side,
            limit_price=order.limit_price
        )
        return OrderResponse(**result)
    except Exception as e:
        return OrderResponse(
            success=False,
            error=str(e)
        )

@router.post("/order/stop", response_model=OrderResponse)
async def place_stop_order(order: StopOrderRequest):
    """Place a stop order"""
    try:
        result = assistant.trading.place_stop_order(
            symbol=order.symbol.upper(),
            qty=order.qty,
            side=order.side,
            stop_price=order.stop_price
        )
        return OrderResponse(**result)
    except Exception as e:
        return OrderResponse(
            success=False,
            error=str(e)
        )

@router.get("/orders", response_model=OrderListResponse)
async def get_open_orders():
    """Get all open orders"""
    try:
        result = assistant.trading.get_open_orders()
        return OrderListResponse(
            orders=result.get("orders", []),
            count=result.get("count", 0),
            success=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/orders/history")
async def get_order_history(limit: int = 10, status: str = "all"):
    """Get order history"""
    try:
        return assistant.trading.get_order_history(limit=limit, status=status)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/order/{order_id}")
async def cancel_order(order_id: str):
    """Cancel a specific order"""
    try:
        result = assistant.trading.cancel_order(order_id)
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to cancel order")
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/orders/all")
async def cancel_all_orders():
    """Cancel all open orders"""
    try:
        return assistant.trading.cancel_all_orders()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/portfolio/history")
async def get_portfolio_history(period: str = "1M", timeframe: str = "1D"):
    """
    Get portfolio value history for charting
    period: 1D, 1W, 1M, 3M, 6M, 1Y, ALL
    timeframe: 1Min, 5Min, 15Min, 1H, 1D
    """
    try:
        from alpaca.trading.requests import GetPortfolioHistoryRequest
        
        # Use the existing trading client from settings
        trading_client = TradingClient(
            settings.ALPACA_API_KEY,
            settings.ALPACA_SECRET_KEY,
            paper=True
        )
        
        # Create request with correct parameters
        history_request = GetPortfolioHistoryRequest(
            period=period,
            timeframe=timeframe
        )
        
        # Get portfolio history from Alpaca
        history = trading_client.get_portfolio_history(history_request)
        
        # Format data for frontend chart
        data_points = []
        if history.timestamp:
            for i, ts in enumerate(history.timestamp):
                data_points.append({
                    "timestamp": ts,
                    "equity": history.equity[i] if history.equity else 0,
                    "profit_loss": history.profit_loss[i] if history.profit_loss else 0,
                    "profit_loss_pct": history.profit_loss_pct[i] if history.profit_loss_pct else 0
                })
        
        # Calculate CORRECT P/L from first to last data point
        if data_points and len(data_points) > 1:
            start_equity = data_points[0]["equity"]
            end_equity = data_points[-1]["equity"]
            total_pl = end_equity - start_equity
            total_pl_pct = (total_pl / start_equity) if start_equity > 0 else 0
        elif data_points:
            # Only one data point - use Alpaca's provided values
            total_pl = data_points[-1]["profit_loss"]
            total_pl_pct = data_points[-1]["profit_loss_pct"]
        else:
            total_pl = 0
            total_pl_pct = 0
        
        return {
            "success": True,
            "period": period,
            "timeframe": timeframe,
            "data": data_points,
            "base_value": history.base_value if history.base_value else 0,
            "total_pl": total_pl,
            "total_pl_pct": total_pl_pct
        }
        
    except Exception as e:
        print(f"Portfolio history error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "data": []
        }

# ========== News Endpoints ==========

@router.post("/news", response_model=NewsResponse)
async def get_news(request: NewsRequest):
    """Get recent news for a stock"""
    try:
        data = assistant.news.get_recent_news(
            symbol=request.symbol.upper(),
            days=request.days,
            limit=request.limit
        )
        
        return NewsResponse(
            symbol=request.symbol.upper(),
            articles=data.get("articles", []),
            count=data.get("count", 0),
            success=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )