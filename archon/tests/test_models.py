from datetime import datetime

import pytest

from archon.core.models import (
    AgentThought,
    AgentType,
    AnalysisResult,
    Consensus,
    RiskAssessment,
    RiskLevel,
    Stance,
)


class TestAgentThought:
    def test_creation(self):
        thought = AgentThought(
            agent_type=AgentType.ORACLE,
            symbol="NVDA",
            stance=Stance.BULLISH,
            confidence=75.5,
            reasoning="Strong fundamentals",
            key_factors=["earnings beat", "revenue growth"],
            data_sources=["fundamentals", "earnings"],
        )

        assert thought.agent_type == AgentType.ORACLE
        assert thought.symbol == "NVDA"
        assert thought.stance == Stance.BULLISH
        assert thought.confidence == 75.5
        assert len(thought.key_factors) == 2

    def test_confidence_validation(self):
        with pytest.raises(ValueError):
            AgentThought(
                agent_type=AgentType.QUANT,
                symbol="AAPL",
                stance=Stance.NEUTRAL,
                confidence=150,
                reasoning="Invalid",
                key_factors=[],
                data_sources=[],
            )


class TestRiskAssessment:
    def test_approved_assessment(self):
        risk = RiskAssessment(
            approved=True,
            risk_level=RiskLevel.MEDIUM,
            position_size_pct=5.0,
            stop_loss_pct=8.0,
            risk_reward_ratio=2.5,
        )

        assert risk.approved
        assert risk.veto_reason is None
        assert risk.position_size_pct == 5.0

    def test_vetoed_assessment(self):
        risk = RiskAssessment(
            approved=False,
            veto_reason="Extreme volatility detected",
            risk_level=RiskLevel.EXTREME,
            position_size_pct=0,
        )

        assert not risk.approved
        assert risk.veto_reason == "Extreme volatility detected"


class TestConsensus:
    def test_bullish_consensus(self):
        thoughts = [
            AgentThought(
                agent_type=AgentType.ORACLE,
                symbol="NVDA",
                stance=Stance.BULLISH,
                confidence=80,
                reasoning="Good",
                key_factors=["growth"],
                data_sources=["fundamentals"],
            ),
        ]

        risk = RiskAssessment(
            approved=True,
            risk_level=RiskLevel.LOW,
            position_size_pct=5.0,
        )

        consensus = Consensus(
            symbol="NVDA",
            overall_stance=Stance.BULLISH,
            overall_confidence=80,
            agent_thoughts=thoughts,
            risk_assessment=risk,
            suggested_action="BUY",
        )

        assert consensus.overall_stance == Stance.BULLISH
        assert len(consensus.agent_thoughts) == 1


class TestStanceEnum:
    def test_stance_values(self):
        assert Stance.BULLISH.value == "bullish"
        assert Stance.BEARISH.value == "bearish"
        assert Stance.NEUTRAL.value == "neutral"


class TestAgentTypeEnum:
    def test_agent_types(self):
        assert AgentType.SENTINEL.value == "sentinel"
        assert AgentType.ORACLE.value == "oracle"
        assert AgentType.QUANT.value == "quant"
        assert AgentType.PULSE.value == "pulse"
