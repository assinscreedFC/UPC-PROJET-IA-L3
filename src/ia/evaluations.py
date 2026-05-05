from src.engine.board import QuoridorBoard
from collections import deque


def evaluate_board(board: QuoridorBoard, player_id: int, strategy: str) -> float:
    """
    Sélecteur d'heuristique.
    """
    if strategy == "simple":
        return heuristic_simple_distance(board, player_id)
    elif strategy == "advanced":
        return heuristic_shortest_path(board, player_id)
    elif strategy == "expert":
        return heuristic_expert(board, player_id)
    else:
        return heuristic_shortest_path(board, player_id)


def heuristic_simple_distance(board: QuoridorBoard, player_id: int) -> float:
    """
    Niveau 1 : Différentiel de chemin pur.
    Ratio symétrique 1:1 — stable à toutes les profondeurs de recherche.
    """
    opp_id = 2 if player_id == 1 else 1
    len_p = bfs_shortest_path_len(board, player_id)
    len_o = bfs_shortest_path_len(board, opp_id)

    if len_p == 0: return 100000
    if len_o == 0: return -100000

    return (len_o - len_p) * 10


def heuristic_shortest_path(board: QuoridorBoard, player_id: int) -> float:
    """
    Niveau 2 : Différentiel + économie de murs.
    L'IA comprend que les murs sont une ressource stratégique.
    """
    opp_id = 2 if player_id == 1 else 1
    len_p = bfs_shortest_path_len(board, player_id)
    len_o = bfs_shortest_path_len(board, opp_id)

    if len_p == 0: return 100000
    if len_o == 0: return -100000

    # Base symétrique
    score = (len_o - len_p) * 10

    # Économie de murs : avoir plus de murs restants = avantage stratégique
    walls_diff = board.walls_count[player_id] - board.walls_count[opp_id]
    score += walls_diff * 5

    return score


def heuristic_expert(board: QuoridorBoard, player_id: int) -> float:
    """
    Niveau 3 : Différentiel + économie de murs + progression + tempo.
    L'IA évalue finement la position globale.
    """
    opp_id = 2 if player_id == 1 else 1
    len_p = bfs_shortest_path_len(board, player_id)
    len_o = bfs_shortest_path_len(board, opp_id)

    if len_p == 0: return 1000000
    if len_o == 0: return -1000000

    # 1. Base symétrique
    score = (len_o - len_p) * 10

    # 2. Économie de murs (poids plus fort que advanced)
    my_walls = board.walls_count[player_id]
    opp_walls = board.walls_count[opp_id]
    score += (my_walls - opp_walls) * 5

    # 3. Progression vers l'objectif
    p_y = board.positions[player_id][1]
    progress = p_y if player_id == 1 else (8 - p_y)
    score += progress * 3

    # 4. Tempo : quand on mène la course ET qu'on a des murs, l'avantage
    #    est amplifié car on peut défendre notre avance
    path_diff = len_o - len_p
    if path_diff > 0 and my_walls > 0:
        score += path_diff * 3

    # 5. Endgame : si l'adversaire n'a plus de murs, foncer
    if opp_walls == 0:
        score += progress * 2

    return score


def bfs_shortest_path_len(board: QuoridorBoard, pid: int) -> int:
    """
    Calcule la distance réelle (BFS) vers la victoire.
    """
    start = board.positions[pid]
    target_y = 8 if pid == 1 else 0

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

    return 50  # Indique un blocage majeur
