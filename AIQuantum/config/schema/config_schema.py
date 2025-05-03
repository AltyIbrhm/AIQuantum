from pydantic import BaseModel, Field
from typing import List, Optional

class GeneralConfig(BaseModel):
    project_name: str
    version: str
    environment: str

class DataConfig(BaseModel):
    source: str
    symbols: List[str]
    timeframe: str
    lookback_days: int

class StrategyConfig(BaseModel):
    enabled_strategies: List[str]
    default_strategy: str

class RiskConfig(BaseModel):
    max_position_size: float = Field(ge=0.0, le=1.0)
    max_daily_loss: float = Field(ge=0.0, le=1.0)
    max_drawdown: float = Field(ge=0.0, le=1.0)

class TradingConfig(BaseModel):
    mode: str
    paper_balance: float
    live_api_key: str = ""
    live_api_secret: str = ""

class LoggingConfig(BaseModel):
    level: str
    file: str
    max_size: int
    backup_count: int

class Config(BaseModel):
    general: GeneralConfig
    data: DataConfig
    strategy: StrategyConfig
    risk: RiskConfig
    trading: TradingConfig
    logging: LoggingConfig 