"""
Main pipeline orchestrator - Fetches news, analyzes sentiment, stores in database
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.pipeline.fetchers.finnhub_fetcher import FinnhubNewsFetcher
from src.ml.sentiment import SentimentAnalyzer
from src.database import SessionLocal, Company, Article, SentimentScore, DailySentiment
from datetime import datetime, timedelta
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentPipeline:
    """Main pipeline for fetching news and analyzing sentiment"""
    
    def __init__(self):
        self.fetcher = FinnhubNewsFetcher()
        self.analyzer = SentimentAnalyzer()
        self.db = SessionLocal()
        logger.info("✅ Pipeline initialized")
    
    def get_companies_from_db(self):
        """Get all companies from database"""
        return self.db.query(Company).all()
    
    def save_article(self, company_id, article_data, parsed_article):
        """Save article to database if it doesn't exist"""
        try:
            # Check if article already exists (by URL)
            existing = self.db.query(Article).filter(
                Article.url == parsed_article['url']
            ).first()
            
            if existing:
                return existing.id
            
            # Create new article
            article = Article(
                company_id=company_id,
                title=parsed_article['title'],
                source=parsed_article['source'],
                url=parsed_article['url'],
                published_at=parsed_article['published_at']
            )
            
            self.db.add(article)
            self.db.flush()  # Get the ID without committing
            logger.info(f"✅ Saved article: {parsed_article['title'][:50]}...")
            return article.id
            
        except Exception as e:
            logger.error(f"❌ Error saving article: {e}")
            self.db.rollback()
            return None
    
    def save_sentiment(self, company_id, article_id, sentiment_result):
        """Save sentiment score to database"""
        try:
            sentiment = SentimentScore(
                company_id=company_id,
                article_id=article_id,
                sentiment_score=sentiment_result['score'],
                confidence=sentiment_result['confidence'],
                model_version=sentiment_result['model_version']
            )
            
            self.db.add(sentiment)
            logger.info(f"✅ Saved sentiment: {sentiment_result['score']:.2f} - {sentiment_result['label']}")
            
        except Exception as e:
            logger.error(f"❌ Error saving sentiment: {e}")
            self.db.rollback()
    
    def update_daily_aggregate(self, company_id, date):
        """Update or create daily sentiment aggregate"""
        try:
            # Calculate aggregates for the day
            start_of_day = datetime(date.year, date.month, date.day)
            end_of_day = start_of_day + timedelta(days=1)
            
            # Get all sentiments for this company on this day
            sentiments = self.db.query(SentimentScore).join(
                Article, SentimentScore.article_id == Article.id
            ).filter(
                SentimentScore.company_id == company_id,
                Article.published_at >= start_of_day,
                Article.published_at < end_of_day
            ).all()
            
            if not sentiments:
                return
            
            # Calculate statistics
            total = len(sentiments)
            avg_score = sum(s.sentiment_score for s in sentiments) / total
            
            # Count by sentiment label
            positive = sum(1 for s in sentiments if s.sentiment_score >= 0.05)
            negative = sum(1 for s in sentiments if s.sentiment_score <= -0.05)
            neutral = total - positive - negative
            
            # Get top headlines (latest 5)
            top_articles = self.db.query(Article).filter(
                Article.company_id == company_id,
                Article.published_at >= start_of_day,
                Article.published_at < end_of_day
            ).order_by(Article.published_at.desc()).limit(5).all()
            
            top_headlines = [
                {'title': a.title, 'source': a.source, 'published': a.published_at.isoformat()}
                for a in top_articles
            ]
            
            # Check if aggregate exists
            daily = self.db.query(DailySentiment).filter(
                DailySentiment.company_id == company_id,
                DailySentiment.date == date.date()
            ).first()
            
            if daily:
                # Update existing
                daily.avg_sentiment = avg_score
                daily.total_articles = total
                daily.positive_count = positive
                daily.negative_count = negative
                daily.neutral_count = neutral
                daily.top_headlines = json.dumps(top_headlines)
                logger.info(f"✅ Updated daily aggregate for {date.date()}")
            else:
                # Create new
                daily = DailySentiment(
                    company_id=company_id,
                    date=date.date(),
                    avg_sentiment=avg_score,
                    total_articles=total,
                    positive_count=positive,
                    negative_count=negative,
                    neutral_count=neutral,
                    top_headlines=json.dumps(top_headlines)
                )
                self.db.add(daily)
                logger.info(f"✅ Created daily aggregate for {date.date()}")
            
        except Exception as e:
            logger.error(f"❌ Error updating daily aggregate: {e}")
            self.db.rollback()
    
    def run_for_company(self, company, days_back=3):
        """Run pipeline for a single company"""
        logger.info(f"\n{'='*50}")
        logger.info(f"Processing {company.ticker} - {company.company_name}")
        logger.info(f"{'='*50}")
        
        # Fetch news
        news = self.fetcher.fetch_company_news(company.ticker, days_back)
        
        if not news:
            logger.warning(f"⚠️ No news for {company.ticker}")
            return
        
        # Process each article
        for article in news:
            try:
                # Parse article
                parsed = self.fetcher.parse_article(article)
                
                # Save article to DB
                article_id = self.save_article(company.id, article, parsed)
                if not article_id:
                    continue
                
                # Analyze sentiment
                sentiment = self.analyzer.analyze_news_article(
                    parsed['title'], 
                    parsed.get('summary', '')
                )
                
                # Save sentiment
                self.save_sentiment(company.id, article_id, sentiment)
                
                # Update daily aggregate for this article's date
                self.update_daily_aggregate(company.id, parsed['published_at'])
                
            except Exception as e:
                logger.error(f"❌ Error processing article: {e}")
                continue
        
        # Commit all changes for this company
        try:
            self.db.commit()
            logger.info(f"✅ Completed processing for {company.ticker}")
        except Exception as e:
            logger.error(f"❌ Error committing for {company.ticker}: {e}")
            self.db.rollback()
    
    def run_all(self, days_back=3):
        """Run pipeline for all companies"""
        companies = self.get_companies_from_db()
        logger.info(f"📊 Found {len(companies)} companies to process")
        
        for company in companies:
            self.run_for_company(company, days_back)
        
        self.db.close()
        logger.info("✅ Pipeline completed!")


if __name__ == "__main__":
    print("="*50)
    print("🔧 RUNNING SENTIMENT PIPELINE")
    print("="*50)
    
    pipeline = SentimentPipeline()
    
    # Run for all companies (last 3 days)
    pipeline.run_all(days_back=3)