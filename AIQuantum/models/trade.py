from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import json

class TradeSide(Enum):
    LONG = "LONG"
    SHORT = "SHORT"

@dataclass
class Trade:
    """A class representing a single trade in the trading system."""
    
    # Required fields
    entry_time: datetime
    entry_price: float
    side: TradeSide
    size: float
    confidence: float
    
    # Optional fields (can be set after trade entry)
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Calculated fields
    pnl: Optional[float] = None
    duration: Optional[float] = None  # in seconds
    status: str = "OPEN"  # OPEN, CLOSED, STOPPED, EXPIRED
    
    def __post_init__(self):
        """Initialize calculated fields after object creation."""
        if self.exit_time and self.entry_time:
            self.duration = (self.exit_time - self.entry_time).total_seconds()
            self._calculate_pnl()
    
    def _calculate_pnl(self) -> None:
        """Calculate the P&L for the trade."""
        if self.exit_price is None:
            return
            
        if self.side == TradeSide.LONG:
            self.pnl = (self.exit_price - self.entry_price) * self.size
        else:  # SHORT
            self.pnl = (self.entry_price - self.exit_price) * self.size
    
    def _calculate_duration(self) -> None:
        """Calculate the duration of the trade in seconds."""
        if self.exit_time and self.entry_time:
            self.duration = (self.exit_time - self.entry_time).total_seconds()

    def close_trade(self, exit_time: datetime, exit_price: float) -> None:
        """Close the trade with the given exit time and price."""
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.status = "CLOSED"
        self._calculate_duration()
        self._calculate_pnl()
    
    def stop_trade(self, exit_time: datetime, exit_price: float) -> None:
        """Stop the trade (hit stop loss) with the given exit time and price."""
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.status = "STOPPED"
        self._calculate_duration()
        self._calculate_pnl()
    
    def expire_trade(self, exit_time: datetime, exit_price: float) -> None:
        """Expire the trade with the given exit time and price."""
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.status = "EXPIRED"
        self._calculate_duration()
        self._calculate_pnl()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the trade to a dictionary for serialization."""
        return {
            "entry_time": self.entry_time.isoformat(),
            "entry_price": self.entry_price,
            "side": self.side.value,
            "size": self.size,
            "confidence": self.confidence,
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "exit_price": self.exit_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "pnl": self.pnl,
            "duration": self.duration,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Trade':
        """Create a Trade instance from a dictionary."""
        data = data.copy()
        data["entry_time"] = datetime.fromisoformat(data["entry_time"])
        if data["exit_time"]:
            data["exit_time"] = datetime.fromisoformat(data["exit_time"])
        data["side"] = TradeSide(data["side"])
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert the trade to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Trade':
        """Create a Trade instance from a JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    def __str__(self) -> str:
        """Return a string representation of the trade."""
        return (
            f"Trade({self.side.value} | Entry: {self.entry_price:.2f} | "
            f"Size: {self.size:.2f} | Confidence: {self.confidence:.2f} | "
            f"Status: {self.status})"
        ) 