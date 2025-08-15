from typing import List, Optional, Tuple

from .board import Board


class Game:
    def __init__(self):
        self.board = Board()
        self.current_player = Board.BLACK
        self.history = []
        self.game_over = False
        self.passed_last_turn = False

    def get_current_player(self) -> int:
        return self.current_player

    def get_valid_moves(self) -> List[Tuple[int, int]]:
        return self.board.get_valid_moves(self.current_player)

    def make_move(self, row: int, col: int) -> bool:
        if self.game_over:
            return False

        if self.board.place_stone(row, col, self.current_player):
            self.history.append((row, col, self.current_player))
            self.passed_last_turn = False
            self.switch_turn()
            return True
        return False

    def switch_turn(self):
        self.current_player = self.board.get_opponent(self.current_player)

        if not self.get_valid_moves():
            if self.passed_last_turn:
                self.game_over = True
            else:
                self.passed_last_turn = True
                self.current_player = self.board.get_opponent(self.current_player)
                if not self.get_valid_moves():
                    self.game_over = True
        else:
            self.passed_last_turn = False

    def is_game_over(self) -> bool:
        return self.game_over or self.board.is_full()

    def get_winner(self) -> Optional[int]:
        if not self.is_game_over():
            return None

        count = self.board.count_stones()
        if count[Board.BLACK] > count[Board.WHITE]:
            return Board.BLACK
        elif count[Board.WHITE] > count[Board.BLACK]:
            return Board.WHITE
        else:
            return 0

    def get_score(self) -> dict:
        return self.board.count_stones()

    def reset(self):
        self.board = Board()
        self.current_player = Board.BLACK
        self.history = []
        self.game_over = False
        self.passed_last_turn = False

    def undo(self) -> bool:
        if not self.history:
            return False

        self.board = Board()
        self.current_player = Board.BLACK
        self.game_over = False
        self.passed_last_turn = False

        history_copy = self.history[:-1]
        self.history = []

        for row, col, _ in history_copy:
            self.make_move(row, col)

        return True

    def get_player_name(self, player: int) -> str:
        if player == Board.BLACK:
            return "黒"
        elif player == Board.WHITE:
            return "白"
        else:
            return "引き分け"

    def get_board_state(self) -> List[List[int]]:
        return [row[:] for row in self.board.grid]
