import pytest

from app import database


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """把数据库指向临时文件：用例之间互不影响，也不会碰真实 chat.db。"""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("CHATBOT_DB_URL", "sqlite:///" + db_file.as_posix())
    database.init_db()
    yield db_file
    database.dispose_engine()
