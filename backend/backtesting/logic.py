# version 1
def buy(rsi_prev, rsi_now, rsi_ma, current_price, prev_price):
    delta_rsi = rsi_now - rsi_prev
    delta_price = current_price - prev_price
    if rsi_now > rsi_ma and delta_price > 0:
        return True
    return False

def sell(rsi_prev, rsi_now, rsi_ma, current_price, prev_price):
    delta_rsi = rsi_now - rsi_prev
    delta_price = current_price - prev_price
    if rsi_now < rsi_ma and delta_price < 0:
        return True
    return False

# # version 2
# import numpy as np

# # ============================================================================
# # GEOMETRIC BROWNIAN MOTION SIMULATION
# # ============================================================================

# def simulate_gbm(current_price, historical_prices, n_simulations=500, n_steps=10, dt=1/252):
#     """
#     Simulate future prices using Geometric Brownian Motion with Euler-Maruyama method
    
#     Args:
#         current_price: Current stock/crypto price
#         historical_prices: Array of recent historical prices (for estimating drift and volatility)
#         n_simulations: Number of Monte Carlo simulations (default: 500)
#         n_steps: Number of time steps to simulate ahead (default: 10)
#         dt: Time step size (default: 1/252 for daily, use 1/(252*390) for minute data)
    
#     Returns:
#         Array of simulated final prices, or None if insufficient data
#     """
#     if len(historical_prices) < 20:
#         return None
    
#     # Calculate returns from historical prices
#     returns = np.diff(historical_prices) / historical_prices[:-1]
    
#     # Estimate drift (mu) and volatility (sigma) from historical data
#     mu = np.mean(returns)
#     sigma = np.std(returns)
    
#     # Cap sigma to prevent extreme predictions (crypto can be very volatile)
#     sigma = min(sigma, 0.5)  # Cap at 50% volatility
    
#     # Run Monte Carlo simulations
#     simulated_prices = np.zeros(n_simulations)
    
#     for sim in range(n_simulations):
#         price = current_price
        
#         # Euler-Maruyama discretization: dS = mu*S*dt + sigma*S*dW
#         for step in range(n_steps):
#             # Generate random shock from standard normal distribution
#             dW = np.random.normal(0, np.sqrt(dt))
            
#             # Calculate price change
#             dS = mu * price * dt + sigma * price * dW
            
#             # Update price (ensure it doesn't go negative)
#             price = max(price + dS, 0.01)
        
#         simulated_prices[sim] = price
    
#     return simulated_prices


# # ============================================================================
# # HYBRID BUY LOGIC: GBM + RSI + MOMENTUM
# # ============================================================================

# def buy(rsi_prev, rsi_now, rsi_ma, current_price, prev_price, historical_prices=None):
#     """
#     Hybrid buy logic combining:
#     - GBM prediction for strategic direction
#     - RSI for momentum confirmation
#     - Price action for timing
    
#     Args:
#         rsi_prev: Previous RSI value
#         rsi_now: Current RSI value
#         rsi_ma: RSI moving average
#         current_price: Current price
#         prev_price: Previous price
#         historical_prices: Array of recent prices for GBM (optional, needs 20+ bars)
    
#     Returns:
#         True if should buy, False otherwise
#     """
#     # ========== RSI CONDITIONS ==========
#     # RSI shows bullish momentum
#     rsi_bullish = (
#         rsi_now > rsi_ma and      # RSI above its moving average
#         rsi_now < 70 and          # Not overbought (avoid buying at peaks)
#         rsi_now > 30              # Not in extreme oversold (could continue falling)
#     )
    
#     # ========== PRICE MOMENTUM CONDITIONS ==========
#     delta_price = current_price - prev_price
#     delta_rsi = rsi_now - rsi_prev
    
#     price_rising = delta_price > 0           # Price is going up
#     rsi_rising = delta_rsi > 0.5             # RSI is increasing (momentum building)
    
#     # ========== GBM PREDICTION ==========
#     gbm_bullish = False
    
#     if historical_prices is not None and len(historical_prices) >= 20:
#         # Run GBM simulation
#         simulated = simulate_gbm(
#             current_price=current_price,
#             historical_prices=historical_prices,
#             n_simulations=500,
#             n_steps=10,
#             dt=1/(252*390)  # Minute-level data
#         )
        
#         if simulated is not None:
#             # Use multiple statistics for robust prediction
#             median_price = np.median(simulated)
#             percentile_60 = np.percentile(simulated, 60)
#             mean_price = np.mean(simulated)
            
#             # Bullish if 60th percentile shows at least 0.2% gain
#             # This means 60% of simulations predict price increase
#             expected_gain = (percentile_60 - current_price) / current_price
#             gbm_bullish = expected_gain > 0.002  # At least 0.2% expected gain
    
#     # ========== DECISION LOGIC ==========
    
#     if historical_prices is not None and len(historical_prices) >= 20:
#         # STRONG BUY: All three signals agree
#         # - GBM predicts upward movement
#         # - RSI shows bullish momentum
#         # - Price is rising
#         return gbm_bullish and rsi_bullish and price_rising
#     else:
#         # FALLBACK: Use RSI + Price momentum only (no GBM data yet)
#         return rsi_bullish and price_rising and rsi_rising


# # ============================================================================
# # HYBRID SELL LOGIC: GBM + RSI + RISK MANAGEMENT
# # ============================================================================

# def sell(rsi_prev, rsi_now, rsi_ma, current_price, prev_price, historical_prices=None, 
#          entry_price=None, position_duration=0):
#     """
#     Hybrid sell logic combining:
#     - GBM prediction for strategic direction
#     - RSI for momentum confirmation
#     - Stop loss and take profit for risk management
    
#     Args:
#         rsi_prev: Previous RSI value
#         rsi_now: Current RSI value
#         rsi_ma: RSI moving average
#         current_price: Current price
#         prev_price: Previous price
#         historical_prices: Array of recent prices for GBM (optional)
#         entry_price: Price at which position was entered (for P&L calculation)
#         position_duration: Minutes holding the position
    
#     Returns:
#         True if should sell, False otherwise
#     """
#     # ========== RISK MANAGEMENT (HIGHEST PRIORITY) ==========
    
#     if entry_price is not None:
#         profit_pct = (current_price - entry_price) / entry_price * 100
        
#         # Stop Loss: Exit if loss exceeds -2%
#         if profit_pct <= -2.0:
#             return True
        
#         # Take Profit: Exit if gain exceeds +3%
#         if profit_pct >= 3.0:
#             return True
        
#         # Trailing Stop: If profit > 1.5%, exit on 0.5% pullback
#         if profit_pct >= 1.5:
#             pullback_pct = (current_price - prev_price) / prev_price * 100
#             if pullback_pct < -0.5:
#                 return True
    
#     # ========== RSI CONDITIONS ==========
#     # RSI shows bearish signals
#     rsi_bearish = (
#         rsi_now < rsi_ma or       # RSI dropped below its MA
#         rsi_now > 75              # Extremely overbought (take profits)
#     )
    
#     # ========== PRICE MOMENTUM CONDITIONS ==========
#     delta_price = current_price - prev_price
#     delta_rsi = rsi_now - rsi_prev
    
#     price_falling = delta_price < 0          # Price is dropping
#     rsi_falling = delta_rsi < -0.5           # RSI is decreasing
    
#     # ========== GBM PREDICTION ==========
#     gbm_bearish = False
    
#     if historical_prices is not None and len(historical_prices) >= 20:
#         # Run GBM simulation
#         simulated = simulate_gbm(
#             current_price=current_price,
#             historical_prices=historical_prices,
#             n_simulations=500,
#             n_steps=10,
#             dt=1/(252*390)  # Minute-level data
#         )
        
#         if simulated is not None:
#             # Use multiple statistics for robust prediction
#             median_price = np.median(simulated)
#             percentile_40 = np.percentile(simulated, 40)
            
#             # Bearish if 40th percentile shows at least 0.2% loss
#             # This means 60% of simulations predict price decrease
#             expected_loss = (percentile_40 - current_price) / current_price
#             gbm_bearish = expected_loss < -0.002  # At least 0.2% expected loss
    
#     # ========== DECISION LOGIC ==========
    
#     # EXTREME CONDITION: Exit if RSI extremely overbought (>80)
#     if rsi_now > 80:
#         return True
    
#     # TIME-BASED EXIT: If held > 60 minutes with minimal profit, exit
#     if entry_price is not None and position_duration > 60:
#         profit_pct = (current_price - entry_price) / entry_price * 100
#         if 0 < profit_pct < 0.5:  # Small profit, not worth holding
#             return True
    
#     if historical_prices is not None and len(historical_prices) >= 20:
#         # STRONG SELL: Both GBM and RSI agree on bearish outlook
#         return (gbm_bearish and rsi_bearish) or (gbm_bearish and price_falling)
#     else:
#         # FALLBACK: Use RSI + Price momentum only
#         return (rsi_bearish and price_falling) or rsi_now > 75

# version 3
# # --- This state must be held outside the function ---
# purchase_price = 0.0
# is_invested = False
# # ----------------------------------------------------

# def check_for_buy(rsi_now, rsi_ma, current_price, prev_price):
#     global is_invested, purchase_price
    
#     delta_price = current_price - prev_price
#     # Buy condition: RSI is strong, price is rising, and we aren't already invested
#     if rsi_now > rsi_ma and delta_price > 0 and not is_invested:
#         is_invested = True
#         purchase_price = current_price
#         return True # <-- Signal to execute BUY
#     return False

# def check_for_sell(rsi_now, rsi_ma, current_price):
#     global is_invested, purchase_price
    
#     if not is_invested:
#         return False

#     # Stop-Loss: Sell if price drops 1% below our purchase price
#     stop_loss_price = purchase_price * 0.99 
    
#     # Take-Profit (example): RSI is now overbought (e.g., > 70) and turning down
#     take_profit_condition = rsi_now < rsi_ma # Your original trend-break logic

#     if current_price < stop_loss_price or take_profit_condition:
#         is_invested = False
#         purchase_price = 0.0
#         return True # <-- Signal to execute SELL
#     return False