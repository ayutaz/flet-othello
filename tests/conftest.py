import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from game.board import Board
from game.game import Game


@pytest.fixture
def empty_board():
    """空のボードを返すフィクスチャ"""
    board = Board()
    board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
    return board


@pytest.fixture
def initial_board():
    """初期配置のボードを返すフィクスチャ"""
    return Board()


@pytest.fixture
def mid_game_board():
    """中盤の典型的な盤面を返すフィクスチャ"""
    board = Board()
    
    moves = [
        (2, 3, Board.BLACK),
        (2, 2, Board.WHITE),
        (2, 4, Board.BLACK),
        (1, 2, Board.WHITE),
        (3, 2, Board.BLACK),
        (4, 2, Board.WHITE),
        (2, 1, Board.BLACK),
        (2, 5, Board.WHITE),
    ]
    
    for row, col, player in moves:
        board.place_stone(row, col, player)
        board.current_player = board.get_opponent(player) if hasattr(board, 'current_player') else Board.WHITE
    
    return board


@pytest.fixture
def end_game_board():
    """終盤の典型的な盤面を返すフィクスチャ"""
    board = Board()
    
    for row in range(6):
        for col in range(8):
            if (row + col) % 2 == 0:
                board.grid[row][col] = Board.BLACK
            else:
                board.grid[row][col] = Board.WHITE
    
    for col in range(8):
        board.grid[6][col] = Board.BLACK if col < 4 else Board.WHITE
        board.grid[7][col] = Board.WHITE if col < 4 else Board.BLACK
    
    board.grid[7][7] = Board.EMPTY
    board.grid[7][6] = Board.EMPTY
    
    return board


@pytest.fixture
def game_with_history():
    """履歴付きのゲームインスタンスを返すフィクスチャ"""
    game = Game()
    
    moves = [(2, 3), (2, 2), (2, 4), (1, 2), (3, 2)]
    
    for row, col in moves:
        game.make_move(row, col)
    
    return game


@pytest.fixture
def corner_game():
    """角に着手可能な盤面を持つゲーム"""
    game = Game()
    game.board.grid = [[Board.EMPTY for _ in range(8)] for _ in range(8)]
    
    game.board.set_cell(0, 1, Board.WHITE)
    game.board.set_cell(0, 2, Board.WHITE)
    game.board.set_cell(0, 3, Board.BLACK)
    
    game.board.set_cell(1, 0, Board.WHITE)
    game.board.set_cell(1, 1, Board.WHITE)
    game.board.set_cell(1, 2, Board.BLACK)
    
    game.board.set_cell(2, 0, Board.WHITE)
    game.board.set_cell(2, 1, Board.BLACK)
    
    game.board.set_cell(3, 0, Board.BLACK)
    
    return game


@pytest.fixture
def pass_required_game():
    """パスが必要な盤面を持つゲーム"""
    game = Game()
    game.board.grid = [[Board.BLACK for _ in range(8)] for _ in range(8)]
    
    game.board.set_cell(7, 7, Board.EMPTY)
    game.board.set_cell(7, 6, Board.WHITE)
    game.board.set_cell(6, 7, Board.WHITE)
    
    game.current_player = Board.WHITE
    
    return game


@pytest.fixture
def nearly_full_board():
    """ほぼ満杯のボード"""
    board = Board()
    
    for row in range(8):
        for col in range(8):
            board.grid[row][col] = Board.BLACK if (row + col) % 2 == 0 else Board.WHITE
    
    board.grid[7][7] = Board.EMPTY
    
    return board


@pytest.mark.fast
class FastTest:
    """高速テスト用のマーカー"""
    pass


@pytest.mark.integration
class IntegrationTest:
    """統合テスト用のマーカー"""
    pass


@pytest.mark.slow
class SlowTest:
    """低速テスト用のマーカー"""
    pass