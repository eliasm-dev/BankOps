"""
Server model — physical or virtual machines hosting databases.

Each server has resource metrics (CPU, memory, disk, network)
that are updated by the monitoring collector (simulated in demo).
"""
from datetime import datetime
from sqlalchemy import String, Float, BigInteger, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Server(Base):
    __tablename__ = "servers"
    __table_args__ = (
        Index("ix_servers_status", "status"),
        Index("ix_servers_environment", "environment"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    hostname: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)  # IPv6 compatible
    operating_system: Mapped[str] = mapped_column(String(120), nullable=False)
    os_version: Mapped[str] = mapped_column(String(80), default="")
    environment: Mapped[str] = mapped_column(String(20), nullable=False)  # production, staging, development
    status: Mapped[str] = mapped_column(String(20), default="online")     # online, offline, maintenance

    # Resource capacity
    cpu_cores: Mapped[int] = mapped_column(default=4)
    memory_gb: Mapped[float] = mapped_column(Float, default=16.0)
    disk_gb: Mapped[float] = mapped_column(Float, default=100.0)

    # Current utilization (updated by monitoring)
    cpu_percent: Mapped[float] = mapped_column(Float, default=0.0)
    memory_percent: Mapped[float] = mapped_column(Float, default=0.0)
    disk_percent: Mapped[float] = mapped_column(Float, default=0.0)
    network_in_mbps: Mapped[float] = mapped_column(Float, default=0.0)
    network_out_mbps: Mapped[float] = mapped_column(Float, default=0.0)

    # Uptime
    uptime_seconds: Mapped[int] = mapped_column(BigInteger, default=0)
    last_boot: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    database_instances: Mapped[list["DatabaseInstance"]] = relationship(back_populates="server")
    monitoring_metrics: Mapped[list["MonitoringMetric"]] = relationship(back_populates="server")
