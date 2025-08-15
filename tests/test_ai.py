import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from game.ai import AI
from game.game import Game
from game.board import Board


class TestAIDifficultyModes:
    def test_easy_ランダム選択(self):
        ai = AI(difficulty="easy")
        game = Game()
        
        with patch("random.choice") as mock_choice:
            mock_choice.return_value = (2, 3)
            move = ai.get_move(game)
            assert move == (2, 3)
            mock_choice.assert_called_once()

    def test_medium_最大獲得(self):
        ai = AI(difficulty="medium")
        game = Game()
        
        move = ai.get_move(game)
        assert move in game.get_valid_moves()
        
        game.board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
        game.board.set_cell(3, 3, Board.BLACK)
        game.board.set_cell(3, 4, Board.WHITE)
        game.board.set_cell(3, 5, Board.WHITE)
        game.board.set_cell(3, 6, Board.WHITE)
        game.board.set_cell(3, 7, Board.BLACK)
        
        game.current_player = Board.BLACK
        move = ai.get_greedy_move(game, [(3, 2), (3, 1)])
        assert move == (3, 2)

    def test_hard_戦略的選択(self):
        ai = AI(difficulty="hard")
        game = Game()
        
        move = ai.get_move(game)
        assert move in game.get_valid_moves()

    def test_有効手なしの処理(self):
        ai = AI()
        game = Game()
        game.board.grid = [[Board.BLACK for _ in range(8)] for _ in range(8)]
        
        move = ai.get_move(game)
        assert move is None


class TestAIEvaluation:
    def test_角の評価(self):
        ai = AI()
        game = Game()
        
        corner_score = ai.evaluate_move(game, (0, 0))
        regular_score = ai.evaluate_move(game, (3, 3))
        
        game.board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
        game.board.set_cell(0, 1, Board.WHITE)
        game.board.set_cell(1, 0, Board.WHITE)
        game.board.set_cell(7, 7, Board.BLACK)
        
        corner_eval = ai.evaluate_move(game, (0, 0))
        assert corner_eval > 0

    def test_辺の評価(self):
        ai = AI()
        game = Game()
        
        game.board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
        game.board.set_cell(0, 3, Board.WHITE)
        game.board.set_cell(0, 4, Board.WHITE)
        game.board.set_cell(0, 5, Board.BLACK)
        
        edge_score = ai.evaluate_move(game, (0, 2))
        assert edge_score >= 0

    def test_危険位置の評価(self):
        ai = AI()
        game = Game()
        
        x_square_score = ai.evaluate_move(game, (1, 1))
        c_square_score = ai.evaluate_move(game, (0, 1))
        
        game.board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
        game.board.set_cell(0, 0, Board.EMPTY)
        game.board.set_cell(1, 2, Board.WHITE)
        game.board.set_cell(2, 2, Board.BLACK)
        
        bad_position_eval = ai.evaluate_move(game, (1, 1))
        assert bad_position_eval < 0

    def test_機動力の評価(self):
        ai = AI()
        game = Game()
        
        game.board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
        game.board.set_cell(3, 3, Board.BLACK)
        game.board.set_cell(3, 4, Board.WHITE)
        game.board.set_cell(4, 3, Board.WHITE)
        game.board.set_cell(4, 4, Board.BLACK)
        
        mobility_score = ai.evaluate_move(game, (2, 2))
        assert isinstance(mobility_score, (int, float))


class TestMinimaxAlgorithm:
    def test_minimax_終端状態(self):
        ai = AI()
        board = Board()
        board.grid = [[Board.BLACK for _ in range(8)] for _ in range(8)]
        
        score, move = ai.minimax(board, 0, Board.BLACK, float("-inf"), float("inf"), True)
        assert move is None
        assert isinstance(score, float)

    def test_minimax_1手読み(self):
        ai = AI()
        board = Board()
        
        score, move = ai.minimax(board, 1, Board.BLACK, float("-inf"), float("inf"), True)
        if move:
            assert move in board.get_valid_moves(Board.BLACK)

    def test_minimax_複数手読み(self):
        ai = AI()
        board = Board()
        
        score, move = ai.minimax(board, 3, Board.BLACK, float("-inf"), float("inf"), True)
        if move:
            assert move in board.get_valid_moves(Board.BLACK)

    def test_alphabeta_枝刈り(self):
        ai = AI()
        board = Board()
        
        with patch.object(ai, 'evaluate_board') as mock_eval:
            mock_eval.return_value = 0.0
            score, move = ai.minimax(board, 2, Board.BLACK, float("-inf"), float("inf"), True)
            assert isinstance(score, float)

    def test_minimax_最大化プレイヤー(self):
        ai = AI()
        board = Board()
        board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
        board.set_cell(3, 3, Board.BLACK)
        board.set_cell(3, 4, Board.WHITE)
        board.set_cell(4, 3, Board.WHITE)
        board.set_cell(4, 4, Board.BLACK)
        
        score, move = ai.minimax(board, 2, Board.BLACK, float("-inf"), float("inf"), True)
        assert score > float("-inf")

    def test_minimax_最小化プレイヤー(self):
        ai = AI()
        board = Board()
        board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
        board.set_cell(3, 3, Board.BLACK)
        board.set_cell(3, 4, Board.WHITE)
        board.set_cell(4, 3, Board.WHITE)
        board.set_cell(4, 4, Board.BLACK)
        
        score, move = ai.minimax(board, 2, Board.WHITE, float("-inf"), float("inf"), False)
        assert score < float("inf")


class TestBoardEvaluation:
    def test_evaluate_board_初期状態(self):
        ai = AI()
        board = Board()
        
        score = ai.evaluate_board(board, Board.BLACK)
        assert isinstance(score, float)

    def test_evaluate_board_黒優勢(self):
        ai = AI()
        board = Board()
        for row in range(5):
            for col in range(8):
                board.grid[row][col] = Board.BLACK
        
        score = ai.evaluate_board(board, Board.BLACK)
        assert score > 0

    def test_evaluate_board_白優勢(self):
        ai = AI()
        board = Board()
        for row in range(5):
            for col in range(8):
                board.grid[row][col] = Board.WHITE
        
        score = ai.evaluate_board(board, Board.BLACK)
        assert score < 0

    def test_get_position_value(self):
        ai = AI()
        
        assert ai.get_position_value(0, 0) == 100
        assert ai.get_position_value(0, 7) == 100
        assert ai.get_position_value(7, 0) == 100
        assert ai.get_position_value(7, 7) == 100
        
        assert ai.get_position_value(1, 1) == -50
        assert ai.get_position_value(0, 1) == -20
        assert ai.get_position_value(1, 0) == -20


class TestAISpecialCases:
    def test_単一有効手(self):
        ai = AI()
        game = Game()
        game.board.grid = [[Board.BLACK for _ in range(8)] for _ in range(8)]
        game.board.set_cell(7, 7, Board.EMPTY)
        game.board.set_cell(7, 6, Board.WHITE)
        game.current_player = Board.BLACK
        
        move = ai.get_move(game)
        assert move == (7, 7)

    def test_完全ゲーム_AI対AI(self):
        ai1 = AI(difficulty="easy")
        ai2 = AI(difficulty="medium")
        game = Game()
        
        move_count = 0
        max_moves = 100
        
        while not game.is_game_over() and move_count < max_moves:
            current_ai = ai1 if game.get_current_player() == Board.BLACK else ai2
            move = current_ai.get_move(game)
            
            if move:
                game.make_move(move[0], move[1])
                move_count += 1
            else:
                game.switch_turn()
        
        assert game.is_game_over() or move_count == max_moves

    def test_get_random_move(self):
        ai = AI()
        valid_moves = [(2, 3), (3, 2), (4, 5), (5, 4)]
        
        for _ in range(10):
            move = ai.get_random_move(valid_moves)
            assert move in valid_moves

    def test_get_greedy_move_同点の場合(self):
        ai = AI()
        game = Game()
        game.board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
        game.board.set_cell(3, 3, Board.BLACK)
        game.board.set_cell(3, 4, Board.WHITE)
        game.board.set_cell(4, 3, Board.WHITE)
        game.board.set_cell(4, 4, Board.BLACK)
        
        valid_moves = game.board.get_valid_moves(Board.BLACK)
        move = ai.get_greedy_move(game, valid_moves)
        assert move in valid_moves

    def test_get_smart_move_評価値比較(self):
        ai = AI()
        game = Game()
        
        valid_moves = game.get_valid_moves()
        move = ai.get_smart_move(game, valid_moves)
        assert move in valid_moves
        
        scores = []
        for m in valid_moves:
            score = ai.evaluate_move(game, m)
            scores.append((score, m))
        
        best_score = max(scores, key=lambda x: x[0])[0]
        selected_score = ai.evaluate_move(game, move)
        assert selected_score == best_score


class TestAIIntegration:
    def test_AI難易度別の動作確認(self):
        difficulties = ["easy", "medium", "hard"]
        
        for difficulty in difficulties:
            ai = AI(difficulty=difficulty)
            game = Game()
            
            for _ in range(5):
                move = ai.get_move(game)
                if move:
                    assert move in game.get_valid_moves()
                    game.make_move(move[0], move[1])

    def test_AI設定値の確認(self):
        ai = AI()
        assert ai.corner_weight == 100
        assert ai.edge_weight == 10
        assert ai.mobility_weight == 5
        assert ai.difficulty == "easy"

    def test_複雑な盤面でのAI動作(self):
        ai = AI(difficulty="hard")
        game = Game()
        
        test_moves = [(2, 3), (2, 2), (2, 4), (1, 2)]
        for move in test_moves:
            if game.get_current_player() == Board.BLACK:
                game.make_move(move[0], move[1])
            else:
                ai_move = ai.get_move(game)
                if ai_move:
                    game.make_move(ai_move[0], ai_move[1])
        
        assert len(game.history) > 0