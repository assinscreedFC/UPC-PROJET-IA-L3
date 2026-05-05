import math
import random
from typing import Tuple, Optional, List,Union
from src.engine.board import QuoridorBoard
from src.ia.evaluations import evaluate_board
from src.ia.moves_optimization import get_optimized_moves


def _fast_copy(board: QuoridorBoard) -> QuoridorBoard:
    """Copie légère du plateau — ~50x plus rapide que copy.deepcopy.
    Sûr car tous les éléments (tuples, ints, strings) sont immutables."""
    new = QuoridorBoard.__new__(QuoridorBoard)
    new.size = 9
    new.positions = dict(board.positions)
    new.walls = set(board.walls)
    new.walls_count = dict(board.walls_count)
    new.winner = board.winner
    return new


class QuoridorIA:
    """
    Intelligence Artificielle capable de simuler et choisir le meilleur coup.
    """

    def __init__(self, player_id: int, depth: int, strategy: str) -> None:
        """
        Initialise l'IA.

        Args:
            player_id (int): ID du joueur (1 ou 2).
            depth (int): Profondeur de recherche.
            strategy (str): Nom de la fonction d'évaluation à utiliser.
        """
        self.player_id = player_id
        self.depth = depth
        self.strategy = strategy
        self.position_history: list = []  # Historique des positions pour éviter l'oscillation

    def alpha_beta(self, board: QuoridorBoard, depth: int, alpha: float,
                   beta: float, maximizing_player: bool) -> float:
        """
        Algorithme de recherche avec élagage pour optimiser le temps de calcul.

        Args:
            board (QuoridorBoard): État simulé du plateau.
            depth (int): Profondeur actuelle.
            alpha (float): Meilleur score garanti pour MAX.
            beta (float): Meilleur score garanti pour MIN.
            maximizing_player (bool): True si c'est le tour de l'IA.

        Returns:
            float: Score de l'évaluation.
        """
        # A3 — Traiter les victoires/défaites directement (évite BFS inutile,
        # préfère les victoires rapides et les défaites lentes)
        if board.winner is not None:
            if board.winner == self.player_id:
                return 1000000 + depth
            else:
                return -1000000 - depth

        if depth == 0:
            return evaluate_board(board, self.player_id, self.strategy)

        current_player = self.player_id if maximizing_player else (3 - self.player_id)
        moves = get_optimized_moves(board, current_player)

        if maximizing_player:
            value = -math.inf
            for move_type, data in moves:
                new_board = _fast_copy(board)
                if move_type == "MOVE":
                    new_board.move_pawn(current_player, data)
                else:
                    # A4 — Application directe des murs pré-validés
                    new_board.walls.add(data)
                    new_board.walls_count[current_player] -= 1

                value = max(value, self.alpha_beta(new_board, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta: break
            return value
        else:
            value = math.inf
            for move_type, data in moves:
                new_board = _fast_copy(board)
                if move_type == "MOVE":
                    new_board.move_pawn(current_player, data)
                else:
                    # A4 — Application directe des murs pré-validés
                    new_board.walls.add(data)
                    new_board.walls_count[current_player] -= 1

                value = min(value, self.alpha_beta(new_board, depth - 1, alpha, beta, True))
                beta = min(beta, value)
                if alpha >= beta: break
            return value

    def get_best_move(self, board: QuoridorBoard) -> Tuple[str, Union[Tuple[int, int], Tuple[int, int, str]]]:
        """
        Détermine le meilleur coup à jouer pour l'IA en lançant l'algorithme Alpha-Beta.

        Args:
            board (QuoridorBoard): L'état actuel du plateau.

        Returns:
            Tuple: Le meilleur coup trouvé (ex: ("MOVE", (4, 5)) ou ("WALL", (4, 4, 'H'))).
        """
        # On récupère les coups possibles (optimisés)
        moves = get_optimized_moves(board, self.player_id)

        best_move = None
        best_value = -math.inf

        # Initialisation alpha/beta pour la racine
        alpha = -math.inf
        beta = math.inf

        # Positions récentes (les 6 dernières) pour détecter l'oscillation
        recent = set(self.position_history[-6:])

        # On itère sur les coups de premier niveau pour trouver lequel donne le meilleur score
        for move_type, data in moves:
            # Simulation du coup
            new_board = _fast_copy(board)
            if move_type == "MOVE":
                new_board.move_pawn(self.player_id, data)
            else:
                # A4 — Application directe des murs pré-validés
                new_board.walls.add(data)
                new_board.walls_count[self.player_id] -= 1

            # Appel récursif (c'est maintenant au tour de MIN de jouer, d'où False)
            raw_value = self.alpha_beta(new_board, self.depth - 1, alpha, beta, False)

            # A1 — Séparer valeur brute (pour alpha) et valeur ajustée (pour best_value)
            adjusted_value = raw_value
            if move_type == "MOVE" and data in recent:
                adjusted_value -= 50

            if adjusted_value > best_value or (adjusted_value == best_value and random.random() < 0.5):
                best_value = adjusted_value
                best_move = (move_type, data)

            # A1 — Alpha basé sur le score brut, pas le score pénalisé
            alpha = max(alpha, raw_value)

        # Enregistrer la position choisie dans l'historique
        if best_move and best_move[0] == "MOVE":
            self.position_history.append(best_move[1])
            # Garder seulement les 10 dernières positions
            if len(self.position_history) > 10:
                self.position_history = self.position_history[-10:]

        return best_move
