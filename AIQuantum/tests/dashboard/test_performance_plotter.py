import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
from pathlib import Path
from AIQuantum.dashboard.performance_plotter import PerformancePlotter

class TestPerformancePlotter(unittest.TestCase):
    """Test suite for PerformancePlotter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.plotter = PerformancePlotter(output_dir=self.temp_dir.name)
        
        # Create sample equity curve data
        self.start_date = datetime(2024, 1, 1)
        dates = [self.start_date + timedelta(days=i) for i in range(30)]
        equity = [10000 + i * 100 + np.random.normal(0, 50) for i in range(30)]
        drawdown = [0.0] * 30
        for i in range(1, 30):
            peak = max(equity[:i+1])
            drawdown[i] = (peak - equity[i]) / peak if equity[i] < peak else 0.0
            
        self.equity_curve = pd.DataFrame({
            'timestamp': dates,
            'equity': equity,
            'drawdown': drawdown
        })
        
        # Create sample trades data
        self.trades = pd.DataFrame({
            'trade_id': [f'trade_{i}' for i in range(10)],
            'symbol': ['BTC/USD'] * 10,
            'side': ['LONG'] * 10,
            'entry_price': [50000.0] * 10,
            'exit_price': [51000.0] * 5 + [49000.0] * 5,
            'quantity': [1.0] * 10,
            'pnl': [1000.0] * 5 + [-1000.0] * 5,
            'entry_time': [self.start_date + timedelta(hours=i) for i in range(10)],
            'exit_time': [self.start_date + timedelta(hours=i+1) for i in range(10)]
        })
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_initialization(self):
        """Test proper initialization of PerformancePlotter."""
        self.assertTrue(os.path.exists(self.temp_dir.name))
        self.assertEqual(self.plotter.output_dir, Path(self.temp_dir.name))
    
    def test_plot_equity_curve(self):
        """Test equity curve plotting."""
        self.plotter.plot_equity_curve(self.equity_curve)
        plot_files = list(Path(self.temp_dir.name).glob('equity_curve_*.png'))
        self.assertEqual(len(plot_files), 1)
    
    def test_plot_daily_returns(self):
        """Test daily returns plotting."""
        self.plotter.plot_daily_returns(self.equity_curve)
        plot_files = list(Path(self.temp_dir.name).glob('daily_returns_*.png'))
        self.assertEqual(len(plot_files), 1)
    
    def test_plot_trade_distribution(self):
        """Test trade distribution plotting."""
        self.plotter.plot_trade_distribution(self.trades)
        plot_files = list(Path(self.temp_dir.name).glob('trade_distribution_*.png'))
        self.assertEqual(len(plot_files), 1)
    
    def test_plot_win_loss_metrics(self):
        """Test win/loss metrics plotting."""
        self.plotter.plot_win_loss_metrics(self.trades)
        plot_files = list(Path(self.temp_dir.name).glob('win_loss_metrics_*.png'))
        self.assertEqual(len(plot_files), 1)
    
    def test_generate_all_plots(self):
        """Test generation of all plots."""
        self.plotter.generate_all_plots(self.equity_curve, self.trades)
        plot_files = list(Path(self.temp_dir.name).glob('*.png'))
        self.assertEqual(len(plot_files), 4)  # Should generate 4 different plots
    
    def test_empty_data(self):
        """Test handling of empty data."""
        empty_equity = pd.DataFrame(columns=['timestamp', 'equity', 'drawdown'])
        empty_trades = pd.DataFrame(columns=['trade_id', 'pnl', 'entry_time', 'exit_time'])
        
        # Should not raise any errors and should not generate any plots
        self.plotter.generate_all_plots(empty_equity, empty_trades)
        plot_files = list(Path(self.temp_dir.name).glob('*.png'))
        self.assertEqual(len(plot_files), 0)  # Should not generate any plots with empty data

if __name__ == '__main__':
    unittest.main() 