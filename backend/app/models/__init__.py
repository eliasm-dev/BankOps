"""
SQLAlchemy Models Package.

Importing all models here ensures they are registered with the
declarative Base before Alembic runs autogenerate.
"""
from app.models.role import Role
from app.models.user import User
from app.models.server import Server
from app.models.database_instance import DatabaseInstance
from app.models.backup_job import BackupJob
from app.models.backup_run import BackupRun
from app.models.backup_verification import BackupVerification
from app.models.restore_test import RestoreTest
from app.models.incident import Incident
from app.models.incident_history import IncidentHistory
from app.models.audit_log import AuditLog
from app.models.login_history import LoginHistory
from app.models.monitoring_metric import MonitoringMetric

__all__ = [
    "Role",
    "User",
    "Server",
    "DatabaseInstance",
    "BackupJob",
    "BackupRun",
    "BackupVerification",
    "RestoreTest",
    "Incident",
    "IncidentHistory",
    "AuditLog",
    "LoginHistory",
    "MonitoringMetric",
]
