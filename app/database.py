import os
from typing import Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DB_PATH = "chat.db"


def database_url() -> str:
    """当前使用的数据库地址；测试时可用 CHATBOT_DB_URL 指向临时库。"""
    return os.environ.get("CHATBOT_DB_URL", f"sqlite:///{DB_PATH}")


class Base(DeclarativeBase):
    """所有 ORM 模型的公共基类（SQLAlchemy 2.x 声明式写法）。"""


_engine: Optional[Engine] = None
_engine_url: Optional[str] = None


def _create_engine(url: str) -> Engine:
    engine = create_engine(
        url,
        future=True,
        # SQLite 连接会被连接池跨线程复用，必须关掉同线程检查
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        # SQLite 默认不开启外键约束，不开启则 ON DELETE CASCADE 不生效
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()

    return engine


def get_engine() -> Engine:
    """返回当前数据库对应的 Engine；地址变化时（如切到临时库）自动重建。"""
    global _engine, _engine_url

    url = database_url()
    if _engine is not None and _engine_url == url:
        return _engine
    if _engine is not None:
        _engine.dispose()
    _engine = _create_engine(url)
    _engine_url = url
    return _engine


def get_session() -> Session:
    """新建一个 ORM Session（调用方负责 commit / rollback / close）。"""
    factory = sessionmaker(bind=get_engine(), expire_on_commit=False, future=True)
    return factory()


def init_db() -> None:
    # 导入模型，把表结构注册到 Base.metadata
    from app import models  # noqa: F401

    Base.metadata.create_all(get_engine())


def dispose_engine() -> None:
    global _engine, _engine_url
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _engine_url = None
