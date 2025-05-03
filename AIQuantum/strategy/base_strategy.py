from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from ..utils.logger import get_logger

class BaseStrategy(ABC):
    """Abstract base class for all trading strategies."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the strategy with configuration."""
        self.config = config
        self.logger = get_logger(__name__)
        self.name = config.get('name', self.__class__.__name__)
        self.required_columns = ['open', 'high', 'low', 'close', 'volume']
        self.min_data_points = config.get('min_data_points', 100)
        self.position_size_limits = {
            'min': config.get('min_position_size', 0.01),
            'max': config.get('max_position_size', 1.0)
        }
    
    @abstractmethod
    def calculate_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trading signals from the data.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Dictionary containing signal information
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate input data meets requirements.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        try:
            # Check data type
            if not isinstance(data, pd.DataFrame):
                self.logger.error("Input data must be a pandas DataFrame")
                return False
            
            # Check required columns
            missing_cols = [col for col in self.required_columns if col not in data.columns]
            if missing_cols:
                self.logger.error(f"Missing required columns: {missing_cols}")
                return False
            
            # Check data length
            if len(data) < self.min_data_points:
                self.logger.error(f"Insufficient data points. Need at least {self.min_data_points}")
                return False
            
            # Check for NaN values
            if data[self.required_columns].isnull().any().any():
                self.logger.warning("Data contains NaN values")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating data: {str(e)}")
            return False
    
    def get_position_size(self, signal_strength: float) -> float:
        """Calculate position size based on signal strength.
        
        Args:
            signal_strength: Float between -1 and 1 indicating signal strength
            
        Returns:
            float: Position size as a percentage of available capital
        """
        try:
            # Ensure signal strength is between -1 and 1
            signal_strength = np.clip(signal_strength, -1, 1)
            
            # Calculate base position size
            base_size = abs(signal_strength) * self.position_size_limits['max']
            
            # Apply limits
            position_size = np.clip(
                base_size,
                self.position_size_limits['min'],
                self.position_size_limits['max']
            )
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return 0.0
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the strategy.
        
        Returns:
            Dictionary containing strategy metadata
        """
        return {
            'name': self.name,
            'type': self.__class__.__name__,
            'required_columns': self.required_columns,
            'min_data_points': self.min_data_points,
            'position_size_limits': self.position_size_limits,
            'config': self.config
        } 