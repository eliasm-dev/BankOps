"""
Incident model — tracks operational incidents affecting databases or servers.

Incidents have a lifecycle: open -> investigating -> resolved -> closed.
All status changes are recorded in incident_history.
"""
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        Index("ix_incidents_status", "status"),
        Index("ix_incidents_severity", "severity"),
        Index("ix_incidents_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")

    # Classification
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # critical, high, medium, low
    status: Mapped[str] = mapped_column(String(20), default="open")   # open, investigating, resolved, closed

    # Affected resource (one of these should be set)
    database_instance_id: Mapped[int | None] = mapped_column(
        ForeignKey("database_instances.id"), nullable=True
    )
    server_id: Mapped[int | None] = mapped_column(ForeignKey("servers.id"), nullable=True)

    # Assignment
    assigned_to_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reported_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    database_instance: Mapped["DatabaseInstance | None"] = relationship(
        back_populates="incidents", foreign_keys=[database_instance_id]
    )
    server: Mapped["Server | None"] = relationship(foreign_keys=[server_id])
    assigned_to: Mapped["User | None"] = relationship(foreign_keys=[assigned_to_id])
    reported_by: Mapped["User | None"] = relationship(foreign_keys=[reported_by_id])
    history: Mapped[list["IncidentHistory"]] = relationship(back_populates="incident")
