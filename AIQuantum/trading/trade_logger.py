import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from AIQuantum.models.trade import Trade

class TradeLogger:
    """Handles logging of trades and daily summaries to CSV and JSON files."""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the trade logger.
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize log files
        self.trades_file = self.log_dir / "trades.csv"
        self.json_file = self.log_dir / "trades.json"
        self.daily_summary_file = self.log_dir / "daily_summary.csv"
        
        # Initialize CSV headers if files don't exist
        if not self.trades_file.exists():
            self._init_trades_csv()
        if not self.daily_summary_file.exists():
            self._init_daily_summary_csv()
    
    def _init_trades_csv(self) -> None:
        """Initialize the trades CSV file with headers."""
        with open(self.trades_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'entry_time', 'exit_time', 'side', 'entry_price', 'exit_price',
                'size', 'confidence', 'stop_loss', 'take_profit', 'pnl',
                'duration', 'status'
            ])
    
    def _init_daily_summary_csv(self) -> None:
        """Initialize the daily summary CSV file with headers."""
        with open(self.daily_summary_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'date', 'total_trades', 'winning_trades', 'losing_trades',
                'total_pnl', 'win_rate', 'avg_trade_duration'
            ])
    
    def log_trade(self, trade: Trade) -> None:
        """
        Log a single trade to both CSV and JSON files.
        
        Args:
            trade: The trade to log
        """
        # Log to CSV
        with open(self.trades_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                trade.entry_time.isoformat(),
                trade.exit_time.isoformat() if trade.exit_time else '',
                trade.side.value,
                trade.entry_price,
                trade.exit_price if trade.exit_price else '',
                trade.size,
                trade.confidence,
                trade.stop_loss if trade.stop_loss else '',
                trade.take_profit if trade.take_profit else '',
                trade.pnl if trade.pnl else '',
                trade.duration if trade.duration else '',
                trade.status
            ])
        
        # Log to JSON
        trades = []
        if self.json_file.exists():
            with open(self.json_file, 'r') as f:
                trades = json.load(f)
        
        trades.append(trade.to_dict())
        
        with open(self.json_file, 'w') as f:
            json.dump(trades, f, indent=2)
    
    def log_trades(self, trades: List[Trade]) -> None:
        """Log multiple trades."""
        for trade in trades:
            self.log_trade(trade)
    
    def update_daily_summary(self, date: datetime, trades: List[Trade]) -> None:
        """
        Update the daily summary with trades from a specific date.
        
        Args:
            date: The date to summarize
            trades: List of trades to include in the summary
        """
        # Filter trades for the given date
        date_trades = [
            t for t in trades
            if t.entry_time.date() == date.date()
        ]
        
        if not date_trades:
            return
        
        # Calculate summary metrics
        total_trades = len(date_trades)
        winning_trades = sum(1 for t in date_trades if t.pnl and t.pnl > 0)
        losing_trades = total_trades - winning_trades
        total_pnl = sum(t.pnl or 0 for t in date_trades)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        avg_duration = sum(t.duration or 0 for t in date_trades) / total_trades if total_trades > 0 else 0.0
        
        # Write to daily summary CSV
        with open(self.daily_summary_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                date.date().isoformat(),
                total_trades,
                winning_trades,
                losing_trades,
                total_pnl,
                win_rate,
                avg_duration
            ])
    
    def get_trades(self) -> List[Dict[str, Any]]:
        """Retrieve all logged trades from JSON file."""
        if not self.json_file.exists():
            return []
        
        with open(self.json_file, 'r') as f:
            return json.load(f)
    
    def get_daily_summary(self) -> List[Dict[str, Any]]:
        """Retrieve the daily summary from CSV file."""
        if not self.daily_summary_file.exists():
            return []
        
        summaries = []
        with open(self.daily_summary_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                summaries.append({
                    'date': row['date'],
                    'total_trades': int(row['total_trades']),
                    'winning_trades': int(row['winning_trades']),
                    'losing_trades': int(row['losing_trades']),
                    'total_pnl': float(row['total_pnl']),
                    'win_rate': float(row['win_rate']),
                    'avg_trade_duration': float(row['avg_trade_duration'])
                })
        
        return summaries
    
    def clear_logs(self) -> None:
        """Clear all log files."""
        if self.trades_file.exists():
            self.trades_file.unlink()
        if self.json_file.exists():
            self.json_file.unlink()
        if self.daily_summary_file.exists():
            self.daily_summary_file.unlink()
        
        # Reinitialize files
        self._init_trades_csv()
        self._init_daily_summary_csv() 