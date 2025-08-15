import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, Optional, Tuple

from .ai import AI
from .board import Board
from .game import Game


class PlayMode(Enum):
    NORMAL = "normal"  # 通常プレイ
    STEP = "step"  # ステップ実行
    INSTANT = "instant"  # 瞬間実行


class AutoPlayState(Enum):
    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"
    FINISHED = "finished"


@dataclass
class GameResult:
    winner: int
    black_score: int
    white_score: int
    total_moves: int
    black_ai_difficulty: str
    white_ai_difficulty: str


@dataclass
class Statistics:
    total_games: int = 0
    black_wins: int = 0
    white_wins: int = 0
    draws: int = 0
    total_moves: int = 0
    total_black_score: int = 0
    total_white_score: int = 0
    min_moves: int = float("inf")
    max_moves: int = 0
    results: list = None

    def __post_init__(self):
        if self.results is None:
            self.results = []

    def add_result(self, result: GameResult):
        self.total_games += 1
        self.total_moves += result.total_moves
        self.total_black_score += result.black_score
        self.total_white_score += result.white_score

        if result.winner == Board.BLACK:
            self.black_wins += 1
        elif result.winner == Board.WHITE:
            self.white_wins += 1
        else:
            self.draws += 1

        self.min_moves = min(self.min_moves, result.total_moves)
        self.max_moves = max(self.max_moves, result.total_moves)
        self.results.append(result)

    def get_win_rate(self, player: int) -> float:
        if self.total_games == 0:
            return 0.0
        if player == Board.BLACK:
            return self.black_wins / self.total_games * 100
        else:
            return self.white_wins / self.total_games * 100

    def get_average_score(self, player: int) -> float:
        if self.total_games == 0:
            return 0.0
        if player == Board.BLACK:
            return self.total_black_score / self.total_games
        else:
            return self.total_white_score / self.total_games

    def get_average_moves(self) -> float:
        if self.total_games == 0:
            return 0.0
        return self.total_moves / self.total_games


class AutoPlayManager:
    def __init__(self):
        self.game = Game()
        self.black_ai: Optional[AI] = None
        self.white_ai: Optional[AI] = None
        self.state = AutoPlayState.IDLE
        self.play_mode = PlayMode.NORMAL
        self.play_speed = 1.0  # 秒/手
        self.current_game_number = 0
        self.target_games = 1
        self.statistics = Statistics()
        self.on_update: Optional[Callable] = None
        self.on_move: Optional[Callable] = None
        self.on_game_end: Optional[Callable] = None
        self.on_all_games_end: Optional[Callable] = None
        self._play_task: Optional[asyncio.Task] = None
        self._stop_requested = False

    def set_ai_players(
        self, black_difficulty: str = "medium", white_difficulty: str = "medium"
    ):
        """AI プレイヤーを設定"""
        self.black_ai = AI(difficulty=black_difficulty)
        self.white_ai = AI(difficulty=white_difficulty)

    def set_play_mode(self, mode: PlayMode):
        """プレイモードを設定"""
        self.play_mode = mode

    def set_play_speed(self, speed: float):
        """プレイ速度を設定（秒/手）"""
        self.play_speed = max(0.1, min(3.0, speed))

    def set_target_games(self, count: int):
        """目標ゲーム数を設定"""
        self.target_games = max(1, count)

    async def start(self):
        """自動プレイを開始"""
        if self.state != AutoPlayState.IDLE:
            return

        if not self.black_ai or not self.white_ai:
            raise ValueError("Both black and white AI must be set")

        self.state = AutoPlayState.PLAYING
        self._stop_requested = False
        self.current_game_number = 0
        self.statistics = Statistics()

        if self.play_mode == PlayMode.INSTANT:
            await self._play_instant()
        else:
            self._play_task = asyncio.create_task(self._play_loop())

    async def pause(self):
        """自動プレイを一時停止"""
        if self.state == AutoPlayState.PLAYING:
            self.state = AutoPlayState.PAUSED

    async def resume(self):
        """自動プレイを再開"""
        if self.state == AutoPlayState.PAUSED:
            self.state = AutoPlayState.PLAYING

    async def stop(self):
        """自動プレイを停止"""
        self._stop_requested = True
        if self._play_task:
            self._play_task.cancel()
            try:
                await self._play_task
            except asyncio.CancelledError:
                pass
        self.state = AutoPlayState.IDLE

    async def step(self):
        """1手だけ進める（ステップモード用）"""
        if self.state != AutoPlayState.PAUSED and self.play_mode == PlayMode.STEP:
            await self._make_next_move()

    async def skip_current_game(self):
        """現在のゲームをスキップして次へ"""
        if self.state in [AutoPlayState.PLAYING, AutoPlayState.PAUSED]:
            self.game.game_over = True
            await self._handle_game_end()

    async def _play_loop(self):
        """通常/ステップモードのプレイループ"""
        try:
            while (
                self.current_game_number < self.target_games
                and not self._stop_requested
            ):
                self.game.reset()
                self.current_game_number += 1

                if self.on_update:
                    self.on_update()

                while not self.game.is_game_over() and not self._stop_requested:
                    # 一時停止チェック
                    while self.state == AutoPlayState.PAUSED:
                        await asyncio.sleep(0.1)
                        if self._stop_requested:
                            break

                    if self._stop_requested:
                        break

                    # ステップモードの場合は一時停止
                    if self.play_mode == PlayMode.STEP:
                        self.state = AutoPlayState.PAUSED
                        while self.state == AutoPlayState.PAUSED:
                            await asyncio.sleep(0.1)
                            if self._stop_requested:
                                break

                    if self._stop_requested:
                        break

                    await self._make_next_move()

                    # 通常モードの場合は速度に応じて待機
                    if self.play_mode == PlayMode.NORMAL:
                        await asyncio.sleep(self.play_speed)

                if not self._stop_requested:
                    await self._handle_game_end()

            if not self._stop_requested:
                self.state = AutoPlayState.FINISHED
                if self.on_all_games_end:
                    self.on_all_games_end(self.statistics)

        except asyncio.CancelledError:
            pass
        finally:
            self.state = AutoPlayState.IDLE

    async def _play_instant(self):
        """瞬間実行モード"""
        for game_num in range(self.target_games):
            if self._stop_requested:
                break

            self.game.reset()
            self.current_game_number = game_num + 1

            # ゲームが終了するまで即座に実行
            while not self.game.is_game_over():
                if self._stop_requested:
                    break
                await self._make_next_move()

            if not self._stop_requested:
                await self._handle_game_end()

        if not self._stop_requested:
            self.state = AutoPlayState.FINISHED
            if self.on_all_games_end:
                self.on_all_games_end(self.statistics)

        self.state = AutoPlayState.IDLE

    async def _make_next_move(self):
        """次の手を実行"""
        current_player = self.game.get_current_player()
        ai = self.black_ai if current_player == Board.BLACK else self.white_ai

        # 有効手がない場合はパス
        valid_moves = self.game.get_valid_moves()
        if not valid_moves:
            self.game.switch_turn()
            if self.on_update:
                self.on_update()
            return

        # AIに手を選択させる
        move = ai.get_move(self.game)
        if move:
            self.game.make_move(move[0], move[1])
            if self.on_move:
                self.on_move(move, current_player)
            if self.on_update:
                self.on_update()

    async def _handle_game_end(self):
        """ゲーム終了処理"""
        winner = self.game.get_winner()
        score = self.game.get_score()

        result = GameResult(
            winner=winner,
            black_score=score[Board.BLACK],
            white_score=score[Board.WHITE],
            total_moves=len(self.game.history),
            black_ai_difficulty=self.black_ai.difficulty,
            white_ai_difficulty=self.white_ai.difficulty,
        )

        self.statistics.add_result(result)

        if self.on_game_end:
            self.on_game_end(result)

    def get_current_state(self) -> Dict:
        """現在の状態を取得"""
        return {
            "state": self.state,
            "mode": self.play_mode,
            "speed": self.play_speed,
            "current_game": self.current_game_number,
            "target_games": self.target_games,
            "statistics": self.statistics,
        }

    def get_evaluation_map(self) -> Dict[Tuple[int, int], float]:
        """現在の盤面の評価値マップを取得"""
        if not self.game or self.game.is_game_over():
            return {}

        current_player = self.game.get_current_player()
        ai = self.black_ai if current_player == Board.BLACK else self.white_ai

        valid_moves = self.game.get_valid_moves()
        evaluation_map = {}

        for move in valid_moves:
            score = ai.evaluate_move(self.game, move)
            evaluation_map[move] = score

        return evaluation_map