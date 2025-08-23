'use client'

import { useState, useEffect } from 'react'
import { Bell, AlertTriangle, TrendingUp, TrendingDown, Volume2, Activity } from 'lucide-react'

interface Alert {
  id: number
  symbol: string
  alert_type: string
  severity: string
  message: string
  threshold_value?: number
  current_value?: number
  is_active: boolean
  triggered_at: string
}

interface AlertPanelProps {
  selectedStocks: string[]
}

export default function AlertPanel({ selectedStocks }: AlertPanelProps) {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all')

  useEffect(() => {
    if (selectedStocks.length > 0) {
      fetchAlerts()
    } else {
      setAlerts([])
      setLoading(false)
    }
  }, [selectedStocks])

  const fetchAlerts = async () => {
    setLoading(true)
    try {
      // Generate alerts based on dashboard data
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
        setAlerts(data.alerts || [])
      }
    } catch (error) {
      console.error('Error fetching alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  const getAlertIcon = (alertType: string) => {
    switch (alertType) {
      case 'sentiment':
        return Activity
      case 'trend':
        return TrendingUp
      case 'volume':
        return Volume2
      case 'correlation':
        return TrendingDown
      default:
        return AlertTriangle
    }
  }

  const getAlertColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-50 border-red-200 text-red-800'
      case 'medium':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800'
      case 'low':
        return 'bg-blue-50 border-blue-200 text-blue-800'
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800'
    }
  }

  const getSeverityBadgeColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-100 text-red-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const filteredAlerts = filter === 'all' 
    ? alerts 
    : alerts.filter(alert => alert.severity === filter)

  const alertCounts = {
    high: alerts.filter(alert => alert.severity === 'high').length,
    medium: alerts.filter(alert => alert.severity === 'medium').length,
    low: alerts.filter(alert => alert.severity === 'low').length,
    total: alerts.length
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-300 rounded w-32 mb-4"></div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-300 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Bell className="h-6 w-6 text-blue-600" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Smart Alerts</h3>
              <p className="text-sm text-gray-600">
                Real-time notifications based on sentiment and market changes
              </p>
            </div>
          </div>
          
          {/* Alert Summary */}
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              <span>{alertCounts.high} High</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span>{alertCounts.medium} Medium</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>{alertCounts.low} Low</span>
            </div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="mt-4 flex space-x-1">
          {['all', 'high', 'medium', 'low'].map((severity) => (
            <button
              key={severity}
              onClick={() => setFilter(severity as any)}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg capitalize transition-colors ${
                filter === severity
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              {severity === 'all' ? `All (${alertCounts.total})` : `${severity} (${alertCounts[severity as keyof typeof alertCounts]})`}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts List */}
      <div className="max-h-96 overflow-y-auto">
        {filteredAlerts.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <Bell className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p className="font-medium">No alerts found</p>
            <p className="text-sm">
              {selectedStocks.length === 0 
                ? 'Select stocks to start monitoring for alerts'
                : 'Your selected stocks are performing normally'
              }
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredAlerts.map((alert) => {
              const AlertIcon = getAlertIcon(alert.alert_type)
              return (
                <div
                  key={alert.id}
                  className={`p-4 border-l-4 ${
                    alert.severity === 'high' ? 'border-red-500' :
                    alert.severity === 'medium' ? 'border-yellow-500' : 'border-blue-500'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <AlertIcon className={`h-5 w-5 mt-0.5 ${
                        alert.severity === 'high' ? 'text-red-600' :
                        alert.severity === 'medium' ? 'text-yellow-600' : 'text-blue-600'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-medium text-gray-900">{alert.symbol}</span>
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getSeverityBadgeColor(alert.severity)}`}>
                            {alert.severity.toUpperCase()}
                          </span>
                          <span className="text-xs text-gray-500 capitalize">
                            {alert.alert_type.replace('_', ' ')}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700">{alert.message}</p>
                        <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                          <span>{new Date(alert.triggered_at).toLocaleString('en-IN', {
                            timeZone: 'Asia/Kolkata',
                            hour12: true,
                            dateStyle: 'short',
                            timeStyle: 'short'
                          })}</span>
                          {alert.threshold_value && alert.current_value && (
                            <span>
                              Threshold: {alert.threshold_value.toFixed(2)} | 
                              Current: {alert.current_value.toFixed(2)}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    {alert.is_active && (
                      <div className="flex-shrink-0">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Footer */}
      {alerts.length > 0 && (
        <div className="p-4 border-t border-gray-200 bg-gray-50 text-sm text-gray-600 text-center">
          <p>
            Alerts are generated based on sentiment analysis and market data changes. 
            Check regularly during market hours for real-time updates.
          </p>
        </div>
      )}
    </div>
  )
}