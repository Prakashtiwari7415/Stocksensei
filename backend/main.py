"""
FastAPI backend for Stock Market Sentiment Tracker
Provides APIs for stock data, sentiment analysis, and user management
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
import os
from dotenv import load_dotenv

from database.database import get_db, SessionLocal
from models.models import StockData, SentimentData, AlertData, User
from services.stock_service import StockService
from services.sentiment_service import SentimentService
from services.alert_service import AlertService
from schemas.schemas import (
    StockDataResponse, SentimentAnalysisResponse, AlertResponse,
    StockRequest, UserPreferences, DashboardResponse
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Stock Market Sentiment Tracker API",
    description="API for real-time stock data and sentiment analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
stock_service = StockService()
sentiment_service = SentimentService()
alert_service = AlertService()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Stock Market Sentiment Tracker API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "timezone": "Asia/Kolkata"
    }

@app.get("/api/stocks/{symbol}", response_model=StockDataResponse)
async def get_stock_data(
    symbol: str,
    days: Optional[int] = 7,
    db: SessionLocal = Depends(get_db)
):
    """Get stock data for a specific symbol"""
    try:
        # Clean symbol for Indian stocks
        clean_symbol = symbol.upper()
        if not clean_symbol.endswith('.NS') and symbol.lower() not in ['aapl', 'googl', 'msft', 'amzn', 'tsla', 'meta', 'nvda']:
            clean_symbol += '.NS'
        
        stock_data = await stock_service.get_stock_data(clean_symbol, days)
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"Stock data not found for {symbol}")
        
        return stock_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sentiment/{symbol}", response_model=SentimentAnalysisResponse)
async def get_sentiment_analysis(
    symbol: str,
    days: Optional[int] = 7,
    db: SessionLocal = Depends(get_db)
):
    """Get sentiment analysis for a specific stock"""
    try:
        clean_symbol = symbol.upper()
        if not clean_symbol.endswith('.NS') and symbol.lower() not in ['aapl', 'googl', 'msft', 'amzn', 'tsla', 'meta', 'nvda']:
            clean_symbol += '.NS'
            
        sentiment_data = await sentiment_service.analyze_sentiment(clean_symbol, days)
        if not sentiment_data:
            raise HTTPException(status_code=404, detail=f"Sentiment data not found for {symbol}")
        
        return sentiment_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dashboard")
async def get_dashboard_data(
    request: StockRequest,
    db: SessionLocal = Depends(get_db)
):
    """Get comprehensive dashboard data for multiple stocks"""
    try:
        symbols = request.symbols
        lookback_days = request.lookback_days or 7
        
        dashboard_data = {
            "stocks": {},
            "sentiment": {},
            "alerts": [],
            "summary": {
                "total_stocks": len(symbols),
                "avg_sentiment": 0.5,
                "active_alerts": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
        
        # Fetch data for all symbols concurrently
        stock_tasks = [stock_service.get_stock_data(symbol, lookback_days) for symbol in symbols]
        sentiment_tasks = [sentiment_service.analyze_sentiment(symbol, lookback_days) for symbol in symbols]
        
        stock_results = await asyncio.gather(*stock_tasks, return_exceptions=True)
        sentiment_results = await asyncio.gather(*sentiment_tasks, return_exceptions=True)
        
        # Process results
        sentiment_scores = []
        for i, symbol in enumerate(symbols):
            if not isinstance(stock_results[i], Exception) and stock_results[i]:
                dashboard_data["stocks"][symbol] = stock_results[i]
            
            if not isinstance(sentiment_results[i], Exception) and sentiment_results[i]:
                dashboard_data["sentiment"][symbol] = sentiment_results[i]
                sentiment_scores.append(sentiment_results[i].overall_sentiment)
        
        # Calculate summary metrics
        if sentiment_scores:
            dashboard_data["summary"]["avg_sentiment"] = sum(sentiment_scores) / len(sentiment_scores)
        
        # Generate alerts
        alerts = await alert_service.generate_alerts(dashboard_data["sentiment"])
        dashboard_data["alerts"] = alerts
        dashboard_data["summary"]["active_alerts"] = len(alerts)
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts", response_model=List[AlertResponse])
async def get_alerts(
    symbols: Optional[List[str]] = None,
    severity: Optional[str] = None,
    db: SessionLocal = Depends(get_db)
):
    """Get alerts for specified stocks"""
    try:
        alerts = await alert_service.get_alerts(symbols, severity)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-status")
async def get_market_status():
    """Get current market status for Indian and US markets"""
    try:
        now = datetime.now()
        
        # Indian market (NSE): 9:15 AM - 3:30 PM IST, Monday-Friday
        indian_market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        indian_market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        # US market: 9:30 AM - 4:00 PM EST (7:00 PM - 2:30 AM IST next day)
        us_market_open = now.replace(hour=19, minute=0, second=0, microsecond=0)
        us_market_close = (now + timedelta(days=1)).replace(hour=2, minute=30, second=0, microsecond=0)
        
        is_weekday = now.weekday() < 5
        indian_open = is_weekday and indian_market_open <= now <= indian_market_close
        us_open = is_weekday and (now >= us_market_open or now <= us_market_close)
        
        return {
            "indian_market": {
                "is_open": indian_open,
                "next_open": indian_market_open if not indian_open else None,
                "next_close": indian_market_close if indian_open else None,
                "timezone": "Asia/Kolkata"
            },
            "us_market": {
                "is_open": us_open,
                "timezone": "America/New_York"
            },
            "timestamp": now.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/popular-stocks")
async def get_popular_stocks():
    """Get list of popular Indian and US stocks"""
    return {
        "indian_stocks": [
            {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy"},
            {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "sector": "Technology"},
            {"symbol": "INFY.NS", "name": "Infosys", "sector": "Technology"},
            {"symbol": "ITC.NS", "name": "ITC Limited", "sector": "FMCG"},
            {"symbol": "LT.NS", "name": "Larsen & Toubro", "sector": "Construction"},
            {"symbol": "WIPRO.NS", "name": "Wipro", "sector": "Technology"},
            {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel", "sector": "Telecom"},
            {"symbol": "MARUTI.NS", "name": "Maruti Suzuki", "sector": "Automotive"}
        ],
        "us_stocks": [
            {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "E-commerce"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Automotive"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Technology"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"}
        ]
    }

# Background task for periodic data updates
@app.post("/api/refresh-data")
async def refresh_data(background_tasks: BackgroundTasks):
    """Trigger background data refresh for all tracked stocks"""
    background_tasks.add_task(stock_service.refresh_all_data)
    background_tasks.add_task(sentiment_service.refresh_all_sentiment)
    
    return {
        "message": "Data refresh initiated",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )