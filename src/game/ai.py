import random
from typing import Optional, Tuple

from .board import Board
from .game import Game


class AI:
    def __init__(self, difficulty: str = "easy"):
        self.difficulty = difficulty
        self.corner_weight = 100
        self.edge_weight = 10
        self.mobility_weight = 5

    def get_move(self, game: Game) -> Optional[Tuple[int, int]]:
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None

        if self.difficulty == "easy":
            return self.get_random_move(valid_moves)
        elif self.difficulty == "medium":
            return self.get_greedy_move(game, valid_moves)
        else:
            return self.get_smart_move(game, valid_moves)

    def get_random_move(self, valid_moves: list) -> Tuple[int, int]:
        return random.choice(valid_moves)

    def get_greedy_move(self, game: Game, valid_moves: list) -> Tuple[int, int]:
        best_move = valid_moves[0]
        max_flips = 0

        for move in valid_moves:
            flips = len(game.board.get_flips(move[0], move[1], game.current_player))
            if flips > max_flips:
                max_flips = flips
                best_move = move

        return best_move

    def get_smart_move(self, game: Game, valid_moves: list) -> Tuple[int, int]:
        best_move = valid_moves[0]
        best_score = float("-inf")

        for move in valid_moves:
            score = self.evaluate_move(game, move)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def evaluate_move(self, game: Game, move: Tuple[int, int]) -> float:
        row, col = move
        score = 0

        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        if (row, col) in corners:
            score += self.corner_weight

        if row == 0 or row == 7 or col == 0 or col == 7:
            score += self.edge_weight

        bad_positions = [
            (0, 1),
            (1, 0),
            (1, 1),
            (0, 6),
            (1, 6),
            (1, 7),
            (6, 0),
            (6, 1),
            (7, 1),
            (6, 6),
            (6, 7),
            (7, 6),
        ]
        if (row, col) in bad_positions:
            score -= self.edge_weight * 2

        temp_board = game.board.copy()
        temp_board.place_stone(row, col, game.current_player)

        opponent = game.board.get_opponent(game.current_player)
        opponent_moves = temp_board.get_valid_moves(opponent)
        score -= len(opponent_moves) * self.mobility_weight

        flips = len(game.board.get_flips(row, col, game.current_player))
        score += flips * 2

        return score

    def minimax(
        self,
        board: Board,
        depth: int,
        player: int,
        alpha: float,
        beta: float,
        maximizing: bool,
    ) -> Tuple[float, Optional[Tuple[int, int]]]:
        if depth == 0:
            return self.evaluate_board(board, player), None

        valid_moves = board.get_valid_moves(player)
        if not valid_moves:
            opponent = board.get_opponent(player)
            opponent_moves = board.get_valid_moves(opponent)
            if not opponent_moves:
                return self.evaluate_board(board, player), None
            else:
                score, _ = self.minimax(
                    board, depth - 1, opponent, alpha, beta, not maximizing
                )
                return score, None

        best_move = None

        if maximizing:
            max_eval = float("-inf")
            for move in valid_moves:
                temp_board = board.copy()
                temp_board.place_stone(move[0], move[1], player)

                eval_score, _ = self.minimax(
                    temp_board,
                    depth - 1,
                    board.get_opponent(player),
                    alpha,
                    beta,
                    False,
                )

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break

            return max_eval, best_move
        else:
            min_eval = float("inf")
            for move in valid_moves:
                temp_board = board.copy()
                temp_board.place_stone(move[0], move[1], player)

                eval_score, _ = self.minimax(
                    temp_board, depth - 1, board.get_opponent(player), alpha, beta, True
                )

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move

                beta = min(beta, eval_score)
                if beta <= alpha:
                    break

            return min_eval, best_move

    def evaluate_board(self, board: Board, player: int) -> float:
        score = 0.0
        opponent = board.get_opponent(player)

        for row in range(8):
            for col in range(8):
                cell = board.get_cell(row, col)
                if cell == player:
                    score += self.get_position_value(row, col)
                elif cell == opponent:
                    score -= self.get_position_value(row, col)

        player_mobility = len(board.get_valid_moves(player))
        opponent_mobility = len(board.get_valid_moves(opponent))
        score += (player_mobility - opponent_mobility) * self.mobility_weight

        return float(score)

    def get_position_value(self, row: int, col: int) -> int:
        position_values = [
            [100, -20, 10, 5, 5, 10, -20, 100],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [10, -2, 1, 0, 0, 1, -2, 10],
            [5, -2, 0, 0, 0, 0, -2, 5],
            [5, -2, 0, 0, 0, 0, -2, 5],
            [10, -2, 1, 0, 0, 1, -2, 10],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [100, -20, 10, 5, 5, 10, -20, 100],
        ]
        return position_values[row][col]
