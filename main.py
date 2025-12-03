import flet as ft
from database import init_db, add_deck, get_decks, add_card

def main(page: ft.Page):
    # Initialize Database
    init_db()

    page.title = "MemoMaster"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 700

    # UI Elements
    deck_name_input = ft.TextField(label="New Deck Name", width=200)
    
    def add_deck_click(e):
        if not deck_name_input.value:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter a deck name"))
            page.snack_bar.open = True
            page.update()
            return
        add_deck(deck_name_input.value)
        deck_name_input.value = ""
        refresh_decks()
        page.snack_bar = ft.SnackBar(ft.Text("Deck added!"))
        page.snack_bar.open = True
        page.update()

    deck_dropdown = ft.Dropdown(
        label="Select Deck",
        options=[],
        width=300
    )

    front_input = ft.TextField(label="Front (Question)", multiline=True, min_lines=3)
    back_input = ft.TextField(label="Back (Answer)", multiline=True, min_lines=3)

    def refresh_decks():
        decks = get_decks()
        deck_dropdown.options = [ft.dropdown.Option(key=str(d['id']), text=d['name']) for d in decks]
        page.update()

    def save_card_click(e):
        if not deck_dropdown.value:
            page.snack_bar = ft.SnackBar(ft.Text("Please select a deck"))
            page.snack_bar.open = True
            page.update()
            return
        if not front_input.value or not back_input.value:
            page.snack_bar = ft.SnackBar(ft.Text("Please fill in both sides"))
            page.snack_bar.open = True
            page.update()
            return
        
        add_card(int(deck_dropdown.value), front_input.value, back_input.value)
        
        # Clear inputs
        front_input.value = ""
        back_input.value = ""
        front_input.focus()
        
        page.snack_bar = ft.SnackBar(ft.Text("Card saved!"))
        page.snack_bar.open = True
        page.update()

    # Layout
    page.add(
        ft.Text("MemoMaster Studio", size=30, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Text("1. Create a Deck (if needed)", size=16, weight=ft.FontWeight.BOLD),
        ft.Row([deck_name_input, ft.ElevatedButton("Add Deck", on_click=add_deck_click)]),
        ft.Divider(),
        ft.Text("2. Add a Card", size=16, weight=ft.FontWeight.BOLD),
        deck_dropdown,
        front_input,
        back_input,
        ft.ElevatedButton("Save & Add Another", on_click=save_card_click, width=300)
    )

    # Initial Load
    refresh_decks()

if __name__ == "__main__":
    ft.app(target=main)
