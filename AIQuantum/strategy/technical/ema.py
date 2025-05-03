import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from ..base_strategy import BaseStrategy
from ...utils.logger import get_logger

class EMAStrategy(BaseStrategy):
    """
    Exponential Moving Average (EMA) strategy implementation.
    Generates signals based on EMA crossovers and price position relative to EMAs.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize EMA strategy with configuration.
        
        Args:
            config: Strategy configuration dictionary
        """
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        # Default configuration
        self.config = {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9,
            'trend_period': 50,
            'signal_threshold': 0.5
        }
        
        # Update with provided config
        if config:
            self.config.update(config)
        
        self.logger.info(f"Initialized EMA strategy with config: {self.config}")
    
    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """
        Calculate EMA for the given data.
        
        Args:
            data: Series with price data
            period: EMA period
            
        Returns:
            Series with EMA values
        """
        try:
            ema = data.ewm(span=period, adjust=False).mean()
            return ema
        except Exception as e:
            self.logger.error(f"Error calculating EMA: {str(e)}")
            raise
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate input data for EMA calculation.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            True if data is valid
        """
        try:
            # Check required columns
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in data.columns for col in required_columns):
                raise ValueError(f"Missing required columns. Need: {required_columns}")
            
            # Check for NaN values
            if data[required_columns].isnull().any().any():
                self.logger.warning("Data contains NaN values")
            
            # Check for sufficient data points
            max_period = max(self.config['fast_period'], 
                           self.config['slow_period'],
                           self.config['signal_period'],
                           self.config['trend_period'])
            if len(data) < max_period:
                raise ValueError(f"Need at least {max_period} data points for EMA calculation")
            
            return True
        except Exception as e:
            self.logger.error(f"Data validation failed: {str(e)}")
            return False
    
    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate trading signals based on EMAs.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with signals
        """
        try:
            # Validate data
            if not self.validate_data(data):
                raise ValueError("Invalid data for signal calculation")
            
            # Calculate EMAs
            fast_ema = self.calculate_ema(data['close'], self.config['fast_period'])
            slow_ema = self.calculate_ema(data['close'], self.config['slow_period'])
            trend_ema = self.calculate_ema(data['close'], self.config['trend_period'])
            
            # Initialize signals
            signals = pd.DataFrame(index=data.index)
            signals['fast_ema'] = fast_ema
            signals['slow_ema'] = slow_ema
            signals['trend_ema'] = trend_ema
            
            # Generate signals
            signals['signal'] = 0  # Default: hold
            
            # Bullish crossover (fast EMA crosses above slow EMA)
            signals.loc[fast_ema > slow_ema, 'signal'] = 1  # Buy
            
            # Bearish crossover (fast EMA crosses below slow EMA)
            signals.loc[fast_ema < slow_ema, 'signal'] = -1  # Sell
            
            # Add trend strength
            signals['trend_strength'] = np.abs(fast_ema - slow_ema) / slow_ema
            
            # Add signal strength
            signals['strength'] = signals['trend_strength'] * signals['signal'].abs()
            
            # Add metadata
            signals['strategy'] = 'ema'
            signals['timestamp'] = signals.index
            
            self.logger.info(f"Generated {len(signals[signals['signal'] != 0])} signals")
            return signals
            
        except Exception as e:
            self.logger.error(f"Error calculating signals: {str(e)}")
            raise
    
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
    
    def get_metadata(self) -> Dict:
        """
        Get strategy metadata.
        
        Returns:
            Dictionary with strategy metadata
        """
        return {
            'name': 'EMA Strategy',
            'version': '1.0.0',
            'parameters': self.config,
            'description': 'Generates signals based on EMA crossovers and trend strength'
        } 