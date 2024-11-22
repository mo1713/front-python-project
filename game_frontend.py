from generate_db import db
from nicegui import ui
from game_backend import GameLogic, ReviewLogic


class GameUI:
    def __init__(self,game_logic):
        self.game_logic = game_logic
        self.container = None
        self.mode_container = None
        self.game_controls = None
        self.game_interface = None
        self.review_section = None
        self.score_label = None
        self.word_display = None
        self.input_box = None
        self.hint_label = None
        self.review_count_label = None
        self.card_content = None
        self.flashcard = None

    def setup_ui(self):
        # Add back button to homepage
        with ui.column().classes('w-full'):
            self._create_header()
            self._create_mode_selection()
            self._create_game_controls()
            self._create_game_interface()

    def _create_header(self):
        ui.label("Word Scamble Game").classes('text-2xl text-pink-600 font-bold mb-4')
        with ui.row().classes('gap-4 mb-4'):
            ui.button("Self Album", on_click=lambda: self.show_mode_options('album')).classes('bg-pink-600 hover:bg-pink-800')
            ui.button("Flashcard Topic", on_click=lambda: self.show_mode_options('topic')).classes('bg-pink-600 hover:bg-pink-800 ')

    def _create_mode_selection(self):
        self.mode_container = ui.column().classes('w-full mb-4')

    def _create_game_controls(self):
        self.game_controls = ui.column().classes('w-full mb-4')
        with self.game_controls:
            ui.button("Start", on_click=self.start_new_game).classes('bg-pink-500')
            ui.button("Replay", on_click=self.reset_game).classes('bg-pink-500')
        self.game_controls.set_visibility(False)

    def _create_game_interface(self):
        self.game_interface = ui.column().classes('w-full')
        with self.game_interface:
            self.score_label = ui.label(f"Score: 0").classes('text-lg mb-2')
            self.word_display = ui.label().classes('text-xl mb-2')
            self.hint_label = ui.label().classes('text-sm text-gray-500 mb-2')
            
            with ui.row().classes('gap-2'):
                self.input_box = ui.input(placeholder='Enter word...').classes('w-64')
                ui.button("Check", on_click=self.check_word).classes('bg-pink-500')
                ui.button("Skip", on_click=self.skip_word).classes('bg-pink-500')
                ui.button("Finish", on_click=self.game_logic.save_review_album).classes('bg-pink-500')
        self.game_interface.set_visibility(False)


    def show_mode_options(self, mode):
        self.mode_container.clear()
        with self.mode_container:
            options = (list(self.game_logic.get_albums().keys()) if mode == 'album' 
                      else list(self.game_logic.get_topics()))
            
            if mode == 'album' and not options:
                ui.label("").classes('text-red-500')
                return

            ui.select(
                label="Choose " + ("album" if mode == 'album' else "topic"),
                options=options,
                on_change=lambda e: self.on_source_change(e.value, mode == 'album')
            ).classes('w-full max-w-xs mb-4 ')

    def on_source_change(self, source, is_album):
        if self.game_logic.set_word_source(source, is_album):
            self.game_controls.set_visibility(True)
            self.game_interface.set_visibility(False)
            self.review_section.set_visibility(True)
            self.update_review_section(True)

    def start_new_game(self):
        scrambled_word, word_length = self.game_logic.get_next_word()
        if not scrambled_word:
            ui.notify("Please choose a word source", color="warning")
            return
        
        self.game_interface.set_visibility(True)
        self.word_display.set_text(f"Rearrange: {scrambled_word}")
        self.hint_label.set_text(f"Length of word: {word_length} charaters")
        self.input_box.value = ""

    def check_word(self):
        is_correct, result = self.game_logic.check_answer(self.input_box.value.strip())
        if result == "empty":
            ui.notify("Please enter word", color="warning")
        elif is_correct:
            ui.notify("Correct! +1 point", color="success")
            self.score_label.set_text(f"Score: {self.game_logic.score}")
            
        else:
            ui.notify(f"Wrong! Correct answer: {result}", color="error")
            
        self.start_new_game()

    def skip_word(self):
        correct_word = self.game_logic.skip_current_word()
        ui.notify(f"Correct word: {correct_word}", color="warning")
        self.start_new_game()

    def reset_game(self):
        self.game_logic.reset_game()
        self.score_label.set_text("Score: 0")
        self.start_new_game()
    



class ReviewUI:
    def __init__(self, review_logic):
        self.review_logic = review_logic
        self.review_count_label = None  # Define attributes early to avoid potential errors
        self.card_content = None
        self.flashcard = None
        #self.review_section.set_visibility(False)
        self.update_review_section()
        self._create_review_section()  
        
        # Add your review interface here
    def _create_review_section(self):
        self.review_section = ui.column().classes('w-full mt-4')
        with self.review_section:
            ui.label("Revision").classes('text-2xl text-pink-600 font-bold mb-2')
            self.review_count_label = ui.label().classes('text-sm text-gray-600 mb-2')
            
            self.flashcard = ui.card().classes('w-full h-48 cursor-pointer mb-4')
            with self.flashcard:
                self.card_content = ui.label().classes('text-xl text-center w-full h-full flex items-center justify-center')
            59+88
            with ui.row().classes('w-full justify-center gap-4'):
                ui.button('←', on_click=self.prev_card).classes('bg-pink-500')
                ui.button('Flip', on_click=self.flip_card).classes('bg-pink-500')
                ui.button('→', on_click=self.next_card).classes('bg-pink-500')
            
            with ui.row().classes('w-full justify-center gap-4 mt-4'):
                ui.button('Remembered', on_click=self.mark_as_remembered).classes('bg-pink-500')
                ui.button('Not remember yet', on_click=self.next_card).classes('bg-pink-500')
                ui.button('Finish Revision', on_click = self.review_logic.save_review_album).classes('bg-pink-500')
        #self.review_section.set_visibility(False)
        self.update_review_section()
    
    def update_review_section(self):
        if self.review_count_label:
            count = self.review_logic.get_review_count()
            self.review_count_label.set_text(f'{count} revision word left')
    
        if self.card_content and self.flashcard:
            card_content = self.review_logic.get_current_card()
            if card_content:
                self.card_content.set_text(card_content)
                self.flashcard.style('background-color: white; color: pink')
            else:
                self.card_content.set_text("No revision word left")


    def flip_card(self):
        self.review_logic.flip_card()
        self.update_review_section()

    def next_card(self):
        self.review_logic.next_card()
        self.update_review_section()

    def prev_card(self):
        self.review_logic.prev_card()
        self.update_review_section()

    def mark_as_remembered(self):
        removed_word = self.review_logic.mark_as_remembered()
        if removed_word:
            ui.notify(f'Removed "{removed_word}" from revision word list', color="success")
            self.update_review_section()



class Gamefront:
    def __init__(self):
        self.game_logic = GameLogic()
        self.review_logic = ReviewLogic()

    def setup_home_page(self):
        with ui.column().classes('w-full max-w-3xl mx-auto p-4'):
            with ui.row().classes('w-full items-center gap-4 mb-6'):
                ui.icon('school', size='32px').classes('text-pink-600')
                ui.label('GAME').classes('text-2xl font-bold text-pink-600') 
            
            with ui.row().style('justify-content: center; margin: 10px 0;gap: 10px; flex-wrap: wrap;'): 
                ui.link('Game', '/game').classes(
                    'w-full bg-pink-600 hover:bg-pink-800 text-white font-semibold py-2 rounded-lg shadow-md text-center no-underline'
                )
                ui.link('Review', '/review').classes(
                    'w-full bg-pink-600 hover:bg-pink-800 text-white font-semibold py-2 rounded-lg shadow-md text-center no-underline'
                )

    def setup_game_page(self):
        with ui.column().classes('w-full max-w-3xl mx-auto p-4'):
            game_ui = GameUI(self.game_logic)
            game_ui.setup_ui()

    def setup_review_page(self):
        with ui.column().classes('w-full max-w-3xl mx-auto p-4'):
            # Nếu có từ để ôn tập từ game, truyền vào
            if self.game_logic.review_album:
                self.review_logic.set_review_words(self.game_logic.review_album)
            
            review_ui = ReviewUI(self.review_logic)
            review_ui.setup_ui()

    def register_routes(self):
        # Đăng ký các route cho ứng dụng
        @ui.page('/')
        def home():
            self.setup_home_page()

        @ui.page('/game')
        def game():
            self.setup_game_page()

        @ui.page('/review')
        def review():
            self.setup_review_page()

# Khởi chạy ứng dụng
def start_app():
    app = Gamefront()
    app.register_routes()
    ui.run()

# Sử dụng
if __name__ in {"__main__", "__mp_main__"}:
    start_app()
