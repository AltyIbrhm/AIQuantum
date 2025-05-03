from typing import Dict, Optional
from dataclasses import dataclass
from ..utils.logger import get_logger

@dataclass
class PositionConstraints:
    """
    Position sizing constraints for risk management.
    """
    max_position_size: float = 0.1  # Maximum position size as fraction of portfolio
    min_position_size: float = 0.01  # Minimum position size as fraction of portfolio
    confidence_scaling: bool = True  # Scale position size based on confidence
    volatility_scaling: bool = True  # Scale position size based on volatility
    trend_scaling: bool = True  # Scale position size based on trend alignment

@dataclass
class RiskConstraints:
    """
    Risk management constraints and limits.
    """
    max_daily_drawdown: float = 0.02  # Maximum daily drawdown (2%)
    max_open_trades: int = 5  # Maximum number of concurrent trades
    min_trade_interval: int = 300  # Minimum seconds between trades
    max_position_value: float = 0.2  # Maximum value of any single position
    max_portfolio_risk: float = 0.1  # Maximum risk per trade as fraction of portfolio
    stop_loss_pct: float = 0.02  # Default stop loss percentage
    take_profit_pct: float = 0.04  # Default take profit percentage

class RiskConstraintsManager:
    """
    Manages risk constraints and position sizing rules.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize risk constraints manager.
        
        Args:
            config: Configuration dictionary for constraints
        """
        self.logger = get_logger(__name__)
        
        # Initialize constraints
        self.position_constraints = PositionConstraints()
        self.risk_constraints = RiskConstraints()
        
        # Update with provided config
        if config:
            self._update_constraints(config)
        
        self.logger.info("Initialized risk constraints manager")
    
    def _update_constraints(self, config: Dict) -> None:
        """
        Update constraints from configuration.
        
        Args:
            config: Configuration dictionary
        """
        try:
            # Update position constraints
            if 'position' in config:
                pos_config = config['position']
                for key, value in pos_config.items():
                    if hasattr(self.position_constraints, key):
                        setattr(self.position_constraints, key, value)
            
            # Update risk constraints
            if 'risk' in config:
                risk_config = config['risk']
                for key, value in risk_config.items():
                    if hasattr(self.risk_constraints, key):
                        setattr(self.risk_constraints, key, value)
            
            self.logger.info("Updated risk constraints from config")
        except Exception as e:
            self.logger.error(f"Error updating constraints: {str(e)}")
            raise
    
    def calculate_position_size(
        self,
        base_size: float,
        confidence: float,
        volatility: float,
        trend_alignment: float
    ) -> float:
        """
        Calculate position size based on constraints and market conditions.
        
        Args:
            base_size: Base position size
            confidence: Signal confidence (0-1)
            volatility: Market volatility (0-1)
            trend_alignment: Trend alignment score (0-1)
            
        Returns:
            Adjusted position size
        """
        try:
            # Start with base size
            size = base_size
            
            # Apply confidence scaling
            if self.position_constraints.confidence_scaling:
                size *= confidence
            
            # Apply volatility scaling
            if self.position_constraints.volatility_scaling:
                size *= (1 - volatility)  # Reduce size in high volatility
            
            # Apply trend scaling
            if self.position_constraints.trend_scaling:
                size *= trend_alignment
            
            # Apply position size limits
            size = max(
                self.position_constraints.min_position_size,
                min(size, self.position_constraints.max_position_size)
            )
            
            return size
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return self.position_constraints.min_position_size
    
    def validate_trade(
        self,
        current_drawdown: float,
        open_trades: int,
        last_trade_time: int,
        current_time: int,
        position_value: float,
        portfolio_value: float
    ) -> bool:
        """
        Validate trade against risk constraints.
        
        Args:
            current_drawdown: Current daily drawdown
            open_trades: Number of currently open trades
            last_trade_time: Timestamp of last trade
            current_time: Current timestamp
            position_value: Value of the position
            portfolio_value: Total portfolio value
            
        Returns:
            True if trade is valid, False otherwise
        """
        try:
            # Check daily drawdown
            if current_drawdown > self.risk_constraints.max_daily_drawdown:
                self.logger.warning(f"Daily drawdown {current_drawdown:.2%} exceeds limit")
                return False
            
            # Check open trades
            if open_trades >= self.risk_constraints.max_open_trades:
                self.logger.warning(f"Maximum open trades ({self.risk_constraints.max_open_trades}) reached")
                return False
            
            # Check trade interval
            if (current_time - last_trade_time) < self.risk_constraints.min_trade_interval:
                self.logger.warning("Trade interval too short")
                return False
            
            # Check position value
            if position_value > (portfolio_value * self.risk_constraints.max_position_value):
                self.logger.warning("Position value exceeds limit")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error validating trade: {str(e)}")
            return False
    
    def get_metadata(self) -> Dict:
        """
        Get risk constraints metadata.
        
        Returns:
            Dictionary with constraints metadata
        """
        return {
            'position_constraints': {
                'max_position_size': self.position_constraints.max_position_size,
                'min_position_size': self.position_constraints.min_position_size,
                'confidence_scaling': self.position_constraints.confidence_scaling,
                'volatility_scaling': self.position_constraints.volatility_scaling,
                'trend_scaling': self.position_constraints.trend_scaling
            },
            'risk_constraints': {
                'max_daily_drawdown': self.risk_constraints.max_daily_drawdown,
                'max_open_trades': self.risk_constraints.max_open_trades,
                'min_trade_interval': self.risk_constraints.min_trade_interval,
                'max_position_value': self.risk_constraints.max_position_value,
                'max_portfolio_risk': self.risk_constraints.max_portfolio_risk,
                'stop_loss_pct': self.risk_constraints.stop_loss_pct,
                'take_profit_pct': self.risk_constraints.take_profit_pct
            }
        } 