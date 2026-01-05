from __future__ import annotations
import asyncio
import time
from datetime import datetime

from archon.agents.oracle import OracleAgent
from archon.agents.pulse import PulseAgent
from archon.agents.quant import QuantAgent
from archon.agents.sentinel import SentinelAgent
from archon.core.config import ArchonConfig
from archon.core.models import (
    AgentThought,
    AnalysisResult,
    Consensus,
    RiskAssessment,
    RiskLevel,
    Stance,
)


class ConsensusEngine:
    def __init__(self, config: ArchonConfig | None = None):
        self.config = config or ArchonConfig()
        self.sentinel = SentinelAgent(self.config)
        self.oracle = OracleAgent(self.config)
        self.quant = QuantAgent(self.config)
        self.pulse = PulseAgent(self.config)

    async def analyze(self, symbol: str) -> AnalysisResult:
        start_time = time.time()

        thoughts = await asyncio.gather(
            self.oracle.analyze(symbol),
            self.quant.analyze(symbol),
            self.pulse.analyze(symbol),
            self.sentinel.analyze(symbol),
        )

        oracle_thought, quant_thought, pulse_thought, sentinel_thought = thoughts

        risk_assessment = self.sentinel.extract_risk_assessment(sentinel_thought)
        analysis_thoughts = [oracle_thought, quant_thought, pulse_thought]

        consensus = self._build_consensus(
            symbol=symbol,
            thoughts=analysis_thoughts,
            risk_assessment=risk_assessment,
        )

        glass_box = self._format_glass_box(consensus)
        providers = self._collect_providers(thoughts)

        return AnalysisResult(
            symbol=symbol,
            consensus=consensus,
            glass_box_summary=glass_box,
            execution_time_seconds=round(time.time() - start_time, 2),
            providers_used=providers,
        )

    def _build_consensus(
        self,
        symbol: str,
        thoughts: list[AgentThought],
        risk_assessment: RiskAssessment,
    ) -> Consensus:
        if not risk_assessment.approved:
            return Consensus(
                symbol=symbol,
                overall_stance=Stance.BEARISH,
                overall_confidence=risk_assessment.warnings and 40 or 50,
                agent_thoughts=thoughts,
                risk_assessment=risk_assessment,
                dissenting_opinions=[f"SENTINEL VETO: {risk_assessment.veto_reason}"],
                suggested_action="DO NOT TRADE - Risk assessment failed",
                timestamp=datetime.utcnow(),
            )

        stance_scores = {"bullish": 0, "bearish": 0, "neutral": 0}
        total_confidence = 0.0

        for thought in thoughts:
            weight = thought.confidence / 100
            stance_scores[thought.stance.value] += weight
            total_confidence += thought.confidence

        avg_confidence = total_confidence / len(thoughts) if thoughts else 50
        winning_stance = max(stance_scores, key=lambda k: stance_scores[k])

        dissenting = []
        for thought in thoughts:
            if thought.stance.value != winning_stance:
                dissenting.append(
                    f"{thought.agent_type.value.upper()}: {thought.stance.value} "
                    f"({thought.confidence:.0f}% confidence)"
                )

        action = self._determine_action(
            Stance(winning_stance),
            avg_confidence,
            risk_assessment,
        )

        return Consensus(
            symbol=symbol,
            overall_stance=Stance(winning_stance),
            overall_confidence=round(avg_confidence, 1),
            agent_thoughts=thoughts,
            risk_assessment=risk_assessment,
            dissenting_opinions=dissenting,
            suggested_action=action,
            timestamp=datetime.utcnow(),
        )

    def _determine_action(
        self,
        stance: Stance,
        confidence: float,
        risk: RiskAssessment,
    ) -> str:
        if risk.risk_level == RiskLevel.EXTREME:
            return "WAIT - Extreme risk conditions"

        position = f"{risk.position_size_pct:.1f}% position"
        stop = f"Stop-loss: {risk.stop_loss_pct:.1f}%" if risk.stop_loss_pct else ""

        if stance == Stance.BULLISH:
            if confidence >= 75:
                return f"BUY with {position}. {stop}"
            elif confidence >= 60:
                return f"Scale in: 50% now, 50% on confirmation. {position}. {stop}"
            else:
                return f"WATCH - Bullish but low confidence ({confidence:.0f}%)"

        elif stance == Stance.BEARISH:
            if confidence >= 75:
                return f"SHORT or EXIT existing position. {stop}"
            elif confidence >= 60:
                return f"Reduce exposure. Consider hedging."
            else:
                return f"WATCH - Bearish but low confidence ({confidence:.0f}%)"

        return "HOLD - No clear directional signal"

    def _format_glass_box(self, consensus: Consensus) -> str:
        lines = [
            f"{'=' * 60}",
            f"ARCHON ANALYSIS: {consensus.symbol}",
            f"{'=' * 60}",
            "",
        ]

        stance_emoji = {
            "bullish": "BULLISH",
            "bearish": "BEARISH",
            "neutral": "NEUTRAL",
        }

        for thought in consensus.agent_thoughts:
            agent_name = thought.agent_type.value.upper()
            lines.append(f"{agent_name} thinks:")
            lines.append(f'  "{thought.reasoning[:200]}..."')
            lines.append(f"  Stance: {stance_emoji[thought.stance.value]}")
            lines.append(f"  Confidence: {thought.confidence:.0f}%")
            lines.append(f"  Key factors: {', '.join(thought.key_factors[:3])}")
            lines.append("")

        risk = consensus.risk_assessment
        lines.append("SENTINEL (Risk) says:")
        if risk.approved:
            lines.append(f'  "APPROVED. Position size: {risk.position_size_pct:.1f}%"')
            if risk.stop_loss_pct:
                lines.append(f'  "Stop-loss: {risk.stop_loss_pct:.1f}%"')
            if risk.risk_reward_ratio:
                lines.append(f'  "Risk/Reward: {risk.risk_reward_ratio:.1f}x"')
        else:
            lines.append(f'  "VETO: {risk.veto_reason}"')
        lines.append("")

        lines.append(f"{'=' * 60}")
        lines.append(
            f"CONSENSUS: {stance_emoji[consensus.overall_stance.value]} "
            f"with {consensus.overall_confidence:.0f}% confidence"
        )

        if consensus.dissenting_opinions:
            lines.append(f"Dissent: {'; '.join(consensus.dissenting_opinions)}")

        lines.append(f"Action: {consensus.suggested_action}")
        lines.append(f"{'=' * 60}")

        return "\n".join(lines)

    def _collect_providers(self, thoughts: list[AgentThought]) -> list[str]:
        providers = set()
        for thought in thoughts:
            providers.update(thought.data_sources)
        return sorted(providers)
