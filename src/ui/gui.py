import pygame
import sys
import os
from src.engine.board import QuoridorBoard
from src.ia.minimax import QuoridorIA

# --- CONSTANTES GRAPHIQUES ---
SCREEN_WIDTH = 900  # Un peu plus large pour l'interface
SCREEN_HEIGHT = 600
BOARD_SIZE = 540
OFFSET_X = 50
OFFSET_Y = 30
CELL_SIZE = 60

# Couleurs
COLOR_BG = (40, 44, 52)
COLOR_PANEL = (60, 64, 72)
COLOR_BOARD = (220, 180, 140)
COLOR_LINES = (100, 70, 50)
COLOR_P1 = (230, 50, 50)  # Rouge
COLOR_P2 = (50, 100, 230)  # Bleu
COLOR_WALL = (240, 230, 140)
COLOR_WALL_SHADOW = (100, 100, 100)
COLOR_TEXT = (255, 255, 255)
COLOR_BUTTON = (70, 130, 180)
COLOR_BUTTON_HOVER = (100, 160, 210)


class Button:
    """Classe utilitaire pour créer des boutons cliquables."""

    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hovered = False

    def draw(self, screen):
        color = COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=10)

        text_surf = self.font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class QuoridorGUI:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Initialisation du son

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Quoridor - Projet Complet")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_title = pygame.font.SysFont("Arial", 50, bold=True)
        self.font_ui = pygame.font.SysFont("Arial", 24)
        self.font_small = pygame.font.SysFont("Arial", 18)

        # Chargement Musique (Sécurisé)
        self.load_music("music.mp3")

        # États du jeu : 'MENU', 'GAME', 'VICTORY'
        self.state = 'MENU'

        # Variables de jeu
        self.board = None
        self.ia = None
        self.vs_ia = True
        self.turn = 1  # 1 ou 2
        self.wall_orientation = 'H'
        self.hover_pos = None
        self.message = ""

        # Création des boutons du menu
        cx = SCREEN_WIDTH // 2 - 100
        self.btn_pvp = Button(cx, 200, 200, 50, "Joueur vs Joueur", self.font_ui)
        self.btn_pve_easy = Button(cx, 270, 200, 50, "IA Facile (Niv 1)", self.font_ui)
        self.btn_pve_med = Button(cx, 340, 200, 50, "IA Moyenne (Niv 2)", self.font_ui)
        self.btn_pve_hard = Button(cx, 410, 200, 50, "IA Experte (Niv 3)", self.font_ui)

        # Bouton fin de jeu
        self.btn_restart = Button(cx, 400, 200, 60, "Retour au Menu", self.font_ui)

    def load_music(self, filename):
        """Charge la musique si le fichier existe."""
        path = os.path.join("assets", filename)
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1)  # -1 pour jouer en boucle
                pygame.mixer.music.set_volume(0.3)
                print("Musique chargée !")
            except Exception as e:
                print(f"Erreur audio : {e}")
        else:
            print("Aucun fichier 'assets/music.mp3' trouvé. Le jeu sera silencieux.")

    def start_game(self, vs_ia, difficulty=1):
        """Initialise une nouvelle partie."""
        self.board = QuoridorBoard()
        self.vs_ia = vs_ia
        self.turn = 1
        self.message = "À vous de jouer !"

        if self.vs_ia:
            strategy = "simple" if difficulty == 1 else "advanced"
            self.ia = QuoridorIA(2, depth=difficulty, strategy=strategy)
        else:
            self.ia = None

        self.state = 'GAME'

    def run(self):
        """Boucle principale."""
        while True:
            mouse_pos = pygame.mouse.get_pos()

            # Gestion des événements globale
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.state == 'MENU':
                    self.handle_menu_events(event, mouse_pos)
                elif self.state == 'GAME':
                    self.handle_game_events(event)
                elif self.state == 'VICTORY':
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.btn_restart.is_clicked(mouse_pos):
                            self.state = 'MENU'

            # Gestion de l'affichage selon l'état
            if self.state == 'MENU':
                self.draw_menu(mouse_pos)
            elif self.state == 'GAME':
                self.update_game_logic()
                self.draw_game(mouse_pos)
            elif self.state == 'VICTORY':
                self.draw_victory(mouse_pos)

            pygame.display.flip()
            self.clock.tick(30)

    # --- LOGIQUE MENU ---
    def handle_menu_events(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_pvp.is_clicked(mouse_pos):
                self.start_game(vs_ia=False)
            elif self.btn_pve_easy.is_clicked(mouse_pos):
                self.start_game(vs_ia=True, difficulty=1)
            elif self.btn_pve_med.is_clicked(mouse_pos):
                self.start_game(vs_ia=True, difficulty=2)
            elif self.btn_pve_hard.is_clicked(mouse_pos):
                self.start_game(vs_ia=True, difficulty=3)

    def draw_menu(self, mouse_pos):
        self.screen.fill(COLOR_BG)

        title = self.font_title.render("QUORIDOR", True, COLOR_BOARD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        subtitle = self.font_ui.render("Choisissez votre mode de jeu", True, (200, 200, 200))
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(subtitle, sub_rect)

        # Boutons
        for btn in [self.btn_pvp, self.btn_pve_easy, self.btn_pve_med, self.btn_pve_hard]:
            btn.check_hover(mouse_pos)
            btn.draw(self.screen)

    # --- LOGIQUE JEU ---
    def handle_game_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.wall_orientation = 'V' if self.wall_orientation == 'H' else 'H'

        if event.type == pygame.MOUSEMOTION:
            mx, my = pygame.mouse.get_pos()
            gx = (mx - OFFSET_X) // CELL_SIZE
            gy = (my - OFFSET_Y) // CELL_SIZE
            if 0 <= gx < 9 and 0 <= gy < 9:
                self.hover_pos = (gx, gy)
            else:
                self.hover_pos = None

        # Interaction Joueur Humain (Seulement si c'est son tour)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.vs_ia and self.turn == 2:
                return  # Bloque l'input si c'est à l'IA

            if self.hover_pos:
                gx, gy = self.hover_pos
                success = False

                # Clic Gauche : Déplacement
                if event.button == 1:
                    if self.board.move_pawn(self.turn, (gx, gy)):
                        success = True

                # Clic Droit : Mur
                elif event.button == 3:
                    if self.board.place_wall(self.turn, gx, gy, self.wall_orientation):
                        success = True
                    else:
                        self.message = "Placement impossible !"

                if success:
                    self.check_win_or_switch_turn()

    def update_game_logic(self):
        # Tour de l'IA
        if self.vs_ia and self.turn == 2 and self.board.winner is None:
            self.message = "L'IA réfléchit..."
            self.draw_game(pygame.mouse.get_pos())  # Force l'affichage du message
            pygame.display.flip()

            # Calcul du coup
            move = self.ia.get_best_move(self.board)
            if move:
                type, data = move
                if type == "MOVE":
                    self.board.move_pawn(2, data)
                else:
                    self.board.place_wall(2, *data)
                self.check_win_or_switch_turn()

    def check_win_or_switch_turn(self):
        if self.board.winner is not None:
            self.state = 'VICTORY'
        else:
            self.turn = 1 if self.turn == 2 else 2
            self.message = f"Tour du Joueur {self.turn}"

    def draw_game(self, mouse_pos):
        self.screen.fill(COLOR_BG)

        # 1. Dessin Plateau
        pygame.draw.rect(self.screen, COLOR_BOARD, (OFFSET_X, OFFSET_Y, BOARD_SIZE, BOARD_SIZE))
        for i in range(10):
            # Lignes
            pygame.draw.line(self.screen, COLOR_LINES, (OFFSET_X + i * CELL_SIZE, OFFSET_Y),
                             (OFFSET_X + i * CELL_SIZE, OFFSET_Y + BOARD_SIZE), 2)
            pygame.draw.line(self.screen, COLOR_LINES, (OFFSET_X, OFFSET_Y + i * CELL_SIZE),
                             (OFFSET_X + BOARD_SIZE, OFFSET_Y + i * CELL_SIZE), 2)

        # 2. Murs et Pions
        for wx, wy, o in self.board.walls:
            self.draw_wall_rect(wx, wy, o, COLOR_WALL)

        self.draw_pawn(1, COLOR_P1)
        self.draw_pawn(2, COLOR_P2)

        # 3. Prévisualisation (si tour humain)
        if self.hover_pos and not (self.vs_ia and self.turn == 2):
            hx, hy = self.hover_pos
            self.draw_wall_rect(hx, hy, self.wall_orientation, COLOR_WALL_SHADOW)

        # 4. Panneau Latéral (Infos)
        panel_x = OFFSET_X + BOARD_SIZE + 20
        pygame.draw.rect(self.screen, COLOR_PANEL, (panel_x, OFFSET_Y, 280, BOARD_SIZE), border_radius=10)

        # Info Tour
        turn_text = f"TOUR : {'JOUEUR 1' if self.turn == 1 else 'JOUEUR 2'}"
        turn_col = COLOR_P1 if self.turn == 1 else COLOR_P2
        self.screen.blit(self.font_title.render(turn_text, True, turn_col), (panel_x + 20, OFFSET_Y + 30))

        # Info Murs
        self.screen.blit(self.font_ui.render(f"Murs J1 : {self.board.walls_count[1]}", True, COLOR_P1),
                         (panel_x + 20, OFFSET_Y + 100))
        self.screen.blit(self.font_ui.render(f"Murs J2 : {self.board.walls_count[2]}", True, COLOR_P2),
                         (panel_x + 20, OFFSET_Y + 140))

        # Info Message
        msg_surf = self.font_small.render(self.message, True, (255, 200, 100))
        self.screen.blit(msg_surf, (panel_x + 20, OFFSET_Y + 200))

        # Aide
        help_y = OFFSET_Y + 350
        help_texts = [
            "COMMANDES :",
            "Clic Gauche : Bouger",
            "Clic Droit : Mur",
            "ESPACE : Tourner Mur"
        ]
        for line in help_texts:
            self.screen.blit(self.font_small.render(line, True, (150, 150, 150)), (panel_x + 20, help_y))
            help_y += 30

    def draw_wall_rect(self, x, y, orientation, color):
        thickness = 12
        length = CELL_SIZE * 2
        bx = OFFSET_X + x * CELL_SIZE
        by = OFFSET_Y + y * CELL_SIZE

        if orientation == 'H':
            rect = (bx, by + CELL_SIZE - thickness // 2, length, thickness)
        else:
            rect = (bx + CELL_SIZE - thickness // 2, by, thickness, length)
        pygame.draw.rect(self.screen, color, rect)

    def draw_pawn(self, player_id, color):
        px, py = self.board.positions[player_id]
        cx = OFFSET_X + px * CELL_SIZE + CELL_SIZE // 2
        cy = OFFSET_Y + py * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(self.screen, color, (cx, cy), 20)
        pygame.draw.circle(self.screen, (0, 0, 0), (cx, cy), 20, 2)

    # --- LOGIQUE VICTOIRE ---
    def draw_victory(self, mouse_pos):
        # Fond semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(10)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        winner_text = f"VICTOIRE DU JOUEUR {self.board.winner} !"
        col = COLOR_P1 if self.board.winner == 1 else COLOR_P2

        txt_surf = self.font_title.render(winner_text, True, col)
        txt_rect = txt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

        # Effet d'ombre texte
        shadow = self.font_title.render(winner_text, True, (0, 0, 0))
        self.screen.blit(shadow, (txt_rect.x + 4, txt_rect.y + 4))
        self.screen.blit(txt_surf, txt_rect)

        self.btn_restart.check_hover(mouse_pos)
        self.btn_restart.draw(self.screen)