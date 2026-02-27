"""
Main application entry point.
Initializes FastAPI and includes routers.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import sentiment

# Create FastAPI app
app = FastAPI(
    title="Financial Sentiment Analysis API",
    description="Real-time sentiment analysis from financial news headlines",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sentiment.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Financial Sentiment API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "sentiment": "/v1/sentiment/{ticker}",
            "history": "/v1/sentiment/{ticker}/history",
            "articles": "/v1/sentiment/{ticker}/articles",
            "trending": "/v1/trending"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

from datetime import datetime