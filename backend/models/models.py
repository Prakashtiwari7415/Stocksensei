"""
SQLAlchemy models for the Stock Market Sentiment Tracker
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from database.database import Base

class StockData(Base):
    __tablename__ = "stock_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    name = Column(String(100))
    sector = Column(String(50))
    current_price = Column(Float)
    price_change = Column(Float)
    price_change_pct = Column(Float)
    volume = Column(Integer)
    market_cap = Column(String(20))
    pe_ratio = Column(Float)
    ma_5 = Column(Float)
    ma_20 = Column(Float)
    rsi = Column(Float)
    volatility = Column(Float)
    historical_data = Column(JSON)  # Store OHLCV data as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SentimentData(Base):
    __tablename__ = "sentiment_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    overall_sentiment = Column(Float)
    confidence = Column(Float)
    positive_count = Column(Integer)
    negative_count = Column(Integer)
    neutral_count = Column(Integer)
    total_articles = Column(Integer)
    sentiment_trend = Column(String(20))
    price_correlation = Column(Float)
    recent_headlines = Column(JSON)  # Store headlines as JSON array
    articles_analyzed = Column(JSON)  # Store full article analysis
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AlertData(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    alert_type = Column(String(20))  # sentiment, trend, volume, correlation
    severity = Column(String(10))    # high, medium, low
    message = Column(Text)
    threshold_value = Column(Float)
    current_value = Column(Float)
    is_active = Column(Boolean, default=True)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    name = Column(String(100))
    preferences = Column(JSON)  # Store user preferences as JSON
    watchlist = Column(JSON)    # Store user's stock watchlist
    alert_settings = Column(JSON)  # Store alert preferences
    timezone = Column(String(50), default="Asia/Kolkata")
    currency_preference = Column(String(5), default="INR")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    title = Column(String(500))
    description = Column(Text)
    content = Column(Text)
    url = Column(String(500))
    source = Column(String(100))
    author = Column(String(100))
    published_at = Column(DateTime(timezone=True))
    sentiment_score = Column(Float)
    sentiment_label = Column(String(20))  # positive, negative, neutral
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MarketIndex(Base):
    __tablename__ = "market_indices"
    
    id = Column(Integer, primary_key=True, index=True)
    index_name = Column(String(50))  # SENSEX, NIFTY, S&P500, etc.
    current_value = Column(Float)
    change_value = Column(Float)
    change_percent = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Integer)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())