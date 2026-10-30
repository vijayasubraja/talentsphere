"""Local-first career platform logic and SQLite persistence."""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import secrets
import smtplib
import sqlite3
from datetime import date, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("DATABASE_PATH", BASE_DIR / "data" / "talentsphere.db"))
ROLE_CATALOG: dict[str, dict[str, Any]] = {
    "Senior Software Engineer": {"skills": {"Python": 4, "System Design": 3, "SQL": 3, "Cloud": 2, "Communication": 3}, "experience": 4, "department": "Engineering", "criteria": "Owns technical design, mentors peers, and delivers reliable systems."},
    "Technical Lead": {"skills": {"System Design": 4, "Python": 4, "Leadership": 4, "Cloud": 3, "Communication": 4}, "experience": 6, "department": "Engineering", "criteria": "Leads delivery, architecture decisions, and team development."},
    "Engineering Manager": {"skills": {"Leadership": 4, "Communication": 4, "Project Management": 3, "System Design": 3}, "experience": 7, "department": "Engineering", "criteria": "Builds teams, sets direction, and improves delivery outcomes."},
    "Data Analyst": {"skills": {"SQL": 3, "Python": 2, "Data Visualization": 3, "Communication": 3}, "experience": 1, "department": "Analytics", "criteria": "Produces trusted analysis and communicates actionable insights."},
    "Senior Data Analyst": {"skills": {"SQL": 4, "Python": 3, "Data Visualization": 4, "Statistics": 3, "Communication": 4}, "experience": 4, "department": "Analytics", "criteria": "Owns analytical projects and advises stakeholders."},
    "Business Analyst": {"skills": {"Requirements Analysis": 3, "SQL": 2, "Communication": 3, "Process Improvement": 3}, "experience": 1, "department": "Business", "criteria": "Maps needs into clear requirements and measurable outcomes."},
    "Senior Business Analyst": {"skills": {"Requirements Analysis": 4, "SQL": 3, "Communication": 4, "Process Improvement": 4, "Leadership": 2}, "experience": 4, "department": "Business", "criteria": "Leads complex analysis and aligns cross-functional teams."},
    "HR Manager": {"skills": {"Talent Management": 4, "Communication": 4, "Leadership": 4, "Analytics": 3, "Employment Law": 3}, "experience": 5, "department": "Human Resources", "criteria": "Leads people programs and improves workforce outcomes."},
    "Project Manager": {"skills": {"Project Management": 4, "Communication": 4, "Risk Management": 3, "Leadership": 3}, "experience": 3, "department": "Operations", "criteria": "Delivers cross-functional projects on time, scope, and budget."},
    "SAP Consultant": {"skills": {"SAP": 4, "Requirements Analysis": 3, "Communication": 3, "Process Improvement": 3}, "experience": 2, "department": "Technology", "criteria": "Configures business systems and delivers adoption outcomes."},
}
LEVELS = {"Beginner": 1, "Intermediate": 2, "Advanced": 3, "Expert": 4}

SESSION_COOKIE_NAME = "talentsphere_remember_token"
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "talentsphere-default-session-secret-key-change-in-prod")
SESSION_LIFETIME_DAYS = int(os.getenv("SESSION_LIFETIME_DAYS", "30"))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "20"))
RESET_COOLDOWN_SECONDS = int(os.getenv("RESET_COOLDOWN_SECONDS", "60"))
GENERIC_RESET_MSG = "If an account with that email exists, password reset instructions have been sent. Please check your inbox and spam folder."


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def init_db() -> None:
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS profiles(user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE, phone TEXT DEFAULT '', location TEXT DEFAULT '', job_title TEXT DEFAULT '', department TEXT DEFAULT '', company TEXT DEFAULT '', industry TEXT DEFAULT '', employment_type TEXT DEFAULT '', years_experience REAL DEFAULT 0, summary TEXT DEFAULT '', linkedin TEXT DEFAULT '', github TEXT DEFAULT '', portfolio TEXT DEFAULT '', target_role TEXT DEFAULT '', target_level TEXT DEFAULT '', target_industry TEXT DEFAULT '', timeline TEXT DEFAULT '', career_goal TEXT DEFAULT '', education TEXT DEFAULT '', certifications TEXT DEFAULT '', projects TEXT DEFAULT '', experience TEXT DEFAULT '', resume_text TEXT DEFAULT '', updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS skills(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, name TEXT NOT NULL, category TEXT NOT NULL, proficiency TEXT NOT NULL, years REAL DEFAULT 0, UNIQUE(user_id,name));
        CREATE TABLE IF NOT EXISTS assessments(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, category TEXT NOT NULL, score INTEGER NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS progress(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, item TEXT NOT NULL, percent INTEGER NOT NULL, status TEXT NOT NULL, updated_at TEXT NOT NULL, UNIQUE(user_id,item));
        CREATE TABLE IF NOT EXISTS sessions(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, token_hash TEXT UNIQUE NOT NULL, created_at TEXT NOT NULL, expires_at TEXT NOT NULL, revoked INTEGER NOT NULL DEFAULT 0, last_used_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_sessions_token_hash ON sessions(token_hash);
        CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
        CREATE TABLE IF NOT EXISTS password_resets(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, token_hash TEXT UNIQUE NOT NULL, expires_at TEXT NOT NULL, used INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_password_resets_token_hash ON password_resets(token_hash);
        CREATE INDEX IF NOT EXISTS idx_password_resets_user_id ON password_resets(user_id);
        CREATE TABLE IF NOT EXISTS resume_drafts(user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE, resume_data TEXT NOT NULL DEFAULT '{}', selected_template TEXT NOT NULL DEFAULT 'puffin', updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS employee_work_details(
            user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            employee_id_code TEXT DEFAULT '',
            reporting_manager TEXT DEFAULT '',
            joining_date TEXT DEFAULT '',
            work_location TEXT DEFAULT '',
            department TEXT DEFAULT '',
            designation TEXT DEFAULT '',
            process_name TEXT DEFAULT '',
            process_description TEXT DEFAULT '',
            assigned_responsibilities TEXT DEFAULT '',
            short_term_goals TEXT DEFAULT '',
            long_term_goals TEXT DEFAULT '',
            expected_deliverables TEXT DEFAULT '',
            target_completion_date TEXT DEFAULT '',
            challenges_faced TEXT DEFAULT '',
            reason_for_delay TEXT DEFAULT '',
            support_required TEXT DEFAULT '',
            manager_remarks TEXT DEFAULT '',
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS employee_tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Not Started',
            progress_percent INTEGER NOT NULL DEFAULT 0,
            priority TEXT NOT NULL DEFAULT 'Medium',
            due_date TEXT DEFAULT '',
            completion_date TEXT DEFAULT '',
            completion_remarks TEXT DEFAULT '',
            work_remarks TEXT DEFAULT '',
            pending_reason TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_employee_tasks_user_id ON employee_tasks(user_id);
        """)
        demo_user = db.execute("SELECT id FROM users WHERE email='eleanor.vance@talentsphere.io'").fetchone()
        if not demo_user:
            cur = db.execute(
                "INSERT INTO users(name,email,password_hash,created_at) VALUES(?,?,?,?)",
                ("Eleanor Vance", "eleanor.vance@talentsphere.io", _password("validpassword123"), datetime.now().isoformat())
            )
            demo_uid = cur.lastrowid
        else:
            demo_uid = demo_user["id"]

        # Ensure demo profile has complete information if fields are empty
        prof_check = db.execute("SELECT summary, education FROM profiles WHERE user_id=?", (demo_uid,)).fetchone()
        if not prof_check or not prof_check["summary"]:
            try:
                from data.sample_data import SAMPLE_EMPLOYEE, SAMPLE_SKILLS
                db.execute("""
                    INSERT OR REPLACE INTO profiles(
                        user_id, phone, location, job_title, department, company, industry, employment_type,
                        years_experience, summary, linkedin, github, portfolio, target_role, target_level,
                        timeline, career_goal, education, certifications, projects, experience, updated_at
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    demo_uid,
                    SAMPLE_EMPLOYEE.get("phone", "+1 (512) 890-4421"),
                    SAMPLE_EMPLOYEE.get("location", "Austin, TX (Hybrid)"),
                    SAMPLE_EMPLOYEE.get("job_title", "Senior Cloud & DevOps Engineer"),
                    SAMPLE_EMPLOYEE.get("department", "Platform Engineering & Infrastructure"),
                    "TalentSphere Platforms Inc.",
                    "Technology & Cloud Infrastructure",
                    SAMPLE_EMPLOYEE.get("employment_type", "Full-time"),
                    float(SAMPLE_EMPLOYEE.get("years_experience", 6.5)),
                    SAMPLE_EMPLOYEE.get("summary", ""),
                    "https://linkedin.com/in/eleanor-vance",
                    "https://github.com/eleanorvance",
                    "https://eleanorvance.dev",
                    "Lead Systems Architect",
                    "Lead",
                    "9–12 Months",
                    "Transition to Principal Cloud Systems Architect by driving cloud infrastructure strategy, technical governance, and cross-team alignment.",
                    json.dumps(SAMPLE_EMPLOYEE.get("education", [])),
                    json.dumps(SAMPLE_EMPLOYEE.get("certifications", [])),
                    json.dumps([
                        {
                            "title": "Automated DevSecOps Pipeline",
                            "description": "Multi-region AWS EKS deployment with zero-downtime blue/green rollouts and automated vulnerability scanning.",
                            "technologies": "Kubernetes, Terraform, AWS, Python, GitHub Actions",
                            "contributions": "Designed automated scanning reducing deploy cycles by 65% and adopted by 35+ development squads.",
                            "url": "https://github.com/talentsphere/devsecops-pipeline"
                        },
                        {
                            "title": "Kubernetes FinOps Cost Allocation Engine",
                            "description": "Showback attribution mechanism attributing shared cluster compute costs down to individual product pods.",
                            "technologies": "Prometheus, Grafana, Python, AWS Cost Explorer",
                            "contributions": "Automated tagging and cost governance saving $180K annually in cloud infrastructure.",
                            "url": "https://github.com/talentsphere/finops-engine"
                        }
                    ]),
                    json.dumps(SAMPLE_EMPLOYEE.get("experience", [])),
                    datetime.now().isoformat()
                ))

                existing_skills = db.execute("SELECT COUNT(*) as cnt FROM skills WHERE user_id=?", (demo_uid,)).fetchone()["cnt"]
                if existing_skills == 0:
                    for s in SAMPLE_SKILLS:
                        cat = "Technical" if any(w in s.get("category", "") for w in ["Cloud", "Software", "DevOps", "Infrastructure"]) else "Soft Skill"
                        try:
                            db.execute(
                                "INSERT OR IGNORE INTO skills(user_id, name, category, proficiency, years) VALUES(?,?,?,?,?)",
                                (demo_uid, s["name"], cat, s.get("proficiency", "Intermediate"), float(s.get("years", 3.0)))
                            )
                        except Exception:
                            pass
            except Exception as exc:
                logger.warning("Could not seed demo profile from sample_data: %s", exc)

        # Seed employee work details for demo user if not present
        work_check = db.execute("SELECT user_id FROM employee_work_details WHERE user_id=?", (demo_uid,)).fetchone()
        if not work_check:
            try:
                db.execute("""
                    INSERT OR REPLACE INTO employee_work_details(
                        user_id, employee_id_code, reporting_manager, joining_date, work_location,
                        department, designation, process_name, process_description, assigned_responsibilities,
                        short_term_goals, long_term_goals, expected_deliverables, target_completion_date,
                        challenges_faced, reason_for_delay, support_required, manager_remarks, updated_at
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    demo_uid,
                    "EMP-10482",
                    "Marcus Vance (VP, Platform Engineering)",
                    "2022-03-15",
                    "Austin, TX (Hybrid)",
                    "Platform Engineering & Infrastructure",
                    "Senior Cloud & DevOps Engineer",
                    "Cloud Infrastructure Modernization & Kubernetes GitOps",
                    "Architecting and migrating multi-region Kubernetes clusters to GitOps workflows with automated security compliance and automated disaster recovery.",
                    "• Lead migration of core cluster orchestration to ArgoCD\n• Enforce zero-trust IAM policies across EKS workloads\n• Mentor junior DevOps engineers on Terraform modules\n• Maintain 99.95% cluster availability SLAs",
                    "• Finalize ArgoCD automated blue/green canary rollouts\n• Reduce CI/CD deployment cycle times by 30%\n• Implement automated daily Terraform drift detection",
                    "• Achieve ISO-27001 compliance for all platform infrastructure\n• Transition core workloads to multi-cloud active-active architecture\n• Establish self-service developer platform portal",
                    "1. Multi-cluster GitOps orchestration blueprint\n2. Real-time Prometheus/Grafana infrastructure alerting dashboards\n3. Zero-downtime rollback automation runbook",
                    "2026-12-15",
                    "Intermittent network latency during cross-region state replication and legacy service dependencies.",
                    "Awaiting security review approval for IAM cross-account role delegations.",
                    "Platform security architecture sign-off and access to staging VPC peering routes.",
                    "Eleanor is making outstanding technical progress. Meeting scheduled with Security Lead this Thursday to unblock IAM delegations.",
                    datetime.now().isoformat()
                ))
            except Exception as exc:
                logger.warning("Could not seed demo work details: %s", exc)

        # Seed initial demo tasks if empty
        task_check = db.execute("SELECT COUNT(*) as cnt FROM employee_tasks WHERE user_id=?", (demo_uid,)).fetchone()
        if not task_check or task_check["cnt"] == 0:
            try:
                demo_tasks = [
                    (
                        demo_uid,
                        "Provision EKS v1.30 Production Clusters",
                        "Set up Terraform modules for VPC, subnets, and multi-AZ EKS control plane.",
                        "Completed",
                        100,
                        "High",
                        "2026-10-10",
                        "2026-10-12",
                        "Successfully provisioned across us-east-1 and us-west-2 with zero drift.",
                        "Production rollout complete.",
                        "",
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ),
                    (
                        demo_uid,
                        "Implement HashiCorp Vault Secrets Operator",
                        "Integrate Vault agent injector with Kubernetes pod service accounts.",
                        "Completed",
                        100,
                        "Medium",
                        "2026-10-18",
                        "2026-10-20",
                        "Automated rotation verified for database credentials.",
                        "Secrets operator active in staging & prod.",
                        "",
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ),
                    (
                        demo_uid,
                        "Configure ArgoCD Multi-Cluster GitOps Pipelines",
                        "Deploy ArgoCD ApplicationSets for automated service sync and health checks.",
                        "In Progress",
                        65,
                        "High",
                        "2026-11-10",
                        "",
                        "",
                        "Core repo manifests connected; canary rollback tests currently in progress.",
                        "",
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ),
                    (
                        demo_uid,
                        "Prometheus & Grafana SLI/SLO Alerting Rules",
                        "Build latency and error-rate monitoring dashboards for critical API gateways.",
                        "In Progress",
                        40,
                        "Medium",
                        "2026-11-20",
                        "",
                        "",
                        "Grafana dashboards drafted; configuring Alertmanager PagerDuty webhook.",
                        "",
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ),
                    (
                        demo_uid,
                        "Cross-Region Disaster Recovery Automation Drill",
                        "Execute automated failover testing between primary and secondary AWS regions.",
                        "Not Started",
                        0,
                        "High",
                        "2026-12-05",
                        "",
                        "",
                        "",
                        "Dependent on completion of ArgoCD multi-cluster pipelines.",
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ),
                    (
                        demo_uid,
                        "Developer Self-Service Infrastructure Portal Runbook",
                        "Document self-service catalog templates for squad onboarding.",
                        "Not Started",
                        0,
                        "Low",
                        "2026-12-18",
                        "",
                        "",
                        "",
                        "Scheduled for sprint 24 after GitOps rollout.",
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ),
                ]
                db.executemany("""
                    INSERT INTO employee_tasks(
                        user_id, title, description, status, progress_percent, priority, due_date,
                        completion_date, completion_remarks, work_remarks, pending_reason, created_at, updated_at
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, demo_tasks)
            except Exception as exc:
                logger.warning("Could not seed demo employee tasks: %s", exc)


def _password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 240_000)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        return hmac.compare_digest(_password(password, bytes.fromhex(salt_hex)).split("$", 1)[1], digest_hex)
    except (ValueError, TypeError):
        return False


def _hash_token(raw_token: str) -> str:
    """Computes SHA-256 hash of an opaque token for database storage."""
    return hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()


def _sign_token(raw_token: str) -> str:
    """Generates an HMAC-SHA256 signature for a raw session token."""
    sig = hmac.new(SESSION_SECRET_KEY.encode("utf-8"), raw_token.strip().encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{raw_token.strip()}.{sig}"


def _verify_signed_token(signed_token: str) -> str | None:
    """Verifies HMAC signature on a session token and returns raw token, or None if invalid."""
    if not signed_token or not isinstance(signed_token, str):
        return None
    try:
        raw_token, sig = signed_token.split(".", 1)
        expected_sig = hmac.new(SESSION_SECRET_KEY.encode("utf-8"), raw_token.strip().encode("utf-8"), hashlib.sha256).hexdigest()
        if hmac.compare_digest(sig, expected_sig):
            return raw_token.strip()
        return None
    except (ValueError, TypeError):
        return None


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    """Fetches user details by primary key ID."""
    with connect() as db:
        row = db.execute("SELECT id, name, email FROM users WHERE id=?", (user_id,)).fetchone()
    return dict(row) if row else None


def get_user_by_email(email: str) -> dict[str, Any] | None:
    """Fetches user details by email address."""
    with connect() as db:
        row = db.execute("SELECT id, name, email FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    return dict(row) if row else None


def register(name: str, email: str, password: str) -> tuple[bool, str]:
    name, email = name.strip(), email.strip().lower()
    if not name or "@" not in email or len(password) < 8:
        return False, "Enter a name, valid email, and password with at least 8 characters."
    try:
        with connect() as db:
            cur = db.execute("INSERT INTO users(name,email,password_hash,created_at) VALUES(?,?,?,?)", (name, email, _password(password), datetime.now().isoformat()))
            db.execute("INSERT OR REPLACE INTO profiles(user_id,updated_at) VALUES(?,?)", (cur.lastrowid, datetime.now().isoformat()))
        return True, "Account created. You can sign in now."
    except sqlite3.IntegrityError:
        return False, "An account with that email already exists."


def login(email: str, password: str) -> dict[str, Any] | None:
    with connect() as db:
        row = db.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    if row and verify_password(password, row["password_hash"]):
        return {"id": row["id"], "name": row["name"], "email": row["email"]}
    return None


# -----------------------------------------------------------------------------
# Persistent Session Management ("Remember Me")
# -----------------------------------------------------------------------------

def create_persistent_session(user_id: int) -> str:
    """Creates a new persistent session in SQLite and returns the signed cookie token."""
    raw_token = secrets.token_urlsafe(32)
    signed_token = _sign_token(raw_token)
    token_hash = _hash_token(raw_token)
    now_iso = datetime.now().isoformat()
    expires_at = (datetime.now() + timedelta(days=SESSION_LIFETIME_DAYS)).isoformat()
    with connect() as db:
        db.execute(
            "INSERT INTO sessions(user_id, token_hash, created_at, expires_at, revoked, last_used_at) VALUES(?,?,?,?,0,?)",
            (user_id, token_hash, now_iso, expires_at, now_iso)
        )
    return signed_token


def validate_persistent_session(signed_token: str | None) -> dict[str, Any] | None:
    """Validates a signed persistent session token against SQLite.
    Returns user dict with session details if valid, or None if invalid/expired/revoked."""
    if not signed_token or not isinstance(signed_token, str):
        return None
    raw_token = _verify_signed_token(signed_token)
    if not raw_token:
        return None
    token_hash = _hash_token(raw_token)
    with connect() as db:
        row = db.execute(
            "SELECT s.*, u.name, u.email FROM sessions s JOIN users u ON s.user_id=u.id WHERE s.token_hash=? AND s.revoked=0",
            (token_hash,)
        ).fetchone()
        if not row:
            return None
        expires_at = datetime.fromisoformat(row["expires_at"])
        if datetime.now() > expires_at:
            db.execute("UPDATE sessions SET revoked=1 WHERE id=?", (row["id"],))
            return None
        # Renew last_used_at and update expiration if past midpoint
        now = datetime.now()
        now_iso = now.isoformat()
        try:
            created_dt = datetime.fromisoformat(row["created_at"])
            midpoint = created_dt + timedelta(days=SESSION_LIFETIME_DAYS / 2)
            if now > midpoint:
                new_expires = (now + timedelta(days=SESSION_LIFETIME_DAYS)).isoformat()
                db.execute("UPDATE sessions SET last_used_at=?, expires_at=? WHERE id=?", (now_iso, new_expires, row["id"]))
            else:
                db.execute("UPDATE sessions SET last_used_at=? WHERE id=?", (now_iso, row["id"]))
        except Exception:
            db.execute("UPDATE sessions SET last_used_at=? WHERE id=?", (now_iso, row["id"]))

        return {
            "id": row["user_id"],
            "name": row["name"],
            "email": row["email"],
            "session_id": row["id"],
            "raw_token": raw_token,
            "signed_token": signed_token,
        }


def revoke_session(signed_token: str | None) -> None:
    """Revokes a persistent session token in SQLite."""
    if not signed_token or not isinstance(signed_token, str):
        return
    raw_token = _verify_signed_token(signed_token)
    if not raw_token:
        try:
            raw_token = signed_token.split(".", 1)[0]
        except Exception:
            return
    token_hash = _hash_token(raw_token)
    with connect() as db:
        db.execute("UPDATE sessions SET revoked=1 WHERE token_hash=?", (token_hash,))


def revoke_all_user_sessions(user_id: int) -> None:
    """Revokes all active sessions for a user (e.g., upon password reset)."""
    with connect() as db:
        db.execute("UPDATE sessions SET revoked=1 WHERE user_id=?", (user_id,))


# -----------------------------------------------------------------------------
# Password Recovery / Reset Workflow
# -----------------------------------------------------------------------------

def send_reset_email(to_email: str, reset_url: str) -> bool:
    """Sends password reset email via SMTP with HTML/plain-text templates."""
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_sender = os.getenv("SMTP_SENDER", smtp_user or "noreply@talentsphere.io")
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
    smtp_use_ssl = os.getenv("SMTP_USE_SSL", "false").lower() in ("true", "1", "yes")

    if not smtp_host:
        logger.info("SMTP_HOST is not configured. Reset link for %s: %s", to_email, reset_url)
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reset Your TalentSphere Password"
    msg["From"] = smtp_sender
    msg["To"] = to_email

    text_body = f"""Hello,

We received a request to reset your password for TalentSphere.

Please use the following link to set a new password:
{reset_url}

This link is valid for {RESET_TOKEN_EXPIRE_MINUTES} minutes and can only be used once.

If you did not request this password reset, please ignore this email.

Best regards,
The TalentSphere Team
"""

    html_body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #F8FAFC; margin: 0; padding: 24px; color: #1E293B; }}
.card {{ max-width: 540px; margin: 0 auto; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
.header {{ font-size: 20px; font-weight: 700; color: #111827; margin-bottom: 12px; }}
.btn {{ display: inline-block; background-color: #2563EB; color: #FFFFFF !important; font-weight: 600; font-size: 14px; padding: 12px 24px; border-radius: 8px; text-decoration: none; margin: 20px 0; }}
.footer {{ font-size: 12px; color: #94A3B8; margin-top: 24px; border-top: 1px solid #F1F5F9; padding-top: 16px; }}
</style>
</head>
<body>
<div class="card">
    <div class="header">Reset Your TalentSphere Password</div>
    <p>Hello,</p>
    <p>We received a request to reset your TalentSphere account password. Click the button below to choose a new password:</p>
    <p><a href="{reset_url}" class="btn">Reset Password</a></p>
    <p style="font-size: 13px; color: #64748B;">This link is valid for <b>{RESET_TOKEN_EXPIRE_MINUTES} minutes</b> and can only be used once.</p>
    <p style="font-size: 12px; color: #94A3B8; word-break: break-all;">If the button above does not work, copy and paste this link into your browser:<br>{reset_url}</p>
    <div class="footer">If you did not request this, you can safely ignore this email. Your password will remain unchanged.</div>
</div>
</body>
</html>
"""
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        if smtp_use_ssl:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15) as server:
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.sendmail(smtp_sender, [to_email], msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                if smtp_use_tls:
                    server.starttls()
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.sendmail(smtp_sender, [to_email], msg.as_string())
        return True
    except Exception as exc:
        logger.error("Failed to send password reset email via SMTP: %s", exc)
        return False


def get_app_base_url() -> str:
    """Detects the application's base URL from environment or Streamlit runtime configuration."""
    env_url = os.getenv("APP_BASE_URL", "").strip().rstrip("/")
    if env_url:
        return env_url
    port = 8501
    try:
        import streamlit as st
        if hasattr(st, "config"):
            st_port = st.config.get_option("server.port")
            if st_port:
                port = int(st_port)
    except Exception:
        pass
    port = int(os.getenv("STREAMLIT_SERVER_PORT", os.getenv("PORT", port)))
    return f"http://localhost:{port}"


def request_password_reset(email: str) -> tuple[bool, str]:
    """Initiates a password reset for the specified email.
    Validates whether the email exists in users table. If not, returns an error.
    If registered, generates a secure single-use token, prints the reset URL in the
    server terminal where streamlit run app.py was launched, and dispatches via SMTP if configured."""
    clean_email = email.strip().lower()
    if not clean_email:
        return False, "Please enter your work email address."
    if "@" not in clean_email or "." not in clean_email:
        return False, "Please enter a valid work email address (e.g., name@company.com)."

    with connect() as db:
        user = db.execute("SELECT id, name, email FROM users WHERE email=?", (clean_email,)).fetchone()
        if not user:
            return False, "This email address is not registered. Please enter a valid registered email address."

        user_id = user["id"]
        # Rate limit checks:
        # 1. Cooldown since last request (60s)
        last_req = db.execute(
            "SELECT created_at FROM password_resets WHERE user_id=? ORDER BY id DESC LIMIT 1",
            (user_id,)
        ).fetchone()
        if last_req:
            try:
                last_time = datetime.fromisoformat(last_req["created_at"])
                if datetime.now() - last_time < timedelta(seconds=RESET_COOLDOWN_SECONDS):
                    logger.info("Rate limit hit (cooldown) for user_id=%s", user_id)
                    return False, f"A reset request was recently submitted. Please wait {RESET_COOLDOWN_SECONDS} seconds before requesting another."
            except Exception:
                pass

        # 2. Maximum 5 requests in last 15 minutes
        recent_threshold = (datetime.now() - timedelta(minutes=15)).isoformat()
        count_recent = db.execute(
            "SELECT COUNT(*) as cnt FROM password_resets WHERE user_id=? AND created_at > ?",
            (user_id, recent_threshold)
        ).fetchone()["cnt"]
        if count_recent >= 5:
            logger.info("Rate limit hit (15m window) for user_id=%s", user_id)
            return False, "Too many password reset requests. Please wait 15 minutes before trying again."

        # Generate single-use reset token
        raw_token = secrets.token_urlsafe(32)
        token_hash = _hash_token(raw_token)
        now_iso = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)).isoformat()

        db.execute(
            "INSERT INTO password_resets(user_id, token_hash, expires_at, used, created_at) VALUES(?,?,?,0,?)",
            (user_id, token_hash, expires_at, now_iso)
        )

    # Build reset link using detected base URL and port
    app_base_url = get_app_base_url()
    reset_url = f"{app_base_url}/?reset_token={raw_token}"

    # Print directly to the server terminal with flush=True so it is instantly visible
    print(f"\nPassword reset URL: {reset_url}\n", flush=True)
    logger.info("Password reset URL for %s: %s", clean_email, reset_url)

    smtp_host = os.getenv("SMTP_HOST", "").strip()
    if smtp_host:
        email_sent = send_reset_email(clean_email, reset_url)
        if email_sent:
            return True, "A password reset link has been sent to your email address. Please check your inbox."
        else:
            return True, "Password reset link generated! In development mode, check your server terminal for the reset URL."
    else:
        return True, "Password reset link generated! In development mode, check your server terminal for the reset URL."


def validate_reset_token(raw_token: str | None) -> dict[str, Any] | None:
    """Validates a password reset token.
    Returns token record with user details if valid, or None if invalid/expired/used."""
    if not raw_token or not isinstance(raw_token, str):
        return None
    token_hash = _hash_token(raw_token)
    with connect() as db:
        row = db.execute(
            "SELECT pr.*, u.name, u.email FROM password_resets pr JOIN users u ON pr.user_id=u.id WHERE pr.token_hash=?",
            (token_hash,)
        ).fetchone()
        if not row:
            return None
        if row["used"] == 1:
            return None
        if datetime.now() > datetime.fromisoformat(row["expires_at"]):
            return None
        return {
            "user_id": row["user_id"],
            "name": row["name"],
            "email": row["email"],
            "reset_id": row["id"],
            "expires_at": row["expires_at"],
        }


def reset_password(raw_token: str, new_password: str) -> tuple[bool, str]:
    """Resets the user's password using a valid reset token.
    Invalidates all outstanding reset tokens and revokes all active sessions for that user."""
    token_info = validate_reset_token(raw_token)
    if not token_info:
        return False, "This password reset link is invalid or has expired. Please request a new link."

    new_password = new_password.strip()
    if len(new_password) < 8:
        return False, "Your new password must contain at least 8 characters."
    if not (any(c.isalpha() for c in new_password) and any(c.isdigit() for c in new_password)):
        return False, "Your new password must include both letters and numbers."

    user_id = token_info["user_id"]
    new_hash = _password(new_password)

    with connect() as db:
        # Update user's password hash
        db.execute("UPDATE users SET password_hash=? WHERE id=?", (new_hash, user_id))
        # Invalidate all reset tokens for this user immediately (prevent reuse)
        db.execute("UPDATE password_resets SET used=1 WHERE user_id=?", (user_id,))
        # Revoke all persistent sessions across devices
        db.execute("UPDATE sessions SET revoked=1 WHERE user_id=?", (user_id,))

    return True, "Your password has been reset successfully. You can now sign in with your new password."


PROFILE_FIELDS = ["phone", "location", "job_title", "department", "company", "industry", "employment_type", "years_experience", "summary", "linkedin", "github", "portfolio", "target_role", "target_level", "target_industry", "timeline", "career_goal", "education", "certifications", "projects", "experience", "resume_text"]


def get_profile(user_id: int) -> dict[str, Any]:
    with connect() as db:
        row = db.execute("SELECT u.name,u.email,p.* FROM users u JOIN profiles p ON u.id=p.user_id WHERE u.id=?", (user_id,)).fetchone()
    return dict(row) if row else {}


def parse_json_field(val: Any, default: Any = None) -> Any:
    """Safely decodes JSON strings or returns list/dict structures."""
    if default is None:
        default = []
    if val is None or val == "":
        return default
    if isinstance(val, (list, dict)):
        return val
    if isinstance(val, str):
        trimmed = val.strip()
        if (trimmed.startswith("[") and trimmed.endswith("]")) or (trimmed.startswith("{") and trimmed.endswith("}")):
            try:
                return json.loads(trimmed)
            except Exception:
                pass
        if isinstance(default, list) and trimmed:
            return [{"description": line.strip()} for line in trimmed.splitlines() if line.strip()]
    return default


def update_user_account(user_id: int, name: str, email: str | None = None) -> tuple[bool, str]:
    """Updates user full name and email address in users table with uniqueness checks."""
    clean_name = name.strip()
    if not clean_name:
        return False, "Full name cannot be blank."
    with connect() as db:
        if email:
            clean_email = email.strip().lower()
            if "@" not in clean_email or "." not in clean_email:
                return False, "Please provide a valid email address."
            existing = db.execute("SELECT id FROM users WHERE email=? AND id != ?", (clean_email, user_id)).fetchone()
            if existing:
                return False, "This email address is already associated with another account."
            db.execute("UPDATE users SET name=?, email=? WHERE id=?", (clean_name, clean_email, user_id))
        else:
            db.execute("UPDATE users SET name=? WHERE id=?", (clean_name, user_id))
    return True, "User account successfully updated."


def save_profile(user_id: int, values: dict[str, Any]) -> None:
    fields = [f for f in PROFILE_FIELDS if f in values]
    if not fields:
        return
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO profiles(user_id, updated_at) VALUES(?,?)", (user_id, datetime.now().isoformat()))
        processed = []
        for f in fields:
            v = values[f]
            if isinstance(v, (list, dict)):
                v = json.dumps(v)
            processed.append(v)
        sql = ",".join(f"{f}=?" for f in fields) + ",updated_at=?"
        db.execute(f"UPDATE profiles SET {sql} WHERE user_id=?", processed + [datetime.now().isoformat(), user_id])


def get_resume_draft(user_id: int) -> dict[str, Any]:
    """Retrieves user-specific resume builder draft, prefilling from master profile if not yet saved."""
    with connect() as db:
        row = db.execute("SELECT resume_data, selected_template FROM resume_drafts WHERE user_id=?", (user_id,)).fetchone()
        if row and row["resume_data"]:
            try:
                data = json.loads(row["resume_data"])
                template = row["selected_template"] or "puffin"
                if isinstance(data, dict):
                    data.setdefault("custom_sections", [])
                    data.setdefault("achievements", [])
                    data.setdefault("references", [])
                    if "city" not in data or "country" not in data:
                        loc = data.get("location", "")
                        parts = [p.strip() for p in loc.split(",") if p.strip()]
                        data.setdefault("city", parts[0] if parts else "")
                        data.setdefault("country", parts[1] if len(parts) > 1 else "")
                    return {"resume_data": data, "selected_template": template}
            except Exception:
                pass

    user = get_user_by_id(user_id) or {}
    prof = get_profile(user_id) or {}
    sk_list = list_skills(user_id) or []

    full_name = user.get("name") or prof.get("name") or ""
    name_parts = full_name.split()
    first_name = name_parts[0] if name_parts else ""
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

    edu_raw = parse_json_field(prof.get("education", []))
    exp_raw = parse_json_field(prof.get("experience", []))
    proj_raw = parse_json_field(prof.get("projects", []))
    cert_raw = parse_json_field(prof.get("certifications", []))

    loc_str = prof.get("location", "")
    loc_parts = [p.strip() for p in loc_str.split(",") if p.strip()]
    city_val = loc_parts[0] if loc_parts else ""
    country_val = loc_parts[1] if len(loc_parts) > 1 else ""

    initial_data = {
        "first_name": first_name,
        "last_name": last_name,
        "job_title": prof.get("job_title", ""),
        "email": user.get("email") or prof.get("email", ""),
        "phone": prof.get("phone", ""),
        "location": loc_str,
        "city": city_val,
        "country": country_val,
        "linkedin": prof.get("linkedin", ""),
        "portfolio": prof.get("portfolio") or prof.get("github", ""),
        "summary": prof.get("summary", ""),
        "education": edu_raw if isinstance(edu_raw, list) else [],
        "experience": exp_raw if isinstance(exp_raw, list) else [],
        "projects": proj_raw if isinstance(proj_raw, list) else [],
        "skills": [{"name": s.get("name", ""), "category": s.get("category", "Technical"), "proficiency": s.get("proficiency", "Intermediate")} for s in sk_list] if isinstance(sk_list, list) else [],
        "certifications": cert_raw if isinstance(cert_raw, list) else [],
        "achievements": [],
        "references": [],
        "custom_sections": [],
        "languages": [{"name": "English", "proficiency": "Fluent"}],
        "job_preferences": {
            "share_with_recruiters": False,
            "desired_salary": "$120,000",
            "notice_period": "30 Days",
            "work_mode": "Hybrid",
            "hidden": False,
        },
        "filename": f"{first_name}_{last_name}_Resume".strip("_") or "Resume",
    }
    return {"resume_data": initial_data, "selected_template": "puffin"}


def save_resume_draft(user_id: int, resume_data: dict[str, Any], selected_template: str = "puffin") -> None:
    """Safely saves user's customized resume draft without modifying their master profile."""
    with connect() as db:
        db.execute(
            "INSERT OR REPLACE INTO resume_drafts(user_id, resume_data, selected_template, updated_at) VALUES (?, ?, ?, ?)",
            (user_id, json.dumps(resume_data), selected_template, datetime.now().isoformat())
        )


def list_skills(user_id: int) -> list[dict[str, Any]]:
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT * FROM skills WHERE user_id=? ORDER BY category,name", (user_id,))]


def add_skill(user_id: int, name: str, category: str, proficiency: str, years: float) -> tuple[bool, str]:
    normalized_name = name.strip()
    if not normalized_name:
        return False, "Skill name is required."
    try:
        with connect() as db:
            existing = db.execute("SELECT 1 FROM skills WHERE user_id=? AND LOWER(name)=LOWER(?)", (user_id, normalized_name)).fetchone()
            if existing:
                return False, "That skill is already in your profile."
            db.execute("INSERT INTO skills(user_id,name,category,proficiency,years) VALUES(?,?,?,?,?)", (user_id, normalized_name, category, proficiency, years))
        return True, "Skill added."
    except sqlite3.IntegrityError:
        return False, "That skill is already in your profile."


def delete_skill(user_id: int, skill_id: int) -> None:
    with connect() as db:
        db.execute("DELETE FROM skills WHERE id=? AND user_id=?", (skill_id, user_id))


def add_assessment(user_id: int, category: str, score: int) -> None:
    with connect() as db:
        db.execute("INSERT INTO assessments(user_id,category,score,created_at) VALUES(?,?,?,?)", (user_id, category, score, date.today().isoformat()))


def get_assessments(user_id: int) -> list[dict[str, Any]]:
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT * FROM assessments WHERE user_id=? ORDER BY created_at DESC", (user_id,))]


def save_progress(user_id: int, item: str, percent: int) -> None:
    with connect() as db:
        db.execute("INSERT INTO progress(user_id,item,percent,status,updated_at) VALUES(?,?,?,?,?) ON CONFLICT(user_id,item) DO UPDATE SET percent=excluded.percent,status=excluded.status,updated_at=excluded.updated_at", (user_id, item, percent, "Complete" if percent == 100 else "In progress", date.today().isoformat()))


def get_progress(user_id: int) -> list[dict[str, Any]]:
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT * FROM progress WHERE user_id=? ORDER BY item", (user_id,))]


def save_recommendation_status(user_id: int, topic: str, status: str) -> None:
    """Saves or updates tracking status for a recommendation topic in SQLite."""
    s_clean = (status or "").strip().lower()
    if s_clean in ["completed", "complete"]:
        norm_status = "Completed"
        percent = 100
    elif s_clean in ["in progress", "in_progress"]:
        norm_status = "In Progress"
        percent = 50
    else:
        norm_status = "Not Started"
        percent = 0

    item_name = topic.strip()
    with connect() as db:
        db.execute(
            """INSERT INTO progress(user_id, item, percent, status, updated_at)
               VALUES(?, ?, ?, ?, ?)
               ON CONFLICT(user_id, item) DO UPDATE SET
                   percent=excluded.percent,
                   status=excluded.status,
                   updated_at=excluded.updated_at""",
            (user_id, item_name, percent, norm_status, date.today().isoformat()),
        )


def get_recommendation_statuses(user_id: int) -> dict[str, str]:
    """Returns mapping of topic (lowercase) to normalized status."""
    mapping = {}
    with connect() as db:
        rows = db.execute("SELECT item, status FROM progress WHERE user_id=?", (user_id,)).fetchall()
        for r in rows:
            st_val = (r["status"] or "").strip().lower()
            if st_val in ["completed", "complete"]:
                norm = "Completed"
            elif st_val in ["in progress", "in_progress"]:
                norm = "In Progress"
            else:
                norm = "Not Started"
            mapping[r["item"].strip().lower()] = norm
    return mapping


def profile_completion(profile: dict[str, Any], skills: list[dict[str, Any]]) -> tuple[int, list[str]]:
    checks = {"Phone and location": bool(profile.get("phone") and profile.get("location")), "Current role and employer": bool(profile.get("job_title") and profile.get("company")), "Professional summary": bool(profile.get("summary")), "Education": bool(profile.get("education")), "Skills": bool(skills), "Experience": bool(profile.get("experience")), "Certifications": bool(profile.get("certifications")), "Projects": bool(profile.get("projects")), "Career goal and target role": bool(profile.get("career_goal") and profile.get("target_role")), "Professional link": bool(profile.get("linkedin") or profile.get("github") or profile.get("portfolio")), "Resume content": bool(profile.get("resume_text"))}
    missing = [label for label, done in checks.items() if not done]
    return round(100 * (len(checks) - len(missing)) / len(checks)), missing


def calculate_profile_completion_details(profile: dict[str, Any], skills: list[dict[str, Any]], user: dict[str, Any] | None = None) -> dict[str, Any]:
    """Dynamically calculates weighted profile completion percentage and section breakdown.
    
    Sensible weights:
    - Personal Information: 15% (Name, Email, Phone, Location)
    - Professional Summary: 15% (Job Title / Headline, Summary text)
    - Education: 15% (At least 1 valid education entry)
    - Work Experience: 15% (At least 1 valid experience entry)
    - Projects: 15% (At least 1 valid project entry)
    - Skills & Certifications: 15% (Skills recorded: 8%, Certifications: 7%)
    - Career Goals: 10% (Target Role: 5%, Career Goal: 5%)
    Total = 100%. Optional fields (LinkedIn, Portfolio) do not penalize users.
    """
    user_info = user or {}
    name = (user_info.get("name") or profile.get("name") or "").strip()
    email = (user_info.get("email") or profile.get("email") or "").strip()
    phone = (profile.get("phone") or "").strip()
    location = (profile.get("location") or "").strip()

    # 1. Personal Information (15%)
    personal_missing = []
    if not name:
        personal_missing.append("Full Name")
    if not email or "@" not in email:
        personal_missing.append("Email Address")
    if not phone:
        personal_missing.append("Phone Number")
    if not location:
        personal_missing.append("Location")
    personal_complete = len(personal_missing) == 0
    personal_weight = 15 if personal_complete else round(15 * (4 - len(personal_missing)) / 4)

    # 2. Professional Summary (15%)
    summary_missing = []
    job_title = (profile.get("job_title") or "").strip()
    summary = (profile.get("summary") or "").strip()
    if not job_title:
        summary_missing.append("Headline / Job Title")
    if not summary or len(summary) < 15:
        summary_missing.append("Professional Summary")
    summary_complete = len(summary_missing) == 0
    summary_weight = 15 if summary_complete else round(15 * (2 - len(summary_missing)) / 2)

    # 3. Education (15%)
    edu_list = parse_json_field(profile.get("education", []))
    edu_valid = [e for e in edu_list if (isinstance(e, dict) and ((e.get("institution") or "").strip() or (e.get("degree") or "").strip())) or (isinstance(e, str) and e.strip() and e.strip() not in ("[]", "{}"))]
    edu_complete = len(edu_valid) > 0
    edu_weight = 15 if edu_complete else 0

    # 4. Work Experience (15%)
    exp_list = parse_json_field(profile.get("experience", []))
    exp_valid = [e for e in exp_list if (isinstance(e, dict) and ((e.get("company") or "").strip() or (e.get("role") or "").strip())) or (isinstance(e, str) and e.strip() and e.strip() not in ("[]", "{}"))]
    exp_complete = len(exp_valid) > 0
    exp_weight = 15 if exp_complete else 0

    # 5. Projects (15%)
    proj_list = parse_json_field(profile.get("projects", []))
    proj_valid = [p for p in proj_list if (isinstance(p, dict) and (p.get("title") or "").strip()) or (isinstance(p, str) and p.strip() and p.strip() not in ("[]", "{}"))]
    proj_complete = len(proj_valid) > 0
    proj_weight = 15 if proj_complete else 0

    # 6. Skills & Certifications (15%)
    has_skills = bool(skills and len(skills) > 0)
    cert_list = parse_json_field(profile.get("certifications", []))
    cert_valid = [c for c in cert_list if (isinstance(c, dict) and ((c.get("name") or "").strip() or (c.get("issuer") or "").strip())) or (isinstance(c, str) and c.strip() and c.strip() not in ("[]", "{}"))]
    has_certs = len(cert_valid) > 0
    skills_certs_weight = (8 if has_skills else 0) + (7 if has_certs else 0)
    skills_certs_complete = has_skills and has_certs

    # 7. Career Goals (10%)
    target_role = (profile.get("target_role") or "").strip()
    career_goal = (profile.get("career_goal") or "").strip()
    goals_missing = []
    if not target_role:
        goals_missing.append("Target Role")
    if not career_goal:
        goals_missing.append("Career Goal")
    goals_complete = len(goals_missing) == 0
    goals_weight = (5 if target_role else 0) + (5 if career_goal else 0)

    total_score = min(100, max(0, personal_weight + summary_weight + edu_weight + exp_weight + proj_weight + skills_certs_weight + goals_weight))

    sections_status = [
        {
            "name": "Personal Information",
            "complete": personal_complete,
            "weight": personal_weight,
            "max_weight": 15,
            "missing": personal_missing,
            "suggestion": "Add your phone number and location so recruiters and hiring managers can reach you." if personal_missing else "Contact details are complete."
        },
        {
            "name": "Professional Summary",
            "complete": summary_complete,
            "weight": summary_weight,
            "max_weight": 15,
            "missing": summary_missing,
            "suggestion": "Write a concise professional summary highlighting your core strengths and domain leadership." if summary_missing else "Summary is clearly articulated."
        },
        {
            "name": "Education",
            "complete": edu_complete,
            "weight": edu_weight,
            "max_weight": 15,
            "missing": ["Degree & Institution"] if not edu_complete else [],
            "suggestion": "Add your academic degrees, colleges, or universities under Education." if not edu_complete else "Education entries recorded."
        },
        {
            "name": "Work Experience",
            "complete": exp_complete,
            "weight": exp_weight,
            "max_weight": 15,
            "missing": ["Work Experience Roles"] if not exp_complete else [],
            "suggestion": "Document your past roles, companies, and key achievements." if not exp_complete else "Work history is documented."
        },
        {
            "name": "Projects",
            "complete": proj_complete,
            "weight": proj_weight,
            "max_weight": 15,
            "missing": ["Practical Projects"] if not proj_complete else [],
            "suggestion": "Showcase at least one hands-on project with technologies used and quantifiable results." if not proj_complete else "Project evidence is available."
        },
        {
            "name": "Skills & Certifications",
            "complete": skills_certs_complete,
            "weight": skills_certs_weight,
            "max_weight": 15,
            "missing": (["Technical/Soft Skills"] if not has_skills else []) + (["Industry Certifications"] if not has_certs else []),
            "suggestion": "Add your core skills and verified industry certifications." if not skills_certs_complete else "Skills and credentials recorded."
        },
        {
            "name": "Career Goals",
            "complete": goals_complete,
            "weight": goals_weight,
            "max_weight": 10,
            "missing": goals_missing,
            "suggestion": "Select a target role and describe your career aspirations to activate calibrated role matching." if goals_missing else "Target role and direction defined."
        },
    ]

    completed_sections = [s["name"] for s in sections_status if s["complete"]]
    incomplete_sections = [s["name"] for s in sections_status if not s["complete"]]
    suggested_actions = [s["suggestion"] for s in sections_status if not s["complete"]]

    return {
        "percentage": total_score,
        "sections": sections_status,
        "completed_sections": completed_sections,
        "incomplete_sections": incomplete_sections,
        "suggested_actions": suggested_actions,
    }


def get_career_growth_suggestions(profile: dict[str, Any], skills: list[dict[str, Any]], user_id: int | None = None) -> list[dict[str, Any]]:
    """Analyzes profile, skills, and target role requirements to identify actionable drawbacks and growth suggestions."""
    target_role = (profile.get("target_role") or "").strip()
    spec = ROLE_CATALOG.get(target_role)

    progress_map = {}
    if user_id:
        try:
            for p in get_progress(user_id):
                progress_map[p["item"].strip().lower()] = p["status"]
        except Exception:
            pass

    assessment_categories = set()
    if user_id:
        try:
            for a in get_assessments(user_id):
                assessment_categories.add(a.get("category", "").strip().lower())
        except Exception:
            pass

    suggestions = []

    def get_status_for(title: str, topic: str = "", default: str = "Not started") -> str:
        t_low = title.strip().lower()
        top_low = topic.strip().lower() if topic else ""
        for cand in [top_low, t_low]:
            if cand and cand in progress_map:
                v = progress_map[cand]
                v_clean = v.strip().lower()
                if v_clean in ["completed", "complete"]:
                    return "Completed"
                elif v_clean in ["in progress", "in_progress"]:
                    return "In Progress"
                elif v_clean in ["not started", "not_started"]:
                    return "Not Started"
                return v
        for k, v in progress_map.items():
            if (top_low and (k in top_low or top_low in k)) or (k in t_low or t_low in k):
                v_clean = v.strip().lower()
                if v_clean in ["completed", "complete"]:
                    return "Completed"
                elif v_clean in ["in progress", "in_progress"]:
                    return "In Progress"
                elif v_clean in ["not started", "not_started"]:
                    return "Not Started"
                return v
        return default

    if spec:
        required_skills = spec.get("skills", {})
        required_exp = spec.get("experience", 2)
        current_skills_map = {s["name"].strip().lower(): LEVELS.get(s.get("proficiency"), 1) for s in skills}

        # 1. Missing Required Skills
        for skill_name, req_level in required_skills.items():
            s_low = skill_name.lower()
            if s_low not in current_skills_map:
                prio = "High" if req_level >= 3 else "Medium"
                req_title = f"Develop {skill_name}"
                level_names = {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Expert"}
                suggestions.append({
                    "topic": skill_name,
                    "item_key": f"skill_missing_{s_low}",
                    "title": req_title,
                    "gap": f"Missing required capability: {skill_name}",
                    "why": f"{target_role} expects Level {req_level} ({level_names.get(req_level, 'Advanced')}) in {skill_name} for production delivery.",
                    "action": f"Add {skill_name} to your skills inventory and undertake practical exercises to build hands-on competency.",
                    "priority": prio,
                    "status": get_status_for(req_title, skill_name),
                    "category": "Skill Gap"
                })

        # 2. Skill Proficiency Under-threshold
        for skill_name, req_level in required_skills.items():
            s_low = skill_name.lower()
            if s_low in current_skills_map:
                curr_level = current_skills_map[s_low]
                if curr_level < req_level:
                    gap_amt = req_level - curr_level
                    prio = "High" if gap_amt >= 2 else "Medium"
                    req_title = f"Advance {skill_name} proficiency"
                    level_names = {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Expert"}
                    curr_name = level_names.get(curr_level, "Beginner")
                    target_name = level_names.get(req_level, "Advanced")
                    suggestions.append({
                        "topic": skill_name,
                        "item_key": f"skill_advance_{s_low}",
                        "title": req_title,
                        "gap": f"{skill_name} proficiency is {curr_name} (Level {curr_level}), below target {target_name} (Level {req_level}).",
                        "why": f"Operating effectively as a {target_role} requires deeper practical mastery in {skill_name}.",
                        "action": f"Take on challenging tasks involving {skill_name} or mentor colleagues on architecture to reach {target_name}.",
                        "priority": prio,
                        "status": get_status_for(req_title, skill_name),
                        "category": "Skill Gap"
                    })

        # 3. Unassessed Skills
        if skills and not assessment_categories:
            title = "Complete skill competency assessments"
            top_cat = "Skill Assessments"
            suggestions.append({
                "topic": top_cat,
                "item_key": "assessment_baseline",
                "title": title,
                "gap": "Skills are self-reported without verified competency assessment records.",
                "why": "Completing assessments verifies your ratings and increases readiness score accuracy.",
                "action": "Complete a self-assessment in Technical or Problem Solving to validate your ratings.",
                "priority": "Medium",
                "status": get_status_for(title, top_cat),
                "category": "Assessment"
            })

        # 4. Project Evidence
        projects = parse_json_field(profile.get("projects", []))
        if not projects:
            title = f"Document a practical project for {target_role}"
            top_techs = ", ".join(list(required_skills.keys())[:3])
            top_proj = "Practical Projects"
            suggestions.append({
                "topic": top_proj,
                "item_key": "project_evidence_missing",
                "title": title,
                "gap": f"No practical project evidence recorded demonstrating {target_role} competencies.",
                "why": "Hiring managers and mentors evaluate concrete project deliverables over listed skills.",
                "action": f"Add a project showcasing {top_techs} with clear architectural scope and measurable outcomes.",
                "priority": "High",
                "status": get_status_for(title, top_proj),
                "category": "Project Evidence"
            })
        else:
            all_proj_text = " ".join([
                f"{p.get('title','')} {p.get('description','')} {p.get('technologies','')} {p.get('contributions','')}"
                for p in projects if isinstance(p, dict)
            ]).lower()
            missing_in_projects = [s for s in required_skills if s.lower() not in all_proj_text]
            if len(missing_in_projects) > len(required_skills) / 2:
                title = f"Strengthen project descriptions with {target_role} tooling"
                top_proj = "Practical Projects"
                suggestions.append({
                    "topic": top_proj,
                    "item_key": "project_tech_alignment",
                    "title": title,
                    "gap": f"Current project descriptions do not clearly highlight core tools like {', '.join(missing_in_projects[:2])}.",
                    "why": "Applicant tracking systems and reviewers search for explicit evidence of required technologies.",
                    "action": "Update your project entries to specify the tech stack and quantify your architectural contributions.",
                    "priority": "Medium",
                    "status": get_status_for(title, top_proj),
                    "category": "Project Evidence"
                })

        # 5. Work Experience / Tenure
        years_exp = float(profile.get("years_experience", 0) or 0)
        experiences = parse_json_field(profile.get("experience", []))
        if years_exp < required_exp or not experiences:
            title = f"Build relevant experience toward {required_exp}+ years"
            top_exp = "Relevant Experience"
            suggestions.append({
                "topic": top_exp,
                "item_key": "experience_tenure_gap",
                "title": title,
                "gap": f"Recorded experience is {years_exp} years (role benchmark: {required_exp}+ years).",
                "why": f"{target_role} roles typically expect proven organizational delivery over {required_exp} or more years.",
                "action": "Document all previous technical internships, open-source projects, and contracted deliverables to demonstrate tenure.",
                "priority": "Medium" if years_exp > 0 else "High",
                "status": get_status_for(title, top_exp),
                "category": "Experience"
            })

        # 6. Professional Summary Alignment
        summary_text = (profile.get("summary") or "").lower()
        if target_role.lower() not in summary_text:
            title = f"Align professional summary with {target_role}"
            top_sum = "Professional Summary"
            suggestions.append({
                "topic": top_sum,
                "item_key": "summary_alignment",
                "title": title,
                "gap": f"Your executive summary does not explicitly mention your target trajectory toward {target_role}.",
                "why": "A focused summary immediately sets expectations for mentors and hiring committees.",
                "action": f"Revise your summary to state your experience and express your active advancement toward {target_role}.",
                "priority": "Medium",
                "status": get_status_for(title, top_sum),
                "category": "Profile Alignment"
            })

        # 7. Portfolio URL
        if not profile.get("portfolio") and not profile.get("github"):
            title = "Add portfolio or code repository link"
            top_port = "Portfolio & Code Links"
            suggestions.append({
                "topic": top_port,
                "item_key": "portfolio_link_missing",
                "title": title,
                "gap": "No public portfolio or GitHub URL linked on your profile.",
                "why": "Public project repositories and portfolios provide tangible proof of work for technical roles.",
                "action": "Add your GitHub profile or personal portfolio URL under Personal Information.",
                "priority": "Low",
                "status": get_status_for(title, top_port),
                "category": "Portfolio"
            })

        # 8. Industry Certifications
        certs = parse_json_field(profile.get("certifications", []))
        if not certs:
            title = f"Attain an industry certification relevant to {target_role}"
            top_cert = "Industry Certifications"
            suggestions.append({
                "topic": top_cert,
                "item_key": "certification_missing",
                "title": title,
                "gap": "No verified industry certifications or accreditations recorded.",
                "why": "Accredited credentials demonstrate formalized commitment and validated foundational standards.",
                "action": f"Identify a recognized certification in your discipline (e.g. Cloud, Architecture, or Professional certification) to boost credibility.",
                "priority": "Low",
                "status": get_status_for(title, top_cert),
                "category": "Certifications"
            })

    else:
        title_role = "Select a target career role"
        top_role = "Target Career Role"
        suggestions.append({
            "topic": top_role,
            "item_key": "target_role_unset",
            "title": title_role,
            "gap": "No target career role selected in your profile.",
            "why": "A target role is necessary to calculate skill gaps, readiness score, and benchmark requirements.",
            "action": "Go to Career Goals in My Profile and select your target role (e.g. Senior Software Engineer, Technical Lead).",
            "priority": "High",
            "status": get_status_for(title_role, top_role),
            "category": "Target Role"
        })

        if not profile.get("summary"):
            title_s = "Draft your executive summary"
            top_s = "Professional Summary"
            suggestions.append({
                "topic": top_s,
                "item_key": "summary_unset",
                "title": title_s,
                "gap": "Professional summary is blank.",
                "why": "Your summary is the first section read by reviewers and ATS scanners.",
                "action": "Write 2-4 sentences describing your current capabilities, notable achievements, and interests.",
                "priority": "High",
                "status": get_status_for(title_s, top_s),
                "category": "Profile Alignment"
            })

        if not skills:
            title_sk = "Add your core skills"
            top_sk = "Core Skills"
            suggestions.append({
                "topic": top_sk,
                "item_key": "skills_unset",
                "title": title_sk,
                "gap": "No skills recorded in your profile inventory.",
                "why": "Recorded skills form the foundation for career matching and growth roadmaps.",
                "action": "Add your primary technical and soft skills with self-rated proficiencies.",
                "priority": "High",
                "status": get_status_for(title_sk, top_sk),
                "category": "Skill Gap"
            })

    return suggestions


def gap_analysis(target_role: str, skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    required = ROLE_CATALOG.get(target_role, {}).get("skills", {})
    current = {s["name"].strip().lower(): LEVELS.get(s["proficiency"], 1) for s in skills}
    result = []
    for skill, level in required.items():
        have = current.get(skill.lower(), 0)
        gap = max(0, level - have)
        result.append({"skill": skill, "current": have, "required": level, "gap": gap, "priority": "High" if gap >= 2 else "Medium" if gap == 1 else "On track"})
    return sorted(result, key=lambda x: x["gap"], reverse=True)


def recommendations(profile: dict[str, Any], skills: list[dict[str, Any]]) -> list[dict[str, str]]:
    completion, missing = profile_completion(profile, skills)
    gaps = gap_analysis(profile.get("target_role", ""), skills)
    items = []
    if completion < 80:
        items.append({"priority": "High", "title": "Complete your professional profile", "description": f"Add the missing sections: {', '.join(missing[:4])}. This gives the career matching engine better evidence."})
    for gap in gaps:
        if gap["gap"]:
            items.append({"priority": gap["priority"], "title": f"Develop {gap['skill']}", "description": f"Your target role expects level {gap['required']}; your recorded level is {gap['current']}. Choose a practical project or learning path to build evidence."})
    if not profile.get("resume_text"):
        items.append({"priority": "Medium", "title": "Create a role-aligned resume", "description": "Use your profile details to draft an ATS-friendly resume and add measurable outcomes drawn from your actual work."})
    if not items:
        items.append({"priority": "Medium", "title": "Build evidence for your next step", "description": "Document a recent project with scope, your contribution, and measurable impact. Revisit your target role quarterly."})
    return items[:8]


def profile_analysis(profile: dict[str, Any], skills: list[dict[str, Any]]) -> dict[str, Any]:
    completion, missing = profile_completion(profile, skills)
    gaps = gap_analysis(profile.get("target_role", ""), skills)
    strength = min(100, round(completion * .55 + min(len(skills) * 4, 24) + (12 if profile.get("summary") else 0) + (9 if profile.get("experience") else 0)))
    strengths = []
    if skills: strengths.append(f"A skills profile with {len(skills)} recorded capabilities")
    if profile.get("experience"): strengths.append("Work history is documented")
    if profile.get("projects"): strengths.append("Project evidence is available")
    if not strengths: strengths.append("A clear opportunity to build a complete career baseline")
    weaknesses = [f"Missing profile evidence: {', '.join(missing[:3])}"] if missing else []
    weaknesses += [f"{g['skill']} is {g['gap']} level(s) below target" for g in gaps if g["gap"]][:3]
    return {"score": strength, "completion": completion, "strengths": strengths, "weaknesses": weaknesses or ["Keep adding recent evidence and measurable outcomes."], "recommendations": [r["title"] for r in recommendations(profile, skills)[:4]]}


def role_match(target_role: str, skills: list[dict[str, Any]], years: float = 0) -> int:
    spec = ROLE_CATALOG.get(target_role)
    if not spec: return 0
    required = spec["skills"]
    levels = {str(s["name"]).strip().lower(): LEVELS.get(s["proficiency"], 1) for s in skills}
    fit = sum(min(levels.get(name.strip().lower(), 0), level) / level for name, level in required.items()) / max(1, len(required))
    exp_fit = min(1, years / max(1, spec["experience"]))
    return round(100 * (fit * .85 + exp_fit * .15))


def export_user_data(user_id: int) -> dict[str, Any]:
    profile = get_profile(user_id)
    with connect() as db:
        user = db.execute("SELECT name,email,created_at FROM users WHERE id=?", (user_id,)).fetchone()
    return {"employee": dict(user) if user else {}, "profile": profile, "skills": list_skills(user_id), "assessments": get_assessments(user_id), "progress": get_progress(user_id), "generated_at": datetime.now().isoformat()}


# =============================================================================
# Employee Work Process, Goals, and Task Progress Tracking Services
# =============================================================================

def get_employee_work_details(user_id: int) -> dict[str, Any]:
    """Retrieves employee work details, process, and goals from SQLite with safe fallbacks."""
    with connect() as db:
        row = db.execute("SELECT * FROM employee_work_details WHERE user_id=?", (user_id,)).fetchone()
        user_row = db.execute("SELECT name, email FROM users WHERE id=?", (user_id,)).fetchone()
        prof_row = db.execute("SELECT job_title, department, location, years_experience FROM profiles WHERE user_id=?", (user_id,)).fetchone()

    u_name = user_row["name"] if user_row else "Employee"
    u_email = user_row["email"] if user_row else ""
    p_title = prof_row["job_title"] if prof_row and prof_row["job_title"] else "Senior Professional"
    p_dept = prof_row["department"] if prof_row and prof_row["department"] else "Engineering & Operations"
    p_loc = prof_row["location"] if prof_row and prof_row["location"] else "Hybrid Office"
    p_exp = float(prof_row["years_experience"] or 0) if prof_row else 5.0

    if row:
        d = dict(row)
        d["name"] = u_name
        d["email"] = u_email
        d["years_experience"] = p_exp
        if not d.get("designation"):
            d["designation"] = p_title
        if not d.get("department"):
            d["department"] = p_dept
        if not d.get("work_location"):
            d["work_location"] = p_loc
        if not d.get("employee_id_code"):
            d["employee_id_code"] = f"EMP-{user_id:04d}"
        return d

    return {
        "user_id": user_id,
        "name": u_name,
        "email": u_email,
        "employee_id_code": f"EMP-{user_id:04d}",
        "reporting_manager": "Marcus Vance (VP, Platform Engineering)",
        "joining_date": date.today().isoformat(),
        "work_location": p_loc,
        "department": p_dept,
        "designation": p_title,
        "years_experience": p_exp,
        "process_name": "Core Business Process & System Modernization",
        "process_description": "Managing workflow optimization and deliverables.",
        "assigned_responsibilities": "• Deliver assigned sprint tasks\n• Maintain high delivery quality\n• Collaborate with team members",
        "short_term_goals": "• Complete active deliverables on time\n• Improve sprint execution cycle time",
        "long_term_goals": "• Drive organizational process improvements\n• Achieve quarterly performance targets",
        "expected_deliverables": "• Production-ready deliverables\n• Process documentation and test reports",
        "target_completion_date": (date.today() + timedelta(days=60)).isoformat(),
        "challenges_faced": "",
        "reason_for_delay": "",
        "support_required": "",
        "manager_remarks": "",
        "updated_at": datetime.now().isoformat(),
    }


def save_employee_work_details(user_id: int, values: dict[str, Any]) -> None:
    """Persists employee work process, goals, and organizational details to SQLite."""
    now_iso = datetime.now().isoformat()
    fields = [
        "employee_id_code", "reporting_manager", "joining_date", "work_location",
        "department", "designation", "process_name", "process_description",
        "assigned_responsibilities", "short_term_goals", "long_term_goals",
        "expected_deliverables", "target_completion_date", "challenges_faced",
        "reason_for_delay", "support_required", "manager_remarks"
    ]
    with connect() as db:
        exists = db.execute("SELECT user_id FROM employee_work_details WHERE user_id=?", (user_id,)).fetchone()
        if exists:
            upd_fields = [f for f in fields if f in values]
            if upd_fields:
                sql = ", ".join(f"{f}=?" for f in upd_fields) + ", updated_at=?"
                params = [values[f] for f in upd_fields] + [now_iso, user_id]
                db.execute(f"UPDATE employee_work_details SET {sql} WHERE user_id=?", params)
        else:
            cols = ["user_id"] + [f for f in fields if f in values] + ["updated_at"]
            placeholders = ", ".join(["?"] * len(cols))
            params = [user_id] + [values[f] for f in fields if f in values] + [now_iso]
            db.execute(f"INSERT INTO employee_work_details({', '.join(cols)}) VALUES({placeholders})", params)


def get_employee_tasks(user_id: int, status_filter: str | None = None) -> list[dict[str, Any]]:
    """Retrieves all tasks for the given employee, ensuring tenant isolation."""
    with connect() as db:
        if status_filter:
            rows = db.execute(
                "SELECT * FROM employee_tasks WHERE user_id=? AND status=? ORDER BY id DESC",
                (user_id, status_filter)
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM employee_tasks WHERE user_id=? ORDER BY id DESC",
                (user_id,)
            ).fetchall()
    return [dict(r) for r in rows]


def get_employee_task(task_id: int, user_id: int) -> dict[str, Any] | None:
    """Fetches a specific employee task while verifying user ownership."""
    with connect() as db:
        row = db.execute("SELECT * FROM employee_tasks WHERE id=? AND user_id=?", (task_id, user_id)).fetchone()
    return dict(row) if row else None


def add_employee_task(user_id: int, task_data: dict[str, Any]) -> int:
    """Creates a new employee task record in SQLite."""
    title = (task_data.get("title") or "").strip()
    if not title:
        raise ValueError("Task title is required.")
    status = task_data.get("status", "Not Started")
    if status not in ("Not Started", "In Progress", "Completed"):
        status = "Not Started"
    progress = int(task_data.get("progress_percent", 0) or 0)
    if status == "Completed":
        progress = 100
    elif status == "In Progress" and progress == 0:
        progress = 25
    priority = task_data.get("priority", "Medium")
    if priority not in ("High", "Medium", "Low"):
        priority = "Medium"
    due_date = str(task_data.get("due_date", "") or "").strip()
    comp_date = str(task_data.get("completion_date", "") or "").strip()
    if status == "Completed" and not comp_date:
        comp_date = date.today().isoformat()
    now_iso = datetime.now().isoformat()

    with connect() as db:
        cur = db.execute("""
            INSERT INTO employee_tasks(
                user_id, title, description, status, progress_percent, priority,
                due_date, completion_date, completion_remarks, work_remarks, pending_reason,
                created_at, updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            user_id,
            title,
            (task_data.get("description") or "").strip(),
            status,
            progress,
            priority,
            due_date,
            comp_date,
            (task_data.get("completion_remarks") or "").strip(),
            (task_data.get("work_remarks") or "").strip(),
            (task_data.get("pending_reason") or "").strip(),
            now_iso,
            now_iso
        ))
        return cur.lastrowid


def update_employee_task(task_id: int, user_id: int, task_data: dict[str, Any]) -> bool:
    """Updates an existing employee task without creating duplicate records."""
    with connect() as db:
        row = db.execute("SELECT * FROM employee_tasks WHERE id=? AND user_id=?", (task_id, user_id)).fetchone()
        if not row:
            return False

        allowed = [
            "title", "description", "status", "progress_percent", "priority",
            "due_date", "completion_date", "completion_remarks", "work_remarks", "pending_reason"
        ]
        upd = {}
        for k in allowed:
            if k in task_data:
                upd[k] = task_data[k]

        if upd.get("status") == "Completed":
            upd["progress_percent"] = 100
            if not upd.get("completion_date"):
                upd["completion_date"] = date.today().isoformat()
        elif upd.get("status") == "Not Started":
            upd["progress_percent"] = 0
            upd["completion_date"] = ""
        elif upd.get("status") == "In Progress":
            if upd.get("progress_percent", row["progress_percent"]) == 100:
                upd["progress_percent"] = 50
            upd["completion_date"] = ""

        if not upd:
            return True

        upd["updated_at"] = datetime.now().isoformat()
        sql = ", ".join(f"{k}=?" for k in upd.keys())
        params = list(upd.values()) + [task_id, user_id]
        db.execute(f"UPDATE employee_tasks SET {sql} WHERE id=? AND user_id=?", params)
        return True


def update_task_status(task_id: int, user_id: int, new_status: str, progress_percent: int | None = None, remarks: str | None = None) -> bool:
    """Updates task status and categorizes tasks automatically without creating duplicates."""
    if new_status not in ("Not Started", "In Progress", "Completed"):
        return False

    with connect() as db:
        row = db.execute("SELECT * FROM employee_tasks WHERE id=? AND user_id=?", (task_id, user_id)).fetchone()
        if not row:
            return False

        now_iso = datetime.now().isoformat()
        comp_date = row["completion_date"] or ""
        prog = progress_percent if progress_percent is not None else row["progress_percent"]

        if new_status == "Completed":
            prog = 100
            if not comp_date:
                comp_date = date.today().isoformat()
            if remarks:
                db.execute(
                    "UPDATE employee_tasks SET status=?, progress_percent=?, completion_date=?, completion_remarks=?, updated_at=? WHERE id=? AND user_id=?",
                    (new_status, prog, comp_date, remarks, now_iso, task_id, user_id)
                )
            else:
                db.execute(
                    "UPDATE employee_tasks SET status=?, progress_percent=?, completion_date=?, updated_at=? WHERE id=? AND user_id=?",
                    (new_status, prog, comp_date, now_iso, task_id, user_id)
                )
        elif new_status == "In Progress":
            if prog == 0 or prog == 100:
                prog = 25
            comp_date = ""
            if remarks:
                db.execute(
                    "UPDATE employee_tasks SET status=?, progress_percent=?, completion_date=?, work_remarks=?, updated_at=? WHERE id=? AND user_id=?",
                    (new_status, prog, comp_date, remarks, now_iso, task_id, user_id)
                )
            else:
                db.execute(
                    "UPDATE employee_tasks SET status=?, progress_percent=?, completion_date=?, updated_at=? WHERE id=? AND user_id=?",
                    (new_status, prog, comp_date, now_iso, task_id, user_id)
                )
        else:  # Not Started
            prog = 0
            comp_date = ""
            if remarks:
                db.execute(
                    "UPDATE employee_tasks SET status=?, progress_percent=?, completion_date=?, pending_reason=?, updated_at=? WHERE id=? AND user_id=?",
                    (new_status, prog, comp_date, remarks, now_iso, task_id, user_id)
                )
            else:
                db.execute(
                    "UPDATE employee_tasks SET status=?, progress_percent=?, completion_date=?, updated_at=? WHERE id=? AND user_id=?",
                    (new_status, prog, comp_date, now_iso, task_id, user_id)
                )
        return True


def delete_employee_task(task_id: int, user_id: int) -> bool:
    """Deletes an employee task verifying ownership."""
    with connect() as db:
        cur = db.execute("DELETE FROM employee_tasks WHERE id=? AND user_id=?", (task_id, user_id))
        return cur.rowcount > 0


def calculate_work_metrics(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculates overall work progress metrics and completion percentage.
    Formula: Completion Percentage = (Completed Tasks / Total Assigned Tasks) * 100
    Handles zero tasks safely to avoid division-by-zero.
    """
    total = len(tasks)
    completed = len([t for t in tasks if t.get("status") == "Completed"])
    in_progress = len([t for t in tasks if t.get("status") == "In Progress"])
    pending = len([t for t in tasks if t.get("status") == "Not Started"])
    completion_pct = round((completed / total) * 100, 1) if total > 0 else 0.0
    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "in_progress_tasks": in_progress,
        "pending_tasks": pending,
        "completion_percentage": completion_pct,
    }


def get_work_suggestions(user_id: int, work_details: dict[str, Any], tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generates 6 dynamic work-related suggestions based on actual employee task and progress info."""
    today = date.today()
    saved_statuses = get_recommendation_statuses(user_id)

    total = len(tasks)
    completed = [t for t in tasks if t.get("status") == "Completed"]
    in_prog = [t for t in tasks if t.get("status") == "In Progress"]
    pending = [t for t in tasks if t.get("status") == "Not Started"]

    overdue_tasks = []
    upcoming_tasks = []
    for t in tasks:
        if t.get("status") != "Completed" and t.get("due_date"):
            try:
                d = date.fromisoformat(str(t["due_date"])[:10])
                delta = (d - today).days
                if delta < 0:
                    overdue_tasks.append((t, abs(delta)))
                elif 0 <= delta <= 14:
                    upcoming_tasks.append((t, delta))
            except Exception:
                pass

    # 1. Overdue Task Notifications
    if overdue_tasks:
        first_od, days_od = overdue_tasks[0]
        od_text = f"Task '{first_od['title']}' is {days_od} day(s) past its due date ({first_od['due_date']}). Review impediments in Challenges & Support or adjust the deadline."
        od_prio = "High"
    else:
        od_text = "No overdue tasks detected. All active deliverables are operating within their scheduled timelines."
        od_prio = "Low"

    # 2. Upcoming Deadline Alerts
    if upcoming_tasks:
        first_up, days_up = upcoming_tasks[0]
        up_text = f"Task '{first_up['title']}' is due in {days_up} day(s) ({first_up['due_date']}). Current progress is at {first_up.get('progress_percent', 0)}%."
        up_prio = "High" if days_up <= 3 else "Medium"
    else:
        up_text = "No immediate task deadlines within the next 14 days. Review future milestone allocations in Section B."
        up_prio = "Low"

    # 3. Pending Task Reminders
    if pending:
        high_pend = [t for t in pending if t.get("priority") == "High"]
        target_pend = high_pend[0] if high_pend else pending[0]
        pend_text = f"{len(pending)} task(s) are yet to be started. Priority item '{target_pend['title']}' ({target_pend.get('priority', 'Medium')} Priority) is awaiting kickoff."
        pend_prio = "High" if high_pend else "Medium"
    else:
        pend_text = "All assigned tasks have been kicked off or completed. Continue monitoring in-progress cycle times."
        pend_prio = "Low"

    # 4. Productivity Improvement Suggestions
    if len(in_prog) > 3:
        prod_text = f"You have {len(in_prog)} tasks concurrently in progress. High concurrent WIP causes context switching. Focus on finishing 1–2 items before starting new ones."
        prod_prio = "High"
    elif total > 0 and (len(completed) / total) >= 0.75:
        prod_text = f"Strong delivery velocity! {len(completed)} of {total} tasks ({round((len(completed)/total)*100)}%) completed. Review upcoming sprint goals with your manager."
        prod_prio = "Low"
    elif in_prog:
        lowest_prog = min(in_prog, key=lambda x: x.get("progress_percent", 0))
        prod_text = f"Task '{lowest_prog['title']}' is currently at {lowest_prog.get('progress_percent', 0)}% progress. Allocate focused sprint blocks to advance this deliverable."
        prod_prio = "Medium"
    else:
        prod_text = "Maintain structured daily execution blocks and ensure work remarks and milestones are updated regularly."
        prod_prio = "Low"

    # 5. Process Improvement Recommendations
    proc_name = work_details.get("process_name") or "Current Process"
    target_dt = work_details.get("target_completion_date", "")
    challs = (work_details.get("challenges_faced") or "").strip()
    if challs:
        snippet = (challs[:70] + "...") if len(challs) > 70 else challs
        proc_text = f"Active challenge recorded: '{snippet}'. Request management alignment to unblock cross-functional dependencies."
        proc_prio = "High"
    elif target_dt:
        proc_text = f"Process '{proc_name}' target completion date is {target_dt}. Validate that remaining deliverables align with this schedule."
        proc_prio = "Medium"
    else:
        proc_text = "Keep expected deliverables and assigned responsibilities in Section B calibrated with sprint goals."
        proc_prio = "Low"

    # 6. Goal Completion Suggestions
    st_goals = (work_details.get("short_term_goals") or "").strip()
    completion_rate = round((len(completed) / total * 100)) if total > 0 else 0
    if total > 0:
        goal_text = f"Overall work progress is at {completion_rate}%. Complete remaining in-progress deliverables to fulfill target short-term milestones."
        goal_prio = "Medium" if completion_rate < 50 else "Low"
    elif st_goals:
        goal_text = "Short-term goals are defined. Convert them into specific, actionable tasks in Section C to track milestone attainment."
        goal_prio = "High"
    else:
        goal_text = "Define short-term and long-term goals in Section B to calibrate task management priorities and deliverables."
        goal_prio = "Medium"

    items = [
        {"topic": "Overdue Task Notification", "category": "Schedule", "priority": od_prio, "action": od_text, "item_key": "overdue_notification"},
        {"topic": "Upcoming Deadline Alert", "category": "Deadline", "priority": up_prio, "action": up_text, "item_key": "deadline_alert"},
        {"topic": "Pending Task Reminder", "category": "Task Alert", "priority": pend_prio, "action": pend_text, "item_key": "pending_reminder"},
        {"topic": "Productivity Improvement Suggestion", "category": "Productivity", "priority": prod_prio, "action": prod_text, "item_key": "productivity_suggestion"},
        {"topic": "Process Improvement Recommendation", "category": "Process", "priority": proc_prio, "action": proc_text, "item_key": "process_recommendation"},
        {"topic": "Goal Completion Suggestion", "category": "Goals", "priority": goal_prio, "action": goal_text, "item_key": "goal_completion_suggestion"},
    ]

    for item in items:
        clean_key = item["topic"].strip().lower()
        stat = saved_statuses.get(clean_key, "Not Started")
        item["status"] = stat
        item["gap"] = item["action"]

    return items

