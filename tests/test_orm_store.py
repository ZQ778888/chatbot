"""ORM 存储层测试：每个用例都跑在临时 SQLite 文件上，与真实 chat.db 完全隔离。"""

import sqlite3

import pytest

from app import database, storage


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("CHATBOT_DB_URL", "sqlite:///" + db_file.as_posix())
    database.init_db()
    yield db_file
    database.dispose_engine()


def test_persist_after_reconnect(temp_db):
    """数据持久化：写入后重建 Engine / 新连接，数据依然读得到。"""
    storage.add_exchange("s1", "你好", "你好呀，有什么可以帮你？")
    assert [m["content"] for m in storage.get_history("s1")] == ["你好", "你好呀，有什么可以帮你？"]

    # 丢掉所有连接与 Engine，相当于重新连一次数据库
    database.dispose_engine()
    database.init_db()

    history = storage.get_history("s1")
    assert [m["role"] for m in history] == ["user", "assistant"]
    assert [m["content"] for m in history] == ["你好", "你好呀，有什么可以帮你？"]
    assert storage.get_all_sessions() == ["s1"]


def test_reads_legacy_sqlite_data(temp_db):
    """兼容性：旧版原生 sqlite3 写进去的数据，ORM 能直接读。"""
    conn = sqlite3.connect(str(temp_db))
    conn.execute("INSERT INTO sessions (session_id) VALUES ('legacy')")
    conn.execute(
        "INSERT INTO messages (session_id, role, content) VALUES ('legacy', 'user', '老数据')"
    )
    conn.commit()
    conn.close()

    assert storage.get_history("legacy") == [{"role": "user", "content": "老数据"}]
    assert "legacy" in storage.get_all_sessions()


def test_table_and_column_names_unchanged(temp_db):
    """ORM 建出来的表结构与旧库一致，表名 / 字段名完全不变。"""
    conn = sqlite3.connect(str(temp_db))
    tables = sorted(r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"))
    assert tables == ["messages", "sessions"]
    session_cols = [r[1] for r in conn.execute("PRAGMA table_info(sessions)")]
    message_cols = [r[1] for r in conn.execute("PRAGMA table_info(messages)")]
    conn.close()

    assert session_cols == ["session_id"]
    assert message_cols == ["id", "session_id", "role", "content"]
