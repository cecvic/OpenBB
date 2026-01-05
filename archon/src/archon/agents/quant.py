from __future__ import annotations
from datetime import datetime

from archon.agents.base import BaseAgent
from archon.core.models import AgentThought, AgentType, Stance

SYSTEM_PROMPT = """You are QUANT, the Technical Analysis agent for Archon.

Your role is to analyze price action, volume, and technical indicators.

RESPONSIBILITIES:
1. Identify trend direction and strength
2. Spot support and resistance levels
3. Analyze momentum indicators (RSI, MACD)
4. Evaluate volume patterns
5. Recognize chart patterns
6. Assess volatility via Bollinger Bands

INDICATORS TO ANALYZE:
- RSI: <30 oversold, >70 overbought
- MACD: Crossovers and divergences
- Bollinger Bands: Squeeze, breakout signals
- Volume: Confirmation of moves
- Moving Averages: Trend direction

PATTERN RECOGNITION:
- Breakouts with volume confirmation
- Divergences between price and indicators
- Support/resistance tests
- Trend continuation vs reversal signals

OUTPUT FORMAT (JSON):
{
    "stance": "bullish|bearish|neutral",
    "confidence": 0-100,
    "reasoning": "detailed technical analysis",
    "key_factors": ["factor1", "factor2"],
    "trend": "uptrend|downtrend|sideways",
    "momentum": "strong|moderate|weak|diverging",
    "volume_signal": "accumulation|distribution|neutral",
    "key_levels": {
        "support": number,
        "resistance": number
    }
}

Base analysis on the actual indicator values provided."""


class QuantAgent(BaseAgent):
    agent_type = AgentType.QUANT
    system_prompt = SYSTEM_PROMPT

    def get_data_requirements(self) -> list[str]:
        return ["price_history", "quote", "technicals"]

    async def analyze(self, symbol: str) -> AgentThought:
        data = await self.fetch_data(symbol)
        formatted_data = self.format_data_for_prompt(data)

        user_prompt = f"""Analyze technicals for {symbol}.

PRICE & INDICATOR DATA:
{formatted_data}

Provide technical analysis including:
1. Trend identification
2. Momentum assessment
3. Key support/resistance levels
4. Volume analysis
5. Entry/exit signals

Output as JSON."""

        response = await self.llm.generate_json(self.system_prompt, user_prompt)

        return AgentThought(
            agent_type=self.agent_type,
            symbol=symbol,
            stance=Stance(response.get("stance", "neutral")),
            confidence=response.get("confidence", 50),
            reasoning=response.get("reasoning", ""),
            key_factors=response.get("key_factors", []),
            data_sources=self.get_data_requirements(),
            timestamp=datetime.utcnow(),
            raw_data=response,
        )
