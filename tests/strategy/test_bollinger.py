import pytest
import pandas as pd
import numpy as np
from AIQuantum.strategy.technical.bollinger import BollingerBandsStrategy

def test_bollinger_bands_calculation():
    """Test Bollinger Bands calculation and signal generation."""
    # Create test data
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11]
    })
    
    strategy = BollingerBandsStrategy(window=20, num_std=2)
    signals = strategy.generate_signals(data)
    
    # Check if Bollinger Bands components are present
    assert 'upper_band' in signals.columns
    assert 'middle_band' in signals.columns
    assert 'lower_band' in signals.columns
    
    # Check signal values
    assert 'signal' in signals.columns
    assert signals['signal'].isin([-1, 0, 1]).all()
    
    # Check confidence values
    assert 'confidence' in signals.columns
    assert (signals['confidence'] >= 0).all()
    assert (signals['confidence'] <= 1).all()

def test_bollinger_squeeze():
    """Test Bollinger Bands squeeze detection."""
    # Create data with a squeeze pattern
    data = pd.DataFrame({
        'close': [10, 10.1, 10.2, 10.1, 10, 10.1, 10.2, 10.1, 10, 10.1]
    })
    
    strategy = BollingerBandsStrategy(window=5, num_std=1)
    signals = strategy.generate_signals(data)
    
    # Check squeeze detection
    assert 'squeeze' in signals.columns
    assert signals['squeeze'].dtype == bool

def test_bollinger_reversion():
    """Test mean reversion signals."""
    # Create data with clear mean reversion opportunities
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11]
    })
    
    strategy = BollingerBandsStrategy(window=5, num_std=1)
    signals = strategy.generate_signals(data)
    
    # Check reversion signals
    assert signals['signal'].notna().all()
    assert signals['confidence'].notna().all()

def test_bollinger_edge_cases():
    """Test Bollinger Bands strategy with edge cases."""
    # Test with empty DataFrame
    empty_data = pd.DataFrame(columns=['close'])
    strategy = BollingerBandsStrategy(window=20, num_std=2)
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