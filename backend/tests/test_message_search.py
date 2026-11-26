"""历史消息关键词查询 + 一轮对话事务回滚测试（临时库隔离，见 conftest.py）。"""

import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app


def test_keyword_search_filters(temp_db):
    storage.add_exchange("s1", "今天学了 SQLAlchemy", "不错，继续加油")
    storage.add_exchange("s1", "明天去图书馆", "记得带伞")

    all_msgs = storage.get_history("s1")
    assert len(all_msgs) == 4

    hit = storage.get_history("s1", keyword="SQLAlchemy")
    assert [m["content"] for m in hit] == ["今天学了 SQLAlchemy"]

    # 搜不到就返回空列表，不报错
    assert storage.get_history("s1", keyword="这个词不存在") == []
    # 不传 keyword 时与旧行为一致：返回全部
    assert storage.get_history("s1") == all_msgs


def test_keyword_api(temp_db):
    storage.add_message("kw", "user", "我喜欢苹果")
    storage.add_message("kw", "assistant", "香蕉也不错")
    client = TestClient(app)

    res = client.get("/sessions/kw/messages", params={"keyword": "苹果"})
    assert res.status_code == 200
    assert [m["content"] for m in res.json()["messages"]] == ["我喜欢苹果"]

    res_miss = client.get("/sessions/kw/messages", params={"keyword": "西瓜"})
    assert res_miss.status_code == 200
    assert res_miss.json()["messages"] == []

    # 不带 keyword 时返回全部两条
    res_all = client.get("/sessions/kw/messages")
    assert len(res_all.json()["messages"]) == 2

    # 会话不存在仍然是 404
    assert client.get("/sessions/nope/messages", params={"keyword": "苹果"}).status_code == 404


def test_add_exchange_rolls_back_on_failure(temp_db, monkeypatch):
    """模拟写入助手回复时报错：整轮对话回滚，不会只留下用户那半句。"""
    real_insert = storage._insert_message
    state = {"calls": 0}

    def flaky_insert(db, session_id, role, content):
        state["calls"] += 1
        if state["calls"] == 2:
            raise RuntimeError("模拟写入失败")
        return real_insert(db, session_id, role, content)

    monkeypatch.setattr(storage, "_insert_message", flaky_insert)

    with pytest.raises(RuntimeError):
        storage.add_exchange("rollback", "你好", "你好呀")

    assert state["calls"] == 2
    assert storage.get_history("rollback") == []
    assert "rollback" not in storage.get_all_sessions()
