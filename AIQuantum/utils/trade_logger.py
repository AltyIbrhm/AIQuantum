import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from AIQuantum.utils.logger import get_logger

class TradeLogger:
    """
    Handles logging of trade events, including executed trades and rejected signals.
    Provides detailed logging for debugging and analysis purposes.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the trade logger.
        
        Args:
            log_dir: Directory to store log files
        """
        self.logger = get_logger(__name__)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Define log file paths
        self.trades_path = self.log_dir / "trades.json"
        self.rejected_path = self.log_dir / "rejected_trades.json"
        self.risk_events_path = self.log_dir / "risk_events.json"
        
        # Initialize log files if they don't exist
        for path in [self.trades_path, self.rejected_path, self.risk_events_path]:
            if not path.exists():
                with open(path, "w") as f:
                    json.dump([], f, indent=4)
    
    def log_trade(self, trade_data: Dict[str, Any]) -> None:
        """
        Log an executed trade.
        
        Args:
            trade_data: Dictionary containing trade information
        """
        trade_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            **trade_data
        }
        
        self._append_to_json(self.trades_path, trade_entry)
        self.logger.info(f"Logged trade: {trade_data.get('trade_id', 'Unknown')}")
    
    def log_rejected_trade(self, reason: str, signal: Dict[str, Any], 
                          price: float, timestamp: datetime) -> None:
        """
        Log a rejected trade signal.
        
        Args:
            reason: Reason for rejection
            signal: Original trading signal
            price: Current price at rejection
            timestamp: Time of rejection
        """
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "symbol": signal.get("symbol"),
            "side": signal.get("side"),
            "confidence": signal.get("confidence"),
            "price": price,
            "reason": reason,
        }
        
        self._append_to_json(self.rejected_path, log_entry)
        self.logger.info(f"Logged rejected trade: {reason}")
    
    def log_risk_event(self, message: str, trade_id: Optional[str] = None,
                      details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a risk-related event.
        
        Args:
            message: Description of the risk event
            trade_id: Optional ID of the affected trade
            details: Optional additional details about the event
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "trade_id": trade_id,
            "message": message,
            "details": details or {}
        }
        
        self._append_to_json(self.risk_events_path, log_entry)
        self.logger.info(f"Logged risk event: {message}")
    
    def _append_to_json(self, file_path: Path, entry: Dict[str, Any]) -> None:
        """
        Append an entry to a JSON log file.
        
        Args:
            file_path: Path to the JSON file
            entry: Entry to append
        """
        try:
            with open(file_path, "r+") as f:
                data = json.load(f)
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
        except Exception as e:
            self.logger.error(f"Error writing to {file_path}: {str(e)}")
            # Create new file if it doesn't exist or is corrupted
            with open(file_path, "w") as f:
                json.dump([entry], f, indent=4)
    
    def get_trade_history(self) -> list:
        """Get the complete trade history."""
        return self._read_json(self.trades_path)
    
    def get_rejected_trades(self) -> list:
        """Get the history of rejected trades."""
        return self._read_json(self.rejected_path)
    
    def get_risk_events(self) -> list:
        """Get the history of risk events."""
        return self._read_json(self.risk_events_path)
    
    def _read_json(self, file_path: Path) -> list:
        """
        Read and return the contents of a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of entries from the JSON file
        """
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {str(e)}")
            return [] 