from database import init_db, add_deck, add_card, get_due_cards, update_card_review, get_db_connection
from sm2 import calculate_next_review
import datetime

def test_sm2_logic():
    print("Testing SM-2 Logic...")
    # Test Case 1: New card (interval 0), Good rating (4)
    # Note: Rating 4 (Good) results in 0 change to EF in standard SM-2 formula
    next_int, new_ease, due = calculate_next_review(4, 0, 2.5)
    assert next_int == 1
    assert new_ease == 2.5
    print("  Case 1 Passed")

    # Test Case 1b: Perfect rating (5) should increase EF
    next_int, new_ease, due = calculate_next_review(5, 0, 2.5)
    assert new_ease > 2.5
    print("  Case 1b Passed")

    # Test Case 2: Interval 1, Good rating (4)
    next_int, new_ease, due = calculate_next_review(4, 1, 2.5)
    assert next_int == 6
    print("  Case 2 Passed")

    # Test Case 3: Fail (rating < 3)
    next_int, new_ease, due = calculate_next_review(2, 10, 2.5)
    assert next_int == 1
    print("  Case 3 Passed")

def test_db_logic():
    print("\nTesting DB Logic...")
    init_db()
    
    # Setup
    add_deck("Study Test Deck")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM decks WHERE name = 'Study Test Deck'")
    deck_id = cursor.fetchone()['id']
    conn.close()
    
    add_card(deck_id, "Q1", "A1")
    
    # Verify Due Cards
    due_cards = get_due_cards(deck_id)
    assert len(due_cards) > 0
    card_id = due_cards[0]['id']
    print(f"  Found due card: {card_id}")
    
    # Simulate Review
    update_card_review(card_id, 1, 2.6, datetime.datetime.now() + datetime.timedelta(days=1))
    
    # Verify it's no longer due
    due_cards_after = get_due_cards(deck_id)
    # Note: It might still be due if I didn't push the date far enough into the future, 
    # but I added 1 day, so it should be fine unless test runs at 23:59:59
    assert len(due_cards_after) == 0
    print("  Card updated and no longer due immediately.")

if __name__ == "__main__":
    test_sm2_logic()
    test_db_logic()
    print("\nAll Tests Passed!")
