from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd

class BaseRiskManager(ABC):
    """
    Abstract base class for all risk management systems.
    All risk management implementations must inherit from this class.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the risk manager with configuration.
        
        Args:
            config: Risk management configuration dictionary
        """
        self.config = config
        self.name = config.get('name', self.__class__.__name__)
        self.enabled = config.get('enabled', True)
        
    @abstractmethod
    def validate_position(self, 
                         position_size: float,
                         price: float,
                         balance: float,
                         open_positions: List[Dict[str, Any]]) -> bool:
        """
        Validate if a position can be opened based on risk rules.
        
        Args:
            position_size: Size of the proposed position
            price: Current price
            balance: Available balance
            open_positions: List of currently open positions
            
        Returns:
            True if position is allowed, False otherwise
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self,
                              signal_strength: float,
                              price: float,
                              balance: float,
                              risk_per_trade: float) -> float:
        """
        Calculate the maximum allowed position size based on risk rules.
        
        Args:
            signal_strength: Strength of the trading signal (-1 to 1)
            price: Current price
            balance: Available balance
            risk_per_trade: Maximum risk per trade as a percentage
            
        Returns:
            Maximum allowed position size
        """
        pass
    
    @abstractmethod
    def calculate_stop_loss(self,
                          position_size: float,
                          price: float,
                          balance: float) -> float:
        """
        Calculate stop loss level for a position.
        
        Args:
            position_size: Size of the position
            price: Entry price
            balance: Available balance
            
        Returns:
            Stop loss price level
        """
        pass
    
    def validate_daily_loss(self, daily_pnl: float, balance: float) -> bool:
        """
        Validate if daily loss is within limits.
        
        Args:
            daily_pnl: Today's profit/loss
            balance: Available balance
            
        Returns:
            True if daily loss is acceptable, False otherwise
        """
        max_daily_loss = self.config.get('max_daily_loss', 0.02)
        return (daily_pnl / balance) >= -max_daily_loss
    
    def validate_drawdown(self, current_drawdown: float) -> bool:
        """
        Validate if current drawdown is within limits.
        
        Args:
            current_drawdown: Current drawdown as a percentage
            
        Returns:
            True if drawdown is acceptable, False otherwise
        """
        max_drawdown = self.config.get('max_drawdown', 0.1)
        return current_drawdown <= max_drawdown
    
    def get_risk_metrics(self, positions: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate various risk metrics for current positions.
        
        Args:
            positions: List of current positions
            
        Returns:
            Dictionary of risk metrics
        """
        return {
            'total_exposure': sum(pos['size'] for pos in positions),
            'max_drawdown': self._calculate_max_drawdown(positions),
            'var_95': self._calculate_var(positions, 0.95),
            'sharpe_ratio': self._calculate_sharpe_ratio(positions)
        }
    
    def _calculate_max_drawdown(self, positions: List[Dict[str, Any]]) -> float:
        """
        Calculate maximum drawdown from positions.
        """
        # Implementation depends on available position data
        return 0.0
    
    def _calculate_var(self, positions: List[Dict[str, Any]], confidence: float) -> float:
        """
        Calculate Value at Risk at specified confidence level.
        """
        # Implementation depends on available position data
        return 0.0
    
    def _calculate_sharpe_ratio(self, positions: List[Dict[str, Any]]) -> float:
        """
        Calculate Sharpe ratio from positions.
        """
        # Implementation depends on available position data
        return 0.0
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get current risk management parameters.
        
        Returns:
            Dictionary of parameters
        """
        return self.config.get('parameters', {})
    
    def update_parameters(self, new_params: Dict[str, Any]) -> None:
        """
        Update risk management parameters.
        
        Args:
            new_params: Dictionary of new parameters
        """
        if 'parameters' not in self.config:
            self.config['parameters'] = {}
        self.config['parameters'].update(new_params) 