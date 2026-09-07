"""
Data access layer for QualiTrust.
Uses SQLite for simplicity; swap the connection layer for Postgres/MySQL in production.
"""
import sqlite3
from datetime import datetime
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS qualification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    holder_name TEXT NOT NULL,
    qualification_title TEXT NOT NULL,
    institution TEXT NOT NULL,
    issue_date TEXT NOT NULL,
    certificate_number TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT 'REGISTERED',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    certificate_number TEXT,
    performed_by TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    details TEXT
);
"""


def init_db(app):
    with app.app_context():
        db = get_db_standalone(app)
        db.executescript(SCHEMA)
        db.commit()
        db.close()
    app.teardown_appcontext(close_db)


def get_db_standalone(app):
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def log_action(action, certificate_number, performed_by, details=""):
    db = get_db()
    db.execute(
        "INSERT INTO audit_log (action, certificate_number, performed_by, timestamp, details) "
        "VALUES (?, ?, ?, ?, ?)",
        (action, certificate_number, performed_by, datetime.utcnow().isoformat(), details),
    )
    db.commit()
