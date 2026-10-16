"""
BackupVerification model — post-backup integrity verification.

After a backup completes, a verification job checks that the backup
file is readable, has the expected checksum, and passes basic
integrity checks.
"""
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BackupVerification(Base):
    __tablename__ = "backup_verifications"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign keys
    backup_run_id: Mapped[int] = mapped_column(ForeignKey("backup_runs.id"), nullable=False)

    # Verification details
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success, failed, in_progress
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)

    # Results
    checksum_expected: Mapped[str] = mapped_column(String(128), default="")
    checksum_actual: Mapped[str] = mapped_column(String(128), default="")
    integrity_check: Mapped[str] = mapped_column(String(20), default="pending")  # passed, failed, pending
    error_message: Mapped[str] = mapped_column(Text, default="")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    backup_run: Mapped["BackupRun"] = relationship(back_populates="verification")
