from fastapi.testclient import TestClient
from app import app
import storage

client = TestClient(app)

def test_stream_output_and_save():
    # 调用流式接口
    res = client.post("/chat/stream", json={"session_id": "stream_test", "message": "你好"})
    assert res.status_code == 200
    
    # 确认返回了流式文本
    assert "流式" in res.text
    
    # 确认流式回复结束后，历史记录里真的有保存
    history = storage.get_history("stream_test")
    assert any(msg["role"] == "assistant" for msg in history)