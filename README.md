# 📘 Documentation Technique Interne - Projet Quoridor

Ce document sert de référence technique pour l'équipe de développement. Il détaille l'architecture du code, les procédures de test et le fonctionnement des scripts d'analyse.

---

## ⚙️ Installation & Environnement

Pour garantir la compatibilité entre nos environnements de développement, voici les dépendances requises :

```bash
# Installation des librairies
pip install pygame pandas matplotlib seaborn pytest pytest-cov
```

---

## 📂 Structure du Projet

```
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
```

---

# 🏗 Architecture du Code

## 1️⃣ Le Moteur (`src/engine/board.py`)

Le moteur est découplé de l'affichage. Il gère uniquement la logique stricte.

* **Plateau** : Grille 9x9 (0 à 8).
* **Murs** : Stockés dans un `set` pour une complexité d'accès **O(1)**.

  * Format : `(x, y, orientation)` où `(x,y)` est le coin haut-gauche.
* **Pathfinding** : Utilise un **BFS (Breadth-First Search)** pour vérifier `is_path_available`.

---

## 2️⃣ L'Intelligence Artificielle (`src/ia/`)

### 🔹 `minimax.py`

Implémente **Minimax avec élagage Alpha-Bêta**.

### 🔹 `moves_optimization.py` (Module critique)

Filtre les coups inutiles (murs trop éloignés des joueurs) afin de réduire le temps de calcul.

> Sans cette optimisation, la profondeur 3 devient trop lente.

### 🔹 `evaluations.py`

Contient les stratégies d'évaluation.

* **Simple** : Distance de Manhattan.
* **Advanced** : Différence de chemins réels (Dijkstra/BFS) + gestion du stock de murs.

---

## 3️⃣ Interface Graphique (`src/ui/gui.py`)

Machine à états simple basée sur **Pygame** :

* `MENU` : Sélection de la difficulté
* `GAME` : Boucle de jeu (tour par tour)
* `VICTORY` : Écran de fin

---

# 🛠 Guide d'Utilisation (Développeur)

## A. 🎮 Lancer le Jeu (Debug Visuel)

Pour tester l'IA ou le gameplay manuellement :

```bash
python main.py
```

Utiliser le menu pour choisir la difficulté.

**Commandes :**

* Clic gauche : Déplacer
* Clic droit : Poser un mur
* Espace : Rotation du mur

---

## B. 🧪 Validation du Moteur (Tests Unitaires)

Si une modification est faite dans `board.py`, lancer impérativement les tests avant de commit :

```bash
pytest tests/test_engine.py
```

Cela vérifie les règles critiques (sauts, chevauchements, victoire).

---

## C. 📊 Génération de Statistiques (Rapport)

### 1️⃣ Simulation (Tournoi)

Lancer le script qui fait jouer l'IA contre elle-même (sans affichage) :

```bash
python src/tournament.py
```

Le fichier CSV sera généré dans :

```
data/results/
```

### 2️⃣ Analyse (Graphiques)

Générer les courbes et camemberts :

```bash
python src/analysis.py
```

Les images seront générées dans :

```
data/plots/
```

---

# ✅ État d'avancement

* [x] Moteur Physique : Validé (Tests 100%)
* [x] IA Alpha-Bêta : Fonctionnelle (Niveau 1 à 3)
* [x] Interface : Pygame complet (Menu / Jeu)
* [x] Data : Pipeline de statistiques opérationnel

---

**Projet Quoridor – IA & Data Science**
