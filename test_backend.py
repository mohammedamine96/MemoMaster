from database import init_db, add_deck, get_decks, add_card, get_db_connection

def test_backend():
    print("Testing Backend...")
    init_db()
    
    # Test Adding Deck
    print("Adding Deck 'Python'...")
    add_deck("Python")
    
    decks = get_decks()
    assert len(decks) > 0
    python_deck = next((d for d in decks if d['name'] == 'Python'), None)
    assert python_deck is not None
    print(f"Deck 'Python' found with ID: {python_deck['id']}")
    
    # Test Adding Card
    print("Adding Card to 'Python' deck...")
    add_card(python_deck['id'], "print('Hello')", "Prints Hello to console")
    
    # Verify Card
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cards WHERE deck_id = ?", (python_deck['id'],))
    cards = cursor.fetchall()
    conn.close()
    
    assert len(cards) > 0
    print(f"Card added successfully. Front: {cards[0]['front_content']}")
    print("Backend Test Passed!")

if __name__ == "__main__":
    test_backend()
