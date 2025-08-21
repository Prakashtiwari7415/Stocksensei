import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

def get_stock_symbols() -> List[str]:
    """
    Return a list of popular stock symbols for selection.
    
    Returns:
        List of stock symbols
    """
    return [
        # Technology
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX', 'ADBE', 'CRM',
        'ORCL', 'INTC', 'AMD', 'PYPL', 'SHOP', 'SQ', 'ZOOM', 'DOCU', 'TWLO', 'OKTA',
        
        # Financial Services
        'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'USB',
        
        # Healthcare
        'JNJ', 'PFE', 'UNH', 'ABT', 'TMO', 'DHR', 'BMY', 'ABBV', 'MRK', 'GILD',
        
        # Consumer
        'KO', 'PEP', 'PG', 'WMT', 'HD', 'MCD', 'DIS', 'NKE', 'SBUX', 'TGT',
        
        # Energy
        'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC', 'KMI', 'OKE',
        
        # Industrial
        'BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'FDX', 'RTX', 'LMT', 'NOC'
    ]

def format_currency(amount: float, currency: str = 'INR') -> str:
    """
    Format a number as currency.
    
    Args:
        amount: The amount to format
        currency: Currency code (default: INR)
        
    Returns:
        Formatted currency string
    """
    try:
        if currency == 'INR':
            # Convert USD to INR (approximate rate: 1 USD = 83 INR)
            inr_amount = amount * 83
            return f"₹{inr_amount:,.2f}"
        elif currency == 'USD':
            return f"${amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"
    except:
        return str(amount)

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format a number as a percentage.
    
    Args:
        value: The value to format
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    try:
        return f"{value:.{decimal_places}f}%"
    except:
        return str(value)

def format_large_number(number: float) -> str:
    """
    Format large numbers with K, M, B suffixes.
    
    Args:
        number: The number to format
        
    Returns:
        Formatted number string
    """
    try:
        if abs(number) >= 1e12:
            return f"{number/1e12:.1f}T"
        elif abs(number) >= 1e9:
            return f"{number/1e9:.1f}B"
        elif abs(number) >= 1e6:
            return f"{number/1e6:.1f}M"
        elif abs(number) >= 1e3:
            return f"{number/1e3:.1f}K"
        else:
            return f"{number:.0f}"
    except:
        return str(number)

def calculate_alerts(sentiment_data: Dict[str, Any], threshold: float = 0.7) -> List[Dict[str, Any]]:
    """
    Calculate alerts based on sentiment analysis results.
    
    Args:
        sentiment_data: Dictionary of sentiment data for multiple stocks
        threshold: Sentiment threshold for alerts
        
    Returns:
        List of alert dictionaries
    """
    alerts = []
    
    try:
        for symbol, data in sentiment_data.items():
            overall_sentiment = data.get('overall_sentiment', 0.5)
            confidence = data.get('confidence', 0.0)
            sentiment_trend = data.get('sentiment_trend', 'stable')
            price_correlation = data.get('price_correlation', 0.0)
            
            # Extreme sentiment alerts
            if overall_sentiment > 0.8:
                alerts.append({
                    'symbol': symbol,
                    'type': 'sentiment',
                    'severity': 'high',
                    'message': f'Extremely positive sentiment detected ({overall_sentiment:.2f})'
                })
            elif overall_sentiment < 0.2:
                alerts.append({
                    'symbol': symbol,
                    'type': 'sentiment',
                    'severity': 'high',
                    'message': f'Extremely negative sentiment detected ({overall_sentiment:.2f})'
                })
            
            # Moderate sentiment alerts
            elif overall_sentiment > threshold:
                alerts.append({
                    'symbol': symbol,
                    'type': 'sentiment',
                    'severity': 'medium',
                    'message': f'High positive sentiment ({overall_sentiment:.2f})'
                })
            elif overall_sentiment < (1 - threshold):
                alerts.append({
                    'symbol': symbol,
                    'type': 'sentiment',
                    'severity': 'medium',
                    'message': f'High negative sentiment ({overall_sentiment:.2f})'
                })
            
            # Trend alerts
            if sentiment_trend == 'improving' and overall_sentiment > 0.6:
                alerts.append({
                    'symbol': symbol,
                    'type': 'trend',
                    'severity': 'medium',
                    'message': 'Improving sentiment trend detected'
                })
            elif sentiment_trend == 'declining' and overall_sentiment < 0.4:
                alerts.append({
                    'symbol': symbol,
                    'type': 'trend',
                    'severity': 'medium',
                    'message': 'Declining sentiment trend detected'
                })
            
            # Correlation alerts
            if abs(price_correlation) > 0.7:
                alerts.append({
                    'symbol': symbol,
                    'type': 'correlation',
                    'severity': 'low',
                    'message': f'High price-sentiment correlation detected ({price_correlation:.2f})'
                })
            
            # Confidence alerts
            if confidence < 0.3 and data.get('total_articles', 0) > 5:
                alerts.append({
                    'symbol': symbol,
                    'type': 'confidence',
                    'severity': 'low',
                    'message': f'Low sentiment confidence with mixed signals'
                })
        
        # Sort alerts by severity
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        return alerts
        
    except Exception as e:
        st.error(f"Error calculating alerts: {str(e)}")
        return []

def calculate_portfolio_metrics(stock_data: Dict[str, Any], sentiment_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate portfolio-level metrics from individual stock data.
    
    Args:
        stock_data: Dictionary of stock data for multiple symbols
        sentiment_data: Dictionary of sentiment data for multiple symbols
        
    Returns:
        Dictionary of portfolio metrics
    """
    try:
        if not stock_data or not sentiment_data:
            return {}
        
        # Extract metrics
        price_changes = []
        sentiment_scores = []
        volumes = []
        correlations = []
        
        for symbol in stock_data.keys():
            if symbol in sentiment_data:
                price_changes.append(stock_data[symbol]['price_change_pct'])
                sentiment_scores.append(sentiment_data[symbol]['overall_sentiment'])
                volumes.append(stock_data[symbol]['volume'])
                correlations.append(sentiment_data[symbol].get('price_correlation', 0))
        
        if not price_changes:
            return {}
        
        # Calculate portfolio metrics
        portfolio_return = np.mean(price_changes)
        portfolio_volatility = np.std(price_changes)
        portfolio_sentiment = np.mean(sentiment_scores)
        sentiment_volatility = np.std(sentiment_scores)
        avg_correlation = np.mean(correlations)
        total_volume = sum(volumes)
        
        # Risk-adjusted metrics
        sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
        sentiment_risk_ratio = portfolio_sentiment / sentiment_volatility if sentiment_volatility > 0 else 0
        
        return {
            'portfolio_return': float(portfolio_return),
            'portfolio_volatility': float(portfolio_volatility),
            'portfolio_sentiment': float(portfolio_sentiment),
            'sentiment_volatility': float(sentiment_volatility),
            'avg_correlation': float(avg_correlation),
            'total_volume': float(total_volume),
            'sharpe_ratio': float(sharpe_ratio),
            'sentiment_risk_ratio': float(sentiment_risk_ratio),
            'num_stocks': len(price_changes)
        }
        
    except Exception as e:
        st.error(f"Error calculating portfolio metrics: {str(e)}")
        return {}

def get_market_status() -> Dict[str, Any]:
    """
    Determine current market status (open/closed) and next market events.
    
    Returns:
        Dictionary with market status information
    """
    try:
        now = datetime.now()
        
        # US market hours (EST): 9:30 AM - 4:00 PM, Monday-Friday
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        # Check if it's a weekday
        is_weekday = now.weekday() < 5
        
        # Check if market is open
        is_market_open = (is_weekday and 
                         market_open <= now <= market_close)
        
        # Calculate next market event
        if is_market_open:
            next_event = "Market Close"
            next_event_time = market_close
        elif is_weekday and now < market_open:
            next_event = "Market Open"
            next_event_time = market_open
        else:
            # Find next Monday
            days_until_monday = (7 - now.weekday()) % 7
            if days_until_monday == 0:  # Today is Monday but market is closed
                days_until_monday = 7
            next_monday = now + timedelta(days=days_until_monday)
            next_event = "Market Open"
            next_event_time = next_monday.replace(hour=9, minute=30, second=0, microsecond=0)
        
        time_until_next = next_event_time - now
        
        return {
            'is_open': is_market_open,
            'next_event': next_event,
            'next_event_time': next_event_time,
            'time_until_next': time_until_next,
            'status_text': "🟢 Market Open" if is_market_open else "🔴 Market Closed"
        }
        
    except Exception as e:
        st.error(f"Error getting market status: {str(e)}")
        return {
            'is_open': False,
            'next_event': 'Unknown',
            'status_text': '❓ Status Unknown'
        }

def validate_stock_symbol(symbol: str) -> bool:
    """
    Validate if a stock symbol is properly formatted.
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Basic validation: 1-5 uppercase letters
    symbol = symbol.strip().upper()
    return len(symbol) >= 1 and len(symbol) <= 5 and symbol.isalpha()

def create_download_data(stock_data: Dict[str, Any], sentiment_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Create a downloadable DataFrame with combined stock and sentiment data.
    
    Args:
        stock_data: Dictionary of stock data for multiple symbols
        sentiment_data: Dictionary of sentiment data for multiple symbols
        
    Returns:
        Pandas DataFrame ready for download
    """
    try:
        records = []
        
        for symbol in stock_data.keys():
            if symbol in sentiment_data:
                stock_info = stock_data[symbol]
                sentiment_info = sentiment_data[symbol]
                
                record = {
                    'Symbol': symbol,
                    'Current_Price': stock_info['current_price'],
                    'Price_Change_Pct': stock_info['price_change_pct'],
                    'Volume': stock_info['volume'],
                    'Market_Cap': stock_info.get('market_cap', 'N/A'),
                    'PE_Ratio': stock_info.get('pe_ratio', 'N/A'),
                    'Sector': stock_info.get('sector', 'Unknown'),
                    'Overall_Sentiment': sentiment_info['overall_sentiment'],
                    'Sentiment_Confidence': sentiment_info['confidence'],
                    'Positive_Articles': sentiment_info['positive_count'],
                    'Negative_Articles': sentiment_info['negative_count'],
                    'Neutral_Articles': sentiment_info['neutral_count'],
                    'Total_Articles': sentiment_info['total_articles'],
                    'Sentiment_Trend': sentiment_info['sentiment_trend'],
                    'Price_Correlation': sentiment_info['price_correlation'],
                    'Last_Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                records.append(record)
        
        return pd.DataFrame(records)
        
    except Exception as e:
        st.error(f"Error creating download data: {str(e)}")
        return pd.DataFrame()
