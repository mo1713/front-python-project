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
        with ui.row().classes('w-full items-center gap-4 mb-6'):
            ui.link(
                '/'
            ).classes('text-pink-600')
            ui.label('Word Scramble Game').classes('text-2xl font-bold text-pink-600')

        with ui.column().classes('w-full'):
            self._create_header()
            self._create_mode_selection()
            self._create_game_controls()
            self._create_game_interface()

    def _create_header(self):
        ui.label("Trò Chơi Sắp Xếp Lại Từ").classes('text-3xl font-bold mb-4')
        with ui.row().classes('gap-4 mb-4'):
            ui.button("Album của tôi", on_click=lambda: self.show_mode_options('album')).classes('bg-blue-500')
            ui.button("Chủ đề có sẵn", on_click=lambda: self.show_mode_options('topic')).classes('bg-green-500')

    def _create_mode_selection(self):
        self.mode_container = ui.column().classes('w-full mb-4')

    def _create_game_controls(self):
        self.game_controls = ui.column().classes('w-full mb-4')
        with self.game_controls:
            ui.button("Bắt đầu", on_click=self.start_new_game).classes('bg-green-500')
            ui.button("Chơi lại", on_click=self.reset_game).classes('bg-yellow-500')
        self.game_controls.set_visibility(False)

    def _create_game_interface(self):
        self.game_interface = ui.column().classes('w-full')
        with self.game_interface:
            self.score_label = ui.label(f"Điểm: 0").classes('text-lg mb-2')
            self.word_display = ui.label().classes('text-xl mb-2')
            self.hint_label = ui.label().classes('text-sm text-gray-500 mb-2')
            
            with ui.row().classes('gap-2'):
                self.input_box = ui.input(placeholder='Nhập từ của bạn...').classes('w-64')
                ui.button("Kiểm tra", on_click=self.check_word).classes('bg-blue-500')
                ui.button("Bỏ qua", on_click=self.skip_word).classes('bg-gray-500')
                ui.button("Kết thúc Game", on_click=self.game_logic.save_review_album).classes('bg-gray-500')
        self.game_interface.set_visibility(False)


    def show_mode_options(self, mode):
        self.mode_container.clear()
        with self.mode_container:
            options = (list(self.game_logic.get_albums().keys()) if mode == 'album' 
                      else list(self.game_logic.get_topics()))
            
            if mode == 'album' and not options:
                ui.label("Bạn chưa có album nào").classes('text-red-500')
                return

            ui.select(
                label="Chọn " + ("album" if mode == 'album' else "chủ đề"),
                options=options,
                on_change=lambda e: self.on_source_change(e.value, mode == 'album')
            ).classes('w-full max-w-xs mb-4')

    def on_source_change(self, source, is_album):
        if self.game_logic.set_word_source(source, is_album):
            self.game_controls.set_visibility(True)
            self.game_interface.set_visibility(False)
            self.review_section.set_visibility(True)
            self.update_review_section(True)

    def start_new_game(self):
        scrambled_word, word_length = self.game_logic.get_next_word()
        if not scrambled_word:
            ui.notify("Vui lòng chọn nguồn từ vựng", color="warning")
            return
        
        self.game_interface.set_visibility(True)
        self.word_display.set_text(f"Sắp xếp lại: {scrambled_word}")
        self.hint_label.set_text(f"Độ dài: {word_length} ký tự")
        self.input_box.value = ""

    def check_word(self):
        is_correct, result = self.game_logic.check_answer(self.input_box.value.strip())
        if result == "empty":
            ui.notify("Vui lòng nhập từ", color="warning")
        elif is_correct:
            ui.notify("Chính xác! +1 điểm", color="success")
            self.score_label.set_text(f"Điểm: {self.game_logic.score}")
            
        else:
            ui.notify(f"Sai rồi! Đáp án đúng: {result}", color="error")
            
        self.start_new_game()

    def skip_word(self):
        correct_word = self.game_logic.skip_current_word()
        ui.notify(f"Từ đúng là: {correct_word}", color="warning")
        self.start_new_game()

    def reset_game(self):
        self.game_logic.reset_game()
        self.score_label.set_text("Điểm: 0")
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
        
    def setup_ui(self):
        with ui.row().classes('w-full items-center gap-4 mb-6'):
            ui.link( 
                '/'
            ).classes('text-pink-600')
            ui.label('Review Cards').classes('text-2xl font-bold text-pink-600')
        
        # Add your review interface here
    def _create_review_section(self):
        self.review_section = ui.column().classes('w-full mt-4')
        with self.review_section:
            ui.label("Từ cần ôn tập").classes('text-xl font-bold mb-2')
            self.review_count_label = ui.label().classes('text-sm text-gray-600 mb-2')
            
            self.flashcard = ui.card().classes('w-full h-48 cursor-pointer mb-4')
            with self.flashcard:
                self.card_content = ui.label().classes('text-xl text-center w-full h-full flex items-center justify-center')
            
            with ui.row().classes('w-full justify-center gap-4'):
                ui.button('←', on_click=self.prev_card).classes('bg-gray-500')
                ui.button('Lật thẻ', on_click=self.flip_card).classes('bg-blue-500')
                ui.button('→', on_click=self.next_card).classes('bg-gray-500')
            
            with ui.row().classes('w-full justify-center gap-4 mt-4'):
                ui.button('Đã nhớ', on_click=self.mark_as_remembered).classes('bg-green-500')
                ui.button('Chưa nhớ', on_click=self.next_card).classes('bg-red-500')
                ui.button('Kết thúc ôn tâp', on_click = self.review_logic.save_review_album).classes('bg-red-500')
        #self.review_section.set_visibility(False)
        self.update_review_section()
    
    def update_review_section(self):
        if self.review_count_label:
            count = self.review_logic.get_review_count()
            self.review_count_label.set_text(f'Còn {count} từ cần ôn tập')
    
        if self.card_content and self.flashcard:
            card_content = self.review_logic.get_current_card()
            if card_content:
                self.card_content.set_text(card_content)
                self.flashcard.style('background-color: white; color: black')
            else:
                self.card_content.set_text("Không còn từ nào cần ôn tập")


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
            ui.notify(f'Đã xóa "{removed_word}" khỏi danh sách ôn tập', color="success")
            self.update_review_section()



class Gamefront:
    def __init__(self):
        self.game_logic = GameLogic()
        self.review_logic = ReviewLogic()

    def setup_home_page(self):
        with ui.column().classes('w-full max-w-3xl mx-auto p-4'):
            with ui.row().classes('w-full items-center gap-4 mb-6'):
                ui.icon('school', size='32px').classes('text-pink-600')
                ui.label('FLASHCARDS').classes('text-2xl font-bold text-pink-600') 
            
            with ui.row().style('justify-content: center; margin: 10px 0;gap: 10px; flex-wrap: wrap;'): 
                ui.link('Flashcards Study', '/flashcards').classes(
                    'w-full bg-pink-600 hover:bg-pink-800 text-white font-semibold py-2 rounded-lg shadow-md text-center no-underline'
                )
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
