import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


def analyze_results(csv_path):
    """
    Lit le fichier CSV du tournoi et génère des graphiques pour le rapport.
    """
    # 1. Chargement des données
    if not os.path.exists(csv_path):
        print(f"❌ Erreur : Le fichier {csv_path} n'existe pas. Lancez d'abord tournament.py !")
        return

    print(f"📊 Analyse des données de : {csv_path}")
    df = pd.read_csv(csv_path)

    # Création du dossier pour sauvegarder les images
    if not os.path.exists('data/plots'):
        os.makedirs('data/plots')

    # Configuration du style "Sientifique"
    sns.set_theme(style="whitegrid")

    # --- GRAPHIQUE 1 : TAUX DE VICTOIRE (Camembert) ---
    plt.figure(figsize=(8, 6))
    win_counts = df['winner'].value_counts()

    # On renomme pour que ce soit joli
    labels = [f'Joueur {x}' if x != 'Draw' else 'Match Nul' for x in win_counts.index]

    plt.pie(win_counts, labels=labels, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
    plt.title("Répartition des Victoires (50 parties)")
    plt.savefig('data/plots/victoires.png')
    print("✅ Graphique 'victoires.png' généré.")
    plt.close()

    # --- GRAPHIQUE 2 : DISTRIBUTION DU NOMBRE DE COUPS (Histogramme) ---
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='moves', kde=True, bins=15, color='skyblue')
    plt.title("Distribution de la longueur des parties")
    plt.xlabel("Nombre de coups joués")
    plt.ylabel("Fréquence")
    plt.axvline(df['moves'].mean(), color='red', linestyle='--', label=f'Moyenne: {df["moves"].mean():.1f}')
    plt.legend()
    plt.savefig('data/plots/distribution_coups.png')
    print("✅ Graphique 'distribution_coups.png' généré.")
    plt.close()

    # --- GRAPHIQUE 3 : UTILISATION DES MURS (Boxplot) ---
    # On calcule combien de murs ont été POSÉS (10 - restants)
    df['Murs J1'] = 10 - df['p1_walls_left']
    df['Murs J2'] = 10 - df['p2_walls_left']

    # Transformation pour l'affichage (Melt)
    df_walls = df.melt(value_vars=['Murs J1', 'Murs J2'], var_name='Joueur', value_name='Murs Posés')

    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df_walls, x='Joueur', y='Murs Posés', palette="Set2")
    plt.title("Comparaison de l'utilisation des murs")
    plt.ylim(0, 11)  # Max 10 murs
    plt.savefig('data/plots/utilisation_murs.png')
    print("✅ Graphique 'utilisation_murs.png' généré.")
    plt.close()


if __name__ == "__main__":
    # Nom du fichier généré par votre tournoi (vérifiez le nom dans tournament.py)
    # Exemple : IA niveau 1 contre IA niveau 2
    CSV_FILE = "../data/results/tournoi_d1_vs_d2.csv"
    analyze_results(CSV_FILE)