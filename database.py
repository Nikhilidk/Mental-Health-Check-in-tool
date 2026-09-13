import sqlite3

DB_PATH = "data/entries.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            text TEXT,
            neg REAL,
            neu REAL,
            pos REAL,
            compound REAL,
            entry_length INTEGER
        )
    """)
    conn.commit()
    conn.close()

def add_entry(date, text, neg, neu, pos, compound, entry_length):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO entries (date, text, neg, neu, pos, compound, entry_length) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (date, text, neg, neu, pos, compound, entry_length)
    )
    conn.commit()
    conn.close()

def get_all_entries():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT * FROM entries ORDER BY date")
    rows = cursor.fetchall()
    conn.close()
    return rows
def delete_entry(entry_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()