from typing import Callable

import flet as ft

from game.board import Board

from .theme import Theme


class ControlsUI:
    def __init__(self, theme: Theme):
        self.theme = theme
        self.score_text = None
        self.turn_text = None
        self.history_text = None
        self.game_status_text = None

    def create_controls(
        self,
        on_new_game: Callable,
        on_ai_toggle: Callable,
        on_theme_toggle: Callable,
        on_undo: Callable,
        on_difficulty_change: Callable,
    ) -> ft.Column:

        self.turn_text = ft.Text(
            "現在のターン: ●黒",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=self.theme.text_color,
        )

        self.score_text = ft.Text(
            "黒: 2  白: 2",
            size=16,
            color=self.theme.text_color,
        )

        self.game_status_text = ft.Text(
            "",
            size=18,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREEN,
            visible=False,
        )

        button_row = ft.Row(
            [
                ft.ElevatedButton(
                    "新規ゲーム",
                    on_click=lambda e: on_new_game(),
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                ),
                ft.ElevatedButton(
                    "vs AI",
                    on_click=lambda e: on_ai_toggle(),
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                ),
                ft.ElevatedButton(
                    "1手戻る",
                    on_click=lambda e: on_undo(),
                    bgcolor=ft.Colors.ORANGE,
                    color=ft.Colors.WHITE,
                ),
                ft.IconButton(
                    ft.Icons.BRIGHTNESS_6,
                    on_click=lambda e: on_theme_toggle(),
                    icon_color=self.theme.text_color,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

        difficulty_dropdown = ft.Dropdown(
            label="AI難易度",
            width=150,
            options=[
                ft.dropdown.Option("easy", "簡単"),
                ft.dropdown.Option("medium", "普通"),
                ft.dropdown.Option("hard", "難しい"),
            ],
            value="easy",
            on_change=lambda e: on_difficulty_change(e.control.value),
        )

        self.history_text = ft.Text(
            "履歴: ",
            size=12,
            color=self.theme.text_color,
            max_lines=2,
        )

        controls = ft.Column(
            [
                ft.Container(
                    content=ft.Text(
                        "オセロゲーム",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=self.theme.text_color,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=10),
                ),
                ft.Divider(height=1, color=self.theme.text_color),
                button_row,
                difficulty_dropdown,
                ft.Divider(height=1, color=self.theme.text_color),
                self.turn_text,
                self.score_text,
                self.game_status_text,
                ft.Divider(height=1, color=self.theme.text_color),
                self.history_text,
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
        )

        return controls

    def update_turn(self, player: int, is_ai_turn: bool = False):
        player_symbol = "●黒" if player == Board.BLACK else "○白"
        ai_text = " (AI思考中...)" if is_ai_turn else ""
        self.turn_text.value = f"現在のターン: {player_symbol}{ai_text}"

    def update_score(self, black_count: int, white_count: int):
        self.score_text.value = f"黒: {black_count}  白: {white_count}"

    def update_history(self, history: list):
        if not history:
            self.history_text.value = "履歴: "
            return

        history_str = "履歴: "
        for _, (row, col, player) in enumerate(history[-5:]):
            symbol = "黒" if player == Board.BLACK else "白"
            position = f"{chr(65 + col)}{row + 1}"
            history_str += f"{symbol}{position} → "

        self.history_text.value = history_str[:-3]

    def show_game_over(self, winner: int):
        if winner == Board.BLACK:
            message = "🎉 黒の勝利！"
            color = ft.Colors.BLACK
        elif winner == Board.WHITE:
            message = "🎉 白の勝利！"
            color = ft.Colors.WHITE
        else:
            message = "引き分け！"
            color = ft.Colors.GREY

        self.game_status_text.value = message
        self.game_status_text.color = color
        self.game_status_text.visible = True

    def hide_game_over(self):
        self.game_status_text.visible = False

    def update_theme(self, theme: Theme):
        self.theme = theme
        if self.turn_text:
            self.turn_text.color = theme.text_color
        if self.score_text:
            self.score_text.color = theme.text_color
        if self.history_text:
            self.history_text.color = theme.text_color
