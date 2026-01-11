# Stateless functions - state is passed in and managed by the caller

def check_for_buy(rsi_now, rsi_ma, current_price, prev_price, is_invested):
    """
    Check if we should buy
    
    Args:
        rsi_now: Current RSI value
        rsi_ma: RSI moving average
        current_price: Current price
        prev_price: Previous bar's price
        is_invested: Boolean indicating if we're currently in a position
    
    Returns:
        True if should buy, False otherwise
    """
    delta_price = current_price - prev_price
    
    # Buy condition: RSI is strong, price is rising, and we aren't already invested
    if rsi_now > rsi_ma and delta_price > 0 and not is_invested:
        return True
    
    return False


def check_for_sell(rsi_now, rsi_ma, current_price, purchase_price, is_invested):
    """
    Check if we should sell
    
    Args:
        rsi_now: Current RSI value
        rsi_ma: RSI moving average
        current_price: Current price
        purchase_price: Price at which we entered the position
        is_invested: Boolean indicating if we're currently in a position
    
    Returns:
        True if should sell, False otherwise
    """
    if not is_invested:
        return False

    # Stop-Loss: Sell if price drops 1% below our purchase price
    stop_loss_price = purchase_price * 0.99 
    
    # Take-Profit: RSI trend-break logic
    take_profit_condition = rsi_now < rsi_ma

    if current_price < stop_loss_price or take_profit_condition:
        return True
    
    return False