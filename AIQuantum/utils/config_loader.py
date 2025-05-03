import yaml
import os
from typing import Dict, Any
from pathlib import Path
from ..config.schema.config_schema import Config
from ..config.schema.risk_schema import RiskConfig
from ..config.schema.strategy_schema import StrategyConfig

class ConfigLoader:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_cache: Dict[str, Any] = {}

    def load_config(self, config_name: str) -> Dict[str, Any]:
        """
        Load a configuration file and cache it
        """
        if config_name in self.config_cache:
            return self.config_cache[config_name]

        config_path = self.config_dir / f"{config_name}.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            content = f.read()
            if not content.strip():
                raise yaml.YAMLError("Empty configuration file")
            
            config = yaml.safe_load(content)
            if config is None:
                raise yaml.YAMLError("Invalid YAML configuration")
            
            self.config_cache[config_name] = config
            return config

    def get_base_config(self) -> Config:
        """
        Load and validate base configuration
        """
        config = self.load_config("config")
        return Config(**config)

    def get_risk_config(self) -> RiskConfig:
        """
        Load and validate risk configuration
        """
        config = self.load_config("risk_config")
        return RiskConfig(**config)

    def get_strategy_config(self) -> StrategyConfig:
        """
        Load and validate strategy configuration
        """
        config = self.load_config("config")["strategy"]
        return StrategyConfig(**config)

    def get_live_config(self) -> Dict[str, Any]:
        """
        Load live trading configuration
        """
        return self.load_config("live_config")

    def clear_cache(self):
        """
        Clear the configuration cache
        """
        self.config_cache.clear() 