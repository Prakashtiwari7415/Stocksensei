import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

def create_price_chart(stock_data: Dict[str, Any], sentiment_data: Dict[str, Any], symbol: str) -> go.Figure:
    """
    Create an interactive price chart with sentiment overlay.
    
    Args:
        stock_data: Stock price and volume data
        sentiment_data: Sentiment analysis results
        symbol: Stock symbol for chart title
        
    Returns:
        Plotly figure object
    """
    try:
        df = stock_data['data']
        
        # Create subplots with secondary y-axis
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=(f'{symbol} Price & Moving Averages', 'Volume', 'Technical Indicators'),
            row_heights=[0.6, 0.2, 0.2]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name=f'{symbol} Price',
                increasing_line_color='#00ff88',
                decreasing_line_color='#ff4444'
            ),
            row=1, col=1
        )
        
        # Moving averages
        if 'MA_5' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MA_5'],
                    mode='lines',
                    name='MA(5)',
                    line=dict(color='orange', width=1)
                ),
                row=1, col=1
            )
        
        if 'MA_20' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MA_20'],
                    mode='lines',
                    name='MA(20)',
                    line=dict(color='blue', width=1)
                ),
                row=1, col=1
            )
        
        # Volume bars
        colors = ['red' if close < open else 'green' for close, open in zip(df['Close'], df['Open'])]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # RSI
        if 'RSI' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['RSI'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='purple', width=2)
                ),
                row=3, col=1
            )
            
            # RSI reference lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=3, col=1)
        
        # Add sentiment indicators if available
        if sentiment_data and 'overall_sentiment' in sentiment_data:
            sentiment_score = sentiment_data['overall_sentiment']
            sentiment_color = 'green' if sentiment_score > 0.6 else 'red' if sentiment_score < 0.4 else 'orange'
            
            # Add sentiment annotation
            fig.add_annotation(
                x=df.index[-1],
                y=df['Close'].iloc[-1],
                text=f"Sentiment: {sentiment_score:.2f}",
                showarrow=True,
                arrowhead=2,
                arrowcolor=sentiment_color,
                bgcolor=sentiment_color,
                bordercolor=sentiment_color,
                font=dict(color='white'),
                row=1, col=1
            )
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} - Stock Price Analysis',
            xaxis_rangeslider_visible=False,
            height=600,
            showlegend=True,
            template='plotly_white'
        )
        
        # Update y-axes
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating price chart: {str(e)}")
        return go.Figure()

def create_sentiment_heatmap(stock_data: Dict[str, Any], sentiment_data: Dict[str, Any]) -> go.Figure:
    """
    Create a sector-wise sentiment heatmap.
    
    Args:
        stock_data: Dictionary of stock data for multiple symbols
        sentiment_data: Dictionary of sentiment data for multiple symbols
        
    Returns:
        Plotly figure object
    """
    try:
        # Sector mapping (simplified)
        sector_mapping = {
            'AAPL': 'Technology', 'GOOGL': 'Technology', 'MSFT': 'Technology', 
            'META': 'Technology', 'NVDA': 'Technology',
            'AMZN': 'Consumer Discretionary', 'TSLA': 'Consumer Discretionary',
            'JPM': 'Financial Services', 'BAC': 'Financial Services',
            'JNJ': 'Healthcare', 'PFE': 'Healthcare',
            'XOM': 'Energy', 'CVX': 'Energy'
        }
        
        # Prepare data for heatmap
        sectors = {}
        for symbol in sentiment_data.keys():
            if symbol in stock_data:
                sector = sector_mapping.get(symbol, 'Other')
                if sector not in sectors:
                    sectors[sector] = {'symbols': [], 'sentiments': [], 'price_changes': []}
                
                sectors[sector]['symbols'].append(symbol)
                sectors[sector]['sentiments'].append(sentiment_data[symbol]['overall_sentiment'])
                sectors[sector]['price_changes'].append(stock_data[symbol]['price_change_pct'])
        
        if not sectors:
            st.warning("No sector data available for heatmap")
            return go.Figure()
        
        # Calculate sector averages
        sector_names = []
        avg_sentiments = []
        avg_price_changes = []
        stock_counts = []
        
        for sector, data in sectors.items():
            sector_names.append(sector)
            avg_sentiments.append(np.mean(data['sentiments']))
            avg_price_changes.append(np.mean(data['price_changes']))
            stock_counts.append(len(data['symbols']))
        
        # Create bubble chart (sentiment vs price change)
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=avg_sentiments,
                y=avg_price_changes,
                mode='markers+text',
                text=sector_names,
                textposition='middle center',
                marker=dict(
                    size=np.array(stock_counts) * 20,  # Bubble size based on stock count
                    color=avg_sentiments,
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="Sentiment Score"),
                    line=dict(width=2, color='white')
                ),
                hovertemplate='<b>%{text}</b><br>' +
                             'Sentiment: %{x:.2f}<br>' +
                             'Price Change: %{y:.2f}%<br>' +
                             'Stocks: %{marker.size}' +
                             '<extra></extra>'
            )
        )
        
        # Add quadrant lines
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=0.5, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Add quadrant labels
        fig.add_annotation(x=0.25, y=max(avg_price_changes) * 0.8, text="Negative Sentiment<br>Positive Returns", 
                          showarrow=False, font=dict(size=10, color="gray"))
        fig.add_annotation(x=0.75, y=max(avg_price_changes) * 0.8, text="Positive Sentiment<br>Positive Returns", 
                          showarrow=False, font=dict(size=10, color="gray"))
        fig.add_annotation(x=0.25, y=min(avg_price_changes) * 0.8, text="Negative Sentiment<br>Negative Returns", 
                          showarrow=False, font=dict(size=10, color="gray"))
        fig.add_annotation(x=0.75, y=min(avg_price_changes) * 0.8, text="Positive Sentiment<br>Negative Returns", 
                          showarrow=False, font=dict(size=10, color="gray"))
        
        fig.update_layout(
            title='Sector Sentiment vs Price Performance',
            xaxis_title='Average Sentiment Score',
            yaxis_title='Average Price Change (%)',
            template='plotly_white',
            height=500
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating sentiment heatmap: {str(e)}")
        return go.Figure()

def create_correlation_chart(stock_data: Dict[str, Any], sentiment_data: Dict[str, Any]) -> go.Figure:
    """
    Create a correlation chart between price movements and sentiment scores.
    
    Args:
        stock_data: Dictionary of stock data for multiple symbols
        sentiment_data: Dictionary of sentiment data for multiple symbols
        
    Returns:
        Plotly figure object
    """
    try:
        symbols = []
        price_changes = []
        sentiment_scores = []
        correlations = []
        
        for symbol in stock_data.keys():
            if symbol in sentiment_data:
                symbols.append(symbol)
                price_changes.append(stock_data[symbol]['price_change_pct'])
                sentiment_scores.append(sentiment_data[symbol]['overall_sentiment'])
                correlations.append(sentiment_data[symbol].get('price_correlation', 0))
        
        if not symbols:
            return go.Figure()
        
        # Create scatter plot
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=sentiment_scores,
                y=price_changes,
                mode='markers+text',
                text=symbols,
                textposition='top center',
                marker=dict(
                    size=12,
                    color=correlations,
                    colorscale='RdBu',
                    showscale=True,
                    colorbar=dict(title="Correlation"),
                    line=dict(width=1, color='white')
                ),
                hovertemplate='<b>%{text}</b><br>' +
                             'Sentiment: %{x:.2f}<br>' +
                             'Price Change: %{y:.2f}%<br>' +
                             'Correlation: %{marker.color:.2f}' +
                             '<extra></extra>'
            )
        )
        
        # Add trend line if there are enough points
        if len(sentiment_scores) > 2:
            z = np.polyfit(sentiment_scores, price_changes, 1)
            p = np.poly1d(z)
            x_trend = np.linspace(min(sentiment_scores), max(sentiment_scores), 100)
            y_trend = p(x_trend)
            
            fig.add_trace(
                go.Scatter(
                    x=x_trend,
                    y=y_trend,
                    mode='lines',
                    name='Trend Line',
                    line=dict(color='red', dash='dash'),
                    showlegend=True
                )
            )
        
        # Add reference lines
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=0.5, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title='Stock Performance vs Sentiment Correlation',
            xaxis_title='Sentiment Score',
            yaxis_title='Price Change (%)',
            template='plotly_white',
            height=500
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating correlation chart: {str(e)}")
        return go.Figure()

def create_sentiment_timeline(sentiment_data: Dict[str, Any], symbol: str) -> go.Figure:
    """
    Create a timeline chart showing sentiment evolution over time.
    
    Args:
        sentiment_data: Sentiment analysis results
        symbol: Stock symbol
        
    Returns:
        Plotly figure object
    """
    try:
        if 'recent_headlines' not in sentiment_data:
            return go.Figure()
        
        headlines = sentiment_data['recent_headlines']
        
        # Sort by date
        sorted_headlines = sorted(headlines, key=lambda x: x.get('date', ''))
        
        dates = []
        sentiments = []
        titles = []
        
        for headline in sorted_headlines:
            try:
                date_str = headline.get('date', '')
                if date_str:
                    dates.append(datetime.fromisoformat(date_str.replace('Z', '+00:00')))
                    sentiments.append(headline['sentiment'])
                    titles.append(headline['title'][:50] + '...' if len(headline['title']) > 50 else headline['title'])
            except:
                continue
        
        if not dates:
            return go.Figure()
        
        # Create line chart
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=sentiments,
                mode='lines+markers',
                name='Sentiment Score',
                line=dict(color='blue', width=2),
                marker=dict(size=8),
                hovertemplate='<b>%{text}</b><br>' +
                             'Date: %{x}<br>' +
                             'Sentiment: %{y:.2f}' +
                             '<extra></extra>',
                text=titles
            )
        )
        
        # Add reference line for neutral sentiment
        fig.add_hline(y=0.5, line_dash="dash", line_color="gray", 
                     annotation_text="Neutral Threshold")
        
        fig.update_layout(
            title=f'{symbol} - Sentiment Timeline',
            xaxis_title='Date',
            yaxis_title='Sentiment Score',
            template='plotly_white',
            height=400,
            yaxis=dict(range=[0, 1])
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating sentiment timeline: {str(e)}")
        return go.Figure()
