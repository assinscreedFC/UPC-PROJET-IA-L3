from typing import List, Tuple, Union
from collections import deque
from src.engine.board import QuoridorBoard

# Définition d'un type pour les coups : ("MOVE", (x,y)) ou ("WALL", (x,y,o))
MoveType = Tuple[str, Union[Tuple[int, int], Tuple[int, int, str]]]


def _bfs_distance(board: QuoridorBoard, player_id: int) -> int:
    """Calcule la distance BFS du joueur vers sa ligne d'arrivée."""
    start = board.positions[player_id]
    target_y = 8 if player_id == 1 else 0
    queue = deque([(start, 0)])
    visited = {start}
    while queue:
        (cx, cy), dist = queue.popleft()
        if cy == target_y:
            return dist
        for nx, ny in board.get_accessible_neighbors(cx, cy):
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), dist + 1))
    return 100


def get_optimized_moves(board: QuoridorBoard, player_id: int) -> List[MoveType]:
    """
    Génère une liste priorisée et réduite de coups pour l'IA.

    Filtre les murs qui bloqueraient le joueur lui-même plus que l'adversaire.
    """
    moves: List[MoveType] = []
    opp_id = 3 - player_id

    # 1. Ajouter TOUS les déplacements de pions (Priorité absolue)
    pawn_moves = board.get_legal_pawn_moves(player_id)
    for pos in pawn_moves:
        moves.append(("MOVE", pos))

    # 2. Ajouter les murs INTELLIGENTS (filtrés)
    if board.walls_count[player_id] > 0:
        p1_x, p1_y = board.positions[1]
        p2_x, p2_y = board.positions[2]

        # Boîte englobante autour des joueurs + 2 cases de marge
        min_x = max(0, min(p1_x, p2_x) - 2)
        max_x = min(board.size - 1, max(p1_x, p2_x) + 2)
        min_y = max(0, min(p1_y, p2_y) - 2)
        max_y = min(board.size - 1, max(p1_y, p2_y) + 2)

        # Distances actuelles avant pose de mur
        dist_self_before = _bfs_distance(board, player_id)
        dist_opp_before = _bfs_distance(board, opp_id)

        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                for orientation in ['H', 'V']:
                    if not board._is_wall_placement_valid((x, y, orientation)):
                        continue

                    # Simuler la pose du mur pour vérifier l'impact
                    board.walls.add((x, y, orientation))

                    # Vérifier que les deux joueurs ont encore un chemin
                    if not (board.is_path_available(1) and board.is_path_available(2)):
                        board.walls.discard((x, y, orientation))
                        continue

                    dist_self_after = _bfs_distance(board, player_id)
                    dist_opp_after = _bfs_distance(board, opp_id)

                    board.walls.discard((x, y, orientation))

                    # Rejeter les murs qui nous ralentissent plus que l'adversaire
                    gain_opp = dist_opp_after - dist_opp_before  # positif = bon pour nous
                    cost_self = dist_self_after - dist_self_before  # positif = mauvais pour nous

                    # Garder le mur si :
                    # - il ralentit l'adversaire plus que nous (offensif)
                    # - OU il ralentit l'adversaire sans nous affecter (neutre-offensif)
                    # Rejeter seulement les murs clairement mauvais (nous coûtent plus)
                    if gain_opp >= cost_self and gain_opp > 0:
                        moves.append(("WALL", (x, y, orientation)))

    return moves