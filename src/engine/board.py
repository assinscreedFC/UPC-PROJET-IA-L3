from typing import List, Tuple, Set, Dict, Optional
from collections import deque
import copy

class QuoridorBoard:
    """
    Gère l'état logique du plateau de Quoridor, les déplacements et la validation des règles.
    """

    def __init__(self) -> None:
        """
        Initialise un plateau 9x9 avec les positions de départ et les stocks de murs.
        """
        self.size: int = 9
        # Joueur 1 (y=0) et Joueur 2 (y=8)
        self.positions: Dict[int, Tuple[int, int]] = {1: (4, 0), 2: (4, 8)}
        self.walls: Set[Tuple[int, int, str]] = set()
        self.walls_count: Dict[int, int] = {1: 10, 2: 10}
        self.winner: Optional[int] = None

    def copy(self) -> 'QuoridorBoard':
        """
        Crée une copie profonde de l'état actuel du plateau.

        Returns:
            QuoridorBoard: Une nouvelle instance identique mais indépendante.
        """
        return copy.deepcopy(self)

    def _is_wall_placement_valid(self, new_wall: Tuple[int, int, str]) -> bool:
        """
        Vérifie si un mur peut être posé sans chevauchement ni intersection illégale.

        Args:
            new_wall (Tuple[int, int, str]): Le mur à tester (x, y, orientation).

        Returns:
            bool: True si le placement est valide physiquement, False sinon.
        """
        nx, ny, no = new_wall
        for wx, wy, wo in self.walls:
            # Même point d'ancrage
            if nx == wx and ny == wy:
                return False
            # Chevauchement horizontal
            if no == 'H' and wo == 'H' and abs(nx - wx) < 2 and ny == wy:
                return False
            # Chevauchement vertical
            if no == 'V' and wo == 'V' and nx == wx and abs(ny - wy) < 2:
                return False
            # Intersection en croix (ne peut pas couper un mur perpendiculaire au centre)
            if no != wo and nx == wx and ny == wy:
                return False
        return True

    def place_wall(self, player_id: int, x: int, y: int, orientation: str) -> bool:
        """
        Tente de poser un mur sur le plateau.

        Args:
            player_id (int): L'identifiant du joueur posant le mur.
            x (int): Coordonnée X du point d'ancrage (0-7).
            y (int): Coordonnée Y du point d'ancrage (0-7).
            orientation (str): 'H' pour horizontal, 'V' pour vertical.

        Returns:
            bool: True si le mur a été posé, False si le coup est invalide.
        """
        if self.winner is not None or self.walls_count[player_id] <= 0:
            return False

        # Un mur occupe 2 unités, donc l'ancrage max est size-2 (index 7)
        if not (0 <= x < self.size - 1 and 0 <= y < self.size - 1):
            return False

        new_wall = (x, y, orientation)
        if not self._is_wall_placement_valid(new_wall):
            return False

        # Ajout temporaire pour vérifier l'accessibilité via BFS
        self.walls.add(new_wall)
        if not (self.is_path_available(1) and self.is_path_available(2)):
            self.walls.remove(new_wall)
            return False

        self.walls_count[player_id] -= 1
        return True

    def move_pawn(self, player_id: int, new_pos: Tuple[int, int]) -> bool:
        """
        Déplace le pion d'un joueur vers une nouvelle position.

        Args:
            player_id (int): L'identifiant du joueur qui se déplace (1 ou 2).
            new_pos (Tuple[int, int]): Les coordonnées cibles (x, y).

        Returns:
            bool: True si le déplacement a été effectué, False sinon.
        """
        if self.winner is not None:
            return False

        if new_pos not in self.get_legal_pawn_moves(player_id):
            return False

        self.positions[player_id] = new_pos

        # Vérification de la condition de victoire [cite: 38]
        if (player_id == 1 and new_pos[1] == 8) or (player_id == 2 and new_pos[1] == 0):
            self.winner = player_id
        return True

    def get_legal_pawn_moves(self, player_id: int) -> List[Tuple[int, int]]:
        """
        Calcule les déplacements possibles, incluant les sauts.

        Args:
            player_id (int): ID du joueur.

        Returns:
            List[Tuple[int, int]]: Liste des positions (x, y) légales.
        """
        x, y = self.positions[player_id]
        opp_id = 2 if player_id == 1 else 1
        opp_x, opp_y = self.positions[opp_id]
        moves: List[Tuple[int, int]] = []

        for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < self.size and 0 <= ny < self.size) or self.is_wall_blocking(x, y, nx, ny):
                continue

            if (nx, ny) == (opp_x, opp_y):
                jx, jy = nx + dx, ny + dy
                # Saut direct
                if 0 <= jx < self.size and 0 <= jy < self.size and not self.is_wall_blocking(nx, ny, jx, jy):
                    moves.append((jx, jy))
                else:
                    # Sauts diagonaux
                    for ddx, ddy in [(-1, 0), (1, 0)] if dx == 0 else [(0, -1), (0, 1)]:
                        dx_d, dy_d = nx + ddx, ny + ddy
                        if 0 <= dx_d < self.size and 0 <= dy_d < self.size:
                            if not self.is_wall_blocking(nx, ny, dx_d, dy_d):
                                moves.append((dx_d, dy_d))
            else:
                moves.append((nx, ny))
        return moves

    def is_path_available(self, player_id: int) -> bool:
        """
        Vérifie si un chemin existe vers la ligne d'arrivée (BFS).

        Args:
            player_id (int): ID du joueur.

        Returns:
            bool: True si un chemin est trouvé.
        """
        start = self.positions[player_id]
        target_y = 8 if player_id == 1 else 0
        queue = deque([start])
        visited = {start}
        while queue:
            cx, cy = queue.popleft()
            if cy == target_y: return True
            for next_pos in self.get_accessible_neighbors(cx, cy):
                if next_pos not in visited:
                    visited.add(next_pos)
                    queue.append(next_pos)
        return False

    def get_accessible_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Retourne les cases adjacentes non bloquées par un mur.

        Args:
            x, y (int): Coordonnées de départ.

        Returns:
            List[Tuple[int, int]]: Liste des voisins.
        """
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if not self.is_wall_blocking(x, y, nx, ny):
                    neighbors.append((nx, ny))
        return neighbors

    def is_wall_blocking(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """
        Vérifie si un mur sépare deux cases adjacentes.

        Args:
            x1, y1, x2, y2 (int): Coordonnées des deux cases.

        Returns:
            bool: True si bloqué.
        """
        if x1 == x2:
            my = min(y1, y2)
            return (x1, my, 'H') in self.walls or (x1 - 1, my, 'H') in self.walls
        if y1 == y2:
            mx = min(x1, x2)
            return (mx, y1, 'V') in self.walls or (mx, y1 - 1, 'V') in self.walls
        return False