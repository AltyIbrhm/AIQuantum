import pytest
import pandas as pd
import numpy as np
from AIQuantum.strategy.signal_combiner import SignalCombiner

def test_signal_combiner_basic():
    """Test basic signal combination."""
    # Create test data
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,  # Multiply by 5 to meet minimum data points
        'open': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,
        'high': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,
        'low': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,
        'volume': [1000] * 50
    })
    
    config = {
        'strategies': {
            'ema': {
                'enabled': True,
                'weight': 0.3,
                'min_confidence': 0.6
            },
            'macd': {
                'enabled': True,
                'weight': 0.4,
                'min_confidence': 0.7
            },
            'bollinger': {
                'enabled': True,
                'weight': 0.3,
                'min_confidence': 0.6
            }
        },
        'min_combined_confidence': 0.7
    }
    
    combiner = SignalCombiner(config=config)
    result = combiner.calculate_signals(data)
    
    # Check output format
    assert 'signals' in result
    assert 'combined_signal' in result
    assert 'combined_confidence' in result
    
    # Check signal values
    assert result['combined_signal'] in [-1, 0, 1]
    assert 0 <= result['combined_confidence'] <= 1

def test_signal_combiner_weighted():
    """Test weighted signal combination."""
    # Create test data
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,  # Multiply by 5 to meet minimum data points
        'open': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,
        'high': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,
        'low': [10, 11, 12, 13, 14, 15, 14, 13, 12, 11] * 5,
        'volume': [1000] * 50
    })
    
    config = {
        'strategies': {
            'ema': {
                'enabled': True,
                'weight': 0.7,  # Higher weight for EMA
                'min_confidence': 0.6
            },
            'macd': {
                'enabled': True,
                'weight': 0.2,
                'min_confidence': 0.7
            },
            'bollinger': {
                'enabled': True,
                'weight': 0.1,
                'min_confidence': 0.6
            }
        },
        'min_combined_confidence': 0.7
    }
    
    combiner = SignalCombiner(config=config)
    result = combiner.calculate_signals(data)
    
    # Check weighted combination
    assert result['combined_signal'] in [-1, 0, 1]
    assert 0 <= result['combined_confidence'] <= 1
    assert 'strategy_weights' in result

def test_signal_combiner_edge_cases():
    """Test signal combiner with edge cases."""
    # Create test data with NaN values
    data = pd.DataFrame({
        'close': [10, np.nan, 12, 13, np.nan, 15] * 10,  # Multiply by 10 to meet minimum data points
        'open': [10, 11, 12, 13, 14, 15] * 10,
        'high': [10, 11, 12, 13, 14, 15] * 10,
        'low': [10, 11, 12, 13, 14, 15] * 10,
        'volume': [1000] * 60
    })
    
    config = {
        'strategies': {
            'ema': {
                'enabled': True,
                'weight': 0.3,
                'min_confidence': 0.6
            },
            'macd': {
                'enabled': True,
                'weight': 0.4,
                'min_confidence': 0.7
            },
            'bollinger': {
                'enabled': True,
                'weight': 0.3,
                'min_confidence': 0.6
            }
        },
        'min_combined_confidence': 0.7
    }
    
    combiner = SignalCombiner(config=config)
    result = combiner.calculate_signals(data)
    
    # Check that NaN values are handled
    assert result['combined_signal'] in [-1, 0, 1]
    assert 0 <= result['combined_confidence'] <= 1
    
    # Test with empty DataFrame
    empty_data = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
    with pytest.raises(Exception):
        result = combiner.calculate_signals(empty_data)
    
    # Test with insufficient data
    small_data = pd.DataFrame({
        'close': [10, 11, 12],
        'open': [10, 11, 12],
        'high': [10, 11, 12],
        'low': [10, 11, 12],
        'volume': [1000] * 3
    })
    with pytest.raises(Exception):
        result = combiner.calculate_signals(small_data) 