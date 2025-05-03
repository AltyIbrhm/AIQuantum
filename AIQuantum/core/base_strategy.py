from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    All strategy implementations must inherit from this class.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the strategy with configuration.
        
        Args:
            config: Strategy-specific configuration dictionary
        """
        self.config = config
        self.name = config.get('name', self.__class__.__name__)
        self.enabled = config.get('enabled', True)
        
    @abstractmethod
    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate trading signals based on the input data.
        
        Args:
            data: DataFrame containing price and indicator data
            
        Returns:
            DataFrame with signal columns added
        """
        pass
    
    @abstractmethod
    def get_position_size(self, signal: float, price: float, balance: float) -> float:
        """
        Calculate the position size based on the signal and current balance.
        
        Args:
            signal: Signal strength (-1 to 1)
            price: Current price
            balance: Available balance
            
        Returns:
            Position size in base currency
        """
        pass
    
    def get_confidence(self, signal: float) -> float:
        """
        Calculate confidence level for the signal.
        Default implementation returns absolute value of signal.
        
        Args:
            signal: Signal strength (-1 to 1)
            
        Returns:
            Confidence level (0 to 1)
        """
        return abs(signal)
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate input data before processing.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        return all(col in data.columns for col in required_columns)
    
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess input data before signal calculation.
        
        Args:
            data: Raw input data
            
        Returns:
            Preprocessed data
        """
        return data.copy()
    
    def postprocess_signals(self, signals: pd.DataFrame) -> pd.DataFrame:
        """
        Postprocess signals after calculation.
        
        Args:
            signals: DataFrame with calculated signals
            
        Returns:
            Processed signals
        """
        return signals.copy()
    
    def get_required_indicators(self) -> List[str]:
        """
        Get list of required technical indicators.
        
        Returns:
            List of indicator names
        """
        return []
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get current strategy parameters.
        
        Returns:
            Dictionary of parameters
        """
        return self.config.get('parameters', {})
    
    def update_parameters(self, new_params: Dict[str, Any]) -> None:
        """
        Update strategy parameters.
        
        Args:
            new_params: Dictionary of new parameters
        """
        if 'parameters' not in self.config:
            self.config['parameters'] = {}
        self.config['parameters'].update(new_params) 