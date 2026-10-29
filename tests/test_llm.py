from unittest.mock import MagicMock

import pytest

from config import get_settings
from llm import chat_once


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_model_parameters(monkeypatch):
    monkeypatch.setenv("CHATBOT_API_KEY", "sk-test")
    monkeypatch.setenv("CHATBOT_MODEL", "test-model")
    monkeypatch.setenv("CHATBOT_TEMPERATURE", "0.3")

    # 伪造一个客户端和它的返回值
    fake_response = MagicMock()
    fake_response.choices[0].message.content = "Hello"
    
    mock_create = MagicMock(return_value=fake_response)
    client = MagicMock()
    client.chat.completions.create = mock_create

    messages = [{"role": "user", "content": "Hi"}]
    result = chat_once(client, messages)

    # 检查返回的内容
    assert result == "Hello"
    
    # 检查传给模型的参数对不对
    _, kwargs = mock_create.call_args
    assert kwargs["model"] == "test-model"
    assert kwargs["temperature"] == 0.3
    assert kwargs["messages"] == messages
    assert kwargs["stream"] is False