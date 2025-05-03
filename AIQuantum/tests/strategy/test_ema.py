import pytest
import pandas as pd
import numpy as np
from AIQuantum.strategy.technical.ema import EMAStrategy

def test_ema_basic():
    """Test basic EMA calculation and signal generation."""
    # Create test data with sufficient points
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 15,  # Multiply by 15 to meet minimum data points
        'open': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 15,
        'high': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 15,
        'low': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 15,
        'volume': [1000] * 150
    })
    
    config = {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9,
        'trend_period': 50
    }
    strategy = EMAStrategy(config=config)
    signals = strategy.calculate_signals(data)
    
    # Check if signals DataFrame has required columns
    assert 'signal' in signals
    assert 'strength' in signals
    assert 'metadata' in signals
    
    # Check signal values (should be -1, 0, or 1)
    assert signals['signal'] in [-1, 0, 1]
    
    # Check strength values (should be between 0 and 1)
    assert isinstance(signals['strength'], float)
    assert -1 <= signals['strength'] <= 1

def test_ema_with_volatility():
    """Test EMA strategy with volatile price movements."""
    # Create test data with volatility
    data = pd.DataFrame({
        'close': [10, 12, 8, 15, 7, 16, 6, 17, 5, 18] * 15,  # Multiply by 15 to meet minimum data points
        'open': [10, 12, 8, 15, 7, 16, 6, 17, 5, 18] * 15,
        'high': [10, 12, 8, 15, 7, 16, 6, 17, 5, 18] * 15,
        'low': [10, 12, 8, 15, 7, 16, 6, 17, 5, 18] * 15,
        'volume': [1000] * 150
    })
    
    config = {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9,
        'trend_period': 50
    }
    strategy = EMAStrategy(config=config)
    signals = strategy.calculate_signals(data)
    
    # Check if signals are generated correctly for volatile data
    assert 'signal' in signals
    assert 'strength' in signals
    assert 'metadata' in signals

def test_ema_edge_cases():
    """Test EMA strategy with edge cases."""
    config = {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9,
        'trend_period': 50
    }
    strategy = EMAStrategy(config=config)
    
    # Test with empty DataFrame
    empty_data = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
    result = strategy.calculate_signals(empty_data)
    assert result['signal'] == 0
    assert result['strength'] == 0
    
    # Test with insufficient data
    small_data = pd.DataFrame({
        'close': [10, 11, 12],
        'open': [10, 11, 12],
        'high': [10, 11, 12],
        'low': [10, 11, 12],
        'volume': [1000] * 3
    })
    result = strategy.calculate_signals(small_data)
    assert result['signal'] == 0
    assert result['strength'] == 0
    
    # Test with NaN values
    nan_data = pd.DataFrame({
        'close': [10, np.nan, 12, 13, np.nan, 15] * 25,  # Multiply by 25 to meet minimum data points
        'open': [10, 11, 12, 13, 14, 15] * 25,
        'high': [10, 11, 12, 13, 14, 15] * 25,
        'low': [10, 11, 12, 13, 14, 15] * 25,
        'volume': [1000] * 150
    })
    result = strategy.calculate_signals(nan_data)
    assert result['signal'] == 0  # Should handle NaN values 