"""
Dashboard router — aggregated metrics and summary data.

Provides the data for the main dashboard page.
All endpoints require authentication.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.database import get_db
from app.dependencies import get_current_user
from app.models import (
    DatabaseInstance, Server, BackupRun, BackupJob,
    Incident, MonitoringMetric, AuditLog,
)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get aggregated dashboard summary metrics.

    Returns counts, percentages, and status summaries
    for the main dashboard cards.
    """
    # Database instance counts
    total_databases = db.query(DatabaseInstance).count()
    online_databases = db.query(DatabaseInstance).filter(
        DatabaseInstance.status == "online"
    ).count()
    offline_databases = db.query(DatabaseInstance).filter(
        DatabaseInstance.status == "offline"
    ).count()

    # Server counts
    total_servers = db.query(Server).count()
    online_servers = db.query(Server).filter(Server.status == "online").count()

    # Average availability
    avg_availability = db.query(
        func.avg(DatabaseInstance.availability_percent)
    ).scalar() or 0.0

    # Latest successful backup
    latest_backup = db.query(BackupRun).filter(
        BackupRun.status == "success"
    ).order_by(BackupRun.completed_at.desc()).first()

    # Failed backup count (last 30 days)
    from datetime import datetime, timedelta, timezone
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    failed_backups = db.query(BackupRun).filter(
        BackupRun.status == "failed",
        BackupRun.started_at >= thirty_days_ago,
    ).count()

    # Open incidents
    open_incidents = db.query(Incident).filter(
        Incident.status.in_(["open", "investigating"])
    ).count()

    # Critical open incidents
    critical_incidents = db.query(Incident).filter(
        Incident.status.in_(["open", "investigating"]),
        Incident.severity == "critical",
    ).count()

    # Average CPU and memory across servers
    avg_cpu = db.query(func.avg(Server.cpu_percent)).scalar() or 0.0
    avg_memory = db.query(func.avg(Server.memory_percent)).scalar() or 0.0

    # Storage utilization
    total_storage = db.query(func.sum(Server.disk_gb)).scalar() or 0.0
    # Approximate used storage from server disk_percent
    servers = db.query(Server).all()
    used_storage = sum(s.disk_gb * s.disk_percent / 100 for s in servers)
    storage_percent = (used_storage / total_storage * 100) if total_storage > 0 else 0

    return {
        "databases": {
            "total": total_databases,
            "online": online_databases,
            "offline": offline_databases,
            "availability_percent": round(avg_availability, 2),
        },
        "servers": {
            "total": total_servers,
            "online": online_servers,
        },
        "backups": {
            "latest_successful": {
                "id": latest_backup.id,
                "completed_at": latest_backup.completed_at.isoformat() if latest_backup.completed_at else None,
                "size_bytes": latest_backup.size_bytes,
            } if latest_backup else None,
            "failed_count_30d": failed_backups,
        },
        "incidents": {
            "open": open_incidents,
            "critical": critical_incidents,
        },
        "resources": {
            "cpu_percent": round(avg_cpu, 1),
            "memory_percent": round(avg_memory, 1),
            "storage_percent": round(storage_percent, 1),
            "storage_used_gb": round(used_storage, 1),
            "storage_total_gb": round(total_storage, 1),
        },
    }


@router.get("/performance-trends")
def get_performance_trends(
    hours: int = 24,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get time-series performance trends for charts.

    Returns CPU, memory, and network metrics averaged
    across all servers for the specified time window.
    """
    from datetime import datetime, timedelta, timezone

    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    # Query metrics and group by hour
    metrics = db.query(
        func.date_trunc('hour', MonitoringMetric.timestamp).label('hour'),
        MonitoringMetric.metric_type,
        func.avg(MonitoringMetric.value).label('avg_value'),
    ).filter(
        MonitoringMetric.timestamp >= since,
        MonitoringMetric.server_id.isnot(None),
    ).group_by('hour', MonitoringMetric.metric_type).order_by('hour').all()

    # Organize by metric type
    result = {}
    for hour, metric_type, avg_value in metrics:
        if metric_type not in result:
            result[metric_type] = []
        result[metric_type].append({
            "timestamp": hour.isoformat(),
            "value": round(avg_value, 2),
        })

    return result


@router.get("/recent-events")
def get_recent_events(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get recent system events for the dashboard activity feed.

    Combines recent incidents, backup failures, and audit logs.
    """
    from datetime import datetime, timedelta, timezone

    since = datetime.now(timezone.utc) - timedelta(days=7)

    # Recent incidents
    incidents = db.query(Incident).filter(
        Incident.created_at >= since
    ).order_by(Incident.created_at.desc()).limit(5).all()

    # Recent backup failures
    backup_failures = db.query(BackupRun).filter(
        BackupRun.status == "failed",
        BackupRun.started_at >= since,
    ).order_by(BackupRun.started_at.desc()).limit(5).all()

    # Recent audit logs
    audit_logs = db.query(AuditLog).filter(
        AuditLog.created_at >= since
    ).order_by(AuditLog.created_at.desc()).limit(10).all()

    events = []

    for inc in incidents:
        events.append({
            "type": "incident",
            "severity": inc.severity,
            "title": inc.title,
            "status": inc.status,
            "timestamp": inc.created_at.isoformat(),
        })

    for run in backup_failures:
        events.append({
            "type": "backup_failure",
            "severity": "high",
            "title": f"Backup failed: {run.backup_job.name}",
            "status": "failed",
            "timestamp": run.started_at.isoformat(),
        })

    for log in audit_logs:
        events.append({
            "type": "audit",
            "severity": "info",
            "title": log.description,
            "status": "info",
            "timestamp": log.created_at.isoformat(),
        })

    # Sort by timestamp descending
    events.sort(key=lambda e: e["timestamp"], reverse=True)

    return events[:limit]


@router.get("/critical-alerts")
def get_critical_alerts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get critical alerts requiring immediate attention.

    Returns open critical incidents, failed backups in last 24h,
    and servers with high resource utilization.
    """
    from datetime import datetime, timedelta, timezone

    # Open critical incidents
    critical_incidents = db.query(Incident).filter(
        Incident.status.in_(["open", "investigating"]),
        Incident.severity == "critical",
    ).order_by(Incident.created_at.desc()).all()

    # Failed backups in last 24 hours
    yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_failures = db.query(BackupRun).filter(
        BackupRun.status == "failed",
        BackupRun.started_at >= yesterday,
    ).order_by(BackupRun.started_at.desc()).all()

    # Servers with high CPU or memory
    high_resource_servers = db.query(Server).filter(
        (Server.cpu_percent > 85) | (Server.memory_percent > 90)
    ).all()

    alerts = []

    for inc in critical_incidents:
        alerts.append({
            "type": "critical_incident",
            "title": inc.title,
            "description": inc.description,
            "timestamp": inc.created_at.isoformat(),
            "severity": "critical",
        })

    for run in recent_failures:
        alerts.append({
            "type": "backup_failure",
            "title": f"Backup failed: {run.backup_job.name}",
            "description": run.error_message,
            "timestamp": run.started_at.isoformat(),
            "severity": "high",
        })

    for server in high_resource_servers:
        alerts.append({
            "type": "high_resource_usage",
            "title": f"High resource usage on {server.hostname}",
            "description": f"CPU: {server.cpu_percent}%, Memory: {server.memory_percent}%",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": "medium",
        })

    return alerts
