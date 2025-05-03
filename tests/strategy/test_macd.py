import pytest
import pandas as pd
import numpy as np
from AIQuantum.strategy.technical.macd import MACDStrategy

def test_macd_calculation():
    """Test MACD line, signal line, and histogram calculations."""
    # Create test data
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11]
    })
    
    strategy = MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
    signals = strategy.generate_signals(data)
    
    # Check if MACD components are present
    assert 'macd' in signals.columns
    assert 'signal_line' in signals.columns
    assert 'histogram' in signals.columns
    
    # Check signal values
    assert 'signal' in signals.columns
    assert signals['signal'].isin([-1, 0, 1]).all()
    
    # Check confidence values
    assert 'confidence' in signals.columns
    assert (signals['confidence'] >= 0).all()
    assert (signals['confidence'] <= 1).all()

def test_macd_crossovers():
    """Test MACD signal generation on crossovers."""
    # Create data with clear MACD crossovers
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11, 10, 9]
    })
    
    strategy = MACDStrategy(fast_period=3, slow_period=5, signal_period=2)
    signals = strategy.generate_signals(data)
    
    # Check for expected signal changes
    assert signals['signal'].notna().all()
    assert signals['confidence'].notna().all()

def test_macd_edge_cases():
    """Test MACD strategy with edge cases."""
    # Test with empty DataFrame
    empty_data = pd.DataFrame(columns=['close'])
    strategy = MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
    signals = strategy.generate_signals(empty_data)
    assert len(signals) == 0
    
    # Test with insufficient data
    small_data = pd.DataFrame({'close': [10, 11, 12]})
    signals = strategy.generate_signals(small_data)
    assert len(signals) == len(small_data)
    
    # Test with NaN values
    nan_data = pd.DataFrame({
        'close': [10, np.nan, 12, 13, np.nan, 15]
    })
    signals = strategy.generate_signals(nan_data)
    assert signals['signal'].notna().all() 