import pandas as pd
import numpy as np
from strategy.technical.ema import calculate_ema

def test_ema_basic():
    """Test basic EMA calculation with simple data."""
    # Create a simple price series
    df = pd.DataFrame({
        'close': [i for i in range(1, 51)]  # 1 to 50
    })
    
    # Calculate EMA
    ema = calculate_ema(df, period=10)
    
    # Basic checks
    assert not ema.isnull().all(), "EMA should not be all NaN"
    assert len(ema) == len(df), "EMA length should match input data"
    assert ema.iloc[0] == df['close'].iloc[0], "First EMA value should equal first price"
    
    # Check EMA smoothing
    assert ema.iloc[-1] < df['close'].iloc[-1], "EMA should be smoothed (less than latest price)"
    assert ema.iloc[-1] > df['close'].iloc[0], "EMA should follow trend"

def test_ema_with_volatility():
    """Test EMA calculation with volatile data."""
    # Create price series with volatility
    np.random.seed(42)
    base_prices = np.linspace(100, 200, 100)
    noise = np.random.normal(0, 5, 100)
    prices = base_prices + noise
    
    df = pd.DataFrame({'close': prices})
    
    # Calculate EMAs with different periods
    ema_short = calculate_ema(df, period=10)
    ema_long = calculate_ema(df, period=20)
    
    # Check smoothing effect
    assert ema_long.std() < ema_short.std(), "Longer period EMA should be smoother"
    assert ema_long.std() < df['close'].std(), "EMA should be smoother than raw prices"

def test_ema_edge_cases():
    """Test EMA calculation with edge cases."""
    # Test with single value
    df_single = pd.DataFrame({'close': [100]})
    ema_single = calculate_ema(df_single, period=10)
    assert ema_single.iloc[0] == 100, "Single value EMA should equal the value"
    
    # Test with NaN values
    df_nan = pd.DataFrame({
        'close': [100, np.nan, 102, 103, np.nan, 105]
    })
    ema_nan = calculate_ema(df_nan, period=3)
    assert not ema_nan.isnull().all(), "EMA should handle NaN values"
    
    # Test with constant values
    df_constant = pd.DataFrame({'close': [100] * 50})
    ema_constant = calculate_ema(df_constant, period=10)
    assert (ema_constant == 100).all(), "EMA of constant values should be constant" 