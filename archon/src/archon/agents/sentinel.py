from __future__ import annotations
from datetime import datetime

from archon.agents.base import BaseAgent
from archon.core.models import (
    AgentThought,
    AgentType,
    RiskAssessment,
    RiskLevel,
    Stance,
)

SYSTEM_PROMPT = """You are SENTINEL, the Risk Management agent for Archon.

Your role is to evaluate trading decisions through a risk-first lens.
You have VETO POWER over all trading recommendations.

RESPONSIBILITIES:
1. Assess position sizing based on portfolio risk
2. Evaluate stop-loss placement
3. Calculate risk/reward ratios
4. Identify market regime (trending, ranging, volatile)
5. Flag excessive concentration risk
6. Detect potential black swan indicators

RISK LEVELS:
- LOW: Normal conditions, proceed with standard sizing
- MEDIUM: Heightened caution, reduce position size by 50%
- HIGH: Significant risk, reduce to minimal position or wait
- EXTREME: VETO - do not trade

OUTPUT FORMAT (JSON):
{
    "approved": true/false,
    "veto_reason": "string or null",
    "risk_level": "low|medium|high|extreme",
    "position_size_pct": 0-10,
    "stop_loss_pct": number,
    "risk_reward_ratio": number,
    "warnings": ["list of concerns"],
    "reasoning": "detailed explanation",
    "key_factors": ["factor1", "factor2"]
}

Be conservative. Protecting capital is more important than maximizing gains."""


class SentinelAgent(BaseAgent):
    agent_type = AgentType.SENTINEL
    system_prompt = SYSTEM_PROMPT

    def get_data_requirements(self) -> list[str]:
        return ["price_history", "quote"]

    async def analyze(self, symbol: str) -> AgentThought:
        data = await self.fetch_data(symbol)
        formatted_data = self.format_data_for_prompt(data)

        user_prompt = f"""Analyze risk for {symbol}.

MARKET DATA:
{formatted_data}

Evaluate:
1. Current volatility vs historical
2. Position sizing recommendation (max {self.config.max_position_size_pct}%)
3. Appropriate stop-loss level
4. Overall risk level

Provide your risk assessment as JSON."""

        response = await self.llm.generate_json(self.system_prompt, user_prompt)

        return AgentThought(
            agent_type=self.agent_type,
            symbol=symbol,
            stance=self._determine_stance(response),
            confidence=self._calculate_confidence(response),
            reasoning=response.get("reasoning", ""),
            key_factors=response.get("key_factors", []),
            data_sources=["price_history", "quote"],
            timestamp=datetime.utcnow(),
            raw_data=response,
        )

    def extract_risk_assessment(self, thought: AgentThought) -> RiskAssessment:
        raw = thought.raw_data
        return RiskAssessment(
            approved=raw.get("approved", True),
            veto_reason=raw.get("veto_reason"),
            risk_level=RiskLevel(raw.get("risk_level", "medium")),
            position_size_pct=raw.get("position_size_pct", self.config.default_position_size_pct),
            stop_loss_pct=raw.get("stop_loss_pct"),
            risk_reward_ratio=raw.get("risk_reward_ratio"),
            warnings=raw.get("warnings", []),
        )

    def _determine_stance(self, response: dict) -> Stance:
        if response.get("risk_level") == "extreme":
            return Stance.BEARISH
        if response.get("approved", True):
            return Stance.NEUTRAL
        return Stance.BEARISH

    def _calculate_confidence(self, response: dict) -> float:
        risk_confidence_map = {
            "low": 85,
            "medium": 70,
            "high": 55,
            "extreme": 90,
        }
        return risk_confidence_map.get(response.get("risk_level", "medium"), 70)
