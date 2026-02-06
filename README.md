## 🛠 État de l'implémentation : Sprint 1 (Moteur de Jeu)

### Fonctionnalités implémentées
* [cite_start]**Représentation du plateau** : Matrice 9x9 avec gestion des coordonnées (x, y)[cite: 20].
* **Gestion des murs** : Stockage dans un `set` pour des recherches rapides ($O(1)$). [cite_start]Un mur est défini par son ancrage Nord-Ouest et son orientation ('H' ou 'V')[cite: 40].
* [cite_start]**Algorithme BFS** : Vérifie en temps réel qu'aucun joueur n'est enfermé avant de valider la pose d'un mur[cite: 41].
* **Sauts de pions** : Logique complète incluant le saut direct et les sauts diagonaux si le saut direct est obstrué.
* [cite_start]**Validation par tests** : Suite de tests `pytest` atteignant une couverture quasi-totale des règles (collisions, stock de murs, conditions de victoire)[cite: 41].

### Comment reprendre le travail
1. **Moteur** : La classe principale est `QuoridorBoard` dans `src/engine/board.py`. 
2. **Tests** : Lancez `pytest tests/test_engine.py` pour vérifier que vos modifications ne cassent pas les règles du jeu.
3. [cite_start]**Simulation** : Utilisez `board.copy()` pour obtenir un état de jeu virtuel pour les futurs algorithmes de recherche.