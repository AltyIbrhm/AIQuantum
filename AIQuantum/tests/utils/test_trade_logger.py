import unittest
import json
import tempfile
import os
from datetime import datetime
from pathlib import Path
from AIQuantum.utils.trade_logger import TradeLogger

class TestTradeLogger(unittest.TestCase):
    """Test suite for TradeLogger class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.logger = TradeLogger(log_dir=self.temp_dir.name)
        
        # Sample trade data
        self.trade_data = {
            "trade_id": "test_trade_1",
            "symbol": "BTC/USD",
            "side": "LONG",
            "entry_price": 50000.0,
            "quantity": 1.0
        }
        
        # Sample signal data
        self.signal = {
            "symbol": "BTC/USD",
            "side": "LONG",
            "confidence": 0.85
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_initialization(self):
        """Test proper initialization of TradeLogger."""
        self.assertTrue(os.path.exists(self.temp_dir.name))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir.name, "trades.json")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir.name, "rejected_trades.json")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir.name, "risk_events.json")))
    
    def test_log_trade(self):
        """Test logging of executed trades."""
        self.logger.log_trade(self.trade_data)
        
        with open(os.path.join(self.temp_dir.name, "trades.json"), "r") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["trade_id"], self.trade_data["trade_id"])
            self.assertEqual(data[0]["symbol"], self.trade_data["symbol"])
    
    def test_log_rejected_trade(self):
        """Test logging of rejected trades."""
        timestamp = datetime.utcnow()
        self.logger.log_rejected_trade("Test rejection", self.signal, 50000.0, timestamp)
        
        with open(os.path.join(self.temp_dir.name, "rejected_trades.json"), "r") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["symbol"], self.signal["symbol"])
            self.assertEqual(data[0]["reason"], "Test rejection")
    
    def test_log_risk_event(self):
        """Test logging of risk events."""
        self.logger.log_risk_event("Test risk event", "test_trade_1", {"drawdown": 0.1})
        
        with open(os.path.join(self.temp_dir.name, "risk_events.json"), "r") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["message"], "Test risk event")
            self.assertEqual(data[0]["trade_id"], "test_trade_1")
            self.assertEqual(data[0]["details"]["drawdown"], 0.1)
    
    def test_get_trade_history(self):
        """Test retrieving trade history."""
        self.logger.log_trade(self.trade_data)
        history = self.logger.get_trade_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["trade_id"], self.trade_data["trade_id"])
    
    def test_get_rejected_trades(self):
        """Test retrieving rejected trades."""
        timestamp = datetime.utcnow()
        self.logger.log_rejected_trade("Test rejection", self.signal, 50000.0, timestamp)
        rejected = self.logger.get_rejected_trades()
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["symbol"], self.signal["symbol"])
    
    def test_get_risk_events(self):
        """Test retrieving risk events."""
        self.logger.log_risk_event("Test risk event", "test_trade_1")
        events = self.logger.get_risk_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["message"], "Test risk event")
    
    def test_corrupted_file_handling(self):
        """Test handling of corrupted JSON files."""
        # Create a corrupted trades.json file
        with open(os.path.join(self.temp_dir.name, "trades.json"), "w") as f:
            f.write("invalid json")
        
        # Should handle the corruption and create a new file
        self.logger.log_trade(self.trade_data)
        history = self.logger.get_trade_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["trade_id"], self.trade_data["trade_id"])

if __name__ == '__main__':
    unittest.main() 