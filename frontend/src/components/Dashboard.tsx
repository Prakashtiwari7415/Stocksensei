'use client'

import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { TrendingUp, TrendingDown, Activity, AlertTriangle, DollarSign, BarChart3 } from 'lucide-react'

interface StockData {
  symbol: string
  name: string
  current_price: number
  price_change: number
  price_change_pct: number
  volume: number
  market_cap: string
  historical_data?: Array<{
    date: string
    close: number
    volume: number
  }>
}

interface SentimentData {
  symbol: string
  overall_sentiment: number
  confidence: number
  total_articles: number
  sentiment_trend: string
  recent_headlines: Array<{
    title: string
    sentiment: number
    source: string
    date: string
  }>
}

interface DashboardProps {
  selectedStocks: string[]
  isLoading: boolean
  onRefresh: () => void
}

export default function Dashboard({ selectedStocks, isLoading, onRefresh }: DashboardProps) {
  const [stockData, setStockData] = useState<Record<string, StockData>>({})
  const [sentimentData, setSentimentData] = useState<Record<string, SentimentData>>({})
  const [activeTab, setActiveTab] = useState<'overview' | 'sentiment' | 'charts'>('overview')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (selectedStocks.length > 0) {
      fetchDashboardData()
    }
  }, [selectedStocks])

  const fetchDashboardData = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/dashboard', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbols: selectedStocks,
          lookback_days: 7
        })
      })

      if (response.ok) {
        const data = await response.json()
        setStockData(data.stocks || {})
        setSentimentData(data.sentiment || {})
      } else {
        console.error('Failed to fetch dashboard data')
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number, symbol: string) => {
    if (symbol.endsWith('.NS')) {
      return `₹${amount.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
    } else {
      const inrAmount = amount * 83
      return `₹${inrAmount.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
    }
  }

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.6) return 'text-green-600'
    if (sentiment < 0.4) return 'text-red-600'
    return 'text-yellow-600'
  }

  const getSentimentLabel = (sentiment: number) => {
    if (sentiment > 0.7) return 'Very Positive'
    if (sentiment > 0.6) return 'Positive'
    if (sentiment > 0.4) return 'Neutral'
    if (sentiment > 0.3) return 'Negative'
    return 'Very Negative'
  }

  if (loading || isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-pulse">
          <div className="flex space-x-4 mb-6">
            <div className="h-4 bg-gray-300 rounded w-24"></div>
            <div className="h-4 bg-gray-300 rounded w-24"></div>
            <div className="h-4 bg-gray-300 rounded w-24"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="border rounded-lg p-4">
                <div className="h-4 bg-gray-300 rounded w-20 mb-2"></div>
                <div className="h-6 bg-gray-300 rounded w-32 mb-2"></div>
                <div className="h-4 bg-gray-300 rounded w-24"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6 py-4">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'sentiment', label: 'Sentiment Analysis', icon: Activity },
            { id: 'charts', label: 'Price Charts', icon: TrendingUp }
          ].map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Stock Overview</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {selectedStocks.map((symbol) => {
                const stock = stockData[symbol]
                const sentiment = sentimentData[symbol]
                
                if (!stock) {
                  return (
                    <div key={symbol} className="border border-gray-200 rounded-lg p-4">
                      <div className="text-center text-gray-500">Loading {symbol}...</div>
                    </div>
                  )
                }

                return (
                  <div key={symbol} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-900">{stock.symbol}</h4>
                        <p className="text-sm text-gray-600">{stock.name}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-gray-900">
                          {formatCurrency(stock.current_price, stock.symbol)}
                        </div>
                        <div className={`text-sm flex items-center ${
                          stock.price_change >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {stock.price_change >= 0 ? (
                            <TrendingUp className="h-3 w-3 mr-1" />
                          ) : (
                            <TrendingDown className="h-3 w-3 mr-1" />
                          )}
                          {stock.price_change_pct.toFixed(2)}%
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Market Cap:</span>
                        <div className="font-medium">{stock.market_cap}</div>
                      </div>
                      <div>
                        <span className="text-gray-500">Volume:</span>
                        <div className="font-medium">{stock.volume.toLocaleString()}</div>
                      </div>
                    </div>

                    {sentiment && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-500">Sentiment:</span>
                          <div className={`text-sm font-medium ${getSentimentColor(sentiment.overall_sentiment)}`}>
                            {getSentimentLabel(sentiment.overall_sentiment)}
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                          <div
                            className={`h-1.5 rounded-full ${
                              sentiment.overall_sentiment > 0.6 ? 'bg-green-500' :
                              sentiment.overall_sentiment < 0.4 ? 'bg-red-500' : 'bg-yellow-500'
                            }`}
                            style={{ width: `${sentiment.overall_sentiment * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {activeTab === 'sentiment' && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Analysis</h3>
            <div className="space-y-6">
              {selectedStocks.map((symbol) => {
                const sentiment = sentimentData[symbol]
                
                if (!sentiment) {
                  return (
                    <div key={symbol} className="border border-gray-200 rounded-lg p-4">
                      <div className="text-center text-gray-500">Loading sentiment for {symbol}...</div>
                    </div>
                  )
                }

                return (
                  <div key={symbol} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h4 className="font-semibold text-gray-900">{symbol}</h4>
                        <p className="text-sm text-gray-600">
                          Based on {sentiment.total_articles} articles
                        </p>
                      </div>
                      <div className="text-right">
                        <div className={`text-lg font-bold ${getSentimentColor(sentiment.overall_sentiment)}`}>
                          {getSentimentLabel(sentiment.overall_sentiment)}
                        </div>
                        <div className="text-sm text-gray-500">
                          Confidence: {(sentiment.confidence * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div className="text-center p-2 bg-green-50 rounded">
                        <div className="text-lg font-bold text-green-600">{sentiment.positive_count || 0}</div>
                        <div className="text-xs text-green-700">Positive</div>
                      </div>
                      <div className="text-center p-2 bg-gray-50 rounded">
                        <div className="text-lg font-bold text-gray-600">{sentiment.neutral_count || 0}</div>
                        <div className="text-xs text-gray-700">Neutral</div>
                      </div>
                      <div className="text-center p-2 bg-red-50 rounded">
                        <div className="text-lg font-bold text-red-600">{sentiment.negative_count || 0}</div>
                        <div className="text-xs text-red-700">Negative</div>
                      </div>
                    </div>

                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Recent Headlines:</h5>
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {sentiment.recent_headlines?.slice(0, 5).map((headline, idx) => (
                          <div key={idx} className="text-sm p-2 bg-gray-50 rounded">
                            <div className={`font-medium ${getSentimentColor(headline.sentiment)}`}>
                              {headline.title}
                            </div>
                            <div className="text-gray-500 text-xs mt-1">
                              {headline.source} • {new Date(headline.date).toLocaleDateString()}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {activeTab === 'charts' && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Price Charts</h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {selectedStocks.map((symbol) => {
                const stock = stockData[symbol]
                
                if (!stock || !stock.historical_data) {
                  return (
                    <div key={symbol} className="border border-gray-200 rounded-lg p-4">
                      <div className="text-center text-gray-500">Loading chart for {symbol}...</div>
                    </div>
                  )
                }

                const chartData = stock.historical_data.map(point => ({
                  date: new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                  price: stock.symbol.endsWith('.NS') ? point.close : point.close * 83,
                  volume: point.volume || 0
                }))

                return (
                  <div key={symbol} className="border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-3">{stock.symbol}</h4>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <Tooltip 
                            formatter={(value: any) => [`₹${parseFloat(value).toLocaleString('en-IN')}`, 'Price']}
                          />
                          <Area 
                            type="monotone" 
                            dataKey="price" 
                            stroke="#3B82F6" 
                            fill="#3B82F6" 
                            fillOpacity={0.1}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}