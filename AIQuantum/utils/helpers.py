from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

class Helpers:
    """Utility helper functions for the AIQuantum project."""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
        """Validate that a DataFrame has required columns and no NaN values."""
        if not isinstance(df, pd.DataFrame):
            return False
        
        # Check required columns
        if not all(col in df.columns for col in required_columns):
            return False
        
        # Check for NaN values
        if df[required_columns].isnull().any().any():
            return False
            
        return True
    
    @staticmethod
    def calculate_returns(prices: Union[pd.Series, np.ndarray]) -> np.ndarray:
        """Calculate percentage returns from a price series."""
        if isinstance(prices, pd.Series):
            prices = prices.values
        return np.diff(prices) / prices[:-1]
    
    @staticmethod
    def calculate_volatility(returns: Union[pd.Series, np.ndarray], window: int = 20) -> np.ndarray:
        """Calculate rolling volatility from returns."""
        if isinstance(returns, pd.Series):
            returns = returns.values
        return pd.Series(returns).rolling(window=window).std().values
    
    @staticmethod
    def normalize_signal(signal: Union[pd.Series, np.ndarray], min_val: float = -1, max_val: float = 1) -> np.ndarray:
        """Normalize a signal to a specified range."""
        if isinstance(signal, pd.Series):
            signal = signal.values
        signal_min = np.nanmin(signal)
        signal_max = np.nanmax(signal)
        if signal_max == signal_min:
            return np.zeros_like(signal)
        return min_val + (signal - signal_min) * (max_val - min_val) / (signal_max - signal_min)
    
    @staticmethod
    def calculate_zscore(series: Union[pd.Series, np.ndarray], window: int = 20) -> np.ndarray:
        """Calculate rolling z-score of a series."""
        if isinstance(series, pd.Series):
            series = series.values
        rolling_mean = pd.Series(series).rolling(window=window).mean()
        rolling_std = pd.Series(series).rolling(window=window).std()
        return (series - rolling_mean) / rolling_std
    
    @staticmethod
    def detect_outliers(series: Union[pd.Series, np.ndarray], threshold: float = 3.0) -> np.ndarray:
        """Detect outliers using z-score method."""
        zscore = Helpers.calculate_zscore(series)
        return np.abs(zscore) > threshold 