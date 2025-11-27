import sqlite3

DB_FILE = "rfq_ai.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            subject TEXT,
            received_at TEXT,
            classified_as TEXT,
            raw_body TEXT
        )
    """)

    conn.commit()
    conn.close()
