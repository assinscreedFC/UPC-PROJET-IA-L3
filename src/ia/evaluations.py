from src.engine.board import QuoridorBoard
from collections import deque


def evaluate_board(board: QuoridorBoard, player_id: int, strategy: str) -> float:
    """
    Fonction chapeau qui dirige vers la bonne heuristique.
    """
    if strategy == "simple":
        return heuristic_simple_distance(board, player_id)
    elif strategy == "advanced":
        return heuristic_shortest_path(board, player_id)
    else:
        # Par défaut
        return heuristic_simple_distance(board, player_id)


def heuristic_simple_distance(board: QuoridorBoard, player_id: int) -> float:
    """
    Niveau 1 : Différence de distance "à vol d'oiseau" (Manhattan) vers la ligne d'arrivée.
    Rapide mais peu précise car elle ignore les murs.
    """
    opp_id = 2 if player_id == 1 else 1

    p_x, p_y = board.positions[player_id]
    o_x, o_y = board.positions[opp_id]

    # Cibles : ligne 8 pour J1, ligne 0 pour J2
    target_p = 8 if player_id == 1 else 0
    target_o = 8 if opp_id == 1 else 0

    dist_p = abs(target_p - p_y)
    dist_o = abs(target_o - o_y)

    # Plus ma distance est petite, mieux c'est. Plus celle de l'adversaire est grande, mieux c'est.
    return (dist_o - dist_p) * 10


def heuristic_shortest_path(board: QuoridorBoard, player_id: int) -> float:
    """
    Niveau 2/3 : Utilise le BFS pour connaître la distance RÉELLE en contournant les murs.
    Beaucoup plus fort stratégiquement.
    """
    opp_id = 2 if player_id == 1 else 1

    len_p = bfs_shortest_path_len(board, player_id)
    len_o = bfs_shortest_path_len(board, opp_id)

    # Bonus pour les murs restants (stratégique)
    walls_score = (board.walls_count[player_id] - board.walls_count[opp_id]) * 5

    # Score basé sur la différence de chemin réel + murs
    return (len_o - len_p) * 10 + walls_score


def bfs_shortest_path_len(board: QuoridorBoard, pid: int) -> int:
    """
    Calcule la longueur du chemin le plus court vers la victoire.
    Retourne une grande valeur (100) si bloqué (théoriquement impossible avec nos règles).
    """
    start = board.positions[pid]
    target_y = 8 if pid == 1 else 0

    queue = deque([(start, 0)])  # (pos, distance)
    visited = {start}

    while queue:
        (cx, cy), dist = queue.popleft()
        if cy == target_y:
            return dist

        for nx, ny in board.get_accessible_neighbors(cx, cy):
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), dist + 1))

    return 100  # Valeur de pénalité si aucun chemin trouvé