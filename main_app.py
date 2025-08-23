"""
Enhanced Stock Market Sentiment Tracker - Full-stack Streamlit Application
Combines real-time stock data with sentiment analysis in a beginner-friendly interface
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.services.stock_service import StockService
    from backend.services.sentiment_service import SentimentService  
    from backend.services.alert_service import AlertService
except ImportError as e:
    st.error(f"Backend services not available: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Stock Market Sentiment Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .alert-high {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .alert-medium {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .alert-low {
        background-color: #f0f9ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .sentiment-positive {
        color: #16a34a;
        font-weight: bold;
    }
    .sentiment-negative {
        color: #dc2626;
        font-weight: bold;
    }
    .sentiment-neutral {
        color: #ca8a04;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def get_services():
    return {
        'stock': StockService(),
        'sentiment': SentimentService(),
        'alert': AlertService()
    }

services = get_services()

# Helper functions
def format_currency(amount, symbol):
    """Format currency in Indian Rupees"""
    if symbol.endswith('.NS'):
        return f"₹{amount:,.2f}"
    else:
        inr_amount = amount * 83
        return f"₹{inr_amount:,.2f}"

def get_sentiment_color(sentiment):
    """Get color based on sentiment score"""
    if sentiment > 0.6:
        return "#16a34a"  # Green
    elif sentiment < 0.4:
        return "#dc2626"  # Red
    else:
        return "#ca8a04"  # Yellow

def get_sentiment_label(sentiment):
    """Get sentiment label"""
    if sentiment > 0.7:
        return "Very Positive"
    elif sentiment > 0.6:
        return "Positive"
    elif sentiment > 0.4:
        return "Neutral"
    elif sentiment > 0.3:
        return "Negative"
    else:
        return "Very Negative"

# Main application
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📈 Stock Market Sentiment Tracker</h1>
        <p>Real-time Indian & US market analysis with news sentiment tracking in Indian Rupees (₹)</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar - Stock Selection
    st.sidebar.header("🎯 Stock Selection")
    
    # Popular stocks
    popular_indian = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "ITC.NS", "LT.NS",
        "WIPRO.NS", "BHARTIARTL.NS", "MARUTI.NS"
    ]
    
    popular_us = [
        "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA"
    ]

    # Stock selection
    st.sidebar.subheader("🇮🇳 Indian Stocks (NSE)")
    selected_indian = st.sidebar.multiselect(
        "Select Indian stocks:",
        popular_indian,
        default=["RELIANCE.NS", "TCS.NS"],
        key="indian_stocks"
    )

    st.sidebar.subheader("🇺🇸 US Stocks (NYSE/NASDAQ)")
    selected_us = st.sidebar.multiselect(
        "Select US stocks:",
        popular_us,
        default=["AAPL", "GOOGL"],
        key="us_stocks"
    )

    # Combine selections
    selected_stocks = selected_indian + selected_us

    if not selected_stocks:
        st.warning("Please select at least one stock from the sidebar to start tracking.")
        return

    # Settings
    st.sidebar.header("⚙️ Settings")
    lookback_days = st.sidebar.slider("Analysis Period (days)", 1, 30, 7)
    auto_refresh = st.sidebar.checkbox("Auto-refresh (5 min)", value=True)
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()

    # Market status
    st.sidebar.header("🕒 Market Status")
    now = datetime.now()
    indian_open = 9 <= now.hour < 15.5 and now.weekday() < 5
    us_open = (19 <= now.hour or now.hour < 2.5) and now.weekday() < 5
    
    st.sidebar.write(f"🇮🇳 NSE: {'🟢 Open' if indian_open else '🔴 Closed'}")
    st.sidebar.write(f"🇺🇸 NYSE: {'🟢 Open' if us_open else '🔴 Closed'}")
    st.sidebar.write(f"🕒 IST: {now.strftime('%H:%M:%S')}")

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💭 Sentiment Analysis", "📈 Price Charts", "🚨 Smart Alerts"])

    # Load data for selected stocks
    stock_data = {}
    sentiment_data = {}
    
    # Create loading placeholder
    loading_placeholder = st.empty()
    loading_placeholder.info("Loading market data and sentiment analysis... Please wait.")

    # Progress bar
    progress_bar = st.progress(0)
    
    for i, symbol in enumerate(selected_stocks):
        try:
            # Update progress
            progress_bar.progress((i + 1) / len(selected_stocks))
            
            # Get stock data
            stock_info = asyncio.run(services['stock'].get_stock_data(symbol, lookback_days))
            if stock_info:
                stock_data[symbol] = stock_info
            
            # Get sentiment data
            sentiment_info = asyncio.run(services['sentiment'].analyze_sentiment(symbol, lookback_days))
            if sentiment_info:
                sentiment_data[symbol] = sentiment_info
                
        except Exception as e:
            st.error(f"Error loading data for {symbol}: {str(e)}")
            continue

    # Clear loading indicators
    loading_placeholder.empty()
    progress_bar.empty()

    # Tab 1: Overview
    with tab1:
        st.header("📊 Market Overview")
        
        if not stock_data:
            st.error("No stock data available. Please check your internet connection and try again.")
            return
            
        # Create overview cards
        cols = st.columns(min(len(selected_stocks), 3))
        
        for i, (symbol, data) in enumerate(stock_data.items()):
            with cols[i % 3]:
                sentiment = sentiment_data.get(symbol)
                
                # Price change indicator
                change_color = "🟢" if data.price_change >= 0 else "🔴"
                change_symbol = "↗️" if data.price_change >= 0 else "↘️"
                
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{symbol} {change_color}</h3>
                    <h4>{data.name}</h4>
                    <h2>{format_currency(data.current_price, symbol)}</h2>
                    <p>{change_symbol} {data.price_change_pct:.2f}% ({format_currency(data.price_change, symbol)})</p>
                    <hr>
                    <small>Volume: {data.volume:,}</small><br>
                    <small>Market Cap: {data.market_cap}</small>
                    {f'<br><small>Sentiment: <span class="sentiment-{get_sentiment_label(sentiment.overall_sentiment).lower().replace(" ", "-")}">{get_sentiment_label(sentiment.overall_sentiment)}</span></small>' if sentiment else ''}
                </div>
                """, unsafe_allow_html=True)

        # Market summary
        st.subheader("📈 Market Summary")
        
        summary_cols = st.columns(4)
        with summary_cols[0]:
            total_gainers = sum(1 for data in stock_data.values() if data.price_change >= 0)
            st.metric("Gainers", total_gainers, f"{total_gainers}/{len(stock_data)}")
            
        with summary_cols[1]:
            total_losers = len(stock_data) - total_gainers
            st.metric("Losers", total_losers, f"{total_losers}/{len(stock_data)}")
            
        with summary_cols[2]:
            avg_sentiment = np.mean([s.overall_sentiment for s in sentiment_data.values()]) if sentiment_data else 0.5
            st.metric("Avg Sentiment", f"{avg_sentiment:.2f}", get_sentiment_label(avg_sentiment))
            
        with summary_cols[3]:
            total_articles = sum(s.total_articles for s in sentiment_data.values()) if sentiment_data else 0
            st.metric("News Articles", total_articles)

    # Tab 2: Sentiment Analysis
    with tab2:
        st.header("💭 Sentiment Analysis")
        
        if not sentiment_data:
            st.warning("No sentiment data available for selected stocks.")
            return
            
        for symbol, sentiment in sentiment_data.items():
            with st.expander(f"📰 {symbol} - {get_sentiment_label(sentiment.overall_sentiment)}", expanded=True):
                
                # Sentiment metrics
                sent_cols = st.columns(4)
                with sent_cols[0]:
                    st.metric("Overall Sentiment", f"{sentiment.overall_sentiment:.2f}")
                with sent_cols[1]:
                    st.metric("Confidence", f"{sentiment.confidence:.2f}")
                with sent_cols[2]:
                    st.metric("Total Articles", sentiment.total_articles)
                with sent_cols[3]:
                    st.metric("Trend", sentiment.sentiment_trend.title())
                
                # Sentiment distribution
                st.subheader("📊 Sentiment Distribution")
                
                dist_cols = st.columns(3)
                with dist_cols[0]:
                    st.success(f"Positive: {sentiment.positive_count}")
                with dist_cols[1]:
                    st.warning(f"Neutral: {sentiment.neutral_count}")
                with dist_cols[2]:
                    st.error(f"Negative: {sentiment.negative_count}")
                
                # Recent headlines
                st.subheader("📰 Recent Headlines")
                for headline in sentiment.recent_headlines[:5]:
                    sentiment_class = "positive" if headline.sentiment > 0.6 else "negative" if headline.sentiment < 0.4 else "neutral"
                    st.markdown(f"""
                    <div style="padding: 0.5rem; margin: 0.5rem 0; border-left: 3px solid {get_sentiment_color(headline.sentiment)}; background-color: #f8f9fa;">
                        <strong>{headline.title}</strong><br>
                        <small>📺 {headline.source} • 📅 {headline.date} • 💭 Sentiment: {headline.sentiment:.2f}</small>
                    </div>
                    """, unsafe_allow_html=True)

    # Tab 3: Price Charts
    with tab3:
        st.header("📈 Price Charts")
        
        for symbol, data in stock_data.items():
            if not data.historical_data:
                continue
                
            st.subheader(f"📊 {symbol} - {data.name}")
            
            # Convert historical data to DataFrame
            df = pd.DataFrame(data.historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df['price_inr'] = df['close'] if symbol.endswith('.NS') else df['close'] * 83
            
            # Create candlestick chart
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Price (₹)", "Volume"),
                vertical_spacing=0.1,
                row_heights=[0.7, 0.3]
            )
            
            # Candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=df['date'],
                    open=df['open'] if symbol.endswith('.NS') else df['open'] * 83,
                    high=df['high'] if symbol.endswith('.NS') else df['high'] * 83,
                    low=df['low'] if symbol.endswith('.NS') else df['low'] * 83,
                    close=df['price_inr'],
                    name="Price"
                ),
                row=1, col=1
            )
            
            # Volume chart
            fig.add_trace(
                go.Bar(
                    x=df['date'],
                    y=df['volume'],
                    name="Volume",
                    marker_color='lightblue'
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title=f"{symbol} Price & Volume",
                xaxis_rangeslider_visible=False,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Technical indicators
            if data.ma_5 and data.ma_20:
                st.write(f"🔍 **Technical Indicators:**")
                tech_cols = st.columns(3)
                with tech_cols[0]:
                    st.metric("5-day MA", format_currency(data.ma_5, symbol))
                with tech_cols[1]:
                    st.metric("20-day MA", format_currency(data.ma_20, symbol))
                with tech_cols[2]:
                    if data.rsi:
                        rsi_color = "🟢" if 30 <= data.rsi <= 70 else "🔴"
                        st.metric("RSI", f"{data.rsi:.1f} {rsi_color}")

    # Tab 4: Smart Alerts
    with tab4:
        st.header("🚨 Smart Alerts")
        
        # Generate alerts
        try:
            alerts = asyncio.run(services['alert'].generate_alerts(sentiment_data))
            
            if not alerts:
                st.success("✅ All monitored stocks are performing normally. No alerts at this time.")
                return
                
            # Alert summary
            alert_counts = {'high': 0, 'medium': 0, 'low': 0}
            for alert in alerts:
                alert_counts[alert.severity] += 1
            
            st.subheader("📊 Alert Summary")
            alert_cols = st.columns(3)
            with alert_cols[0]:
                st.error(f"🔴 High Priority: {alert_counts['high']}")
            with alert_cols[1]:
                st.warning(f"🟡 Medium Priority: {alert_counts['medium']}")
            with alert_cols[2]:
                st.info(f"🔵 Low Priority: {alert_counts['low']}")
            
            # Display alerts
            st.subheader("🚨 Active Alerts")
            
            for alert in alerts:
                alert_class = f"alert-{alert.severity}"
                icon_map = {
                    'sentiment': '💭',
                    'trend': '📈',
                    'volume': '📢',
                    'correlation': '🔗',
                    'distribution': '📊'
                }
                icon = icon_map.get(alert.alert_type, '⚠️')
                
                st.markdown(f"""
                <div class="{alert_class}">
                    <h4>{icon} {alert.symbol} - {alert.severity.upper()} ALERT</h4>
                    <p><strong>Type:</strong> {alert.alert_type.replace('_', ' ').title()}</p>
                    <p><strong>Message:</strong> {alert.message}</p>
                    <p><small>🕒 {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S IST')}</small></p>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error generating alerts: {str(e)}")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9em;">
        <p>📊 Data updated every 15 minutes during market hours • 💱 All prices in Indian Rupees (₹)</p>
        <p>🇮🇳 Indian markets: NSE/BSE • 🇺🇸 US markets: NYSE/NASDAQ • 🕒 Timezone: Asia/Kolkata (IST)</p>
    </div>
    """, unsafe_allow_html=True)

    # Auto-refresh
    if auto_refresh:
        import time
        time.sleep(300)  # 5 minutes
        st.rerun()

if __name__ == "__main__":
    main()