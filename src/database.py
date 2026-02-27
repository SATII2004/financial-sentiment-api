"""
Database models using SQLAlchemy
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, DECIMAL, ForeignKey, Index, JSON, Date,UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection URL
DATABASE_URL = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Create engine
engine = create_engine(DATABASE_URL, echo=True)  # echo=True shows SQL queries (remove in production)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

# Base class for models
Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), unique=True, nullable=False)
    company_name = Column(String(100))
    sector = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationships
    articles = relationship("Article", back_populates="company")
    sentiment_scores = relationship("SentimentScore", back_populates="company")
    daily_sentiments = relationship("DailySentiment", back_populates="company")
    
    __table_args__ = (
        Index('idx_ticker', 'ticker'),
    )

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    title = Column(Text, nullable=False)
    source = Column(String(100))
    url = Column(Text)
    published_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationships
    company = relationship("Company", back_populates="articles")
    sentiment_scores = relationship("SentimentScore", back_populates="article")
    
    __table_args__ = (
        Index('idx_published', 'published_at'),
        Index('idx_company_date', 'company_id', 'published_at'),
    )

class SentimentScore(Base):
    __tablename__ = 'sentiment_scores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    article_id = Column(Integer, ForeignKey('articles.id'))
    sentiment_score = Column(DECIMAL(3, 2))  # -1 to 1
    confidence = Column(DECIMAL(3, 2))
    model_version = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationships
    company = relationship("Company", back_populates="sentiment_scores")
    article = relationship("Article", back_populates="sentiment_scores")
    
    __table_args__ = (
        Index('idx_sentiment_lookup', 'company_id', 'created_at'),
    )

class DailySentiment(Base):
    __tablename__ = 'daily_sentiment'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    date = Column(Date, nullable=False)
    avg_sentiment = Column(DECIMAL(3, 2))
    total_articles = Column(Integer)
    positive_count = Column(Integer)
    negative_count = Column(Integer)
    neutral_count = Column(Integer)
    top_headlines = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    company = relationship("Company", back_populates="daily_sentiments")
    
    __table_args__ = (
        UniqueConstraint('company_id', 'date', name='unique_company_date'),
        Index('idx_date_sentiment', 'date', 'avg_sentiment'),
    )

# Function to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create tables (if they don't exist)
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created/verified successfully!")

if __name__ == "__main__":
    create_tables()