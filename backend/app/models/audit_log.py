"""
AuditLog model — global security and operational audit trail.

Records important actions: login attempts, user changes, database
modifications, backup operations, permission changes, etc.
"""
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_created_at", "created_at"),
        Index("ix_audit_logs_resource_type", "resource_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Who
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    username: Mapped[str] = mapped_column(String(80), default="system")  # denormalized for display

    # What
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)  # user, database, backup, etc.
    resource_id: Mapped[str] = mapped_column(String(50), default="")

    # Details
    description: Mapped[str] = mapped_column(Text, default="")
    ip_address: Mapped[str] = mapped_column(String(45), default="")
    user_agent: Mapped[str] = mapped_column(String(255), default="")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user: Mapped["User | None"] = relationship(back_populates="audit_logs")
