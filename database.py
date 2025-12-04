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

def get_decks_with_stats():
    """
    Returns a list of decks with their statistics:
    - id
    - name
    - color_code
    - total_cards
    - due_cards (count of cards where due_date <= now)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            d.id, 
            d.name, 
            d.color_code,
            COUNT(c.id) as total_cards,
            SUM(CASE WHEN c.due_date <= ? THEN 1 ELSE 0 END) as due_cards
        FROM decks d
        LEFT JOIN cards c ON d.id = c.deck_id
        GROUP BY d.id
    '''
    
    # Use current time for due date comparison
    now = datetime.datetime.now()
    
    cursor.execute(query, (now,))
    results = cursor.fetchall()
    conn.close()
    
    # Convert to list of dicts for easier handling
    decks = []
    for row in results:
        decks.append({
            "id": row["id"],
            "name": row["name"],
            "color_code": row["color_code"],
            "total_cards": row["total_cards"],
            "due_cards": row["due_cards"] if row["due_cards"] else 0
        })
    
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

def get_due_cards(deck_id):
    """Returns a list of cards due for review in the specified deck."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    
    cursor.execute('''
        SELECT * FROM cards 
        WHERE deck_id = ? AND due_date <= ?
        ORDER BY due_date ASC
    ''', (deck_id, now))
    
    cards = cursor.fetchall()
    conn.close()
    return cards

def update_card_review(card_id, interval, ease_factor, due_date):
    """Updates the card's review stats."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE cards 
        SET review_interval = ?, ease_factor = ?, due_date = ?
        WHERE id = ?
    ''', (interval, ease_factor, due_date, card_id))
    
    conn.commit()
    conn.close()

def log_study_review(card_id, quality):
    """Logs the study session result."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO study_log (card_id, quality_rating)
        VALUES (?, ?)
    ''', (card_id, quality))
    
    conn.commit()
    conn.close()
