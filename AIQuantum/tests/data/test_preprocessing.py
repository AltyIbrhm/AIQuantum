import pandas as pd
import numpy as np
from data.preprocessing import preprocess_data

def test_preprocess_basic():
    """Test basic preprocessing functionality."""
    # Create sample OHLCV data
    df = pd.DataFrame({
        'open': [100] * 50,
        'high': [102] * 50,
        'low': [98] * 50,
        'close': [101] * 50,
        'volume': [1000] * 50
    })
    
    # Add some variation
    df['close'] += np.random.normal(0, 1, 50)
    df['high'] = df['close'] + np.random.uniform(0, 2, 50)
    df['low'] = df['close'] - np.random.uniform(0, 2, 50)
    
    # Preprocess data
    result = preprocess_data(df)
    
    # Check basic requirements
    assert not result.empty, "Result should not be empty"
    assert len(result) == len(df), "Length should be preserved"
    assert all(col in result.columns for col in ['open', 'high', 'low', 'close', 'volume']), "Basic columns should be preserved"
    
    # Check for added indicators
    assert 'ema_12' in result.columns, "Should add EMA12"
    assert 'ema_26' in result.columns, "Should add EMA26"
    assert 'rsi' in result.columns, "Should add RSI"
    assert 'macd' in result.columns, "Should add MACD"
    assert 'macd_signal' in result.columns, "Should add MACD signal"
    assert 'macd_hist' in result.columns, "Should add MACD histogram"

def test_preprocess_with_nan():
    """Test preprocessing with NaN values."""
    # Create data with NaN values
    df = pd.DataFrame({
        'open': [100, np.nan, 102, 103, np.nan],
        'high': [102, 103, np.nan, 105, 104],
        'low': [98, 99, 100, np.nan, 102],
        'close': [101, 102, 103, 104, np.nan],
        'volume': [1000, np.nan, 1200, 1300, 1400]
    })
    
    # Preprocess data
    result = preprocess_data(df)
    
    # Check NaN handling
    assert not result.isnull().all().any(), "Should handle NaN values"
    assert len(result) == len(df), "Length should be preserved"

def test_preprocess_with_insufficient_data():
    """Test preprocessing with insufficient data points."""
    # Create minimal data
    df = pd.DataFrame({
        'open': [100],
        'high': [102],
        'low': [98],
        'close': [101],
        'volume': [1000]
    })
    
    # Preprocess data
    result = preprocess_data(df)
    
    # Check handling of insufficient data
    assert not result.empty, "Should handle minimal data"
    assert len(result) == len(df), "Length should be preserved"
    assert result['ema_12'].iloc[0] == df['close'].iloc[0], "First EMA should equal first price"

def test_preprocess_with_extreme_values():
    """Test preprocessing with extreme values."""
    # Create data with extreme values
    df = pd.DataFrame({
        'open': [100, 1000, 0.1, 10000, 0.01],
        'high': [102, 1002, 0.12, 10002, 0.02],
        'low': [98, 998, 0.08, 9998, 0.005],
        'close': [101, 1001, 0.11, 10001, 0.015],
        'volume': [1000, 10000, 100, 100000, 10]
    })
    
    # Preprocess data
    result = preprocess_data(df)
    
    # Check handling of extreme values
    assert not result.empty, "Should handle extreme values"
    assert len(result) == len(df), "Length should be preserved"
    assert all(result['close'] > 0), "All close prices should be positive"
    assert all(result['volume'] > 0), "All volumes should be positive" 