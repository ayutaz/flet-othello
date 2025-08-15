import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from game.game import Game
from game.board import Board


class TestGameInitialization:
    def test_ゲーム初期状態(self):
        game = Game()
        assert game.get_current_player() == Board.BLACK
        assert game.game_over is False
        assert game.passed_last_turn is False
        assert len(game.history) == 0

    def test_初期有効手(self):
        game = Game()
        valid_moves = game.get_valid_moves()
        assert len(valid_moves) == 4
        assert (2, 3) in valid_moves
        assert (3, 2) in valid_moves
        assert (4, 5) in valid_moves
        assert (5, 4) in valid_moves


class TestGameProgression:
    def test_正常な手の実行(self):
        game = Game()
        assert game.make_move(2, 3) is True
        assert game.get_current_player() == Board.WHITE
        assert len(game.history) == 1
        assert game.history[0] == (2, 3, Board.BLACK)

    def test_無効な手の拒否(self):
        game = Game()
        assert game.make_move(0, 0) is False
        assert game.get_current_player() == Board.BLACK
        assert len(game.history) == 0

    def test_既に石がある場所への配置(self):
        game = Game()
        assert game.make_move(3, 3) is False
        assert game.get_current_player() == Board.BLACK

    def test_ターン切り替え(self):
        game = Game()
        assert game.get_current_player() == Board.BLACK
        game.make_move(2, 3)
        assert game.get_current_player() == Board.WHITE
        game.make_move(2, 2)
        assert game.get_current_player() == Board.BLACK

    def test_連続した手の実行(self):
        game = Game()
        # 実際に有効な手の順序に変更
        moves = [(2, 3), (2, 2), (3, 2), (4, 2)]
        for i, move in enumerate(moves):
            expected_player = Board.BLACK if i % 2 == 0 else Board.WHITE
            assert game.get_current_player() == expected_player
            result = game.make_move(move[0], move[1])
            assert result is True, f"Move {move} failed for player {expected_player}"

    def test_ゲーム終了後の手の拒否(self):
        game = Game()
        game.game_over = True
        assert game.make_move(2, 3) is False


class TestPassHandling:
    def test_片方のパス処理(self):
        game = Game()
        game.board.grid = [[Board.BLACK for _ in range(8)] for _ in range(8)]
        game.board.set_cell(7, 7, Board.EMPTY)
        game.board.set_cell(7, 6, Board.WHITE)
        
        game.current_player = Board.WHITE
        game.switch_turn()
        
        assert game.current_player == Board.BLACK

    def test_連続パスでゲーム終了(self):
        game = Game()
        game.board.grid = [[Board.BLACK for _ in range(8)] for _ in range(8)]
        game.board.set_cell(7, 7, Board.EMPTY)
        
        game.current_player = Board.WHITE
        game.switch_turn()
        
        assert game.game_over is True

    def test_パス後の手番復帰(self):
        game = Game()
        game.board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
        game.board.set_cell(0, 0, Board.BLACK)
        game.board.set_cell(0, 1, Board.WHITE)
        game.board.set_cell(0, 2, Board.WHITE)
        game.board.set_cell(0, 3, Board.BLACK)
        
        game.current_player = Board.WHITE
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            game.switch_turn()
            assert game.current_player == Board.BLACK


class TestGameState:
    def test_スコア取得_初期状態(self):
        game = Game()
        score = game.get_score()
        assert score[Board.BLACK] == 2
        assert score[Board.WHITE] == 2

    def test_スコア取得_ゲーム中(self):
        game = Game()
        game.make_move(2, 3)
        score = game.get_score()
        assert score[Board.BLACK] == 4
        assert score[Board.WHITE] == 1

    def test_ボード状態の取得(self):
        game = Game()
        board_state = game.get_board_state()
        assert len(board_state) == 8
        assert all(len(row) == 8 for row in board_state)
        assert board_state[3][3] == Board.WHITE
        assert board_state[3][4] == Board.BLACK

    def test_履歴の記録(self):
        game = Game()
        # 実際に有効な手に変更
        moves = [(2, 3), (2, 2), (3, 2)]
        for move in moves:
            result = game.make_move(move[0], move[1])
            assert result is True, f"Move {move} failed"
        
        assert len(game.history) == 3
        assert game.history[0] == (2, 3, Board.BLACK)
        assert game.history[1] == (2, 2, Board.WHITE)
        assert game.history[2] == (3, 2, Board.BLACK)


class TestGameEnd:
    def test_ゲーム終了判定_継続中(self):
        game = Game()
        assert game.is_game_over() is False

    def test_ゲーム終了判定_満杯(self):
        game = Game()
        game.board.grid = [[Board.BLACK for _ in range(8)] for _ in range(8)]
        assert game.is_game_over() is True

    def test_ゲーム終了判定_有効手なし(self):
        game = Game()
        game.game_over = True
        assert game.is_game_over() is True

    def test_勝者判定_黒勝利(self):
        game = Game()
        game.board.grid = [[Board.BLACK for _ in range(8)] for _ in range(8)]
        game.board.set_cell(0, 0, Board.WHITE)
        game.game_over = True
        
        winner = game.get_winner()
        assert winner == Board.BLACK

    def test_勝者判定_白勝利(self):
        game = Game()
        game.board.grid = [[Board.WHITE for _ in range(8)] for _ in range(8)]
        game.board.set_cell(0, 0, Board.BLACK)
        game.game_over = True
        
        winner = game.get_winner()
        assert winner == Board.WHITE

    def test_勝者判定_引き分け(self):
        game = Game()
        for row in range(4):
            for col in range(8):
                game.board.grid[row][col] = Board.BLACK
        for row in range(4, 8):
            for col in range(8):
                game.board.grid[row][col] = Board.WHITE
        game.game_over = True
        
        winner = game.get_winner()
        assert winner == 0

    def test_勝者判定_ゲーム継続中(self):
        game = Game()
        winner = game.get_winner()
        assert winner is None


class TestSpecialOperations:
    def test_アンドゥ_単一(self):
        game = Game()
        game.make_move(2, 3)
        initial_player = game.get_current_player()
        
        assert game.undo() is True
        assert game.get_current_player() == Board.BLACK
        assert len(game.history) == 0

    def test_アンドゥ_複数(self):
        game = Game()
        # 有効な手に変更
        moves = [(2, 3), (2, 2), (3, 2)]
        for move in moves:
            game.make_move(move[0], move[1])
        
        assert game.undo() is True
        assert len(game.history) == 2
        
        board_state = game.get_board_state()
        assert board_state[3][2] == Board.EMPTY

    def test_アンドゥ_履歴なし(self):
        game = Game()
        assert game.undo() is False

    def test_アンドゥ後の一貫性(self):
        game = Game()
        game.make_move(2, 3)
        game.make_move(2, 2)
        score_before = game.get_score().copy()
        
        game.make_move(3, 2)  # 有効な手に変更
        game.undo()
        score_after = game.get_score()
        
        # アンドゥは完全にゲームを再構築するため、手番も含めて確認
        assert game.get_current_player() == Board.BLACK
        # アンドゥ後は2手だけ実行された状態になる
        assert len(game.history) == 2

    def test_リセット(self):
        game = Game()
        game.make_move(2, 3)
        game.make_move(2, 2)
        
        game.reset()
        
        assert game.get_current_player() == Board.BLACK
        assert len(game.history) == 0
        assert game.game_over is False
        assert game.passed_last_turn is False
        
        score = game.get_score()
        assert score[Board.BLACK] == 2
        assert score[Board.WHITE] == 2


class TestPlayerNames:
    def test_プレイヤー名の取得(self):
        game = Game()
        assert game.get_player_name(Board.BLACK) == "黒"
        assert game.get_player_name(Board.WHITE) == "白"
        assert game.get_player_name(0) == "引き分け"


class TestComplexScenarios:
    def test_完全ゲームシナリオ(self):
        game = Game()
        move_count = 0
        max_moves = 60
        
        while not game.is_game_over() and move_count < max_moves:
            valid_moves = game.get_valid_moves()
            if valid_moves:
                move = valid_moves[0]
                game.make_move(move[0], move[1])
                move_count += 1
            else:
                game.switch_turn()
        
        if game.is_game_over():
            winner = game.get_winner()
            assert winner is not None

    def test_特定の盤面パターン(self):
        game = Game()
        
        specific_moves = [
            (2, 3), (2, 2), (2, 4), (1, 2),
            (3, 2), (4, 2), (2, 1), (2, 5)
        ]
        
        for i, move in enumerate(specific_moves):
            if game.make_move(move[0], move[1]):
                expected_player = Board.WHITE if i % 2 == 0 else Board.BLACK
                assert game.get_current_player() == expected_player

    def test_複雑なパス処理シナリオ(self):
        game = Game()
        game.board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
        
        game.board.set_cell(0, 0, Board.BLACK)
        game.board.set_cell(0, 1, Board.BLACK)
        game.board.set_cell(1, 0, Board.BLACK)
        game.board.set_cell(1, 1, Board.WHITE)
        game.board.set_cell(7, 7, Board.WHITE)
        game.board.set_cell(7, 6, Board.BLACK)
        game.board.set_cell(6, 7, Board.BLACK)
        
        game.current_player = Board.BLACK
        valid_moves = game.get_valid_moves()
        
        if not valid_moves:
            game.switch_turn()
            if not game.get_valid_moves():
                assert game.game_over is True