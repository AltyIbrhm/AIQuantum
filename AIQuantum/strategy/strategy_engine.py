from typing import Dict, List, Optional, Any
import pandas as pd
from ..utils.logger import get_logger

class StrategyEngine:
    """Engine for managing and executing trading strategies."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the strategy engine with configuration."""
        self.config = config
        self.logger = get_logger(__name__)
        self.strategies = {}
        self._initialize_strategies()
    
    def _initialize_strategies(self):
        """Initialize trading strategies from configuration."""
        strategy_configs = self.config.get('strategies', {})
        for name, config in strategy_configs.items():
            try:
                strategy_class = self._get_strategy_class(config['type'])
                self.strategies[name] = strategy_class(config)
                self.logger.info(f"Initialized strategy: {name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize strategy {name}: {str(e)}")
    
    def _get_strategy_class(self, strategy_type: str):
        """Get the strategy class based on type."""
        # This would be expanded with actual strategy imports
        strategy_map = {
            'ema': None,  # EMAStrategy
            'rsi': None,  # RSIStrategy
            'macd': None,  # MACDStrategy
            'bollinger': None,  # BollingerStrategy
        }
        if strategy_type not in strategy_map:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        return strategy_map[strategy_type]
    
    def execute_strategies(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Execute all registered strategies on the provided data."""
        results = {}
        for name, strategy in self.strategies.items():
            try:
                signals = strategy.calculate_signals(data)
                results[name] = signals
                self.logger.info(f"Executed strategy {name}")
            except Exception as e:
                self.logger.error(f"Error executing strategy {name}: {str(e)}")
                results[name] = None
        return results
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate data for all strategies."""
        for name, strategy in self.strategies.items():
            try:
                if not strategy.validate_data(data):
                    self.logger.warning(f"Data validation failed for strategy {name}")
                    return False
            except Exception as e:
                self.logger.error(f"Error validating data for strategy {name}: {str(e)}")
                return False
        return True
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the strategy engine and its strategies."""
        return {
            'active_strategies': list(self.strategies.keys()),
            'strategy_configs': self.config.get('strategies', {}),
            'strategy_metadata': {
                name: strategy.get_metadata()
                for name, strategy in self.strategies.items()
            }
        } 