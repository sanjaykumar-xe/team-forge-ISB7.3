"""
Team Forge Database Layer (SQLite)
----------------------------------
Zero-cost, local relational storage for:
  1. Users (Google OAuth profiles)
  2. Validation Jobs (Async background pipeline tracking & history)
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
DB_PATH = os.path.join(DB_DIR, "team_forge.db")


def get_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database with row_factory enabled."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables for users and validation jobs."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        name TEXT,
        avatar_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS validation_jobs (
        job_id TEXT PRIMARY KEY,
        user_id TEXT,
        idea_text TEXT NOT NULL,
        email TEXT NOT NULL,
        status TEXT NOT NULL, -- 'queued', 'processing', 'completed', 'failed'
        result_json TEXT,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    conn.commit()
    conn.close()


# Initialize database on module import
init_db()


def create_or_get_user(email: str, name: Optional[str] = None, avatar_url: Optional[str] = None) -> Dict[str, Any]:
    """Creates a user if not already existing, or returns the existing record."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return dict(existing)

    user_id = f"usr_{os.urandom(6).hex()}"
    cursor.execute(
        "INSERT INTO users (id, email, name, avatar_url) VALUES (?, ?, ?, ?)",
        (user_id, email, name, avatar_url)
    )
    conn.commit()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Retrieves a user by their email address."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a user by their unique ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_validation_job(job_id: str, idea_text: str, email: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Creates a new validation job with initial status 'queued'."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO validation_jobs (job_id, user_id, idea_text, email, status) VALUES (?, ?, ?, ?, 'queued')",
        (job_id, user_id, idea_text, email)
    )
    conn.commit()

    cursor.execute("SELECT * FROM validation_jobs WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def update_job_status(job_id: str, status: str, result_dict: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
    """Updates job status, result JSON, and completion timestamp."""
    conn = get_connection()
    cursor = conn.cursor()

    completed_at = datetime.utcnow().isoformat() if status in ("completed", "failed") else None
    result_json = json.dumps(result_dict) if result_dict else None

    cursor.execute("""
    UPDATE validation_jobs 
    SET status = ?, result_json = COALESCE(?, result_json), error_message = ?, completed_at = ?
    WHERE job_id = ?
    """, (status, result_json, error, completed_at, job_id))

    conn.commit()
    conn.close()


def get_job_by_id(job_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a job by its unique job_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM validation_jobs WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    if data.get("result_json"):
        try:
            data["result"] = json.loads(data["result_json"])
        except Exception:
            data["result"] = None
    return data


def get_jobs_by_user(user_id: str, email: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all past validation jobs for a user by user_id OR email, ordered newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    if email:
        cursor.execute(
            "SELECT * FROM validation_jobs WHERE user_id = ? OR email = ? ORDER BY created_at DESC",
            (user_id, email)
        )
    else:
        cursor.execute(
            "SELECT * FROM validation_jobs WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        if d.get("result_json"):
            try:
                d["result"] = json.loads(d["result_json"])
            except Exception:
                d["result"] = None
        results.append(d)
    return results
