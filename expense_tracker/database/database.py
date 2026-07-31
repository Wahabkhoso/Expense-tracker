"""
database.py
Central database connection manager for the ExpensePro application.
All modules interact with SQLite exclusively through this module.
"""

import sqlite3
import os
from contextlib import contextmanager
from database.schema import ALL_TABLES, DEFAULT_CATEGORIES

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "expense_tracker.db")


class Database:
    """Handles all raw SQLite connections and initialization."""

    def __init__(self, db_path: str = DB_PATH):
        os.makedirs(DB_DIR, exist_ok=True)
        self.db_path = db_path
        self._initialize()

    def _initialize(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")
            for statement in ALL_TABLES:
                cur.execute(statement)
            cur.execute("SELECT COUNT(*) FROM categories")
            if cur.fetchone()[0] == 0:
                cur.executemany(
                    "INSERT INTO categories (name, type) VALUES (?, ?)",
                    DEFAULT_CATEGORIES,
                )
            conn.commit()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()

    def execute(self, query: str, params: tuple = ()):
        """Execute an INSERT/UPDATE/DELETE query. Returns lastrowid."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return cur.lastrowid

    def fetch_all(self, query: str, params: tuple = ()):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    def fetch_one(self, query: str, params: tuple = ()):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None


# Singleton instance shared across the application
db = Database()
