import pytest
import pandas as pd
import numpy as np
from AIQuantum.strategy.signal_combiner import SignalCombiner

def test_signal_combiner_basic():
    """Test basic signal combination."""
    # Create test signals
    signals = pd.DataFrame({
        'strategy1_signal': [1, 1, -1, 0, 1],
        'strategy1_confidence': [0.8, 0.7, 0.6, 0.5, 0.9],
        'strategy2_signal': [1, -1, -1, 1, 0],
        'strategy2_confidence': [0.7, 0.8, 0.9, 0.6, 0.5]
    })
    
    combiner = SignalCombiner()
    combined = combiner.combine_signals(signals)
    
    # Check output format
    assert 'final_signal' in combined.columns
    assert 'final_confidence' in combined.columns
    
    # Check signal values
    assert combined['final_signal'].isin([-1, 0, 1]).all()
    
    # Check confidence values
    assert (combined['final_confidence'] >= 0).all()
    assert (combined['final_confidence'] <= 1).all()

def test_signal_combiner_weighted():
    """Test weighted signal combination."""
    # Create test signals with different weights
    signals = pd.DataFrame({
        'strategy1_signal': [1, 1, -1, 0, 1],
        'strategy1_confidence': [0.8, 0.7, 0.6, 0.5, 0.9],
        'strategy2_signal': [1, -1, -1, 1, 0],
        'strategy2_confidence': [0.7, 0.8, 0.9, 0.6, 0.5]
    })
    
    weights = {
        'strategy1': 0.7,
        'strategy2': 0.3
    }
    
    combiner = SignalCombiner(weights=weights)
    combined = combiner.combine_signals(signals)
    
    # Check weighted combination
    assert combined['final_signal'].notna().all()
    assert combined['final_confidence'].notna().all()

def test_signal_combiner_edge_cases():
    """Test signal combiner with edge cases."""
    # Test with empty DataFrame
    empty_signals = pd.DataFrame()
    combiner = SignalCombiner()
    combined = combiner.combine_signals(empty_signals)
    assert len(combined) == 0
    
    # Test with NaN values
    nan_signals = pd.DataFrame({
        'strategy1_signal': [1, np.nan, -1],
        'strategy1_confidence': [0.8, 0.7, np.nan],
        'strategy2_signal': [1, -1, np.nan],
        'strategy2_confidence': [0.7, np.nan, 0.9]
    })
    combined = combiner.combine_signals(nan_signals)
    assert combined['final_signal'].notna().all()
    
    # Test with single strategy
    single_signals = pd.DataFrame({
        'strategy1_signal': [1, -1, 0],
        'strategy1_confidence': [0.8, 0.7, 0.6]
    })
    combined = combiner.combine_signals(single_signals)
    assert len(combined) == len(single_signals) 