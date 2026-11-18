from typing import List

from sqlalchemy import select

from app.database import get_session
from app.models import MessageModel, SessionModel


def _ensure_session(db, session_id: str) -> SessionModel:
    """会话不存在就创建（对应旧代码的 INSERT OR IGNORE INTO sessions）。"""
    session_obj = db.get(SessionModel, session_id)
    if session_obj is None:
        session_obj = SessionModel(session_id=session_id)
        db.add(session_obj)
        db.flush()
    return session_obj


def _insert_message(db, session_id: str, role: str, content: str) -> MessageModel:
    message = MessageModel(session_id=session_id, role=role, content=content)
    db.add(message)
    db.flush()
    return message


def add_message(session_id: str, role: str, content: str) -> None:
    """写入单条消息。"""
    with get_session() as db:
        try:
            _ensure_session(db, session_id)
            _insert_message(db, session_id, role, content)
            db.commit()
        except Exception:
            db.rollback()
            raise


def add_exchange(session_id: str, user_message: str, assistant_reply: str) -> None:
    """在一次事务中同时写入用户消息与助手回复。

    两条要么都成功，要么都回滚，绝不会只留下半轮对话。
    """
    with get_session() as db:
        try:
            _ensure_session(db, session_id)
            _insert_message(db, session_id, "user", user_message)
            _insert_message(db, session_id, "assistant", assistant_reply)
            db.commit()
        except Exception:
            db.rollback()
            raise


def get_history(session_id: str) -> List[dict]:
    """按 id 升序返回某个会话的全部消息。"""
    with get_session() as db:
        stmt = (
            select(MessageModel)
            .where(MessageModel.session_id == session_id)
            .order_by(MessageModel.id.asc())
        )
        rows = db.scalars(stmt).all()
        return [{"role": row.role, "content": row.content} for row in rows]


def get_all_sessions() -> List[str]:
    """返回所有会话 ID。"""
    with get_session() as db:
        return list(db.scalars(select(SessionModel.session_id)).all())


def clear_history(session_id: str) -> None:
    """删除会话，其消息由 relationship 的 delete-orphan 级联删除。"""
    with get_session() as db:
        try:
            session_obj = db.get(SessionModel, session_id)
            if session_obj is not None:
                db.delete(session_obj)
            db.commit()
        except Exception:
            db.rollback()
            raise
