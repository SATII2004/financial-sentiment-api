"""
API routes for sentiment data
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.database import get_db, Company, Article, SentimentScore, DailySentiment
from pydantic import BaseModel
from typing import List, Optional
import json

router = APIRouter(prefix="/v1", tags=["sentiment"])

# Pydantic models for response
class SentimentResponse(BaseModel):
    ticker: str
    company_name: str
    timestamp: datetime
    overall_sentiment: dict
    summary: dict
    top_headlines: List[dict]
    trending_topics: List[str]
    historical_trend: dict

class ArticleResponse(BaseModel):
    title: str
    source: str
    published_at: datetime
    sentiment_score: float
    sentiment_label: str
    url: str

class DailySentimentResponse(BaseModel):
    date: str
    avg_sentiment: float
    total_articles: int
    positive_count: int
    negative_count: int
    neutral_count: int

@router.get("/sentiment/{ticker}")
async def get_sentiment(
    ticker: str,
    days: int = Query(7, description="Number of days of history to return"),
    db: Session = Depends(get_db)
):
    """
    Get sentiment analysis for a specific stock ticker
    
    - **ticker**: Stock symbol (e.g., TSLA, AAPL, MSFT)
    - **days**: Number of days of historical data to return (default: 7)
    """
    # Find company
    company = db.query(Company).filter(Company.ticker == ticker.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")
    
    # Get latest sentiment scores
    latest_scores = db.query(SentimentScore).filter(
        SentimentScore.company_id == company.id
    ).order_by(SentimentScore.created_at.desc()).limit(50).all()
    
    if not latest_scores:
        raise HTTPException(status_code=404, detail=f"No sentiment data found for {ticker}")
    
    # Calculate overall sentiment
    avg_score = sum(s.sentiment_score for s in latest_scores) / len(latest_scores)
    if avg_score >= 0.05:
        label = "BULLISH"
    elif avg_score <= -0.05:
        label = "BEARISH"
    else:
        label = "NEUTRAL"
    
    # Get daily aggregates for historical trend
    cutoff_date = datetime.now() - timedelta(days=days)
    daily_data = db.query(DailySentiment).filter(
        DailySentiment.company_id == company.id,
        DailySentiment.date >= cutoff_date.date()
    ).order_by(DailySentiment.date).all()
    
    # Get latest articles with sentiment
    latest_articles = db.query(Article, SentimentScore).join(
        SentimentScore, Article.id == SentimentScore.article_id
    ).filter(
        Article.company_id == company.id
    ).order_by(Article.published_at.desc()).limit(10).all()
    
    # Format top headlines
    top_headlines = []
    for article, score in latest_articles:
        sentiment_label = "positive" if score.sentiment_score >= 0.05 else "negative" if score.sentiment_score <= -0.05 else "neutral"
        top_headlines.append({
            "title": article.title,
            "source": article.source,
            "published_at": article.published_at,
            "sentiment": score.sentiment_score,
            "sentiment_label": sentiment_label,
            "url": article.url
        })
    
    # Extract trending topics (simple implementation - could be improved)
    all_words = []
    for article, _ in latest_articles:
        words = article.title.lower().split()
        all_words.extend([w for w in words if len(w) > 4])
    
    from collections import Counter
    trending = [word for word, count in Counter(all_words).most_common(5)]
    
    # Format historical trend
    historical = {
        "dates": [d.date.strftime("%Y-%m-%d") for d in daily_data],
        "sentiments": [float(d.avg_sentiment) for d in daily_data],
        "volumes": [d.total_articles for d in daily_data]
    }
    
    return {
        "ticker": company.ticker,
        "company_name": company.company_name,
        "timestamp": datetime.now(),
        "overall_sentiment": {
            "score": round(avg_score, 2),
            "label": label,
            "confidence": round(sum(s.confidence for s in latest_scores) / len(latest_scores), 2)
        },
        "summary": {
            "total_articles_analyzed": len(latest_scores),
            "positive_count": sum(1 for s in latest_scores if s.sentiment_score >= 0.05),
            "negative_count": sum(1 for s in latest_scores if s.sentiment_score <= -0.05),
            "neutral_count": sum(1 for s in latest_scores if -0.05 < s.sentiment_score < 0.05)
        },
        "top_headlines": top_headlines[:5],
        "trending_topics": trending,
        "historical_trend": historical
    }

@router.get("/sentiment/{ticker}/history")
async def get_sentiment_history(
    ticker: str,
    days: int = Query(30, description="Number of days of history"),
    db: Session = Depends(get_db)
):
    """Get historical sentiment data for a ticker"""
    company = db.query(Company).filter(Company.ticker == ticker.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")
    
    cutoff_date = datetime.now() - timedelta(days=days)
    daily_data = db.query(DailySentiment).filter(
        DailySentiment.company_id == company.id,
        DailySentiment.date >= cutoff_date.date()
    ).order_by(DailySentiment.date).all()
    
    return [
        {
            "date": d.date.strftime("%Y-%m-%d"),
            "avg_sentiment": float(d.avg_sentiment),
            "total_articles": d.total_articles,
            "positive_count": d.positive_count,
            "negative_count": d.negative_count,
            "neutral_count": d.neutral_count
        }
        for d in daily_data
    ]

@router.get("/sentiment/{ticker}/articles")
async def get_sentiment_articles(
    ticker: str,
    limit: int = Query(20, description="Number of articles to return"),
    db: Session = Depends(get_db)
):
    """Get recent articles with sentiment for a ticker"""
    company = db.query(Company).filter(Company.ticker == ticker.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")
    
    articles = db.query(Article, SentimentScore).join(
        SentimentScore, Article.id == SentimentScore.article_id
    ).filter(
        Article.company_id == company.id
    ).order_by(Article.published_at.desc()).limit(limit).all()
    
    result = []
    for article, score in articles:
        sentiment_label = "positive" if score.sentiment_score >= 0.05 else "negative" if score.sentiment_score <= -0.05 else "neutral"
        result.append({
            "title": article.title,
            "source": article.source,
            "published_at": article.published_at,
            "sentiment_score": float(score.sentiment_score),
            "sentiment_label": sentiment_label,
            "confidence": float(score.confidence),
            "url": article.url
        })
    
    return result

@router.get("/trending")
async def get_trending_tickers(
    limit: int = Query(5, description="Number of trending tickers"),
    db: Session = Depends(get_db)
):
    """Get most discussed tickers"""
    from sqlalchemy import func
    
    trending = db.query(
        Company.ticker,
        Company.company_name,
        func.count(Article.id).label('article_count')
    ).join(
        Article, Company.id == Article.company_id
    ).filter(
        Article.published_at >= datetime.now() - timedelta(days=1)
    ).group_by(
        Company.id
    ).order_by(
        func.count(Article.id).desc()
    ).limit(limit).all()
    
    return [
        {
            "ticker": t.ticker,
            "company_name": t.company_name,
            "article_count": t.article_count
        }
        for t in trending
    ]