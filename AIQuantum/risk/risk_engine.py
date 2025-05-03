from typing import Dict, Optional, Tuple, Any
from datetime import datetime
from .constraints import RiskConstraintsManager
from ..utils.logger import get_logger

class RiskEngine:
    """
    Risk management engine for evaluating trades and managing risk.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize risk engine.
        
        Args:
            config: Configuration dictionary
        """
        self.logger = get_logger(__name__)
        
        # Initialize constraints manager with default config if None
        default_config = {
            'min_position_value': 100,
            'max_position_value': 10000,
            'max_portfolio_risk': 0.1,
            'max_daily_drawdown': 0.05,
            'max_open_trades': 3,
            'trade_cooldown_minutes': 30
        }
        self.config = config or default_config
        self.constraints = RiskConstraintsManager(self.config)
        
        # Initialize state
        self.open_trades = 0
        self.last_trade_time = 0
        self.daily_drawdown = 0.0
        self.portfolio_value = 0.0
        
        self.logger.info("Initialized risk engine")
    
    def calculate_position_size(self, portfolio_value: float, risk_per_trade: float) -> float:
        """
        Calculate position size based on portfolio value and risk per trade.
        
        Args:
            portfolio_value: Current portfolio value
            risk_per_trade: Risk percentage per trade
            
        Returns:
            Calculated position size
            
        Raises:
            ValueError: If input parameters are invalid
        """
        if portfolio_value <= 0:
            raise ValueError("Portfolio value must be positive")
        if risk_per_trade <= 0:
            raise ValueError("Risk per trade must be positive")
        if risk_per_trade > 1:
            raise ValueError("Risk per trade must be less than 100%")
            
        position_size = portfolio_value * risk_per_trade
        return max(position_size, self.config['min_position_value'])

    def validate_trade(
        self,
        portfolio_value: float,
        daily_drawdown: float = None,
        num_open_trades: int = None,
        position_size: float = None,
        last_trade_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Validate a trade against risk constraints.
        
        Args:
            portfolio_value: Current portfolio value
            daily_drawdown: Current daily drawdown
            num_open_trades: Number of currently open trades
            position_size: Size of the proposed trade
            last_trade_time: Time of the last trade
            
        Returns:
            Dictionary with validation result and reason
            
        Raises:
            KeyError: If required fields are missing
        """
        # Check required fields
        if daily_drawdown is None or num_open_trades is None or position_size is None:
            raise KeyError("Missing required fields: daily_drawdown, num_open_trades, position_size")
            
        validation_result = self.constraints.validate_trade(
            portfolio_value=portfolio_value,
            daily_drawdown=daily_drawdown,
            num_open_trades=num_open_trades,
            position_size=position_size,
            last_trade_time=last_trade_time
        )
        return validation_result
    
    def evaluate_trade(
        self,
        decision: str,
        confidence: float,
        volatility: float,
        trend_alignment: float,
        current_price: float,
        portfolio_value: float
    ) -> Tuple[bool, float, Dict]:
        """
        Evaluate a trade decision against risk constraints.
        
        Args:
            decision: Trading decision ('BUY', 'SELL', 'HOLD')
            confidence: Signal confidence (0-1)
            volatility: Market volatility (0-1)
            trend_alignment: Trend alignment score (0-1)
            current_price: Current asset price
            portfolio_value: Current portfolio value
            
        Returns:
            Tuple of (is_valid, position_size, metadata)
        """
        try:
            # Update portfolio value
            self.portfolio_value = portfolio_value
            
            # Initialize metadata
            metadata = {
                'decision': decision,
                'confidence': confidence,
                'volatility': volatility,
                'trend_alignment': trend_alignment,
                'current_price': current_price,
                'portfolio_value': portfolio_value,
                'constraints': self.constraints.get_metadata()
            }
            
            # If HOLD, return immediately
            if decision == 'HOLD':
                return False, 0.0, metadata
            
            # Calculate base position size
            base_size = self.constraints.risk_constraints.max_portfolio_risk
            
            # Calculate adjusted position size
            position_size = self.constraints.calculate_position_size(
                base_size=base_size,
                confidence=confidence,
                volatility=volatility,
                trend_alignment=trend_alignment
            )
            
            # Calculate position value
            position_value = position_size * portfolio_value
            
            # Validate trade against constraints
            current_time = int(datetime.now().timestamp())
            is_valid = self.constraints.validate_trade(
                current_drawdown=self.daily_drawdown,
                open_trades=self.open_trades,
                last_trade_time=self.last_trade_time,
                current_time=current_time,
                position_value=position_value,
                portfolio_value=portfolio_value
            )
            
            # Update metadata
            metadata.update({
                'position_size': position_size,
                'position_value': position_value,
                'is_valid': is_valid,
                'constraints_violated': not is_valid
            })
            
            # If trade is valid, update state
            if is_valid:
                self.last_trade_time = current_time
                if decision == 'BUY':
                    self.open_trades += 1
            
            return is_valid, position_size, metadata
            
        except Exception as e:
            self.logger.error(f"Error evaluating trade: {str(e)}")
            return False, 0.0, metadata
    
    def update_drawdown(self, new_drawdown: float) -> None:
        """
        Update daily drawdown.
        
        Args:
            new_drawdown: New drawdown value
        """
        try:
            self.daily_drawdown = new_drawdown
            self.logger.info(f"Updated daily drawdown to {new_drawdown:.2%}")
        except Exception as e:
            self.logger.error(f"Error updating drawdown: {str(e)}")
    
    def close_trade(self) -> None:
        """
        Update state when a trade is closed.
        """
        try:
            if self.open_trades > 0:
                self.open_trades -= 1
                self.logger.info(f"Closed trade. Open trades: {self.open_trades}")
        except Exception as e:
            self.logger.error(f"Error closing trade: {str(e)}")
    
    def reset_daily(self) -> None:
        """
        Reset daily metrics.
        """
        try:
            self.daily_drawdown = 0.0
            self.logger.info("Reset daily metrics")
        except Exception as e:
            self.logger.error(f"Error resetting daily metrics: {str(e)}")
    
    def get_state(self) -> Dict:
        """
        Get current risk engine state.
        
        Returns:
            Dictionary with current state
        """
        return {
            'open_trades': self.open_trades,
            'last_trade_time': self.last_trade_time,
            'daily_drawdown': self.daily_drawdown,
            'portfolio_value': self.portfolio_value,
            'constraints': self.constraints.get_metadata()
        } 