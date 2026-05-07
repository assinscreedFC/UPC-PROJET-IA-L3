"""
Minimax pur (sans élagage alpha-beta) pour le jeu Quoridor.
"""

import math

from typing import Tuple, Union, Optional

from src.engine.board import QuoridorBoard
from src.ia.evaluations import evaluate_board
from src.ia.moves_optimization import get_optimized_moves


def _fast_copy(board: QuoridorBoard) -> QuoridorBoard:
    """Copie légère du plateau."""
    new = QuoridorBoard.__new__(QuoridorBoard)
    new.size = 9
    new.positions = dict(board.positions)
    new.walls = set(board.walls)
    new.walls_count = dict(board.walls_count)
    new.winner = board.winner
    return new


class QuoridorIA:
    """
    IA Quoridor utilisant l'algorithme Minimax pur (sans élagage).
    """

    def __init__(self, player_id: int, depth: int, strategy: str) -> None:
        self.player_id = player_id
        self.depth = depth
        self.strategy = strategy
        self.position_history: list = []

    def minimax(self, board: QuoridorBoard, depth: int, maximizing: bool) -> float:
        """
        Algorithme Minimax récursif sans élagage.
        """
        if board.winner is not None:
            if board.winner == self.player_id:
                return 1000000 + depth
            else:
                return -1000000 - depth

        if depth == 0:
            return evaluate_board(board, self.player_id, self.strategy)

        current_player = self.player_id if maximizing else (3 - self.player_id)
        moves = get_optimized_moves(board, current_player)

        if maximizing:
            best = -math.inf
            for move_type, data in moves:
                new_board = _fast_copy(board)
                if move_type == "MOVE":
                    new_board.move_pawn(current_player, data)
                else:
                    new_board.walls.add(data)
                    new_board.walls_count[current_player] -= 1
                score = self.minimax(new_board, depth - 1, False)
                if score > best:
                    best = score
            return best
        else:
            best = math.inf
            for move_type, data in moves:
                new_board = _fast_copy(board)
                if move_type == "MOVE":
                    new_board.move_pawn(current_player, data)
                else:
                    new_board.walls.add(data)
                    new_board.walls_count[current_player] -= 1
                score = self.minimax(new_board, depth - 1, True)
                if score < best:
                    best = score
            return best

    def get_best_move(self, board: QuoridorBoard) -> Tuple[str, Union[Tuple[int, int], Tuple[int, int, str]]]:
        """
        Détermine le meilleur coup à jouer.
        """
        moves = get_optimized_moves(board, self.player_id)

        best_move = None
        best_value = -math.inf

        recent = set(self.position_history[-6:])

        for move_type, data in moves:
            new_board = _fast_copy(board)
            if move_type == "MOVE":
                new_board.move_pawn(self.player_id, data)
            else:
                new_board.walls.add(data)
                new_board.walls_count[self.player_id] -= 1

            value = self.minimax(new_board, self.depth - 1, False)

            # Pénalité anti-oscillation
            adjusted = value
            if move_type == "MOVE" and data in recent:
                adjusted -= 50

            if adjusted > best_value:
                best_value = adjusted
                best_move = (move_type, data)

        # Historique des positions
        if best_move and best_move[0] == "MOVE":
            self.position_history.append(best_move[1])
            if len(self.position_history) > 10:
                self.position_history = self.position_history[-10:]

        return best_move