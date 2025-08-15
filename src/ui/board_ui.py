from typing import Callable

import flet as ft

from game.board import Board
from game.game import Game

from .theme import Theme


class BoardUI:
    def __init__(self, game: Game, theme: Theme, on_cell_click: Callable):
        self.game = game
        self.theme = theme
        self.on_cell_click = on_cell_click
        self.cells = []
        self.board_container = None

    def create_board(self) -> ft.Container:
        grid = ft.Column(
            spacing=2,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        self.cells = []
        for row in range(Board.BOARD_SIZE):
            row_cells = []
            row_container = ft.Row(
                spacing=2,
                alignment=ft.MainAxisAlignment.CENTER,
            )

            for col in range(Board.BOARD_SIZE):
                cell = self.create_cell(row, col)
                row_cells.append(cell)
                row_container.controls.append(cell)

            self.cells.append(row_cells)
            grid.controls.append(row_container)

        self.board_container = ft.Container(
            content=grid,
            bgcolor=self.theme.board_color,
            border_radius=10,
            padding=10,
            width=420,
            height=420,
        )

        return self.board_container

    def create_cell(self, row: int, col: int) -> ft.Container:
        cell_content = ft.Container(
            width=45,
            height=45,
            bgcolor=self.theme.cell_color,
            border_radius=5,
            on_click=lambda e, r=row, c=col: self.on_cell_click(r, c),
            alignment=ft.alignment.center,
        )

        return cell_content

    def update_board(self):
        board_state = self.game.get_board_state()
        valid_moves = self.game.get_valid_moves()
        valid_positions = set(valid_moves)

        for row in range(Board.BOARD_SIZE):
            for col in range(Board.BOARD_SIZE):
                cell = self.cells[row][col]
                cell_value = board_state[row][col]

                if (row, col) in valid_positions and not self.game.is_game_over():
                    cell.bgcolor = self.theme.valid_move_color
                    cell.border = ft.border.all(2, self.theme.text_color)
                else:
                    cell.bgcolor = self.theme.cell_color
                    cell.border = None

                if cell_value == Board.BLACK:
                    cell.content = self.create_stone(True)
                elif cell_value == Board.WHITE:
                    cell.content = self.create_stone(False)
                else:
                    cell.content = None

    def create_stone(self, is_black: bool) -> ft.Container:
        return ft.Container(
            width=35,
            height=35,
            bgcolor=(
                self.theme.black_stone_color
                if is_black
                else self.theme.white_stone_color
            ),
            border_radius=20,
            border=ft.border.all(1, "#000000" if not is_black else "#808080"),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=3,
                color=ft.Colors.BLACK26,
                offset=ft.Offset(2, 2),
            ),
        )

    def update_theme(self, theme: Theme):
        self.theme = theme
        if self.board_container:
            self.board_container.bgcolor = theme.board_color
        self.update_board()

    def highlight_last_move(self, row: int, col: int):
        if 0 <= row < Board.BOARD_SIZE and 0 <= col < Board.BOARD_SIZE:
            cell = self.cells[row][col]
            cell.border = ft.border.all(3, ft.Colors.YELLOW)
