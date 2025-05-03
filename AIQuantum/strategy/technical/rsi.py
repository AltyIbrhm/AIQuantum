import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from ..base_strategy import BaseStrategy
from ...utils.logger import get_logger

class RSIStrategy(BaseStrategy):
    """
    Relative Strength Index (RSI) strategy implementation.
    Generates signals based on overbought/oversold conditions.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize RSI strategy with configuration.
        
        Args:
            config: Strategy configuration dictionary
        """
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        # Default configuration
        self.config = {
            'period': 14,
            'overbought': 70,
            'oversold': 30,
            'signal_threshold': 0.5
        }
        
        # Update with provided config
        if config:
            self.config.update(config)
        
        self.logger.info(f"Initialized RSI strategy with config: {self.config}")
    
    def calculate_rsi(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate RSI values for the given data.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with RSI values
        """
        try:
            # Calculate price changes
            delta = data['close'].diff()
            
            # Separate gains and losses
            gain = (delta.where(delta > 0, 0)).rolling(window=self.config['period']).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.config['period']).mean()
            
            # Calculate RS and RSI
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # Handle NaN values
            rsi = rsi.fillna(50)  # Neutral value for NaN
            
            self.logger.info(f"Calculated RSI with period {self.config['period']}")
            return rsi
            
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {str(e)}")
            raise
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate input data for RSI calculation.
        
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
                raise ValueError(f"Need at least {self.config['period']} data points for RSI calculation")
            
            return True
        except Exception as e:
            self.logger.error(f"Data validation failed: {str(e)}")
            return False
    
    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate trading signals based on RSI.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with signals
        """
        try:
            # Validate data
            if not self.validate_data(data):
                raise ValueError("Invalid data for signal calculation")
            
            # Calculate RSI
            rsi = self.calculate_rsi(data)
            
            # Initialize signals
            signals = pd.DataFrame(index=data.index)
            signals['rsi'] = rsi
            
            # Generate signals
            signals['signal'] = 0  # Default: hold
            
            # Overbought condition
            signals.loc[rsi > self.config['overbought'], 'signal'] = -1  # Sell
            
            # Oversold condition
            signals.loc[rsi < self.config['oversold'], 'signal'] = 1  # Buy
            
            # Add signal strength
            signals['strength'] = np.abs(rsi - 50) / 50  # Normalized to [0, 1]
            
            # Add metadata
            signals['strategy'] = 'rsi'
            signals['timestamp'] = signals.index
            
            self.logger.info(f"Generated {len(signals[signals['signal'] != 0])} signals")
            return signals
            
        except Exception as e:
            self.logger.error(f"Error calculating signals: {str(e)}")
            raise
    
    def get_position_size(self, data: pd.DataFrame, signal: float) -> float:
        """
        Calculate position size based on RSI signal strength.
        
        Args:
            data: DataFrame with OHLCV data
            signal: Current signal value
            
        Returns:
            Position size as a fraction of portfolio
        """
        try:
            # Get signal strength
            strength = np.abs(signal - 50) / 50
            
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
            'name': 'RSI Strategy',
            'version': '1.0.0',
            'parameters': self.config,
            'description': 'Generates signals based on RSI overbought/oversold conditions'
        } 