📘 Documentation Technique Interne - Projet Quoridor

Ce document sert de référence technique pour l'équipe de développement. Il détaille l'architecture du code, les procédures de test et le fonctionnement des scripts d'analyse.

⚙️ Installation & Environnement

Pour garantir la compatibilité entre nos environnements de développement, voici les dépendances requises :

# Installation des librairies
pip install pygame pandas matplotlib seaborn pytest pytest-cov


📂 Structure du Projet

UPC-PROJET-IA-L3/
├── assets/                 # Ressources (music.mp3, images)
├── data/                   # Données générées (ne pas commit les gros CSV)
│   ├── results/            # CSV bruts des tournois
│   └── plots/              # Graphiques générés (png)
├── src/
│   ├── engine/
│   │   └── board.py        # Moteur logique (Grille, Murs, Règles)
│   ├── ia/
│   │   ├── minimax.py      # Algorithme Alpha-Bêta
│   │   ├── evaluations.py  # Fonctions heuristiques (BFS, Manhattan)
│   │   └── moves_optimization.py # Réduction du facteur de branchement
│   ├── ui/
│   │   └── gui.py          # Interface Pygame (Menu, Jeu, Events)
│   ├── tournament.py       # Script de simulation (50+ parties)
│   └── analysis.py         # Script Data Science (Pandas/Matplotlib)
├── tests/                  # Tests unitaires (Pytest)
├── main.py                 # Lanceur principal (GUI)
└── README.md               # Ce document


🏗 Architecture du Code

1. Le Moteur (src/engine/board.py)

Le moteur est découplé de l'affichage. Il gère la logique stricte.

Plateau : Grille 9x9 (0 à 8).

Murs : Stockés dans un set pour une complexité d'accès O(1).

Format : (x, y, orientation) où x,y est le coin haut-gauche.

Pathfinding : Utilise un BFS (Breadth-First Search) pour vérifier is_path_available.

2. L'Intelligence Artificielle (src/ia/)

minimax.py : Implémente Minimax avec élagage Alpha-Bêta.

moves_optimization.py : Module Critique. Il filtre les coups inutiles (murs trop loin des joueurs) pour réduire le temps de calcul. Sans cela, la profondeur 3 est trop lente.

evaluations.py : Contient les stratégies.

Simple : Distance de Manhattan.

Advanced : Différence de chemins réels (Dijkstra/BFS) + gestion du stock de murs.

3. Interface Graphique (src/ui/gui.py)

Machine à états simple basée sur Pygame :

MENU : Sélection de la difficulté.

GAME : Boucle de jeu (Tour par tour).

VICTORY : Écran de fin.

🛠 Guide d'Utilisation (Dev)

A. Lancer le Jeu (Debug Visuel)

Pour tester l'IA ou le gameplay manuellement :

python main.py


Utiliser le Menu pour choisir la difficulté.

Commandes : Clic Gauche (Bouger), Clic Droit (Mur), Espace (Rotation).

B. Validation du Moteur (Tests Unitaires)

Si une modification est faite dans board.py, lancer impérativement les tests avant de commit :

pytest tests/test_engine.py


Cela vérifie les règles critiques (sauts, chevauchements, victoire).

C. Génération de Statistiques (Rapport)

Pour analyser la performance de l'IA sur 50 parties :

Simulation (Tournoi) :
Lancer le script qui fait jouer l'IA contre elle-même (sans affichage) :

python src/tournament.py


Le fichier CSV sera dans data/results/.

Analyse (Graphiques) :
Générer les courbes et camemberts :

python src/analysis.py


Les images seront dans data/plots/.

🐛 Problèmes Fréquents & Solutions

Problème

Cause Probable

Solution

Crash TypeError au lancement

main.py envoie des arguments à QuoridorGUI.

Vérifier que main.py appelle juste QuoridorGUI().run().

L'IA est lente (>5s)

Profondeur trop élevée ou optimisation désactivée.

Vérifier depth (max 3 recommandé) et que moves_optimization est actif.

Pas de son

Fichier manquant.

Ajouter un fichier music.mp3 dans le dossier assets/.

Mur impossible à poser

Chevauchement logique.

Le moteur interdit les intersections ("Croix") et chevauchements. C'est normal.

✅ État d'avancement

[x] Moteur Physique : Validé (Tests 100%).

[x] IA Alpha-Bêta : Fonctionnelle (Niv 1 à 3).

[x] Interface : Pygame complet (Menu/Jeu).

[x] Data : Pipeline de stats opérationnel.