import time
import csv
from typing import List, Dict
from src.engine.board import QuoridorBoard
from src.ia.minimax import QuoridorIA


def play_game(ia1: QuoridorIA, ia2: QuoridorIA) -> Dict:
    """
    Simule une partie complète entre deux IA (sans affichage).

    Args:
        ia1 (QuoridorIA): L'IA qui commence (Joueur 1).
        ia2 (QuoridorIA): L'IA qui suit (Joueur 2).

    Returns:
        Dict: Dictionnaire contenant le vainqueur, le nombre de coups et la durée.
    """
    board = QuoridorBoard()
    turn = 1
    move_count = 0
    start_time = time.time()

    # Limite de sécurité pour éviter les boucles infinies (match nul)
    MAX_MOVES = 200

    while board.winner is None and move_count < MAX_MOVES:
        current_ia = ia1 if turn == 1 else ia2

        # L'IA décide son coup
        move = current_ia.get_best_move(board)

        if move is None:
            break  # Plus de coups possibles (cas rare)

        type, data = move

        # Application du coup
        if type == "MOVE":
            board.move_pawn(current_ia.player_id, data)
        else:
            board.place_wall(current_ia.player_id, *data)

        move_count += 1
        turn = 2 if turn == 1 else 1

    duration = time.time() - start_time

    return {
        "winner": board.winner,
        "moves": move_count,
        "time": round(duration, 4),
        "p1_walls_left": board.walls_count[1],
        "p2_walls_left": board.walls_count[2]
    }


def run_tournament(n_games: int, depth_j1: int, depth_j2: int):
    """
    Lance une série de parties et enregistre les résultats dans un CSV.

    Args:
        n_games (int): Nombre de parties à jouer (min 50 selon le sujet).
        depth_j1 (int): Niveau de difficulté du Joueur 1.
        depth_j2 (int): Niveau de difficulté du Joueur 2.
    """
    results = []
    print(f"🏆 Lancement du tournoi : IA Niv{depth_j1} vs IA Niv{depth_j2} ({n_games} parties)")

    # Initialisation des IA
    # Stratégie 'advanced' pour les deux pour comparer uniquement la profondeur
    player1 = QuoridorIA(1, depth=depth_j1, strategy="advanced")
    player2 = QuoridorIA(2, depth=depth_j2, strategy="advanced")

    wins = {1: 0, 2: 0, "Draw": 0}

    for i in range(n_games):
        print(f"   Partie {i + 1}/{n_games}...", end="\r")

        # Pour éviter le déterminisme absolu (mêmes parties), on peut alterner qui commence
        # Mais ici, on garde J1 = IA1 pour respecter les paramètres
        stats = play_game(player1, player2)

        if stats["winner"] is None:
            wins["Draw"] += 1
        else:
            wins[stats["winner"]] += 1

        results.append(stats)

    print(f"\n✅ Tournoi terminé !")
    print(f"Victoires J1 (Prof {depth_j1}): {wins[1]}")
    print(f"Victoires J2 (Prof {depth_j2}): {wins[2]}")
    print(f"Matchs nuls : {wins['Draw']}")

    # Sauvegarde CSV pour le rapport
    filename = f"../data/results/tournoi_d{depth_j1}_vs_d{depth_j2}.csv"
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["winner", "moves", "time", "p1_walls_left", "p2_walls_left"])
            writer.writeheader()
            writer.writerows(results)
        print(f"📁 Données sauvegardées dans {filename}")
    except FileNotFoundError:
        print("⚠️ Erreur: Le dossier 'data/results' n'existe pas. Créez-le ou lancez setup_project.ps1")


if __name__ == "__main__":
    # Exemple : 50 parties entre une IA Profondeur 1 (Rapide) et Profondeur 2 (Plus maline)
    run_tournament(50, depth_j1=2, depth_j2=1)