from __future__ import annotations
import json
from abc import ABC, abstractmethod
from typing import Any

import httpx

from archon.core.config import ArchonConfig


class BaseLLMClient(ABC):
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: type | None = None,
    ) -> str:
        pass


class AnthropicClient(BaseLLMClient):
    def __init__(self, config: ArchonConfig):
        self.api_key = config.anthropic_api_key
        self.model = config.anthropic_model
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature

        if not self.api_key:
            raise ValueError("ARCHON_ANTHROPIC_API_KEY not set")

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: type | None = None,
    ) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]


class OpenAIClient(BaseLLMClient):
    def __init__(self, config: ArchonConfig):
        self.api_key = config.openai_api_key
        self.model = config.openai_model
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature

        if not self.api_key:
            raise ValueError("ARCHON_OPENAI_API_KEY not set")

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: type | None = None,
    ) -> str:
        body: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        if response_format:
            body["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class LLMClient:
    def __init__(self, config: ArchonConfig | None = None):
        self.config = config or ArchonConfig()

        if self.config.llm_provider == "anthropic":
            self._client = AnthropicClient(self.config)
        else:
            self._client = OpenAIClient(self.config)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: type | None = None,
    ) -> str:
        return await self._client.generate(system_prompt, user_prompt, response_format)

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        response = await self.generate(
            system_prompt + "\n\nRespond ONLY with valid JSON.",
            user_prompt,
        )
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(clean)
