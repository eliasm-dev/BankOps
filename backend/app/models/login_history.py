"""
LoginHistory model — records all login attempts (success and failure).

Used for security monitoring, detecting brute-force attacks,
and displaying recent activity to users.
"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LoginHistory(Base):
    __tablename__ = "login_history"
    __table_args__ = (
        Index("ix_login_history_user_id", "user_id"),
        Index("ix_login_history_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign keys
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Attempt details
    username: Mapped[str] = mapped_column(String(80), nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    failure_reason: Mapped[str] = mapped_column(String(255), default="")

    # Context
    ip_address: Mapped[str] = mapped_column(String(45), default="")
    user_agent: Mapped[str] = mapped_column(String(255), default="")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user: Mapped["User | None"] = relationship(back_populates="login_history")
