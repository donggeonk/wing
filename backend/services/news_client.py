import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

class NewsAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"
    
    def get_recent_news(self, symbol, days=7, limit=5, custom_query=None):
        """
        Get recent news for a stock symbol using News API
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')
            days: Number of days to look back (default: 7)
            limit: Maximum number of articles (default: 5)
            custom_query: Optional custom search query from LLM. 
                         If provided, overrides default query.
                         Use {symbol} as placeholder for the stock symbol.
        
        Query Format Rules:
            - Use AND, OR, NOT operators (must be UPPERCASE)
            - Use parentheses () for grouping
            - Use quotes "" for exact phrases
            - Keep it simple with keywords
        
        Examples:
            # Default - broad search
            get_recent_news('AAPL')
            
            # LLM provides custom query
            get_recent_news('AAPL', custom_query='{symbol}')
            get_recent_news('AAPL', custom_query='{symbol} AND (stock OR price)')
            get_recent_news('AAPL', custom_query='{symbol} AND earnings')
            get_recent_news('TSLA', custom_query='({symbol} OR Tesla) AND (Elon Musk OR CEO)')
        """
        try:
            # If LLM provides custom query, use it. Otherwise use default.
            if custom_query:
                query = custom_query.format(symbol=symbol)
            else:
                # Default: just the symbol (broad search)
                query = symbol
            
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': limit,
                'from': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                'apiKey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                return {
                    "symbol": symbol,
                    "query_used": query,
                    "total_articles": len(articles),
                    "articles": [
                        {
                            "headline": article['title'],
                            "summary": article.get('description', '')[:200] or (article.get('content', '')[:200] if article.get('content') else ''),
                            "author": article.get('author', 'Unknown'),
                            "source": article['source']['name'],
                            "url": article['url'],
                            "created_at": article['publishedAt'],
                            "symbols": [symbol]
                        }
                        for article in articles
                    ]
                }
            else:
                return {"error": data.get('message', 'Unknown error')}
                
        except Exception as e:
            return {"error": str(e)}


# # Test
# if __name__ == '__main__':
#     load_dotenv()
    
#     news_client = NewsAPIClient(api_key=os.getenv('NEWS_API_KEY'))
    
#     print("\n" + "="*80)
#     print("TEST 1: Default Query (No custom query)")
#     print("="*80)
#     news = news_client.get_recent_news('AAPL', limit=3)
#     if "error" not in news:
#         print(f"Query used: {news['query_used']}")
#         print(f"Found {news['total_articles']} articles:\n")
#         for i, article in enumerate(news['articles'], 1):
#             print(f"{i}. {article['headline']}")
#             print(f"   Source: {article['source']}\n")
    
#     print("\n" + "="*80)
#     print("TEST 2: LLM Custom Query (Stock-focused)")
#     print("="*80)
#     news = news_client.get_recent_news(
#         'TSLA',
#         limit=3,
#         custom_query='{symbol} AND (stock OR price OR earnings)'
#     )
#     if "error" not in news:
#         print(f"Query used: {news['query_used']}")
#         print(f"Found {news['total_articles']} articles:\n")
#         for i, article in enumerate(news['articles'], 1):
#             print(f"{i}. {article['headline']}")
#             print(f"   Source: {article['source']}\n")
    
#     print("\n" + "="*80)
#     print("TEST 3: LLM Custom Query (Product news)")
#     print("="*80)
#     news = news_client.get_recent_news(
#         'AAPL',
#         limit=3,
#         custom_query='{symbol} AND (iPhone OR Mac OR product OR launch)'
#     )
#     if "error" not in news:
#         print(f"Query used: {news['query_used']}")
#         print(f"Found {news['total_articles']} articles:\n")
#         for i, article in enumerate(news['articles'], 1):
#             print(f"{i}. {article['headline']}")
#             print(f"   Source: {article['source']}\n")



# news_function = {
#     "type": "function",
#     "function": {
#         "name": "get_recent_news",
#         "description": "Get recent news articles for a stock symbol. Returns headlines, summaries, sources, and URLs.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "symbol": {
#                     "type": "string",
#                     "description": "Stock symbol (e.g., 'AAPL', 'TSLA', 'NVDA')"
#                 },
#                 "days": {
#                     "type": "integer",
#                     "description": "Number of days to look back (default: 7)",
#                     "default": 7
#                 },
#                 "limit": {
#                     "type": "integer",
#                     "description": "Maximum number of articles to return (default: 5)",
#                     "default": 5
#                 },
#                 "custom_query": {
#                     "type": "string",
#                     "description": "Optional custom search query. Use {symbol} as placeholder. Use AND, OR, NOT operators (UPPERCASE). Examples: '{symbol}', '{symbol} AND stock', '{symbol} AND (earnings OR revenue)'",
#                     "default": None
#                 }
#             },
#             "required": ["symbol"]
#         }
#     }
# }