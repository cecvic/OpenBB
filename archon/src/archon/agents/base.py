from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

from archon.core.config import ArchonConfig
from archon.core.llm import LLMClient
from archon.core.models import AgentThought, AgentType


class BaseAgent(ABC):
    agent_type: AgentType
    system_prompt: str

    def __init__(self, config: ArchonConfig | None = None):
        self.config = config or ArchonConfig()
        self.llm = LLMClient(self.config)
        self._obb = None

    @property
    def obb(self):
        if self._obb is None:
            from openbb import obb

            self._obb = obb
        return self._obb

    @abstractmethod
    async def analyze(self, symbol: str) -> AgentThought:
        pass

    @abstractmethod
    def get_data_requirements(self) -> list[str]:
        pass

    async def fetch_data(self, symbol: str) -> dict[str, Any]:
        data = {}
        for requirement in self.get_data_requirements():
            try:
                result = await self._fetch_single(symbol, requirement)
                data[requirement] = result
            except Exception as e:
                data[requirement] = {"error": str(e)}
        return data

    async def _fetch_single(self, symbol: str, data_type: str) -> dict[str, Any]:
        handlers = {
            "price_history": self._fetch_price_history,
            "quote": self._fetch_quote,
            "fundamentals": self._fetch_fundamentals,
            "news": self._fetch_news,
            "technicals": self._fetch_technicals,
            "earnings": self._fetch_earnings,
            "analyst_estimates": self._fetch_analyst_estimates,
            "insider_trading": self._fetch_insider_trading,
            "economic_calendar": self._fetch_economic_calendar,
        }
        handler = handlers.get(data_type)
        if handler:
            return await handler(symbol)
        return {}

    async def _fetch_price_history(self, symbol: str) -> dict[str, Any]:
        result = self.obb.equity.price.historical(symbol=symbol, provider="yfinance")
        return {"records": len(result.results), "data": result.to_dict()[:30]}

    async def _fetch_quote(self, symbol: str) -> dict[str, Any]:
        result = self.obb.equity.price.quote(symbol=symbol, provider="yfinance")
        return result.to_dict() if result.results else {}

    async def _fetch_fundamentals(self, symbol: str) -> dict[str, Any]:
        try:
            income = self.obb.equity.fundamental.income(symbol=symbol, provider="fmp", limit=4)
            balance = self.obb.equity.fundamental.balance(symbol=symbol, provider="fmp", limit=4)
            return {
                "income_statement": income.to_dict()[:4] if income.results else [],
                "balance_sheet": balance.to_dict()[:4] if balance.results else [],
            }
        except Exception:
            return {}

    async def _fetch_news(self, symbol: str) -> dict[str, Any]:
        try:
            result = self.obb.news.company(symbol=symbol, provider="benzinga", limit=10)
            return {"articles": result.to_dict()[:10]} if result.results else {}
        except Exception:
            return {}

    async def _fetch_technicals(self, symbol: str) -> dict[str, Any]:
        try:
            hist = self.obb.equity.price.historical(symbol=symbol, provider="yfinance")
            if not hist.results:
                return {}

            rsi = self.obb.technical.rsi(data=hist.results, length=14)
            macd = self.obb.technical.macd(data=hist.results)
            bbands = self.obb.technical.bbands(data=hist.results, length=20)

            return {
                "rsi": rsi.to_dict()[-1] if rsi.results else {},
                "macd": macd.to_dict()[-1] if macd.results else {},
                "bbands": bbands.to_dict()[-1] if bbands.results else {},
            }
        except Exception:
            return {}

    async def _fetch_earnings(self, symbol: str) -> dict[str, Any]:
        try:
            result = self.obb.equity.estimates.historical(symbol=symbol, provider="fmp")
            return {"estimates": result.to_dict()[:8]} if result.results else {}
        except Exception:
            return {}

    async def _fetch_analyst_estimates(self, symbol: str) -> dict[str, Any]:
        try:
            result = self.obb.equity.estimates.consensus(symbol=symbol, provider="fmp")
            return result.to_dict() if result.results else {}
        except Exception:
            return {}

    async def _fetch_insider_trading(self, symbol: str) -> dict[str, Any]:
        try:
            result = self.obb.equity.ownership.insider_trading(symbol=symbol, provider="fmp")
            return {"trades": result.to_dict()[:20]} if result.results else {}
        except Exception:
            return {}

    async def _fetch_economic_calendar(self, symbol: str) -> dict[str, Any]:
        try:
            result = self.obb.economy.calendar(provider="fmp")
            return {"events": result.to_dict()[:10]} if result.results else {}
        except Exception:
            return {}

    def format_data_for_prompt(self, data: dict[str, Any]) -> str:
        import json

        return json.dumps(data, indent=2, default=str)[:15000]
