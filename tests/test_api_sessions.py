from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_session_management():
    # 发个消息生成记录
    client.post("/chat", json={"session_id": "test_mgr", "message": "测试"})
    
    # 查列表
    res_list = client.get("/sessions")
    assert "test_mgr" in res_list.json()["sessions"]
    
    # 查记录
    res_msg = client.get("/sessions/test_mgr/messages")
    assert len(res_msg.json()["messages"]) > 0
    
    # 删记录
    client.delete("/sessions/test_mgr")
    
    # 删完再查应该是 404
    res_after_delete = client.get("/sessions/test_mgr/messages")
    assert res_after_delete.status_code == 404

def test_not_found():
    # 查一个不存在的会话，返回404
    res = client.get("/sessions/never_exist/messages")
    assert res.status_code == 404