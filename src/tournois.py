import time
import csv
import os
from typing import Dict, List, Tuple
from itertools import combinations
from src.engine.board import QuoridorBoard
from src.ia.minimax import QuoridorIA


# ============================================================
# 8 PARTICIPANTS — combinaisons depth x strategie
# ============================================================

PARTICIPANTS = {
    "Naive":        {"depth": 1, "strategy": "simple"},
    "Prudente":     {"depth": 1, "strategy": "advanced"},
    "Agressive":    {"depth": 1, "strategy": "expert"},
    "Calculatrice": {"depth": 2, "strategy": "simple"},
    "Stratege":     {"depth": 2, "strategy": "advanced"},
    "Commandante":  {"depth": 2, "strategy": "expert"},
    "Visionnaire":  {"depth": 3, "strategy": "advanced"},
    "Maitresse":    {"depth": 3, "strategy": "expert"},
}

# Composition des poules (melange de niveaux dans chaque groupe)
GROUPE_A = ["Naive", "Stratege", "Agressive", "Visionnaire"]
GROUPE_B = ["Prudente", "Calculatrice", "Commandante", "Maitresse"]


# ============================================================
# SIMULATION D'UN MATCH
# ============================================================

def play_game(ia1: QuoridorIA, ia2: QuoridorIA) -> Dict:
    """Simule une partie complete entre deux IA."""
    board = QuoridorBoard()
    turn = 1
    move_count = 0
    start_time = time.time()
    MAX_MOVES = 200

    while board.winner is None and move_count < MAX_MOVES:
        current_ia = ia1 if turn == 1 else ia2
        move = current_ia.get_best_move(board)
        if move is None:
            break

        move_type, data = move
        if move_type == "MOVE":
            board.move_pawn(current_ia.player_id, data)
        else:
            board.place_wall(current_ia.player_id, *data)

        move_count += 1
        turn = 2 if turn == 1 else 1

    return {
        "winner_id": board.winner,
        "moves": move_count,
        "time": round(time.time() - start_time, 4),
        "p1_walls_left": board.walls_count[1],
        "p2_walls_left": board.walls_count[2],
    }


def play_match(name1: str, name2: str, phase: str, match_num: int) -> Dict:
    """Joue un seul match entre deux IA nommees. Retourne le resultat detaille."""
    cfg1 = PARTICIPANTS[name1]
    cfg2 = PARTICIPANTS[name2]

    ia1 = QuoridorIA(1, depth=cfg1["depth"], strategy=cfg1["strategy"])
    ia2 = QuoridorIA(2, depth=cfg2["depth"], strategy=cfg2["strategy"])

    stats = play_game(ia1, ia2)

    if stats["winner_id"] == 1:
        winner = name1
    elif stats["winner_id"] == 2:
        winner = name2
    else:
        winner = "Nul"

    print(f"    [{match_num:>2}] {name1} vs {name2} -> {winner} ({stats['moves']} coups, {stats['time']:.2f}s)")

    return {
        "phase": phase,
        "match": match_num,
        "ia1": name1,
        "ia1_depth": cfg1["depth"],
        "ia1_strategy": cfg1["strategy"],
        "ia2": name2,
        "ia2_depth": cfg2["depth"],
        "ia2_strategy": cfg2["strategy"],
        "winner": winner,
        "moves": stats["moves"],
        "time": stats["time"],
        "p1_walls_used": 10 - stats["p1_walls_left"],
        "p2_walls_used": 10 - stats["p2_walls_left"],
    }


# ============================================================
# PHASE DE POULES
# ============================================================

def play_group_stage(group_name: str, members: List[str], n_rounds: int = 3) -> Tuple[List[Dict], List[str]]:
    """
    Phase de poules : chaque paire joue n_rounds fois.
    Retourne les resultats et le classement (par nombre de victoires).
    """
    print(f"\n{'='*60}")
    print(f"  POULE {group_name} : {', '.join(members)}")
    print(f"  ({n_rounds} matchs par paire = {len(list(combinations(members, 2))) * n_rounds} matchs)")
    print(f"{'='*60}")

    results = []
    match_num = 0

    # Chaque paire joue n_rounds fois
    pairs = list(combinations(members, 2))
    for round_num in range(1, n_rounds + 1):
        print(f"\n  --- Journee {round_num} ---")
        for name1, name2 in pairs:
            match_num += 1
            # Alterner qui est J1/J2 a chaque round
            if round_num % 2 == 0:
                name1, name2 = name2, name1
            result = play_match(name1, name2, f"Poule {group_name} - J{round_num}", match_num)
            results.append(result)

    # Classement par victoires
    wins = {m: 0 for m in members}
    for r in results:
        if r["winner"] in wins:
            wins[r["winner"]] += 1

    ranking = sorted(members, key=lambda m: wins[m], reverse=True)

    print(f"\n  Classement Poule {group_name} :")
    for i, name in enumerate(ranking, 1):
        print(f"    {i}. {name:15s} - {wins[name]} victoires")

    return results, ranking


# ============================================================
# PHASE ELIMINATOIRE
# ============================================================

def play_knockout(rankings_a: List[str], rankings_b: List[str]) -> Tuple[List[Dict], List[str]]:
    """
    Phase eliminatoire avec croisements inter-poules.
    Retourne les resultats et le classement final 1er-8eme.
    """
    results = []
    match_count = 0

    # --- QUARTS DE FINALE ---
    # Croisements : 1A vs 4B, 2A vs 3B, 1B vs 4A, 2B vs 3A
    print(f"\n{'='*60}")
    print(f"  QUARTS DE FINALE")
    print(f"{'='*60}")

    quarter_matchups = [
        (rankings_a[0], rankings_b[3]),  # 1A vs 4B
        (rankings_b[0], rankings_a[3]),  # 1B vs 4A
        (rankings_a[1], rankings_b[2]),  # 2A vs 3B
        (rankings_b[1], rankings_a[2]),  # 2B vs 3A
    ]

    quarter_winners = []
    quarter_losers = []

    for name1, name2 in quarter_matchups:
        match_count += 1
        result = play_match(name1, name2, "Quart de finale", match_count)
        results.append(result)

        if result["winner"] == name1 or result["winner"] == "Nul":
            # En cas de nul, J1 (mieux classe) avance
            quarter_winners.append(name1)
            quarter_losers.append(name2)
        else:
            quarter_winners.append(name2)
            quarter_losers.append(name1)

    # --- DEMI-FINALES ---
    print(f"\n{'='*60}")
    print(f"  DEMI-FINALES")
    print(f"{'='*60}")

    semi_matchups = [
        (quarter_winners[0], quarter_winners[2]),  # W(Q1) vs W(Q3)
        (quarter_winners[1], quarter_winners[3]),  # W(Q2) vs W(Q4)
    ]

    semi_winners = []
    semi_losers = []

    for name1, name2 in semi_matchups:
        match_count += 1
        result = play_match(name1, name2, "Demi-finale", match_count)
        results.append(result)

        if result["winner"] == name1 or result["winner"] == "Nul":
            semi_winners.append(name1)
            semi_losers.append(name2)
        else:
            semi_winners.append(name2)
            semi_losers.append(name1)

    # --- PETITE FINALE (3eme place) ---
    print(f"\n{'='*60}")
    print(f"  PETITE FINALE (3eme place)")
    print(f"{'='*60}")

    match_count += 1
    result_pf = play_match(semi_losers[0], semi_losers[1], "Petite finale", match_count)
    results.append(result_pf)

    if result_pf["winner"] == semi_losers[0] or result_pf["winner"] == "Nul":
        third, fourth = semi_losers[0], semi_losers[1]
    else:
        third, fourth = semi_losers[1], semi_losers[0]

    # --- GRANDE FINALE ---
    print(f"\n{'='*60}")
    print(f"  GRANDE FINALE")
    print(f"{'='*60}")

    match_count += 1
    result_gf = play_match(semi_winners[0], semi_winners[1], "Finale", match_count)
    results.append(result_gf)

    if result_gf["winner"] == semi_winners[0] or result_gf["winner"] == "Nul":
        champion, second = semi_winners[0], semi_winners[1]
    else:
        champion, second = semi_winners[1], semi_winners[0]

    # Classement 5-8 : les perdants des quarts, classes par leur position en poule
    ranking_5_8 = sorted(quarter_losers,
                         key=lambda n: (rankings_a + rankings_b).index(n))

    final_ranking = [champion, second, third, fourth] + ranking_5_8

    return results, final_ranking


# ============================================================
# TOURNOI COMPLET
# ============================================================

def run_tournament():
    """Lance le tournoi complet : poules + quarts + demis + finale."""

    print("\n" + "#" * 60)
    print("#" + " " * 14 + "TOURNOI QUORIDOR IA" + " " * 19 + "#")
    print("#" + " " * 14 + "8 participants - 44 matchs" + " " * 12 + "#")
    print("#" * 60)

    print("\nParticipants :")
    for name, cfg in PARTICIPANTS.items():
        print(f"  {name:15s} | Depth {cfg['depth']} | {cfg['strategy']}")

    print(f"\nPoule A : {', '.join(GROUPE_A)}")
    print(f"Poule B : {', '.join(GROUPE_B)}")

    all_results: List[Dict] = []

    # --- PHASE DE POULES (36 matchs) ---
    results_a, ranking_a = play_group_stage("A", GROUPE_A, n_rounds=3)
    all_results.extend(results_a)

    results_b, ranking_b = play_group_stage("B", GROUPE_B, n_rounds=3)
    all_results.extend(results_b)

    # --- PHASE ELIMINATOIRE (8 matchs) ---
    results_ko, final_ranking = play_knockout(ranking_a, ranking_b)
    all_results.extend(results_ko)

    # --- CLASSEMENT FINAL ---
    print("\n" + "#" * 60)
    print("#" + " " * 14 + "CLASSEMENT FINAL" + " " * 22 + "#")
    print("#" * 60)

    medals = ["1er ", "2eme", "3eme", "4eme", "5eme", "6eme", "7eme", "8eme"]
    for i, name in enumerate(final_ranking):
        cfg = PARTICIPANTS[name]
        print(f"  {medals[i]} : {name:15s} (D{cfg['depth']}, {cfg['strategy']})")

    print(f"\n  Total matchs joues : {len(all_results)}")

    # --- SAUVEGARDE ---
    os.makedirs("data/results", exist_ok=True)

    # CSV des matchs
    filename = "data/results/tournoi_complet.csv"
    fieldnames = list(all_results[0].keys())
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    print(f"  CSV matchs : {filename}")

    # CSV classement
    ranking_file = "data/results/classement.csv"
    with open(ranking_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["rang", "nom", "depth", "strategy"])
        writer.writeheader()
        for rank, name in enumerate(final_ranking, 1):
            cfg = PARTICIPANTS[name]
            writer.writerow({"rang": rank, "nom": name,
                             "depth": cfg["depth"], "strategy": cfg["strategy"]})
    print(f"  CSV classement : {ranking_file}")

    return all_results


if __name__ == "__main__":
    run_tournament()
