"""
Alert service for generating and managing stock market alerts
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import numpy as np
from schemas.schemas import AlertResponse, SentimentAnalysisResponse

class AlertService:
    def __init__(self):
        self.alert_rules = {
            'sentiment_high': 0.75,
            'sentiment_low': 0.25,
            'sentiment_extreme_high': 0.85,
            'sentiment_extreme_low': 0.15,
            'volatility_threshold': 0.05,
            'volume_spike_threshold': 2.0,
            'correlation_threshold': 0.7
        }

    async def generate_alerts(self, sentiment_data: Dict[str, SentimentAnalysisResponse]) -> List[AlertResponse]:
        """Generate alerts based on sentiment analysis and market data"""
        alerts = []
        alert_id_counter = 1
        
        try:
            for symbol, data in sentiment_data.items():
                symbol_alerts = self._analyze_symbol_for_alerts(symbol, data, alert_id_counter)
                alerts.extend(symbol_alerts)
                alert_id_counter += len(symbol_alerts)
            
            # Sort alerts by severity
            severity_order = {'high': 0, 'medium': 1, 'low': 2}
            alerts.sort(key=lambda x: severity_order.get(x.severity, 3))
            
            return alerts
            
        except Exception as e:
            print(f"Error generating alerts: {str(e)}")
            return []

    def _analyze_symbol_for_alerts(self, symbol: str, data: SentimentAnalysisResponse, start_id: int) -> List[AlertResponse]:
        """Analyze a single symbol for various alert conditions"""
        alerts = []
        current_id = start_id
        
        # Extreme sentiment alerts
        if data.overall_sentiment > self.alert_rules['sentiment_extreme_high']:
            alerts.append(AlertResponse(
                id=current_id,
                symbol=symbol,
                alert_type='sentiment',
                severity='high',
                message=f'Extremely positive sentiment detected ({data.overall_sentiment:.2f})',
                threshold_value=self.alert_rules['sentiment_extreme_high'],
                current_value=data.overall_sentiment,
                is_active=True,
                triggered_at=datetime.now()
            ))
            current_id += 1
            
        elif data.overall_sentiment < self.alert_rules['sentiment_extreme_low']:
            alerts.append(AlertResponse(
                id=current_id,
                symbol=symbol,
                alert_type='sentiment',
                severity='high',
                message=f'Extremely negative sentiment detected ({data.overall_sentiment:.2f})',
                threshold_value=self.alert_rules['sentiment_extreme_low'],
                current_value=data.overall_sentiment,
                is_active=True,
                triggered_at=datetime.now()
            ))
            current_id += 1

        # Moderate sentiment alerts
        elif data.overall_sentiment > self.alert_rules['sentiment_high']:
            alerts.append(AlertResponse(
                id=current_id,
                symbol=symbol,
                alert_type='sentiment',
                severity='medium',
                message=f'High positive sentiment detected ({data.overall_sentiment:.2f})',
                threshold_value=self.alert_rules['sentiment_high'],
                current_value=data.overall_sentiment,
                is_active=True,
                triggered_at=datetime.now()
            ))
            current_id += 1
            
        elif data.overall_sentiment < self.alert_rules['sentiment_low']:
            alerts.append(AlertResponse(
                id=current_id,
                symbol=symbol,
                alert_type='sentiment',
                severity='medium',
                message=f'High negative sentiment detected ({data.overall_sentiment:.2f})',
                threshold_value=self.alert_rules['sentiment_low'],
                current_value=data.overall_sentiment,
                is_active=True,
                triggered_at=datetime.now()
            ))
            current_id += 1

        # Sentiment trend alerts
        if data.sentiment_trend == 'improving':
            alerts.append(AlertResponse(
                id=current_id,
                symbol=symbol,
                alert_type='trend',
                severity='medium',
                message='Improving sentiment trend detected - positive momentum building',
                threshold_value=None,
                current_value=data.overall_sentiment,
                is_active=True,
                triggered_at=datetime.now()
            ))
            current_id += 1
            
        elif data.sentiment_trend == 'declining':
            alerts.append(AlertResponse(
                id=current_id,
                symbol=symbol,
                alert_type='trend',
                severity='medium',
                message='Declining sentiment trend detected - negative momentum building',
                threshold_value=None,
                current_value=data.overall_sentiment,
                is_active=True,
                triggered_at=datetime.now()
            ))
            current_id += 1

        # News volume alerts
        if data.total_articles > 15:
            alerts.append(AlertResponse(
                id=current_id,
                symbol=symbol,
                alert_type='volume',
                severity='low',
                message=f'High news activity detected ({data.total_articles} articles) - increased market attention',
                threshold_value=15.0,
                current_value=float(data.total_articles),
                is_active=True,
                triggered_at=datetime.now()
            ))
            current_id += 1
            
        elif data.total_articles < 3:
            alerts.append(AlertResponse(
                id=current_id,
                symbol=symbol,
                alert_type='volume',
                severity='low',
                message=f'Low news activity detected ({data.total_articles} articles) - limited information available',
                threshold_value=3.0,
                current_value=float(data.total_articles),
                is_active=True,
                triggered_at=datetime.now()
            ))
            current_id += 1

        # Confidence alerts
        if data.confidence < 0.4:
            alerts.append(AlertResponse(
                id=current_id,
                symbol=symbol,
                alert_type='confidence',
                severity='low',
                message=f'Mixed sentiment signals detected - conflicting market opinions (confidence: {data.confidence:.2f})',
                threshold_value=0.4,
                current_value=data.confidence,
                is_active=True,
                triggered_at=datetime.now()
            ))
            current_id += 1

        # Price correlation alerts
        if abs(data.price_correlation) > self.alert_rules['correlation_threshold']:
            correlation_type = "strong positive" if data.price_correlation > 0 else "strong negative"
            alerts.append(AlertResponse(
                id=current_id,
                symbol=symbol,
                alert_type='correlation',
                severity='low',
                message=f'{correlation_type.title()} price-sentiment correlation detected ({data.price_correlation:.2f})',
                threshold_value=self.alert_rules['correlation_threshold'],
                current_value=abs(data.price_correlation),
                is_active=True,
                triggered_at=datetime.now()
            ))
            current_id += 1

        # Sentiment distribution alerts
        total_articles = data.total_articles
        if total_articles > 0:
            positive_ratio = data.positive_count / total_articles
            negative_ratio = data.negative_count / total_articles
            
            if positive_ratio > 0.8:
                alerts.append(AlertResponse(
                    id=current_id,
                    symbol=symbol,
                    alert_type='distribution',
                    severity='medium',
                    message=f'Overwhelming positive news coverage ({positive_ratio:.0%} positive articles)',
                    threshold_value=0.8,
                    current_value=positive_ratio,
                    is_active=True,
                    triggered_at=datetime.now()
                ))
                current_id += 1
                
            elif negative_ratio > 0.8:
                alerts.append(AlertResponse(
                    id=current_id,
                    symbol=symbol,
                    alert_type='distribution',
                    severity='medium',
                    message=f'Overwhelming negative news coverage ({negative_ratio:.0%} negative articles)',
                    threshold_value=0.8,
                    current_value=negative_ratio,
                    is_active=True,
                    triggered_at=datetime.now()
                ))
                current_id += 1

        return alerts

    async def get_alerts(self, symbols: Optional[List[str]] = None, severity: Optional[str] = None) -> List[AlertResponse]:
        """Get filtered alerts based on symbols and severity"""
        # This would typically query the database for stored alerts
        # For now, return empty list as alerts are generated on-demand
        return []

    def update_alert_rules(self, new_rules: Dict[str, float]):
        """Update alert thresholds and rules"""
        self.alert_rules.update(new_rules)

    def get_alert_summary(self, alerts: List[AlertResponse]) -> Dict[str, Any]:
        """Generate summary statistics for alerts"""
        if not alerts:
            return {
                'total_alerts': 0,
                'by_severity': {'high': 0, 'medium': 0, 'low': 0},
                'by_type': {},
                'most_alerted_symbols': []
            }

        # Count by severity
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        for alert in alerts:
            severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1

        # Count by type
        type_counts = {}
        for alert in alerts:
            type_counts[alert.alert_type] = type_counts.get(alert.alert_type, 0) + 1

        # Count by symbol
        symbol_counts = {}
        for alert in alerts:
            symbol_counts[alert.symbol] = symbol_counts.get(alert.symbol, 0) + 1

        # Get most alerted symbols
        most_alerted = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'total_alerts': len(alerts),
            'by_severity': severity_counts,
            'by_type': type_counts,
            'most_alerted_symbols': [{'symbol': symbol, 'count': count} for symbol, count in most_alerted],
            'generated_at': datetime.now().isoformat()
        }