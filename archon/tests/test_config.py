import os

import pytest

from archon.core.config import ArchonConfig, get_config


class TestArchonConfig:
    def test_default_values(self):
        config = ArchonConfig()

        assert config.llm_provider == "anthropic"
        assert config.anthropic_model == "claude-sonnet-4-20250514"
        assert config.openai_model == "gpt-4o"
        assert config.max_tokens == 4096
        assert config.temperature == 0.3
        assert config.default_position_size_pct == 5.0
        assert config.max_position_size_pct == 10.0

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("ARCHON_LLM_PROVIDER", "openai")
        monkeypatch.setenv("ARCHON_MAX_TOKENS", "8192")
        monkeypatch.setenv("ARCHON_TEMPERATURE", "0.7")

        config = ArchonConfig()

        assert config.llm_provider == "openai"
        assert config.max_tokens == 8192
        assert config.temperature == 0.7

    def test_get_config(self):
        config = get_config()
        assert isinstance(config, ArchonConfig)

    def test_sentinel_strict_mode_default(self):
        config = ArchonConfig()
        assert config.sentinel_strict_mode is True

    def test_cache_ttl(self):
        config = ArchonConfig()
        assert config.cache_ttl_seconds == 300
