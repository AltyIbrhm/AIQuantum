import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional

def generate_mock_ohlcv(
    symbol: str = "BTC/USD",
    timeframe: str = "1h",
    days: int = 30,
    volatility: float = 0.02,
    trend: float = 0.001,
    start_price: float = 50000.0
) -> pd.DataFrame:
    """
    Generate mock OHLCV data for testing.
    
    Args:
        symbol: Trading pair symbol
        timeframe: Timeframe for candles
        days: Number of days of data to generate
        volatility: Base volatility level (0-1)
        trend: Daily trend factor
        start_price: Starting price
        
    Returns:
        DataFrame with OHLCV data
    """
    # Calculate number of candles based on timeframe
    if timeframe == "1h":
        num_candles = days * 24
    elif timeframe == "4h":
        num_candles = days * 6
    elif timeframe == "1d":
        num_candles = days
    else:
        raise ValueError(f"Unsupported timeframe: {timeframe}")
    
    # Generate timestamps
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    timestamps = pd.date_range(start=start_time, end=end_time, periods=num_candles)
    
    # Initialize price array
    prices = np.zeros(num_candles)
    prices[0] = start_price
    
    # Generate price movements
    for i in range(1, num_candles):
        # Random walk with trend and volatility
        daily_trend = trend * (1 if i % 24 == 0 else 0)  # Apply trend once per day
        random_walk = np.random.normal(0, volatility)
        price_change = prices[i-1] * (daily_trend + random_walk)
        prices[i] = prices[i-1] + price_change
    
    # Generate OHLC data
    opens = prices.copy()
    closes = np.roll(prices, -1)
    closes[-1] = prices[-1]
    
    # Add some noise to highs and lows
    highs = np.maximum(opens, closes) * (1 + np.random.uniform(0, volatility/2, num_candles))
    lows = np.minimum(opens, closes) * (1 - np.random.uniform(0, volatility/2, num_candles))
    
    # Generate volume with some correlation to price movement
    base_volume = 1000.0
    volume = base_volume * (1 + np.abs(np.random.normal(0, 0.5, num_candles)))
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volume
    })
    
    # Set timestamp as index
    df.set_index('timestamp', inplace=True)
    
    return df

def get_mock_ohlcv_data(
    symbol: str = "BTC/USD",
    timeframe: str = "1h",
    days: int = 30,
    config: Optional[Dict] = None
) -> pd.DataFrame:
    """
    Get mock OHLCV data with configurable parameters.
    
    Args:
        symbol: Trading pair symbol
        timeframe: Timeframe for candles
        days: Number of days of data to generate
        config: Optional configuration dictionary
        
    Returns:
        DataFrame with OHLCV data
    """
    # Default parameters
    params = {
        'volatility': 0.02,
        'trend': 0.001,
        'start_price': 50000.0
    }
    
    # Update from config if provided
    if config and 'mock_data' in config:
        params.update(config['mock_data'])
    
    return generate_mock_ohlcv(
        symbol=symbol,
        timeframe=timeframe,
        days=days,
        **params
    ) 