# Archon - Glass-Box Trading Intelligence Platform

A multi-agent AI trading intelligence system built on OpenBB that provides transparent, explainable analysis.

## Features

- **Glass-Box Reasoning**: See exactly how each AI agent thinks
- **Multi-Agent Analysis**: 4 specialized agents working together
  - **SENTINEL**: Risk Management (with VETO power)
  - **ORACLE**: Fundamentals & Macro Analysis
  - **QUANT**: Technical Analysis
  - **PULSE**: Sentiment & News Analysis
- **Consensus Engine**: Synthesizes multiple perspectives
- **Risk-First Architecture**: SENTINEL can block risky trades

## Installation

```bash
cd archon
pip install -e .
```

## Configuration

Set environment variables or create `.env` file:

```bash
# Required: Choose one LLM provider
ARCHON_LLM_PROVIDER=anthropic  # or "openai"

# API Keys
ARCHON_ANTHROPIC_API_KEY=your_key_here
# or
ARCHON_OPENAI_API_KEY=your_key_here

# Optional: OpenBB PAT for premium data
ARCHON_OPENBB_PAT=your_pat_here
```

## Usage

### CLI

```bash
archon NVDA
```

### Python

```python
import asyncio
from archon.core.engine import ConsensusEngine

async def analyze():
    engine = ConsensusEngine()
    result = await engine.analyze("NVDA")
    print(result.glass_box_summary)

asyncio.run(analyze())
```

## Output Example

```
============================================================
ARCHON ANALYSIS: NVDA
============================================================

ORACLE thinks:
  "Strong fundamentals. Data center revenue up 154% YoY..."
  Stance: BULLISH
  Confidence: 82%
  Key factors: earnings beat, revenue growth, AI demand

QUANT thinks:
  "RSI at 58 - neutral. Price above 50-day SMA..."
  Stance: BULLISH
  Confidence: 71%
  Key factors: uptrend, volume confirmation, support holding

PULSE thinks:
  "Sentiment very bullish. 847 mentions in 24h..."
  Stance: NEUTRAL
  Confidence: 61%
  Key factors: high sentiment, insider selling concern

SENTINEL (Risk) says:
  "APPROVED. Position size: 4.2%"
  "Stop-loss: 8.0%"
  "Risk/Reward: 2.3x"

============================================================
CONSENSUS: BULLISH with 72% confidence
Dissent: PULSE: neutral (61% confidence)
Action: Scale in: 50% now, 50% on confirmation. 4.2% position.
============================================================
```

## Architecture

```
                    ┌─────────────────┐
                    │  ConsensusEngine │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌─────▼────┐         ┌────▼────┐
   │ ORACLE  │         │  QUANT   │         │  PULSE  │
   │(Fundmtl)│         │(Technclr)│         │(Sentmnt)│
   └────┬────┘         └────┬─────┘         └────┬────┘
        │                   │                    │
        └───────────────────┴────────────────────┘
                            │
                    ┌───────▼───────┐
                    │   SENTINEL    │
                    │ (Risk - VETO) │
                    └───────────────┘
                            │
                    ┌───────▼───────┐
                    │   OpenBB      │
                    │ (Data Layer)  │
                    └───────────────┘
```

## License

MIT
