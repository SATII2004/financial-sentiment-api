"""
Finnhub API fetcher for news articles
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.api_clients import FinnhubClient
import logging
from datetime import datetime, timedelta
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinnhubNewsFetcher:
    """Fetches news articles from Finnhub API"""
    
    def __init__(self):
        self.client = FinnhubClient()
        logger.info("✅ Finnhub News Fetcher initialized")
    
    def fetch_company_news(self, ticker, days_back=7):
        """
        Fetch news for a specific company from last X days
        
        Args:
            ticker (str): Stock ticker symbol
            days_back (int): Number of days to look back
            
        Returns:
            list: List of news articles
        """
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)
        
        # Format dates as YYYY-MM-DD
        from_str = from_date.strftime('%Y-%m-%d')
        to_str = to_date.strftime('%Y-%m-%d')
        
        logger.info(f"📰 Fetching news for {ticker} from {from_str} to {to_str}")
        
        # Fetch from API
        news = self.client.get_company_news(ticker, from_str, to_str)
        
        if news:
            logger.info(f"✅ Found {len(news)} articles for {ticker}")
        else:
            logger.warning(f"⚠️ No news found for {ticker}")
        
        return news
    
    def fetch_multiple_companies(self, tickers, days_back=7):
        """
        Fetch news for multiple companies
        
        Args:
            tickers (list): List of ticker symbols
            days_back (int): Number of days to look back
            
        Returns:
            dict: Dictionary with ticker as key and news list as value
        """
        all_news = {}
        
        for ticker in tickers:
            try:
                news = self.fetch_company_news(ticker, days_back)
                all_news[ticker] = news
                
                # Small delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Error fetching {ticker}: {e}")
                all_news[ticker] = []
        
        return all_news
    
    def parse_article(self, article):
        """
        Parse raw Finnhub article into our format
        
        Args:
            article (dict): Raw article from Finnhub
            
        Returns:
            dict: Parsed article
        """
        return {
            'title': article.get('headline', ''),
            'summary': article.get('summary', ''),
            'source': article.get('source', ''),
            'url': article.get('url', ''),
            'published_at': datetime.fromtimestamp(article.get('datetime', 0)),
            'image': article.get('image', ''),
            'related': article.get('related', ''),
            'categories': article.get('category', '')
        }


# Quick test
if __name__ == "__main__":
    print("="*50)
    print("🔧 TESTING FINNHUB FETCHER")
    print("="*50)
    
    fetcher = FinnhubNewsFetcher()
    
    # Test with Apple
    news = fetcher.fetch_company_news('AAPL', days_back=3)
    
    if news:
        print(f"\n📰 Latest news for AAPL:")
        print("="*50)
        for i, article in enumerate(news[:5]):  # Show first 5
            parsed = fetcher.parse_article(article)
            print(f"\n{i+1}. {parsed['title']}")
            print(f"   Source: {parsed['source']}")
            print(f"   Time: {parsed['published_at']}")
    else:
        print("❌ No news found")
    
    print("="*50)