import unittest
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import tempfile
import os
from AIQuantum.trading.performance_tracker import PerformanceTracker

class TestPerformanceTracker(unittest.TestCase):
    """Test suite for PerformanceTracker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.initial_balance = 10000.0
        self.tracker = PerformanceTracker(self.initial_balance)
        self.start_time = datetime(2024, 1, 1, 12, 0)
        
    def test_initialization(self):
        """Test proper initialization of PerformanceTracker."""
        self.assertEqual(self.tracker.initial_balance, self.initial_balance)
        self.assertEqual(self.tracker.current_balance, self.initial_balance)
        self.assertEqual(self.tracker.peak_balance, self.initial_balance)
        self.assertEqual(len(self.tracker.equity_curve), 0)
        self.assertEqual(len(self.tracker.trades), 0)
    
    def test_update_without_trade(self):
        """Test updating performance metrics without a trade."""
        new_balance = 10500.0
        self.tracker.update(self.start_time, new_balance)
        
        self.assertEqual(self.tracker.current_balance, new_balance)
        self.assertEqual(self.tracker.peak_balance, new_balance)
        self.assertEqual(len(self.tracker.equity_curve), 1)
        self.assertEqual(len(self.tracker.trades), 0)
        
        # Check equity curve entry
        curve_entry = self.tracker.equity_curve[0]
        self.assertEqual(curve_entry['timestamp'], self.start_time)
        self.assertEqual(curve_entry['balance'], new_balance)
        self.assertEqual(curve_entry['equity'], new_balance)
        self.assertEqual(curve_entry['drawdown'], 0.0)
    
    def test_update_with_trade(self):
        """Test updating performance metrics with a trade."""
        trade = {
            'trade_id': 'test_trade_1',
            'symbol': 'BTC/USD',
            'side': 'LONG',
            'entry_price': 50000.0,
            'exit_price': 51000.0,
            'quantity': 1.0,
            'pnl': 1000.0,
            'entry_time': self.start_time,
            'exit_time': self.start_time + timedelta(hours=1)
        }
        
        new_balance = self.initial_balance + trade['pnl']
        self.tracker.update(self.start_time + timedelta(hours=1), new_balance, trade)
        
        self.assertEqual(len(self.tracker.trades), 1)
        self.assertEqual(self.tracker.trades[0], trade)
        self.assertEqual(self.tracker.current_balance, new_balance)
    
    def test_performance_metrics_no_trades(self):
        """Test performance metrics calculation with no trades."""
        metrics = self.tracker.get_performance_metrics()
        
        self.assertEqual(metrics['total_trades'], 0)
        self.assertEqual(metrics['win_rate'], 0.0)
        self.assertEqual(metrics['profit_factor'], 0.0)
        self.assertEqual(metrics['total_return'], 0.0)
        self.assertEqual(metrics['max_drawdown'], 0.0)
        self.assertEqual(metrics['sharpe_ratio'], 0.0)
        self.assertEqual(metrics['sortino_ratio'], 0.0)
    
    def test_performance_metrics_with_trades(self):
        """Test performance metrics calculation with multiple trades."""
        # Add winning trades
        for i in range(3):
            trade = {
                'trade_id': f'win_trade_{i}',
                'symbol': 'BTC/USD',
                'side': 'LONG',
                'entry_price': 50000.0,
                'exit_price': 51000.0,
                'quantity': 1.0,
                'pnl': 1000.0,
                'entry_time': self.start_time + timedelta(hours=i),
                'exit_time': self.start_time + timedelta(hours=i+1)
            }
            self.tracker.update(
                self.start_time + timedelta(hours=i+1),
                self.tracker.current_balance + trade['pnl'],
                trade
            )
        
        # Add losing trades
        for i in range(2):
            trade = {
                'trade_id': f'loss_trade_{i}',
                'symbol': 'BTC/USD',
                'side': 'LONG',
                'entry_price': 50000.0,
                'exit_price': 49000.0,
                'quantity': 1.0,
                'pnl': -1000.0,
                'entry_time': self.start_time + timedelta(hours=i+3),
                'exit_time': self.start_time + timedelta(hours=i+4)
            }
            self.tracker.update(
                self.start_time + timedelta(hours=i+4),
                self.tracker.current_balance + trade['pnl'],
                trade
            )
        
        metrics = self.tracker.get_performance_metrics()
        
        self.assertEqual(metrics['total_trades'], 5)
        self.assertEqual(metrics['winning_trades'], 3)
        self.assertEqual(metrics['losing_trades'], 2)
        self.assertAlmostEqual(metrics['win_rate'], 0.6)
        self.assertAlmostEqual(metrics['profit_factor'], 1.5)  # 3000/2000
        self.assertAlmostEqual(metrics['total_return'], 0.1)  # 1000/10000
        self.assertGreater(metrics['sharpe_ratio'], 0)
        self.assertGreater(metrics['sortino_ratio'], 0)
    
    def test_equity_curve(self):
        """Test equity curve generation and calculations."""
        # Add some balance updates with no drawdown
        times = [self.start_time + timedelta(hours=i) for i in range(5)]
        balances = [10000.0, 10500.0, 11000.0, 11500.0, 12000.0]  # Strictly increasing sequence
        
        for t, b in zip(times, balances):
            self.tracker.update(t, b)
        
        equity_curve = self.tracker.get_equity_curve()
        
        self.assertIsInstance(equity_curve, pd.DataFrame)
        self.assertEqual(len(equity_curve), 5)
        self.assertTrue(all(col in equity_curve.columns for col in ['timestamp', 'balance', 'equity', 'drawdown']))
        
        # Test drawdown calculation
        self.assertEqual(equity_curve['drawdown'].max(), 0.0)  # No drawdown in strictly increasing sequence
        self.assertEqual(equity_curve['drawdown'].min(), 0.0)
    
    def test_drawdown_calculation(self):
        """Test maximum drawdown calculation with a clear drawdown period."""
        # Create a sequence with a clear drawdown
        times = [self.start_time + timedelta(hours=i) for i in range(5)]
        balances = [10000.0, 11000.0, 9000.0, 9500.0, 12000.0]  # Peak at 11000, trough at 9000
        
        for t, b in zip(times, balances):
            self.tracker.update(t, b)
        
        metrics = self.tracker.get_performance_metrics()
        expected_drawdown = (11000.0 - 9000.0) / 11000.0
        
        self.assertAlmostEqual(metrics['max_drawdown'], expected_drawdown)
    
    def test_sharpe_sortino_ratios(self):
        """Test Sharpe and Sortino ratio calculations."""
        # Create a sequence of returns
        times = [self.start_time + timedelta(days=i) for i in range(10)]
        returns = [0.01, 0.02, -0.01, 0.03, -0.02, 0.01, 0.02, -0.01, 0.02, 0.01]
        balance = self.initial_balance
        
        for t, r in zip(times, returns):
            balance *= (1 + r)
            self.tracker.update(t, balance)
        
        metrics = self.tracker.get_performance_metrics()
        
        self.assertGreater(metrics['sharpe_ratio'], 0)
        self.assertGreater(metrics['sortino_ratio'], metrics['sharpe_ratio'])  # Sortino should be higher
    
    def test_save_results(self):
        """Test saving results to CSV files."""
        # Add some test data
        trade = {
            'trade_id': 'test_trade',
            'symbol': 'BTC/USD',
            'side': 'LONG',
            'entry_price': 50000.0,
            'exit_price': 51000.0,
            'quantity': 1.0,
            'pnl': 1000.0,
            'entry_time': self.start_time,
            'exit_time': self.start_time + timedelta(hours=1)
        }
        self.tracker.update(self.start_time + timedelta(hours=1), self.initial_balance + 1000.0, trade)
        
        # Save to temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = os.path.join(temp_dir, 'test_results')
            self.tracker.save_results(base_path)
            
            # Check if files were created
            self.assertTrue(os.path.exists(f"{base_path}_metrics.csv"))
            self.assertTrue(os.path.exists(f"{base_path}_equity_curve.csv"))
            self.assertTrue(os.path.exists(f"{base_path}_trades.csv"))
            
            # Verify metrics file content
            metrics_df = pd.read_csv(f"{base_path}_metrics.csv", index_col=0)
            self.assertGreater(len(metrics_df), 0)
            
            # Verify equity curve file content
            equity_df = pd.read_csv(f"{base_path}_equity_curve.csv")
            self.assertEqual(len(equity_df), 1)
            
            # Verify trades file content
            trades_df = pd.read_csv(f"{base_path}_trades.csv")
            self.assertEqual(len(trades_df), 1)

if __name__ == '__main__':
    unittest.main() 