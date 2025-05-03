from pydantic import BaseModel, Field
from typing import Optional

class PositionSizingConfig(BaseModel):
    max_position_size: float = Field(ge=0.0, le=1.0)
    min_position_size: float = Field(ge=0.0, le=1.0)
    position_size_increment: float = Field(ge=0.0, le=1.0)

class RiskLimitsConfig(BaseModel):
    max_daily_loss: float = Field(ge=0.0, le=1.0)
    max_drawdown: float = Field(ge=0.0, le=1.0)
    max_leverage: float = Field(ge=0.0)
    max_open_positions: int = Field(ge=1)

class StopLossConfig(BaseModel):
    trailing_stop: bool
    trailing_stop_distance: float = Field(ge=0.0, le=1.0)
    hard_stop_loss: float = Field(ge=0.0, le=1.0)

class RiskMetricsConfig(BaseModel):
    var_confidence: float = Field(ge=0.0, le=1.0)
    var_lookback_days: int = Field(ge=1)
    max_correlation: float = Field(ge=0.0, le=1.0)

class MonitoringConfig(BaseModel):
    check_interval: int = Field(ge=1)
    alert_thresholds: dict

class RiskConfig(BaseModel):
    position_sizing: PositionSizingConfig
    risk_limits: RiskLimitsConfig
    stop_loss: StopLossConfig
    risk_metrics: RiskMetricsConfig
    monitoring: MonitoringConfig 