-- ============================================================================
-- BankOps — Banking Operations & Database Monitoring System
-- PostgreSQL Schema Reference
-- ============================================================================
-- This file is the canonical DDL reference. The actual schema is managed
-- by Alembic migrations (see backend/alembic/versions/).
-- ============================================================================

-- ── Roles ───────────────────────────────────────────────────────────────────
CREATE TABLE roles (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255) DEFAULT '',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_roles_name ON roles (name);

-- ── Users ───────────────────────────────────────────────────────────────────
CREATE TABLE users (
    id                  SERIAL PRIMARY KEY,
    username            VARCHAR(80) NOT NULL UNIQUE,
    email               VARCHAR(255) NOT NULL UNIQUE,
    full_name           VARCHAR(120) NOT NULL,
    hashed_password     VARCHAR(255) NOT NULL,
    role_id             INTEGER NOT NULL REFERENCES roles(id),
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    must_change_password BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login          TIMESTAMPTZ
);
CREATE INDEX ix_users_username ON users (username);
CREATE INDEX ix_users_email ON users (email);

-- ── Servers ─────────────────────────────────────────────────────────────────
CREATE TABLE servers (
    id                SERIAL PRIMARY KEY,
    hostname          VARCHAR(120) NOT NULL UNIQUE,
    ip_address        VARCHAR(45) NOT NULL,
    operating_system  VARCHAR(120) NOT NULL,
    os_version        VARCHAR(80) DEFAULT '',
    environment       VARCHAR(20) NOT NULL,
    status            VARCHAR(20) NOT NULL DEFAULT 'online',
    cpu_cores         INTEGER NOT NULL DEFAULT 4,
    memory_gb         DOUBLE PRECISION NOT NULL DEFAULT 16.0,
    disk_gb           DOUBLE PRECISION NOT NULL DEFAULT 100.0,
    cpu_percent       DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    memory_percent    DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    disk_percent      DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    network_in_mbps   DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    network_out_mbps  DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    uptime_seconds    BIGINT NOT NULL DEFAULT 0,
    last_boot         TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_servers_hostname ON servers (hostname);
CREATE INDEX ix_servers_status ON servers (status);
CREATE INDEX ix_servers_environment ON servers (environment);

-- ── Database Instances ───────────────────────────────────────────────────────
CREATE TABLE database_instances (
    id                    SERIAL PRIMARY KEY,
    name                  VARCHAR(120) NOT NULL,
    db_type               VARCHAR(50) NOT NULL,
    version               VARCHAR(50) NOT NULL,
    port                  INTEGER NOT NULL DEFAULT 5432,
    server_id             INTEGER NOT NULL REFERENCES servers(id),
    assigned_admin_id     INTEGER REFERENCES users(id),
    environment           VARCHAR(20) NOT NULL,
    status                VARCHAR(20) NOT NULL DEFAULT 'online',
    storage_used_gb       DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    storage_total_gb      DOUBLE PRECISION NOT NULL DEFAULT 100.0,
    last_health_check     TIMESTAMPTZ,
    availability_percent  DOUBLE PRECISION NOT NULL DEFAULT 100.0,
    description           TEXT DEFAULT '',
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_db_instances_name ON database_instances (name);
CREATE INDEX ix_db_instances_status ON database_instances (status);
CREATE INDEX ix_db_instances_environment ON database_instances (environment);
CREATE INDEX ix_db_instances_type ON database_instances (db_type);

-- ── Backup Jobs ──────────────────────────────────────────────────────────────
CREATE TABLE backup_jobs (
    id                     SERIAL PRIMARY KEY,
    name                   VARCHAR(120) NOT NULL,
    database_instance_id   INTEGER NOT NULL REFERENCES database_instances(id),
    backup_type            VARCHAR(20) NOT NULL,
    schedule               VARCHAR(100) NOT NULL,
    retention_days         INTEGER NOT NULL DEFAULT 30,
    destination            VARCHAR(255) DEFAULT 's3://bankops-backups/',
    is_active              BOOLEAN NOT NULL DEFAULT TRUE,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_backup_jobs_db_instance ON backup_jobs (database_instance_id);
CREATE INDEX ix_backup_jobs_active ON backup_jobs (is_active);

-- ── Backup Runs ──────────────────────────────────────────────────────────────
CREATE TABLE backup_runs (
    id                SERIAL PRIMARY KEY,
    backup_job_id     INTEGER NOT NULL REFERENCES backup_jobs(id),
    status            VARCHAR(20) NOT NULL,
    started_at        TIMESTAMPTZ NOT NULL,
    completed_at      TIMESTAMPTZ,
    size_bytes        BIGINT NOT NULL DEFAULT 0,
    duration_seconds  BIGINT NOT NULL DEFAULT 0,
    error_message     TEXT DEFAULT '',
    verified          BOOLEAN NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_backup_runs_job_id ON backup_runs (backup_job_id);
CREATE INDEX ix_backup_runs_status ON backup_runs (status);
CREATE INDEX ix_backup_runs_started_at ON backup_runs (started_at);

-- ── Backup Verifications ─────────────────────────────────────────────────────
CREATE TABLE backup_verifications (
    id                SERIAL PRIMARY KEY,
    backup_run_id     INTEGER NOT NULL REFERENCES backup_runs(id),
    status            VARCHAR(20) NOT NULL,
    started_at        TIMESTAMPTZ NOT NULL,
    completed_at      TIMESTAMPTZ,
    duration_seconds  DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    checksum_expected VARCHAR(128) DEFAULT '',
    checksum_actual   VARCHAR(128) DEFAULT '',
    integrity_check   VARCHAR(20) DEFAULT 'pending',
    error_message     TEXT DEFAULT '',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Restore Tests ────────────────────────────────────────────────────────────
CREATE TABLE restore_tests (
    id                   SERIAL PRIMARY KEY,
    backup_run_id        INTEGER NOT NULL REFERENCES backup_runs(id),
    status               VARCHAR(20) NOT NULL,
    started_at           TIMESTAMPTZ NOT NULL,
    completed_at         TIMESTAMPTZ,
    duration_seconds     DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    data_integrity_check VARCHAR(20) DEFAULT 'pending',
    rows_validated       INTEGER NOT NULL DEFAULT 0,
    error_message        TEXT DEFAULT '',
    notes                TEXT DEFAULT '',
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Incidents ───────────────────────────────────────────────────────────────
CREATE TABLE incidents (
    id                     SERIAL PRIMARY KEY,
    title                  VARCHAR(255) NOT NULL,
    description            TEXT DEFAULT '',
    severity               VARCHAR(20) NOT NULL,
    status                 VARCHAR(20) NOT NULL DEFAULT 'open',
    database_instance_id   INTEGER REFERENCES database_instances(id),
    server_id              INTEGER REFERENCES servers(id),
    assigned_to_id         INTEGER REFERENCES users(id),
    reported_by_id         INTEGER REFERENCES users(id),
    created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at            TIMESTAMPTZ,
    closed_at              TIMESTAMPTZ
);
CREATE INDEX ix_incidents_status ON incidents (status);
CREATE INDEX ix_incidents_severity ON incidents (severity);
CREATE INDEX ix_incidents_created_at ON incidents (created_at);

-- ── Incident History ─────────────────────────────────────────────────────────
CREATE TABLE incident_history (
    id             SERIAL PRIMARY KEY,
    incident_id    INTEGER NOT NULL REFERENCES incidents(id),
    changed_by_id  INTEGER REFERENCES users(id),
    field_changed  VARCHAR(50) NOT NULL,
    old_value      TEXT DEFAULT '',
    new_value      TEXT DEFAULT '',
    comment        TEXT DEFAULT '',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Audit Logs ──────────────────────────────────────────────────────────────
CREATE TABLE audit_logs (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER REFERENCES users(id),
    username       VARCHAR(80) DEFAULT 'system',
    action         VARCHAR(100) NOT NULL,
    resource_type  VARCHAR(50) NOT NULL,
    resource_id    VARCHAR(50) DEFAULT '',
    description    TEXT DEFAULT '',
    ip_address     VARCHAR(45) DEFAULT '',
    user_agent     VARCHAR(255) DEFAULT '',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_audit_logs_user_id ON audit_logs (user_id);
CREATE INDEX ix_audit_logs_action ON audit_logs (action);
CREATE INDEX ix_audit_logs_created_at ON audit_logs (created_at);
CREATE INDEX ix_audit_logs_resource_type ON audit_logs (resource_type);

-- ── Login History ────────────────────────────────────────────────────────────
CREATE TABLE login_history (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER REFERENCES users(id),
    username       VARCHAR(80) NOT NULL,
    success        BOOLEAN NOT NULL,
    failure_reason VARCHAR(255) DEFAULT '',
    ip_address     VARCHAR(45) DEFAULT '',
    user_agent     VARCHAR(255) DEFAULT '',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_login_history_user_id ON login_history (user_id);
CREATE INDEX ix_login_history_created_at ON login_history (created_at);

-- ── Monitoring Metrics ──────────────────────────────────────────────────────
CREATE TABLE monitoring_metrics (
    id                   SERIAL PRIMARY KEY,
    server_id            INTEGER REFERENCES servers(id),
    database_instance_id INTEGER REFERENCES database_instances(id),
    metric_type          VARCHAR(50) NOT NULL,
    value                DOUBLE PRECISION NOT NULL,
    unit                 VARCHAR(20) DEFAULT 'percent',
    timestamp            TIMESTAMPTZ NOT NULL
);
CREATE INDEX ix_metrics_server_id ON monitoring_metrics (server_id);
CREATE INDEX ix_metrics_db_instance_id ON monitoring_metrics (database_instance_id);
CREATE INDEX ix_metrics_timestamp ON monitoring_metrics (timestamp);
CREATE INDEX ix_metrics_type ON monitoring_metrics (metric_type);

-- ── Updated At Trigger ──────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_servers_updated_at
    BEFORE UPDATE ON servers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_database_instances_updated_at
    BEFORE UPDATE ON database_instances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_backup_jobs_updated_at
    BEFORE UPDATE ON backup_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_incidents_updated_at
    BEFORE UPDATE ON incidents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
