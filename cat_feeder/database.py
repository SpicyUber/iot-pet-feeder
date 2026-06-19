import sqlite3
from datetime import datetime

DB_PATH = "feeder.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rfid_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_id TEXT UNIQUE NOT NULL,
            name TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_scan TIMESTAMP,
            scan_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def tag_exists(tag_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM rfid_tags WHERE tag_id = ?", (tag_id,)).fetchone()
    conn.close()
    return row is not None


def register_tag(tag_id, name=None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO rfid_tags (tag_id, name, registered_at) VALUES (?, ?, ?)",
        (tag_id, name, datetime.now()),
    )
    conn.commit()
    conn.close()


def update_scan(tag_id):
    conn = get_connection()
    conn.execute(
        "UPDATE rfid_tags SET last_scan = ?, scan_count = scan_count + 1 WHERE tag_id = ?",
        (datetime.now(), tag_id),
    )
    conn.commit()
    conn.close()


def get_all_tags():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rfid_tags ORDER BY registered_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_tag(tag_id):
    conn = get_connection()
    conn.execute("DELETE FROM rfid_tags WHERE tag_id = ?", (tag_id,))
    conn.commit()
    conn.close()


def set_name(tag_id, name):
    conn = get_connection()
    conn.execute("UPDATE rfid_tags SET name = ? WHERE tag_id = ?", (name, tag_id))
    conn.commit()
    conn.close()
