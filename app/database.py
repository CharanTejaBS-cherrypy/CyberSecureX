import sqlite3
import os
import time

DB_PATH = os.path.join(os.path.dirname(__file__), "file_links.db")


def init_db():
    """Initialize the SQLite database and create the links table if not exists."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS links (
                token TEXT PRIMARY KEY,
                filename TEXT,
                filepath TEXT,
                expires_at REAL,
                max_downloads INTEGER,
                downloads INTEGER,
                password TEXT
            )
        """)
    print("✅ Database initialized.")


def insert_file_link(token, filename, filepath, expires_at, max_downloads, password):
    """Insert a new file sharing link into the database."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO links (token, filename, filepath, expires_at, max_downloads, downloads, password)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (token, filename, filepath, expires_at, max_downloads, 0, password))


def get_all_links():
    """Retrieve all links with their status."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT token, filename, downloads, max_downloads, expires_at FROM links
        """)
        rows = cursor.fetchall()
    return rows


def get_link_by_token(token):
    """Retrieve a single link's data by its token."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT filename, filepath, expires_at, max_downloads, downloads, password FROM links
            WHERE token = ?
        """, (token,))
        row = cursor.fetchone()
    return row


def increment_download_count(token):
    """Increment download count by 1 for a file."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            UPDATE links SET downloads = downloads + 1 WHERE token = ?
        """, (token,))


def delete_link(token):
    """Remove a file sharing link from the database."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            DELETE FROM links WHERE token = ?
        """, (token,))


def cleanup_expired_links():
    """Delete expired links and their files."""
    current_time = time.time()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT token, filepath FROM links WHERE expires_at < ?
        """, (current_time,))
        rows = cursor.fetchall()

        for token, filepath in rows:
            if os.path.exists(filepath):
                os.remove(filepath)
            delete_link(token)
