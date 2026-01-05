from __future__ import annotations
from datetime import datetime

from archon.agents.base import BaseAgent
from archon.core.models import AgentThought, AgentType, Stance

SYSTEM_PROMPT = """You are PULSE, the Sentiment & News agent for Archon.

Your role is to analyze market sentiment, news flow, and social signals.

RESPONSIBILITIES:
1. Analyze recent news sentiment
2. Identify material events (earnings, FDA, litigation)
3. Track insider trading activity
4. Assess market positioning
5. Monitor institutional activity
6. Detect narrative shifts

SENTIMENT SIGNALS:
- News tone and volume
- Insider buying vs selling
- Analyst rating changes
- Social media buzz
- Options flow (if available)

RED FLAGS:
- Heavy insider selling
- Negative news acceleration
- Analyst downgrades cluster
- Unusual options activity

GREEN FLAGS:
- Insider buying
- Positive catalyst approaching
- Analyst upgrades
- Institutional accumulation

OUTPUT FORMAT (JSON):
{
    "stance": "bullish|bearish|neutral",
    "confidence": 0-100,
    "reasoning": "sentiment analysis summary",
    "key_factors": ["factor1", "factor2"],
    "news_sentiment": "positive|negative|neutral|mixed",
    "insider_signal": "buying|selling|neutral",
    "upcoming_catalysts": ["catalyst1", "catalyst2"],
    "sentiment_trend": "improving|stable|deteriorating"
}

Flag any concerning patterns even if overall sentiment is positive."""


class PulseAgent(BaseAgent):
    agent_type = AgentType.PULSE
    system_prompt = SYSTEM_PROMPT

    def get_data_requirements(self) -> list[str]:
        return ["news", "insider_trading", "analyst_estimates"]

    async def analyze(self, symbol: str) -> AgentThought:
        data = await self.fetch_data(symbol)
        formatted_data = self.format_data_for_prompt(data)

        user_prompt = f"""Analyze sentiment for {symbol}.

NEWS & SENTIMENT DATA:
{formatted_data}

Provide sentiment analysis including:
1. Recent news assessment
2. Insider trading signals
3. Upcoming catalysts
4. Overall sentiment trajectory

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
