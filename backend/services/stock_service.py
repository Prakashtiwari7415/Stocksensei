"""
Stock data service for fetching and processing market data
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import requests
import os
from schemas.schemas import StockDataResponse

class StockService:
    def __init__(self):
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes

    async def get_stock_data(self, symbol: str, days: int = 7) -> Optional[StockDataResponse]:
        """
        Fetch comprehensive stock data for a symbol
        """
        try:
            # Check cache first
            cache_key = f"{symbol}_{days}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if (datetime.now() - timestamp).seconds < self.cache_timeout:
                    return cached_data

            # Fetch data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=max(days, 30))  # Get more data for indicators
            
            hist_data = ticker.history(start=start_date, end=end_date)
            
            if hist_data.empty:
                return None

            # Get current info
            info = ticker.info
            
            # Calculate technical indicators
            hist_data['MA_5'] = hist_data['Close'].rolling(window=5).mean()
            hist_data['MA_20'] = hist_data['Close'].rolling(window=20).mean()
            hist_data['RSI'] = self._calculate_rsi(hist_data['Close'])
            hist_data['Volatility'] = hist_data['Close'].rolling(window=5).std()

            # Get current metrics
            current_price = float(hist_data['Close'].iloc[-1])
            previous_close = float(hist_data['Close'].iloc[-2]) if len(hist_data) > 1 else current_price
            price_change = current_price - previous_close
            price_change_pct = (price_change / previous_close) * 100 if previous_close != 0 else 0

            # Format market cap
            market_cap = info.get('marketCap', 0)
            if market_cap:
                if market_cap >= 1e12:
                    market_cap_str = f"{market_cap/1e12:.1f}T"
                elif market_cap >= 1e9:
                    market_cap_str = f"{market_cap/1e9:.1f}B"
                elif market_cap >= 1e6:
                    market_cap_str = f"{market_cap/1e6:.1f}M"
                else:
                    market_cap_str = str(market_cap)
            else:
                market_cap_str = "N/A"

            # Convert historical data to list of dicts
            historical_data = []
            for date, row in hist_data.tail(days).iterrows():
                historical_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row['Open']) if pd.notna(row['Open']) else None,
                    "high": float(row['High']) if pd.notna(row['High']) else None,
                    "low": float(row['Low']) if pd.notna(row['Low']) else None,
                    "close": float(row['Close']) if pd.notna(row['Close']) else None,
                    "volume": int(row['Volume']) if pd.notna(row['Volume']) else None,
                    "ma_5": float(row['MA_5']) if pd.notna(row['MA_5']) else None,
                    "ma_20": float(row['MA_20']) if pd.notna(row['MA_20']) else None,
                    "rsi": float(row['RSI']) if pd.notna(row['RSI']) else None
                })

            # Create response object
            stock_response = StockDataResponse(
                symbol=symbol,
                name=info.get('longName', symbol),
                sector=info.get('sector', 'Unknown'),
                current_price=current_price,
                price_change=price_change,
                price_change_pct=price_change_pct,
                volume=int(hist_data['Volume'].iloc[-1]),
                market_cap=market_cap_str,
                pe_ratio=float(info.get('trailingPE', 0)) if info.get('trailingPE') else None,
                ma_5=float(hist_data['MA_5'].iloc[-1]) if pd.notna(hist_data['MA_5'].iloc[-1]) else None,
                ma_20=float(hist_data['MA_20'].iloc[-1]) if pd.notna(hist_data['MA_20'].iloc[-1]) else None,
                rsi=float(hist_data['RSI'].iloc[-1]) if pd.notna(hist_data['RSI'].iloc[-1]) else None,
                volatility=float(hist_data['Volatility'].iloc[-1]) if pd.notna(hist_data['Volatility'].iloc[-1]) else None,
                historical_data=historical_data,
                last_updated=datetime.now()
            )

            # Cache the result
            self.cache[cache_key] = (stock_response, datetime.now())
            
            return stock_response

        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {str(e)}")
            return None

    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index (RSI)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    async def get_market_indices(self) -> Dict[str, Dict[str, Any]]:
        """Get major market indices data"""
        indices = {
            'SENSEX': '^BSESN',
            'NIFTY': '^NSEI', 
            'S&P 500': '^GSPC',
            'NASDAQ': '^IXIC',
            'Dow Jones': '^DJI',
            'VIX': '^VIX'
        }

        market_data = {}
        
        for name, symbol in indices.items():
            try:
                stock_data = await self.get_stock_data(symbol, days=2)
                if stock_data:
                    market_data[name] = {
                        'current_value': stock_data.current_price,
                        'change': stock_data.price_change,
                        'change_pct': stock_data.price_change_pct
                    }
            except Exception as e:
                print(f"Error fetching {name}: {str(e)}")
                continue
        
        return market_data

    async def get_sector_performance(self) -> Dict[str, float]:
        """Get sector ETF performance"""
        sector_etfs = {
            'Technology': 'XLK',
            'Healthcare': 'XLV', 
            'Financial': 'XLF',
            'Energy': 'XLE',
            'Consumer Discretionary': 'XLY',
            'Consumer Staples': 'XLP',
            'Industrials': 'XLI',
            'Materials': 'XLB',
            'Real Estate': 'XLRE',
            'Utilities': 'XLU',
            'Communication': 'XLC'
        }

        sector_performance = {}
        
        for sector, etf in sector_etfs.items():
            try:
                stock_data = await self.get_stock_data(etf, days=2)
                if stock_data:
                    sector_performance[sector] = stock_data.price_change_pct
            except Exception as e:
                print(f"Error fetching {sector} sector data: {str(e)}")
                sector_performance[sector] = 0.0
        
        return sector_performance

    async def refresh_all_data(self):
        """Background task to refresh all cached stock data"""
        try:
            # Clear old cache
            self.cache.clear()
            print("Stock data cache refreshed")
        except Exception as e:
            print(f"Error refreshing stock data: {str(e)}")

    def format_currency(self, amount: float, symbol: str) -> str:
        """Format currency based on stock origin"""
        try:
            if symbol.endswith('.NS'):
                # Indian stock - amount is already in INR
                return f"₹{amount:,.2f}"
            else:
                # US stock - convert USD to INR (rate: 83 INR per USD)
                inr_amount = amount * 83
                return f"₹{inr_amount:,.2f}"
        except:
            return str(amount)