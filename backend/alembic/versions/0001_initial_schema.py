"""Initial schema — creates all BankOps tables.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2024-01-01 00:00:00

This migration creates the complete normalized schema for the
Banking Operations & Database Monitoring System.

Table creation order respects foreign key dependencies:
    roles -> users -> servers -> database_instances
    -> backup_jobs -> backup_runs -> backup_verifications
    -> restore_tests -> incidents -> incident_history
    -> audit_logs -> login_history -> monitoring_metrics
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── roles ──────────────────────────────────────────────────
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.String(255), default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_roles_name", "roles", ["name"])

    # ── users ──────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(80), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("must_change_password", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    # ── servers ────────────────────────────────────────────────
    op.create_table(
        "servers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("hostname", sa.String(120), nullable=False, unique=True),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("operating_system", sa.String(120), nullable=False),
        sa.Column("os_version", sa.String(80), default=""),
        sa.Column("environment", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), default="online"),
        sa.Column("cpu_cores", sa.Integer(), default=4),
        sa.Column("memory_gb", sa.Float(), default=16.0),
        sa.Column("disk_gb", sa.Float(), default=100.0),
        sa.Column("cpu_percent", sa.Float(), default=0.0),
        sa.Column("memory_percent", sa.Float(), default=0.0),
        sa.Column("disk_percent", sa.Float(), default=0.0),
        sa.Column("network_in_mbps", sa.Float(), default=0.0),
        sa.Column("network_out_mbps", sa.Float(), default=0.0),
        sa.Column("uptime_seconds", sa.BigInteger(), default=0),
        sa.Column("last_boot", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_servers_hostname", "servers", ["hostname"])
    op.create_index("ix_servers_status", "servers", ["status"])
    op.create_index("ix_servers_environment", "servers", ["environment"])

    # ── database_instances ─────────────────────────────────────
    op.create_table(
        "database_instances",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("db_type", sa.String(50), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("port", sa.Integer(), default=5432),
        sa.Column("server_id", sa.Integer(), sa.ForeignKey("servers.id"), nullable=False),
        sa.Column("assigned_admin_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("environment", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), default="online"),
        sa.Column("storage_used_gb", sa.Float(), default=0.0),
        sa.Column("storage_total_gb", sa.Float(), default=100.0),
        sa.Column("last_health_check", sa.DateTime(timezone=True), nullable=True),
        sa.Column("availability_percent", sa.Float(), default=100.0),
        sa.Column("description", sa.Text(), default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_db_instances_name", "database_instances", ["name"])
    op.create_index("ix_db_instances_status", "database_instances", ["status"])
    op.create_index("ix_db_instances_environment", "database_instances", ["environment"])
    op.create_index("ix_db_instances_type", "database_instances", ["db_type"])

    # ── backup_jobs ────────────────────────────────────────────
    op.create_table(
        "backup_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("database_instance_id", sa.Integer(), sa.ForeignKey("database_instances.id"), nullable=False),
        sa.Column("backup_type", sa.String(20), nullable=False),
        sa.Column("schedule", sa.String(100), nullable=False),
        sa.Column("retention_days", sa.Integer(), default=30),
        sa.Column("destination", sa.String(255), default="s3://bankops-backups/"),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_backup_jobs_db_instance", "backup_jobs", ["database_instance_id"])
    op.create_index("ix_backup_jobs_active", "backup_jobs", ["is_active"])

    # ── backup_runs ────────────────────────────────────────────
    op.create_table(
        "backup_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("backup_job_id", sa.Integer(), sa.ForeignKey("backup_jobs.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), default=0),
        sa.Column("duration_seconds", sa.BigInteger(), default=0),
        sa.Column("error_message", sa.Text(), default=""),
        sa.Column("verified", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_backup_runs_job_id", "backup_runs", ["backup_job_id"])
    op.create_index("ix_backup_runs_status", "backup_runs", ["status"])
    op.create_index("ix_backup_runs_started_at", "backup_runs", ["started_at"])

    # ── backup_verifications ───────────────────────────────────
    op.create_table(
        "backup_verifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("backup_run_id", sa.Integer(), sa.ForeignKey("backup_runs.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Float(), default=0.0),
        sa.Column("checksum_expected", sa.String(128), default=""),
        sa.Column("checksum_actual", sa.String(128), default=""),
        sa.Column("integrity_check", sa.String(20), default="pending"),
        sa.Column("error_message", sa.Text(), default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── restore_tests ──────────────────────────────────────────
    op.create_table(
        "restore_tests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("backup_run_id", sa.Integer(), sa.ForeignKey("backup_runs.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Float(), default=0.0),
        sa.Column("data_integrity_check", sa.String(20), default="pending"),
        sa.Column("rows_validated", sa.Integer(), default=0),
        sa.Column("error_message", sa.Text(), default=""),
        sa.Column("notes", sa.Text(), default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── incidents ──────────────────────────────────────────────
    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), default=""),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), default="open"),
        sa.Column("database_instance_id", sa.Integer(), sa.ForeignKey("database_instances.id"), nullable=True),
        sa.Column("server_id", sa.Integer(), sa.ForeignKey("servers.id"), nullable=True),
        sa.Column("assigned_to_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reported_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_incidents_status", "incidents", ["status"])
    op.create_index("ix_incidents_severity", "incidents", ["severity"])
    op.create_index("ix_incidents_created_at", "incidents", ["created_at"])

    # ── incident_history ───────────────────────────────────────
    op.create_table(
        "incident_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("incident_id", sa.Integer(), sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("changed_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("field_changed", sa.String(50), nullable=False),
        sa.Column("old_value", sa.Text(), default=""),
        sa.Column("new_value", sa.Text(), default=""),
        sa.Column("comment", sa.Text(), default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── audit_logs ─────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("username", sa.String(80), default="system"),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(50), default=""),
        sa.Column("description", sa.Text(), default=""),
        sa.Column("ip_address", sa.String(45), default=""),
        sa.Column("user_agent", sa.String(255), default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])
    op.create_index("ix_audit_logs_resource_type", "audit_logs", ["resource_type"])

    # ── login_history ──────────────────────────────────────────
    op.create_table(
        "login_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("username", sa.String(80), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("failure_reason", sa.String(255), default=""),
        sa.Column("ip_address", sa.String(45), default=""),
        sa.Column("user_agent", sa.String(255), default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_login_history_user_id", "login_history", ["user_id"])
    op.create_index("ix_login_history_created_at", "login_history", ["created_at"])

    # ── monitoring_metrics ────────────────────────────────────
    op.create_table(
        "monitoring_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("server_id", sa.Integer(), sa.ForeignKey("servers.id"), nullable=True),
        sa.Column("database_instance_id", sa.Integer(), sa.ForeignKey("database_instances.id"), nullable=True),
        sa.Column("metric_type", sa.String(50), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(20), default="percent"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_metrics_server_id", "monitoring_metrics", ["server_id"])
    op.create_index("ix_metrics_db_instance_id", "monitoring_metrics", ["database_instance_id"])
    op.create_index("ix_metrics_timestamp", "monitoring_metrics", ["timestamp"])
    op.create_index("ix_metrics_type", "monitoring_metrics", ["metric_type"])


def downgrade() -> None:
    """Drop all tables in reverse dependency order."""
    op.drop_table("monitoring_metrics")
    op.drop_table("login_history")
    op.drop_table("audit_logs")
    op.drop_table("incident_history")
    op.drop_table("incidents")
    op.drop_table("restore_tests")
    op.drop_table("backup_verifications")
    op.drop_table("backup_runs")
    op.drop_table("backup_jobs")
    op.drop_table("database_instances")
    op.drop_table("servers")
    op.drop_table("users")
    op.drop_table("roles")
