from typing import List, Tuple, Union
from src.engine.board import QuoridorBoard

# Définition d'un type pour les coups : ("MOVE", (x,y)) ou ("WALL", (x,y,o))
MoveType = Tuple[str, Union[Tuple[int, int], Tuple[int, int, str]]]


def get_optimized_moves(board: QuoridorBoard, player_id: int) -> List[MoveType]:
    """
    Génère une liste priorisée et réduite de coups pour l'IA.

    Cette fonction est cruciale pour la performance de l'Alpha-Beta. Elle évite
    de tester des murs inutiles aux quatre coins du plateau.

    Args:
        board (QuoridorBoard): L'instance actuelle du plateau.
        player_id (int): L'identifiant du joueur qui doit jouer.

    Returns:
        List[MoveType]: Une liste de tuples décrivant les coups possibles.
                        Ex: [('MOVE', (4, 1)), ('WALL', (4, 0, 'H')), ...]
    """
    moves: List[MoveType] = []

    # 1. Ajouter TOUS les déplacements de pions (Priorité absolue)
    # Les mouvements sont peu nombreux (max 4 ou 5) et font avancer la partie.
    pawn_moves = board.get_legal_pawn_moves(player_id)
    for pos in pawn_moves:
        moves.append(("MOVE", pos))

    # 2. Ajouter les murs INTELLIGENTS (Heuristique de proximité)
    # Si le joueur a encore des murs, on ne considère que ceux autour des joueurs.
    if board.walls_count[player_id] > 0:
        # On récupère les positions des deux joueurs pour définir une "zone d'intérêt"
        p1_x, p1_y = board.positions[1]
        p2_x, p2_y = board.positions[2]

        # On définit une boîte englobante autour des joueurs + 2 cases de marge
        min_x = max(0, min(p1_x, p2_x) - 2)
        max_x = min(board.size - 1, max(p1_x, p2_x) + 2)
        min_y = max(0, min(p1_y, p2_y) - 2)
        max_y = min(board.size - 1, max(p1_y, p2_y) + 2)

        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                for orientation in ['H', 'V']:
                    # On ne garde que les murs physiquement posables
                    # Note: On utilise la méthode 'privée' pour tester vite sans copier tout le plateau
                    if board._is_wall_placement_valid((x, y, orientation)):
                        moves.append(("WALL", (x, y, orientation)))

    return moves