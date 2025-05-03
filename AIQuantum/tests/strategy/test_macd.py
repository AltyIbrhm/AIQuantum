import pytest
import pandas as pd
import numpy as np
from AIQuantum.strategy.technical.macd import MACDStrategy

def test_macd_calculation():
    """Test MACD line, signal line, and histogram calculations."""
    # Create test data
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
        'trend_period': 50,
        'signal_threshold': 0.5,
        'momentum_threshold': 0.1,
        'divergence_lookback': 14
    }
    strategy = MACDStrategy(config=config)
    signals = strategy.calculate_signals(data)
    
    # Check if MACD components are present
    assert 'macd_line' in signals.columns
    assert 'signal_line' in signals.columns
    assert 'histogram' in signals.columns
    assert 'trend_ema' in signals.columns
    
    # Check signal values
    assert 'signal' in signals.columns
    assert signals['signal'].isin([-1, 0, 1]).all()
    
    # Check strength values
    assert 'strength' in signals.columns
    assert not signals['strength'].isnull().any()  # No NaN values
    assert (signals['strength'].abs() <= 1).all()  # Values between -1 and 1
    
    # Check momentum values
    assert 'momentum' in signals.columns
    assert 'momentum_strength' in signals.columns
    
    # Check trend values
    assert 'trend_strength' in signals.columns
    
    # Check divergence detection
    assert 'price_high' in signals.columns
    assert 'price_low' in signals.columns
    assert 'macd_high' in signals.columns
    assert 'macd_low' in signals.columns
    
    # Check metadata
    assert 'strategy' in signals.columns
    assert 'timestamp' in signals.columns

def test_macd_crossovers():
    """Test MACD signal generation on crossovers."""
    # Create data with clear MACD crossovers
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11, 10, 9] * 15,  # Multiply by 15 to meet minimum data points
        'open': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11, 10, 9] * 15,
        'high': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11, 10, 9] * 15,
        'low': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11, 10, 9] * 15,
        'volume': [1000] * 180
    })
    
    config = {
        'fast_period': 3,
        'slow_period': 5,
        'signal_period': 2,
        'trend_period': 10,
        'signal_threshold': 0.5,
        'momentum_threshold': 0.1,
        'divergence_lookback': 14
    }
    strategy = MACDStrategy(config=config)
    signals = strategy.calculate_signals(data)
    
    # Check for expected signal changes
    assert signals['signal'].notna().all()
    assert 'momentum' in signals.columns
    assert 'momentum_strength' in signals.columns
    assert 'trend_strength' in signals.columns

def test_macd_edge_cases():
    """Test MACD strategy with edge cases."""
    # Test with empty DataFrame
    empty_data = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
    config = {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9,
        'trend_period': 50,
        'signal_threshold': 0.5,
        'momentum_threshold': 0.1,
        'divergence_lookback': 14
    }
    strategy = MACDStrategy(config=config)
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
        'close': [10, np.nan, 12, 13, np.nan, 15] * 25,  # Multiply by 25 to meet minimum data points
        'open': [10, 11, 12, 13, 14, 15] * 25,
        'high': [10, 11, 12, 13, 14, 15] * 25,
        'low': [10, 11, 12, 13, 14, 15] * 25,
        'volume': [1000] * 150
    })
    signals = strategy.calculate_signals(nan_data)
    assert signals['signal'].notna().all()  # Should handle NaN values 