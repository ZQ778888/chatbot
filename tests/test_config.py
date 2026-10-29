import pytest
from pydantic import ValidationError

from config import get_settings


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_defaults(monkeypatch):
    monkeypatch.setenv("CHATBOT_API_KEY", "sk-test")
    monkeypatch.delenv("CHATBOT_MODEL", raising=False)
    settings = get_settings()
    assert settings.model == "deepseek-chat"
    assert settings.temperature == 1.0


def test_temperature_out_of_range(monkeypatch):
    monkeypatch.setenv("CHATBOT_API_KEY", "sk-test")
    monkeypatch.setenv("CHATBOT_TEMPERATURE", "5")
    with pytest.raises(ValidationError):
        get_settings()


def test_secret_not_leaked(monkeypatch):
    monkeypatch.setenv("CHATBOT_API_KEY", "sk-very-secret")
    settings = get_settings()
    assert "sk-very-secret" not in repr(settings)
    assert "sk-very-secret" not in str(settings)