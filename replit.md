# Stock Market Sentiment Tracker

## Overview

This is a Streamlit-based web application that combines real-time stock market data with sentiment analysis from news sources. The application provides traders and investors with a comprehensive dashboard to monitor stock prices, technical indicators, and market sentiment trends in real-time. Users can select multiple stocks to track, view interactive charts with price movements and sentiment overlays, and receive alerts based on configurable criteria.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application with responsive layout
- **Visualization**: Plotly for interactive charts including candlestick price charts, sentiment heatmaps, and correlation charts
- **UI Components**: Sidebar for stock selection and configuration, multi-column dashboard layout for displaying multiple metrics simultaneously
- **Caching Strategy**: Streamlit's `@st.cache_resource` decorator for component initialization to improve performance

### Backend Architecture
- **Modular Design**: Separated into distinct modules for data fetching (`data_fetcher.py`), sentiment analysis (`sentiment_analyzer.py`), visualizations (`visualizations.py`), and utilities (`utils.py`)
- **Data Processing**: Pandas and NumPy for data manipulation and numerical computations
- **Real-time Updates**: Configurable refresh intervals (5-30 minutes) for automatic data updates
- **Technical Analysis**: Built-in calculation of moving averages (MA_5, MA_20), RSI, and volatility indicators

### Data Storage Solutions
- **In-Memory Processing**: Uses pandas DataFrames for temporary data storage and manipulation
- **No Persistent Database**: Current architecture relies on real-time API calls without local data persistence
- **Caching**: Leverages Streamlit's caching mechanisms for API responses and computed results

### Authentication and Authorization
- **API Key Management**: Environment variable-based configuration for external API keys (NEWS_API_KEY, ALPHA_VANTAGE_API_KEY)
- **No User Authentication**: Single-user application without login requirements
- **Demo Mode**: Fallback to demo keys when environment variables are not configured

### Sentiment Analysis Engine
- **Dual NLP Approach**: Combines TextBlob and VADER sentiment analysis for more robust sentiment scoring
- **News Integration**: Processes news articles related to selected stocks to generate sentiment metrics
- **Correlation Analysis**: Attempts to correlate sentiment trends with price movements for predictive insights

## External Dependencies

### Market Data APIs
- **Yahoo Finance (yfinance)**: Primary source for real-time and historical stock data, company information, and market statistics
- **Alpha Vantage API**: Secondary financial data source for additional market metrics and technical indicators

### News and Sentiment APIs
- **News API**: Fetches recent news articles related to specific stocks for sentiment analysis
- **External News Sources**: Processes headlines and article content from various financial news providers

### Python Libraries
- **Data Processing**: pandas, numpy for data manipulation and numerical analysis
- **Visualization**: plotly for interactive charts and graphs
- **Web Framework**: streamlit for the web application interface
- **NLP Libraries**: textblob and vaderSentiment for natural language processing and sentiment analysis
- **HTTP Requests**: requests library for API communications

### Development and Deployment
- **Environment Configuration**: Uses environment variables for API key management and configuration
- **Package Management**: Standard Python package management (requirements likely managed via pip)
- **Error Handling**: Built-in error handling for API failures and data availability issues