from __future__ import annotations
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ArchonConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ARCHON_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: Literal["anthropic", "openai"] = "anthropic"
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None

    anthropic_model: str = "claude-sonnet-4-20250514"
    openai_model: str = "gpt-4o"

    max_tokens: int = 4096
    temperature: float = 0.3

    openbb_pat: str | None = Field(default=None, description="OpenBB Personal Access Token")

    sentinel_strict_mode: bool = True
    default_position_size_pct: float = 5.0
    max_position_size_pct: float = 10.0

    enable_real_time_data: bool = False
    cache_ttl_seconds: int = 300

    log_level: str = "INFO"
    log_reasoning_chains: bool = True


def get_config() -> ArchonConfig:
    return ArchonConfig()
