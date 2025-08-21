import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import asyncio
from data_fetcher import StockDataFetcher
from sentiment_analyzer import SentimentAnalyzer
from visualizations import create_price_chart, create_sentiment_heatmap, create_correlation_chart
from utils import get_stock_symbols, format_currency, calculate_alerts

# Page configuration
st.set_page_config(
    page_title="Stock Market Sentiment Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def init_components():
    stock_fetcher = StockDataFetcher()
    sentiment_analyzer = SentimentAnalyzer()
    return stock_fetcher, sentiment_analyzer

stock_fetcher, sentiment_analyzer = init_components()

# Sidebar configuration
st.sidebar.title("📈 Market Dashboard")
st.sidebar.markdown("---")

# Stock selection
st.sidebar.subheader("Stock Selection")
default_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "JPM"]
selected_stocks = st.sidebar.multiselect(
    "Select stocks to track:",
    options=get_stock_symbols(),
    default=default_symbols,
    help="Choose stocks to monitor for sentiment and price analysis"
)

# Refresh interval
refresh_interval = st.sidebar.selectbox(
    "Data refresh interval:",
    options=[5, 10, 15, 30],
    index=1,
    help="Minutes between automatic data updates"
)

# Analysis parameters
st.sidebar.subheader("Analysis Settings")
sentiment_threshold = st.sidebar.slider(
    "Sentiment Alert Threshold:",
    min_value=0.1,
    max_value=1.0,
    value=0.7,
    step=0.1,
    help="Trigger alerts when sentiment scores exceed this threshold"
)

lookback_days = st.sidebar.slider(
    "Historical Analysis Period (days):",
    min_value=1,
    max_value=30,
    value=7,
    help="Number of days to analyze for trends"
)

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("Auto-refresh data", value=True)

# Main dashboard
st.title("📈 Stock Market Sentiment & Impact Tracker")
st.markdown("Real-time stock analysis with news sentiment correlation and predictive insights")

# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📰 Sentiment Analysis", "🗺️ Sector Heatmap", "⚠️ Alerts"])

with tab1:
    st.header("Real-Time Market Dashboard")
    
    if not selected_stocks:
        st.warning("Please select at least one stock from the sidebar to begin analysis.")
        st.stop()
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Data containers
    stock_data_container = st.container()
    chart_container = st.container()
    
    # Initialize session state for data storage
    if 'stock_data' not in st.session_state:
        st.session_state.stock_data = {}
    if 'sentiment_data' not in st.session_state:
        st.session_state.sentiment_data = {}
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None

    # Data fetching function
    def fetch_and_update_data():
        try:
            with st.spinner("Fetching real-time data..."):
                # Fetch stock data
                stock_data = {}
                sentiment_data = {}
                
                progress_bar = st.progress(0)
                
                for i, symbol in enumerate(selected_stocks):
                    # Update progress
                    progress_bar.progress((i + 1) / len(selected_stocks))
                    
                    # Fetch stock data
                    stock_info = stock_fetcher.get_stock_data(symbol, lookback_days)
                    if stock_info:
                        stock_data[symbol] = stock_info
                        
                        # Fetch sentiment data for this stock
                        sentiment_info = sentiment_analyzer.analyze_stock_sentiment(symbol)
                        if sentiment_info:
                            sentiment_data[symbol] = sentiment_info
                
                progress_bar.empty()
                
                # Update session state
                st.session_state.stock_data = stock_data
                st.session_state.sentiment_data = sentiment_data
                st.session_state.last_update = datetime.now()
                
                return True
                
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            return False

    # Manual refresh button
    col_refresh1, col_refresh2, col_refresh3 = st.columns([1, 2, 1])
    with col_refresh2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            fetch_and_update_data()

    # Auto-refresh mechanism
    if auto_refresh and st.session_state.last_update:
        time_since_update = datetime.now() - st.session_state.last_update
        if time_since_update.total_seconds() > (refresh_interval * 60):
            fetch_and_update_data()

    # Initial data fetch if no data exists
    if not st.session_state.stock_data:
        fetch_and_update_data()

    # Display last update time
    if st.session_state.last_update:
        st.caption(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

    # Display stock data and charts
    if st.session_state.stock_data:
        # Market summary metrics
        with col1:
            total_stocks = len(st.session_state.stock_data)
            st.metric("Tracked Stocks", total_stocks)
        
        with col2:
            if st.session_state.sentiment_data:
                avg_sentiment = np.mean([data.get('overall_sentiment', 0) 
                                       for data in st.session_state.sentiment_data.values()])
                st.metric("Avg Sentiment", f"{avg_sentiment:.2f}", 
                         delta=f"{'Positive' if avg_sentiment > 0.5 else 'Negative'}")
        
        with col3:
            positive_stocks = sum(1 for data in st.session_state.sentiment_data.values() 
                                if data.get('overall_sentiment', 0) > 0.6)
            st.metric("Positive Sentiment", f"{positive_stocks}/{total_stocks}")
        
        with col4:
            market_alerts = calculate_alerts(st.session_state.sentiment_data, sentiment_threshold)
            st.metric("Active Alerts", len(market_alerts))

        # Stock price charts
        with chart_container:
            st.subheader("Stock Price Trends")
            
            # Create tabs for different chart views
            chart_tab1, chart_tab2 = st.tabs(["Individual Charts", "Comparison View"])
            
            with chart_tab1:
                # Individual stock charts
                for symbol in selected_stocks:
                    if symbol in st.session_state.stock_data:
                        stock_info = st.session_state.stock_data[symbol]
                        sentiment_info = st.session_state.sentiment_data.get(symbol, {})
                        
                        col_chart1, col_chart2 = st.columns([3, 1])
                        
                        with col_chart1:
                            # Price chart with sentiment overlay
                            fig = create_price_chart(stock_info, sentiment_info, symbol)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col_chart2:
                            # Stock metrics
                            current_price = stock_info['data']['Close'].iloc[-1]
                            prev_price = stock_info['data']['Close'].iloc[-2] if len(stock_info['data']) > 1 else current_price
                            price_change = current_price - prev_price
                            price_change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0
                            
                            st.metric(
                                f"{symbol} Price",
                                format_currency(current_price),
                                delta=f"{price_change_pct:.2f}%"
                            )
                            
                            if sentiment_info:
                                sentiment_score = sentiment_info.get('overall_sentiment', 0)
                                sentiment_label = "Positive" if sentiment_score > 0.6 else "Negative" if sentiment_score < 0.4 else "Neutral"
                                st.metric("Sentiment", f"{sentiment_score:.2f}", delta=sentiment_label)
                                
                                correlation = sentiment_info.get('price_correlation', 0)
                                st.metric("Price-Sentiment Correlation", f"{correlation:.2f}")
            
            with chart_tab2:
                # Comparison view
                if len(selected_stocks) > 1:
                    comparison_fig = create_correlation_chart(st.session_state.stock_data, st.session_state.sentiment_data)
                    st.plotly_chart(comparison_fig, use_container_width=True)
                else:
                    st.info("Select multiple stocks to view comparison charts.")

with tab2:
    st.header("📰 News Sentiment Analysis")
    
    if st.session_state.sentiment_data:
        # Overall sentiment distribution
        sentiment_scores = [data.get('overall_sentiment', 0) for data in st.session_state.sentiment_data.values()]
        labels = list(st.session_state.sentiment_data.keys())
        
        fig_sentiment = px.bar(
            x=labels,
            y=sentiment_scores,
            title="Stock Sentiment Scores",
            labels={'x': 'Stock Symbol', 'y': 'Sentiment Score'},
            color=sentiment_scores,
            color_continuous_scale='RdYlGn'
        )
        fig_sentiment.add_hline(y=0.5, line_dash="dash", line_color="gray", 
                               annotation_text="Neutral Threshold")
        st.plotly_chart(fig_sentiment, use_container_width=True)
        
        # Detailed sentiment breakdown
        st.subheader("Detailed Sentiment Analysis")
        
        for symbol in selected_stocks:
            if symbol in st.session_state.sentiment_data:
                sentiment_info = st.session_state.sentiment_data[symbol]
                
                with st.expander(f"{symbol} - Sentiment Details"):
                    col_sent1, col_sent2 = st.columns(2)
                    
                    with col_sent1:
                        st.metric("Overall Sentiment", f"{sentiment_info.get('overall_sentiment', 0):.2f}")
                        st.metric("Positive Articles", sentiment_info.get('positive_count', 0))
                        st.metric("Negative Articles", sentiment_info.get('negative_count', 0))
                    
                    with col_sent2:
                        st.metric("Neutral Articles", sentiment_info.get('neutral_count', 0))
                        st.metric("Total Articles Analyzed", sentiment_info.get('total_articles', 0))
                        
                        # Sentiment trend indicator
                        trend = sentiment_info.get('sentiment_trend', 'stable')
                        trend_emoji = "📈" if trend == "improving" else "📉" if trend == "declining" else "➡️"
                        st.metric("Sentiment Trend", f"{trend_emoji} {trend.title()}")
                    
                    # Recent headlines
                    if 'recent_headlines' in sentiment_info:
                        st.subheader("Recent Headlines")
                        for headline in sentiment_info['recent_headlines'][:5]:
                            sentiment_color = "green" if headline['sentiment'] > 0.6 else "red" if headline['sentiment'] < 0.4 else "orange"
                            st.markdown(f"**{headline['title']}**")
                            st.markdown(f"<span style='color: {sentiment_color}'>Sentiment: {headline['sentiment']:.2f}</span>", 
                                      unsafe_allow_html=True)
                            st.caption(f"Source: {headline.get('source', 'Unknown')} | {headline.get('date', 'Unknown date')}")
                            st.markdown("---")
    else:
        st.info("No sentiment data available. Please refresh the data from the main dashboard.")

with tab3:
    st.header("🗺️ Sector Sentiment Heatmap")
    
    if st.session_state.sentiment_data and st.session_state.stock_data:
        # Create sector heatmap
        heatmap_fig = create_sentiment_heatmap(st.session_state.stock_data, st.session_state.sentiment_data)
        st.plotly_chart(heatmap_fig, use_container_width=True)
        
        # Sector performance summary
        st.subheader("Sector Performance Summary")
        
        # Group stocks by sector (simplified mapping)
        sector_mapping = {
            'AAPL': 'Technology', 'GOOGL': 'Technology', 'MSFT': 'Technology', 'META': 'Technology', 'NVDA': 'Technology',
            'AMZN': 'Consumer Discretionary', 'TSLA': 'Consumer Discretionary',
            'JPM': 'Financial Services'
        }
        
        sector_data = {}
        for symbol in selected_stocks:
            if symbol in st.session_state.sentiment_data:
                sector = sector_mapping.get(symbol, 'Other')
                if sector not in sector_data:
                    sector_data[sector] = {'sentiment_scores': [], 'stocks': []}
                
                sentiment_score = st.session_state.sentiment_data[symbol].get('overall_sentiment', 0)
                sector_data[sector]['sentiment_scores'].append(sentiment_score)
                sector_data[sector]['stocks'].append(symbol)
        
        # Display sector summary
        for sector, data in sector_data.items():
            avg_sentiment = np.mean(data['sentiment_scores'])
            sentiment_status = "Positive" if avg_sentiment > 0.6 else "Negative" if avg_sentiment < 0.4 else "Neutral"
            
            with st.expander(f"{sector} Sector - {sentiment_status} ({avg_sentiment:.2f})"):
                col_sector1, col_sector2 = st.columns(2)
                
                with col_sector1:
                    st.metric("Average Sentiment", f"{avg_sentiment:.2f}")
                    st.metric("Stocks Tracked", len(data['stocks']))
                
                with col_sector2:
                    st.write("**Stocks in this sector:**")
                    for stock in data['stocks']:
                        stock_sentiment = st.session_state.sentiment_data[stock].get('overall_sentiment', 0)
                        st.write(f"• {stock}: {stock_sentiment:.2f}")
    else:
        st.info("No data available for sector analysis. Please refresh the data from the main dashboard.")

with tab4:
    st.header("⚠️ Predictive Alerts")
    
    if st.session_state.sentiment_data:
        # Calculate and display alerts
        alerts = calculate_alerts(st.session_state.sentiment_data, sentiment_threshold)
        
        if alerts:
            st.warning(f"🚨 {len(alerts)} Active Alert(s)")
            
            for alert in alerts:
                alert_type = alert['type']
                symbol = alert['symbol']
                message = alert['message']
                severity = alert['severity']
                
                # Choose alert color based on severity
                if severity == 'high':
                    st.error(f"🔴 **{alert_type.upper()}** - {symbol}: {message}")
                elif severity == 'medium':
                    st.warning(f"🟡 **{alert_type.upper()}** - {symbol}: {message}")
                else:
                    st.info(f"🔵 **{alert_type.upper()}** - {symbol}: {message}")
        else:
            st.success("✅ No active alerts. Market sentiment is within normal ranges.")
        
        # Alert configuration
        st.subheader("Alert Settings")
        
        col_alert1, col_alert2 = st.columns(2)
        
        with col_alert1:
            st.write("**Current Alert Criteria:**")
            st.write(f"• Sentiment threshold: {sentiment_threshold}")
            st.write(f"• Analysis period: {lookback_days} days")
            st.write(f"• Auto-refresh: {'Enabled' if auto_refresh else 'Disabled'}")
        
        with col_alert2:
            st.write("**Alert Types:**")
            st.write("• Extreme positive sentiment (>0.8)")
            st.write("• Extreme negative sentiment (<0.2)")
            st.write("• Rapid sentiment changes")
            st.write("• High price-sentiment correlation")
        
        # Historical alerts (placeholder for future implementation)
        st.subheader("Recent Alert History")
        st.info("Alert history feature will be available in future updates.")
        
    else:
        st.info("No sentiment data available for alert analysis. Please refresh the data from the main dashboard.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>📈 Stock Market Sentiment & Impact Tracker | Real-time analysis with predictive insights</p>
        <p>Data sources: Yahoo Finance, News APIs | Analysis powered by NLP sentiment processing</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Auto-refresh mechanism (runs every refresh_interval minutes)
if auto_refresh:
    time.sleep(refresh_interval * 60)
    st.rerun()
