"""
BackupRun model — a single execution of a backup job.

Records start/end times, size, status, and any error message.
A successful run may have associated verification and restore-test records.
"""
from datetime import datetime
from sqlalchemy import String, Float, BigInteger, DateTime, ForeignKey, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BackupRun(Base):
    __tablename__ = "backup_runs"
    __table_args__ = (
        Index("ix_backup_runs_job_id", "backup_job_id"),
        Index("ix_backup_runs_status", "status"),
        Index("ix_backup_runs_started_at", "started_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign keys
    backup_job_id: Mapped[int] = mapped_column(ForeignKey("backup_jobs.id"), nullable=False)

    # Execution details
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success, failed, running, cancelled
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Size and duration
    size_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    duration_seconds: Mapped[int] = mapped_column(BigInteger, default=0)

    # Error info (populated on failure)
    error_message: Mapped[str] = mapped_column(Text, default="")

    # Verification flag
    verified: Mapped[bool] = mapped_column(default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    backup_job: Mapped["BackupJob"] = relationship(back_populates="backup_runs")
    verification: Mapped["BackupVerification | None"] = relationship(back_populates="backup_run")
    restore_tests: Mapped[list["RestoreTest"]] = relationship(back_populates="backup_run")
