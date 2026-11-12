import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_continuous_chat():
    # 同一个会话连续对话
    res1 = client.post("/chat", json={"session_id": "test1", "message": "你好"})
    assert res1.status_code == 200
    res2 = client.post("/chat", json={"session_id": "test1", "message": "第二句"})
    assert res2.status_code == 200

def test_different_sessions():
    # 不同会话不串话
    client.post("/chat", json={"session_id": "A", "message": "我是A"})
    client.post("/chat", json={"session_id": "B", "message": "我是B"})
    
    res_a = client.get("/sessions/A/messages")
    assert "我是A" in str(res_a.json())
    assert "我是B" not in str(res_a.json())

def test_empty_message():
    # 空消息被拒绝 (400错误)
    res = client.post("/chat", json={"session_id": "u1", "message": "  "})
    assert res.status_code == 400

def test_study_feature():
    # 学习功能可用
    res = client.post("/study/correct", json={"text": "I is a student."})
    assert res.status_code == 200
    assert "语法解析" in res.json()["correction"]