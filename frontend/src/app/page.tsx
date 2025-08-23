'use client'

import { useState, useEffect } from 'react'
import Dashboard from '../components/Dashboard'
import StockSelector from '../components/StockSelector'
import AlertPanel from '../components/AlertPanel'
import { TrendingUp, BarChart3, Bell, RefreshCw, Clock } from 'lucide-react'

interface MarketStatus {
  indian_market: {
    is_open: boolean
    next_open?: string
    next_close?: string
    timezone: string
  }
  us_market: {
    is_open: boolean
    timezone: string
  }
  timestamp: string
}

export default function Home() {
  const [selectedStocks, setSelectedStocks] = useState<string[]>(['RELIANCE.NS', 'TCS.NS', 'AAPL', 'GOOGL'])
  const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  useEffect(() => {
    fetchMarketStatus()
    const interval = setInterval(fetchMarketStatus, 60000) // Update every minute
    return () => clearInterval(interval)
  }, [])

  const fetchMarketStatus = async () => {
    try {
      const response = await fetch('/api/market-status')
      if (response.ok) {
        const data = await response.json()
        setMarketStatus(data)
      }
    } catch (error) {
      console.error('Error fetching market status:', error)
    }
  }

  const handleRefreshData = () => {
    setIsLoading(true)
    setLastUpdated(new Date())
    setTimeout(() => setIsLoading(false), 2000)
  }

  const formatMarketStatus = (status: MarketStatus) => {
    const indianStatus = status.indian_market.is_open ? '🟢 NSE Open' : '🔴 NSE Closed'
    const usStatus = status.us_market.is_open ? '🟢 NYSE Open' : '🔴 NYSE Closed'
    return `${indianStatus} | ${usStatus}`
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg border-b-4 border-blue-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-8 w-8 text-blue-600" />
                <h1 className="text-2xl font-bold text-gray-900">Stock Sentiment Tracker</h1>
              </div>
              <div className="hidden sm:block text-sm text-gray-600 bg-blue-50 px-3 py-1 rounded-full">
                Real-time Indian & US Markets
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {marketStatus && (
                <div className="text-sm font-medium text-gray-700 bg-gray-100 px-3 py-1 rounded-full">
                  {formatMarketStatus(marketStatus)}
                </div>
              )}
              <button
                onClick={handleRefreshData}
                disabled={isLoading}
                className="flex items-center space-x-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                <span className="hidden sm:inline">Refresh</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Info Banner */}
        <div className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white p-4 rounded-lg mb-6 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">Track Market Sentiment in Real-Time</h2>
              <p className="text-blue-100 mt-1">
                Monitor stock prices in Indian Rupees (₹) with news sentiment analysis for better investment decisions
              </p>
            </div>
            <div className="hidden md:flex items-center space-x-4 text-blue-100">
              <div className="flex items-center space-x-1">
                <BarChart3 className="h-5 w-5" />
                <span>Price Tracking</span>
              </div>
              <div className="flex items-center space-x-1">
                <Bell className="h-5 w-5" />
                <span>Smart Alerts</span>
              </div>
              <div className="flex items-center space-x-1">
                <Clock className="h-5 w-5" />
                <span>Real-time Data</span>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Stock Selector */}
          <div className="lg:col-span-1">
            <StockSelector
              selectedStocks={selectedStocks}
              onStockSelectionChange={setSelectedStocks}
            />
            
            {/* Last Updated */}
            <div className="mt-4 p-3 bg-white rounded-lg shadow text-sm text-gray-600">
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4" />
                <span>Last updated: {lastUpdated.toLocaleTimeString('en-IN', {
                  timeZone: 'Asia/Kolkata',
                  hour12: true
                })}</span>
              </div>
            </div>
          </div>

          {/* Main Dashboard */}
          <div className="lg:col-span-3">
            <Dashboard
              selectedStocks={selectedStocks}
              isLoading={isLoading}
              onRefresh={handleRefreshData}
            />
          </div>
        </div>

        {/* Alerts Section */}
        <div className="mt-6">
          <AlertPanel selectedStocks={selectedStocks} />
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            Data updated every 15 minutes during market hours. 
            Indian markets: NSE/BSE | US markets: NYSE/NASDAQ
          </p>
          <p className="mt-1">
            All prices converted to Indian Rupees (₹) for easy understanding
          </p>
        </div>
      </div>
    </main>
  )
}