from typing import List, Tuple


class Board:
    EMPTY = 0
    BLACK = 1
    WHITE = 2
    BOARD_SIZE = 8

    def __init__(self):
        self.grid = [
            [self.EMPTY for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)
        ]
        self.initialize_board()

    def initialize_board(self):
        center = self.BOARD_SIZE // 2
        self.grid[center - 1][center - 1] = self.WHITE
        self.grid[center - 1][center] = self.BLACK
        self.grid[center][center - 1] = self.BLACK
        self.grid[center][center] = self.WHITE

    def is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE

    def get_cell(self, row: int, col: int) -> int:
        if self.is_valid_position(row, col):
            return self.grid[row][col]
        return -1

    def set_cell(self, row: int, col: int, value: int):
        if self.is_valid_position(row, col):
            self.grid[row][col] = value

    def is_empty(self, row: int, col: int) -> bool:
        return self.get_cell(row, col) == self.EMPTY

    def get_opponent(self, player: int) -> int:
        return self.WHITE if player == self.BLACK else self.BLACK

    def get_flips(self, row: int, col: int, player: int) -> List[Tuple[int, int]]:
        if not self.is_empty(row, col):
            return []

        opponent = self.get_opponent(player)
        flips = []

        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]

        for dr, dc in directions:
            temp_flips = []
            r, c = row + dr, col + dc

            while self.is_valid_position(r, c) and self.get_cell(r, c) == opponent:
                temp_flips.append((r, c))
                r += dr
                c += dc

            if (
                temp_flips
                and self.is_valid_position(r, c)
                and self.get_cell(r, c) == player
            ):
                flips.extend(temp_flips)

        return flips

    def is_valid_move(self, row: int, col: int, player: int) -> bool:
        return len(self.get_flips(row, col, player)) > 0

    def get_valid_moves(self, player: int) -> List[Tuple[int, int]]:
        valid_moves = []
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                if self.is_valid_move(row, col, player):
                    valid_moves.append((row, col))
        return valid_moves

    def place_stone(self, row: int, col: int, player: int) -> bool:
        flips = self.get_flips(row, col, player)
        if not flips:
            return False

        self.set_cell(row, col, player)
        for r, c in flips:
            self.set_cell(r, c, player)
        return True

    def count_stones(self) -> dict:
        count = {self.BLACK: 0, self.WHITE: 0, self.EMPTY: 0}
        for row in self.grid:
            for cell in row:
                count[cell] += 1
        return count

    def is_full(self) -> bool:
        return self.count_stones()[self.EMPTY] == 0

    def copy(self):
        new_board = Board()
        new_board.grid = [row[:] for row in self.grid]
        return new_board

    def __str__(self) -> str:
        symbols = {self.EMPTY: "□", self.BLACK: "●", self.WHITE: "○"}
        result = []
        for row in self.grid:
            result.append(" ".join(symbols[cell] for cell in row))
        return "\n".join(result)
