import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from services.alpaca_info import AlpacaClient
from services.alpaca_trade import AlpacaTrading
from services.news_client import NewsAPIClient
from services.function_schemas import FUNCTION_SCHEMAS
from services.system_prompts import TRADING_ASSISTANT_PROMPT

load_dotenv()

class TradingAssistant:
    """
    AI Trading Assistant with function calling capabilities
    
    Combines information retrieval AND trading execution
    
    Add new functions by:
    1. Adding the function to available_functions dict
    2. Adding the function schema to services/function_schemas.py
    """
    
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Initialize service clients
        self.alpaca = AlpacaClient(
            api_key=os.getenv('ALPACA_API_KEY'),
            api_secret=os.getenv('ALPACA_SECRET_KEY')
        )
        self.trading = AlpacaTrading(
            api_key=os.getenv('ALPACA_API_KEY'),
            api_secret=os.getenv('ALPACA_SECRET_KEY'),
            paper=True  # Paper trading mode
        )
        self.news = NewsAPIClient(api_key=os.getenv('NEWS_API_KEY'))
        
        # Map function names to actual functions
        self.available_functions = {
            # Information & Analysis Functions
            "get_account": self.alpaca.get_account,
            "get_portfolio_positions": self.alpaca.get_portfolio_positions,
            "get_portfolio_summary": self.alpaca.get_portfolio_summary,
            "get_latest_bar": self.alpaca.get_latest_bar,
            "get_latest_quote": self.alpaca.get_latest_quote,
            "get_latest_trade": self.alpaca.get_latest_trade,
            "get_market_snapshot": self.alpaca.get_market_snapshot,
            "get_historical_stats": self.alpaca.get_historical_stats,
            "compare_stocks": self.alpaca.compare_stocks,
            "get_recent_news": self.news.get_recent_news,
            
            # Trading Execution Functions
            "place_market_order": self.trading.place_market_order,
            "place_limit_order": self.trading.place_limit_order,
            "place_stop_order": self.trading.place_stop_order,
            "get_open_orders": self.trading.get_open_orders,
            "cancel_order": self.trading.cancel_order,
            "cancel_all_orders": self.trading.cancel_all_orders,
            "get_order_history": self.trading.get_order_history,
            "get_order_by_id": self.trading.get_order_by_id,
        }
        
        # Import function schemas from separate file
        self.tools = FUNCTION_SCHEMAS
        
        # Conversation history - memory
        self.messages = [
            {
                "role": "system",
                "content": TRADING_ASSISTANT_PROMPT
            }
        ]
    
    def chat(self, user_message):
        """
        Main chat interface - handles user messages and function calls
        
        Args: user_message: User's question or request
        Returns: Assistant's response after processing any function calls
        """
        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Initial API call
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.messages,
            tools=self.tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        # If no function calls, return the response
        if not tool_calls:
            self.messages.append({
                "role": "assistant",
                "content": response_message.content
            })
            return response_message.content
        
        # Add assistant's response to messages
        self.messages.append(response_message)
        
        # Process each function call
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Show function call for transparency (especially for trades!)
            if function_name.startswith('place_') or function_name.startswith('cancel_'):
                print(f"\nEXECUTING: {function_name}")
                print(f"Arguments: {function_args}\n")
            
            # Call the actual function
            function_to_call = self.available_functions[function_name]
            function_response = function_to_call(**function_args)
            
            # Show execution result for trades
            if function_name.startswith('place_') or function_name.startswith('cancel_'):
                if function_response.get('success'):
                    print(f"Success: {function_name} completed\n")
                    if 'order_id' in function_response:
                        print(f"Order ID: {function_response['order_id']}")
                else:
                    print(f"Failed: {function_response.get('error', 'Unknown error')}\n")
            
            # Add function response to messages
            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(function_response)
            })
        
        # Get final response with function results
        final_response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.messages
        )
        
        final_message = final_response.choices[0].message.content
        
        # Add final response to history
        self.messages.append({
            "role": "assistant",
            "content": final_message
        })
        
        return final_message
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.messages = [self.messages[0]]  # Keep system message


# Interactive chat interface
if __name__ == '__main__':
    print("\n" + "="*80)
    print("AI TRADING COPILOT - CLI")
    print("="*80)
    print("\nWelcome! I'm your personal trading and investment assistant.")
    print("I can help you:")
    print("  • Analyze your portfolio and research stocks")
    print("  • Provide market insights and recommendations")
    print("  • Execute trades (market, limit, and stop orders)")
    print("  • Manage and track your orders")
    print("\nPAPER TRADING MODE - No real money involved!")
    print("\nCommands:")
    print("  • Type your question or trading request")
    print("  • Type 'quit' or 'exit' to end the session")
    print("  • Type 'reset' to clear conversation history")
    print("="*80 + "\n")
    
    assistant = TradingAssistant()
    
    while True:
        try:
            # Get user input
            user_input = input("YOU: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! Happy trading!\n")
                break
            
            # Check for reset command
            if user_input.lower() == 'reset':
                assistant.reset_conversation()
                print("\nConversation history cleared.\n")
                continue
            
            # Skip empty input
            if not user_input:
                continue
            
            # Get assistant response
            print()  # Add blank line
            response = assistant.chat(user_input)
            print(f"\nASSISTANT: {response}\n")
            print("-" * 80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")
            print("Please try again or type 'quit' to exit.\n")