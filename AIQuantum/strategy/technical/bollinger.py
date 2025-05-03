import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from ..base_strategy import BaseStrategy
from ...utils.logger import get_logger

class BollingerStrategy(BaseStrategy):
    """
    Bollinger Bands strategy implementation.
    Generates signals based on price position relative to bands, volatility, and mean-reversion.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Bollinger Bands strategy with configuration.
        
        Args:
            config: Strategy configuration dictionary
        """
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        # Default configuration
        self.config = {
            'period': 20,
            'std_dev': 2.0,
            'squeeze_threshold': 0.5,
            'reversion_threshold': 0.1,
            'trend_period': 50,
            'signal_threshold': 0.5,
            'min_band_width': 0.01
        }
        
        # Update with provided config
        if config:
            self.config.update(config)
        
        self.logger.info(f"Initialized Bollinger strategy with config: {self.config}")
    
    def calculate_bands(self, data: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands components.
        
        Args:
            data: Series with price data
            
        Returns:
            Tuple of (middle band, upper band, lower band)
        """
        try:
            # Calculate middle band (SMA)
            middle_band = data.rolling(window=self.config['period']).mean()
            
            # Calculate standard deviation
            std_dev = data.rolling(window=self.config['period']).std()
            
            # Calculate upper and lower bands
            upper_band = middle_band + (self.config['std_dev'] * std_dev)
            lower_band = middle_band - (self.config['std_dev'] * std_dev)
            
            return middle_band, upper_band, lower_band
        except Exception as e:
            self.logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            raise
    
    def calculate_band_width(self, middle: pd.Series, upper: pd.Series, lower: pd.Series) -> pd.Series:
        """
        Calculate Bollinger Band width.
        
        Args:
            middle: Middle band values
            upper: Upper band values
            lower: Lower band values
            
        Returns:
            Series with band width values
        """
        try:
            return (upper - lower) / middle
        except Exception as e:
            self.logger.error(f"Error calculating band width: {str(e)}")
            raise
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate input data for Bollinger Bands calculation.
        
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
            if len(data) < self.config['period']:
                raise ValueError(f"Need at least {self.config['period']} data points for Bollinger Bands calculation")
            
            return True
        except Exception as e:
            self.logger.error(f"Data validation failed: {str(e)}")
            return False
    
    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate trading signals based on Bollinger Bands.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with signals
        """
        try:
            # Validate data
            if not self.validate_data(data):
                raise ValueError("Invalid data for signal calculation")
            
            # Calculate Bollinger Bands
            middle_band, upper_band, lower_band = self.calculate_bands(data['close'])
            
            # Calculate band width
            band_width = self.calculate_band_width(middle_band, upper_band, lower_band)
            
            # Calculate trend EMA
            trend_ema = data['close'].ewm(span=self.config['trend_period'], adjust=False).mean()
            
            # Initialize signals
            signals = pd.DataFrame(index=data.index)
            signals['middle_band'] = middle_band
            signals['upper_band'] = upper_band
            signals['lower_band'] = lower_band
            signals['band_width'] = band_width
            signals['trend_ema'] = trend_ema
            
            # Generate signals
            signals['signal'] = 0  # Default: hold
            
            # Mean reversion signals
            # Buy when price closes below lower band and starts moving up
            signals.loc[
                (data['close'] < lower_band) & 
                (data['close'] > data['close'].shift(1)) & 
                (band_width > self.config['min_band_width']),
                'signal'
            ] = 1
            
            # Sell when price closes above upper band and starts moving down
            signals.loc[
                (data['close'] > upper_band) & 
                (data['close'] < data['close'].shift(1)) & 
                (band_width > self.config['min_band_width']),
                'signal'
            ] = -1
            
            # Add squeeze detection
            signals['squeeze'] = band_width < self.config['squeeze_threshold']
            
            # Add reversion detection
            signals['reversion'] = (
                (data['close'].shift(1) < lower_band.shift(1)) & 
                (data['close'] > lower_band) & 
                (band_width > self.config['min_band_width'])
            ) | (
                (data['close'].shift(1) > upper_band.shift(1)) & 
                (data['close'] < upper_band) & 
                (band_width > self.config['min_band_width'])
            )
            
            # Add signal strength
            signals['strength'] = np.abs(data['close'] - middle_band) / middle_band
            
            # Add volatility metric
            signals['volatility'] = band_width
            
            # Add metadata
            signals['strategy'] = 'bollinger'
            signals['timestamp'] = signals.index
            
            self.logger.info(f"Generated {len(signals[signals['signal'] != 0])} signals")
            return signals
            
        except Exception as e:
            self.logger.error(f"Error calculating signals: {str(e)}")
            raise
    
    def get_position_size(self, data: pd.DataFrame, signal: float) -> float:
        """
        Calculate position size based on Bollinger Bands signal strength and volatility.
        
        Args:
            data: DataFrame with OHLCV data
            signal: Current signal value
            
        Returns:
            Position size as a fraction of portfolio
        """
        try:
            # Get signal strength
            strength = np.abs(signal)
            
            # Calculate bands for volatility
            middle_band, upper_band, lower_band = self.calculate_bands(data['close'])
            band_width = self.calculate_band_width(middle_band, upper_band, lower_band)
            
            # Scale position size based on signal strength and volatility
            base_size = self.config.get('position_size', 0.1)
            volatility_factor = 1 + band_width.iloc[-1]  # Higher volatility = larger position
            position_size = base_size * strength * volatility_factor
            
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
            'name': 'Bollinger Bands Strategy',
            'version': '1.0.0',
            'parameters': self.config,
            'description': 'Generates signals based on price position relative to Bollinger Bands, volatility, and mean-reversion'
        } 