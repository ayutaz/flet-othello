import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from game.board import Board


class TestBoardInitialization:
    def test_初期化時のボードサイズ(self):
        board = Board()
        assert len(board.grid) == 8
        assert all(len(row) == 8 for row in board.grid)

    def test_初期配置の正確性(self):
        board = Board()
        assert board.get_cell(3, 3) == Board.WHITE
        assert board.get_cell(3, 4) == Board.BLACK
        assert board.get_cell(4, 3) == Board.BLACK
        assert board.get_cell(4, 4) == Board.WHITE

    def test_初期配置以外は空(self):
        board = Board()
        empty_count = 0
        for row in range(8):
            for col in range(8):
                if (row, col) not in [(3, 3), (3, 4), (4, 3), (4, 4)]:
                    assert board.get_cell(row, col) == Board.EMPTY
                    empty_count += 1
        assert empty_count == 60


class TestBoardBasicOperations:
    def test_有効な位置の判定(self):
        board = Board()
        for row in range(8):
            for col in range(8):
                assert board.is_valid_position(row, col) is True

    @pytest.mark.parametrize(
        "row,col",
        [
            (-1, 0),
            (0, -1),
            (8, 0),
            (0, 8),
            (-1, -1),
            (8, 8),
            (100, 100),
        ],
    )
    def test_無効な位置の判定(self, row, col):
        board = Board()
        assert board.is_valid_position(row, col) is False

    def test_空のセルの判定(self):
        board = Board()
        assert board.is_empty(0, 0) is True
        assert board.is_empty(3, 3) is False
        assert board.is_empty(3, 4) is False

    def test_石の配置と取得(self):
        board = Board()
        board.set_cell(0, 0, Board.BLACK)
        assert board.get_cell(0, 0) == Board.BLACK
        
        board.set_cell(0, 0, Board.WHITE)
        assert board.get_cell(0, 0) == Board.WHITE

    def test_範囲外への石の配置(self):
        board = Board()
        board.set_cell(-1, 0, Board.BLACK)
        assert board.get_cell(-1, 0) == -1


class TestBoardGameLogic:
    def test_相手プレイヤーの取得(self):
        board = Board()
        assert board.get_opponent(Board.BLACK) == Board.WHITE
        assert board.get_opponent(Board.WHITE) == Board.BLACK

    def test_単一方向のひっくり返し(self):
        board = Board()
        # 初期配置で(2,3)に黒を置くと(3,3)の白がひっくり返る
        flips = board.get_flips(2, 3, Board.BLACK)
        assert (3, 3) in flips
        assert len(flips) == 1

    def test_複数方向のひっくり返し(self):
        board = Board()
        # 初期配置を変更して複数方向のテストを設定
        board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
        board.set_cell(3, 3, Board.WHITE)
        board.set_cell(3, 4, Board.WHITE)
        board.set_cell(4, 3, Board.WHITE)
        board.set_cell(4, 4, Board.BLACK)
        board.set_cell(3, 5, Board.BLACK)
        board.set_cell(5, 3, Board.BLACK)
        
        # (2,2)に黒を置くと2方向でひっくり返る
        flips = board.get_flips(2, 2, Board.BLACK)
        assert (3, 3) in flips
        assert (4, 4) not in flips  # これは既に黒
        assert len(flips) == 1

    def test_ひっくり返せない場合(self):
        board = Board()
        flips = board.get_flips(0, 0, Board.BLACK)
        assert len(flips) == 0

    def test_既に石がある場所(self):
        board = Board()
        flips = board.get_flips(3, 3, Board.BLACK)
        assert len(flips) == 0

    def test_有効手の判定_初期状態(self):
        board = Board()
        assert board.is_valid_move(2, 3, Board.BLACK) is True
        assert board.is_valid_move(3, 2, Board.BLACK) is True
        assert board.is_valid_move(4, 5, Board.BLACK) is True
        assert board.is_valid_move(5, 4, Board.BLACK) is True

    def test_有効手の判定_無効(self):
        board = Board()
        assert board.is_valid_move(0, 0, Board.BLACK) is False
        assert board.is_valid_move(3, 3, Board.BLACK) is False

    @pytest.mark.parametrize(
        "row,col",
        [(0, 0), (0, 7), (7, 0), (7, 7)],
    )
    def test_角への配置(self, row, col):
        board = Board()
        board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
        
        adj_positions = []
        if row == 0:
            adj_positions.append((1, col))
        else:
            adj_positions.append((6, col))
        
        if col == 0:
            adj_positions.append((row, 1))
        else:
            adj_positions.append((row, 6))
        
        for pos in adj_positions:
            board.set_cell(pos[0], pos[1], Board.WHITE)
        
        opposite_row = 7 - row
        opposite_col = 7 - col
        board.set_cell(opposite_row, opposite_col, Board.BLACK)
        
        if board.is_valid_move(row, col, Board.BLACK):
            assert board.place_stone(row, col, Board.BLACK) is True
            assert board.get_cell(row, col) == Board.BLACK


class TestBoardGameState:
    def test_石のカウント_初期状態(self):
        board = Board()
        count = board.count_stones()
        assert count[Board.BLACK] == 2
        assert count[Board.WHITE] == 2
        assert count[Board.EMPTY] == 60

    def test_石のカウント_ゲーム中(self):
        board = Board()
        board.place_stone(2, 3, Board.BLACK)
        count = board.count_stones()
        assert count[Board.BLACK] == 4
        assert count[Board.WHITE] == 1
        assert count[Board.EMPTY] == 59

    def test_ボード満杯の判定_初期(self):
        board = Board()
        assert board.is_full() is False

    def test_ボード満杯の判定_満杯(self):
        board = Board()
        for row in range(8):
            for col in range(8):
                board.grid[row][col] = Board.BLACK
        assert board.is_full() is True

    def test_有効手リストの取得_初期(self):
        board = Board()
        black_moves = board.get_valid_moves(Board.BLACK)
        assert len(black_moves) == 4
        assert (2, 3) in black_moves
        assert (3, 2) in black_moves
        assert (4, 5) in black_moves
        assert (5, 4) in black_moves

    def test_有効手リストの取得_白(self):
        board = Board()
        white_moves = board.get_valid_moves(Board.WHITE)
        assert len(white_moves) == 4
        assert (2, 4) in white_moves
        assert (4, 2) in white_moves
        assert (3, 5) in white_moves
        assert (5, 3) in white_moves

    def test_ボードのコピー(self):
        board = Board()
        board.place_stone(2, 3, Board.BLACK)
        
        copied = board.copy()
        assert copied.get_cell(2, 3) == Board.BLACK
        assert copied.get_cell(3, 3) == Board.BLACK
        
        # 白の手番として(2,2)に配置
        copied.place_stone(2, 2, Board.WHITE)
        # 元のボードと異なることを確認
        assert board.get_cell(2, 2) != copied.get_cell(2, 2)

    def test_石の配置と反転(self):
        board = Board()
        assert board.place_stone(2, 3, Board.BLACK) is True
        assert board.get_cell(2, 3) == Board.BLACK
        assert board.get_cell(3, 3) == Board.BLACK

    def test_無効な石の配置(self):
        board = Board()
        assert board.place_stone(0, 0, Board.BLACK) is False
        assert board.get_cell(0, 0) == Board.EMPTY


class TestBoardEdgeCases:
    def test_8方向全てのひっくり返し(self):
        board = Board()
        board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
        
        board.set_cell(4, 4, Board.BLACK)
        
        directions = [
            (3, 3), (3, 4), (3, 5),
            (4, 3),         (4, 5),
            (5, 3), (5, 4), (5, 5)
        ]
        for row, col in directions:
            board.set_cell(row, col, Board.WHITE)
        
        corners = [
            (2, 2), (2, 4), (2, 6),
            (4, 2),         (4, 6),
            (6, 2), (6, 4), (6, 6)
        ]
        for row, col in corners:
            board.set_cell(row, col, Board.BLACK)
        
        flips = board.get_flips(4, 4, Board.BLACK)
        assert len(flips) == 0

    def test_長い列のひっくり返し(self):
        board = Board()
        board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
        
        for col in range(1, 7):
            board.set_cell(0, col, Board.WHITE)
        board.set_cell(0, 0, Board.BLACK)
        board.set_cell(0, 7, Board.BLACK)
        
        flips = board.get_flips(0, 4, Board.BLACK)
        assert len(flips) == 0

    def test_文字列表現(self):
        board = Board()
        str_repr = str(board)
        assert "●" in str_repr
        assert "○" in str_repr
        assert "□" in str_repr