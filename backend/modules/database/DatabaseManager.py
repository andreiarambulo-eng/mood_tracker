"""SQLite database manager with singleton pattern."""
import sqlite3
import os
import threading
from config.app import DATABASE_PATH


class DatabaseManager:
    """Thread-safe singleton SQLite database manager."""

    _instance = None
    _lock = threading.Lock()
    _local = threading.local()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._init_db()
        return cls._instance

    @classmethod
    def _get_connection(cls) -> sqlite3.Connection:
        """Get a thread-local database connection."""
        if not hasattr(cls._local, 'connection') or cls._local.connection is None:
            cls._local.connection = sqlite3.connect(DATABASE_PATH)
            cls._local.connection.row_factory = sqlite3.Row
            cls._local.connection.execute("PRAGMA journal_mode=WAL")
            cls._local.connection.execute("PRAGMA foreign_keys=ON")
        return cls._local.connection

    @classmethod
    def _init_db(cls):
        """Initialize database tables."""
        conn = cls._get_connection()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'User',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_login TEXT
            );

            CREATE TABLE IF NOT EXISTS moods (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                mood_score INTEGER NOT NULL CHECK(mood_score BETWEEN 1 AND 5),
                mood_label TEXT NOT NULL,
                remark TEXT,
                sentiment_score REAL DEFAULT 0.0,
                sentiment_label TEXT DEFAULT 'Neutral',
                logged_date TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, logged_date)
            );

            CREATE INDEX IF NOT EXISTS idx_moods_user_id ON moods(user_id);
            CREATE INDEX IF NOT EXISTS idx_moods_logged_date ON moods(logged_date);
            CREATE INDEX IF NOT EXISTS idx_moods_user_date ON moods(user_id, logged_date);
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """)
        conn.commit()
        print(f"SQLite database initialized: {DATABASE_PATH}")

    @classmethod
    def execute(cls, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return cursor."""
        conn = cls._get_connection()
        return conn.execute(query, params)

    @classmethod
    def execute_and_commit(cls, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query, commit, and return cursor."""
        conn = cls._get_connection()
        cursor = conn.execute(query, params)
        conn.commit()
        return cursor

    @classmethod
    def fetchone(cls, query: str, params: tuple = ()) -> dict | None:
        """Fetch a single row as dict."""
        cursor = cls.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    @classmethod
    def fetchall(cls, query: str, params: tuple = ()) -> list[dict]:
        """Fetch all rows as list of dicts."""
        cursor = cls.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    @classmethod
    def ping(cls) -> bool:
        """Check database connectivity."""
        try:
            cls._get_connection().execute("SELECT 1")
            return True
        except Exception:
            return False
