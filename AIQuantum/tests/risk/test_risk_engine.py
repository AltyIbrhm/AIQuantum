import pytest
import pandas as pd
from datetime import datetime, timedelta
from AIQuantum.risk.risk_engine import RiskEngine

def test_risk_engine_initialization():
    """Test risk engine initialization with different configurations."""
    # Test with default config
    engine = RiskEngine()
    assert engine is not None
    
    # Test with custom config
    custom_config = {
        'max_daily_drawdown': 0.05,
        'max_position_value': 10000,
        'max_open_trades': 3,
        'min_position_value': 100,
        'trade_cooldown_minutes': 30
    }
    engine = RiskEngine(config=custom_config)
    assert engine.config == custom_config

def test_risk_engine_position_sizing():
    """Test position sizing calculations."""
    engine = RiskEngine()
    
    # Test basic position sizing
    portfolio_value = 10000
    risk_per_trade = 0.02  # 2%
    position_size = engine.calculate_position_size(portfolio_value, risk_per_trade)
    assert position_size == 200  # 2% of 10000
    
    # Test with different risk levels
    position_size = engine.calculate_position_size(portfolio_value, 0.05)  # 5%
    assert position_size == 500
    
    # Test with minimum position size
    position_size = engine.calculate_position_size(1000, 0.01)  # 1% of 1000 = 10
    assert position_size >= engine.config['min_position_value']

def test_risk_engine_trade_validation():
    """Test trade validation against risk constraints."""
    engine = RiskEngine()
    
    # Test valid trade
    trade_info = {
        'portfolio_value': 10000,
        'daily_drawdown': 0.02,
        'num_open_trades': 1,
        'position_size': 500,
        'last_trade_time': datetime.now() - timedelta(minutes=31)
    }
    result = engine.validate_trade(**trade_info)
    assert result['valid']
    
    # Test invalid trade (exceeding drawdown)
    trade_info['daily_drawdown'] = 0.06
    result = engine.validate_trade(**trade_info)
    assert not result['valid']
    
    # Test invalid trade (too many open trades)
    trade_info['daily_drawdown'] = 0.02
    trade_info['num_open_trades'] = 4
    result = engine.validate_trade(**trade_info)
    assert not result['valid']

def test_risk_engine_edge_cases():
    """Test risk engine with edge cases."""
    engine = RiskEngine()
    
    # Test with zero portfolio value
    with pytest.raises(ValueError):
        engine.calculate_position_size(0, 0.02)
    
    # Test with negative risk
    with pytest.raises(ValueError):
        engine.calculate_position_size(10000, -0.02)
    
    # Test with risk > 1
    with pytest.raises(ValueError):
        engine.calculate_position_size(10000, 1.5)
    
    # Test with missing trade info
    with pytest.raises(KeyError):
        engine.validate_trade(portfolio_value=10000)  # Missing required fields 