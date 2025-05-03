import pytest
import pandas as pd
import numpy as np
from AIQuantum.strategy.technical.bollinger import BollingerStrategy

def test_bollinger_bands_calculation():
    """Test Bollinger Bands calculation and signal generation."""
    # Create test data
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,  # Multiply by 5 to meet minimum data points
        'open': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,
        'high': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,
        'low': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,
        'volume': [1000] * 50
    })
    
    config = {
        'period': 20,
        'std_dev': 2.0
    }
    strategy = BollingerStrategy(config=config)
    signals = strategy.calculate_signals(data)
    
    # Check if Bollinger Bands components are present
    assert 'upper_band' in signals.columns
    assert 'middle_band' in signals.columns
    assert 'lower_band' in signals.columns
    
    # Check signal values
    assert 'signal' in signals.columns
    assert signals['signal'].isin([-1, 0, 1]).all()
    
    # Check strength values
    assert 'strength' in signals.columns
    assert (signals['strength'] >= 0).all()

def test_bollinger_squeeze():
    """Test Bollinger Bands squeeze detection."""
    # Create data with a squeeze pattern
    data = pd.DataFrame({
        'close': [10, 10.1, 10.2, 10.1, 10, 10.1, 10.2, 10.1, 10, 10.1] * 5,  # Multiply by 5 to meet minimum data points
        'open': [10, 10.1, 10.2, 10.1, 10, 10.1, 10.2, 10.1, 10, 10.1] * 5,
        'high': [10, 10.1, 10.2, 10.1, 10, 10.1, 10.2, 10.1, 10, 10.1] * 5,
        'low': [10, 10.1, 10.2, 10.1, 10, 10.1, 10.2, 10.1, 10, 10.1] * 5,
        'volume': [1000] * 50
    })
    
    config = {
        'period': 5,
        'std_dev': 1.0,
        'squeeze_threshold': 0.5
    }
    strategy = BollingerStrategy(config=config)
    signals = strategy.calculate_signals(data)
    
    # Check squeeze detection
    assert 'squeeze' in signals.columns
    assert signals['squeeze'].dtype == bool

def test_bollinger_reversion():
    """Test mean reversion signals."""
    # Create data with clear mean reversion opportunities
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,  # Multiply by 5 to meet minimum data points
        'open': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,
        'high': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,
        'low': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,
        'volume': [1000] * 50
    })
    
    config = {
        'period': 5,
        'std_dev': 1.0,
        'reversion_threshold': 0.1
    }
    strategy = BollingerStrategy(config=config)
    signals = strategy.calculate_signals(data)
    
    # Check reversion signals
    assert signals['signal'].notna().all()
    assert 'reversion' in signals.columns

def test_bollinger_edge_cases():
    """Test Bollinger Bands strategy with edge cases."""
    # Test with empty DataFrame
    empty_data = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
    config = {
        'period': 20,
        'std_dev': 2.0
    }
    strategy = BollingerStrategy(config=config)
    with pytest.raises(ValueError):
        signals = strategy.calculate_signals(empty_data)
    
    # Test with insufficient data
    small_data = pd.DataFrame({
        'close': [10, 11, 12],
        'open': [10, 11, 12],
        'high': [10, 11, 12],
        'low': [10, 11, 12],
        'volume': [1000] * 3
    })
    with pytest.raises(ValueError):
        signals = strategy.calculate_signals(small_data)
    
    # Test with NaN values
    nan_data = pd.DataFrame({
        'close': [10, np.nan, 12, 13, np.nan, 15] * 10,  # Multiply by 10 to meet minimum data points
        'open': [10, 11, 12, 13, 14, 15] * 10,
        'high': [10, 11, 12, 13, 14, 15] * 10,
        'low': [10, 11, 12, 13, 14, 15] * 10,
        'volume': [1000] * 60
    })
    signals = strategy.calculate_signals(nan_data)
    assert signals['signal'].notna().all()  # Should handle NaN values 