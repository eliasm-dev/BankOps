"""
BackupJob model — a configured backup schedule for a database.

Each job defines the backup type, schedule (cron-like), and retention.
Actual execution records are stored in backup_runs.
"""
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BackupJob(Base):
    __tablename__ = "backup_jobs"
    __table_args__ = (
        Index("ix_backup_jobs_db_instance", "database_instance_id"),
        Index("ix_backup_jobs_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    # Foreign keys
    database_instance_id: Mapped[int] = mapped_column(ForeignKey("database_instances.id"), nullable=False)

    # Configuration
    backup_type: Mapped[str] = mapped_column(String(20), nullable=False)  # full, incremental, differential
    schedule: Mapped[str] = mapped_column(String(100), nullable=False)    # cron expression or description
    retention_days: Mapped[int] = mapped_column(Integer, default=30)
    destination: Mapped[str] = mapped_column(String(255), default="s3://bankops-backups/")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    database_instance: Mapped["DatabaseInstance"] = relationship(back_populates="backup_jobs")
    backup_runs: Mapped[list["BackupRun"]] = relationship(back_populates="backup_job")
