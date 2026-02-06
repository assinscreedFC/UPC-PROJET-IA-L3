import sys
# On importe la classe GUI
from src.ui.gui import QuoridorGUI


def main():
    # On ne demande plus rien dans la console !
    # Tout se gère maintenant à la souris dans le menu du jeu.

    # Création de l'interface (sans arguments)
    game = QuoridorGUI()

    # Lancement de la boucle principale
    game.run()


if __name__ == "__main__":
    main()