"""
IncidentHistory model — audit trail for incident status changes.

Every time an incident's status, severity, or assignment changes,
a new history entry is created.
"""
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IncidentHistory(Base):
    __tablename__ = "incident_history"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign keys
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), nullable=False)
    changed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Change details
    field_changed: Mapped[str] = mapped_column(String(50), nullable=False)  # status, severity, assigned_to, etc.
    old_value: Mapped[str] = mapped_column(Text, default="")
    new_value: Mapped[str] = mapped_column(Text, default="")
    comment: Mapped[str] = mapped_column(Text, default="")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    incident: Mapped["Incident"] = relationship(back_populates="history")
    changed_by: Mapped["User | None"] = relationship()
