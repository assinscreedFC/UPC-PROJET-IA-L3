from src.engine.board import QuoridorBoard
from collections import deque
import random


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
    Niveau 1 : Ratio de base.
    L'IA commence à comprendre que bloquer vaut plus que bouger.
    """
    opp_id = 2 if player_id == 1 else 1
    len_p = bfs_shortest_path_len(board, player_id)
    len_o = bfs_shortest_path_len(board, opp_id)

    # On donne 2x plus d'importance au chemin de l'adversaire.
    # Si je fais un pas : +10 pts. Si je le bloque d'une case : +20 pts.
    score = (len_o * 20) - (len_p * 10)

    return score + random.uniform(-0.1, 0.1)


def heuristic_shortest_path(board: QuoridorBoard, player_id: int) -> float:
    """
    Niveau 2 : Agressivité intermédiaire.
    Priorité au différentiel de chemin sans aucune pénalité de mur.
    """
    opp_id = 2 if player_id == 1 else 1
    len_p = bfs_shortest_path_len(board, player_id)
    len_o = bfs_shortest_path_len(board, opp_id)

    if len_p == 0: return 100000
    if len_o == 0: return -100000

    # Ratio 3:1 -> Bloquer est 3 fois plus gratifiant que d'avancer.
    score = (len_o * 30) - (len_p * 10)

    # Bonus de centralité pour ne pas rester coincé sur les bords
    pos_x = board.positions[player_id][0]
    score += (4 - abs(4 - pos_x)) * 5

    return score + random.uniform(-0.2, 0.2)


def heuristic_expert(board: QuoridorBoard, player_id: int) -> float:
    """
    Niveau 3 : Maître du blocage et du Tempo.
    Priorité absolue au sabotage du chemin adverse.
    """
    opp_id = 2 if player_id == 1 else 1
    len_p = bfs_shortest_path_len(board, player_id)
    len_o = bfs_shortest_path_len(board, opp_id)

    if len_p == 0: return 1000000
    if len_o == 0: return -1000000

    # 1. Le Différentiel Massif
    # Ratio 4:1 -> L'IA est obsédée par l'allongement du chemin adverse.
    score = (len_o * 40) - (len_p * 10)

    # 2. Bonus de Menace (Sabotage préventif)
    # Si l'adversaire est à moins de 7 cases, chaque case qu'il gagne nous coûte très cher.
    # Cela force l'IA à poser des murs AVANT qu'il ne soit trop tard.
    if len_o <= 7:
        score += (10 - len_o) * 100

    # 3. Centralité stratégique
    pos_x = board.positions[player_id][0]
    score += (4 - abs(4 - pos_x)) * 10

    # 4. Anti-stagnation
    # On ajoute une petite récompense liée à la coordonnée Y pour s'assurer
    # que si aucun mur n'est utile, l'IA avance au lieu de faire du surplace.
    p_y = board.positions[player_id][1]
    progress_y = p_y if player_id == 1 else (8 - p_y)
    score += progress_y * 2

    return score + random.uniform(-0.05, 0.05)


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