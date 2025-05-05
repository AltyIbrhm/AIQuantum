"""
Position sizing module for AIQuantum trading system.
Implements various position sizing strategies including ATR-based and confidence-weighted sizing.
"""

from typing import Dict, Optional, Union
import numpy as np
import pandas as pd
from dataclasses import dataclass
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class PositionSizingConfig:
    """Configuration for position sizing parameters."""
    risk_per_trade: float  # Risk per trade as a percentage of account
    max_position_size: float  # Maximum position size as a percentage of account
    min_position_size: float  # Minimum position size as a percentage of account
    atr_period: int = 14  # Period for ATR calculation
    confidence_threshold: float = 0.7  # Minimum confidence threshold for full position size
    volatility_factor: float = 1.0  # Multiplier for volatility-based adjustments

    def __post_init__(self):
        """Validate configuration parameters after initialization."""
        if not 0 < self.risk_per_trade <= 1:
            raise ValueError("Risk per trade must be between 0 and 1")
        if not 0 < self.max_position_size <= 1:
            raise ValueError("Max position size must be between 0 and 1")
        if not 0 < self.min_position_size <= self.max_position_size:
            raise ValueError("Min position size must be between 0 and max position size")
        if not 0 < self.confidence_threshold <= 1:
            raise ValueError("Confidence threshold must be between 0 and 1")

class PositionSizer:
    """
    Position sizing calculator that implements multiple sizing strategies.
    
    Features:
    - ATR-based position sizing
    - Risk-per-trade percentage based sizing
    - Confidence-weighted position scaling
    - Volatility-based adjustments
    """
    
    def __init__(self, config: PositionSizingConfig):
        """
        Initialize the position sizer with configuration parameters.
        
        Args:
            config: PositionSizingConfig object containing sizing parameters
        """
        self.config = config
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """
        Calculate the Average True Range (ATR) for position sizing.
        
        Args:
            high: High prices series
            low: Low prices series
            close: Close prices series
            
        Returns:
            pd.Series: ATR values
        """
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.config.atr_period).mean()
        return atr
    
    def calculate_position_size(
        self,
        account_value: float,
        current_price: float,
        atr: float,
        confidence: Optional[float] = None,
        volatility_factor: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Calculate the position size based on multiple factors.
        
        Args:
            account_value: Current account value
            current_price: Current price of the asset
            atr: Current ATR value
            confidence: Optional confidence score (0-1) for the trade
            volatility_factor: Optional volatility adjustment factor
            
        Returns:
            Dict containing position size details:
            {
                'position_size': float,  # Number of units
                'position_value': float,  # Position value in currency
                'risk_amount': float,     # Risk amount in currency
                'confidence_factor': float  # Applied confidence scaling
            }
        """
        # Calculate base risk amount
        risk_amount = account_value * self.config.risk_per_trade
        logger.debug(f"Risk amount: {risk_amount}")
        
        # Calculate ATR-based stop distance with volatility adjustment
        effective_volatility = volatility_factor if volatility_factor is not None else self.config.volatility_factor
        atr_stop_distance = atr * effective_volatility
        if atr_stop_distance <= 0:
            raise ZeroDivisionError("ATR stop distance must be greater than 0")
        logger.debug(f"ATR stop distance: {atr_stop_distance}")
            
        # Calculate raw position size based on risk and ATR
        # Position size = Risk amount / (ATR stop distance in currency terms)
        raw_position_size = risk_amount / (atr_stop_distance * current_price)
        logger.debug(f"Raw position size: {raw_position_size}")
        
        # Apply confidence scaling if provided
        confidence_factor = 1.0
        if confidence is not None:
            # Scale confidence linearly from 0 to threshold
            confidence_factor = confidence / self.config.confidence_threshold
            raw_position_size *= confidence_factor
        logger.debug(f"Position size after confidence: {raw_position_size}")
        
        # Calculate position value
        raw_position_value = raw_position_size * current_price
        
        # Calculate position limits
        max_position_value = account_value * self.config.max_position_size
        min_position_value = account_value * self.config.min_position_size
        logger.debug(f"Position value limits: {min_position_value} - {max_position_value}")
        
        # Only apply position size limits if we exceed them
        final_position_value = raw_position_value
        if raw_position_value > max_position_value:
            final_position_value = max_position_value
        elif raw_position_value < min_position_value:
            final_position_value = min_position_value
            
        final_position_size = final_position_value / current_price
        logger.debug(f"Final position size: {final_position_size}")
        
        return {
            'position_size': final_position_size,
            'position_value': final_position_value,
            'risk_amount': risk_amount,
            'confidence_factor': confidence_factor
        }
    
    def get_position_limits(
        self,
        account_value: float,
        current_price: float
    ) -> Dict[str, float]:
        """
        Calculate position size limits based on account value and current price.
        
        Args:
            account_value: Current account value
            current_price: Current price of the asset
            
        Returns:
            Dict containing position limits:
            {
                'max_units': float,
                'min_units': float,
                'max_value': float,
                'min_value': float
            }
        """
        max_value = account_value * self.config.max_position_size
        min_value = account_value * self.config.min_position_size
        
        return {
            'max_units': max_value / current_price,
            'min_units': min_value / current_price,
            'max_value': max_value,
            'min_value': min_value
        } 