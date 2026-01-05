#!/usr/bin/env python3
import asyncio
import os

os.environ.setdefault("ARCHON_LLM_PROVIDER", "anthropic")


async def main():
    from archon.core.engine import ConsensusEngine
    from archon.core.config import ArchonConfig

    config = ArchonConfig()
    engine = ConsensusEngine(config)

    symbols = ["NVDA", "AAPL", "TSLA"]

    for symbol in symbols:
        print(f"\n{'=' * 60}")
        print(f"Analyzing {symbol}...")
        print("=" * 60)

        result = await engine.analyze(symbol)

        print(result.glass_box_summary)
        print(f"\nExecution time: {result.execution_time_seconds}s")
        print(f"Data sources: {', '.join(result.providers_used)}")


if __name__ == "__main__":
    asyncio.run(main())
