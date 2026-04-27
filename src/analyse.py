import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os


def analyze_tournament(csv_path: str = "data/results/tournoi_complet.csv"):
    """Analyse complete du tournoi avec graphiques."""

    if not os.path.exists(csv_path):
        print(f"Erreur : {csv_path} introuvable. Lancez : python -m src.tournois")
        return

    df = pd.read_csv(csv_path)
    os.makedirs("data/plots", exist_ok=True)
    sns.set_theme(style="whitegrid")

    # Identifier les phases
    poule_df = df[df["phase"].str.startswith("Poule")]
    ko_df = df[~df["phase"].str.startswith("Poule")]
    all_ias = sorted(set(df["ia1"].tolist() + df["ia2"].tolist()))

    print(f"\nAnalyse du tournoi : {len(df)} matchs, {len(all_ias)} participants")
    print("=" * 55)

    # --- STATS TEXTUELLES ---
    # Classement global
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

    # Stats par phase eliminatoire
    if len(ko_df) > 0:
        print("\nPhase eliminatoire :")
        for phase in ko_df["phase"].unique():
            phase_rows = ko_df[ko_df["phase"] == phase]
            for _, row in phase_rows.iterrows():
                print(f"  {phase:20s} : {row['ia1']} vs {row['ia2']} -> {row['winner']}")

    # =========================================================
    # GRAPHIQUE 1 : BRACKET DU TOURNOI
    # =========================================================
    ranking_file = "data/results/classement.csv"
    if os.path.exists(ranking_file):
        ranking = pd.read_csv(ranking_file)

        fig, ax = plt.subplots(figsize=(16, 10))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 12)
        ax.axis("off")
        fig.patch.set_facecolor("#2B2D33")

        ax.text(6, 11.3, "TOURNOI QUORIDOR IA", fontsize=24, fontweight="bold",
                ha="center", color="white", family="monospace")
        ax.text(6, 10.8, f"{len(df)} matchs | {len(all_ias)} participants",
                fontsize=12, ha="center", color="#aaa")

        # Poules
        for gi, (grp_name, y_start) in enumerate([("Poule A", 9.5), ("Poule B", 7.0)]):
            grp_df = poule_df[poule_df["phase"].str.contains(grp_name.split()[1])]
            if len(grp_df) == 0:
                continue

            grp_ias = sorted(set(grp_df["ia1"].tolist() + grp_df["ia2"].tolist()))
            grp_wins = {}
            for ia in grp_ias:
                grp_wins[ia] = len(grp_df[grp_df["winner"] == ia])
            grp_sorted = sorted(grp_ias, key=lambda x: grp_wins[x], reverse=True)

            color = "#4A90D9" if gi == 0 else "#6AB0E9"
            box = mpatches.FancyBboxPatch((0.3, y_start - 0.9), 4.5, 1.3,
                                           boxstyle="round,pad=0.1", facecolor=color,
                                           edgecolor="white", linewidth=1.5, alpha=0.85)
            ax.add_patch(box)
            ax.text(2.55, y_start + 0.2, grp_name, fontsize=12, ha="center",
                    fontweight="bold", color="white")
            for j, ia in enumerate(grp_sorted):
                ax.text(2.55, y_start - 0.15 - j * 0.22, f"{j+1}. {ia} ({grp_wins[ia]}V)",
                        fontsize=9, ha="center", color="white")

        # Phase eliminatoire
        ko_phases = ["Quart de finale", "Demi-finale", "Petite finale", "Finale"]
        phase_positions = {
            "Quart de finale": [(6.5, 9.5), (6.5, 8.3), (6.5, 7.1), (6.5, 5.9)],
            "Demi-finale": [(9, 8.9), (9, 6.5)],
            "Petite finale": [(11, 6.5)],
            "Finale": [(11, 8.9)],
        }
        phase_colors = {
            "Quart de finale": "#8B5CF6",
            "Demi-finale": "#E8A838",
            "Petite finale": "#888",
            "Finale": "#E84040",
        }

        for phase_name in ko_phases:
            phase_rows = ko_df[ko_df["phase"] == phase_name]
            positions = phase_positions.get(phase_name, [])
            color = phase_colors.get(phase_name, "#666")

            for idx, (_, row) in enumerate(phase_rows.iterrows()):
                if idx >= len(positions):
                    break
                px, py = positions[idx]
                box = mpatches.FancyBboxPatch((px - 1.0, py - 0.45), 2.0, 0.9,
                                               boxstyle="round,pad=0.08", facecolor=color,
                                               edgecolor="white", linewidth=1.2, alpha=0.9)
                ax.add_patch(box)
                winner = row["winner"]
                c1 = "#90EE90" if row["ia1"] == winner else "white"
                c2 = "#90EE90" if row["ia2"] == winner else "white"
                ax.text(px, py + 0.15, phase_name[:5], fontsize=7, ha="center",
                        color="#ddd", style="italic")
                ax.text(px, py - 0.0, row["ia1"], fontsize=8, ha="center", color=c1,
                        fontweight="bold" if row["ia1"] == winner else "normal")
                ax.text(px, py - 0.2, row["ia2"], fontsize=8, ha="center", color=c2,
                        fontweight="bold" if row["ia2"] == winner else "normal")

        # Classement final
        medals = ["1er", "2eme", "3eme", "4eme", "5eme", "6eme", "7eme", "8eme"]
        medal_colors = ["#FFD700", "#C0C0C0", "#CD7F32", "#888", "#666", "#666", "#555", "#555"]
        for j, row_r in ranking.iterrows():
            ax.text(6, 4.0 - j * 0.35, f"{medals[j]} : {row_r['nom']}  (D{row_r['depth']}, {row_r['strategy']})",
                    fontsize=11, ha="center", color=medal_colors[j], fontweight="bold")

        plt.savefig("data/plots/bracket.png", dpi=150, bbox_inches="tight", facecolor="#2B2D33")
        print("\n  [1/6] bracket.png")
        plt.close()

    # =========================================================
    # GRAPHIQUE 2 : PERFORMANCE GLOBALE PAR IA
    # =========================================================
    fig, ax = plt.subplots(figsize=(12, 6))

    perf_data = []
    for ia in all_ias:
        p = played_global[ia]
        w = wins_global[ia]
        l = p - w
        perf_data.append({"IA": ia, "Victoires": w, "Defaites": l,
                          "Matchs": p, "Taux": round(w / max(p, 1) * 100, 1)})

    pdf = pd.DataFrame(perf_data).sort_values("Taux", ascending=True)

    ax.barh(pdf["IA"], pdf["Victoires"], color="#4CAF50", label="Victoires")
    ax.barh(pdf["IA"], pdf["Defaites"], left=pdf["Victoires"], color="#F44336", label="Defaites")

    for _, row in pdf.iterrows():
        ax.text(row["Matchs"] + 0.2, row["IA"], f"{row['Taux']}%",
                va="center", fontweight="bold", fontsize=10)

    ax.set_xlabel("Nombre de matchs")
    ax.set_title("Taux de victoire global de chaque IA", fontsize=14, fontweight="bold")
    ax.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig("data/plots/performance_globale.png", dpi=150)
    print("  [2/6] performance_globale.png")
    plt.close()

    # =========================================================
    # GRAPHIQUE 3 : PERFORMANCE EN POULES vs ELIMINATION
    # =========================================================
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax_i, (subset, title) in enumerate([
        (poule_df, "Phase de poules"),
        (ko_df, "Phase eliminatoire"),
    ]):
        ax = axes[ax_i]
        if len(subset) == 0:
            ax.text(0.5, 0.5, "Pas de donnees", ha="center", va="center", transform=ax.transAxes)
            ax.set_title(title)
            continue

        sub_ias = sorted(set(subset["ia1"].tolist() + subset["ia2"].tolist()))
        sub_wins = {ia: len(subset[subset["winner"] == ia]) for ia in sub_ias}
        sub_played = {}
        for ia in sub_ias:
            sub_played[ia] = len(subset[(subset["ia1"] == ia) | (subset["ia2"] == ia)])

        sdf = pd.DataFrame([
            {"IA": ia, "Victoires": sub_wins[ia], "Matchs": sub_played[ia]}
            for ia in sub_ias
        ]).sort_values("Victoires", ascending=True)

        bars = ax.barh(sdf["IA"], sdf["Victoires"], color="#4A90D9" if ax_i == 0 else "#E8A838")
        for _, row in sdf.iterrows():
            pct = round(row["Victoires"] / max(row["Matchs"], 1) * 100)
            ax.text(row["Victoires"] + 0.1, row["IA"], f"{pct}%", va="center", fontsize=9)

        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_xlabel("Victoires")

    plt.tight_layout()
    plt.savefig("data/plots/poules_vs_elimination.png", dpi=150)
    print("  [3/6] poules_vs_elimination.png")
    plt.close()

    # =========================================================
    # GRAPHIQUE 4 : NOMBRE DE COUPS PAR MATCH (evolution)
    # =========================================================
    fig, ax = plt.subplots(figsize=(14, 5))

    # Colorer par type de phase
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
    ax.set_title("Longueur de chaque match du tournoi", fontsize=14, fontweight="bold")

    # Legende
    legend_patches = [
        mpatches.Patch(color="#4A90D9", label="Poules"),
        mpatches.Patch(color="#8B5CF6", label="Quarts"),
        mpatches.Patch(color="#E8A838", label="Demis"),
        mpatches.Patch(color="#E84040", label="Finale"),
    ]
    ax.legend(handles=legend_patches, loc="upper right")
    plt.tight_layout()
    plt.savefig("data/plots/evolution_coups.png", dpi=150)
    print("  [4/6] evolution_coups.png")
    plt.close()

    # =========================================================
    # GRAPHIQUE 5 : UTILISATION DES MURS PAR IA
    # =========================================================
    fig, ax = plt.subplots(figsize=(12, 6))

    walls_data = []
    for _, row in df.iterrows():
        walls_data.append({"IA": row["ia1"], "Murs poses": row["p1_walls_used"]})
        walls_data.append({"IA": row["ia2"], "Murs poses": row["p2_walls_used"]})

    walls_df = pd.DataFrame(walls_data)
    order = sorted(all_ias, key=lambda x: walls_df[walls_df["IA"] == x]["Murs poses"].mean())

    sns.boxplot(data=walls_df, x="IA", y="Murs poses", hue="IA", palette="Set2",
                order=order, legend=False, ax=ax)

    for i, ia in enumerate(order):
        avg = walls_df[walls_df["IA"] == ia]["Murs poses"].mean()
        ax.text(i, avg + 0.3, f"{avg:.1f}", ha="center", fontweight="bold", fontsize=9)

    ax.set_ylim(0, 11)
    ax.set_ylabel("Murs poses (sur 10)")
    ax.set_title("Utilisation des murs par IA", fontsize=14, fontweight="bold")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig("data/plots/murs_par_ia.png", dpi=150)
    print("  [5/6] murs_par_ia.png")
    plt.close()

    # =========================================================
    # GRAPHIQUE 6 : TEMPS DE CALCUL PAR DEPTH
    # =========================================================
    fig, ax = plt.subplots(figsize=(10, 6))

    time_data = []
    for _, row in df.iterrows():
        cfg1 = {"depth": row["ia1_depth"], "strategy": row["ia1_strategy"]}
        cfg2 = {"depth": row["ia2_depth"], "strategy": row["ia2_strategy"]}
        time_data.append({"Config": f"D{cfg1['depth']}-{cfg1['strategy']}", "Temps": row["time"] / 2})
        time_data.append({"Config": f"D{cfg2['depth']}-{cfg2['strategy']}", "Temps": row["time"] / 2})

    tdf = pd.DataFrame(time_data)
    order_t = sorted(tdf["Config"].unique())
    sns.boxplot(data=tdf, x="Config", y="Temps", hue="Config", palette="viridis",
                order=order_t, legend=False, ax=ax)
    ax.set_ylabel("Temps moyen par match (s)")
    ax.set_title("Temps de calcul selon la configuration (depth + strategie)",
                 fontsize=13, fontweight="bold")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig("data/plots/temps_par_config.png", dpi=150)
    print("  [6/6] temps_par_config.png")
    plt.close()

    print(f"\n  Tous les graphiques dans data/plots/")


if __name__ == "__main__":
    analyze_tournament()
