"""Tests for Settings: SKILLS_PROFILES_* env vars over .env over built-in defaults."""

import os

import pytest

from skills_profiles.config import Settings

_ENV_VARS = [name for name in os.environ if name.startswith("SKILLS_PROFILES_")]


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Keep developer shell environment out of configuration assertions."""
    for name in _ENV_VARS:
        monkeypatch.delenv(name)


def test_built_in_defaults(tmp_path, monkeypatch):
    # chdir away so a developer-local .env cannot satisfy the defaults
    monkeypatch.chdir(tmp_path)
    settings = Settings(_env_file=None)
    assert settings.model == "gpt-4.1-mini"
    assert settings.base_url is None
    assert settings.api_key is None
    assert settings.limit == 10
    assert settings.concurrency == 2
    # Agnes documents 20 RPM for its chat and image models alike
    assert settings.llm_rate_limit == 20
    assert settings.image_rate_limit == 20


def test_env_var_overrides_dotenv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("SKILLS_PROFILES_MODEL=env-model\n", encoding="utf-8")
    monkeypatch.setenv("SKILLS_PROFILES_MODEL", "cli-model")
    assert Settings().model == "cli-model"


def test_dotenv_fills_unset_fields(tmp_path, monkeypatch):
    """A local .env provides fields the environment leaves unset."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "SKILLS_PROFILES_MODEL=env-model\n"
        "SKILLS_PROFILES_BASE_URL=https://example.com/v1\n"
        "SKILLS_PROFILES_API_KEY=sk-test\n",
        encoding="utf-8",
    )
    settings = Settings()
    assert settings.model == "env-model"
    assert settings.base_url == "https://example.com/v1"
    assert settings.api_key == "sk-test"


def test_rejects_invalid_concurrency(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="concurrency"):
        Settings(concurrency=0, _env_file=None)
    with pytest.raises(ValueError, match="concurrency"):
        Settings(concurrency=-1, _env_file=None)


def test_rejects_negative_max_retries(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="max_retries"):
        Settings(max_retries=-1, _env_file=None)


def test_rejects_negative_rate_limits(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="llm_rate_limit"):
        Settings(llm_rate_limit=-1, _env_file=None)
    with pytest.raises(ValueError, match="image_rate_limit"):
        Settings(image_rate_limit=-1, _env_file=None)
