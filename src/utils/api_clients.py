"""
API client wrappers for Finnhub and Alpha Vantage.
Handles authentication, rate limiting, and error handling.
"""
import os
import finnhub
import requests
from dotenv import load_dotenv
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add this function to debug environment variables
def debug_env():
    """Debug function to check environment variables"""
    from dotenv import load_dotenv
    load_dotenv()
    
    finnhub_key = os.getenv('FINNHUB_KEY')
    alpha_key = os.getenv('ALPHA_VANTAGE_KEY')
    
    print("\n🔍 Environment Debug:")
    print(f"FINNHUB_KEY present: {'✅ Yes' if finnhub_key else '❌ No'}")
    if finnhub_key:
        print(f"  Length: {len(finnhub_key)} characters")
        print(f"  Starts with: {finnhub_key[:5]}...")
    print(f"ALPHA_VANTAGE_KEY present: {'✅ Yes' if alpha_key else '❌ No'}")
    if alpha_key:
        print(f"  Length: {len(alpha_key)} characters")
        print(f"  Starts with: {alpha_key[:5]}...")
    print()

class FinnhubClient:
    """Wrapper for Finnhub API client"""
    
    def __init__(self):
        self.api_key = os.getenv('FINNHUB_KEY')
        if not self.api_key:
            raise ValueError("❌ FINNHUB_KEY not found in environment variables")
        
        # Initialize the official Finnhub client
        self.client = finnhub.Client(api_key=self.api_key)
        logger.info("✅ Finnhub client initialized")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def get_company_news(self, symbol: str, from_date: str = None, to_date: str = None):
        """
        Fetch company news.
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL')
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
        """
        try:
            # If dates not provided, get last 7 days
            if not from_date:
                from_date = time.strftime("%Y-%m-%d", time.localtime(time.time() - 7*24*60*60))
            if not to_date:
                to_date = time.strftime("%Y-%m-%d")
            
            # Finnhub provides company news
            news = self.client.company_news(symbol, _from=from_date, to=to_date)
            logger.info(f"✅ Fetched {len(news)} news articles for {symbol}")
            return news
        except Exception as e:
            logger.error(f"❌ Error fetching news for {symbol}: {e}")
            return []
    
    def get_stock_quote(self, symbol: str):
        """Get real-time stock quote"""
        try:
            quote = self.client.quote(symbol)
            return quote
        except Exception as e:
            logger.error(f"❌ Error fetching quote for {symbol}: {e}")
            return None


class AlphaVantageClient:
    """Wrapper for Alpha Vantage API client"""
    
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_KEY')
        if not self.api_key:
            raise ValueError("❌ ALPHA_VANTAGE_KEY not found in environment variables")
        
        self.base_url = "https://www.alphavantage.co/query"
        self.last_request_time = 0
        self.min_request_interval = 12  # Alpha Vantage free tier: 5 calls per minute
        logger.info("✅ Alpha Vantage client initialized")
    
    def _rate_limit(self):
        """Simple rate limiting to stay within free tier limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.info(f"⏱️ Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def get_technical_indicator(self, symbol: str, indicator: str = 'RSI'):
        """
        Get technical indicators for a symbol.
        """
        self._rate_limit()
        
        params = {
            'function': indicator,
            'symbol': symbol,
            'interval': 'daily',
            'time_period': 14,
            'series_type': 'close',
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if 'Error Message' in data:
                logger.error(f"❌ Alpha Vantage error: {data['Error Message']}")
                return None
            
            logger.info(f"✅ Fetched {indicator} for {symbol}")
            return data
        except Exception as e:
            logger.error(f"❌ Error fetching technical indicator: {e}")
            return None


# Simple test function to verify API keys work
def test_api_connections():
    """Test both API connections"""
    print("\n🔍 Testing API Connections...\n")
    debug_env()

    # Test Finnhub
    try:
        finnhub_client = FinnhubClient()
        news = finnhub_client.get_company_news('AAPL')
        if news:
            print(f"✅ Finnhub: Successfully connected! Got {len(news)} news items")
            if len(news) > 0:
                print(f"   Sample headline: {news[0]['headline'][:50]}...")
        else:
            print("⚠️ Finnhub: Connected but no news returned")
    except Exception as e:
        print(f"❌ Finnhub connection failed: {e}")
    
    # Test Alpha Vantage
    try:
        av_client = AlphaVantageClient()
        rsi = av_client.get_technical_indicator('AAPL', 'RSI')
        if rsi and 'Technical Analysis: RSI' in rsi:
            print(f"✅ Alpha Vantage: Successfully connected! Got RSI data")
            # Get the latest date
            latest_date = list(rsi['Technical Analysis: RSI'].keys())[0]
            latest_rsi = rsi['Technical Analysis: RSI'][latest_date]['RSI']
            print(f"   Latest RSI for AAPL: {latest_rsi}")
        else:
            print("⚠️ Alpha Vantage: Connected but unexpected response")
    except Exception as e:
        print(f"❌ Alpha Vantage connection failed: {e}")

if __name__ == "__main__":
    test_api_connections()