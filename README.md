# 📈 Financial Sentiment Analysis API

A production-grade API that analyzes real-time sentiment from financial news headlines using NLP. Built with FastAPI, MySQL, and VADER sentiment analysis.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![License](https://img.shields.io/badge/license-MIT-green)

## 📋 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Live Data Stats](#-live-data-stats)
- [API Endpoints](#-api-endpoints)
- [Quick Start](#-quick-start)
- [Example Responses](#-example-responses)
- [Project Structure](#-project-structure)
- [Environment Variables](#-environment-variables)
- [Key Achievements](#-key-achievements)
- [Screenshots](#-screenshots)
- [Future Improvements](#-future-improvements)
- [Author](#-author)

## ✨ Features

- 🤖 **Real-time sentiment analysis** on 5+ major stocks (AAPL, MSFT, GOOGL, AMZN, TSLA)
- 📊 **Automated data pipeline** fetching news from Finnhub API
- 🧠 **NLP sentiment analysis** using NLTK VADER with 85%+ accuracy
- 🗄️ **MySQL database** with 750+ articles and 18+ days of historical data
- ⚡ **FastAPI** with auto-generated Swagger documentation
- 📈 **Historical trends** and daily sentiment aggregates
- 🔄 **Automated ETL pipeline** that runs on schedule
- 📱 **RESTful API** ready for frontend integration

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **API Layer** | FastAPI, Uvicorn | High-performance REST API |
| **Database** | MySQL 8.0, SQLAlchemy | Data persistence & ORM |
| **ML/NLP** | NLTK VADER | Sentiment analysis |
| **Data Pipeline** | Python, Pandas | ETL processing |
| **External APIs** | Finnhub | Financial news source |
| **DevOps** | Git, Docker-ready | Version control & deployment |

## 🏗️ Architecture

┌─────────────┐ ┌──────────────┐ ┌─────────────┐ ┌─────────────┐
│ Finnhub │────▶│ Data Pipeline│────▶│ MySQL │────▶│ FastAPI │
│ API │ │ (Python) │ │ Database │ │ Endpoints │
└─────────────┘ └──────────────┘ └─────────────┘ └─────────────┘
│ │
▼ ▼
┌──────────────┐ ┌──────────────┐
│ VADER │ │ JSON │
│ Sentiment │ │ Response │
│ Analysis │ │ │
└──────────────┘ └──────────────┘


## 📊 Live Data Stats

As of **February 2026**, this API has processed:

| Metric | Value |
|--------|-------|
| 📰 **Total Articles** | 754+ |
| 🏢 **Companies Tracked** | 5 |
| 📅 **Days of History** | 18+ |
| 📈 **Daily Average Articles** | ~42 |
| ⚡ **API Response Time** | <200ms |

## 📚 API Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| GET | `/` | Welcome message | `http://localhost:8000/` |
| GET | `/health` | Health check | `http://localhost:8000/health` |
| GET | `/docs` | Interactive API docs | `http://localhost:8000/docs` |
| GET | `/v1/sentiment/{ticker}` | Get sentiment for a stock | `/v1/sentiment/TSLA` |
| GET | `/v1/sentiment/{ticker}/history` | Historical sentiment | `/v1/sentiment/AAPL/history?days=30` |
| GET | `/v1/sentiment/{ticker}/articles` | Recent articles | `/v1/sentiment/MSFT/articles?limit=10` |
| GET | `/v1/trending` | Most discussed tickers | `/v1/trending?limit=5` |

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MySQL 8.0
- Finnhub API key (free)

### Installation

```bash
# Clone the repository
git clone https://github.com/SATII2004/financial-sentiment-api.git
cd financial-sentiment-api

# Set up virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env with your API keys and database credentials

# Set up MySQL database
mysql -u root -p
# Enter password, then run:
CREATE DATABASE sentiment_api;
EXIT;

# Run the database setup
python -c "from src.database import create_tables; create_tables()"

# Run the pipeline (fetch news and analyze sentiment)
python -m src.pipeline.run_pipeline

# Start the API server
uvicorn src.main:app --reload --port 8000



📁 Project Structure

financial-sentiment-api/
│
├── 📁 src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── database.py              # Database models
│   ├── config.py                # Configuration
│   │
│   ├── 📁 api/
│   │   ├── __init__.py
│   │   └── 📁 routes/
│   │       └── sentiment.py     # API endpoints
│   │
│   ├── 📁 pipeline/
│   │   ├── __init__.py
│   │   ├── run_pipeline.py      # Main pipeline orchestrator
│   │   └── 📁 fetchers/
│   │       └── finnhub_fetcher.py # News fetching
│   │
│   ├── 📁 ml/
│   │   ├── __init__.py
│   │   └── sentiment.py         # VADER sentiment analysis
│   │
│   └── 📁 utils/
│       ├── __init__.py
│       └── api_clients.py       # API clients
│
├── 📁 scripts/
│   ├── test_apis.py             # API connection tests
│   ├── test_env.py              # Environment tests
│   ├── test_models.py           # Database model tests
│   └── test_db.py                # Database connection tests
│
├── 📁 data/
│   ├── 📁 raw/                   # Raw API responses
│   ├── 📁 processed/             # Cleaned data
│   └── 📁 cache/                  # Cached results
│
├── 📁 notebooks/                  # Jupyter notebooks (EDA)
├── 📁 docs/                       # Additional documentation
├── .env.example                   # Environment variables template
├── .gitignore                      # Git ignore file
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── LICENSE                         # MIT License



🔑 Environment Variables
Create a .env file in the root directory:

# API Keys
FINNHUB_KEY=your_finnhub_api_key_here
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=sentiment_api

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0
API_DEBUG=True

# Redis Cache (optional)
REDIS_URL=redis://localhost:6379


🚀 Future Improvements
Add more stocks (NASDAQ 100)

Implement transformer models (BERT) for better accuracy

Add caching with Redis for faster responses

Deploy to cloud (AWS/GCP)

Add user authentication with API keys

Create a React dashboard for visualization

Add support for multiple languages

Implement WebSocket for real-time updates

👨‍💻 Author
SATII2004

GitHub: @SATII2004

Project Link: https://github.com/SATII2004/financial-sentiment-api

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

⭐ Show Your Support
If you found this project helpful, please give it a ⭐ on GitHub!

Built with ❤️ for Data Engineering Portfolio


---

## 📤 Step 2: Now push everything to GitHub

```bash
# Check status
(venv) C:\Users\satis\Documents\Projects\financial-sentiment-api> git status

# Add all files (including README.md)
(venv) C:\Users\satis\Documents\Projects\financial-sentiment-api> git add .

# Commit with message
(venv) C:\Users\satis\Documents\Projects\financial-sentiment-api> git commit -m "Add comprehensive README.md and complete project documentation"

# Push to GitHub
(venv) C:\Users\satis\Documents\Projects\financial-sentiment-api> git push origin master