import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from AIQuantum.utils.logger import get_logger

class PerformancePlotter:
    """
    Generates performance visualization plots for trading results.
    Creates equity curve, returns distribution, and other performance metrics plots.
    """
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize the performance plotter.
        
        Args:
            output_dir: Directory to save the generated plots
        """
        self.logger = get_logger(__name__)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style for all plots
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = [12, 6]
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
        
    def plot_equity_curve(self, equity_curve: pd.DataFrame, title: str = "Equity Curve") -> None:
        """
        Plot equity curve over time with drawdown.
        
        Args:
            equity_curve: DataFrame with timestamp, equity, and drawdown columns
            title: Plot title
        """
        if equity_curve.empty:
            self.logger.warning("Empty equity curve data provided")
            return
            
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
        fig.suptitle(title, fontsize=16)
        
        # Plot equity curve
        ax1.plot(equity_curve['timestamp'], equity_curve['equity'], label='Equity', color='blue')
        ax1.set_ylabel('Equity ($)')
        ax1.grid(True)
        ax1.legend()
        
        # Plot drawdown
        ax2.fill_between(equity_curve['timestamp'], equity_curve['drawdown'] * 100, 0, 
                        color='red', alpha=0.3, label='Drawdown')
        ax2.set_ylabel('Drawdown (%)')
        ax2.set_xlabel('Date')
        ax2.grid(True)
        ax2.legend()
        
        plt.tight_layout()
        self._save_plot(fig, 'equity_curve')
        
    def plot_daily_returns(self, equity_curve: pd.DataFrame, title: str = "Daily Returns") -> None:
        """
        Plot daily returns as a bar chart.
        
        Args:
            equity_curve: DataFrame with timestamp and equity columns
            title: Plot title
        """
        if equity_curve.empty:
            self.logger.warning("Empty equity curve data provided")
            return
            
        # Calculate daily returns
        equity_curve['timestamp'] = pd.to_datetime(equity_curve['timestamp'])
        equity_curve.set_index('timestamp', inplace=True)
        daily_returns = equity_curve['equity'].resample('D').last().pct_change()
        
        if daily_returns.empty:
            self.logger.warning("No daily returns data available")
            return
            
        plt.figure(figsize=(12, 6))
        plt.bar(daily_returns.index, daily_returns.values * 100, 
                color=np.where(daily_returns >= 0, 'green', 'red'), alpha=0.7)
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Return (%)')
        plt.grid(True, alpha=0.3)
        
        self._save_plot(plt.gcf(), 'daily_returns')
        
    def plot_trade_distribution(self, trades: pd.DataFrame, title: str = "Trade Distribution") -> None:
        """
        Plot trade PnL distribution and duration.
        
        Args:
            trades: DataFrame containing trade information
            title: Plot title
        """
        if trades.empty:
            self.logger.warning("Empty trades data provided")
            return
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle(title, fontsize=16)
        
        # Plot PnL distribution
        if 'pnl' in trades.columns:
            ax1.hist(trades['pnl'], bins=30, color='blue', alpha=0.7)
            ax1.set_title('PnL Distribution')
            ax1.set_xlabel('PnL ($)')
            ax1.set_ylabel('Frequency')
        
        # Plot trade duration distribution
        if 'entry_time' in trades.columns and 'exit_time' in trades.columns:
            trades['duration'] = (trades['exit_time'] - trades['entry_time']).dt.total_seconds() / 3600  # Convert to hours
            ax2.hist(trades['duration'], bins=30, color='green', alpha=0.7)
            ax2.set_title('Trade Duration Distribution')
            ax2.set_xlabel('Duration (hours)')
            ax2.set_ylabel('Frequency')
        
        plt.tight_layout()
        self._save_plot(fig, 'trade_distribution')
        
    def plot_win_loss_metrics(self, trades: pd.DataFrame, title: str = "Win/Loss Metrics") -> None:
        """
        Plot win/loss metrics including win rate and profit factor.
        
        Args:
            trades: DataFrame containing trade information
            title: Plot title
        """
        if trades.empty or 'pnl' not in trades.columns:
            self.logger.warning("No valid trade data provided for win/loss metrics")
            return
            
        # Calculate metrics
        total_trades = len(trades)
        winning_trades = len(trades[trades['pnl'] > 0])
        losing_trades = len(trades[trades['pnl'] < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        total_profit = trades[trades['pnl'] > 0]['pnl'].sum()
        total_loss = abs(trades[trades['pnl'] < 0]['pnl'].sum())
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # Create plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle(title, fontsize=16)
        
        # Win/Loss pie chart
        ax1.pie([winning_trades, losing_trades], 
                labels=['Winning Trades', 'Losing Trades'],
                autopct='%1.1f%%',
                colors=['green', 'red'])
        ax1.set_title(f'Win Rate: {win_rate:.1%}')
        
        # Profit/Loss bar chart
        ax2.bar(['Total Profit', 'Total Loss'], 
                [total_profit, total_loss],
                color=['green', 'red'])
        ax2.set_title(f'Profit Factor: {profit_factor:.2f}')
        ax2.set_ylabel('Amount ($)')
        
        plt.tight_layout()
        self._save_plot(fig, 'win_loss_metrics')
        
    def _save_plot(self, fig: plt.Figure, name: str) -> None:
        """
        Save plot to file.
        
        Args:
            fig: Matplotlib figure to save
            name: Base name for the output file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"{name}_{timestamp}.png"
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(fig)
        self.logger.info(f"Saved plot to {filename}")
        
    def generate_all_plots(self, equity_curve: pd.DataFrame, trades: pd.DataFrame) -> None:
        """
        Generate all performance plots.
        
        Args:
            equity_curve: DataFrame with equity curve data
            trades: DataFrame with trade data
        """
        self.plot_equity_curve(equity_curve)
        self.plot_daily_returns(equity_curve)
        self.plot_trade_distribution(trades)
        self.plot_win_loss_metrics(trades)
        self.logger.info("Generated all performance plots") 