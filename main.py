import flet as ft
import datetime
from database import init_db, add_deck, get_decks_with_stats, add_card, get_due_cards, update_card_review, log_study_review
from sm2 import calculate_next_review

def main(page: ft.Page):
    # Initialize Database
    init_db()

    page.title = "MemoMaster"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 700
    page.padding = 20

    # --- State ---
    decks = []
    current_study_cards = []
    current_card_index = 0
    is_showing_answer = False

    # --- UI Components ---
    
    def get_dashboard_header(total_due):
        return ft.Container(
            content=ft.Column([
                ft.Text("Hello, Student!", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(f"You have {total_due} cards due today.", size=16, color=ft.colors.GREY_700),
            ]),
            padding=ft.padding.only(bottom=20)
        )

    def get_deck_item(deck):
        due_count = deck['due_cards']
        total_count = deck['total_cards']
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(deck['name'], size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Text(f"{due_count} due", color=ft.colors.WHITE, size=12),
                            bgcolor=ft.colors.RED_400 if due_count > 0 else ft.colors.GREEN_400,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=10,
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.ProgressBar(value=0 if total_count == 0 else (total_count - due_count) / total_count, color=deck['color_code'], bgcolor=ft.colors.GREY_200),
                    ft.Text(f"{total_count} cards total", size=12, color=ft.colors.GREY_500)
                ]),
                padding=15,
                on_click=lambda e: start_study_session(deck['id'])
            )
        )

    # --- Study Mode UI ---
    study_container = ft.Column(expand=True, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    def show_answer(e):
        nonlocal is_showing_answer
        is_showing_answer = True
        update_study_view()

    def rate_card(quality):
        nonlocal current_card_index, is_showing_answer
        
        card = current_study_cards[current_card_index]
        
        # Calculate SM-2
        next_interval, new_ease, next_due = calculate_next_review(
            quality, 
            card['review_interval'], 
            card['ease_factor']
        )
        
        # Update DB
        update_card_review(card['id'], next_interval, new_ease, next_due)
        log_study_review(card['id'], quality)
        
        # Move to next card
        current_card_index += 1
        is_showing_answer = False
        
        if current_card_index >= len(current_study_cards):
            finish_study_session()
        else:
            update_study_view()

    def update_study_view():
        study_container.controls.clear()
        
        if current_card_index >= len(current_study_cards):
            finish_study_session()
            return

        card = current_study_cards[current_card_index]
        
        # Progress
        study_container.controls.append(
            ft.Text(f"Card {current_card_index + 1} / {len(current_study_cards)}", color=ft.colors.GREY_500)
        )
        
        # Front (Question)
        study_container.controls.append(
            ft.Container(
                content=ft.Text(card['front_content'], size=24, text_align=ft.TextAlign.CENTER),
                padding=40,
                alignment=ft.alignment.center,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=10,
                width=350,
                height=200,
                margin=ft.margin.only(bottom=20)
            )
        )
        
        if not is_showing_answer:
            study_container.controls.append(
                ft.ElevatedButton("Show Answer", on_click=show_answer, width=200, height=50)
            )
        else:
            # Back (Answer)
            study_container.controls.append(
                ft.Container(
                    content=ft.Text(card['back_content'], size=20, text_align=ft.TextAlign.CENTER),
                    padding=40,
                    alignment=ft.alignment.center,
                    bgcolor=ft.colors.GREY_100,
                    border_radius=10,
                    width=350,
                    margin=ft.margin.only(bottom=20)
                )
            )
            
            # Rating Buttons
            study_container.controls.append(
                ft.Row([
                    ft.ElevatedButton("Again", on_click=lambda e: rate_card(0), bgcolor=ft.colors.RED_400, color=ft.colors.WHITE),
                    ft.ElevatedButton("Hard", on_click=lambda e: rate_card(3), bgcolor=ft.colors.ORANGE_400, color=ft.colors.WHITE),
                    ft.ElevatedButton("Good", on_click=lambda e: rate_card(4), bgcolor=ft.colors.BLUE_400, color=ft.colors.WHITE),
                    ft.ElevatedButton("Easy", on_click=lambda e: rate_card(5), bgcolor=ft.colors.GREEN_400, color=ft.colors.WHITE),
                ], alignment=ft.MainAxisAlignment.CENTER)
            )
            
        page.update()

    def start_study_session(deck_id):
        nonlocal current_study_cards, current_card_index, is_showing_answer
        current_study_cards = get_due_cards(deck_id)
        
        if not current_study_cards:
            page.snack_bar = ft.SnackBar(ft.Text("No cards due for this deck!"))
            page.snack_bar.open = True
            page.update()
            return

        current_card_index = 0
        is_showing_answer = False
        
        page.clean()
        page.add(
            ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: return_to_dashboard()),
            study_container
        )
        update_study_view()

    def finish_study_session():
        page.clean()
        page.add(
            ft.Column([
                ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN, size=100),
                ft.Text("Session Complete!", size=30, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("Back to Dashboard", on_click=lambda e: return_to_dashboard())
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
        )
        page.update()

    def return_to_dashboard():
        page.clean()
        page.add(
            dashboard_view,
            ft.FloatingActionButton(icon=ft.icons.ADD, on_click=open_add_deck_dialog)
        )
        refresh_dashboard()

    # --- Dialogs ---
    new_deck_name = ft.TextField(label="Deck Name", autofocus=True)
    
    def close_dialog(e):
        add_deck_dialog.open = False
        page.update()

    def create_deck(e):
        if not new_deck_name.value:
            return
        add_deck(new_deck_name.value)
        new_deck_name.value = ""
        add_deck_dialog.open = False
        refresh_dashboard()

    add_deck_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Create New Deck"),
        content=new_deck_name,
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.TextButton("Create", on_click=create_deck),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_add_deck_dialog(e):
        page.dialog = add_deck_dialog
        add_deck_dialog.open = True
        page.update()

    # --- Main Layout ---
    dashboard_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    
    def refresh_dashboard():
        nonlocal decks
        decks = get_decks_with_stats()
        
        total_due = sum(d['due_cards'] for d in decks)
        
        dashboard_view.controls.clear()
        dashboard_view.controls.append(get_dashboard_header(total_due))
        
        for deck in decks:
            dashboard_view.controls.append(get_deck_item(deck))
            
        page.update()

    page.add(
        dashboard_view,
        ft.FloatingActionButton(icon=ft.icons.ADD, on_click=open_add_deck_dialog)
    )

    # Initial Load
    refresh_dashboard()

if __name__ == "__main__":
    ft.app(target=main)
