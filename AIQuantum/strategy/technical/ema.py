from typing import Dict, Any, List, Optional, Union
import numpy as np
import pandas as pd
from ..base_strategy import BaseStrategy
from ...utils.logger import get_logger

def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """Calculate Exponential Moving Average.
    
    Args:
        series: Price series
        period: EMA period
        
    Returns:
        Series with EMA values
    """
    return series.ewm(span=period, adjust=False).mean()

class EMAStrategy(BaseStrategy):
    """Trading strategy based on Exponential Moving Averages."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the EMA strategy.
        
        Args:
            config: Strategy configuration
        """
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        # EMA parameters
        self.fast_period = config.get('fast_period', 12)
        self.slow_period = config.get('slow_period', 26)
        self.signal_period = config.get('signal_period', 9)
        self.trend_period = config.get('trend_period', 50)
        
        # Signal thresholds
        self.signal_threshold = config.get('signal_threshold', 0.0)
        self.trend_threshold = config.get('trend_threshold', 0.01)
    
    def calculate_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trading signals based on EMA crossovers.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Dictionary containing signal information
        """
        try:
            if not self.validate_data(data):
                return {'signal': 0, 'strength': 0, 'metadata': {}}
            
            # Calculate EMAs
            fast_ema = calculate_ema(data['close'], self.fast_period)
            slow_ema = calculate_ema(data['close'], self.slow_period)
            trend_ema = calculate_ema(data['close'], self.trend_period)
            
            # Calculate signal line
            signal_line = calculate_ema(fast_ema - slow_ema, self.signal_period)
            
            # Get latest values
            current_fast = fast_ema.iloc[-1]
            current_slow = slow_ema.iloc[-1]
            current_trend = trend_ema.iloc[-1]
            current_signal = signal_line.iloc[-1]
            current_price = data['close'].iloc[-1]
            
            # Calculate distances
            fast_slow_dist = (current_fast - current_slow) / current_slow
            price_trend_dist = (current_price - current_trend) / current_trend
            
            # Determine signal
            signal = 0
            if fast_slow_dist > self.signal_threshold:
                signal = 1 if price_trend_dist > self.trend_threshold else 0
            elif fast_slow_dist < -self.signal_threshold:
                signal = -1 if price_trend_dist < -self.trend_threshold else 0
            
            # Calculate signal strength based on distance and trend alignment
            strength = min(1.0, abs(fast_slow_dist) * 5)  # Scale up for stronger signals
            if signal != 0:
                strength *= abs(price_trend_dist) * 2  # Boost strength if trend aligned
            
            return {
                'signal': signal,
                'strength': strength * signal,  # Signed strength
                'metadata': {
                    'fast_ema': current_fast,
                    'slow_ema': current_slow,
                    'trend_ema': current_trend,
                    'signal_line': current_signal,
                    'fast_slow_dist': fast_slow_dist,
                    'price_trend_dist': price_trend_dist
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating signals: {str(e)}")
            return {'signal': 0, 'strength': 0, 'metadata': {'error': str(e)}}
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate input data meets EMA requirements.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        try:
            # Call parent validation
            if not super().validate_data(data):
                return False
            
            # Check minimum data points for longest EMA
            required_points = max(self.fast_period, self.slow_period, self.trend_period) * 2
            if len(data) < required_points:
                self.logger.error(f"Insufficient data points. Need at least {required_points}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating data: {str(e)}")
            return False
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the EMA strategy.
        
        Returns:
            Dictionary containing strategy metadata
        """
        metadata = super().get_metadata()
        metadata.update({
            'periods': {
                'fast': self.fast_period,
                'slow': self.slow_period,
                'signal': self.signal_period,
                'trend': self.trend_period
            },
            'thresholds': {
                'signal': self.signal_threshold,
                'trend': self.trend_threshold
            }
        })
        return metadata

    def get_position_size(self, data: pd.DataFrame, signal: float) -> float:
        """
        Calculate position size based on EMA signal strength.
        
        Args:
            data: DataFrame with OHLCV data
            signal: Current signal value
            
        Returns:
            Position size as a fraction of portfolio
        """
        try:
            # Get signal strength
            strength = np.abs(signal)
            
            # Scale position size based on signal strength
            base_size = self.config.get('position_size', 0.1)
            position_size = base_size * strength
            
            # Apply risk limits
            max_size = self.config.get('max_position_size', 0.2)
            position_size = min(position_size, max_size)
            
            return position_size
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return 0.0 