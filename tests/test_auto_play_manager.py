import asyncio
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

pytestmark = pytest.mark.asyncio

from game.auto_play_manager import (
    AutoPlayManager,
    AutoPlayState,
    PlayMode,
    GameResult,
    Statistics,
)
from game.board import Board


class TestAutoPlayManager:
    def test_初期状態(self):
        manager = AutoPlayManager()
        assert manager.state == AutoPlayState.IDLE
        assert manager.play_mode == PlayMode.NORMAL
        assert manager.play_speed == 1.0
        assert manager.current_game_number == 0
        assert manager.target_games == 1

    def test_AI設定(self):
        manager = AutoPlayManager()
        manager.set_ai_players("easy", "hard")
        assert manager.black_ai is not None
        assert manager.white_ai is not None
        assert manager.black_ai.difficulty == "easy"
        assert manager.white_ai.difficulty == "hard"

    def test_プレイモード設定(self):
        manager = AutoPlayManager()
        manager.set_play_mode(PlayMode.STEP)
        assert manager.play_mode == PlayMode.STEP

        manager.set_play_mode(PlayMode.INSTANT)
        assert manager.play_mode == PlayMode.INSTANT

    def test_プレイ速度設定(self):
        manager = AutoPlayManager()
        manager.set_play_speed(0.5)
        assert manager.play_speed == 0.5

        # 最小値のテスト
        manager.set_play_speed(0.05)
        assert manager.play_speed == 0.1

        # 最大値のテスト
        manager.set_play_speed(5.0)
        assert manager.play_speed == 3.0

    def test_対戦数設定(self):
        manager = AutoPlayManager()
        manager.set_target_games(10)
        assert manager.target_games == 10

        # 最小値のテスト
        manager.set_target_games(0)
        assert manager.target_games == 1

    @pytest.mark.asyncio
    async def test_開始時のAI必須チェック(self):
        manager = AutoPlayManager()
        with pytest.raises(ValueError):
            await manager.start()

    @pytest.mark.asyncio
    async def test_瞬間実行モード(self):
        manager = AutoPlayManager()
        manager.set_ai_players("easy", "easy")
        manager.set_play_mode(PlayMode.INSTANT)
        manager.set_target_games(1)

        # コールバックの設定
        update_count = {"count": 0}
        game_end_count = {"count": 0}

        def on_update():
            update_count["count"] += 1

        def on_game_end(result):
            game_end_count["count"] += 1

        manager.on_update = on_update
        manager.on_game_end = on_game_end

        await manager.start()

        # ゲームが終了していることを確認
        assert manager.state == AutoPlayState.IDLE
        assert game_end_count["count"] == 1
        assert update_count["count"] > 0

    @pytest.mark.asyncio
    async def test_一時停止と再開(self):
        manager = AutoPlayManager()
        manager.set_ai_players("easy", "easy")
        manager.set_play_mode(PlayMode.NORMAL)
        manager.set_play_speed(0.1)

        # 開始
        await manager.start()
        assert manager.state == AutoPlayState.PLAYING

        # 一時停止
        await manager.pause()
        assert manager.state == AutoPlayState.PAUSED

        # 再開
        await manager.resume()
        assert manager.state == AutoPlayState.PLAYING

        # 停止
        await manager.stop()
        assert manager.state == AutoPlayState.IDLE

    def test_評価マップ取得(self):
        manager = AutoPlayManager()
        manager.set_ai_players("medium", "medium")

        # ゲーム開始前
        eval_map = manager.get_evaluation_map()
        assert len(eval_map) > 0  # 初期状態でも有効手があるはず

        # 各評価値が数値であることを確認
        for move, score in eval_map.items():
            assert isinstance(score, (int, float))
            assert isinstance(move, tuple)
            assert len(move) == 2


class TestStatistics:
    def test_統計初期状態(self):
        stats = Statistics()
        assert stats.total_games == 0
        assert stats.black_wins == 0
        assert stats.white_wins == 0
        assert stats.draws == 0
        assert stats.total_moves == 0
        assert stats.min_moves == float("inf")
        assert stats.max_moves == 0

    def test_結果追加(self):
        stats = Statistics()

        # 黒勝利の結果を追加
        result1 = GameResult(
            winner=Board.BLACK,
            black_score=40,
            white_score=24,
            total_moves=30,
            black_ai_difficulty="medium",
            white_ai_difficulty="easy",
        )
        stats.add_result(result1)

        assert stats.total_games == 1
        assert stats.black_wins == 1
        assert stats.white_wins == 0
        assert stats.draws == 0
        assert stats.total_moves == 30
        assert stats.min_moves == 30
        assert stats.max_moves == 30

        # 白勝利の結果を追加
        result2 = GameResult(
            winner=Board.WHITE,
            black_score=20,
            white_score=44,
            total_moves=40,
            black_ai_difficulty="easy",
            white_ai_difficulty="hard",
        )
        stats.add_result(result2)

        assert stats.total_games == 2
        assert stats.black_wins == 1
        assert stats.white_wins == 1
        assert stats.draws == 0
        assert stats.total_moves == 70
        assert stats.min_moves == 30
        assert stats.max_moves == 40

        # 引き分けの結果を追加
        result3 = GameResult(
            winner=0,
            black_score=32,
            white_score=32,
            total_moves=35,
            black_ai_difficulty="medium",
            white_ai_difficulty="medium",
        )
        stats.add_result(result3)

        assert stats.total_games == 3
        assert stats.black_wins == 1
        assert stats.white_wins == 1
        assert stats.draws == 1

    def test_勝率計算(self):
        stats = Statistics()

        # ゲームがない場合
        assert stats.get_win_rate(Board.BLACK) == 0.0
        assert stats.get_win_rate(Board.WHITE) == 0.0

        # 結果を追加
        for i in range(3):
            result = GameResult(
                winner=Board.BLACK,
                black_score=40,
                white_score=24,
                total_moves=30,
                black_ai_difficulty="medium",
                white_ai_difficulty="easy",
            )
            stats.add_result(result)

        for i in range(2):
            result = GameResult(
                winner=Board.WHITE,
                black_score=20,
                white_score=44,
                total_moves=30,
                black_ai_difficulty="easy",
                white_ai_difficulty="hard",
            )
            stats.add_result(result)

        # 黒: 3勝/5ゲーム = 60%
        assert stats.get_win_rate(Board.BLACK) == 60.0
        # 白: 2勝/5ゲーム = 40%
        assert stats.get_win_rate(Board.WHITE) == 40.0

    def test_平均スコア計算(self):
        stats = Statistics()

        # ゲームがない場合
        assert stats.get_average_score(Board.BLACK) == 0.0
        assert stats.get_average_score(Board.WHITE) == 0.0

        # 結果を追加
        result1 = GameResult(
            winner=Board.BLACK,
            black_score=40,
            white_score=24,
            total_moves=30,
            black_ai_difficulty="medium",
            white_ai_difficulty="easy",
        )
        stats.add_result(result1)

        result2 = GameResult(
            winner=Board.WHITE,
            black_score=20,
            white_score=44,
            total_moves=30,
            black_ai_difficulty="easy",
            white_ai_difficulty="hard",
        )
        stats.add_result(result2)

        # 黒平均: (40+20)/2 = 30
        assert stats.get_average_score(Board.BLACK) == 30.0
        # 白平均: (24+44)/2 = 34
        assert stats.get_average_score(Board.WHITE) == 34.0

    def test_平均手数計算(self):
        stats = Statistics()

        # ゲームがない場合
        assert stats.get_average_moves() == 0.0

        # 結果を追加
        stats.add_result(
            GameResult(
                winner=Board.BLACK,
                black_score=40,
                white_score=24,
                total_moves=30,
                black_ai_difficulty="medium",
                white_ai_difficulty="easy",
            )
        )

        stats.add_result(
            GameResult(
                winner=Board.WHITE,
                black_score=20,
                white_score=44,
                total_moves=40,
                black_ai_difficulty="easy",
                white_ai_difficulty="hard",
            )
        )

        # 平均: (30+40)/2 = 35
        assert stats.get_average_moves() == 35.0


class TestPlayModes:
    @pytest.mark.asyncio
    async def test_ステップモード(self):
        manager = AutoPlayManager()
        manager.set_ai_players("easy", "easy")
        manager.set_play_mode(PlayMode.STEP)

        # ステップモードでは開始後すぐに一時停止状態になる
        task = asyncio.create_task(manager.start())
        await asyncio.sleep(0.1)  # 少し待つ

        # ステップモードでは PAUSED 状態になるはず
        assert manager.state == AutoPlayState.PAUSED

        # ステップ実行
        await manager.step()

        # 停止
        await manager.stop()
        assert manager.state == AutoPlayState.IDLE

    @pytest.mark.asyncio
    async def test_複数ゲーム実行(self):
        manager = AutoPlayManager()
        manager.set_ai_players("easy", "easy")
        manager.set_play_mode(PlayMode.INSTANT)
        manager.set_target_games(3)

        game_count = {"count": 0}

        def on_game_end(result):
            game_count["count"] += 1

        manager.on_game_end = on_game_end

        await manager.start()

        # 3ゲーム終了していることを確認
        assert game_count["count"] == 3
        assert manager.statistics.total_games == 3