from typing import List, Dict, Optional
from datetime import datetime, timedelta
from AIQuantum.models.trade import Trade, TradeSide

class PositionTracker:
    """Manages active and closed trades, handles SL/TP logic, and enforces trade constraints."""
    
    def __init__(self, max_open_trades: int = 1, cooldown_period: int = 3600):
        """
        Initialize the position tracker.
        
        Args:
            max_open_trades: Maximum number of open trades allowed
            cooldown_period: Minimum time (in seconds) between trades
        """
        self.max_open_trades = max_open_trades
        self.cooldown_period = cooldown_period
        self.active_trades: List[Trade] = []
        self.closed_trades: List[Trade] = []
        self.last_trade_time: Optional[datetime] = None
    
    def can_open_trade(self, current_time: datetime) -> bool:
        """Check if a new trade can be opened based on constraints."""
        if len(self.active_trades) >= self.max_open_trades:
            return False
            
        if self.last_trade_time is not None:
            time_since_last = (current_time - self.last_trade_time).total_seconds()
            if time_since_last < self.cooldown_period:
                return False
                
        return True
    
    def open_trade(self, trade: Trade) -> bool:
        """
        Open a new trade if constraints are satisfied.
        
        Args:
            trade: The trade to open
            
        Returns:
            bool: True if trade was opened successfully, False otherwise
        """
        if not self.can_open_trade(trade.entry_time):
            return False
            
        self.active_trades.append(trade)
        self.last_trade_time = trade.entry_time
        return True
    
    def check_sl_tp(self, current_time: datetime, current_price: float) -> List[Trade]:
        """
        Check if any active trades have hit their stop loss or take profit.
        
        Args:
            current_time: Current timestamp
            current_price: Current market price
            
        Returns:
            List[Trade]: List of trades that were closed due to SL/TP
        """
        closed_trades = []
        
        for trade in self.active_trades[:]:  # Create a copy to safely modify during iteration
            if trade.side == TradeSide.LONG:
                if trade.stop_loss and current_price <= trade.stop_loss:
                    # For stop loss, use the actual market price for PnL
                    trade.stop_trade(current_time, current_price)
                    closed_trades.append(trade)
                elif trade.take_profit and current_price >= trade.take_profit:
                    # For take profit, use the actual market price for PnL
                    trade.close_trade(current_time, current_price)
                    closed_trades.append(trade)
                elif trade.take_profit and trade.stop_loss:
                    # Manual close if price is between SL and TP
                    if current_price > trade.stop_loss and current_price < trade.take_profit:
                        trade.close_trade(current_time, current_price)
                        closed_trades.append(trade)
            else:  # SHORT
                if trade.stop_loss and current_price >= trade.stop_loss:
                    # For stop loss, use the actual market price for PnL
                    trade.stop_trade(current_time, current_price)
                    closed_trades.append(trade)
                elif trade.take_profit and current_price <= trade.take_profit:
                    # For take profit, use the actual market price for PnL
                    trade.close_trade(current_time, current_price)
                    closed_trades.append(trade)
                elif trade.take_profit and trade.stop_loss:
                    # Manual close if price is between SL and TP
                    if current_price < trade.stop_loss and current_price > trade.take_profit:
                        trade.close_trade(current_time, current_price)
                        closed_trades.append(trade)
            
            if trade in closed_trades:
                self.active_trades.remove(trade)
                self.closed_trades.append(trade)
        
        return closed_trades
    
    def expire_trades(self, current_time: datetime, current_price: float, max_duration: int) -> List[Trade]:
        """
        Expire trades that have exceeded their maximum duration.
        
        Args:
            current_time: Current timestamp
            current_price: Current market price
            max_duration: Maximum trade duration in seconds
            
        Returns:
            List[Trade]: List of trades that were expired
        """
        expired_trades = []
        
        for trade in self.active_trades[:]:
            duration = (current_time - trade.entry_time).total_seconds()
            if duration > max_duration:
                trade.expire_trade(current_time, current_price)
                expired_trades.append(trade)
                self.active_trades.remove(trade)
                self.closed_trades.append(trade)
        
        return expired_trades
    
    def get_portfolio_summary(self) -> Dict[str, float]:
        """
        Get a summary of the portfolio's performance.
        
        Returns:
            Dict containing portfolio metrics
        """
        total_pnl = sum(trade.pnl or 0 for trade in self.closed_trades)
        winning_trades = sum(1 for trade in self.closed_trades if trade.pnl and trade.pnl > 0)
        total_trades = len(self.closed_trades)
        
        return {
            "total_pnl": total_pnl,
            "win_rate": winning_trades / total_trades if total_trades > 0 else 0.0,
            "total_trades": total_trades,
            "active_trades": len(self.active_trades),
            "avg_trade_duration": sum(
                trade.duration or 0 for trade in self.closed_trades
            ) / total_trades if total_trades > 0 else 0.0
        }
    
    def get_active_positions(self) -> List[Trade]:
        """Get a list of all active trades."""
        return self.active_trades.copy()
    
    def get_closed_positions(self) -> List[Trade]:
        """Get a list of all closed trades."""
        return self.closed_trades.copy()
    
    def clear_positions(self) -> None:
        """Clear all active and closed trades."""
        self.active_trades.clear()
        self.closed_trades.clear()
        self.last_trade_time = None 