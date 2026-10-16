"""
BankOps Demo Data Seeder.

Populates the database with realistic simulated data for the
Banking Operations & Database Monitoring System.

ALL DATA IS SIMULATED — no real banking systems or customer data.

Usage:
    python -m app.seed

This script is idempotent: it clears existing data before seeding.
"""
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models import (
    Role, User, Server, DatabaseInstance,
    BackupJob, BackupRun, BackupVerification, RestoreTest,
    Incident, IncidentHistory, AuditLog, LoginHistory, MonitoringMetric,
)
from app.security.password import hash_password

# ── Constants ──────────────────────────────────────────────────

DB_TYPES = ["oracle", "sqlserver", "mysql", "postgresql"]
DB_VERSIONS = {
    "oracle": ["19c", "21c", "23ai"],
    "sqlserver": ["2019", "2022"],
    "mysql": ["8.0", "8.4"],
    "postgresql": ["15", "16"],
}
ENVIRONMENTS = ["production", "testing", "development"]
SERVER_OS = [
    ("Windows Server 2022", "21H2"),
    ("Windows Server 2019", "1809"),
    ("Red Hat Enterprise Linux", "9.3"),
    ("Ubuntu Server", "22.04 LTS"),
    ("Oracle Linux", "8.9"),
]
BACKUP_TYPES = ["full", "incremental", "differential"]
INCIDENT_SEVERITIES = ["critical", "high", "medium", "low"]
INCIDENT_STATUSES = ["open", "investigating", "resolved", "closed"]

# Deterministic random for reproducible seed data
random.seed(42)


def _now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def _days_ago(days: int) -> datetime:
    """Return a datetime N days ago."""
    return _now() - timedelta(days=days)


def _hours_ago(hours: int) -> datetime:
    """Return a datetime N hours ago."""
    return _now() - timedelta(hours=hours)


# ── Seed Functions ─────────────────────────────────────────────

def seed_roles(db: Session) -> dict[str, Role]:
    """Create the three RBAC roles."""
    roles = {}
    for name, desc in [
        ("admin", "Full system access — user management, all CRUD operations"),
        ("dba", "Database management — CRUD on databases, backups, incidents"),
        ("viewer", "Read-only access — dashboards, reports, no mutations"),
    ]:
        role = Role(name=name, description=desc)
        db.add(role)
        roles[name] = role
    db.flush()
    return roles


def seed_users(db: Session, roles: dict[str, Role]) -> dict[str, User]:
    """Create demo users with hashed passwords."""
    users = {}
    user_data = [
        ("admin", "admin@bankops.local", "System Administrator", "admin", "Admin@123"),
        ("dba", "dba@bankops.local", "Senior DBA", "dba", "Dba@123"),
        ("viewer", "viewer@bankops.local", "Read-Only Viewer", "viewer", "Viewer@123"),
        ("jsmith", "jsmith@bankops.local", "John Smith", "dba", "Jsmith@123"),
        ("agarcia", "agarcia@bankops.local", "Ana Garcia", "dba", "Agarcia@123"),
        ("mwilson", "mwilson@bankops.local", "Mike Wilson", "viewer", "Mwilson@123"),
    ]
    for username, email, full_name, role_name, password in user_data:
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role_id=roles[role_name].id,
            is_active=True,
            last_login=_hours_ago(random.randint(1, 48)),
        )
        db.add(user)
        users[username] = user
    db.flush()
    return users


def seed_servers(db: Session) -> list[Server]:
    """Create demo servers."""
    servers = []
    server_data = [
        ("srv-db-prod-01", "10.0.1.11", "Windows Server 2022", "21H2", "production", 16, 64.0, 500.0),
        ("srv-db-prod-02", "10.0.1.12", "Red Hat Enterprise Linux", "9.3", "production", 16, 64.0, 500.0),
        ("srv-db-prod-03", "10.0.1.13", "Oracle Linux", "8.9", "production", 8, 32.0, 250.0),
        ("srv-db-test-01", "10.0.2.21", "Ubuntu Server", "22.04 LTS", "testing", 8, 32.0, 200.0),
        ("srv-db-dev-01", "10.0.3.31", "Windows Server 2019", "1809", "development", 4, 16.0, 100.0),
        ("srv-db-prod-04", "10.0.1.14", "Red Hat Enterprise Linux", "9.3", "production", 32, 128.0, 1000.0),
    ]
    for hostname, ip, os_name, os_ver, env, cores, mem, disk in server_data:
        status = random.choices(["online", "offline", "maintenance"], weights=[85, 10, 5])[0]
        server = Server(
            hostname=hostname,
            ip_address=ip,
            operating_system=os_name,
            os_version=os_ver,
            environment=env,
            status=status,
            cpu_cores=cores,
            memory_gb=mem,
            disk_gb=disk,
            cpu_percent=round(random.uniform(5, 85), 1),
            memory_percent=round(random.uniform(20, 90), 1),
            disk_percent=round(random.uniform(30, 80), 1),
            network_in_mbps=round(random.uniform(10, 500), 1),
            network_out_mbps=round(random.uniform(5, 200), 1),
            uptime_seconds=random.randint(86400, 2592000),
            last_boot=_days_ago(random.randint(1, 30)),
        )
        db.add(server)
        servers.append(server)
    db.flush()
    return servers


def seed_database_instances(db: Session, servers: list[Server], users: dict[str, User]) -> list[DatabaseInstance]:
    """Create demo database instances across all types."""
    instances = []
    db_data = [
        # (name, type, version, port, server_idx, env, admin_username, storage_used, storage_total)
        ("CORE-BANKING-DB", "oracle", "19c", 1521, 0, "production", "jsmith", 320.0, 500.0),
        ("PAYMENTS-DB", "oracle", "21c", 1521, 1, "production", "agarcia", 280.0, 500.0),
        ("CUSTOMER-DB", "sqlserver", "2022", 1433, 2, "production", "jsmith", 180.0, 250.0),
        ("TRANSACTIONS-DB", "sqlserver", "2019", 1433, 5, "production", "agarcia", 750.0, 1000.0),
        ("WEBAPP-DB", "mysql", "8.0", 3306, 1, "production", "jsmith", 95.0, 200.0),
        ("ANALYTICS-DB", "postgresql", "16", 5432, 5, "production", "agarcia", 420.0, 1000.0),
        ("TEST-CORE-DB", "oracle", "19c", 1521, 3, "testing", "jsmith", 45.0, 100.0),
        ("TEST-WEBAPP-DB", "mysql", "8.4", 3306, 3, "testing", "agarcia", 22.0, 50.0),
        ("DEV-APP-DB", "postgresql", "15", 5432, 4, "development", "jsmith", 8.0, 30.0),
        ("DEV-LEGACY-DB", "sqlserver", "2019", 1433, 4, "development", "agarcia", 15.0, 50.0),
    ]
    for name, db_type, version, port, srv_idx, env, admin, used, total in db_data:
        status = random.choices(["online", "offline", "degraded"], weights=[80, 10, 10])[0]
        instance = DatabaseInstance(
            name=name,
            db_type=db_type,
            version=version,
            port=port,
            server_id=servers[srv_idx].id,
            assigned_admin_id=users[admin].id,
            environment=env,
            status=status,
            storage_used_gb=used,
            storage_total_gb=total,
            last_health_check=_hours_ago(random.randint(1, 24)),
            availability_percent=round(random.uniform(95.0, 100.0), 2),
            description=f"{db_type.upper()} database for {env} environment",
        )
        db.add(instance)
        instances.append(instance)
    db.flush()
    return instances


def seed_backup_jobs(db: Session, instances: list[DatabaseInstance]) -> list[BackupJob]:
    """Create backup jobs for each database instance."""
    jobs = []
    schedules = {
        "full": "0 2 * * *",        # Daily at 2 AM
        "incremental": "0 */4 * * *",  # Every 4 hours
        "differential": "0 1 * * *",   # Daily at 1 AM
    }
    for instance in instances:
        # Each instance gets 1-2 backup jobs
        num_jobs = random.randint(1, 2)
        for i in range(num_jobs):
            btype = random.choice(BACKUP_TYPES)
            job = BackupJob(
                name=f"{instance.name}-{btype.upper()}-{i+1}",
                database_instance_id=instance.id,
                backup_type=btype,
                schedule=schedules[btype],
                retention_days=random.choice([7, 14, 30, 90]),
                destination=f"s3://bankops-backups/{instance.environment}/{instance.name}/",
                is_active=True,
            )
            db.add(job)
            jobs.append(job)
    db.flush()
    return jobs


def seed_backup_runs(db: Session, jobs: list[BackupJob]) -> list[BackupRun]:
    """Create backup run history for each job."""
    runs = []
    for job in jobs:
        # Generate 10-20 runs per job
        for _ in range(random.randint(10, 20)):
            started = _days_ago(random.randint(0, 30))
            duration = random.randint(300, 7200)  # 5 min to 2 hours
            completed = started + timedelta(seconds=duration)
            status = random.choices(
                ["success", "failed", "cancelled"],
                weights=[80, 15, 5]
            )[0]
            size = random.randint(1_000_000, 500_000_000_000) if status == "success" else 0
            error = ""
            if status == "failed":
                error = random.choice([
                    "Connection timeout to database server",
                    "Insufficient disk space on backup target",
                    "Network interruption during transfer",
                    "Database lock timeout — could not acquire backup lock",
                    "Authentication failure — invalid credentials",
                    "Backup verification checksum mismatch",
                ])
            run = BackupRun(
                backup_job_id=job.id,
                status=status,
                started_at=started,
                completed_at=completed if status != "running" else None,
                size_bytes=size,
                duration_seconds=duration if status != "running" else 0,
                error_message=error,
                verified=(status == "success" and random.random() > 0.3),
            )
            db.add(run)
            runs.append(run)
    db.flush()
    return runs


def seed_backup_verifications(db: Session, runs: list[BackupRun]) -> list[BackupVerification]:
    """Create verification records for successful backup runs."""
    verifications = []
    for run in runs:
        if run.status == "success" and run.verified:
            started = run.completed_at
            duration = random.uniform(30, 600)
            completed = started + timedelta(seconds=duration)
            status = random.choices(["success", "failed"], weights=[90, 10])[0]
            checksum = f"sha256:{random.getrandbits(256):064x}"
            verification = BackupVerification(
                backup_run_id=run.id,
                status=status,
                started_at=started,
                completed_at=completed,
                duration_seconds=duration,
                checksum_expected=checksum,
                checksum_actual=checksum if status == "success" else f"sha256:{random.getrandbits(256):064x}",
                integrity_check="passed" if status == "success" else "failed",
                error_message="" if status == "success" else "Checksum mismatch — backup file corrupted",
            )
            db.add(verification)
            verifications.append(verification)
    db.flush()
    return verifications


def seed_restore_tests(db: Session, runs: list[BackupRun]) -> list[RestoreTest]:
    """Create restore test records for some verified backups."""
    tests = []
    verified_runs = [r for r in runs if r.status == "success" and r.verified]
    # Test about 30% of verified backups
    for run in random.sample(verified_runs, min(len(verified_runs) // 3, 15)):
        started = run.completed_at + timedelta(hours=random.randint(1, 48))
        duration = random.uniform(600, 3600)
        completed = started + timedelta(seconds=duration)
        status = random.choices(["success", "failed"], weights=[85, 15])[0]
        test = RestoreTest(
            backup_run_id=run.id,
            status=status,
            started_at=started,
            completed_at=completed,
            duration_seconds=duration,
            data_integrity_check="passed" if status == "success" else "failed",
            rows_validated=random.randint(10000, 10000000) if status == "success" else 0,
            error_message="" if status == "success" else "Data integrity check failed — row count mismatch",
            notes="Automated restore test to sandbox environment",
        )
        db.add(test)
        tests.append(test)
    db.flush()
    return tests


def seed_incidents(db: Session, instances: list[DatabaseInstance], servers: list[Server], users: dict[str, User]) -> list[Incident]:
    """Create demo incidents with realistic scenarios."""
    incidents = []
    incident_data = [
        ("CORE-BANKING-DB connection timeout", "Production core banking database experiencing intermittent connection timeouts. Affecting transaction processing.", "critical", "investigating", 0, None, "jsmith", "admin"),
        ("PAYMENTS-DB disk space critical", "Payments database server disk usage at 95%. Immediate cleanup required.", "high", "open", 1, None, "agarcia", "dba"),
        ("CUSTOMER-DB replication lag", "Customer database replication lag exceeding 30 seconds. Investigating network issues.", "medium", "resolved", 2, None, "jsmith", "dba"),
        ("WEBAPP-DB slow query performance", "Web application database experiencing slow query performance during peak hours.", "low", "closed", 4, None, "agarcia", "dba"),
        ("srv-db-prod-02 memory leak", "Red Hat production server showing memory leak pattern. Restart scheduled for maintenance window.", "high", "investigating", None, 1, "jsmith", "admin"),
        ("TRANSACTIONS-DB backup failure", "Last 3 backup jobs for transactions database failed due to network interruption.", "critical", "open", 5, None, "agarcia", "dba"),
        ("ANALYTICS-DB index corruption", "Analytics database showing index corruption on large fact table. Rebuild in progress.", "medium", "resolved", 6, None, "jsmith", "dba"),
        ("DEV-APP-DB unauthorized access attempt", "Multiple failed login attempts detected on development database.", "low", "closed", 8, None, "agarcia", "admin"),
    ]
    for title, desc, severity, status, db_idx, srv_idx, assignee, reporter in incident_data:
        created = _days_ago(random.randint(1, 14))
        resolved = None
        closed = None
        if status in ("resolved", "closed"):
            resolved = created + timedelta(hours=random.randint(2, 48))
        if status == "closed":
            closed = resolved + timedelta(hours=random.randint(1, 24))
        incident = Incident(
            title=title,
            description=desc,
            severity=severity,
            status=status,
            database_instance_id=instances[db_idx].id if db_idx is not None else None,
            server_id=servers[srv_idx].id if srv_idx is not None else None,
            assigned_to_id=users[assignee].id,
            reported_by_id=users[reporter].id,
            created_at=created,
            resolved_at=resolved,
            closed_at=closed,
        )
        db.add(incident)
        incidents.append(incident)
    db.flush()
    return incidents


def seed_incident_history(db: Session, incidents: list[Incident], users: dict[str, User]):
    """Create history entries for incidents."""
    for incident in incidents:
        # Always create an "opened" entry
        history = IncidentHistory(
            incident_id=incident.id,
            changed_by_id=incident.reported_by_id,
            field_changed="status",
            old_value="",
            new_value="open",
            comment="Incident created",
        )
        db.add(history)

        # Add status change entries based on current status
        if incident.status in ("investigating", "resolved", "closed"):
            h = IncidentHistory(
                incident_id=incident.id,
                changed_by_id=incident.assigned_to_id,
                field_changed="status",
                old_value="open",
                new_value="investigating",
                comment="Started investigation",
            )
            db.add(h)
        if incident.status in ("resolved", "closed"):
            h = IncidentHistory(
                incident_id=incident.id,
                changed_by_id=incident.assigned_to_id,
                field_changed="status",
                old_value="investigating",
                new_value="resolved",
                comment="Issue resolved — root cause identified and fixed",
            )
            db.add(h)
        if incident.status == "closed":
            h = IncidentHistory(
                incident_id=incident.id,
                changed_by_id=incident.assigned_to_id,
                field_changed="status",
                old_value="resolved",
                new_value="closed",
                comment="Incident closed — verified stable for 24 hours",
            )
            db.add(h)
    db.flush()


def seed_audit_logs(db: Session, users: dict[str, User]):
    """Create audit log entries."""
    actions = [
        ("user.login", "user", "User logged in successfully"),
        ("user.logout", "user", "User logged out"),
        ("user.created", "user", "New user account created"),
        ("user.updated", "user", "User profile updated"),
        ("database.created", "database", "Database instance added to monitoring"),
        ("database.updated", "database", "Database instance configuration updated"),
        ("database.deleted", "database", "Database instance removed from monitoring"),
        ("backup.started", "backup", "Backup job started"),
        ("backup.completed", "backup", "Backup job completed successfully"),
        ("backup.failed", "backup", "Backup job failed"),
        ("incident.created", "incident", "New incident reported"),
        ("incident.updated", "incident", "Incident status updated"),
        ("server.updated", "server", "Server metrics updated"),
        ("report.exported", "report", "Report exported to CSV"),
    ]
    for _ in range(50):
        action, resource_type, desc = random.choice(actions)
        user = random.choice(list(users.values()))
        log = AuditLog(
            user_id=user.id,
            username=user.username,
            action=action,
            resource_type=resource_type,
            resource_id=str(random.randint(1, 100)),
            description=desc,
            ip_address=f"10.0.{random.randint(0, 255)}.{random.randint(1, 254)}",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            created_at=_hours_ago(random.randint(1, 720)),
        )
        db.add(log)
    db.flush()


def seed_login_history(db: Session, users: dict[str, User]):
    """Create login history entries."""
    for _ in range(80):
        user = random.choice(list(users.values()))
        success = random.choices([True, False], weights=[90, 10])[0]
        reason = ""
        if not success:
            reason = random.choice([
                "Invalid password",
                "Account locked",
                "Account disabled",
                "Password expired",
            ])
        entry = LoginHistory(
            user_id=user.id if success else None,
            username=user.username,
            success=success,
            failure_reason=reason,
            ip_address=f"10.0.{random.randint(0, 255)}.{random.randint(1, 254)}",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            created_at=_hours_ago(random.randint(1, 720)),
        )
        db.add(entry)
    db.flush()


def seed_monitoring_metrics(db: Session, servers: list[Server], instances: list[DatabaseInstance]):
    """Create time-series monitoring metrics for the last 7 days."""
    metric_types = ["cpu", "memory", "disk", "network_in", "network_out"]
    now = _now()
    for server in servers:
        for metric_type in metric_types:
            # Generate data points every 15 minutes for 7 days
            for i in range(7 * 24 * 4):  # 7 days * 24 hours * 4 per hour
                timestamp = now - timedelta(minutes=15 * i)
                if metric_type == "cpu":
                    value = random.uniform(5, 95)
                elif metric_type == "memory":
                    value = random.uniform(20, 90)
                elif metric_type == "disk":
                    value = random.uniform(30, 85)
                elif metric_type == "network_in":
                    value = random.uniform(10, 500)
                else:
                    value = random.uniform(5, 200)
                metric = MonitoringMetric(
                    server_id=server.id,
                    metric_type=metric_type,
                    value=round(value, 2),
                    unit="percent" if metric_type in ("cpu", "memory", "disk") else "mbps",
                    timestamp=timestamp,
                )
                db.add(metric)

    for instance in instances:
        for metric_type in ["cpu", "memory", "iops"]:
            for i in range(7 * 24 * 4):
                timestamp = now - timedelta(minutes=15 * i)
                if metric_type == "cpu":
                    value = random.uniform(10, 80)
                elif metric_type == "memory":
                    value = random.uniform(30, 85)
                else:
                    value = random.uniform(100, 5000)
                metric = MonitoringMetric(
                    database_instance_id=instance.id,
                    metric_type=metric_type,
                    value=round(value, 2),
                    unit="percent" if metric_type in ("cpu", "memory") else "iops",
                    timestamp=timestamp,
                )
                db.add(metric)
    db.flush()


# ── Main Seeder ────────────────────────────────────────────────

def run_seed():
    """
    Run the complete seed process.

    Clears all existing data and populates the database with
    realistic demo data. Uses a single transaction.
    """
    db = SessionLocal()
    try:
        print("Clearing existing data...")
        # Delete in reverse dependency order
        db.query(MonitoringMetric).delete()
        db.query(LoginHistory).delete()
        db.query(AuditLog).delete()
        db.query(IncidentHistory).delete()
        db.query(Incident).delete()
        db.query(RestoreTest).delete()
        db.query(BackupVerification).delete()
        db.query(BackupRun).delete()
        db.query(BackupJob).delete()
        db.query(DatabaseInstance).delete()
        db.query(Server).delete()
        db.query(User).delete()
        db.query(Role).delete()
        db.commit()

        print("Seeding roles...")
        roles = seed_roles(db)

        print("Seeding users...")
        users = seed_users(db, roles)

        print("Seeding servers...")
        servers = seed_servers(db)

        print("Seeding database instances...")
        instances = seed_database_instances(db, servers, users)

        print("Seeding backup jobs...")
        jobs = seed_backup_jobs(db, instances)

        print("Seeding backup runs...")
        runs = seed_backup_runs(db, jobs)

        print("Seeding backup verifications...")
        verifications = seed_backup_verifications(db, runs)

        print("Seeding restore tests...")
        tests = seed_restore_tests(db, runs)

        print("Seeding incidents...")
        incidents = seed_incidents(db, instances, servers, users)

        print("Seeding incident history...")
        seed_incident_history(db, incidents, users)

        print("Seeding audit logs...")
        seed_audit_logs(db, users)

        print("Seeding login history...")
        seed_login_history(db, users)

        print("Seeding monitoring metrics...")
        seed_monitoring_metrics(db, servers, instances)

        db.commit()
        print(f"""
Seed complete!
  Roles: {len(roles)}
  Users: {len(users)}
  Servers: {len(servers)}
  Database Instances: {len(instances)}
  Backup Jobs: {len(jobs)}
  Backup Runs: {len(runs)}
  Backup Verifications: {len(verifications)}
  Restore Tests: {len(tests)}
  Incidents: {len(incidents)}
  Audit Logs: {db.query(AuditLog).count()}
  Login History: {db.query(LoginHistory).count()}
  Monitoring Metrics: {db.query(MonitoringMetric).count()}

Demo login credentials:
  admin / Admin@123    (Admin role)
  dba / Dba@123        (DBA role)
  viewer / Viewer@123  (Viewer role)
""")
    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
