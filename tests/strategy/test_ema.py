import pytest
import pandas as pd
import numpy as np
from AIQuantum.strategy.technical.ema import EMAStrategy

def test_ema_basic():
    """Test basic EMA calculation and signal generation."""
    # Create test data
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11]
    })
    
    strategy = EMAStrategy(short_window=3, long_window=5)
    signals = strategy.generate_signals(data)
    
    # Check if signals DataFrame has required columns
    assert 'signal' in signals.columns
    assert 'confidence' in signals.columns
    
    # Check signal values (should be -1, 0, or 1)
    assert signals['signal'].isin([-1, 0, 1]).all()
    
    # Check confidence values (should be between 0 and 1)
    assert (signals['confidence'] >= 0).all()
    assert (signals['confidence'] <= 1).all()

def test_ema_with_volatility():
    """Test EMA strategy with volatile price movements."""
    # Create test data with volatility
    data = pd.DataFrame({
        'close': [10, 12, 8, 15, 7, 16, 6, 17, 5, 18]
    })
    
    strategy = EMAStrategy(short_window=2, long_window=4)
    signals = strategy.generate_signals(data)
    
    # Check if signals are generated correctly for volatile data
    assert len(signals) == len(data)
    assert signals['signal'].notna().all()
    assert signals['confidence'].notna().all()

def test_ema_edge_cases():
    """Test EMA strategy with edge cases."""
    # Test with empty DataFrame
    empty_data = pd.DataFrame(columns=['close'])
    strategy = EMAStrategy(short_window=3, long_window=5)
    signals = strategy.generate_signals(empty_data)
    assert len(signals) == 0
    
    # Test with single value
    single_data = pd.DataFrame({'close': [10]})
    signals = strategy.generate_signals(single_data)
    assert len(signals) == 1
    assert signals['signal'].iloc[0] == 0  # Should be neutral
    
    # Test with NaN values
    nan_data = pd.DataFrame({
        'close': [10, np.nan, 12, 13, np.nan, 15]
    })
    signals = strategy.generate_signals(nan_data)
    assert signals['signal'].notna().all()  # Should handle NaN values 