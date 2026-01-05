from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    SENTINEL = "sentinel"
    ORACLE = "oracle"
    QUANT = "quant"
    PULSE = "pulse"


class Stance(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class AgentThought(BaseModel):
    agent_type: AgentType
    symbol: str
    stance: Stance
    confidence: float = Field(ge=0, le=100)
    reasoning: str
    key_factors: list[str]
    data_sources: list[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    raw_data: dict[str, Any] = Field(default_factory=dict)


class RiskAssessment(BaseModel):
    approved: bool
    veto_reason: str | None = None
    risk_level: RiskLevel
    position_size_pct: float = Field(ge=0, le=100)
    stop_loss_pct: float | None = None
    risk_reward_ratio: float | None = None
    warnings: list[str] = Field(default_factory=list)


class Consensus(BaseModel):
    symbol: str
    overall_stance: Stance
    overall_confidence: float = Field(ge=0, le=100)
    agent_thoughts: list[AgentThought]
    risk_assessment: RiskAssessment
    dissenting_opinions: list[str] = Field(default_factory=list)
    suggested_action: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AnalysisResult(BaseModel):
    symbol: str
    consensus: Consensus
    glass_box_summary: str
    execution_time_seconds: float
    providers_used: list[str]
