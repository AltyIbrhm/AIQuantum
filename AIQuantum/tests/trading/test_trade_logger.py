import pytest
import json
import csv
from datetime import datetime
from pathlib import Path
from AIQuantum.models.trade import Trade, TradeSide
from AIQuantum.trading.trade_logger import TradeLogger

@pytest.fixture
def trade_logger(tmp_path):
    """Create a trade logger with a temporary directory."""
    return TradeLogger(log_dir=str(tmp_path))

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

def test_log_trade_to_csv_json(trade_logger, sample_trade):
    """Test logging a trade to both CSV and JSON files."""
    # Log the trade
    trade_logger.log_trade(sample_trade)
    
    # Check CSV file
    with open(trade_logger.trades_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        row = rows[0]
        assert row['entry_time'] == '2024-01-01T12:00:00'
        assert float(row['entry_price']) == 100.0
        assert row['side'] == 'LONG'
        assert float(row['size']) == 1.0
        assert float(row['confidence']) == 0.8
    
    # Check JSON file
    with open(trade_logger.json_file, 'r') as f:
        trades = json.load(f)
        assert len(trades) == 1
        trade = trades[0]
        assert trade['entry_time'] == '2024-01-01T12:00:00'
        assert trade['entry_price'] == 100.0
        assert trade['side'] == 'LONG'
        assert trade['size'] == 1.0
        assert trade['confidence'] == 0.8

def test_log_multiple_trades(trade_logger, sample_trade):
    """Test logging multiple trades."""
    # Create a second trade
    trade2 = Trade(
        entry_time=datetime(2024, 1, 1, 13, 0),
        entry_price=101.0,
        side=TradeSide.SHORT,
        size=2.0,
        confidence=0.9,
        symbol="BTC/USD"
    )
    
    # Log both trades
    trade_logger.log_trades([sample_trade, trade2])
    
    # Check CSV file
    with open(trade_logger.trades_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
    
    # Check JSON file
    with open(trade_logger.json_file, 'r') as f:
        trades = json.load(f)
        assert len(trades) == 2

def test_daily_summary_logging(trade_logger, sample_trade):
    """Test daily summary logging."""
    # Create trades for the same day
    trade2 = Trade(
        entry_time=datetime(2024, 1, 1, 13, 0),
        entry_price=101.0,
        side=TradeSide.LONG,
        size=1.0,
        confidence=0.8,
        symbol="BTC/USD"
    )
    
    # Close the trades with different outcomes
    sample_trade.close_trade(datetime(2024, 1, 1, 14, 0), 110.0)  # Win
    trade2.close_trade(datetime(2024, 1, 1, 15, 0), 95.0)  # Loss
    
    # Log the trades
    trade_logger.log_trades([sample_trade, trade2])
    
    # Update daily summary
    trade_logger.update_daily_summary(datetime(2024, 1, 1), [sample_trade, trade2])
    
    # Check daily summary
    with open(trade_logger.daily_summary_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        row = rows[0]
        assert row['date'] == '2024-01-01'
        assert int(row['total_trades']) == 2
        assert int(row['winning_trades']) == 1
        assert int(row['losing_trades']) == 1
        assert float(row['total_pnl']) == 4.0  # 10.0 - 6.0
        assert float(row['win_rate']) == 0.5
        assert float(row['avg_trade_duration']) > 0

def test_trade_logger_handles_existing_files(trade_logger, sample_trade):
    """Test that the logger handles existing files correctly."""
    # Log initial trade
    trade_logger.log_trade(sample_trade)
    
    # Create a second trade
    trade2 = Trade(
        entry_time=datetime(2024, 1, 1, 13, 0),
        entry_price=101.0,
        side=TradeSide.LONG,
        size=1.0,
        confidence=0.8,
        symbol="BTC/USD"
    )
    
    # Log second trade (should append to existing files)
    trade_logger.log_trade(trade2)
    
    # Check CSV file
    with open(trade_logger.trades_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
    
    # Check JSON file
    with open(trade_logger.json_file, 'r') as f:
        trades = json.load(f)
        assert len(trades) == 2

def test_clear_logs(trade_logger, sample_trade):
    """Test clearing all log files."""
    # Log some trades
    trade_logger.log_trade(sample_trade)
    trade_logger.update_daily_summary(datetime(2024, 1, 1), [sample_trade])
    
    # Clear logs
    trade_logger.clear_logs()
    
    # Check that files are reinitialized
    with open(trade_logger.trades_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 0
    
    with open(trade_logger.daily_summary_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 0
    
    assert not trade_logger.json_file.exists()

def test_get_trades_and_summary(trade_logger, sample_trade):
    """Test retrieving logged trades and summaries."""
    # Log a trade and update summary
    trade_logger.log_trade(sample_trade)
    trade_logger.update_daily_summary(datetime(2024, 1, 1), [sample_trade])
    
    # Get trades
    trades = trade_logger.get_trades()
    assert len(trades) == 1
    assert trades[0]['entry_price'] == 100.0
    
    # Get daily summary
    summary = trade_logger.get_daily_summary()
    assert len(summary) == 1
    assert summary[0]['date'] == '2024-01-01'
    assert summary[0]['total_trades'] == 1 