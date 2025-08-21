import pandas as pd
import numpy as np
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from data_fetcher import StockDataFetcher

class SentimentAnalyzer:
    """Handles news sentiment analysis using multiple NLP approaches."""
    
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.stock_fetcher = StockDataFetcher()
        
    def analyze_stock_sentiment(self, symbol: str, days: int = 7) -> Optional[Dict[str, Any]]:
        """
        Analyze sentiment for a specific stock using news articles.
        
        Args:
            symbol (str): Stock symbol
            days (int): Number of days to analyze
            
        Returns:
            Dict containing sentiment analysis results
        """
        try:
            # Fetch news articles
            articles = self.stock_fetcher.get_news_data(symbol, days)
            
            if not articles:
                return {
                    'overall_sentiment': 0.5,
                    'confidence': 0.0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0,
                    'total_articles': 0,
                    'sentiment_trend': 'stable',
                    'recent_headlines': [],
                    'price_correlation': 0.0
                }
            
            # Analyze each article
            analyzed_articles = []
            for article in articles:
                sentiment_data = self._analyze_article_sentiment(article)
                if sentiment_data:
                    analyzed_articles.append(sentiment_data)
            
            if not analyzed_articles:
                return None
            
            # Calculate overall sentiment metrics
            sentiment_scores = [article['compound_score'] for article in analyzed_articles]
            overall_sentiment = np.mean(sentiment_scores)
            confidence = np.std(sentiment_scores)
            
            # Normalize overall sentiment to 0-1 scale
            normalized_sentiment = (overall_sentiment + 1) / 2
            
            # Count sentiment categories
            positive_count = sum(1 for score in sentiment_scores if score > 0.05)
            negative_count = sum(1 for score in sentiment_scores if score < -0.05)
            neutral_count = len(sentiment_scores) - positive_count - negative_count
            
            # Calculate sentiment trend
            sentiment_trend = self._calculate_sentiment_trend(analyzed_articles)
            
            # Get price correlation
            price_correlation = self._calculate_price_sentiment_correlation(symbol, analyzed_articles, days)
            
            # Prepare recent headlines for display
            recent_headlines = []
            for article in analyzed_articles[:10]:  # Top 10 most recent
                recent_headlines.append({
                    'title': article['title'],
                    'sentiment': (article['compound_score'] + 1) / 2,  # Normalize to 0-1
                    'source': article['source'],
                    'date': article['published_at']
                })
            
            return {
                'overall_sentiment': normalized_sentiment,
                'confidence': 1 - min(float(confidence), 1.0),  # Convert std to confidence
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'total_articles': len(analyzed_articles),
                'sentiment_trend': sentiment_trend,
                'recent_headlines': recent_headlines,
                'price_correlation': price_correlation,
                'raw_scores': sentiment_scores
            }
            
        except Exception as e:
            st.error(f"Error analyzing sentiment for {symbol}: {str(e)}")
            return None
    
    def _analyze_article_sentiment(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze sentiment of a single article using multiple methods."""
        try:
            # Combine title and description for analysis
            text = f"{article.get('title', '')} {article.get('description', '')}"
            
            if not text.strip():
                return None
            
            # Clean text
            cleaned_text = self._clean_text(text)
            
            # VADER sentiment analysis
            vader_scores = self.vader_analyzer.polarity_scores(cleaned_text)
            
            # TextBlob sentiment analysis
            blob = TextBlob(cleaned_text)
            sentiment = blob.sentiment
            textblob_polarity = sentiment.polarity
            textblob_subjectivity = sentiment.subjectivity
            
            # Combine scores (weighted average)
            compound_score = (vader_scores['compound'] * 0.7) + (textblob_polarity * 0.3)
            
            return {
                'title': article.get('title', ''),
                'source': article.get('source', ''),
                'published_at': article.get('published_at', ''),
                'vader_compound': vader_scores['compound'],
                'vader_positive': vader_scores['pos'],
                'vader_negative': vader_scores['neg'],
                'vader_neutral': vader_scores['neu'],
                'textblob_polarity': textblob_polarity,
                'textblob_subjectivity': textblob_subjectivity,
                'compound_score': compound_score,
                'text_length': len(cleaned_text)
            }
            
        except Exception as e:
            st.warning(f"Error analyzing article sentiment: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text for sentiment analysis."""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.,!?;:]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _calculate_sentiment_trend(self, analyzed_articles: List[Dict[str, Any]]) -> str:
        """Calculate the trend in sentiment over time."""
        try:
            # Sort articles by date
            sorted_articles = sorted(analyzed_articles, 
                                   key=lambda x: x.get('published_at', ''))
            
            if len(sorted_articles) < 3:
                return 'stable'
            
            # Split into recent and older articles
            mid_point = len(sorted_articles) // 2
            older_scores = [article['compound_score'] for article in sorted_articles[:mid_point]]
            recent_scores = [article['compound_score'] for article in sorted_articles[mid_point:]]
            
            older_avg = np.mean(older_scores)
            recent_avg = np.mean(recent_scores)
            
            # Calculate trend
            difference = recent_avg - older_avg
            
            if difference > 0.1:
                return 'improving'
            elif difference < -0.1:
                return 'declining'
            else:
                return 'stable'
                
        except Exception as e:
            st.warning(f"Error calculating sentiment trend: {str(e)}")
            return 'stable'
    
    def _calculate_price_sentiment_correlation(self, symbol: str, analyzed_articles: List[Dict[str, Any]], days: int) -> float:
        """Calculate correlation between sentiment scores and price movements."""
        try:
            # Get stock price data
            stock_data = self.stock_fetcher.get_stock_data(symbol, days)
            if not stock_data or stock_data['data'].empty:
                return 0.0
            
            price_data = stock_data['data']['Close']
            
            # Calculate daily price changes
            price_changes = price_data.pct_change().dropna()
            
            if len(price_changes) < 2:
                return 0.0
            
            # Group sentiment by date
            daily_sentiment = {}
            for article in analyzed_articles:
                try:
                    pub_date = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
                    date_key = pub_date.date()
                    
                    if date_key not in daily_sentiment:
                        daily_sentiment[date_key] = []
                    daily_sentiment[date_key].append(article['compound_score'])
                except:
                    continue
            
            # Calculate average sentiment per day
            avg_daily_sentiment = {}
            for date, scores in daily_sentiment.items():
                avg_daily_sentiment[date] = np.mean(scores)
            
            if len(avg_daily_sentiment) < 2:
                return 0.0
            
            # Align sentiment with price data
            aligned_sentiment = []
            aligned_prices = []
            
            for date in avg_daily_sentiment.keys():
                date_str = date.strftime('%Y-%m-%d')
                if date_str in price_changes.index.strftime('%Y-%m-%d'):
                    aligned_sentiment.append(avg_daily_sentiment[date])
                    price_idx = price_changes.index[price_changes.index.strftime('%Y-%m-%d') == date_str][0]
                    aligned_prices.append(price_changes[price_idx])
            
            if len(aligned_sentiment) < 2:
                return 0.0
            
            # Calculate correlation
            correlation = np.corrcoef(aligned_sentiment, aligned_prices)[0, 1]
            
            # Handle NaN values
            if np.isnan(correlation):
                return 0.0
            
            return correlation
            
        except Exception as e:
            st.warning(f"Error calculating price-sentiment correlation: {str(e)}")
            return 0.0
    
    def analyze_market_sentiment(self, symbols: List[str]) -> Dict[str, Any]:
        """Analyze overall market sentiment across multiple stocks."""
        try:
            all_sentiments = []
            stock_sentiments = {}
            
            for symbol in symbols:
                sentiment_data = self.analyze_stock_sentiment(symbol)
                if sentiment_data:
                    stock_sentiments[symbol] = sentiment_data
                    all_sentiments.append(sentiment_data['overall_sentiment'])
            
            if not all_sentiments:
                return {
                    'overall_market_sentiment': 0.5,
                    'market_confidence': 0.0,
                    'bullish_stocks': 0,
                    'bearish_stocks': 0,
                    'neutral_stocks': 0
                }
            
            # Calculate market-wide metrics
            overall_sentiment = np.mean(all_sentiments)
            market_confidence = 1 - np.std(all_sentiments)
            
            # Count sentiment categories
            bullish_stocks = sum(1 for sentiment in all_sentiments if sentiment > 0.6)
            bearish_stocks = sum(1 for sentiment in all_sentiments if sentiment < 0.4)
            neutral_stocks = len(all_sentiments) - bullish_stocks - bearish_stocks
            
            return {
                'overall_market_sentiment': overall_sentiment,
                'market_confidence': max(0.0, float(market_confidence)),
                'bullish_stocks': bullish_stocks,
                'bearish_stocks': bearish_stocks,
                'neutral_stocks': neutral_stocks,
                'stock_sentiments': stock_sentiments
            }
            
        except Exception as e:
            st.error(f"Error analyzing market sentiment: {str(e)}")
            return {}
