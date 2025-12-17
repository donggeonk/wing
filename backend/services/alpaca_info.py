from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import (
    StockBarsRequest,
    StockLatestQuoteRequest,
    StockLatestTradeRequest,
    StockLatestBarRequest,
    StockSnapshotRequest,
    NewsRequest
)
from alpaca.data.timeframe import TimeFrame
from alpaca.data import NewsClient
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv
import json

class AlpacaClient:
    def __init__(self, api_key, api_secret, base_url=None):
        # base_url parameter kept for compatibility but not used in alpaca-py
        self.client = TradingClient(api_key, api_secret, paper=True)
        self.data_client = StockHistoricalDataClient(api_key, api_secret)
        self.news_client = NewsClient(api_key, api_secret)
    
    # Get current portfolio positions
    def get_portfolio_positions(self):
        positions = self.client.get_all_positions()
        return [
            {
                "symbol": p.symbol,
                "qty": float(p.qty),
                "market_value": float(p.market_value),
                "unrealized_pl": float(p.unrealized_pl),
            }
            for p in positions
        ]
    
    # Get portfolio summary for LLM context
    def get_portfolio_summary(self):
        """
        Get comprehensive portfolio summary for LLM context
        Combines account info, positions, and performance metrics
        """
        try:
            account = self.get_account()
            positions = self.get_portfolio_positions()
            
            # Calculate portfolio metrics
            total_pl = sum(pos['unrealized_pl'] for pos in positions)
            total_value = account['equity']
            cash_percentage = (account['cash'] / total_value * 100) if total_value > 0 else 0
            
            return {
                "account": account,
                "positions": positions,
                "summary": {
                    "total_positions": len(positions),
                    "total_unrealized_pl": total_pl,
                    "cash_percentage": cash_percentage,
                    "invested_percentage": 100 - cash_percentage
                }
            }
        except Exception as e:
            return {"error": str(e)}
        
    # Compare multiple stocks' performance
    def compare_stocks(self, symbols, days=30):
        """
        Compare multiple stocks' performance over a period
        Useful for LLM to answer "Should I buy AAPL or MSFT?"
        """
        try:
            comparison = []
            
            for symbol in symbols:
                stats = self.get_historical_stats(symbol, days)
                snapshot = self.get_market_snapshot(symbol)
                
                if "error" not in stats and "error" not in snapshot:
                    # Calculate percentage change over period
                    period_change = ((stats['avg_close'] - stats['low']) / stats['low']) * 100
                    
                    comparison.append({
                        "symbol": symbol,
                        "current_price": snapshot['daily_bar']['close'],
                        "daily_change_percent": snapshot['daily_performance']['change_percent'],
                        "period_avg_close": stats['avg_close'],
                        "period_high": stats['high'],
                        "period_low": stats['low'],
                        "period_change_percent": period_change,
                        "avg_volume": stats['avg_volume']
                    })
            
            return {
                "symbols": symbols,
                "period_days": days,
                "comparison": comparison
            }
        except Exception as e:
            return {"error": str(e)}

    # Get account information
    def get_account(self):
        acct = self.client.get_account()
        return {
            "equity": float(acct.equity),
            "cash": float(acct.cash),
            "buying_power": float(acct.buying_power),
        }
    
    # Get historical stock data (OHLCV bars) - complete historical data for charts, detailed analysis
    def get_stock_bars(self, symbol, start, end, timeframe):
        timeframe_map = {
            '1Min': TimeFrame.Minute,
            '5Min': TimeFrame(5, "Min"),
            '15Min': TimeFrame(15, "Min"),
            '1Hour': TimeFrame.Hour,
            '1Day': TimeFrame.Day
        }

        request_params = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=timeframe_map.get(timeframe, TimeFrame.Day),
            start=start,
            end=end
        )

        bars = self.data_client.get_stock_bars(request_params)
        return bars.df
    
    # Get latest bar (current OHLCV)
    def get_latest_bar(self, symbol):
        """
        Get the most recent OHLCV bar for a stock
        Returns: dict with open, high, low, close, volume, vwap, timestamp
        """
        try:
            bar_request = StockLatestBarRequest(symbol_or_symbols=[symbol])
            latest_bar = self.data_client.get_stock_latest_bar(bar_request)
            
            if symbol in latest_bar:
                bar = latest_bar[symbol]
                return {
                    "symbol": symbol,
                    "open": float(bar.open),
                    "high": float(bar.high),
                    "low": float(bar.low),
                    "close": float(bar.close),
                    "volume": float(bar.volume),
                    "vwap": float(bar.vwap),
                    "timestamp": bar.timestamp.isoformat()
                }
        except Exception as e:
            return {"error": str(e)}
    
    # Get latest quote (bid/ask prices)
    def get_latest_quote(self, symbol):
        """
        Get the latest bid/ask quote for a stock
        Returns: dict with ask_price, ask_size, bid_price, bid_size, spread, timestamp
        """
        try:
            quote_request = StockLatestQuoteRequest(symbol_or_symbols=[symbol])
            latest_quote = self.data_client.get_stock_latest_quote(quote_request)
            
            if symbol in latest_quote:
                quote = latest_quote[symbol]
                return {
                    "symbol": symbol,
                    "ask_price": float(quote.ask_price),
                    "ask_size": float(quote.ask_size),
                    "bid_price": float(quote.bid_price),
                    "bid_size": float(quote.bid_size),
                    "spread": float(quote.ask_price - quote.bid_price),
                    "timestamp": quote.timestamp.isoformat()
                }
        except Exception as e:
            return {"error": str(e)}
    
    # Get latest trade execution
    def get_latest_trade(self, symbol):
        """
        Get the latest trade execution for a stock
        Returns: dict with price, size, exchange, timestamp
        """
        try:
            trade_request = StockLatestTradeRequest(symbol_or_symbols=[symbol])
            latest_trade = self.data_client.get_stock_latest_trade(trade_request)
            
            if symbol in latest_trade:
                trade = latest_trade[symbol]
                return {
                    "symbol": symbol,
                    "price": float(trade.price),
                    "size": float(trade.size),
                    "exchange": trade.exchange,
                    "timestamp": trade.timestamp.isoformat()
                }
        except Exception as e:
            return {"error": str(e)}
    
    # Get market snapshot (complete current state)
    def get_market_snapshot(self, symbol):
        """
        Get complete market snapshot including daily bar, previous day, and intraday data
        Returns: dict with daily_bar, previous_daily_bar, minute_bar, daily_performance
        """
        try:
            snapshot_request = StockSnapshotRequest(symbol_or_symbols=[symbol])
            snapshot = self.data_client.get_stock_snapshot(snapshot_request)
            
            if symbol in snapshot:
                snap = snapshot[symbol]
                
                # Calculate daily performance
                daily_change = snap.daily_bar.close - snap.previous_daily_bar.close
                daily_change_pct = (daily_change / snap.previous_daily_bar.close) * 100
                
                return {
                    "symbol": symbol,
                    "latest_trade": {
                        "price": float(snap.latest_trade.price),
                        "size": float(snap.latest_trade.size),
                        "timestamp": snap.latest_trade.timestamp.isoformat()
                    },
                    "latest_quote": {
                        "ask_price": float(snap.latest_quote.ask_price),
                        "bid_price": float(snap.latest_quote.bid_price),
                        "ask_size": float(snap.latest_quote.ask_size),
                        "bid_size": float(snap.latest_quote.bid_size)
                    },
                    "minute_bar": {
                        "open": float(snap.minute_bar.open),
                        "high": float(snap.minute_bar.high),
                        "low": float(snap.minute_bar.low),
                        "close": float(snap.minute_bar.close),
                        "volume": float(snap.minute_bar.volume),
                        "timestamp": snap.minute_bar.timestamp.isoformat()
                    },
                    "daily_bar": {
                        "open": float(snap.daily_bar.open),
                        "high": float(snap.daily_bar.high),
                        "low": float(snap.daily_bar.low),
                        "close": float(snap.daily_bar.close),
                        "volume": float(snap.daily_bar.volume),
                        "vwap": float(snap.daily_bar.vwap),
                        "timestamp": snap.daily_bar.timestamp.isoformat()
                    },
                    "previous_daily_bar": {
                        "close": float(snap.previous_daily_bar.close),
                        "volume": float(snap.previous_daily_bar.volume)
                    },
                    "daily_performance": {
                        "change": float(daily_change),
                        "change_percent": float(daily_change_pct)
                    }
                }
        except Exception as e:
            return {"error": str(e)}
    
    # Get historical statistics summary for quick insights
    def get_historical_stats(self, symbol, days=30):
        """
        Get historical statistics for a stock over a period
        Returns: dict with avg_close, high, low, avg_volume, total_volume, days
        """
        try:
            bars_request = StockBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=TimeFrame.Day,
                start=datetime.now() - timedelta(days=days),
                end=datetime.now()
            )
            bars = self.data_client.get_stock_bars(bars_request)
            df = bars.df
            
            # Reset index if multi-index (symbol, timestamp)
            if isinstance(df.index, pd.MultiIndex):
                df = df.reset_index(level=0, drop=True)
            
            if len(df) > 0:
                return {
                    "symbol": symbol,
                    "period_days": days,
                    "actual_days": len(df),
                    "avg_close": float(df['close'].mean()),
                    "high": float(df['close'].max()),
                    "low": float(df['close'].min()),
                    "avg_volume": float(df['volume'].mean()),
                    "total_volume": float(df['volume'].sum()),
                    "start_date": str(df.index[0]),
                    "end_date": str(df.index[-1])
                }
            else:
                return {"error": "No historical data available"}
        except Exception as e:
            return {"error": str(e)}

# # Test function
# if __name__ == '__main__':
#     load_dotenv()
#     print("TESTING ALPACA CLIENT")
     
#     # Initialize client
#     client = AlpacaClient(
#         api_key=os.getenv('ALPACA_API_KEY'),
#         api_secret=os.getenv('ALPACA_SECRET_KEY'),
#         base_url='https://paper-api.alpaca.markets'
#     )
   
#     # Test account
#     print("\nTEST 1: Account Information")
#     account = client.get_account()
#     print(f"Equity: ${account['equity']:,.2f}")
#     print(f"Cash: ${account['cash']:,.2f}")
#     print(f"Buying Power: ${account['buying_power']:,.2f}")
    
#     # Test positions
#     print("\nTEST 2: Portfolio Positions")
#     positions = client.get_portfolio_positions()
#     if positions:
#         for pos in positions:
#             print(f"Symbol: {pos['symbol']}, Qty: {pos['qty']}, Value: ${pos['market_value']:,.2f}")
#     else:
#         print("No positions found (empty portfolio)\n")
    
#     # Test stock data functions
#     symbol = 'AAPL'
#     print(f"\nTEST 3: Latest Bar for {symbol}")

#     # Latest Quote
#     print("1. Latest Quote:")
#     quote = client.get_latest_quote(symbol)
#     if "error" not in quote:
#         print(f"   Ask: ${quote['ask_price']:.2f}, Bid: ${quote['bid_price']:.2f}")
#         print(f"   Spread: ${quote['spread']:.2f}")
#     else:
#         print(f"   Error: {quote['error']}")
    
#     # Latest Trade
#     print("\n2. Latest Trade:")
#     trade = client.get_latest_trade(symbol)
#     if "error" not in trade:
#         print(f"   Price: ${trade['price']:.2f}, Size: {trade['size']}")
#     else:
#         print(f"   Error: {trade['error']}")
    
#     # Latest Bar
#     print("\n3. Latest Bar:")
#     bar = client.get_latest_bar(symbol)
#     if "error" not in bar:
#         print(f"   Open: ${bar['open']:.2f}, Close: ${bar['close']:.2f}")
#         print(f"   High: ${bar['high']:.2f}, Low: ${bar['low']:.2f}")
#         print(f"   Volume: {bar['volume']:,.0f}")
#     else:
#         print(f"   Error: {bar['error']}")
    
#     # Current Market Snapshot
#     print("\n4. Market Snapshot:")
#     snapshot = client.get_market_snapshot(symbol)
#     if "error" not in snapshot:
#         print(f"   Daily Change: ${snapshot['daily_performance']['change']:.2f}")
#         print(f"   Daily Change %: {snapshot['daily_performance']['change_percent']:+.2f}%")
#     else:
#         print(f"   Error: {snapshot['error']}")
    
#     # Historical Stats
#     print("\n5. Historical Statistics (30 days):")
#     stats = client.get_historical_stats(symbol, days=30)
#     if "error" not in stats:
#         print(f"   Average Close: ${stats['avg_close']:.2f}")
#         print(f"   High: ${stats['high']:.2f}, Low: ${stats['low']:.2f}")
#         print(f"   Average Volume: {stats['avg_volume']:,.0f}")
#     else:
#         print(f"   Error: {stats['error']}")