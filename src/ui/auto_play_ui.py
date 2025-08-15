from typing import Callable

import flet as ft

from game.auto_play_manager import AutoPlayState, PlayMode, Statistics, GameResult
from game.board import Board

from .theme import Theme


class AutoPlayUI:
    def __init__(self, theme: Theme):
        self.theme = theme
        self.play_button = None
        self.pause_button = None
        self.stop_button = None
        self.step_button = None
        self.skip_button = None
        self.speed_slider = None
        self.speed_text = None
        self.mode_dropdown = None
        self.black_ai_dropdown = None
        self.white_ai_dropdown = None
        self.game_count_input = None
        self.statistics_text = None
        self.progress_bar = None
        self.progress_text = None
        self.state_text = None

    def create_controls(
        self,
        on_play: Callable,
        on_pause: Callable,
        on_stop: Callable,
        on_step: Callable,
        on_skip: Callable,
        on_speed_change: Callable,
        on_mode_change: Callable,
        on_black_ai_change: Callable,
        on_white_ai_change: Callable,
        on_game_count_change: Callable,
    ) -> ft.Column:
        # 状態表示
        self.state_text = ft.Text(
            "状態: 待機中",
            size=14,
            weight=ft.FontWeight.BOLD,
            color=self.theme.text_color,
        )

        # AI設定
        ai_settings_title = ft.Text(
            "AI設定",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=self.theme.text_color,
        )

        self.black_ai_dropdown = ft.Dropdown(
            label="黒 AI",
            width=150,
            options=[
                ft.dropdown.Option("easy", "簡単"),
                ft.dropdown.Option("medium", "普通"),
                ft.dropdown.Option("hard", "難しい"),
            ],
            value="medium",
            on_change=lambda e: on_black_ai_change(e.control.value),
        )

        self.white_ai_dropdown = ft.Dropdown(
            label="白 AI",
            width=150,
            options=[
                ft.dropdown.Option("easy", "簡単"),
                ft.dropdown.Option("medium", "普通"),
                ft.dropdown.Option("hard", "難しい"),
            ],
            value="medium",
            on_change=lambda e: on_white_ai_change(e.control.value),
        )

        ai_row = ft.Row(
            [self.black_ai_dropdown, self.white_ai_dropdown],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

        # プレイモード設定
        play_settings_title = ft.Text(
            "プレイ設定",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=self.theme.text_color,
        )

        self.mode_dropdown = ft.Dropdown(
            label="モード",
            width=150,
            options=[
                ft.dropdown.Option("normal", "通常"),
                ft.dropdown.Option("step", "ステップ"),
                ft.dropdown.Option("instant", "瞬間実行"),
            ],
            value="normal",
            on_change=lambda e: on_mode_change(PlayMode(e.control.value)),
        )

        self.game_count_input = ft.TextField(
            label="対戦数",
            value="1",
            width=100,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=lambda e: on_game_count_change(int(e.control.value) if e.control.value.isdigit() else 1),
        )

        mode_row = ft.Row(
            [self.mode_dropdown, self.game_count_input],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

        # 速度調整
        self.speed_text = ft.Text(
            "速度: 1.0秒/手",
            size=14,
            color=self.theme.text_color,
        )

        self.speed_slider = ft.Slider(
            min=0.1,
            max=3.0,
            value=1.0,
            divisions=29,
            label="{value}秒",
            on_change=lambda e: self._on_speed_change(e, on_speed_change),
        )

        speed_container = ft.Container(
            content=ft.Column(
                [self.speed_text, self.speed_slider],
                spacing=5,
            ),
            margin=ft.margin.symmetric(vertical=10),
        )

        # コントロールボタン
        self.play_button = ft.IconButton(
            icon=ft.Icons.PLAY_ARROW,
            icon_size=30,
            bgcolor=ft.Colors.GREEN,
            icon_color=ft.Colors.WHITE,
            on_click=lambda e: on_play(),
        )

        self.pause_button = ft.IconButton(
            icon=ft.Icons.PAUSE,
            icon_size=30,
            bgcolor=ft.Colors.ORANGE,
            icon_color=ft.Colors.WHITE,
            on_click=lambda e: on_pause(),
            disabled=True,
        )

        self.stop_button = ft.IconButton(
            icon=ft.Icons.STOP,
            icon_size=30,
            bgcolor=ft.Colors.RED,
            icon_color=ft.Colors.WHITE,
            on_click=lambda e: on_stop(),
            disabled=True,
        )

        self.step_button = ft.IconButton(
            icon=ft.Icons.SKIP_NEXT,
            icon_size=30,
            bgcolor=ft.Colors.BLUE,
            icon_color=ft.Colors.WHITE,
            on_click=lambda e: on_step(),
            disabled=True,
        )

        self.skip_button = ft.IconButton(
            icon=ft.Icons.FAST_FORWARD,
            icon_size=30,
            bgcolor=ft.Colors.PURPLE,
            icon_color=ft.Colors.WHITE,
            on_click=lambda e: on_skip(),
            disabled=True,
        )

        control_row = ft.Row(
            [
                self.play_button,
                self.pause_button,
                self.stop_button,
                self.step_button,
                self.skip_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        )

        # 進捗表示
        self.progress_text = ft.Text(
            "進捗: 0 / 0",
            size=14,
            color=self.theme.text_color,
        )

        self.progress_bar = ft.ProgressBar(
            width=300,
            value=0,
            color=ft.Colors.BLUE,
            bgcolor=ft.Colors.GREY_400,
        )

        progress_container = ft.Container(
            content=ft.Column(
                [self.progress_text, self.progress_bar],
                spacing=5,
            ),
            margin=ft.margin.symmetric(vertical=10),
        )

        # 統計表示
        statistics_title = ft.Text(
            "統計",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=self.theme.text_color,
        )

        self.statistics_text = ft.Text(
            "まだ対戦していません",
            size=12,
            color=self.theme.text_color,
        )

        # 全体のレイアウト
        controls = ft.Column(
            [
                ft.Container(
                    content=ft.Text(
                        "自動プレイモード",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=self.theme.text_color,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=10),
                ),
                ft.Divider(height=1, color=self.theme.text_color),
                self.state_text,
                ft.Divider(height=1, color=self.theme.text_color),
                ai_settings_title,
                ai_row,
                ft.Divider(height=1, color=self.theme.text_color),
                play_settings_title,
                mode_row,
                speed_container,
                ft.Divider(height=1, color=self.theme.text_color),
                control_row,
                progress_container,
                ft.Divider(height=1, color=self.theme.text_color),
                statistics_title,
                self.statistics_text,
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO,
        )

        return controls

    def _on_speed_change(self, e, callback: Callable):
        """速度変更時の処理"""
        speed = e.control.value
        self.speed_text.value = f"速度: {speed:.1f}秒/手"
        callback(speed)

    def update_state(self, state: AutoPlayState):
        """状態表示を更新"""
        state_map = {
            AutoPlayState.IDLE: "待機中",
            AutoPlayState.PLAYING: "プレイ中",
            AutoPlayState.PAUSED: "一時停止",
            AutoPlayState.FINISHED: "完了",
        }
        self.state_text.value = f"状態: {state_map.get(state, '不明')}"

        # ボタンの有効/無効を切り替え
        if state == AutoPlayState.IDLE:
            self.play_button.disabled = False
            self.pause_button.disabled = True
            self.stop_button.disabled = True
            self.step_button.disabled = True
            self.skip_button.disabled = True
        elif state == AutoPlayState.PLAYING:
            self.play_button.disabled = True
            self.pause_button.disabled = False
            self.stop_button.disabled = False
            self.step_button.disabled = True
            self.skip_button.disabled = False
        elif state == AutoPlayState.PAUSED:
            self.play_button.disabled = True
            self.pause_button.disabled = True
            self.stop_button.disabled = False
            mode = self.mode_dropdown.value
            self.step_button.disabled = mode != "step"
            self.skip_button.disabled = False
            # 再開ボタンとして機能
            self.play_button.disabled = False
            self.play_button.icon = ft.Icons.PLAY_ARROW
        elif state == AutoPlayState.FINISHED:
            self.play_button.disabled = False
            self.pause_button.disabled = True
            self.stop_button.disabled = True
            self.step_button.disabled = True
            self.skip_button.disabled = True

    def update_progress(self, current: int, total: int):
        """進捗表示を更新"""
        self.progress_text.value = f"進捗: {current} / {total}"
        if total > 0:
            self.progress_bar.value = current / total
        else:
            self.progress_bar.value = 0

    def update_statistics(self, stats: Statistics):
        """統計表示を更新"""
        if stats.total_games == 0:
            self.statistics_text.value = "まだ対戦していません"
            return

        text = f"""対戦数: {stats.total_games}
黒勝利: {stats.black_wins} ({stats.get_win_rate(Board.BLACK):.1f}%)
白勝利: {stats.white_wins} ({stats.get_win_rate(Board.WHITE):.1f}%)
引分け: {stats.draws}

平均手数: {stats.get_average_moves():.1f}
最短手数: {stats.min_moves if stats.min_moves != float('inf') else 0}
最長手数: {stats.max_moves}

黒平均得点: {stats.get_average_score(Board.BLACK):.1f}
白平均得点: {stats.get_average_score(Board.WHITE):.1f}"""

        self.statistics_text.value = text

    def show_game_result(self, result: GameResult):
        """個別ゲーム結果を表示（必要に応じて実装）"""
        pass

    def update_theme(self, theme: Theme):
        """テーマを更新"""
        self.theme = theme
        # 各テキストコンポーネントの色を更新
        if self.state_text:
            self.state_text.color = theme.text_color
        if self.speed_text:
            self.speed_text.color = theme.text_color
        if self.progress_text:
            self.progress_text.color = theme.text_color
        if self.statistics_text:
            self.statistics_text.color = theme.text_color