from typing import Dict, Optional, Any
from dataclasses import dataclass
from ..utils.logger import get_logger
from datetime import datetime, timedelta

@dataclass
class PositionConstraints:
    """
    Position sizing constraints for risk management.
    """
    min_value: float
    max_value: float
    max_portfolio_risk: float = 0.1  # 10% default

@dataclass
class RiskConstraints:
    """
    Risk management constraints and limits.
    """
    max_daily_drawdown: float
    max_open_trades: int
    trade_cooldown_minutes: int

class RiskConstraintsManager:
    """
    Manages risk constraints and position sizing rules.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize risk constraints manager.
        
        Args:
            config: Configuration dictionary
        """
        self.logger = get_logger(__name__)
        
        # Initialize position constraints
        self.position_constraints = PositionConstraints(
            min_value=config.get('min_position_value', 100),
            max_value=config.get('max_position_value', 10000),
            max_portfolio_risk=config.get('max_portfolio_risk', 0.1)
        )
        
        # Initialize risk constraints
        self.risk_constraints = RiskConstraints(
            max_daily_drawdown=config.get('max_daily_drawdown', 0.05),
            max_open_trades=config.get('max_open_trades', 3),
            trade_cooldown_minutes=config.get('trade_cooldown_minutes', 30)
        )
        
        self.logger.info(f"Initialized risk constraints: {self.get_metadata()}")
    
    def validate_trade(
        self,
        portfolio_value: float,
        daily_drawdown: float,
        num_open_trades: int,
        position_size: float,
        last_trade_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Validate a trade against risk constraints.
        
        Args:
            portfolio_value: Current portfolio value
            daily_drawdown: Current daily drawdown
            num_open_trades: Number of currently open trades
            position_size: Proposed position size
            last_trade_time: Time of last trade
            
        Returns:
            Dictionary with validation result and reason
        """
        try:
            self.logger.debug(f"Validating trade: portfolio_value={portfolio_value}, daily_drawdown={daily_drawdown}, num_open_trades={num_open_trades}, position_size={position_size}, last_trade_time={last_trade_time}")
            
            # Check position size constraints
            if position_size < self.position_constraints.min_value:
                self.logger.debug(f"Position size {position_size} below minimum {self.position_constraints.min_value}")
                return {
                    'valid': False,
                    'reason': f"Position size {position_size} below minimum {self.position_constraints.min_value}"
                }
            
            if position_size > self.position_constraints.max_value:
                self.logger.debug(f"Position size {position_size} above maximum {self.position_constraints.max_value}")
                return {
                    'valid': False,
                    'reason': f"Position size {position_size} above maximum {self.position_constraints.max_value}"
                }
            
            # Check portfolio risk
            position_risk = position_size / portfolio_value
            self.logger.debug(f"Position risk: {position_risk:.2%}")
            if position_risk > self.position_constraints.max_portfolio_risk:
                self.logger.debug(f"Position risk {position_risk:.2%} exceeds maximum {self.position_constraints.max_portfolio_risk:.2%}")
                return {
                    'valid': False,
                    'reason': f"Position risk {position_risk:.2%} exceeds maximum {self.position_constraints.max_portfolio_risk:.2%}"
                }
            
            # Check drawdown
            self.logger.debug(f"Daily drawdown: {daily_drawdown:.2%}")
            if daily_drawdown > self.risk_constraints.max_daily_drawdown:
                self.logger.debug(f"Daily drawdown {daily_drawdown:.2%} exceeds maximum {self.risk_constraints.max_daily_drawdown:.2%}")
                return {
                    'valid': False,
                    'reason': f"Daily drawdown {daily_drawdown:.2%} exceeds maximum {self.risk_constraints.max_daily_drawdown:.2%}"
                }
            
            # Check open trades
            self.logger.debug(f"Number of open trades: {num_open_trades}")
            if num_open_trades >= self.risk_constraints.max_open_trades:
                self.logger.debug(f"Maximum number of open trades ({self.risk_constraints.max_open_trades}) reached")
                return {
                    'valid': False,
                    'reason': f"Maximum number of open trades ({self.risk_constraints.max_open_trades}) reached"
                }
            
            # Check trade cooldown
            if last_trade_time is not None:
                cooldown = timedelta(minutes=self.risk_constraints.trade_cooldown_minutes)
                time_since_last = datetime.now() - last_trade_time
                self.logger.debug(f"Time since last trade: {time_since_last.total_seconds()/60:.1f} minutes")
                if time_since_last < cooldown:
                    self.logger.debug(f"Trade cooldown period not elapsed ({time_since_last.total_seconds()/60:.1f} minutes since last trade)")
                    return {
                        'valid': False,
                        'reason': f"Trade cooldown period not elapsed ({time_since_last.total_seconds()/60:.1f} minutes since last trade)"
                    }
            
            # All checks passed
            self.logger.debug("All constraints satisfied")
            return {
                'valid': True,
                'reason': "All constraints satisfied",
                'metadata': {
                    'position_risk': position_risk,
                    'daily_drawdown': daily_drawdown,
                    'num_open_trades': num_open_trades,
                    'position_size': position_size,
                    'portfolio_value': portfolio_value
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error validating trade: {str(e)}")
            return {'valid': False, 'reason': f"Error validating trade: {str(e)}"}
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the risk constraints.
        
        Returns:
            Dictionary containing constraints metadata
        """
        return {
            'position_constraints': {
                'min_value': self.position_constraints.min_value,
                'max_value': self.position_constraints.max_value,
                'max_portfolio_risk': self.position_constraints.max_portfolio_risk
            },
            'risk_constraints': {
                'max_daily_drawdown': self.risk_constraints.max_daily_drawdown,
                'max_open_trades': self.risk_constraints.max_open_trades,
                'trade_cooldown_minutes': self.risk_constraints.trade_cooldown_minutes
            }
        } 