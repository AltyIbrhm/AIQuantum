import pytest
from datetime import datetime, timedelta
from AIQuantum.risk.constraints import RiskConstraintsManager, PositionConstraints, RiskConstraints

def test_drawdown_constraint():
    """Test drawdown constraint evaluation."""
    constraints = RiskConstraintsManager({
        'max_daily_drawdown': 0.05,  # 5%
        'max_position_value': 10000,
        'max_open_trades': 3,
        'min_position_value': 100,
        'trade_cooldown_minutes': 30
    })
    
    # Test within limits
    result = constraints.validate_trade(
        portfolio_value=10000,
        daily_drawdown=0.02,
        num_open_trades=1,
        position_size=500,  # 5% of portfolio
        last_trade_time=None
    )
    assert result['valid'], f"Trade within drawdown limit should be valid. Got: {result}"
    
    # Test exceeding drawdown
    result = constraints.validate_trade(
        portfolio_value=10000,
        daily_drawdown=0.06,
        num_open_trades=1,
        position_size=500,
        last_trade_time=None
    )
    assert not result['valid'], f"Trade exceeding drawdown limit should be invalid. Got: {result}"

def test_position_size_constraints():
    """Test position size constraints."""
    constraints = RiskConstraintsManager({
        'max_position_value': 10000,
        'min_position_value': 100,
        'max_portfolio_risk': 0.1  # 10%
    })
    
    # Test valid position size
    result = constraints.validate_trade(
        portfolio_value=10000,
        daily_drawdown=0.0,
        num_open_trades=0,
        position_size=800,  # 8% of portfolio
        last_trade_time=None
    )
    assert result['valid'], f"Position size within limits should be valid. Got: {result}"
    
    # Test too small position
    result = constraints.validate_trade(
        portfolio_value=10000,
        daily_drawdown=0.0,
        num_open_trades=0,
        position_size=50,  # Below minimum
        last_trade_time=None
    )
    assert not result['valid'], f"Position size below minimum should be invalid. Got: {result}"
    
    # Test too large position
    result = constraints.validate_trade(
        portfolio_value=10000,
        daily_drawdown=0.0,
        num_open_trades=0,
        position_size=1500,  # 15% of portfolio
        last_trade_time=None
    )
    assert not result['valid'], f"Position size above maximum risk should be invalid. Got: {result}"

def test_open_trades_constraint():
    """Test maximum open trades constraint."""
    constraints = RiskConstraintsManager({
        'max_open_trades': 3,
        'max_position_value': 10000
    })
    
    # Test within limit
    result = constraints.validate_trade(
        portfolio_value=10000,
        daily_drawdown=0.0,
        num_open_trades=2,
        position_size=500,  # 5% of portfolio
        last_trade_time=None
    )
    assert result['valid'], f"Number of trades within limit should be valid. Got: {result}"
    
    # Test at limit
    result = constraints.validate_trade(
        portfolio_value=10000,
        daily_drawdown=0.0,
        num_open_trades=3,
        position_size=500,
        last_trade_time=None
    )
    assert not result['valid'], f"Number of trades at limit should be invalid. Got: {result}"

def test_trade_cooldown():
    """Test trade cooldown constraint."""
    constraints = RiskConstraintsManager({
        'trade_cooldown_minutes': 30,
        'max_position_value': 10000
    })
    
    # Test after cooldown
    last_trade = datetime.now() - timedelta(minutes=31)
    result = constraints.validate_trade(
        portfolio_value=10000,
        daily_drawdown=0.0,
        num_open_trades=0,
        position_size=500,  # 5% of portfolio
        last_trade_time=last_trade
    )
    assert result['valid'], f"Trade after cooldown should be valid. Got: {result}"
    
    # Test during cooldown
    last_trade = datetime.now() - timedelta(minutes=15)
    result = constraints.validate_trade(
        portfolio_value=10000,
        daily_drawdown=0.0,
        num_open_trades=0,
        position_size=500,
        last_trade_time=last_trade
    )
    assert not result['valid'], f"Trade during cooldown should be invalid. Got: {result}" 