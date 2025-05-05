import unittest
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import shutil
import os
import json

from AIQuantum.trading.paper_trading_engine import PaperTradingEngine
from AIQuantum.models.trade import Trade, TradeSide

class TestPaperTradingEngine(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.test_dir = tempfile.mkdtemp()
        self.config = {
            'initial_balance': 10000.0,
            'max_open_trades': 1,
            'cooldown_period': 300,  # 5 minutes
            'risk_config': {
                'risk_per_trade': 0.02,
                'max_position_size': 1.0
            },
            'strategy_config': {},
            'log_dir': self.test_dir,
            'lookback': 20  # Add lookback parameter
        }
        self.engine = PaperTradingEngine(self.config)
        
        # Create sample OHLCV data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
        self.ohlcv_data = pd.DataFrame({
            'open': np.random.normal(100, 1, 100),
            'high': np.random.normal(101, 1, 100),
            'low': np.random.normal(99, 1, 100),
            'close': np.random.normal(100, 1, 100),
            'volume': np.random.normal(1000, 100, 100)
        }, index=dates)
        
    def tearDown(self):
        """Clean up test environment after each test."""
        shutil.rmtree(self.test_dir)
        
    def test_trade_rejection_logging(self):
        """Test that trade rejections are properly logged."""
        # Create a signal during cooldown period
        signal = {
            'symbol': 'BTC/USD',
            'side': 'buy',
            'confidence': 0.8,
            'stop_loss': 95.0
        }
        
        # First trade should be accepted
        candle = pd.Series({
            'open': 100.0,
            'high': 101.0,
            'low': 99.0,
            'close': 100.0,
            'volume': 1000.0
        }, name=datetime.now())
        
        self.engine.evaluate_trade(signal, candle)
        
        # Second trade during cooldown should be rejected
        candle.name = datetime.now() + timedelta(seconds=60)
        self.engine.evaluate_trade(signal, candle)
        
        # Check rejected trades log
        with open(os.path.join(self.test_dir, 'rejected_trades.json'), 'r') as f:
            rejected_trades = json.load(f)
            
        self.assertEqual(len(rejected_trades), 1)
        self.assertEqual(
            rejected_trades[0]['reason'],
            'Trade cooldown or max trades reached'
        )
        
    def test_risk_event_logging(self):
        """Test that risk events are properly logged."""
        signal = {
            'symbol': 'BTC/USD',
            'side': 'buy',
            'confidence': 0.8,
            'stop_loss': 100.0  # Same as current price, should trigger risk event
        }
        
        candle = pd.Series({
            'open': 100.0,
            'high': 101.0,
            'low': 99.0,
            'close': 100.0,
            'volume': 1000.0
        }, name=datetime.now())
        
        self.engine.evaluate_trade(signal, candle)
        
        # Check risk events log
        with open(os.path.join(self.test_dir, 'risk_events.json'), 'r') as f:
            risk_events = json.load(f)
            
        self.assertEqual(len(risk_events), 1)
        self.assertEqual(risk_events[0]['message'], 'Zero or negative price risk')
        self.assertEqual(
            risk_events[0]['details']['price_risk'],
            0.0
        )
        
    def test_position_size_limit_logging(self):
        """Test that position size limit events are properly logged."""
        signal = {
            'symbol': 'BTC/USD',
            'side': 'buy',
            'confidence': 0.8,
            'stop_loss': 90.0  # 10% stop loss
        }
        
        candle = pd.Series({
            'open': 100.0,
            'high': 101.0,
            'low': 99.0,
            'close': 100.0,
            'volume': 1000.0
        }, name=datetime.now())
        
        # Set a very small position size limit
        self.engine.config['risk_config']['max_position_size'] = 0.1
        self.engine.evaluate_trade(signal, candle)
        
        # Check risk events log
        with open(os.path.join(self.test_dir, 'risk_events.json'), 'r') as f:
            risk_events = json.load(f)
            
        position_size_events = [
            e for e in risk_events 
            if e['message'] == 'Position size exceeds limit'
        ]
        self.assertEqual(len(position_size_events), 1)
        self.assertLess(
            position_size_events[0]['details']['max_size'],
            position_size_events[0]['details']['calculated_size']
        )
        
    def test_backtest_logging(self):
        """Test logging during backtest execution."""
        # Mock strategy to generate signals
        def mock_generate_signal(candle_slice):
            return {
                'symbol': 'BTC/USD',
                'side': 'buy' if candle_slice.iloc[-1]['close'] > candle_slice.iloc[0]['close'] else 'sell',
                'confidence': 0.8,
                'stop_loss': candle_slice.iloc[-1]['close'] * 0.95
            }
            
        self.engine.strategy.generate_signal = Mock(side_effect=mock_generate_signal)
        
        # Run backtest
        self.engine.run_backtest(self.ohlcv_data)
        
        # Check logs
        with open(os.path.join(self.test_dir, 'trades.json'), 'r') as f:
            trades = json.load(f)
        with open(os.path.join(self.test_dir, 'rejected_trades.json'), 'r') as f:
            rejected_trades = json.load(f)
        with open(os.path.join(self.test_dir, 'risk_events.json'), 'r') as f:
            risk_events = json.load(f)
            
        # Verify we have some logged events
        self.assertGreater(len(trades), 0)
        self.assertGreater(len(rejected_trades), 0)
        self.assertGreater(len(risk_events), 0)
        
if __name__ == '__main__':
    unittest.main() 