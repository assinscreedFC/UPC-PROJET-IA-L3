"""
Minimax avec élagage Alpha-Bêta pour le jeu Quoridor.
Basé sur minimax2.py, amélioré avec les coupures alpha/beta
pour réduire le nombre de nœuds explorés de O(b^d) à O(b^(d/2)).
"""

import math
import random
from typing import Tuple, Union

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
    IA Quoridor utilisant Minimax + élagage Alpha-Bêta.
    """

    def __init__(self, player_id: int, depth: int, strategy: str) -> None:
        self.player_id = player_id
        self.depth = depth
        self.strategy = strategy
        self.position_history: list = []

    def minimax(self, board: QuoridorBoard, depth: int, alpha: float,
                beta: float, maximizing: bool) -> float:
        """
        Minimax récursif avec élagage Alpha-Bêta.
        - alpha : meilleur score garanti pour MAX
        - beta  : meilleur score garanti pour MIN
        - Coupure quand alpha >= beta
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
                score = self.minimax(new_board, depth - 1, alpha, beta, False)
                if score > best:
                    best = score
                alpha = max(alpha, best)
                if alpha >= beta:
                    break
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
                score = self.minimax(new_board, depth - 1, alpha, beta, True)
                if score < best:
                    best = score
                beta = min(beta, best)
                if alpha >= beta:
                    break
            return best

    def get_best_move(self, board: QuoridorBoard) -> Tuple[str, Union[Tuple[int, int], Tuple[int, int, str]]]:
        """
        Détermine le meilleur coup à jouer.
        """
        moves = get_optimized_moves(board, self.player_id)

        best_move = None
        best_value = -math.inf

        # Alpha de la racine mis à jour avec le score brut (pas pénalisé)
        # pour ne pas fausser l'élagage des coups suivants
        alpha = -math.inf
        beta = math.inf

        recent = set(self.position_history[-6:])

        for move_type, data in moves:
            new_board = _fast_copy(board)
            if move_type == "MOVE":
                new_board.move_pawn(self.player_id, data)
            else:
                new_board.walls.add(data)
                new_board.walls_count[self.player_id] -= 1

            value = self.minimax(new_board, self.depth - 1, alpha, beta, False)

            # Pénalité anti-oscillation (uniquement au choix final, pas dans la récursion)
            adjusted = value
            if move_type == "MOVE" and data in recent:
                adjusted -= 50

            if adjusted > best_value:
                best_value = adjusted
                best_move = (move_type, data)

            # Alpha basé sur le score brut, pas le score pénalisé
            alpha = max(alpha, value)

        # Historique des positions
        if best_move and best_move[0] == "MOVE":
            self.position_history.append(best_move[1])
            if len(self.position_history) > 10:
                self.position_history = self.position_history[-10:]

        return best_move
