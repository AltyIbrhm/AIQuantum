from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class TechnicalStrategyConfig(BaseModel):
    name: str
    parameters: Dict[str, float]
    enabled: bool = True

class MLStrategyConfig(BaseModel):
    name: str
    model_path: str
    confidence_threshold: float = Field(ge=0.0, le=1.0)
    lookback_window: int = Field(ge=1)
    enabled: bool = True

class SignalCombinerConfig(BaseModel):
    method: str  # 'weighted', 'majority', 'confidence'
    weights: Optional[Dict[str, float]] = None
    min_confidence: float = Field(ge=0.0, le=1.0)

class StrategyConfig(BaseModel):
    technical_strategies: List[TechnicalStrategyConfig]
    ml_strategies: List[MLStrategyConfig]
    signal_combiner: SignalCombinerConfig
    default_strategy: str
    min_trades_per_day: int = Field(ge=0)
    max_trades_per_day: int = Field(ge=1) 