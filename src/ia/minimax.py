import math
from typing import Tuple, Optional, List,Union
from src.engine.board import QuoridorBoard
from src.ia.evaluations import evaluate_board
from src.ia.moves_optimization import get_optimized_moves

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
        if depth == 0 or board.winner is not None:
            return evaluate_board(board, self.player_id, self.strategy)

        current_player = self.player_id if maximizing_player else (3 - self.player_id)
        moves = get_optimized_moves(board, current_player)

        if maximizing_player:
            value = -math.inf
            for type, data in moves:
                new_board = board.copy()
                if type == "MOVE":
                    new_board.move_pawn(current_player, data)
                else:
                    new_board.place_wall(current_player, *data)

                value = max(value, self.alpha_beta(new_board, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta: break
            return value
        else:
            value = math.inf
            for type, data in moves:
                new_board = board.copy()
                if type == "MOVE":
                    new_board.move_pawn(current_player, data)
                else:
                    new_board.place_wall(current_player, *data)

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

        # On itère sur les coups de premier niveau pour trouver lequel donne le meilleur score
        for type, data in moves:
            # Simulation du coup
            new_board = board.copy()
            if type == "MOVE":
                new_board.move_pawn(self.player_id, data)
            else:
                new_board.place_wall(self.player_id, *data)

            # Appel récursif (c'est maintenant au tour de MIN de jouer, d'où False)
            value = self.alpha_beta(new_board, self.depth - 1, alpha, beta, False)

            if value > best_value:
                best_value = value
                best_move = (type, data)

            # Mise à jour de l'alpha pour l'élagage
            alpha = max(alpha, value)

        return best_move