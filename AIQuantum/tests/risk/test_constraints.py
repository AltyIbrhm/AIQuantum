from risk.constraints import RiskConstraintsManager, PositionConstraints, RiskConstraints
import pytest

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
        balance=10000,
        current_drawdown=0.02,
        open_trades=1,
        position_value=5000,
        last_trade_time=None
    )
    assert result["allowed"], "Should allow trade within drawdown limits"
    
    # Test exceeding drawdown
    result = constraints.validate_trade(
        balance=10000,
        current_drawdown=0.06,
        open_trades=1,
        position_value=5000,
        last_trade_time=None
    )
    assert not result["allowed"], "Should reject trade exceeding drawdown"
    assert "drawdown" in result["reason"].lower(), "Reason should mention drawdown"

def test_position_size_constraints():
    """Test position size constraints."""
    constraints = RiskConstraintsManager({
        'max_position_value': 10000,
        'min_position_value': 100,
        'max_portfolio_risk': 0.1  # 10%
    })
    
    # Test valid position size
    result = constraints.validate_trade(
        balance=10000,
        current_drawdown=0.0,
        open_trades=0,
        position_value=5000,
        last_trade_time=None
    )
    assert result["allowed"], "Should allow valid position size"
    
    # Test too small position
    result = constraints.validate_trade(
        balance=10000,
        current_drawdown=0.0,
        open_trades=0,
        position_value=50,
        last_trade_time=None
    )
    assert not result["allowed"], "Should reject too small position"
    
    # Test too large position
    result = constraints.validate_trade(
        balance=10000,
        current_drawdown=0.0,
        open_trades=0,
        position_value=15000,
        last_trade_time=None
    )
    assert not result["allowed"], "Should reject too large position"

def test_open_trades_constraint():
    """Test maximum open trades constraint."""
    constraints = RiskConstraintsManager({
        'max_open_trades': 3,
        'max_position_value': 10000
    })
    
    # Test within limit
    result = constraints.validate_trade(
        balance=10000,
        current_drawdown=0.0,
        open_trades=2,
        position_value=5000,
        last_trade_time=None
    )
    assert result["allowed"], "Should allow trade within open trades limit"
    
    # Test at limit
    result = constraints.validate_trade(
        balance=10000,
        current_drawdown=0.0,
        open_trades=3,
        position_value=5000,
        last_trade_time=None
    )
    assert not result["allowed"], "Should reject trade at open trades limit"

def test_trade_cooldown():
    """Test trade cooldown constraint."""
    import datetime
    constraints = RiskConstraintsManager({
        'trade_cooldown_minutes': 30,
        'max_position_value': 10000
    })
    
    # Test after cooldown
    last_trade = datetime.datetime.now() - datetime.timedelta(minutes=31)
    result = constraints.validate_trade(
        balance=10000,
        current_drawdown=0.0,
        open_trades=0,
        position_value=5000,
        last_trade_time=last_trade
    )
    assert result["allowed"], "Should allow trade after cooldown"
    
    # Test during cooldown
    last_trade = datetime.datetime.now() - datetime.timedelta(minutes=29)
    result = constraints.validate_trade(
        balance=10000,
        current_drawdown=0.0,
        open_trades=0,
        position_value=5000,
        last_trade_time=last_trade
    )
    assert not result["allowed"], "Should reject trade during cooldown"
    assert "cooldown" in result["reason"].lower(), "Reason should mention cooldown" 