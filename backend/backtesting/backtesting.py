import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from logic import buy, sell
from dotenv import load_dotenv

load_dotenv()

class Backtester:
    def __init__(self, api_key, secret_key, base_url):
        self.api = tradeapi.REST(api_key, secret_key, base_url=base_url)
        self.symbol = 'ETH/USD'
        self.rsi_window = 14
        self.ma_window = 14
        
    def calculate_rsi(self, prices, window=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def get_historical_data(self, start_date, end_date):
        """Get historical ETH data"""
        try:
            print(f"Fetching {self.symbol} data from {start_date} to {end_date}...")
            
            bars = self.api.get_crypto_bars(
                self.symbol,
                '1Min',  # 1-minute bars
                start=start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                end=end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            ).df
            
            print(f"Retrieved {len(bars)} bars")
            return bars
            
        except Exception as e:
            print(f"Error getting historical data: {e}")
            return None
    
    def run_backtest(self, start_date, end_date, initial_capital=100):
        """Run backtest on historical data"""
        # Get historical data
        bars = self.get_historical_data(start_date, end_date)
        
        if bars is None or len(bars) == 0:
            print("No data retrieved!")
            return None, None
        
        # Calculate indicators
        print("Calculating RSI and RSI MA...")
        bars['rsi'] = self.calculate_rsi(bars['close'], self.rsi_window)
        bars['rsi_ma'] = bars['rsi'].rolling(window=self.ma_window).mean()
        
        # Remove NaN values
        bars = bars.dropna()
        
        print(f"Starting backtest with ${initial_capital:.2f}")
        print("=" * 80)
        
        # Trading variables
        cash = initial_capital
        position = 0  # Amount of ETH held
        position_value = 0
        in_position = False
        trades = []
        
        # Iterate through each bar
        for i in range(1, len(bars)):
            current_bar = bars.iloc[i]
            prev_bar = bars.iloc[i-1]
            
            rsi_now = current_bar['rsi']
            rsi_prev = prev_bar['rsi']
            rsi_ma_now = current_bar['rsi_ma']
            current_price = current_bar['close']
            prev_price = prev_bar['close']
            timestamp = current_bar.name
            delta_rsi = rsi_now - rsi_prev
            delta_price = current_price - prev_price
            
            # Check buy signal - now passes current_price and prev_price
            if not in_position and buy(rsi_prev, rsi_now, rsi_ma_now, current_price, prev_price):
                # Buy with all available cash
                position = cash / current_price
                position_value = cash
                print(f"\n[BUY] {timestamp}")
                print(f"  Price: ${current_price:.2f} | Price Delta: ${delta_price:.2f}")
                print(f"  RSI: {rsi_now:.2f} | RSI MA: {rsi_ma_now:.2f} | RSI Delta: {delta_rsi:.2f}")
                print(f"  Spent: ${cash:.2f}")
                print(f"  ETH bought: {position:.6f}")
                
                trades.append({
                    'timestamp': timestamp,
                    'action': 'BUY',
                    'price': current_price,
                    'amount': position,
                    'value': cash,
                    'rsi': rsi_now,
                    'rsi_ma': rsi_ma_now,
                    'delta_rsi': delta_rsi,
                    'delta_price': delta_price
                })
                
                cash = 0
                in_position = True
            
            # Check sell signal
            elif in_position and sell(rsi_prev, rsi_now, rsi_ma_now, current_price, prev_price):
                # Sell all position
                cash = position * current_price
                profit = cash - position_value
                profit_pct = (profit / position_value) * 100
                
                print(f"\n[SELL] {timestamp}")
                print(f"  Price: ${current_price:.2f} | Price Delta: ${delta_price:.2f}")
                print(f"  RSI: {rsi_now:.2f} | RSI MA: {rsi_ma_now:.2f} | RSI Delta: {delta_rsi:.2f}")
                print(f"  ETH sold: {position:.6f}")
                print(f"  Received: ${cash:.2f}")
                print(f"  Profit/Loss: ${profit:.2f} ({profit_pct:+.2f}%)")
                
                trades.append({
                    'timestamp': timestamp,
                    'action': 'SELL',
                    'price': current_price,
                    'amount': position,
                    'value': cash,
                    'rsi': rsi_now,
                    'rsi_ma': rsi_ma_now,
                    'delta_rsi': delta_rsi,
                    'delta_price': delta_price,
                    'profit': profit,
                    'profit_pct': profit_pct
                })
                
                position = 0
                position_value = 0
                in_position = False
        
        # Final portfolio value
        final_value = cash + (position * bars.iloc[-1]['close'] if in_position else 0)
        total_return = final_value - initial_capital
        total_return_pct = (total_return / initial_capital) * 100
        
        print("\n" + "=" * 80)
        print("BACKTEST SUMMARY")
        print("=" * 80)
        print(f"Period: {start_date.date()} to {end_date.date()}")
        print(f"Initial Capital: ${initial_capital:.2f}")
        print(f"Final Value: ${final_value:.2f}")
        print(f"Total Return: ${total_return:.2f} ({total_return_pct:+.2f}%)")
        print(f"Number of Trades: {len(trades)}")
        
        if in_position:
            print(f"\nWarning: Still holding {position:.6f} ETH (worth ${position * bars.iloc[-1]['close']:.2f})")
        
        return trades, final_value

if __name__ == "__main__":
    # Load credentials
    API_KEY = os.getenv('ALPACA_API_KEY')
    SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
    BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    if not API_KEY or not SECRET_KEY:
        raise ValueError("Please set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env file")
    
    # start_date = datetime(2024, 12, 8, 0, 0, 0)
    # end_date = datetime(2025, 4, 8, 18, 0, 0)

    start_date = datetime(2025, 4, 21, 0, 0, 0)
    end_date = datetime(2025, 8, 13, 0, 0, 0)
    
    # Initial seed money
    seed_money = 1000
    
    # Run backtest
    backtester = Backtester(API_KEY, SECRET_KEY, BASE_URL)
    trades, final_value = backtester.run_backtest(start_date, end_date, seed_money)
    
    if trades is None:
        print("Backtest failed!")