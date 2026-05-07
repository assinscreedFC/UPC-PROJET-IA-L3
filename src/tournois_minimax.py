"""
Tournoi complet entre IA utilisant l'algorithme Minimax pur (sans élagage alpha-bêta).
Profondeurs 1 à 4, heuristiques simple/advanced/expert.
Résultats et analyse sauvegardés dans data/minimax/
"""

import time
import csv
import os
import random
from typing import Dict, List, Tuple
from itertools import combinations
from src.engine.board import QuoridorBoard
from src.ia.minimax2 import QuoridorIA


# ============================================================
# 12 PARTICIPANTS — D1 à D4 × 3 heuristiques
# ============================================================

PARTICIPANTS = {
    # Profondeur 1
    "D1-Simple":    {"depth": 1, "strategy": "simple"},
    "D1-Advanced":  {"depth": 1, "strategy": "advanced"},
    "D1-Expert":    {"depth": 1, "strategy": "expert"},
    # Profondeur 2
    "D2-Simple":    {"depth": 2, "strategy": "simple"},
    "D2-Advanced":  {"depth": 2, "strategy": "advanced"},
    "D2-Expert":    {"depth": 2, "strategy": "expert"},
    # Profondeur 3
    "D3-Simple":    {"depth": 3, "strategy": "simple"},
    "D3-Advanced":  {"depth": 3, "strategy": "advanced"},
    "D3-Expert":    {"depth": 3, "strategy": "expert"},
    # Profondeur 4
    "D4-Simple":    {"depth": 4, "strategy": "simple"},
    "D4-Advanced":  {"depth": 4, "strategy": "advanced"},
    "D4-Expert":    {"depth": 4, "strategy": "expert"},
}

# 3 poules de 4 — mélange de profondeurs dans chaque groupe
GROUPE_A = ["D1-Simple", "D2-Expert", "D3-Advanced", "D4-Simple"]
GROUPE_B = ["D1-Advanced", "D2-Simple", "D3-Expert", "D4-Advanced"]
GROUPE_C = ["D1-Expert", "D2-Advanced", "D3-Simple", "D4-Expert"]

OUTPUT_DIR = "data/minimax"


# ============================================================
# SIMULATION D'UN MATCH
# ============================================================

def play_game(ia1: QuoridorIA, ia2: QuoridorIA) -> Dict:
    """Simule une partie complète entre deux IA."""
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
    """Joue un seul match entre deux IA nommées."""
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

    print(f"    [{match_num:>2}] {name1} vs {name2} -> {winner} ({stats['moves']} coups, {stats['time']:.2f}s)", flush=True)

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
    Retourne les résultats et le classement (par nombre de victoires).
    """
    print(f"\n{'='*60}")
    print(f"  POULE {group_name} : {', '.join(members)}")
    print(f"  ({n_rounds} matchs par paire = {len(list(combinations(members, 2))) * n_rounds} matchs)")
    print(f"{'='*60}", flush=True)

    results = []
    match_num = 0

    pairs = list(combinations(members, 2))
    for round_num in range(1, n_rounds + 1):
        print(f"\n  --- Journée {round_num} ---", flush=True)
        for pair_idx, (name1, name2) in enumerate(pairs):
            match_num += 1
            if (round_num + pair_idx) % 2 == 1:
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
# MATCH ALLER-RETOUR (ÉLIMINATOIRE)
# ============================================================

def play_match_home_away(name1: str, name2: str, phase: str, match_num: int) -> Tuple[List[Dict], str]:
    """
    Joue un match aller-retour entre deux IA.
    Départage : coups → murs restants → 3e match.
    """
    result1 = play_match(name1, name2, phase, match_num)
    result2 = play_match(name2, name1, phase, match_num)

    results = [result1, result2]

    wins1 = sum(1 for r in results if r["winner"] == name1)
    wins2 = sum(1 for r in results if r["winner"] == name2)

    if wins1 != wins2:
        winner = name1 if wins1 > wins2 else name2
        return results, winner

    # Égalité 1-1 : départager sur le nombre de coups
    won_by_1 = [r for r in results if r["winner"] == name1]
    won_by_2 = [r for r in results if r["winner"] == name2]

    if won_by_1 and won_by_2:
        moves1 = min(r["moves"] for r in won_by_1)
        moves2 = min(r["moves"] for r in won_by_2)
        if moves1 != moves2:
            winner = name1 if moves1 < moves2 else name2
            return results, winner

        best_r1 = min(won_by_1, key=lambda r: r["moves"])
        best_r2 = min(won_by_2, key=lambda r: r["moves"])
        walls_left_1 = 10 - (best_r1["p1_walls_used"] if best_r1["ia1"] == name1 else best_r1["p2_walls_used"])
        walls_left_2 = 10 - (best_r2["p1_walls_used"] if best_r2["ia1"] == name2 else best_r2["p2_walls_used"])
        if walls_left_1 != walls_left_2:
            winner = name1 if walls_left_1 > walls_left_2 else name2
            return results, winner

    # 3e match tiebreak
    if random.random() < 0.5:
        result3 = play_match(name1, name2, phase + " (tiebreak)", match_num)
    else:
        result3 = play_match(name2, name1, phase + " (tiebreak)", match_num)
    results.append(result3)

    if result3["winner"] == name1:
        return results, name1
    elif result3["winner"] == name2:
        return results, name2
    else:
        return results, name1


# ============================================================
# PHASE ÉLIMINATOIRE (3 poules → top 2 de chaque + 2 meilleurs 3e)
# ============================================================

def play_knockout(rankings_a: List[str], rankings_b: List[str], rankings_c: List[str],
                  all_pool_results: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """
    Phase éliminatoire : 8 qualifiés (top 2 de chaque poule + 2 meilleurs 3èmes).
    Quarts → Demis → Petite finale → Finale.
    """
    results = []
    match_count = 0

    # Sélection des 8 qualifiés
    # Top 2 de chaque poule = 6 qualifiés directs
    qualified = [rankings_a[0], rankings_a[1],
                 rankings_b[0], rankings_b[1],
                 rankings_c[0], rankings_c[1]]

    # 2 meilleurs 3èmes (par victoires en poules)
    thirds = [rankings_a[2], rankings_b[2], rankings_c[2]]
    third_wins = {}
    for name in thirds:
        third_wins[name] = sum(1 for r in all_pool_results if r["winner"] == name)
    thirds_sorted = sorted(thirds, key=lambda n: third_wins[n], reverse=True)
    qualified.extend(thirds_sorted[:2])

    # Les éliminés
    eliminated = [thirds_sorted[2]] + [rankings_a[3], rankings_b[3], rankings_c[3]]

    print(f"\n{'='*60}")
    print(f"  QUALIFIÉS POUR LA PHASE ÉLIMINATOIRE")
    print(f"{'='*60}")
    for i, name in enumerate(qualified, 1):
        cfg = PARTICIPANTS[name]
        print(f"    {i}. {name:15s} (D{cfg['depth']}, {cfg['strategy']})")

    # --- QUARTS DE FINALE ---
    print(f"\n{'='*60}")
    print(f"  QUARTS DE FINALE")
    print(f"{'='*60}", flush=True)

    # Croisements : 1A vs meilleur 3e qualifié, 1B vs 2C, 1C vs 2B, 2A vs 2e meilleur 3e
    quarter_matchups = [
        (qualified[0], qualified[7]),  # 1A vs 8e qualifié
        (qualified[2], qualified[5]),  # 1B vs 2C
        (qualified[4], qualified[3]),  # 1C vs 2B
        (qualified[1], qualified[6]),  # 2A vs 7e qualifié
    ]

    quarter_winners = []
    quarter_losers = []

    for name1, name2 in quarter_matchups:
        match_count += 1
        match_results, winner = play_match_home_away(name1, name2, "Quart de finale", match_count)
        results.extend(match_results)
        loser = name2 if winner == name1 else name1
        quarter_winners.append(winner)
        quarter_losers.append(loser)

    # --- DEMI-FINALES ---
    print(f"\n{'='*60}")
    print(f"  DEMI-FINALES")
    print(f"{'='*60}", flush=True)

    semi_matchups = [
        (quarter_winners[0], quarter_winners[2]),
        (quarter_winners[1], quarter_winners[3]),
    ]

    semi_winners = []
    semi_losers = []

    for name1, name2 in semi_matchups:
        match_count += 1
        match_results, winner = play_match_home_away(name1, name2, "Demi-finale", match_count)
        results.extend(match_results)
        loser = name2 if winner == name1 else name1
        semi_winners.append(winner)
        semi_losers.append(loser)

    # --- PETITE FINALE ---
    print(f"\n{'='*60}")
    print(f"  PETITE FINALE (3ème place)")
    print(f"{'='*60}", flush=True)

    match_count += 1
    pf_results, third = play_match_home_away(semi_losers[0], semi_losers[1], "Petite finale", match_count)
    results.extend(pf_results)
    fourth = semi_losers[1] if third == semi_losers[0] else semi_losers[0]

    # --- GRANDE FINALE ---
    print(f"\n{'='*60}")
    print(f"  GRANDE FINALE")
    print(f"{'='*60}", flush=True)

    match_count += 1
    gf_results, champion = play_match_home_away(semi_winners[0], semi_winners[1], "Finale", match_count)
    results.extend(gf_results)
    second = semi_winners[1] if champion == semi_winners[0] else semi_winners[0]

    # Classement final 1-12
    final_ranking = [champion, second, third, fourth] + quarter_losers + eliminated

    return results, final_ranking


# ============================================================
# ANALYSE ET GRAPHIQUES
# ============================================================

def analyze_results(all_results: List[Dict], final_ranking: List[str]):
    """Génère les statistiques et graphiques dans data/minimax/"""
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import seaborn as sns

    os.makedirs(f"{OUTPUT_DIR}/plots", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/results", exist_ok=True)

    df = pd.DataFrame(all_results)
    sns.set_theme(style="whitegrid")

    all_ias = sorted(set(df["ia1"].tolist() + df["ia2"].tolist()))
    poule_df = df[df["phase"].str.startswith("Poule")]
    ko_df = df[~df["phase"].str.startswith("Poule")]

    # --- STATS TEXTUELLES ---
    print(f"\n{'='*60}")
    print(f"  ANALYSE — Minimax pur (sans élagage)")
    print(f"  {len(df)} matchs, {len(all_ias)} participants")
    print(f"{'='*60}")

    wins_global = {ia: 0 for ia in all_ias}
    played_global = {ia: 0 for ia in all_ias}
    for _, row in df.iterrows():
        played_global[row["ia1"]] += 1
        played_global[row["ia2"]] += 1
        if row["winner"] in wins_global:
            wins_global[row["winner"]] += 1

    print("\nBilan global :")
    sorted_ias = sorted(all_ias, key=lambda x: wins_global[x], reverse=True)
    for ia in sorted_ias:
        p = played_global[ia]
        w = wins_global[ia]
        pct = round(w / max(p, 1) * 100)
        print(f"  {ia:15s} : {w:>2}/{p} victoires ({pct}%)")

    # =========================================================
    # GRAPHIQUE 1 : BRACKET DU TOURNOI
    # =========================================================
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 14)
    ax.axis("off")
    fig.patch.set_facecolor("#2B2D33")

    ax.text(6, 13.3, "TOURNOI MINIMAX PUR", fontsize=24, fontweight="bold",
            ha="center", color="white", family="monospace")
    ax.text(6, 12.8, f"{len(df)} matchs | {len(all_ias)} participants | Sans élagage",
            fontsize=12, ha="center", color="#aaa")

    # Poules
    poule_groups = [("A", GROUPE_A, 11.5), ("B", GROUPE_B, 9.5), ("C", GROUPE_C, 7.5)]
    for gi, (grp_name, members, y_start) in enumerate(poule_groups):
        grp_df = poule_df[poule_df["phase"].str.contains(grp_name)]
        grp_wins = {m: len(grp_df[grp_df["winner"] == m]) for m in members}
        grp_sorted = sorted(members, key=lambda x: grp_wins[x], reverse=True)

        colors = ["#4A90D9", "#6AB0E9", "#5BC0A0"]
        box = mpatches.FancyBboxPatch((0.3, y_start - 1.1), 4.5, 1.5,
                                       boxstyle="round,pad=0.1", facecolor=colors[gi],
                                       edgecolor="white", linewidth=1.5, alpha=0.85)
        ax.add_patch(box)
        ax.text(2.55, y_start + 0.2, f"Poule {grp_name}", fontsize=12, ha="center",
                fontweight="bold", color="white")
        for j, ia in enumerate(grp_sorted):
            ax.text(2.55, y_start - 0.1 - j * 0.28, f"{j+1}. {ia} ({grp_wins[ia]}V)",
                    fontsize=9, ha="center", color="white")

    # Classement final
    medals = ["1er", "2e", "3e", "4e", "5e", "6e", "7e", "8e", "9e", "10e", "11e", "12e"]
    medal_colors = ["#FFD700", "#C0C0C0", "#CD7F32"] + ["#888"] * 9
    for j, name in enumerate(final_ranking[:12]):
        cfg = PARTICIPANTS[name]
        ax.text(6, 5.5 - j * 0.38, f"{medals[j]} : {name}  (D{cfg['depth']}, {cfg['strategy']})",
                fontsize=11, ha="center", color=medal_colors[j], fontweight="bold")

    plt.savefig(f"{OUTPUT_DIR}/plots/bracket.png", dpi=150, bbox_inches="tight", facecolor="#2B2D33")
    print(f"\n  [1/7] bracket.png")
    plt.close()

    # =========================================================
    # GRAPHIQUE 2 : PERFORMANCE GLOBALE PAR IA
    # =========================================================
    fig, ax = plt.subplots(figsize=(12, 7))

    perf_data = []
    for ia in all_ias:
        p = played_global[ia]
        w = wins_global[ia]
        l = p - w
        perf_data.append({"IA": ia, "Victoires": w, "Defaites": l,
                          "Matchs": p, "Taux": round(w / max(p, 1) * 100, 1)})

    pdf = pd.DataFrame(perf_data).sort_values("Taux", ascending=True)

    ax.barh(pdf["IA"], pdf["Victoires"], color="#4CAF50", label="Victoires")
    ax.barh(pdf["IA"], pdf["Defaites"], left=pdf["Victoires"], color="#F44336", label="Défaites")

    for _, row in pdf.iterrows():
        ax.text(row["Matchs"] + 0.2, row["IA"], f"{row['Taux']}%",
                va="center", fontweight="bold", fontsize=9)

    ax.set_xlabel("Nombre de matchs")
    ax.set_title("Performance globale — Minimax pur (sans élagage)", fontsize=14, fontweight="bold")
    ax.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/plots/performance_globale.png", dpi=150)
    print("  [2/7] performance_globale.png")
    plt.close()

    # =========================================================
    # GRAPHIQUE 3 : VICTOIRES PAR PROFONDEUR
    # =========================================================
    fig, ax = plt.subplots(figsize=(10, 6))

    depth_wins = {1: 0, 2: 0, 3: 0, 4: 0}
    depth_played = {1: 0, 2: 0, 3: 0, 4: 0}
    for _, row in df.iterrows():
        depth_played[row["ia1_depth"]] += 1
        depth_played[row["ia2_depth"]] += 1
        if row["winner"] != "Nul":
            winner_cfg = PARTICIPANTS[row["winner"]]
            depth_wins[winner_cfg["depth"]] += 1

    depths = [1, 2, 3, 4]
    taux = [round(depth_wins[d] / max(depth_played[d], 1) * 100, 1) for d in depths]

    bars = ax.bar(depths, taux, color=["#FF6B6B", "#FFA726", "#66BB6A", "#42A5F5"], edgecolor="black")
    for bar, t in zip(bars, taux):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{t}%", ha="center", fontweight="bold", fontsize=12)

    ax.set_xlabel("Profondeur", fontsize=12)
    ax.set_ylabel("Taux de victoire (%)", fontsize=12)
    ax.set_title("Taux de victoire par profondeur — Minimax pur", fontsize=14, fontweight="bold")
    ax.set_xticks(depths)
    ax.set_xticklabels(["D1", "D2", "D3", "D4"])
    ax.set_ylim(0, 100)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/plots/victoires_par_profondeur.png", dpi=150)
    print("  [3/7] victoires_par_profondeur.png")
    plt.close()

    # =========================================================
    # GRAPHIQUE 4 : VICTOIRES PAR HEURISTIQUE
    # =========================================================
    fig, ax = plt.subplots(figsize=(10, 6))

    strat_wins = {"simple": 0, "advanced": 0, "expert": 0}
    strat_played = {"simple": 0, "advanced": 0, "expert": 0}
    for _, row in df.iterrows():
        strat_played[row["ia1_strategy"]] += 1
        strat_played[row["ia2_strategy"]] += 1
        if row["winner"] != "Nul":
            winner_cfg = PARTICIPANTS[row["winner"]]
            strat_wins[winner_cfg["strategy"]] += 1

    strats = ["simple", "advanced", "expert"]
    taux_s = [round(strat_wins[s] / max(strat_played[s], 1) * 100, 1) for s in strats]

    bars = ax.bar(strats, taux_s, color=["#FFCC02", "#FF8C00", "#E84040"], edgecolor="black")
    for bar, t in zip(bars, taux_s):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{t}%", ha="center", fontweight="bold", fontsize=12)

    ax.set_xlabel("Heuristique", fontsize=12)
    ax.set_ylabel("Taux de victoire (%)", fontsize=12)
    ax.set_title("Taux de victoire par heuristique — Minimax pur", fontsize=14, fontweight="bold")
    ax.set_ylim(0, 100)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/plots/victoires_par_heuristique.png", dpi=150)
    print("  [4/7] victoires_par_heuristique.png")
    plt.close()

    # =========================================================
    # GRAPHIQUE 5 : TEMPS DE CALCUL PAR PROFONDEUR
    # =========================================================
    fig, ax = plt.subplots(figsize=(12, 6))

    time_data = []
    for _, row in df.iterrows():
        time_data.append({"Config": f"D{row['ia1_depth']}-{row['ia1_strategy']}", "Temps (s)": row["time"] / 2})
        time_data.append({"Config": f"D{row['ia2_depth']}-{row['ia2_strategy']}", "Temps (s)": row["time"] / 2})

    tdf = pd.DataFrame(time_data)
    order_t = sorted(tdf["Config"].unique())
    sns.boxplot(data=tdf, x="Config", y="Temps (s)", hue="Config", palette="viridis",
                order=order_t, legend=False, ax=ax)
    ax.set_ylabel("Temps moyen par match (s)")
    ax.set_title("Temps de calcul par configuration — Minimax pur (sans élagage)",
                 fontsize=13, fontweight="bold")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/plots/temps_par_config.png", dpi=150)
    print("  [5/7] temps_par_config.png")
    plt.close()

    # =========================================================
    # GRAPHIQUE 6 : NOMBRE DE COUPS PAR MATCH
    # =========================================================
    fig, ax = plt.subplots(figsize=(14, 5))

    colors_list = []
    for _, row in df.iterrows():
        if "Poule" in row["phase"]:
            colors_list.append("#4A90D9")
        elif "Quart" in row["phase"]:
            colors_list.append("#8B5CF6")
        elif "Demi" in row["phase"]:
            colors_list.append("#E8A838")
        elif "Finale" in row["phase"]:
            colors_list.append("#E84040")
        else:
            colors_list.append("#888")

    ax.bar(range(len(df)), df["moves"], color=colors_list, alpha=0.8)
    ax.axhline(df["moves"].mean(), color="red", linestyle="--", alpha=0.7,
               label=f"Moyenne: {df['moves'].mean():.0f} coups")
    ax.set_xlabel("Match #")
    ax.set_ylabel("Nombre de coups")
    ax.set_title("Longueur des matchs — Minimax pur", fontsize=14, fontweight="bold")

    legend_patches = [
        mpatches.Patch(color="#4A90D9", label="Poules"),
        mpatches.Patch(color="#8B5CF6", label="Quarts"),
        mpatches.Patch(color="#E8A838", label="Demis"),
        mpatches.Patch(color="#E84040", label="Finale"),
    ]
    ax.legend(handles=legend_patches, loc="upper right")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/plots/evolution_coups.png", dpi=150)
    print("  [6/7] evolution_coups.png")
    plt.close()

    # =========================================================
    # GRAPHIQUE 7 : UTILISATION DES MURS PAR IA
    # =========================================================
    fig, ax = plt.subplots(figsize=(14, 6))

    walls_data = []
    for _, row in df.iterrows():
        walls_data.append({"IA": row["ia1"], "Murs posés": row["p1_walls_used"]})
        walls_data.append({"IA": row["ia2"], "Murs posés": row["p2_walls_used"]})

    walls_df = pd.DataFrame(walls_data)
    order = sorted(all_ias, key=lambda x: walls_df[walls_df["IA"] == x]["Murs posés"].mean())

    sns.boxplot(data=walls_df, x="IA", y="Murs posés", hue="IA", palette="Set3",
                order=order, legend=False, ax=ax)

    for i, ia in enumerate(order):
        avg = walls_df[walls_df["IA"] == ia]["Murs posés"].mean()
        ax.text(i, avg + 0.3, f"{avg:.1f}", ha="center", fontweight="bold", fontsize=8)

    ax.set_ylim(0, 11)
    ax.set_ylabel("Murs posés (sur 10)")
    ax.set_title("Utilisation des murs par IA — Minimax pur", fontsize=14, fontweight="bold")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/plots/murs_par_ia.png", dpi=150)
    print("  [7/7] murs_par_ia.png")
    plt.close()

    print(f"\n  Tous les graphiques dans {OUTPUT_DIR}/plots/")


# ============================================================
# TOURNOI COMPLET
# ============================================================

def run_tournament():
    """Lance le tournoi Minimax pur complet : 3 poules + phase éliminatoire."""

    print("\n" + "#" * 60)
    print("#" + " " * 10 + "TOURNOI MINIMAX PUR (SANS ÉLAGAGE)" + " " * 7 + "#")
    print("#" + " " * 10 + f"12 participants — D1 à D4" + " " * 16 + "#")
    print("#" * 60)

    print("\nParticipants :")
    for name, cfg in PARTICIPANTS.items():
        print(f"  {name:15s} | Depth {cfg['depth']} | {cfg['strategy']}")

    print(f"\nPoule A : {', '.join(GROUPE_A)}")
    print(f"Poule B : {', '.join(GROUPE_B)}")
    print(f"Poule C : {', '.join(GROUPE_C)}")

    all_results: List[Dict] = []

    # --- PHASE DE POULES (54 matchs : 3 poules × 6 paires × 3 matchs) ---
    results_a, ranking_a = play_group_stage("A", GROUPE_A, n_rounds=3)
    all_results.extend(results_a)

    results_b, ranking_b = play_group_stage("B", GROUPE_B, n_rounds=3)
    all_results.extend(results_b)

    results_c, ranking_c = play_group_stage("C", GROUPE_C, n_rounds=3)
    all_results.extend(results_c)

    pool_results = list(all_results)

    # --- PHASE ÉLIMINATOIRE ---
    results_ko, final_ranking = play_knockout(ranking_a, ranking_b, ranking_c, pool_results)
    all_results.extend(results_ko)

    # --- CLASSEMENT FINAL ---
    print("\n" + "#" * 60)
    print("#" + " " * 14 + "CLASSEMENT FINAL" + " " * 22 + "#")
    print("#" * 60)

    medals = ["1er ", "2ème", "3ème", "4ème", "5ème", "6ème", "7ème", "8ème",
              "9ème", "10e ", "11e ", "12e "]
    for i, name in enumerate(final_ranking):
        cfg = PARTICIPANTS[name]
        print(f"  {medals[i]} : {name:15s} (D{cfg['depth']}, {cfg['strategy']})")

    print(f"\n  Total matchs joués : {len(all_results)}")

    # --- SAUVEGARDE CSV ---
    os.makedirs(f"{OUTPUT_DIR}/results", exist_ok=True)

    filename = f"{OUTPUT_DIR}/results/tournoi_minimax.csv"
    fieldnames = list(all_results[0].keys())
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    print(f"  CSV matchs : {filename}")

    ranking_file = f"{OUTPUT_DIR}/results/classement.csv"
    with open(ranking_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["rang", "nom", "depth", "strategy"])
        writer.writeheader()
        for rank, name in enumerate(final_ranking, 1):
            cfg = PARTICIPANTS[name]
            writer.writerow({"rang": rank, "nom": name,
                             "depth": cfg["depth"], "strategy": cfg["strategy"]})
    print(f"  CSV classement : {ranking_file}")

    # --- ANALYSE ET GRAPHIQUES ---
    analyze_results(all_results, final_ranking)

    return all_results


if __name__ == "__main__":
    run_tournament()
