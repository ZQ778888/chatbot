from typing import List, Optional

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SessionModel(Base):
    """对应旧的 sessions 表：一个会话只有 session_id 一个字段。"""

    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(Text, primary_key=True)
    # 一对多：一个会话包含多条消息
    messages: Mapped[List["MessageModel"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="MessageModel.id",
    )


class MessageModel(Base):
    """对应旧的 messages 表，字段名与既有数据库保持一致。"""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=True
    )
    role: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 多对一：每条消息属于一个会话
    session: Mapped["SessionModel"] = relationship(back_populates="messages")
