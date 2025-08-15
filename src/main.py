import asyncio

import flet as ft

from game.ai import AI
from game.auto_play_manager import AutoPlayManager, PlayMode
from game.board import Board
from game.game import Game
from ui.auto_play_ui import AutoPlayUI
from ui.board_ui import BoardUI
from ui.controls import ControlsUI
from ui.theme import Theme


class OthelloApp:
    def __init__(self):
        self.game = Game()
        self.theme = Theme(dark_mode=False)
        self.board_ui = None
        self.controls_ui = None
        self.auto_play_ui = None
        self.ai_enabled = False
        self.ai = AI(difficulty="easy")
        self.auto_play_manager = AutoPlayManager()
        self.page = None
        self.is_auto_play_mode = False
        self.mode_toggle_button = None

    def main(self, page: ft.Page):
        self.page = page
        page.title = "Othello Game"
        page.theme_mode = self.theme.get_theme_mode()
        page.bgcolor = self.theme.bg_color
        page.window.width = 900
        page.window.height = 700
        page.window.resizable = True
        page.window.center()

        self.board_ui = BoardUI(self.game, self.theme, self.on_cell_click)
        self.controls_ui = ControlsUI(self.theme)
        self.auto_play_ui = AutoPlayUI(self.theme)

        # 自動プレイマネージャーのコールバック設定
        self.auto_play_manager.on_update = self.on_auto_play_update
        self.auto_play_manager.on_move = self.on_auto_play_move
        self.auto_play_manager.on_game_end = self.on_auto_play_game_end
        self.auto_play_manager.on_all_games_end = self.on_auto_play_all_games_end

        board = self.board_ui.create_board()
        
        # モード切り替えボタン
        self.mode_toggle_button = ft.ElevatedButton(
            "自動プレイモードへ",
            on_click=lambda e: self.toggle_mode(),
            bgcolor=ft.Colors.PURPLE,
            color=ft.Colors.WHITE,
        )

        # 通常モードのコントロール
        normal_controls = self.controls_ui.create_controls(
            on_new_game=self.new_game,
            on_ai_toggle=self.toggle_ai,
            on_theme_toggle=self.toggle_theme,
            on_undo=self.undo_move,
            on_difficulty_change=self.change_difficulty,
        )

        # 自動プレイモードのコントロール
        auto_play_controls = self.auto_play_ui.create_controls(
            on_play=lambda: asyncio.create_task(self.auto_play_start()),
            on_pause=lambda: asyncio.create_task(self.auto_play_pause()),
            on_stop=lambda: asyncio.create_task(self.auto_play_stop()),
            on_step=lambda: asyncio.create_task(self.auto_play_step()),
            on_skip=lambda: asyncio.create_task(self.auto_play_skip()),
            on_speed_change=self.auto_play_speed_change,
            on_mode_change=self.auto_play_mode_change,
            on_black_ai_change=self.auto_play_black_ai_change,
            on_white_ai_change=self.auto_play_white_ai_change,
            on_game_count_change=self.auto_play_game_count_change,
        )

        # コントロールパネルのコンテナ
        self.controls_container = ft.Container(
            content=ft.Column([
                self.mode_toggle_button,
                ft.Divider(height=1, color=self.theme.text_color),
                normal_controls,
            ]),
            margin=20,
            width=350,
        )

        self.auto_controls_container = ft.Container(
            content=ft.Column([
                self.mode_toggle_button,
                ft.Divider(height=1, color=self.theme.text_color),
                auto_play_controls,
            ]),
            margin=20,
            width=350,
            visible=False,
        )

        main_row = ft.Row(
            [
                ft.Container(
                    content=board,
                    margin=20,
                ),
                self.controls_container,
                self.auto_controls_container,
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

    def toggle_mode(self):
        """通常モードと自動プレイモードを切り替え"""
        self.is_auto_play_mode = not self.is_auto_play_mode
        
        if self.is_auto_play_mode:
            self.mode_toggle_button.text = "通常モードへ"
            self.controls_container.visible = False
            self.auto_controls_container.visible = True
            # 自動プレイ用のゲームに切り替え
            self.game = self.auto_play_manager.game
            self.board_ui.game = self.game
        else:
            self.mode_toggle_button.text = "自動プレイモードへ"
            self.controls_container.visible = True
            self.auto_controls_container.visible = False
            # 通常プレイ用のゲームに戻す
            self.game = Game()
            self.board_ui.game = self.game
            
        self.update_ui()
        self.page.update()

    # 自動プレイモードのコールバック
    async def auto_play_start(self):
        """自動プレイを開始"""
        self.auto_play_manager.set_ai_players(
            self.auto_play_ui.black_ai_dropdown.value,
            self.auto_play_ui.white_ai_dropdown.value,
        )
        await self.auto_play_manager.start()

    async def auto_play_pause(self):
        """自動プレイを一時停止"""
        await self.auto_play_manager.pause()
        self.auto_play_ui.update_state(self.auto_play_manager.state)
        self.page.update()

    async def auto_play_stop(self):
        """自動プレイを停止"""
        await self.auto_play_manager.stop()
        self.auto_play_ui.update_state(self.auto_play_manager.state)
        self.page.update()

    async def auto_play_step(self):
        """ステップ実行"""
        await self.auto_play_manager.step()

    async def auto_play_skip(self):
        """現在のゲームをスキップ"""
        await self.auto_play_manager.skip_current_game()

    def auto_play_speed_change(self, speed: float):
        """プレイ速度を変更"""
        self.auto_play_manager.set_play_speed(speed)

    def auto_play_mode_change(self, mode: PlayMode):
        """プレイモードを変更"""
        self.auto_play_manager.set_play_mode(mode)
        # ステップモードの場合、ステップボタンを有効化
        if mode == PlayMode.STEP:
            self.auto_play_ui.step_button.disabled = False
        else:
            self.auto_play_ui.step_button.disabled = True
        self.page.update()

    def auto_play_black_ai_change(self, difficulty: str):
        """黒AIの難易度を変更"""
        if self.auto_play_manager.black_ai:
            self.auto_play_manager.black_ai.difficulty = difficulty

    def auto_play_white_ai_change(self, difficulty: str):
        """白AIの難易度を変更"""
        if self.auto_play_manager.white_ai:
            self.auto_play_manager.white_ai.difficulty = difficulty

    def auto_play_game_count_change(self, count: int):
        """対戦数を変更"""
        self.auto_play_manager.set_target_games(count)

    def on_auto_play_update(self):
        """自動プレイの状態更新時のコールバック"""
        self.board_ui.update_board()
        self.auto_play_ui.update_state(self.auto_play_manager.state)
        self.auto_play_ui.update_progress(
            self.auto_play_manager.current_game_number,
            self.auto_play_manager.target_games,
        )
        
        # スコア表示の更新
        score = self.game.get_score()
        self.controls_ui.update_score(score[Board.BLACK], score[Board.WHITE])
        
        if self.page:
            self.page.update()

    def on_auto_play_move(self, move: tuple, player: int):
        """自動プレイで手が打たれた時のコールバック"""
        # 必要に応じてアニメーションや効果音を追加
        pass

    def on_auto_play_game_end(self, result):
        """1ゲーム終了時のコールバック"""
        self.auto_play_ui.update_statistics(self.auto_play_manager.statistics)
        if self.page:
            self.page.update()

    def on_auto_play_all_games_end(self, statistics):
        """全ゲーム終了時のコールバック"""
        self.auto_play_ui.update_state(self.auto_play_manager.state)
        self.auto_play_ui.update_statistics(statistics)
        if self.page:
            self.page.update()


def main():
    app = OthelloApp()
    ft.app(target=app.main)


if __name__ == "__main__":
    main()
