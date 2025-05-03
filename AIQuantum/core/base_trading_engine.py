from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime

class BaseTradingEngine(ABC):
    """
    Abstract base class for all trading engines.
    All trading engine implementations must inherit from this class.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the trading engine with configuration.
        
        Args:
            config: Trading engine configuration dictionary
        """
        self.config = config
        self.name = config.get('name', self.__class__.__name__)
        self.enabled = config.get('enabled', True)
        self.positions = []
        self.trades = []
        self.balance = config.get('initial_balance', 10000.0)
        
    @abstractmethod
    def place_order(self,
                   symbol: str,
                   side: str,
                   order_type: str,
                   quantity: float,
                   price: Optional[float] = None) -> Dict[str, Any]:
        """
        Place an order with the exchange.
        
        Args:
            symbol: Trading pair symbol
            side: 'buy' or 'sell'
            order_type: Type of order (market, limit, etc.)
            quantity: Order quantity
            price: Order price (required for limit orders)
            
        Returns:
            Order details dictionary
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an existing order.
        
        Args:
            order_id: ID of the order to cancel
            
        Returns:
            True if order was cancelled successfully
        """
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get the status of an order.
        
        Args:
            order_id: ID of the order
            
        Returns:
            Order status dictionary
        """
        pass
    
    def open_position(self,
                     symbol: str,
                     side: str,
                     quantity: float,
                     price: float,
                     stop_loss: Optional[float] = None,
                     take_profit: Optional[float] = None) -> Dict[str, Any]:
        """
        Open a new position.
        
        Args:
            symbol: Trading pair symbol
            side: 'buy' or 'sell'
            quantity: Position size
            price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Position details dictionary
        """
        position = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'entry_price': price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'entry_time': datetime.now(),
            'status': 'open'
        }
        self.positions.append(position)
        return position
    
    def close_position(self,
                      position_id: str,
                      price: float,
                      reason: str = 'manual') -> Dict[str, Any]:
        """
        Close an existing position.
        
        Args:
            position_id: ID of the position to close
            price: Exit price
            reason: Reason for closing
            
        Returns:
            Closed position details
        """
        position = next((p for p in self.positions if p['id'] == position_id), None)
        if position:
            position['exit_price'] = price
            position['exit_time'] = datetime.now()
            position['status'] = 'closed'
            position['close_reason'] = reason
            position['pnl'] = self._calculate_pnl(position)
            return position
        return None
    
    def _calculate_pnl(self, position: Dict[str, Any]) -> float:
        """
        Calculate profit/loss for a position.
        
        Args:
            position: Position details dictionary
            
        Returns:
            Profit/loss amount
        """
        if position['side'] == 'buy':
            return (position['exit_price'] - position['entry_price']) * position['quantity']
        else:
            return (position['entry_price'] - position['exit_price']) * position['quantity']
    
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """
        Get list of currently open positions.
        
        Returns:
            List of open positions
        """
        return [p for p in self.positions if p['status'] == 'open']
    
    def get_closed_positions(self) -> List[Dict[str, Any]]:
        """
        Get list of closed positions.
        
        Returns:
            List of closed positions
        """
        return [p for p in self.positions if p['status'] == 'closed']
    
    def get_position_by_id(self, position_id: str) -> Optional[Dict[str, Any]]:
        """
        Get position details by ID.
        
        Args:
            position_id: ID of the position
            
        Returns:
            Position details if found, None otherwise
        """
        return next((p for p in self.positions if p['id'] == position_id), None)
    
    def get_account_balance(self) -> float:
        """
        Get current account balance.
        
        Returns:
            Current balance
        """
        return self.balance
    
    def update_balance(self, amount: float) -> None:
        """
        Update account balance.
        
        Args:
            amount: Amount to add (positive) or subtract (negative)
        """
        self.balance += amount
    
    def get_trading_history(self) -> List[Dict[str, Any]]:
        """
        Get complete trading history.
        
        Returns:
            List of all trades
        """
        return self.trades
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get current trading engine parameters.
        
        Returns:
            Dictionary of parameters
        """
        return self.config.get('parameters', {})
    
    def update_parameters(self, new_params: Dict[str, Any]) -> None:
        """
        Update trading engine parameters.
        
        Args:
            new_params: Dictionary of new parameters
        """
        if 'parameters' not in self.config:
            self.config['parameters'] = {}
        self.config['parameters'].update(new_params) 