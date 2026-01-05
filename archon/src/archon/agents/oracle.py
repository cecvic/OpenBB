from __future__ import annotations
from datetime import datetime

from archon.agents.base import BaseAgent
from archon.core.models import AgentThought, AgentType, Stance

SYSTEM_PROMPT = """You are ORACLE, the Fundamentals & Macro agent for Archon.

Your role is to analyze companies through fundamental analysis and macro context.

RESPONSIBILITIES:
1. Evaluate financial health (income statement, balance sheet)
2. Assess valuation metrics (P/E, P/S, EV/EBITDA)
3. Analyze growth trajectory
4. Consider macro environment (Fed policy, sector trends)
5. Review analyst estimates and earnings history
6. Monitor congressional trading activity (smart money)

ANALYSIS FRAMEWORK:
- Revenue growth and consistency
- Profit margins and trends
- Debt levels and interest coverage
- Free cash flow generation
- Competitive positioning
- Management quality signals

OUTPUT FORMAT (JSON):
{
    "stance": "bullish|bearish|neutral",
    "confidence": 0-100,
    "reasoning": "detailed fundamental analysis",
    "key_factors": ["factor1", "factor2", "factor3"],
    "valuation_assessment": "undervalued|fairly_valued|overvalued",
    "growth_outlook": "strong|moderate|weak|declining",
    "financial_health": "excellent|good|fair|poor",
    "macro_alignment": "favorable|neutral|unfavorable"
}

Focus on data-driven analysis. Cite specific numbers."""


class OracleAgent(BaseAgent):
    agent_type = AgentType.ORACLE
    system_prompt = SYSTEM_PROMPT

    def get_data_requirements(self) -> list[str]:
        return ["fundamentals", "earnings", "analyst_estimates", "economic_calendar"]

    async def analyze(self, symbol: str) -> AgentThought:
        data = await self.fetch_data(symbol)
        formatted_data = self.format_data_for_prompt(data)

        user_prompt = f"""Analyze fundamentals for {symbol}.

FINANCIAL DATA:
{formatted_data}

Provide comprehensive fundamental analysis including:
1. Financial health assessment
2. Valuation relative to peers and history
3. Growth trajectory
4. Macro environment impact

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
