import time
import csv
from typing import Dict
from src.engine.board import QuoridorBoard
from src.ia.minimax import QuoridorIA


def play_game(ia1: QuoridorIA, ia2: QuoridorIA) -> Dict:
    """
    Simule une partie complète entre deux IA.
    """
    board = QuoridorBoard()
    turn = 1
    move_count = 0
    start_time = time.time()
    MAX_MOVES = 200

    while board.winner is None and move_count < MAX_MOVES:
        current_ia = ia1 if turn == 1 else ia2
        move = current_ia.get_best_move(board)

        if move is None: break

        type, data = move
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
        "p1_walls": board.walls_count[1],
        "p2_walls": board.walls_count[2]
    }


def run_tournament(n_games: int, strat_j1: str, depth_j1: int, strat_j2: str, depth_j2: int):
    """
    Lance un tournoi configurable.
    """
    results = []
    print(f"🏆 Tournoi : {strat_j1.upper()}(D{depth_j1}) vs {strat_j2.upper()}(D{depth_j2})")
    print(f"   Nombre de parties : {n_games}")

    # Initialisation des IA avec les bonnes stratégies
    player1 = QuoridorIA(1, depth=depth_j1, strategy=strat_j1)
    player2 = QuoridorIA(2, depth=depth_j2, strategy=strat_j2)

    wins = {1: 0, 2: 0, "Draw": 0}

    for i in range(n_games):
        if i % 5 == 0: print(f"   Partie {i}/{n_games}...", end="\r")

        stats = play_game(player1, player2)

        if stats["winner"] is None:
            wins["Draw"] += 1
        else:
            wins[stats["winner"]] += 1
        results.append(stats)

    print(f"\n✅ Tournoi terminé !")
    print(f"Victoires J1 ({strat_j1}): {wins[1]} ({wins[1] / n_games * 100}%)")
    print(f"Victoires J2 ({strat_j2}): {wins[2]} ({wins[2] / n_games * 100}%)")
    print(f"Nuls : {wins['Draw']}")

    # Nom de fichier explicite
    filename = f"data/results/tournoi_{strat_j1}_d{depth_j1}_vs_{strat_j2}_d{depth_j2}.csv"
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["winner", "moves", "time", "p1_walls", "p2_walls"])
            writer.writeheader()
            writer.writerows(results)
    except:
        pass


if __name__ == "__main__":
    # EXEMPLE DE TOURNOI À LANCER POUR LE RAPPORT :

    # Comparaison : L'IA "Advanced" (Ancienne) vs "Expert" (Nouvelle)
    # Même profondeur (2) pour voir si la stratégie fait la différence.
    run_tournament(
        n_games=1,
        strat_j1="expert", depth_j1=10,
        strat_j2="expert", depth_j2=10
    )