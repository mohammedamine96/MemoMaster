# app/managers/card_manager.py
import sqlite3
from app.database import DB_PATH


def get_all_cards():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cards")
    rows = cursor.fetchall()

    conn.close()
    return rows


def add_card(front: str, back: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO cards (front, back) VALUES (?, ?)", (front, back))

    conn.commit()
    conn.close()


def delete_card(card_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))

    conn.commit()
    conn.close()
