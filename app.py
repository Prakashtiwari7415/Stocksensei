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

# Custom CSS for better beginner experience
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
    }
    .positive { color: #4CAF50; }
    .negative { color: #f44336; }
    .neutral { color: #ff9800; }
    .info-box {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2196F3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def init_components():
    stock_fetcher = StockDataFetcher()
    sentiment_analyzer = SentimentAnalyzer()
    return stock_fetcher, sentiment_analyzer

stock_fetcher, sentiment_analyzer = init_components()

# Sidebar configuration
st.sidebar.title("📈 Easy Stock Tracker")
st.sidebar.markdown("### Choose Your Settings")

# Add helpful info box
st.sidebar.markdown("""
<div class="info-box">
<strong>💡 How it works:</strong><br>
• Pick stocks you want to watch<br>
• See if people are talking positively or negatively about them<br>
• Watch price changes in Indian Rupees
</div>
""", unsafe_allow_html=True)

# Stock selection with Indian companies included
st.sidebar.subheader("📊 Pick Stocks to Watch")
indian_stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFC.NS", "WIPRO.NS", "LT.NS", "BHARTIARTL.NS", "MARUTI.NS"]
us_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA"]
default_symbols = indian_stocks[:4] + us_stocks[:4]

all_stocks = indian_stocks + us_stocks
selected_stocks = st.sidebar.multiselect(
    "Choose stocks:",
    options=all_stocks,
    default=default_symbols,
    help="Pick stocks you want to track. Indian stocks end with .NS"
)

# Simplified settings
st.sidebar.subheader("⚙️ Simple Settings")

# Refresh interval with simple options
refresh_interval = st.sidebar.selectbox(
    "How often to update data:",
    options=[5, 15, 30],
    index=1,
    format_func=lambda x: f"Every {x} minutes",
    help="How often to get fresh data"
)

# Simplified analysis period
lookback_days = st.sidebar.selectbox(
    "How many days to look back:",
    options=[3, 7, 14],
    index=1,
    format_func=lambda x: f"{x} days",
    help="How far back to check news and trends"
)

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("📱 Auto-update data", value=True, help="Automatically refresh data")

# Set a default sentiment threshold for beginners
sentiment_threshold = 0.7

# Main dashboard with simplified header
st.markdown("""
<div class="main-header">
    <h1>📈 Stock Market Sentiment Tracker</h1>
    <p>See what people think about stocks and how prices are moving (in Indian Rupees ₹)</p>
</div>
""", unsafe_allow_html=True)

# Create simplified tabs
tab1, tab2, tab3 = st.tabs(["📊 Main Dashboard", "📰 News Feelings", "⚠️ Alerts"])

with tab1:
    st.header("📊 Your Stock Dashboard")
    
    if not selected_stocks:
        st.markdown("""
        <div class="info-box">
        <strong>👋 Welcome!</strong><br>
        Please pick some stocks from the sidebar to start tracking them.
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    # Create columns for simple metrics
    col1, col2, col3 = st.columns(3)
    
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
        # Simple metrics for beginners
        with col1:
            total_stocks = len(st.session_state.stock_data)
            st.metric("📊 Stocks Watching", total_stocks)
        
        with col2:
            if st.session_state.sentiment_data:
                avg_sentiment = np.mean([data.get('overall_sentiment', 0) 
                                       for data in st.session_state.sentiment_data.values()])
                sentiment_emoji = "😊" if avg_sentiment > 0.6 else "😐" if avg_sentiment > 0.4 else "😟"
                st.metric("Overall Mood", f"{sentiment_emoji} {avg_sentiment:.1f}/1.0")
        
        with col3:
            market_alerts = calculate_alerts(st.session_state.sentiment_data, sentiment_threshold)
            alert_emoji = "🚨" if len(market_alerts) > 0 else "✅"
            st.metric("Alerts", f"{alert_emoji} {len(market_alerts)}")

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
                            # Simple stock metrics in Indian Rupees
                            current_price = stock_info['data']['Close'].iloc[-1]
                            prev_price = stock_info['data']['Close'].iloc[-2] if len(stock_info['data']) > 1 else current_price
                            price_change = current_price - prev_price
                            price_change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0
                            
                            # Clean symbol name for display
                            display_symbol = symbol.replace('.NS', ' (India)')
                            
                            st.metric(
                                f"💰 {display_symbol}",
                                format_currency(current_price),
                                delta=f"{price_change_pct:.1f}%"
                            )
                            
                            if sentiment_info:
                                sentiment_score = sentiment_info.get('overall_sentiment', 0)
                                if sentiment_score > 0.6:
                                    sentiment_display = "😊 Good"
                                elif sentiment_score > 0.4:
                                    sentiment_display = "😐 Okay"
                                else:
                                    sentiment_display = "😟 Poor"
                                st.metric("🗞️ News Mood", sentiment_display)
            
            with chart_tab2:
                # Comparison view
                if len(selected_stocks) > 1:
                    comparison_fig = create_correlation_chart(st.session_state.stock_data, st.session_state.sentiment_data)
                    st.plotly_chart(comparison_fig, use_container_width=True)
                else:
                    st.info("Select multiple stocks to view comparison charts.")

with tab2:
    st.header("📰 What People Are Saying")
    
    st.markdown("""
    <div class="info-box">
    <strong>💡 What this shows:</strong><br>
    • We read news articles about your stocks<br>
    • We check if the news sounds positive or negative<br>
    • This helps predict if stock prices might go up or down
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.sentiment_data:
        # Simple sentiment display
        st.subheader("📊 Overall News Mood")
        
        sentiment_scores = [data.get('overall_sentiment', 0) for data in st.session_state.sentiment_data.values()]
        labels = [symbol.replace('.NS', ' (India)') for symbol in st.session_state.sentiment_data.keys()]
        
        # Create simple chart
        fig_sentiment = px.bar(
            x=labels,
            y=sentiment_scores,
            title="How People Feel About Each Stock",
            labels={'x': 'Stock', 'y': 'Positive Feeling (0 = Bad, 1 = Good)'},
            color=sentiment_scores,
            color_continuous_scale='RdYlGn'
        )
        fig_sentiment.add_hline(y=0.5, line_dash="dash", line_color="gray", 
                               annotation_text="Neutral (Neither Good nor Bad)")
        st.plotly_chart(fig_sentiment, use_container_width=True)
        
        # Simple stock details
        st.subheader("📈 Individual Stock Details")
        
        for symbol in selected_stocks:
            if symbol in st.session_state.sentiment_data:
                sentiment_info = st.session_state.sentiment_data[symbol]
                display_name = symbol.replace('.NS', ' (India)')
                
                with st.expander(f"📊 {display_name} Details"):
                    col_sent1, col_sent2 = st.columns(2)
                    
                    with col_sent1:
                        mood = sentiment_info.get('overall_sentiment', 0)
                        if mood > 0.6:
                            mood_text = "😊 People are happy about this stock"
                        elif mood > 0.4:
                            mood_text = "😐 People feel okay about this stock"
                        else:
                            mood_text = "😟 People are worried about this stock"
                        st.write(f"**Overall Mood:** {mood_text}")
                        st.write(f"**Good News:** {sentiment_info.get('positive_count', 0)} articles")
                        st.write(f"**Bad News:** {sentiment_info.get('negative_count', 0)} articles")
                    
                    with col_sent2:
                        st.write(f"**Neutral News:** {sentiment_info.get('neutral_count', 0)} articles")
                        total_articles = sentiment_info.get('total_articles', 0)
                        st.write(f"**Total Articles:** {total_articles}")
                        
                        # Simple trend
                        trend = sentiment_info.get('sentiment_trend', 'stable')
                        if trend == "improving":
                            trend_text = "📈 Getting better!"
                        elif trend == "declining":
                            trend_text = "📉 Getting worse"
                        else:
                            trend_text = "➡️ Staying same"
                        st.write(f"**Trend:** {trend_text}")
                    
                    # Recent headlines (simplified)
                    if 'recent_headlines' in sentiment_info and sentiment_info['recent_headlines']:
                        st.write("**📰 Recent News:**")
                        for i, headline in enumerate(sentiment_info['recent_headlines'][:3], 1):
                            sentiment_value = headline['sentiment']
                            if sentiment_value > 0.6:
                                sentiment_icon = "😊"
                            elif sentiment_value > 0.4:
                                sentiment_icon = "😐"
                            else:
                                sentiment_icon = "😟"
                            st.write(f"{i}. {sentiment_icon} {headline['title'][:80]}...")
    else:
        st.markdown("""
        <div class="info-box">
        <strong>📰 No news data yet</strong><br>
        Please click "🔄 Refresh Data" in the main dashboard to get news information.
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.header("⚠️ Important Alerts")
    
    st.markdown("""
    <div class="info-box">
    <strong>💡 What alerts mean:</strong><br>
    • 🚨 Red = Very important, pay attention!<br>
    • 🟡 Yellow = Worth noting, but not urgent<br>
    • ✅ Green = All good, nothing to worry about
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.sentiment_data:
        # Calculate and display alerts
        alerts = calculate_alerts(st.session_state.sentiment_data, sentiment_threshold)
        
        if alerts:
            st.markdown(f"### 🚨 {len(alerts)} Things Need Your Attention")
            
            for alert in alerts:
                alert_type = alert['type']
                symbol = alert['symbol'].replace('.NS', ' (India)')
                message = alert['message']
                severity = alert['severity']
                
                # Simplify alert messages for beginners
                if "extremely positive sentiment" in message.lower():
                    simple_message = "People are VERY excited about this stock!"
                elif "extremely negative sentiment" in message.lower():
                    simple_message = "People are VERY worried about this stock!"
                elif "high positive sentiment" in message.lower():
                    simple_message = "People are quite happy with this stock"
                elif "high negative sentiment" in message.lower():
                    simple_message = "People are quite worried about this stock"
                else:
                    simple_message = message
                
                # Choose alert display based on severity
                if severity == 'high':
                    st.error(f"🚨 **{symbol}**: {simple_message}")
                elif severity == 'medium':
                    st.warning(f"🟡 **{symbol}**: {simple_message}")
                else:
                    st.info(f"💡 **{symbol}**: {simple_message}")
        else:
            st.success("✅ Everything looks normal! No alerts right now.")
            st.balloons()
        
        # Simple explanation
        st.subheader("📚 What Do These Alerts Mean?")
        
        col_help1, col_help2 = st.columns(2)
        
        with col_help1:
            st.markdown("""
            **🚨 Red Alerts:**
            - Very strong feelings (good or bad)
            - Price might change a lot soon
            - Consider buying or selling
            """)
        
        with col_help2:
            st.markdown("""
            **🟡 Yellow Alerts:**
            - Moderate feelings about the stock
            - Keep watching this stock
            - No immediate action needed
            """)
    else:
        st.markdown("""
        <div class="info-box">
        <strong>📊 No alert data yet</strong><br>
        Please click "🔄 Refresh Data" in the main dashboard to check for any important updates.
        </div>
        """, unsafe_allow_html=True)



# Simple footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 14px;'>
    <p>📈 Easy Stock Market Tracker | Shows prices in Indian Rupees (₹)</p>
    <p>Gets data from Yahoo Finance and analyzes news to help you understand market feelings</p>
</div>
""", unsafe_allow_html=True)
