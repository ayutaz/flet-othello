import flet as ft


class Theme:
    def __init__(self, dark_mode: bool = False):
        self.dark_mode = dark_mode
        self.update_colors()

    def update_colors(self):
        if self.dark_mode:
            self.bg_color = "#1a1a1a"
            self.board_color = "#2d4a2b"
            self.cell_color = "#3d5a3b"
            self.valid_move_color = "#5a7a58"
            self.text_color = "#ffffff"
            self.black_stone_color = "#2c2c2c"
            self.white_stone_color = "#e0e0e0"
            self.grid_line_color = "#1a2a1a"
        else:
            self.bg_color = "#f0f0f0"
            self.board_color = "#4a7c4e"
            self.cell_color = "#5a8c5e"
            self.valid_move_color = "#7aac7e"
            self.text_color = "#000000"
            self.black_stone_color = "#1a1a1a"
            self.white_stone_color = "#ffffff"
            self.grid_line_color = "#3a5c3e"

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.update_colors()

    def get_theme_mode(self) -> ft.ThemeMode:
        return ft.ThemeMode.DARK if self.dark_mode else ft.ThemeMode.LIGHT
