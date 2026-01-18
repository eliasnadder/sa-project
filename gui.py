# gui.py
import json
import os
import pygame
import sys
import time
from engines.board import create_initial_board, OFF_BOARD, print_message
from engines.board import HOUSE_REBIRTH, HOUSE_OF_HAPPINESS, HOUSE_WATER, HOUSE_THREE_TRUTHS, HOUSE_RE_ATUM, HOUSE_HORUS
from engines.rules import get_valid_moves, apply_move, check_win
from engines.sticks import throw_sticks
from players.ai_pruning import AI
from engines.game_state_pyrsistent import GameState
from players.player import PlayerType
import matplotlib.pyplot as plt
from players.game_modes import SlowAI, FastAI

AI_OPTIONS = {
    "SLOW": {"ai_class": SlowAI, "depth": 4, "label": "Slow AI"},
    "MEDIUM": {"ai_class": FastAI, "depth": 3, "label": "Medium AI"},
    "FAST": {"ai_class": FastAI, "depth": 2, "label": "Fast AI"}
}

# --- Const
# ants ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
GRID_SIZE = 80
MARGIN = 20
BOARD_OFFSET_X = 100
BOARD_OFFSET_Y = 150

# Colors
WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
BG_COLOR = (30, 30, 40)
BOARD_COLOR = (210, 180, 140)  # Tan
SQUARE_BORDER = (101, 67, 33)  # Dark Brown
HIGHLIGHT_COLOR = (100, 255, 100)  # Green for valid moves
SELECTED_COLOR = (255, 255, 0)    # Yellow for selected piece
TEXT_COLOR = (255, 255, 255)
ERROR_COLOR = (255, 100, 100)

# Player Colors
P1_COLOR = (0, 200, 255)   # Cyan
P2_COLOR = (255, 0, 255)   # Magenta

plt.ion()


class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self, screen, font):
        color = (100, 100, 200) if self.hovered else (70, 70, 70)
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)

        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def check_click(self, pos):
        if self.rect.collidepoint(pos) and self.action:
            return self.action
        return None


class TextInputBox:
    def __init__(self, x, y, width, height, hint=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.hint = hint
        self.active = False
        self.error = False

    def draw(self, screen, font):
        # Background
        color = (90, 90, 90) if not self.active else (120, 120, 120)
        if self.error:
            color = (180, 80, 80)
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)

        # Text or hint
        if self.text:
            text_surf = font.render(self.text, True, WHITE)
        else:
            text_surf = font.render(self.hint, True, (150, 150, 150))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.error = False

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return self.text
            elif event.unicode.isdigit():
                self.text += event.unicode
        return None


class SenetGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Senet - Ancient Egyptian Board Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 20)

        # Game State
        self.state = "MENU"  # MENU, AI_SETUP, PLAYING, GAMEOVER
        self.board = []
        self.current_player = PlayerType.PLAYER
        self.opponent = PlayerType.OPPONENT
        self.ai = None
        self.ai_depth = 3  # Default depth
        self.game_mode = None  # 1 = HvH, 2 = HvAI

        self.current_roll = None
        self.valid_moves = []
        self.selected_piece_index = None
        self.message = "Welcome to Senet"
        self.turn_phase = "THROW"  # THROW, SELECT, MOVE
        self.winner = None

        # Menu Buttons
        self.btn_hvh = Button(SCREEN_WIDTH//2 - 150, 300,
                              300, 60, "Human vs Human", 1)
        self.btn_ai = Button(SCREEN_WIDTH//2 - 150, 400,
                             300, 60, "Human vs AI", "AI_SETUP")

        # AI Setup Elements
        self.input_depth = TextInputBox(
            SCREEN_WIDTH//2 - 100, 350, 200, 50, hint="Enter depth (e.g. 3)")
        self.btn_start_ai = Button(
            SCREEN_WIDTH//2 - 100, 450, 200, 60, "Start Game", "START_AI")
        self.depth_error_msg = ""

        self.btn_slow = Button(SCREEN_WIDTH//2 - 150, 300, 300, 60, "Slow AI", "SLOW")
        self.btn_medium = Button(SCREEN_WIDTH//2 - 150, 380, 300, 60, "Medium AI", "MEDIUM")
        self.btn_fast = Button(SCREEN_WIDTH//2 - 150, 460, 300, 60, "Fast AI", "FAST")

        
        # Game Buttons
        self.btn_throw = Button(SCREEN_WIDTH//2 - 75,
                                550, 150, 50, "Throw Sticks", "THROW")
        self.btn_menu = Button(20, 20, 100, 40, "Menu", "MENU_RETURN")

    def reset_game(self, mode, depth=3):
        self.board = create_initial_board()
        self.current_player = PlayerType.PLAYER
        self.current_roll = None
        self.valid_moves = []
        self.selected_piece_index = None
        self.turn_phase = "THROW"
        self.message = "Player X's Turn. Throw the sticks!"
        self.game_mode = mode
        self.winner = None
        self.ai_depth = depth

        if mode == 2:
            # Init weights
            ai_weights = None
            weights_file = "best_ai_weights.json"

            if os.path.exists(weights_file):
                try:
                    with open(weights_file, "r") as f:
                        ai_weights = json.load(f)
                    print_message(
                        "The training weights have been successfully loaded! The AI ​​is now at its maximum power.", "info")
                except Exception as e:
                    print_message(
                        f"File upload error; default weights will be used.: {e}", "warning")
            else:
                print_message(
                    "The weights file does not exist, using default weights.", "warning")
            # ------------------------------------------

            self.ai = AI(player_symbol=PlayerType.OPPONENT,
                         depth=depth, weights=ai_weights)
        else:
            self.ai = None

    def get_screen_pos(self, index):
        """Converts board index (0-29) to screen (x, y) coordinates handling the S-shape."""
        if index == OFF_BOARD:
            return SCREEN_WIDTH - 80, BOARD_OFFSET_Y + GRID_SIZE + 10

        col = index % 10
        row = index // 10

        if row == 1:
            draw_col = 9 - col
        else:
            draw_col = col

        x = BOARD_OFFSET_X + draw_col * GRID_SIZE
        y = BOARD_OFFSET_Y + row * GRID_SIZE
        return x, y

    def get_index_from_pos(self, pos):
        """Converts screen (x, y) to board index."""
        mx, my = pos

        if not (BOARD_OFFSET_X <= mx < BOARD_OFFSET_X + 10 * GRID_SIZE and
                BOARD_OFFSET_Y <= my < BOARD_OFFSET_Y + 3 * GRID_SIZE):
            return None

        rel_x = mx - BOARD_OFFSET_X
        rel_y = my - BOARD_OFFSET_Y

        col = int(rel_x // GRID_SIZE)
        row = int(rel_y // GRID_SIZE)

        if row == 1:
            actual_col = 9 - col
            index = (row * 10) + actual_col
        else:
            index = (row * 10) + col

        return index

    def run(self):
        running = True
        while running:
            self.screen.fill(BG_COLOR)
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(mouse_pos)
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event)

            # Update Logic (AI Turn)
            if self.state == "PLAYING" and self.game_mode == 2 and \
               self.current_player == PlayerType.OPPONENT and not self.winner:
                self.handle_ai_turn()

            # Drawing
            if self.state == "MENU":
                self.draw_menu(mouse_pos)
            elif self.state == "AI_SETUP":
                self.draw_ai_setup(mouse_pos)
            elif self.state == "PLAYING" or self.state == "GAMEOVER":
                self.draw_game(mouse_pos)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def handle_key(self, event):
        if self.state == "AI_SETUP":
            result = self.input_depth.handle_event(event)
            if result is not None:
                # Enter pressed
                self.try_start_ai_game(result)

    def handle_click(self, pos):
        if self.state == "MENU":
            self.btn_hvh.check_hover(pos)
            self.btn_ai.check_hover(pos)

            choice = self.btn_hvh.check_click(pos)
            if choice == 1:
                self.reset_game(1)
                self.state = "PLAYING"
                return

            choice = self.btn_ai.check_click(pos)
            if choice == "AI_SETUP":
                self.state = "AI_SETUP"
                self.input_depth.text = ""
                self.depth_error_msg = ""
                return

        # elif self.state == "AI_SETUP":
        #     self.input_depth.handle_event(pygame.event.Event(
        #         pygame.MOUSEBUTTONDOWN, {'pos': pos}))

        #     if self.btn_start_ai.check_click(pos) == "START_AI":
        #         self.try_start_ai_game(self.input_depth.text)

        #     if self.btn_menu.check_click(pos) == "MENU_RETURN":
        #         self.state = "MENU"
        #         return
        
        elif self.state == "AI_SETUP":
            if self.btn_slow.check_click(pos) == "SLOW":
                self.try_start_ai_game("4")   # Slow AI → depth 4
            elif self.btn_medium.check_click(pos) == "MEDIUM":
                self.try_start_ai_game("3")   # Medium AI → depth 3
            elif self.btn_fast.check_click(pos) == "FAST":
                self.try_start_ai_game("2")   # Fast AI → depth 2

            elif self.btn_menu.check_click(pos) == "MENU_RETURN":
                self.state = "MENU"

        elif self.state == "PLAYING":
            if self.btn_menu.check_click(pos) == "MENU_RETURN":
                self.state = "MENU"
                return

            if self.turn_phase == "THROW" and self.btn_throw.check_click(pos) == "THROW":
                if not (self.game_mode == 2 and self.current_player == PlayerType.OPPONENT):
                    self.perform_throw()
                return

            if self.turn_phase == "SELECT":
                clicked_idx = self.get_index_from_pos(pos)

                if clicked_idx is None:
                    if self.selected_piece_index is not None:
                        for move in self.valid_moves:
                            if move[0] == self.selected_piece_index and move[1] == OFF_BOARD:
                                if pos[0] > BOARD_OFFSET_X + 10 * GRID_SIZE:
                                    self.execute_move(move)
                                    return

                if clicked_idx is not None:
                    if self.board[clicked_idx] == self.current_player:
                        has_moves = any(
                            m[0] == clicked_idx for m in self.valid_moves)
                        if has_moves:
                            self.selected_piece_index = clicked_idx
                            self.message = f"Selected square {clicked_idx + 1}"

                    elif self.selected_piece_index is not None:
                        target_move = None
                        for move in self.valid_moves:
                            if move[0] == self.selected_piece_index and move[1] == clicked_idx:
                                target_move = move
                                break
                        if target_move:
                            self.execute_move(target_move)

    def try_start_ai_game(self, text):
        if not text.strip():
            self.depth_error_msg = "Please enter a depth value!"
            self.input_depth.error = True
            return

        try:
            depth = int(text.strip())
            if depth <= 0:
                raise ValueError
        except ValueError:
            self.depth_error_msg = "Depth must be a positive integer!"
            self.input_depth.error = True
            return

        self.reset_game(2, depth=depth)
        self.state = "PLAYING"

    def perform_throw(self):
        self.current_roll = throw_sticks()
        self.valid_moves = get_valid_moves(
            self.board, self.current_player, self.current_roll)

        msg = f"Rolled: {self.current_roll}. "
        if not self.valid_moves:
            msg += "No moves! Next turn."
            self.message = msg
            self.draw_game(pygame.mouse.get_pos())
            pygame.display.flip()
            time.sleep(1)
            self.switch_turn()
        else:
            msg += "Select a piece to move."
            self.message = msg
            self.turn_phase = "SELECT"
            self.selected_piece_index = None

    def execute_move(self, move):
        start, end = move

        if self.current_player == PlayerType.OPPONENT:
            print(f"[AI EXECUTE] Move from {start} to {end}")

        self.board = apply_move(self.board, start, end)

        if check_win(self.board, self.current_player):
            self.winner = self.current_player
            self.state = "GAMEOVER"
            self.message = f"PLAYER {self.current_player} WINS!"
        else:
            self.switch_turn()

    def switch_turn(self):
        self.current_player = PlayerType.OPPONENT if self.current_player == PlayerType.PLAYER else PlayerType.PLAYER
        self.turn_phase = "THROW"
        self.current_roll = None
        self.valid_moves = []
        self.selected_piece_index = None
        self.message = f"Player {self.current_player}'s Turn."

    def handle_ai_turn(self):
        self.message = "AI is thinking..."
        self.draw_game(pygame.mouse.get_pos())
        pygame.display.flip()
        time.sleep(0.5)

        self.current_roll = throw_sticks()
        self.draw_game(pygame.mouse.get_pos())
        pygame.display.flip()
        time.sleep(0.5)

        state = GameState.from_board(self.board, self.current_player)
        move = self.ai.choose_best_move(state, self.current_roll)

        if move:
            start, end = move
            print(
                f"[AI MOVE] Rolled: {self.current_roll} | From: {start} -> To: {end}")
        else:
            print(f"[AI MOVE] Rolled: {self.current_roll} | No valid moves")

        if move:
            self.selected_piece_index = move[0]
            self.draw_game(pygame.mouse.get_pos())
            pygame.display.flip()
            time.sleep(0.5)

            self.execute_move(move)
        else:
            self.message = f"AI rolled {self.current_roll} but has no moves."
            self.draw_game(pygame.mouse.get_pos())
            pygame.display.flip()
            time.sleep(1.0)
            self.switch_turn()

    def draw_menu(self, mouse_pos):
        title = self.title_font.render("SENET", True, BOARD_COLOR)
        subtitle = self.font.render("The Game of Passing", True, WHITE)

        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 -
                         subtitle.get_width()//2, 160))

        self.btn_hvh.check_hover(mouse_pos)
        self.btn_ai.check_hover(mouse_pos)

        self.btn_hvh.draw(self.screen, self.font)
        self.btn_ai.draw(self.screen, self.font)

    # def draw_ai_setup(self, mouse_pos):
    #     # Back to menu button
    #     self.btn_menu.check_hover(mouse_pos)
    #     self.btn_menu.draw(self.screen, self.font)

    #     # Title
    #     title = self.title_font.render("AI Settings", True, BOARD_COLOR)
    #     self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

    #     # Instructions
    #     hint_text = self.font.render(
    #         "Recommended depth: 3 (higher = stronger but slower)", True, WHITE)
    #     self.screen.blit(hint_text, (SCREEN_WIDTH//2 -
    #                      hint_text.get_width()//2, 250))

    #     # Input box
    #     self.input_depth.draw(self.screen, self.font)

    #     # Error message
    #     if self.depth_error_msg:
    #         error_surf = self.small_font.render(
    #             self.depth_error_msg, True, ERROR_COLOR)
    #         self.screen.blit(error_surf, (SCREEN_WIDTH//2 -
    #                          error_surf.get_width()//2, 410))

    #     # Start button
    #     self.btn_start_ai.check_hover(mouse_pos)
    #     self.btn_start_ai.draw(self.screen, self.font)
    
    def draw_ai_setup(self, mouse_pos):
        # Back to menu button
        self.btn_menu.check_hover(mouse_pos)
        self.btn_menu.draw(self.screen, self.font)

        # Title
        title = self.title_font.render("AI Settings", True, BOARD_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

        # Instructions
        hint_text = self.font.render(
            "Select AI difficulty", True, WHITE)
        self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, 250))

        # Draw buttons
        for btn in [self.btn_slow, self.btn_medium, self.btn_fast]:
            btn.check_hover(mouse_pos)
            btn.draw(self.screen, self.font)


    def draw_game(self, mouse_pos):
        self.btn_menu.check_hover(mouse_pos)
        self.btn_menu.draw(self.screen, self.font)

        status_color = P1_COLOR if self.current_player == 'X' else P2_COLOR
        status_text = self.font.render(self.message, True, status_color)
        self.screen.blit(status_text, (150, 30))

        # Draw Board Grid
        for i in range(30):
            x, y = self.get_screen_pos(i)
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)

            color = BOARD_COLOR

            if i == HOUSE_REBIRTH:
                color = (150, 200, 150)
            if i == HOUSE_OF_HAPPINESS:
                color = (220, 220, 150)
            if i == HOUSE_WATER:
                color = (150, 150, 220)
            if i in [HOUSE_THREE_TRUTHS, HOUSE_RE_ATUM, HOUSE_HORUS]:
                color = (220, 150, 150)

            if self.selected_piece_index is not None:
                for move in self.valid_moves:
                    if move[0] == self.selected_piece_index and move[1] == i:
                        color = HIGHLIGHT_COLOR

            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, SQUARE_BORDER, rect, 2)

            label = str(i + 1)
            special_char = ""
            if i == HOUSE_REBIRTH:
                special_char = "R"
            if i == HOUSE_OF_HAPPINESS:
                special_char = "H"
            if i == HOUSE_WATER:
                special_char = "W"

            idx_surf = pygame.font.SysFont(
                'Arial', 12).render(label, True, (100, 80, 60))
            self.screen.blit(idx_surf, (x + 5, y + 5))

            if special_char:
                char_surf = self.font.render(
                    special_char, True, (255, 255, 255))
                self.screen.blit(char_surf, (x + GRID_SIZE //
                                 2 - 10, y + GRID_SIZE//2 - 15))

        # Draw Pieces
        for i, piece in enumerate(self.board):
            if piece:
                x, y = self.get_screen_pos(i)
                center = (x + GRID_SIZE//2, y + GRID_SIZE//2)
                color = P1_COLOR if piece == 'X' else P2_COLOR

                if i == self.selected_piece_index:
                    pygame.draw.circle(
                        self.screen, SELECTED_COLOR, center, GRID_SIZE//2 - 5)
                    pygame.draw.circle(self.screen, color,
                                       center, GRID_SIZE//2 - 8)
                else:
                    can_move = False
                    if self.turn_phase == "SELECT" and piece == self.current_player:
                        for m in self.valid_moves:
                            if m[0] == i:
                                can_move = True
                                break

                    if can_move:
                        pygame.draw.circle(
                            self.screen, WHITE, center, GRID_SIZE//2 - 5)
                        pygame.draw.circle(
                            self.screen, color, center, GRID_SIZE//2 - 8)
                    else:
                        pygame.draw.circle(
                            self.screen, BLACK, center, GRID_SIZE//2 - 5)
                        pygame.draw.circle(
                            self.screen, color, center, GRID_SIZE//2 - 7)

                txt = self.font.render(piece, True, WHITE)
                self.screen.blit(txt, (center[0]-8, center[1]-14))

        # Draw Exit Zone
        exit_rect = pygame.Rect(
            SCREEN_WIDTH - 120, BOARD_OFFSET_Y + GRID_SIZE, 100, GRID_SIZE)
        pygame.draw.rect(self.screen, (50, 50, 50), exit_rect, border_radius=5)
        exit_txt = self.font.render("EXIT", True, WHITE)
        self.screen.blit(exit_txt, (SCREEN_WIDTH - 100,
                         BOARD_OFFSET_Y + GRID_SIZE + 25))

        if self.selected_piece_index is not None:
            for move in self.valid_moves:
                if move[0] == self.selected_piece_index and move[1] == OFF_BOARD:
                    pygame.draw.rect(self.screen, HIGHLIGHT_COLOR,
                                     exit_rect, 4, border_radius=5)

        if self.turn_phase == "THROW" and not self.winner:
            if not (self.game_mode == 2 and self.current_player == PlayerType.OPPONENT):
                self.btn_throw.check_hover(mouse_pos)
                self.btn_throw.draw(self.screen, self.font)

        if self.winner:
            win_surf = self.title_font.render(
                f"{self.winner} WINS!", True, SELECTED_COLOR)
            self.screen.blit(win_surf, (SCREEN_WIDTH//2 -
                             win_surf.get_width()//2, 600))


if __name__ == "__main__":
    gui = SenetGUI()
    gui.run()
