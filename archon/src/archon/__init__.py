"""
Archon - Glass-Box Trading Intelligence Platform

A multi-agent AI trading intelligence system built on OpenBB that provides
transparent, explainable analysis with specialized agents.

Agents:
- SENTINEL: Risk Management (with VETO power)
- ORACLE: Fundamentals & Macro Analysis
- QUANT: Technical Analysis
- PULSE: Sentiment & News Analysis
"""

__version__ = "0.1.0"
__author__ = "Archon Team"

from archon.core.models import AgentThought, AnalysisResult, Consensus
from archon.core.config import ArchonConfig

__all__ = [
    "AgentThought",
    "AnalysisResult",
    "Consensus",
    "ArchonConfig",
    "__version__",
]
