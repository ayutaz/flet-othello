import asyncio

import flet as ft

from game.ai import AI
from game.board import Board
from game.game import Game
from ui.board_ui import BoardUI
from ui.controls import ControlsUI
from ui.theme import Theme


class OthelloApp:
    def __init__(self):
        self.game = Game()
        self.theme = Theme(dark_mode=False)
        self.board_ui = None
        self.controls_ui = None
        self.ai_enabled = False
        self.ai = AI(difficulty="easy")
        self.page = None

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Othello Game"
        page.theme_mode = self.theme.get_theme_mode()
        page.bgcolor = self.theme.bg_color
        page.window.width = 800
        page.window.height = 600
        page.window.resizable = True
        page.window.center()

        self.board_ui = BoardUI(self.game, self.theme, self.on_cell_click)
        self.controls_ui = ControlsUI(self.theme)

        board = self.board_ui.create_board()
        controls = self.controls_ui.create_controls(
            on_new_game=self.new_game,
            on_ai_toggle=self.toggle_ai,
            on_theme_toggle=self.toggle_theme,
            on_undo=self.undo_move,
            on_difficulty_change=self.change_difficulty,
        )

        main_row = ft.Row(
            [
                ft.Container(
                    content=board,
                    margin=20,
                ),
                ft.Container(
                    content=controls,
                    margin=20,
                    width=300,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        page.add(
            ft.Container(
                content=main_row,
                expand=True,
                alignment=ft.alignment.center,
            )
        )

        self.update_ui()

    def on_cell_click(self, row: int, col: int):
        if self.game.is_game_over():
            return

        if self.ai_enabled and self.game.current_player == Board.WHITE:
            return

        if self.game.make_move(row, col):
            self.update_ui()

            if self.ai_enabled and not self.game.is_game_over():
                if self.game.current_player == Board.WHITE:
                    asyncio.create_task(self.make_ai_move())

    async def make_ai_move(self):
        self.controls_ui.update_turn(Board.WHITE, is_ai_turn=True)
        self.page.update()

        await asyncio.sleep(0.5)

        ai_move = self.ai.get_move(self.game)
        if ai_move:
            self.game.make_move(ai_move[0], ai_move[1])
            self.update_ui()

    def new_game(self):
        self.game.reset()
        self.controls_ui.hide_game_over()
        self.update_ui()

    def toggle_ai(self):
        self.ai_enabled = not self.ai_enabled
        if self.ai_enabled:
            self.new_game()

    def toggle_theme(self):
        self.theme.toggle_theme()
        self.page.theme_mode = self.theme.get_theme_mode()
        self.page.bgcolor = self.theme.bg_color
        self.board_ui.update_theme(self.theme)
        self.controls_ui.update_theme(self.theme)
        self.page.update()

    def undo_move(self):
        if self.game.undo():
            self.controls_ui.hide_game_over()
            self.update_ui()

    def change_difficulty(self, difficulty: str):
        self.ai.difficulty = difficulty

    def update_ui(self):
        self.board_ui.update_board()

        score = self.game.get_score()
        self.controls_ui.update_score(score[Board.BLACK], score[Board.WHITE])
        self.controls_ui.update_turn(self.game.current_player)
        self.controls_ui.update_history(self.game.history)

        if self.game.is_game_over():
            winner = self.game.get_winner()
            self.controls_ui.show_game_over(winner)

        if self.page:
            self.page.update()


def main():
    app = OthelloApp()
    ft.app(target=app.main)


if __name__ == "__main__":
    main()
