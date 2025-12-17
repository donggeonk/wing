from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from datetime import datetime
import os
from dotenv import load_dotenv

class AlpacaTrading:
    """
    Alpaca Trading Execution Client
    Handles all dynamic trading operations (placing, canceling, managing orders)
    
    Separated from AlpacaClient for:
    - Clear separation of concerns (read vs write operations)
    - Enhanced security (can restrict access to trading functions)
    - Better error handling for execution-specific issues
    """
    
    def __init__(self, api_key, api_secret, paper=True):
        """
        Initialize trading client
        
        Args:
            api_key: Alpaca API key
            api_secret: Alpaca API secret
            paper: True for paper trading, False for live trading (default: True)
        """
        self.client = TradingClient(api_key, api_secret, paper=paper)
        self.paper_mode = paper
    
    def place_market_order(self, symbol, qty, side):
        """
        Place a market order (buy/sell at current market price)
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            qty: Quantity of shares (can be fractional)
            side: 'buy' or 'sell'
        
        Returns:
            dict with order details or error
        """
        try:
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )
            
            order = self.client.submit_order(order_data)
            
            return {
                "success": True,
                "order_id": str(order.id),
                "symbol": order.symbol,
                "qty": float(order.qty),
                "side": order.side.value,
                "type": order.type.value,
                "status": order.status.value,
                "submitted_at": order.submitted_at.isoformat(),
                "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None,
                "paper_trading": self.paper_mode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol,
                "qty": qty,
                "side": side
            }
    
    def place_limit_order(self, symbol, qty, side, limit_price):
        """
        Place a limit order (buy/sell at specific price or better)
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            qty: Quantity of shares
            side: 'buy' or 'sell'
            limit_price: Maximum price to pay (buy) or minimum price to accept (sell)
        
        Returns:
            dict with order details or error
        """
        try:
            order_data = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
                limit_price=limit_price
            )
            
            order = self.client.submit_order(order_data)
            
            return {
                "success": True,
                "order_id": str(order.id),
                "symbol": order.symbol,
                "qty": float(order.qty),
                "side": order.side.value,
                "type": order.type.value,
                "limit_price": float(order.limit_price),
                "status": order.status.value,
                "submitted_at": order.submitted_at.isoformat(),
                "paper_trading": self.paper_mode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "limit_price": limit_price
            }
    
    def place_stop_order(self, symbol, qty, side, stop_price):
        """
        Place a stop order (triggers market order when price reaches stop_price)
        Useful for stop-loss or breakout strategies
        
        Args:
            symbol: Stock symbol
            qty: Quantity of shares
            side: 'buy' or 'sell'
            stop_price: Price that triggers the order
        
        Returns:
            dict with order details or error
        """
        try:
            order_data = StopOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
                stop_price=stop_price
            )
            
            order = self.client.submit_order(order_data)
            
            return {
                "success": True,
                "order_id": str(order.id),
                "symbol": order.symbol,
                "qty": float(order.qty),
                "side": order.side.value,
                "type": order.type.value,
                "stop_price": float(order.stop_price),
                "status": order.status.value,
                "submitted_at": order.submitted_at.isoformat(),
                "paper_trading": self.paper_mode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "stop_price": stop_price
            }
    
    def get_open_orders(self):
        """
        Get all open (pending) orders
        
        Returns:
            list of open orders or error dict
        """
        try:
            orders = self.client.get_orders(status='open')
            
            return {
                "success": True,
                "total_orders": len(orders),
                "orders": [
                    {
                        "order_id": str(order.id),
                        "symbol": order.symbol,
                        "qty": float(order.qty),
                        "filled_qty": float(order.filled_qty),
                        "side": order.side.value,
                        "type": order.type.value,
                        "status": order.status.value,
                        "limit_price": float(order.limit_price) if order.limit_price else None,
                        "stop_price": float(order.stop_price) if order.stop_price else None,
                        "submitted_at": order.submitted_at.isoformat(),
                        "time_in_force": order.time_in_force.value
                    }
                    for order in orders
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def cancel_order(self, order_id):
        """
        Cancel a pending order
        
        Args:
            order_id: Order ID to cancel
        
        Returns:
            dict with success status
        """
        try:
            self.client.cancel_order_by_id(order_id)
            return {
                "success": True,
                "message": f"Order {order_id} cancelled successfully",
                "order_id": order_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "order_id": order_id
            }
    
    def cancel_all_orders(self):
        """
        Cancel all open orders
        
        Returns:
            dict with success status and count
        """
        try:
            cancelled_orders = self.client.cancel_orders()
            return {
                "success": True,
                "message": f"Cancelled {len(cancelled_orders)} orders",
                "cancelled_count": len(cancelled_orders),
                "order_ids": [str(order.id) for order in cancelled_orders]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_order_history(self, limit=10, status='all'):
        """
        Get recent order history
        
        Args:
            limit: Maximum number of orders to return (default: 10)
            status: Filter by status - 'all', 'open', 'closed', 'filled', 'cancelled'
        
        Returns:
            list of orders with details
        """
        try:
            orders = self.client.get_orders(status=status, limit=limit)
            
            return {
                "success": True,
                "total_orders": len(orders),
                "filter_status": status,
                "orders": [
                    {
                        "order_id": str(order.id),
                        "symbol": order.symbol,
                        "qty": float(order.qty),
                        "filled_qty": float(order.filled_qty),
                        "side": order.side.value,
                        "type": order.type.value,
                        "status": order.status.value,
                        "limit_price": float(order.limit_price) if order.limit_price else None,
                        "stop_price": float(order.stop_price) if order.stop_price else None,
                        "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None,
                        "submitted_at": order.submitted_at.isoformat(),
                        "filled_at": order.filled_at.isoformat() if order.filled_at else None,
                        "cancelled_at": order.cancelled_at.isoformat() if order.cancelled_at else None,
                        "time_in_force": order.time_in_force.value
                    }
                    for order in orders
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_order_by_id(self, order_id):
        """
        Get details of a specific order
        
        Args:
            order_id: Order ID
        
        Returns:
            dict with order details
        """
        try:
            order = self.client.get_order_by_id(order_id)
            
            return {
                "success": True,
                "order_id": str(order.id),
                "symbol": order.symbol,
                "qty": float(order.qty),
                "filled_qty": float(order.filled_qty),
                "side": order.side.value,
                "type": order.type.value,
                "status": order.status.value,
                "limit_price": float(order.limit_price) if order.limit_price else None,
                "stop_price": float(order.stop_price) if order.stop_price else None,
                "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None,
                "submitted_at": order.submitted_at.isoformat(),
                "filled_at": order.filled_at.isoformat() if order.filled_at else None,
                "cancelled_at": order.cancelled_at.isoformat() if order.cancelled_at else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "order_id": order_id
            }


# Test function
if __name__ == '__main__':
    load_dotenv()
    print("\n" + "="*80)
    print("TESTING ALPACA TRADING CLIENT (PAPER TRADING)")
    print("="*80 + "\n")
    
    # Initialize trading client
    trading = AlpacaTrading(
        api_key=os.getenv('ALPACA_API_KEY'),
        api_secret=os.getenv('ALPACA_SECRET_KEY'),
        paper=True
    )
    
    # Test 1: Get open orders
    print("TEST 1: Get Open Orders")
    print("-" * 80)
    open_orders = trading.get_open_orders()
    if open_orders['success']:
        print(f"Total open orders: {open_orders['total_orders']}")
        if open_orders['orders']:
            for order in open_orders['orders']:
                print(f"  {order['symbol']}: {order['side']} {order['qty']} @ {order['type']}")
        else:
            print("  No open orders")
    else:
        print(f"  Error: {open_orders['error']}")
    
    # Test 2: Get order history
    print("\n\nTEST 2: Order History (Last 5 orders)")
    print("-" * 80)
    history = trading.get_order_history(limit=5, status='all')
    if history['success']:
        print(f"Total orders: {history['total_orders']}")
        for order in history['orders']:
            print(f"  {order['symbol']}: {order['side']} {order['qty']} - Status: {order['status']}")
            if order['filled_avg_price']:
                print(f"    Filled @ ${order['filled_avg_price']:.2f}")
    else:
        print(f"  Error: {history['error']}")
    
    # Test 3: Place a test market order (very small amount)
    print("\n\nTEST 3: Place Market Order (0.01 shares of AAPL)")
    print("-" * 80)
    print("⚠️  This is PAPER TRADING - no real money involved")
    
    market_order = trading.place_market_order(
        symbol='AAPL',
        qty=0.01,
        side='buy'
    )
    
    if market_order['success']:
        print(f"✅ Order placed successfully!")
        print(f"  Order ID: {market_order['order_id']}")
        print(f"  Symbol: {market_order['symbol']}")
        print(f"  Qty: {market_order['qty']}")
        print(f"  Side: {market_order['side']}")
        print(f"  Status: {market_order['status']}")
    else:
        print(f"❌ Order failed: {market_order['error']}")
    
    # Test 4: Place a limit order
    print("\n\nTEST 4: Place Limit Order (0.01 shares of TSLA @ $200)")
    print("-" * 80)
    
    limit_order = trading.place_limit_order(
        symbol='TSLA',
        qty=0.01,
        side='buy',
        limit_price=200.00
    )
    
    if limit_order['success']:
        print(f"✅ Limit order placed!")
        print(f"  Order ID: {limit_order['order_id']}")
        print(f"  Limit Price: ${limit_order['limit_price']:.2f}")
        print(f"  Status: {limit_order['status']}")
        
        # Test 5: Cancel the limit order we just placed
        print("\n\nTEST 5: Cancel the limit order")
        print("-" * 80)
        
        cancel_result = trading.cancel_order(limit_order['order_id'])
        if cancel_result['success']:
            print(f"✅ {cancel_result['message']}")
        else:
            print(f"❌ Cancel failed: {cancel_result['error']}")
    else:
        print(f"❌ Limit order failed: {limit_order['error']}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80 + "\n")