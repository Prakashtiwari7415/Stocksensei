'use client'

import { useState, useEffect } from 'react'
import { Search, Plus, X, TrendingUp, Building2 } from 'lucide-react'

interface Stock {
  symbol: string
  name: string
  sector: string
}

interface PopularStocks {
  indian_stocks: Stock[]
  us_stocks: Stock[]
}

interface StockSelectorProps {
  selectedStocks: string[]
  onStockSelectionChange: (stocks: string[]) => void
}

export default function StockSelector({ selectedStocks, onStockSelectionChange }: StockSelectorProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [popularStocks, setPopularStocks] = useState<PopularStocks | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [showDropdown, setShowDropdown] = useState(false)

  useEffect(() => {
    fetchPopularStocks()
  }, [])

  const fetchPopularStocks = async () => {
    try {
      const response = await fetch('/api/popular-stocks')
      if (response.ok) {
        const data = await response.json()
        setPopularStocks(data)
      }
    } catch (error) {
      console.error('Error fetching popular stocks:', error)
      // Fallback data if API fails
      setPopularStocks({
        indian_stocks: [
          { symbol: 'RELIANCE.NS', name: 'Reliance Industries', sector: 'Energy' },
          { symbol: 'TCS.NS', name: 'Tata Consultancy Services', sector: 'Technology' },
          { symbol: 'INFY.NS', name: 'Infosys', sector: 'Technology' },
          { symbol: 'ITC.NS', name: 'ITC Limited', sector: 'FMCG' },
          { symbol: 'LT.NS', name: 'Larsen & Toubro', sector: 'Construction' }
        ],
        us_stocks: [
          { symbol: 'AAPL', name: 'Apple Inc.', sector: 'Technology' },
          { symbol: 'GOOGL', name: 'Alphabet Inc.', sector: 'Technology' },
          { symbol: 'MSFT', name: 'Microsoft Corporation', sector: 'Technology' },
          { symbol: 'AMZN', name: 'Amazon.com Inc.', sector: 'E-commerce' },
          { symbol: 'TSLA', name: 'Tesla Inc.', sector: 'Automotive' }
        ]
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleAddStock = (symbol: string) => {
    if (!selectedStocks.includes(symbol)) {
      onStockSelectionChange([...selectedStocks, symbol])
    }
    setSearchTerm('')
    setShowDropdown(false)
  }

  const handleRemoveStock = (symbol: string) => {
    onStockSelectionChange(selectedStocks.filter(s => s !== symbol))
  }

  const filteredStocks = popularStocks 
    ? [...popularStocks.indian_stocks, ...popularStocks.us_stocks].filter(stock =>
        stock.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
        stock.sector.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : []

  const getStockInfo = (symbol: string) => {
    if (!popularStocks) return null
    return [...popularStocks.indian_stocks, ...popularStocks.us_stocks]
      .find(stock => stock.symbol === symbol)
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-300 rounded w-32 mb-4"></div>
          <div className="space-y-2">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-300 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
          Stock Selection
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Choose stocks to track and analyze
        </p>
      </div>

      {/* Search */}
      <div className="p-4 border-b border-gray-200">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search stocks..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value)
              setShowDropdown(e.target.value.length > 0)
            }}
            onFocus={() => setShowDropdown(searchTerm.length > 0)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          
          {/* Search Dropdown */}
          {showDropdown && filteredStocks.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              {filteredStocks.slice(0, 8).map((stock) => (
                <button
                  key={stock.symbol}
                  onClick={() => handleAddStock(stock.symbol)}
                  disabled={selectedStocks.includes(stock.symbol)}
                  className="w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium text-gray-900">{stock.symbol}</div>
                      <div className="text-sm text-gray-600 truncate">{stock.name}</div>
                    </div>
                    <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                      {stock.sector}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Selected Stocks */}
      <div className="p-4">
        <h4 className="font-medium text-gray-900 mb-3">
          Selected Stocks ({selectedStocks.length})
        </h4>
        
        {selectedStocks.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Building2 className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>No stocks selected</p>
            <p className="text-sm">Search and add stocks above</p>
          </div>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {selectedStocks.map((symbol) => {
              const stockInfo = getStockInfo(symbol)
              return (
                <div
                  key={symbol}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <div className="font-medium text-gray-900">{symbol}</div>
                      {symbol.endsWith('.NS') ? (
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">NSE</span>
                      ) : (
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded">NYSE</span>
                      )}
                    </div>
                    {stockInfo && (
                      <div className="text-sm text-gray-600 truncate">
                        {stockInfo.name}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => handleRemoveStock(symbol)}
                    className="ml-2 p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Quick Add Suggestions */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <h4 className="font-medium text-gray-900 mb-3">Popular Stocks</h4>
        <div className="grid grid-cols-2 gap-2">
          {popularStocks && (
            <>
              <div>
                <h5 className="text-xs font-medium text-gray-600 mb-2">Indian (NSE)</h5>
                <div className="space-y-1">
                  {popularStocks.indian_stocks.slice(0, 3).map((stock) => (
                    <button
                      key={stock.symbol}
                      onClick={() => handleAddStock(stock.symbol)}
                      disabled={selectedStocks.includes(stock.symbol)}
                      className="w-full text-left px-2 py-1.5 text-sm bg-white border border-gray-200 rounded hover:bg-blue-50 hover:border-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <div className="font-medium text-gray-900">{stock.symbol.replace('.NS', '')}</div>
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <h5 className="text-xs font-medium text-gray-600 mb-2">US (NYSE)</h5>
                <div className="space-y-1">
                  {popularStocks.us_stocks.slice(0, 3).map((stock) => (
                    <button
                      key={stock.symbol}
                      onClick={() => handleAddStock(stock.symbol)}
                      disabled={selectedStocks.includes(stock.symbol)}
                      className="w-full text-left px-2 py-1.5 text-sm bg-white border border-gray-200 rounded hover:bg-green-50 hover:border-green-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <div className="font-medium text-gray-900">{stock.symbol}</div>
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}