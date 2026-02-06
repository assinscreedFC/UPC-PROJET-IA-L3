import pytest
from src.engine.board import QuoridorBoard

@pytest.fixture
def board():
    return QuoridorBoard()

# --- TESTS DE MOUVEMENTS ET SAUTS ---

def test_pawn_jump_straight(board):
    """Test du saut direct par-dessus l'adversaire."""
    board.positions[1], board.positions[2] = (4, 4), (4, 5)
    moves = board.get_legal_pawn_moves(1)
    assert (4, 6) in moves

def test_pawn_jump_diagonal_due_to_wall(board):
    """Test du saut diagonal quand un mur bloque le saut direct."""
    board.positions[1], board.positions[2] = (4, 4), (4, 5)
    board.walls.add((4, 5, 'H')) # Mur derrière le J2
    moves = board.get_legal_pawn_moves(1)
    assert (4, 6) not in moves
    assert (3, 5) in moves and (5, 5) in moves

def test_pawn_jump_diagonal_edge(board):
    """Test du saut diagonal quand on est au bord du plateau."""
    board.positions[1], board.positions[2] = (4, 7), (4, 8)
    moves = board.get_legal_pawn_moves(1)
    assert (3, 8) in moves and (5, 8) in moves

# --- TESTS DE MURS ---

def test_invalid_wall_intersection(board):
    """Test de l'interdiction de croiser des murs perpendiculairement."""
    board.place_wall(1, 4, 4, 'H')
    assert board.place_wall(2, 4, 4, 'V') is False

def test_wall_overlap_horizontal(board):
    """Test du chevauchement partiel de murs horizontaux."""
    board.place_wall(1, 4, 4, 'H')
    assert board.place_wall(2, 5, 4, 'H') is False

def test_wall_blocking_all_paths(board):
    """Test de la règle interdisant d'enfermer un joueur."""
    for i in range(8):
        board.place_wall(1, i, 1, 'H')
    # Le dernier mur qui fermerait tout le passage
    assert board.place_wall(1, 7, 1, 'H') is False

# --- TESTS DE VICTOIRE ET ETATS ---

def test_victory_condition(board):
    """Vérifie que le jeu s'arrête et déclare un vainqueur."""
    board.positions[1] = (4, 7)
    assert board.move_pawn(1, (4, 8)) is True
    assert board.winner == 1
    # Plus aucun mouvement possible après victoire
    assert board.move_pawn(2, (4, 7)) is False

def test_out_of_walls(board):
    """Vérifie qu'on ne peut pas poser plus de 10 murs."""
    board.walls_count[1] = 0
    assert board.place_wall(1, 0, 0, 'H') is False