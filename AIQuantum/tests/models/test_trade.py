import pytest
from datetime import datetime, timedelta
from AIQuantum.models.trade import Trade, TradeSide

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
        take_profit=110.0,
        symbol="BTC/USD"
    )

def test_close_trade(sample_trade):
    """Test closing a trade and verify P&L calculation."""
    exit_time = datetime(2024, 1, 1, 13, 0)
    exit_price = 105.0
    
    sample_trade.close_trade(exit_time, exit_price)
    
    assert sample_trade.status == "CLOSED"
    assert sample_trade.exit_time == exit_time
    assert sample_trade.exit_price == exit_price
    assert sample_trade.pnl == 5.0  # (105 - 100) * 1.0
    assert sample_trade.duration == 3600  # 1 hour in seconds

def test_stop_trade(sample_trade):
    """Test stopping a trade and verify P&L calculation."""
    exit_time = datetime(2024, 1, 1, 12, 30)
    exit_price = 95.0
    
    sample_trade.stop_trade(exit_time, exit_price)
    
    assert sample_trade.status == "STOPPED"
    assert sample_trade.exit_time == exit_time
    assert sample_trade.exit_price == exit_price
    assert sample_trade.pnl == -5.0  # (95 - 100) * 1.0
    assert sample_trade.duration == 1800  # 30 minutes in seconds

def test_expire_trade(sample_trade):
    """Test expiring a trade and verify P&L calculation."""
    exit_time = datetime(2024, 1, 1, 14, 0)
    exit_price = 102.0
    
    sample_trade.expire_trade(exit_time, exit_price)
    
    assert sample_trade.status == "EXPIRED"
    assert sample_trade.exit_time == exit_time
    assert sample_trade.exit_price == exit_price
    assert sample_trade.pnl == 2.0  # (102 - 100) * 1.0
    assert sample_trade.duration == 7200  # 2 hours in seconds

def test_short_trade_pnl():
    """Test P&L calculation for short trades."""
    trade = Trade(
        entry_time=datetime(2024, 1, 1, 12, 0),
        entry_price=100.0,
        side=TradeSide.SHORT,
        size=1.0,
        confidence=0.8,
        symbol="BTC/USD"
    )
    
    trade.close_trade(
        datetime(2024, 1, 1, 13, 0),
        95.0
    )
    
    assert trade.pnl == 5.0  # (100 - 95) * 1.0

def test_serialization_to_from_dict(sample_trade):
    """Test serialization to and from dictionary."""
    # Convert to dict and back
    trade_dict = sample_trade.to_dict()
    new_trade = Trade.from_dict(trade_dict)
    
    # Verify all fields match
    assert new_trade.entry_time == sample_trade.entry_time
    assert new_trade.entry_price == sample_trade.entry_price
    assert new_trade.side == sample_trade.side
    assert new_trade.size == sample_trade.size
    assert new_trade.confidence == sample_trade.confidence
    assert new_trade.stop_loss == sample_trade.stop_loss
    assert new_trade.take_profit == sample_trade.take_profit

def test_serialization_to_from_json(sample_trade):
    """Test serialization to and from JSON."""
    # Convert to JSON and back
    json_str = sample_trade.to_json()
    new_trade = Trade.from_json(json_str)
    
    # Verify all fields match
    assert new_trade.entry_time == sample_trade.entry_time
    assert new_trade.entry_price == sample_trade.entry_price
    assert new_trade.side == sample_trade.side
    assert new_trade.size == sample_trade.size
    assert new_trade.confidence == sample_trade.confidence
    assert new_trade.stop_loss == sample_trade.stop_loss
    assert new_trade.take_profit == sample_trade.take_profit

def test_trade_duration():
    """Test trade duration calculation."""
    entry_time = datetime(2024, 1, 1, 12, 0)
    exit_time = datetime(2024, 1, 1, 13, 30)
    
    trade = Trade(
        entry_time=entry_time,
        entry_price=100.0,
        side=TradeSide.LONG,
        size=1.0,
        confidence=0.8,
        symbol="BTC/USD"
    )
    
    trade.close_trade(exit_time, 105.0)
    
    assert trade.duration == 5400  # 1.5 hours in seconds

def test_trade_string_representation(sample_trade):
    """Test the string representation of a trade."""
    trade_str = str(sample_trade)
    assert "LONG" in trade_str
    assert "100.00" in trade_str
    assert "1.00" in trade_str
    assert "0.80" in trade_str
    assert "OPEN" in trade_str 