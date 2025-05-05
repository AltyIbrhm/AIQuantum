"""
Unit tests for the position sizing module.
Tests ATR calculation, position sizing, and various edge cases.
"""

import pytest
import pandas as pd
import numpy as np
from AIQuantum.risk.position_sizer import PositionSizer, PositionSizingConfig

@pytest.fixture
def basic_config():
    """Create a basic configuration for testing."""
    return PositionSizingConfig(
        risk_per_trade=0.02,  # 2% risk per trade
        max_position_size=0.5,  # 50% max position size (increased for testing)
        min_position_size=0.001,  # 0.1% min position size (decreased for testing)
        atr_period=14,
        confidence_threshold=0.7,
        volatility_factor=1.0
    )

@pytest.fixture
def position_sizer(basic_config):
    """Create a position sizer instance for testing."""
    return PositionSizer(basic_config)

@pytest.fixture
def sample_price_data():
    """Create sample price data for ATR calculation."""
    dates = pd.date_range(start='2023-01-01', periods=20, freq='D')
    high = pd.Series([100, 102, 101, 103, 104, 105, 103, 104, 106, 107,
                      108, 106, 105, 107, 108, 109, 107, 108, 110, 111], index=dates)
    low = pd.Series([98, 99, 100, 101, 102, 103, 101, 102, 104, 105,
                     106, 104, 103, 105, 106, 107, 105, 106, 108, 109], index=dates)
    close = pd.Series([99, 101, 100, 102, 103, 104, 102, 103, 105, 106,
                       107, 105, 104, 106, 107, 108, 106, 107, 109, 110], index=dates)
    return high, low, close

class TestPositionSizingConfig:
    """Test cases for PositionSizingConfig validation."""
    
    def test_valid_config(self):
        """Test that valid configuration is accepted."""
        config = PositionSizingConfig(
            risk_per_trade=0.02,
            max_position_size=0.1,
            min_position_size=0.01
        )
        assert config.risk_per_trade == 0.02
        assert config.max_position_size == 0.1
        assert config.min_position_size == 0.01
    
    def test_invalid_risk_per_trade(self):
        """Test that invalid risk per trade is rejected."""
        with pytest.raises(ValueError):
            PositionSizingConfig(
                risk_per_trade=1.5,  # Invalid: > 1
                max_position_size=0.1,
                min_position_size=0.01
            )
    
    def test_invalid_max_position_size(self):
        """Test that invalid max position size is rejected."""
        with pytest.raises(ValueError):
            PositionSizingConfig(
                risk_per_trade=0.02,
                max_position_size=1.5,  # Invalid: > 1
                min_position_size=0.01
            )
    
    def test_invalid_min_position_size(self):
        """Test that min position size > max position size is rejected."""
        with pytest.raises(ValueError):
            PositionSizingConfig(
                risk_per_trade=0.02,
                max_position_size=0.1,
                min_position_size=0.2  # Invalid: > max_position_size
            )

class TestATRCalculation:
    """Test cases for ATR calculation."""
    
    def test_atr_calculation(self, position_sizer, sample_price_data):
        """Test that ATR is calculated correctly."""
        high, low, close = sample_price_data
        atr = position_sizer.calculate_atr(high, low, close)
        
        # ATR should be a Series with the same index as input
        assert isinstance(atr, pd.Series)
        assert len(atr) == len(high)
        
        # First ATR value should be NaN (due to rolling window)
        assert pd.isna(atr.iloc[0])
        
        # ATR should be positive
        assert (atr.dropna() > 0).all()
        
        # ATR should be less than the maximum price range
        max_range = (high - low).max()
        assert (atr.dropna() <= max_range).all()

class TestPositionSizing:
    """Test cases for position size calculation."""
    
    def test_basic_position_sizing(self, position_sizer):
        """Test basic position sizing calculation."""
        result = position_sizer.calculate_position_size(
            account_value=100000,
            current_price=50.0,
            atr=2.5
        )
        
        # Check all required fields are present
        assert 'position_size' in result
        assert 'position_value' in result
        assert 'risk_amount' in result
        assert 'confidence_factor' in result
        
        # Verify risk amount
        assert result['risk_amount'] == 100000 * 0.02  # 2% of account
        
        # Verify position value calculation
        assert result['position_value'] == result['position_size'] * 50.0
    
    def test_confidence_scaling(self, position_sizer):
        """Test that position size scales with confidence."""
        # Test with high confidence
        high_conf = position_sizer.calculate_position_size(
            account_value=100000,
            current_price=100.0,   # Lower price
            atr=5.0,              # Lower ATR
            confidence=0.9
        )
        
        # Test with low confidence
        low_conf = position_sizer.calculate_position_size(
            account_value=100000,
            current_price=100.0,
            atr=5.0,
            confidence=0.3
        )
        
        # High confidence should result in larger position
        assert high_conf['position_size'] > low_conf['position_size']
        assert high_conf['confidence_factor'] > low_conf['confidence_factor']
        
        # Verify the scaling ratio matches the confidence ratio
        confidence_ratio = 0.9 / 0.3
        position_ratio = high_conf['position_size'] / low_conf['position_size']
        assert abs(confidence_ratio - position_ratio) < 0.1  # Allow for small rounding differences
    
    def test_position_limits(self, position_sizer):
        """Test that position size respects min/max limits."""
        # Test with very large ATR (should hit max limit)
        max_pos = position_sizer.calculate_position_size(
            account_value=100000,
            current_price=50.0,
            atr=100.0  # Very large ATR
        )
        
        # Test with very small ATR (should hit min limit)
        min_pos = position_sizer.calculate_position_size(
            account_value=100000,
            current_price=50.0,
            atr=0.1  # Very small ATR
        )
        
        # Verify limits
        assert max_pos['position_value'] <= 100000 * 0.1  # Max 10% of account
        assert min_pos['position_value'] >= 100000 * 0.01  # Min 1% of account
    
    def test_volatility_adjustment(self, position_sizer):
        """Test that volatility factor adjusts position size."""
        # Test with normal volatility
        normal = position_sizer.calculate_position_size(
            account_value=100000,
            current_price=100.0,   # Lower price
            atr=5.0               # Lower ATR
        )
        
        # Test with high volatility
        high_vol = position_sizer.calculate_position_size(
            account_value=100000,
            current_price=100.0,
            atr=5.0,
            volatility_factor=2.0
        )
        
        # Higher volatility should result in smaller position
        assert normal['position_size'] > high_vol['position_size']
        
        # Verify the position ratio matches the volatility ratio
        volatility_ratio = 2.0
        position_ratio = normal['position_size'] / high_vol['position_size']
        assert abs(volatility_ratio - position_ratio) < 0.1  # Allow for small rounding differences

class TestEdgeCases:
    """Test cases for edge cases and error handling."""
    
    def test_zero_confidence(self, position_sizer):
        """Test handling of zero confidence."""
        result = position_sizer.calculate_position_size(
            account_value=100000,
            current_price=50.0,
            atr=2.5,
            confidence=0.0
        )
        
        # Should still return a valid position size (minimum)
        assert result['position_size'] > 0
        assert result['confidence_factor'] == 0
    
    def test_extreme_volatility(self, position_sizer):
        """Test handling of extreme volatility."""
        result = position_sizer.calculate_position_size(
            account_value=100000,
            current_price=50.0,
            atr=2.5,
            volatility_factor=10.0  # Extreme volatility
        )
        
        # Should still return a valid position size
        assert result['position_size'] > 0
        assert result['position_value'] <= 100000 * 0.1  # Respect max limit
    
    def test_zero_atr(self, position_sizer):
        """Test handling of zero ATR."""
        with pytest.raises(ZeroDivisionError):
            position_sizer.calculate_position_size(
                account_value=100000,
                current_price=50.0,
                atr=0.0
            ) 