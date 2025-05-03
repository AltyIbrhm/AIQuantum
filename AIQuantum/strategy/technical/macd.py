import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from ..base_strategy import BaseStrategy
from ...utils.logger import get_logger

class MACDStrategy(BaseStrategy):
    """
    Moving Average Convergence Divergence (MACD) strategy implementation.
    Generates signals based on MACD line crossovers, histogram momentum, and trend filtering.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize MACD strategy with configuration.
        
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
            'signal_threshold': 0.5,
            'momentum_threshold': 0.1,
            'divergence_lookback': 14
        }
        
        # Update with provided config
        if config:
            self.config.update(config)
        
        self.logger.info(f"Initialized MACD strategy with config: {self.config}")
    
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
    
    def calculate_macd(self, data: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD components.
        
        Args:
            data: Series with price data
            
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        try:
            # Calculate fast and slow EMAs
            fast_ema = self.calculate_ema(data, self.config['fast_period'])
            slow_ema = self.calculate_ema(data, self.config['slow_period'])
            
            # Calculate MACD line
            macd_line = fast_ema - slow_ema
            
            # Calculate signal line
            signal_line = self.calculate_ema(macd_line, self.config['signal_period'])
            
            # Calculate histogram
            histogram = macd_line - signal_line
            
            return macd_line, signal_line, histogram
        except Exception as e:
            self.logger.error(f"Error calculating MACD: {str(e)}")
            raise
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate input data for MACD calculation.
        
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
                raise ValueError(f"Need at least {max_period} data points for MACD calculation")
            
            return True
        except Exception as e:
            self.logger.error(f"Data validation failed: {str(e)}")
            return False
    
    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate trading signals based on MACD.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with signals
        """
        try:
            # Validate data
            if not self.validate_data(data):
                raise ValueError("Invalid data for signal calculation")
            
            # Calculate MACD components
            macd_line, signal_line, histogram = self.calculate_macd(data['close'])
            
            # Calculate trend EMA
            trend_ema = self.calculate_ema(data['close'], self.config['trend_period'])
            
            # Initialize signals
            signals = pd.DataFrame(index=data.index)
            signals['macd_line'] = macd_line
            signals['signal_line'] = signal_line
            signals['histogram'] = histogram
            signals['trend_ema'] = trend_ema
            
            # Generate signals
            signals['signal'] = 0  # Default: hold
            
            # Bullish crossover (MACD crosses above Signal)
            signals.loc[(macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1)), 'signal'] = 1
            
            # Bearish crossover (MACD crosses below Signal)
            signals.loc[(macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1)), 'signal'] = -1
            
            # Add momentum strength
            signals['momentum'] = histogram.diff()
            signals['momentum_strength'] = np.abs(signals['momentum'])
            
            # Add trend strength
            signals['trend_strength'] = np.abs(macd_line - signal_line) / signal_line
            
            # Add signal strength
            signals['strength'] = signals['trend_strength'] * signals['signal'].abs()
            
            # Add divergence detection
            signals['price_high'] = data['high'].rolling(window=self.config['divergence_lookback']).max()
            signals['price_low'] = data['low'].rolling(window=self.config['divergence_lookback']).min()
            signals['macd_high'] = macd_line.rolling(window=self.config['divergence_lookback']).max()
            signals['macd_low'] = macd_line.rolling(window=self.config['divergence_lookback']).min()
            
            # Add metadata
            signals['strategy'] = 'macd'
            signals['timestamp'] = signals.index
            
            self.logger.info(f"Generated {len(signals[signals['signal'] != 0])} signals")
            return signals
            
        except Exception as e:
            self.logger.error(f"Error calculating signals: {str(e)}")
            raise
    
    def get_position_size(self, data: pd.DataFrame, signal: float) -> float:
        """
        Calculate position size based on MACD signal strength and momentum.
        
        Args:
            data: DataFrame with OHLCV data
            signal: Current signal value
            
        Returns:
            Position size as a fraction of portfolio
        """
        try:
            # Get signal strength
            strength = np.abs(signal)
            
            # Get momentum strength
            macd_line, signal_line, histogram = self.calculate_macd(data['close'])
            momentum = np.abs(histogram.iloc[-1])
            
            # Scale position size based on signal and momentum strength
            base_size = self.config.get('position_size', 0.1)
            position_size = base_size * strength * (1 + momentum)
            
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
            'name': 'MACD Strategy',
            'version': '1.0.0',
            'parameters': self.config,
            'description': 'Generates signals based on MACD crossovers, momentum, and trend confirmation'
        } 