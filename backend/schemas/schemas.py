"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class StockRequest(BaseModel):
    symbols: List[str]
    lookback_days: Optional[int] = 7

class UserPreferences(BaseModel):
    timezone: str = "Asia/Kolkata"
    currency: str = "INR"
    alert_threshold: float = 0.7
    refresh_interval: int = 15

class StockDataResponse(BaseModel):
    symbol: str
    name: str
    sector: str
    current_price: float
    price_change: float
    price_change_pct: float
    volume: int
    market_cap: str
    pe_ratio: Optional[float]
    ma_5: Optional[float]
    ma_20: Optional[float]
    rsi: Optional[float]
    volatility: Optional[float]
    historical_data: Optional[List[Dict[str, Any]]]
    last_updated: datetime

class HeadlineData(BaseModel):
    title: str
    sentiment: float
    source: str
    date: str
    url: Optional[str] = None

class SentimentAnalysisResponse(BaseModel):
    symbol: str
    overall_sentiment: float
    confidence: float
    positive_count: int
    negative_count: int
    neutral_count: int
    total_articles: int
    sentiment_trend: str
    price_correlation: float
    recent_headlines: List[HeadlineData]
    last_updated: datetime

class AlertResponse(BaseModel):
    id: int
    symbol: str
    alert_type: str
    severity: str
    message: str
    threshold_value: Optional[float]
    current_value: Optional[float]
    is_active: bool
    triggered_at: datetime

class DashboardResponse(BaseModel):
    stocks: Dict[str, StockDataResponse]
    sentiment: Dict[str, SentimentAnalysisResponse]
    alerts: List[AlertResponse]
    summary: Dict[str, Any]

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    preferences: Optional[UserPreferences] = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    preferences: Optional[Dict[str, Any]]
    watchlist: Optional[List[str]]
    timezone: str
    currency_preference: str
    is_active: bool
    created_at: datetime

class NewsArticleResponse(BaseModel):
    id: int
    symbol: str
    title: str
    description: str
    source: str
    published_at: datetime
    sentiment_score: float
    sentiment_label: str
    url: Optional[str]

class MarketStatusResponse(BaseModel):
    indian_market: Dict[str, Any]
    us_market: Dict[str, Any]
    timestamp: datetime

class PopularStock(BaseModel):
    symbol: str
    name: str
    sector: str

class PopularStocksResponse(BaseModel):
    indian_stocks: List[PopularStock]
    us_stocks: List[PopularStock]