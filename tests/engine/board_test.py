import pytest
from src.engine.board import QuoridorBoard


@pytest.fixture
def board():
    """Fixture : Crée un plateau neuf avant chaque test."""
    return QuoridorBoard()


# ==========================================
# 1. TESTS D'INITIALISATION ET UTILITAIRES
# ==========================================

def test_initial_state(board):
    """Vérifie l'état de départ du plateau."""
    assert board.size == 9
    assert board.positions[1] == (4, 0)
    assert board.positions[2] == (4, 8)
    assert board.walls_count[1] == 10
    assert board.walls_count[2] == 10
    assert board.winner is None
    assert len(board.walls) == 0


def test_copy_board(board):
    """Vérifie que la méthode copy() crée bien une instance indépendante."""
    board.positions[1] = (0, 0)
    board.walls.add((0, 0, 'H'))

    new_board = board.copy()
    new_board.positions[1] = (1, 1)
    new_board.walls.add((1, 1, 'H'))

    # L'original ne doit pas avoir bougé
    assert board.positions[1] == (0, 0)
    assert len(board.walls) == 1
    # La copie doit être modifiée
    assert new_board.positions[1] == (1, 1)
    assert len(new_board.walls) == 2


# ==========================================
# 2. TESTS DE DÉPLACEMENTS SIMPLES
# ==========================================

def test_move_pawn_valid(board):
    """Test un déplacement simple vers le haut."""
    # J1 est en (4, 0), déplacement vers (4, 1) autorisé
    assert board.move_pawn(1, (4, 1)) is True
    assert board.positions[1] == (4, 1)


def test_move_pawn_invalid_distance(board):
    """Test un déplacement de plus d'une case (interdit)."""
    assert board.move_pawn(1, (4, 2)) is False
    assert board.positions[1] == (4, 0)  # Pas bougé


def test_move_pawn_out_of_bounds(board):
    """Test un déplacement hors du plateau."""
    board.positions[1] = (0, 0)
    assert board.move_pawn(1, (-1, 0)) is False


def test_move_pawn_blocked_by_wall(board):
    """Test un déplacement bloqué par un mur."""
    # Mur horizontal devant J1
    board.place_wall(2, 4, 0, 'H')
    # Tente de passer au travers
    assert board.move_pawn(1, (4, 1)) is False
    # Vérifie qu'on peut contourner
    assert board.move_pawn(1, (5, 0)) is True


# ==========================================
# 3. TESTS DE SAUTS (RÈGLES COMPLEXES)
# ==========================================

def test_pawn_jump_straight(board):
    """Test saut direct par-dessus l'adversaire."""
    # On place les joueurs face à face
    board.positions[1] = (4, 4)
    board.positions[2] = (4, 5)

    # J1 saute par dessus J2 pour aller en (4, 6)
    moves = board.get_legal_pawn_moves(1)
    assert (4, 6) in moves
    assert board.move_pawn(1, (4, 6)) is True


def test_pawn_jump_diagonal_wall_behind(board):
    """Test saut diagonal car mur derrière l'adversaire."""
    board.positions[1] = (4, 4)
    board.positions[2] = (4, 5)
    # Mur derrière J2 empêchant le saut tout droit
    board.walls.add((4, 5, 'H'))

    moves = board.get_legal_pawn_moves(1)
    assert (4, 6) not in moves  # Saut direct bloqué
    assert (3, 5) in moves  # Diagonale Gauche OK
    assert (5, 5) in moves  # Diagonale Droite OK

    # Exécution du saut diagonal
    assert board.move_pawn(1, (3, 5)) is True


def test_pawn_jump_diagonal_edge(board):
    """Test saut diagonal car bord du plateau derrière."""
    board.positions[1] = (4, 7)
    board.positions[2] = (4, 8)  # J2 est au bord

    moves = board.get_legal_pawn_moves(1)
    assert (4, 9) not in moves  # Hors plateau
    assert (3, 8) in moves  # Diag OK
    assert (5, 8) in moves  # Diag OK


# ==========================================
# 4. TESTS DE MURS (POSE & VALIDATION)
# ==========================================

def test_place_wall_valid(board):
    """Test pose de mur valide."""
    assert board.place_wall(1, 0, 0, 'H') is True
    assert (0, 0, 'H') in board.walls
    assert board.walls_count[1] == 9


def test_place_wall_no_stock(board):
    """Test impossibilité de poser sans stock."""
    board.walls_count[1] = 0
    assert board.place_wall(1, 0, 0, 'H') is False


def test_place_wall_overlap(board):
    """Test chevauchements interdits."""
    board.place_wall(1, 4, 4, 'H')

    # Exactement au même endroit
    assert board.place_wall(2, 4, 4, 'H') is False
    # Croisement (Intersection interdite)
    assert board.place_wall(2, 4, 4, 'V') is False
    # Chevauchement partiel horizontal
    assert board.place_wall(2, 5, 4, 'H') is False
    assert board.place_wall(2, 3, 4, 'H') is False


def test_place_wall_enclosing_player(board):
    """Test interdiction d'enfermer un joueur (BFS check)."""
    # Cas simple : J1 bloqué dans le coin (0,0)
    board.positions[1] = (0, 0)
    # On ferme autour de lui
    board.place_wall(2, 0, 0, 'H')  # Bloque le haut

    # Tente de bloquer le coté droit : doit être refusé car J1 serait enfermé
    assert board.place_wall(2, 0, 0, 'V') is False


# ==========================================
# 5. TESTS DE VICTOIRE (CORRIGÉS)
# ==========================================

def test_victory_condition_j1(board):
    """Vérifie la victoire du Joueur 1 (atteindre ligne 8)."""
    # ÉTAPE CRUCIALE : On déplace J2 loin de la ligne d'arrivée !
    # Sinon J2 est en (4, 8) et bloque le coup gagnant de J1.
    board.positions[2] = (0, 0)

    # Placer J1 juste avant la ligne d'arrivée
    board.positions[1] = (4, 7)

    # Coup gagnant : J1 avance sur la ligne 8
    assert board.move_pawn(1, (4, 8)) is True

    # [cite_start]Vérification que le statut de victoire est bien mis à jour [cite: 38]
    assert board.winner == 1

    # Vérifie que le jeu est verrouillé après victoire
    assert board.move_pawn(2, (0, 1)) is False


def test_victory_condition_j2(board):
    """Vérifie la victoire du Joueur 2 (atteindre ligne 0)."""
    # ÉTAPE CRUCIALE : On déplace J1 loin de la ligne d'arrivée de J2
    board.positions[1] = (8, 8)

    # Placer J2 juste avant sa ligne d'arrivée (qui est 0)
    board.positions[2] = (4, 1)

    # Coup gagnant
    assert board.move_pawn(2, (4, 0)) is True
    assert board.winner == 2