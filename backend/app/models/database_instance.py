"""
DatabaseInstance model — a monitored database running on a server.

Tracks the database type, version, environment, and health status.
Each instance belongs to one server and can have many backup jobs.
"""
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DatabaseInstance(Base):
    __tablename__ = "database_instances"
    __table_args__ = (
        Index("ix_db_instances_status", "status"),
        Index("ix_db_instances_environment", "environment"),
        Index("ix_db_instances_type", "db_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    db_type: Mapped[str] = mapped_column(String(50), nullable=False)   # oracle, sqlserver, mysql, postgresql
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    port: Mapped[int] = mapped_column(default=5432)

    # Foreign keys
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id"), nullable=False)
    assigned_admin_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Classification
    environment: Mapped[str] = mapped_column(String(20), nullable=False)  # production, testing, development
    status: Mapped[str] = mapped_column(String(20), default="online")     # online, offline, degraded

    # Storage
    storage_used_gb: Mapped[float] = mapped_column(Float, default=0.0)
    storage_total_gb: Mapped[float] = mapped_column(Float, default=100.0)

    # Health
    last_health_check: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    availability_percent: Mapped[float] = mapped_column(Float, default=100.0)

    # Metadata
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    server: Mapped["Server"] = relationship(back_populates="database_instances")
    assigned_admin: Mapped["User | None"] = relationship(foreign_keys=[assigned_admin_id])
    backup_jobs: Mapped[list["BackupJob"]] = relationship(back_populates="database_instance")
    incidents: Mapped[list["Incident"]] = relationship(back_populates="database_instance")
    monitoring_metrics: Mapped[list["MonitoringMetric"]] = relationship(back_populates="database_instance")
