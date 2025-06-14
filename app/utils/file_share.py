import time
import uuid
import os
import sqlite3

DB_PATH = "app/database/file_links.db"
UPLOADS_DIR = "app/uploads"

# ------------------- Initialize DB -------------------


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS links (
                token TEXT PRIMARY KEY,
                filename TEXT,
                filepath TEXT,
                expires_at REAL,
                max_downloads INTEGER,
                downloads INTEGER,
                password TEXT
            )
        ''')

# ------------------- Save Uploaded File -------------------


def save_file(file, expiry_minutes, max_downloads, password=None):
    token = str(uuid.uuid4())
    filename = file.filename
    filepath = f"{UPLOADS_DIR}/{token}_{filename}"

    os.makedirs(UPLOADS_DIR, exist_ok=True)

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    expires_at = time.time() + expiry_minutes * 60

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            INSERT INTO links (token, filename, filepath, expires_at, max_downloads, downloads, password)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (token, filename, filepath, expires_at, max_downloads, 0, password))

    return token

# ------------------- Retrieve Link Info -------------------


def get_link(token):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT filename, filepath, expires_at, max_downloads, downloads, password
            FROM links
            WHERE token=?
        ''', (token,))
        return cur.fetchone()

# ------------------- Update Downloads -------------------


def increment_downloads(token):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            UPDATE links SET downloads = downloads + 1 WHERE token=?
        ''', (token,))

# ------------------- Delete Expired or Exhausted Links -------------------


def delete_link(token):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('DELETE FROM links WHERE token=?', (token,))
