import sqlite3
import datetime

DB_NAME = "data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database with the required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Table: Decks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            color_code TEXT
        )
    ''')

    # 2. Table: Cards
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER,
            front_content TEXT NOT NULL,
            back_content TEXT NOT NULL,
            image_path TEXT,
            review_interval INTEGER DEFAULT 0,
            ease_factor REAL DEFAULT 2.5,
            due_date TIMESTAMP,
            FOREIGN KEY (deck_id) REFERENCES decks (id)
        )
    ''')

    # 3. Table: StudyLog
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER,
            date_reviewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            quality_rating INTEGER,
            FOREIGN KEY (card_id) REFERENCES cards (id)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database {DB_NAME} initialized successfully.")

def add_deck(name, color_code="#2196F3"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO decks (name, color_code) VALUES (?, ?)", (name, color_code))
    conn.commit()
    conn.close()

def get_decks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM decks")
    decks = cursor.fetchall()
    conn.close()
    return decks

def add_card(deck_id, front, back):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Default values for new cards
    review_interval = 0
    ease_factor = 2.5
    due_date = datetime.datetime.now()
    
    cursor.execute('''
        INSERT INTO cards (deck_id, front_content, back_content, review_interval, ease_factor, due_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (deck_id, front, back, review_interval, ease_factor, due_date))
    conn.commit()
    conn.close()
