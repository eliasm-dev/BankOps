"""
RestoreTest model — scheduled restore tests for backups.

Periodically, backups are restored to a sandbox environment to
confirm they are usable in a disaster-recovery scenario.
"""
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RestoreTest(Base):
    __tablename__ = "restore_tests"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign keys
    backup_run_id: Mapped[int] = mapped_column(ForeignKey("backup_runs.id"), nullable=False)

    # Test details
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success, failed, in_progress
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)

    # Results
    data_integrity_check: Mapped[str] = mapped_column(String(20), default="pending")  # passed, failed, pending
    rows_validated: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    backup_run: Mapped["BackupRun"] = relationship(back_populates="restore_tests")
