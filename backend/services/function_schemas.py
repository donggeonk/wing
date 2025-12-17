"""
OpenAI Function Schemas for Trading Assistant
Define all function calling schemas here for easy maintenance

Guidelines for writing LLM-friendly descriptions:
- Be specific about what data is returned
- Include use cases and when to use the function
- Mention limitations or important notes
- Use clear, actionable language
"""

FUNCTION_SCHEMAS = [
    # ========== INFORMATION & ANALYSIS FUNCTIONS ==========
    {
        "type": "function",
        "function": {
            "name": "get_account",
            "description": "Get account information including total equity, available cash, buying power, and account status. Use this to answer questions about account balance, available funds, or overall portfolio value.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_portfolio_positions",
            "description": "Get all current stock positions in the portfolio. Returns symbol, quantity, current market value, cost basis, unrealized profit/loss (both $ and %), and current price for each holding. Use this when user asks questions like 'what stocks do I own?' or wants details about their holdings.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_portfolio_summary",
            "description": "Get comprehensive portfolio overview combining account info and all positions. Returns total portfolio value, cash percentage, number of positions, total unrealized P/L, and detailed position list. Use this for holistic portfolio analysis or when user asks 'how is my portfolio doing?'",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_bar",
            "description": "Get the most recent OHLCV (Open, High, Low, Close, Volume) data for a stock. Shows the latest trading bar with opening price, intraday high/low, closing price, trading volume, and timestamp. Use this for current price info or when analyzing recent price action.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol in uppercase (e.g., 'AAPL' for Apple, 'TSLA' for Tesla, 'MSFT' for Microsoft)"
                    }
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_quote",
            "description": "Get real-time bid/ask quotes for a stock. Shows current bid price (what buyers are willing to pay), ask price (what sellers are asking), bid/ask sizes, and spread. Use this to see live market depth and liquidity, especially before discussing trade execution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol in uppercase (e.g., 'AAPL', 'GOOGL', 'NVDA')"
                    }
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_trade",
            "description": "Get the most recent trade execution for a stock. Shows the last trade price, size (number of shares), exchange where it occurred, and exact timestamp. Use this to confirm the very latest transaction price when the most current data is needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol in uppercase (e.g., 'AAPL', 'TSLA', 'AMD')"
                    }
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_market_snapshot",
            "description": "Get comprehensive market snapshot combining daily bar, previous day data, minute bar, latest trade, and daily performance metrics (change %, volume). This is the most complete single function for analyzing a stock's current state. Use this when you need a full picture of how a stock is performing today.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol in uppercase (e.g., 'AAPL', 'TSLA', 'META')"
                    }
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_historical_stats",
            "description": "Get historical statistics for a stock over a custom time period. Returns average closing price, period high/low, average volume, total bars (data points), and the date range analyzed. Use this to understand price trends, volatility, and trading patterns over weeks or months. Great for comparing 'how did X perform over the last 30 days?'",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol in uppercase (e.g., 'AAPL', 'TSLA', 'NFLX')"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to look back for analysis. Default is 30 days. Use 7 for weekly, 30 for monthly, 90 for quarterly, 365 for yearly analysis.",
                        "default": 30
                    }
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_stocks",
            "description": "Compare performance of 2 or more stocks side-by-side over the same time period. Returns current price, today's change %, period high/low/average, and trading volume for each stock. Perfect for answering 'which stock performed better?' or 'should I buy X or Y?' Use this whenever comparing multiple stocks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of 2+ stock ticker symbols to compare (e.g., ['AAPL', 'MSFT', 'GOOGL']). All symbols should be uppercase. Works best with 2-5 stocks for clear comparison."
                    },
                    "days": {
                        "type": "integer",
                        "description": "Time period for comparison in days. Default is 30 days. All stocks are analyzed over the same period for fair comparison.",
                        "default": 30
                    }
                },
                "required": ["symbols"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_news",
            "description": "Get recent news articles about a stock from various sources. Returns headline, summary, source, URL, and publication date for each article. Use this to provide context on why a stock is moving, recent earnings, product launches, or market sentiment. Always cite the news source when referencing articles. You can customize the search query to focus on specific topics like 'earnings', 'CEO', or 'product launch'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol in uppercase (e.g., 'AAPL', 'TSLA', 'NVDA')"
                    },
                    "days": {
                        "type": "integer",
                        "description": "How many days back to search for news. Default is 7 days (last week). Use 1-3 for very recent news, 7 for weekly, 30 for monthly coverage.",
                        "default": 7
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of articles to return. Default is 5. Use 3 for quick overview, 5-10 for comprehensive analysis.",
                        "default": 5
                    },
                    "custom_query": {
                        "type": "string",
                        "description": "Optional: Customize the news search query to focus on specific topics. Use {symbol} as placeholder for the stock symbol. Examples: '{symbol} AND earnings' for earnings news, '{symbol} AND (CEO OR leadership)' for management news, '{symbol} AND (product OR launch)' for product news. Use AND/OR/NOT operators (must be UPPERCASE) to combine keywords."
                    }
                },
                "required": ["symbol"]
            }
        }
    },
    
    # ========== TRADING EXECUTION FUNCTIONS ==========
    {
        "type": "function",
        "function": {
            "name": "place_market_order",
            "description": "Execute a market order to buy or sell stock immediately at current market price. Use this when user wants to trade NOW at whatever the current price is. Market orders execute fast but price is not guaranteed. Always confirm the action before calling this function.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol in uppercase (e.g., 'AAPL', 'TSLA')"
                    },
                    "qty": {
                        "type": "number",
                        "description": "Number of shares to trade. Can be fractional (e.g., 0.5 shares). Must be positive."
                    },
                    "side": {
                        "type": "string",
                        "enum": ["buy", "sell"],
                        "description": "Order side: 'buy' to purchase shares, 'sell' to sell shares you own"
                    }
                },
                "required": ["symbol", "qty", "side"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "place_limit_order",
            "description": "Place a limit order to buy or sell at a specific price or better. Order only executes if market reaches your limit price. Use this when user wants price control and is willing to wait. Good for: 'buy AAPL if it drops to $180' or 'sell TSLA when it hits $300'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol in uppercase"
                    },
                    "qty": {
                        "type": "number",
                        "description": "Number of shares to trade"
                    },
                    "side": {
                        "type": "string",
                        "enum": ["buy", "sell"],
                        "description": "'buy' or 'sell'"
                    },
                    "limit_price": {
                        "type": "number",
                        "description": "Limit price: maximum price for buy orders, minimum price for sell orders"
                    }
                },
                "required": ["symbol", "qty", "side", "limit_price"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "place_stop_order",
            "description": "Place a stop order that triggers a market order when price reaches stop price. Used for stop-loss (limit downside) or breakout trading (buy when price breaks above resistance). Order becomes active market order when stop price is hit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol in uppercase"
                    },
                    "qty": {
                        "type": "number",
                        "description": "Number of shares"
                    },
                    "side": {
                        "type": "string",
                        "enum": ["buy", "sell"],
                        "description": "'buy' or 'sell'"
                    },
                    "stop_price": {
                        "type": "number",
                        "description": "Stop price that triggers the order. For sell stop-loss: below current price. For buy breakout: above current price."
                    }
                },
                "required": ["symbol", "qty", "side", "stop_price"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_open_orders",
            "description": "Get all pending orders that haven't been filled or cancelled yet. Shows limit orders waiting to execute, stop orders waiting to trigger, etc. Use this to check what orders are currently active.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_order",
            "description": "Cancel a specific pending order by its order ID. Use this when user wants to cancel a limit or stop order that hasn't executed yet. Cannot cancel orders that are already filled.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The unique order ID to cancel (get this from get_open_orders or after placing an order)"
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_all_orders",
            "description": "Cancel ALL pending orders at once. Use this when user says 'cancel all my orders' or 'clear all pending orders'. This is a bulk action - be careful!",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_history",
            "description": "Get recent order history showing filled, cancelled, and pending orders. Use this to check past trades, see what executed, or review cancelled orders. Great for 'show me my recent trades' or 'what orders did I place today?'",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of orders to return (default: 10, max: 100)",
                        "default": 10
                    },
                    "status": {
                        "type": "string",
                        "enum": ["all", "open", "closed", "filled", "cancelled"],
                        "description": "Filter by order status. 'all' shows everything, 'filled' shows executed orders, 'cancelled' shows cancelled orders.",
                        "default": "all"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_by_id",
            "description": "Get detailed information about a specific order using its order ID. Shows current status, filled quantity, prices, and timestamps. Use this to check on a specific order's status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The unique order ID to look up"
                    }
                },
                "required": ["order_id"]
            }
        }
    }
]