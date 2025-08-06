import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
DB_PATH = os.path.join(BASE_DIR, "data/db/cards.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # hna 4adi ngad jadwal dyal lcard
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            last_reviewed TIMESTAMP,
            next_review TIMESTAMP,
            interval INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()