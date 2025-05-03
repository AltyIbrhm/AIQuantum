import pandas as pd
import numpy as np
from AIQuantum.strategy.technical.ema import calculate_ema

def test_ema_basic():
    """Test basic EMA calculation with simple data."""
    # Create a simple price series
    df = pd.DataFrame({
        'close': [i for i in range(1, 51)]  # 1 to 50
    })
    
    # Calculate EMA
    ema = calculate_ema(df['close'], period=10)
    
    # Basic checks
    assert not ema.isnull().all().item(), "EMA should not be all NaN"
    assert len(ema) == len(df), "EMA length should match input length"
    assert ema.iloc[-1] > ema.iloc[0], "EMA should trend upward with increasing prices"
    
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
    ema_short = calculate_ema(df['close'], period=10)
    ema_long = calculate_ema(df['close'], period=20)
    
    # Check smoothing effect
    assert ema_long.std().item() < ema_short.std().item(), "Longer period EMA should be smoother"
    assert ema_long.std() < df['close'].std(), "EMA should be smoother than raw prices"
    assert len(ema_short) == len(df), "EMA length should match input length"

def test_ema_edge_cases():
    """Test EMA calculation with edge cases."""
    # Test with single value
    df_single = pd.DataFrame({'close': [100]})
    ema_single = calculate_ema(df_single['close'], period=10)
    assert ema_single.iloc[0] == 100, "Single value EMA should equal the value"
    
    # Test with NaN values
    df_nan = pd.DataFrame({'close': [100, np.nan, 102, 103, np.nan]})
    ema_nan = calculate_ema(df_nan['close'], period=2)
    assert not ema_nan.isnull().all().item(), "EMA should handle NaN values"
    assert len(ema_nan) == len(df_nan), "EMA length should match input length"
    
    # Test with zero values
    df_zero = pd.DataFrame({'close': [0, 0, 0, 0, 0]})
    ema_zero = calculate_ema(df_zero['close'], period=3)
    assert (ema_zero == 0).all().item(), "EMA of all zeros should be zero" 