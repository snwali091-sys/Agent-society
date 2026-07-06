"""
Session Database
-----------------
A lightweight SQLite database that persists every Agent Society run.

Why this exists:
  The in-memory SharedMemory whiteboard is wiped the moment the program
  exits. This module gives Agent Society actual durable storage — every
  task, plan, research, draft, critique, and final output is saved here
  and can be reviewed later, even after restarting the program.

This satisfies the "database" component of the architecture requirement:
  Qwen Cloud → Orchestrator → Agents → SQLite Database → Frontend/API
"""

import sqlite3
import json
import os
import time
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "sessions.db")


def get_connection():
    """Opens a connection to the SQLite database, creating it if needed."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates the sessions table if it doesn't already exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            plan TEXT,
            research TEXT,
            final_output TEXT,
            rounds_completed INTEGER,
            efficiency_gain TEXT,
            conversation_log TEXT,
            created_at REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_session(task: str, plan: str, research: str, final_output: str,
                  rounds_completed: int, efficiency_gain: str,
                  conversation_log: list) -> int:
    """
    Saves a completed Agent Society run to the database.
    Returns the new session's ID.
    """
    init_db()
    conn = get_connection()
    cursor = conn.execute("""
        INSERT INTO sessions
            (task, plan, research, final_output, rounds_completed,
             efficiency_gain, conversation_log, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task, plan, research, final_output, rounds_completed,
        efficiency_gain, json.dumps(conversation_log), time.time()
    ))
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id


def get_all_sessions() -> list:
    """Returns every saved session, most recent first."""
    init_db()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM sessions ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_session(session_id: int) -> Optional[dict]:
    """Returns a single session by its ID, or None if it doesn't exist."""
    init_db()
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


if __name__ == "__main__":
    init_db()
    print(f"✅ Database initialized at: {DB_PATH}")
