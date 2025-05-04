import pytest
from datetime import datetime, timedelta
from AIQuantum.models.trade import Trade, TradeSide
from AIQuantum.trading.position_tracker import PositionTracker

@pytest.fixture
def position_tracker():
    """Create a position tracker with default settings."""
    return PositionTracker(max_open_trades=2, cooldown_period=30)

@pytest.fixture
def sample_trade():
    """Create a sample trade for testing."""
    return Trade(
        entry_time=datetime(2024, 1, 1, 12, 0),
        entry_price=100.0,
        side=TradeSide.LONG,
        size=1.0,
        confidence=0.8,
        stop_loss=95.0,
        take_profit=110.0
    )

def test_add_trade_and_close(position_tracker, sample_trade):
    """Test adding a trade and closing it."""
    # Test opening trade
    assert position_tracker.open_trade(sample_trade)
    assert len(position_tracker.active_trades) == 1
    assert len(position_tracker.closed_trades) == 0
    
    # Test closing trade
    current_time = datetime(2024, 1, 1, 13, 0)
    current_price = 105.0
    closed_trades = position_tracker.check_sl_tp(current_time, current_price)
    
    assert len(closed_trades) == 1
    assert len(position_tracker.active_trades) == 0
    assert len(position_tracker.closed_trades) == 1
    assert closed_trades[0].status == "CLOSED"
    assert closed_trades[0].pnl == 5.0

def test_sl_tp_hit(position_tracker, sample_trade):
    """Test stop loss and take profit hits."""
    # Open trade
    position_tracker.open_trade(sample_trade)
    
    # Test stop loss hit
    current_time = datetime(2024, 1, 1, 12, 30)
    current_price = 94.0  # Below stop loss
    closed_trades = position_tracker.check_sl_tp(current_time, current_price)
    
    assert len(closed_trades) == 1
    assert closed_trades[0].status == "STOPPED"
    assert closed_trades[0].pnl == -6.0
    
    # Test take profit hit
    position_tracker.clear_positions()
    position_tracker.open_trade(sample_trade)
    
    current_price = 111.0  # Above take profit
    closed_trades = position_tracker.check_sl_tp(current_time, current_price)
    
    assert len(closed_trades) == 1
    assert closed_trades[0].status == "CLOSED"
    assert closed_trades[0].pnl == 11.0

def test_trade_expiry(position_tracker, sample_trade):
    """Test trade expiration."""
    # Open trade
    position_tracker.open_trade(sample_trade)
    
    # Test trade expiration
    current_time = datetime(2024, 1, 1, 14, 0)  # 2 hours later
    current_price = 102.0
    max_duration = 3600  # 1 hour
    
    expired_trades = position_tracker.expire_trades(current_time, current_price, max_duration)
    
    assert len(expired_trades) == 1
    assert expired_trades[0].status == "EXPIRED"
    assert expired_trades[0].duration == 7200  # 2 hours in seconds

def test_max_open_trades(position_tracker, sample_trade):
    """Test maximum open trades constraint."""
    # Open first trade
    assert position_tracker.open_trade(sample_trade)
    
    # Try to open second trade
    trade2 = Trade(
        entry_time=datetime(2024, 1, 1, 12, 1),
        entry_price=101.0,
        side=TradeSide.LONG,
        size=1.0,
        confidence=0.8
    )
    assert position_tracker.open_trade(trade2)
    
    # Try to open third trade (should fail)
    trade3 = Trade(
        entry_time=datetime(2024, 1, 1, 12, 2),
        entry_price=102.0,
        side=TradeSide.LONG,
        size=1.0,
        confidence=0.8
    )
    assert not position_tracker.open_trade(trade3)

def test_cooldown_period(position_tracker, sample_trade):
    """Test trade cooldown period."""
    # Open first trade
    assert position_tracker.open_trade(sample_trade)
    
    # Try to open second trade immediately (should fail)
    trade2 = Trade(
        entry_time=datetime(2024, 1, 1, 12, 0, 1),
        entry_price=101.0,
        side=TradeSide.LONG,
        size=1.0,
        confidence=0.8
    )
    assert not position_tracker.open_trade(trade2)
    
    # Try to open trade after cooldown (should succeed)
    trade3 = Trade(
        entry_time=datetime(2024, 1, 1, 13, 0, 1),  # 1 hour later
        entry_price=102.0,
        side=TradeSide.LONG,
        size=1.0,
        confidence=0.8
    )
    assert position_tracker.open_trade(trade3)

def test_portfolio_summary(position_tracker, sample_trade):
    """Test portfolio summary calculation."""
    # Open and close a winning trade
    position_tracker.open_trade(sample_trade)
    position_tracker.check_sl_tp(
        datetime(2024, 1, 1, 13, 0),
        110.0  # Hit take profit
    )
    
    # Open and close a losing trade
    trade2 = Trade(
        entry_time=datetime(2024, 1, 1, 14, 0),
        entry_price=100.0,
        side=TradeSide.LONG,
        size=1.0,
        confidence=0.8,
        stop_loss=95.0
    )
    position_tracker.open_trade(trade2)
    position_tracker.check_sl_tp(
        datetime(2024, 1, 1, 15, 0),
        94.0  # Hit stop loss
    )
    
    summary = position_tracker.get_portfolio_summary()
    
    assert summary["total_pnl"] == 4.0  # 10.0 - 6.0
    assert summary["win_rate"] == 0.5
    assert summary["total_trades"] == 2
    assert summary["active_trades"] == 0
    assert summary["avg_trade_duration"] == 3600  # 1 hour average 