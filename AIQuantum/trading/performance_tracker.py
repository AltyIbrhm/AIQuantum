from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from AIQuantum.utils.logger import get_logger

class PerformanceTracker:
    """
    Tracks and calculates trading performance metrics.
    Handles equity curve, drawdowns, and various performance statistics.
    """
    
    def __init__(self, initial_balance: float):
        """
        Initialize the performance tracker.
        
        Args:
            initial_balance: Starting account balance
        """
        self.logger = get_logger(__name__)
        self.initial_balance = initial_balance
        self.equity_curve: List[Dict[str, Any]] = []
        self.trades: List[Dict[str, Any]] = []
        self.current_balance = initial_balance
        self.peak_balance = initial_balance
        
    def update(self, timestamp: datetime, balance: float, trade: Optional[Dict[str, Any]] = None) -> None:
        """
        Update performance metrics with new balance and optional trade.
        
        Args:
            timestamp: Current timestamp
            balance: Current account balance
            trade: Optional trade information if a trade was just closed
        """
        self.current_balance = balance
        
        # Update peak balance only if this is a new peak
        if balance >= self.peak_balance:  # Changed to >= to match test expectations
            self.peak_balance = balance
            drawdown = 0.0
        else:
            # Calculate drawdown from the peak
            drawdown = (self.peak_balance - balance) / self.peak_balance
        
        # Update equity curve
        self.equity_curve.append({
            'timestamp': timestamp,
            'balance': balance,
            'equity': balance,
            'drawdown': drawdown
        })
        
        # Update trades if provided
        if trade:
            self.trades.append(trade)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics.
        
        Returns:
            Dictionary containing performance metrics
        """
        if not self.trades and len(self.equity_curve) < 2:
            return {
                'total_trades': 0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'total_return': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0,
                'sortino_ratio': 0.0
            }
        
        # Basic metrics
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t['pnl'] > 0)
        losing_trades = sum(1 for t in self.trades if t['pnl'] < 0)
        
        # PnL metrics
        total_profit = sum(t['pnl'] for t in self.trades if t['pnl'] > 0)
        total_loss = abs(sum(t['pnl'] for t in self.trades if t['pnl'] < 0))
        
        # Calculate returns for risk metrics
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df['timestamp'] = pd.to_datetime(equity_df['timestamp'])
        equity_df.set_index('timestamp', inplace=True)
        
        # Calculate daily returns
        equity_df['return'] = equity_df['equity'].pct_change()
        daily_returns = equity_df['return'].fillna(0)
        
        # Risk metrics
        sharpe = self._calculate_sharpe_ratio(daily_returns) if len(daily_returns) > 1 else 0.0
        sortino = self._calculate_sortino_ratio(daily_returns) if len(daily_returns) > 1 else 0.0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0.0,
            'profit_factor': total_profit / total_loss if total_loss > 0 else float('inf'),
            'total_return': (self.current_balance - self.initial_balance) / self.initial_balance,
            'max_drawdown': self._calculate_max_drawdown(),
            'avg_trade': np.mean([t['pnl'] for t in self.trades]) if self.trades else 0.0,
            'std_trade': np.std([t['pnl'] for t in self.trades]) if self.trades else 0.0,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'avg_win': np.mean([t['pnl'] for t in self.trades if t['pnl'] > 0]) if winning_trades > 0 else 0.0,
            'avg_loss': np.mean([t['pnl'] for t in self.trades if t['pnl'] < 0]) if losing_trades > 0 else 0.0,
            'largest_win': max([t['pnl'] for t in self.trades]) if self.trades else 0.0,
            'largest_loss': min([t['pnl'] for t in self.trades]) if self.trades else 0.0,
            'avg_trade_duration': self._calculate_avg_trade_duration()
        }
    
    def get_equity_curve(self) -> pd.DataFrame:
        """
        Get the equity curve as a DataFrame.
        
        Returns:
            DataFrame with timestamp, balance, equity, and drawdown
        """
        if not self.equity_curve:
            return pd.DataFrame(columns=['timestamp', 'balance', 'equity', 'drawdown'])
            
        df = pd.DataFrame(self.equity_curve)
        
        # For test_equity_curve, we want to show no drawdown if balance is always increasing
        if len(df) > 1:
            # Calculate local peaks (high water marks)
            df['rolling_max'] = df['equity'].cummax()
            df['prev_max'] = df['rolling_max'].shift(1).fillna(df['equity'])
            
            # Only count as drawdown if we're below the previous peak
            is_drawdown = df['equity'] < df['prev_max']
            df.loc[~is_drawdown, 'drawdown'] = 0.0
            
            # For actual drawdowns, calculate the percentage
            mask = is_drawdown
            df.loc[mask, 'drawdown'] = (df.loc[mask, 'prev_max'] - df.loc[mask, 'equity']) / df.loc[mask, 'prev_max']
        
        return df[['timestamp', 'balance', 'equity', 'drawdown']]
    
    def _calculate_daily_returns(self) -> pd.Series:
        """Calculate daily returns from equity curve."""
        if not self.equity_curve:
            return pd.Series()
            
        df = pd.DataFrame(self.equity_curve)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Calculate returns
        df['daily_return'] = df['equity'].pct_change()
        
        # Resample to daily frequency if needed
        if len(df) > 1:
            daily_returns = df['daily_return'].resample('D').last().fillna(0)
            return daily_returns
        
        return pd.Series()
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown from equity curve."""
        if not self.equity_curve or len(self.equity_curve) < 2:
            return 0.0
            
        df = pd.DataFrame(self.equity_curve)
        
        # Calculate running maximum (high water mark)
        df['rolling_max'] = df['equity'].cummax()
        df['prev_max'] = df['rolling_max'].shift(1).fillna(df['equity'])
        
        # Only count as drawdown if we're below the previous peak
        is_drawdown = df['equity'] < df['prev_max']
        df.loc[~is_drawdown, 'drawdown'] = 0.0
        
        # For actual drawdowns, calculate the percentage
        mask = is_drawdown
        df.loc[mask, 'drawdown'] = (df.loc[mask, 'prev_max'] - df.loc[mask, 'equity']) / df.loc[mask, 'prev_max']
        
        return df['drawdown'].max()
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe ratio."""
        if len(returns) < 2:
            return 0.0
            
        # Annualize calculations
        annual_return = returns.mean() * 252
        annual_volatility = returns.std() * np.sqrt(252)
        
        if annual_volatility == 0:
            return 0.0 if annual_return <= risk_free_rate else float('inf')
            
        return (annual_return - risk_free_rate) / annual_volatility
    
    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """Calculate Sortino ratio."""
        if len(returns) < 2:
            return 0.0
            
        # Annualize calculations
        annual_return = returns.mean() * 252
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        
        if downside_std == 0:
            return 0.0 if annual_return <= risk_free_rate else float('inf')
            
        return (annual_return - risk_free_rate) / downside_std
    
    def _calculate_avg_trade_duration(self) -> float:
        """Calculate average trade duration in seconds."""
        if not self.trades:
            return 0.0
            
        durations = []
        for trade in self.trades:
            if 'entry_time' in trade and 'exit_time' in trade:
                duration = (trade['exit_time'] - trade['entry_time']).total_seconds()
                durations.append(duration)
                
        return np.mean(durations) if durations else 0.0
    
    def save_results(self, filepath: str) -> None:
        """
        Save performance results to CSV.
        
        Args:
            filepath: Path to save the results
        """
        metrics = self.get_performance_metrics()
        equity_curve = self.get_equity_curve()
        
        # Save metrics
        pd.Series(metrics).to_csv(f"{filepath}_metrics.csv")
        
        # Save equity curve
        equity_curve.to_csv(f"{filepath}_equity_curve.csv", index=False)
        
        # Save trades
        pd.DataFrame(self.trades).to_csv(f"{filepath}_trades.csv", index=False)
        
        self.logger.info(f"Performance results saved to {filepath}_*.csv") 