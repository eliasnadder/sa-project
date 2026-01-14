import pygame
import sys
import time
from board import create_initial_board, BOARD_SIZE, OFF_BOARD
from board import HOUSE_REBIRTH, HOUSE_OF_HAPPINESS, HOUSE_WATER, HOUSE_THREE_TRUTHS, HOUSE_RE_ATUM, HOUSE_HORUS
from rules import get_valid_moves, apply_move, check_win
from sticks import throw_sticks
from ai import AI
from game_state_pyrsistent import GameState
from player import PlayerType

# --- Constants ---
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
HIGHLIGHT_COLOR = (100, 255, 100) # Green for valid moves
SELECTED_COLOR = (255, 255, 0)    # Yellow for selected piece
TEXT_COLOR = (255, 255, 255)

# Player Colors
P1_COLOR = (0, 200, 255)   # Cyan
P2_COLOR = (255, 0, 255)   # Magenta

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

class SenetGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Senet - Ancient Egyptian Board Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        
        # Game State
        self.state = "MENU" # MENU, PLAYING, GAMEOVER
        self.board = []
        self.current_player = PlayerType.PLAYER
        self.opponent = PlayerType.OPPONENT
        self.ai = None
        self.game_mode = None # 1 = HvH, 2 = HvAI
        
        self.current_roll = None
        self.valid_moves = []
        self.selected_piece_index = None
        self.message = "Welcome to Senet"
        self.turn_phase = "THROW" # THROW, SELECT, MOVE
        self.winner = None

        # Menu Buttons
        self.btn_hvh = Button(SCREEN_WIDTH//2 - 150, 300, 300, 60, "Human vs Human", 1)
        self.btn_ai = Button(SCREEN_WIDTH//2 - 150, 400, 300, 60, "Human vs AI", 2)
        
        # Game Buttons
        self.btn_throw = Button(SCREEN_WIDTH//2 - 75, 550, 150, 50, "Throw Sticks", "THROW")
        self.btn_menu = Button(20, 20, 100, 40, "Menu", "MENU_RETURN")

    def reset_game(self, mode):
        self.board = create_initial_board()
        self.current_player = PlayerType.PLAYER
        self.current_roll = None
        self.valid_moves = []
        self.selected_piece_index = None
        self.turn_phase = "THROW"
        self.message = "Player X's Turn. Throw the sticks!"
        self.game_mode = mode
        self.winner = None
        
        if mode == 2:
            # Initialize AI
            self.ai = AI(player_symbol=PlayerType.OPPONENT, depth=3)
        else:
            self.ai = None

    def get_screen_pos(self, index):
        """Converts board index (0-29) to screen (x, y) coordinates handling the S-shape."""
        if index == OFF_BOARD:
            return SCREEN_WIDTH - 80, BOARD_OFFSET_Y + GRID_SIZE + 10

        col = index % 10
        row = index // 10
        
        # Row 0: Left to Right (0-9)
        # Row 1: Right to Left (10-19)
        # Row 2: Left to Right (20-29)
        
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
        
        # Check if click is inside the grid area
        if not (BOARD_OFFSET_X <= mx < BOARD_OFFSET_X + 10 * GRID_SIZE and
                BOARD_OFFSET_Y <= my < BOARD_OFFSET_Y + 3 * GRID_SIZE):
            return None
            
        rel_x = mx - BOARD_OFFSET_X
        rel_y = my - BOARD_OFFSET_Y
        
        col = int(rel_x // GRID_SIZE)
        row = int(rel_y // GRID_SIZE)
        
        if row == 1:
            # Middle row goes backwards
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
            
            # Update Logic (AI Turn)
            if self.state == "PLAYING" and self.game_mode == 2 and \
               self.current_player == PlayerType.OPPONENT and not self.winner:
                self.handle_ai_turn()

            # Drawing
            if self.state == "MENU":
                self.draw_menu(mouse_pos)
            elif self.state == "PLAYING" or self.state == "GAMEOVER":
                self.draw_game(mouse_pos)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def handle_click(self, pos):
        if self.state == "MENU":
            self.btn_hvh.check_hover(pos)
            self.btn_ai.check_hover(pos)
            
            choice = self.btn_hvh.check_click(pos)
            if choice:
                self.reset_game(1)
                self.state = "PLAYING"
                return
                
            choice = self.btn_ai.check_click(pos)
            if choice:
                self.reset_game(2)
                self.state = "PLAYING"
                return

        elif self.state == "PLAYING":
            # Menu Return
            if self.btn_menu.check_click(pos) == "MENU_RETURN":
                self.state = "MENU"
                return

            # Check Throw Button
            if self.turn_phase == "THROW" and self.btn_throw.check_click(pos) == "THROW":
                # Only Human can click throw
                if not (self.game_mode == 2 and self.current_player == PlayerType.OPPONENT):
                    self.perform_throw()
                return

            # Board Interaction
            if self.turn_phase == "SELECT":
                clicked_idx = self.get_index_from_pos(pos)
                
                # Check for bearing off click (somewhere on right side)
                if clicked_idx is None:
                    # If clicking valid "Off Board" move
                    if self.selected_piece_index is not None:
                        for move in self.valid_moves:
                            if move[0] == self.selected_piece_index and move[1] == OFF_BOARD:
                                # Check if click is in bear off area
                                if pos[0] > BOARD_OFFSET_X + 10 * GRID_SIZE:
                                    self.execute_move(move)
                                    return

                if clicked_idx is not None:
                    # 1. Select a piece
                    if self.board[clicked_idx] == self.current_player:
                        # Check if this piece has valid moves
                        has_moves = any(m[0] == clicked_idx for m in self.valid_moves)
                        if has_moves:
                            self.selected_piece_index = clicked_idx
                            self.message = f"Selected square {clicked_idx + 1}"
                    
                    # 2. Move to a target
                    elif self.selected_piece_index is not None:
                        # Find if this click is a valid target for the selected piece
                        target_move = None
                        for move in self.valid_moves:
                            if move[0] == self.selected_piece_index and move[1] == clicked_idx:
                                target_move = move
                                break
                        
                        if target_move:
                            self.execute_move(target_move)

    def perform_throw(self):
        self.current_roll = throw_sticks()
        self.valid_moves = get_valid_moves(self.board, self.current_player, self.current_roll)
        
        msg = f"Rolled: {self.current_roll}. "
        if not self.valid_moves:
            msg += "No moves! Next turn."
            self.message = msg
            # Visual delay so user sees the roll
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
        self.board = apply_move(self.board, start, end)
        
        # Check Win
        if check_win(self.board, self.current_player):
            self.winner = self.current_player
            self.state = "GAMEOVER"
            self.message = f"PLAYER {self.current_player} WINS!"
        else:
            # If roll is 1, 4, or 5, player goes again (traditional rules often allow this)
            # But relying on specific implementation provided. 
            # Looking at game.py provided: 
            # "turn_active = False # End turn after a valid move" 
            # So simple alternating turns.
            self.switch_turn()

    def switch_turn(self):
        self.current_player = PlayerType.OPPONENT if self.current_player == PlayerType.PLAYER else PlayerType.PLAYER
        self.turn_phase = "THROW"
        self.current_roll = None
        self.valid_moves = []
        self.selected_piece_index = None
        self.message = f"Player {self.current_player}'s Turn."

    def handle_ai_turn(self):
        # Brief pause for realism
        self.message = "AI is thinking..."
        self.draw_game(pygame.mouse.get_pos())
        pygame.display.flip()
        time.sleep(0.5)

        # 1. Throw
        self.current_roll = throw_sticks()
        self.draw_game(pygame.mouse.get_pos())
        pygame.display.flip()
        time.sleep(0.5)

        # 2. Calculate Move
        state = GameState.from_board(self.board, self.current_player)
        move = self.ai.choose_best_move(state, self.current_roll)

        if move:
            # Visualize choice
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
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 160))
        
        self.btn_hvh.check_hover(mouse_pos)
        self.btn_ai.check_hover(mouse_pos)
        
        self.btn_hvh.draw(self.screen, self.font)
        self.btn_ai.draw(self.screen, self.font)

    def draw_game(self, mouse_pos):
        # Draw Header info
        self.btn_menu.check_hover(mouse_pos)
        self.btn_menu.draw(self.screen, self.font)
        
        status_color = P1_COLOR if self.current_player == 'X' else P2_COLOR
        status_text = self.font.render(self.message, True, status_color)
        self.screen.blit(status_text, (150, 30))

        # Draw Board Grid
        for i in range(30):
            x, y = self.get_screen_pos(i)
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            
            # Background Color
            color = BOARD_COLOR
            
            # Special Houses Highlights
            if i == HOUSE_REBIRTH: color = (150, 200, 150)
            if i == HOUSE_OF_HAPPINESS: color = (220, 220, 150)
            if i == HOUSE_WATER: color = (150, 150, 220)
            if i in [HOUSE_THREE_TRUTHS, HOUSE_RE_ATUM, HOUSE_HORUS]: color = (220, 150, 150)
            
            # Highlight Valid Move Targets
            if self.selected_piece_index is not None:
                for move in self.valid_moves:
                    if move[0] == self.selected_piece_index and move[1] == i:
                        color = HIGHLIGHT_COLOR
            
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, SQUARE_BORDER, rect, 2)
            
            # Draw Labels for Special Houses
            label = str(i + 1)
            special_char = ""
            if i == HOUSE_REBIRTH: special_char = "R"
            if i == HOUSE_OF_HAPPINESS: special_char = "H"
            if i == HOUSE_WATER: special_char = "W"
            
            # Draw Indices/Markings
            idx_surf = pygame.font.SysFont('Arial', 12).render(label, True, (100, 80, 60))
            self.screen.blit(idx_surf, (x + 5, y + 5))
            
            if special_char:
                char_surf = self.font.render(special_char, True, (255, 255, 255))
                self.screen.blit(char_surf, (x + GRID_SIZE//2 - 10, y + GRID_SIZE//2 - 15))

        # Draw Pieces
        for i, piece in enumerate(self.board):
            if piece:
                x, y = self.get_screen_pos(i)
                center = (x + GRID_SIZE//2, y + GRID_SIZE//2)
                color = P1_COLOR if piece == 'X' else P2_COLOR
                
                # Highlight Selected
                if i == self.selected_piece_index:
                    pygame.draw.circle(self.screen, SELECTED_COLOR, center, GRID_SIZE//2 - 5)
                    pygame.draw.circle(self.screen, color, center, GRID_SIZE//2 - 8)
                else:
                    # Highlight Pieces that CAN move in SELECT phase
                    can_move = False
                    if self.turn_phase == "SELECT" and piece == self.current_player:
                        for m in self.valid_moves:
                            if m[0] == i:
                                can_move = True
                                break
                    
                    if can_move:
                         pygame.draw.circle(self.screen, WHITE, center, GRID_SIZE//2 - 5)
                         pygame.draw.circle(self.screen, color, center, GRID_SIZE//2 - 8)
                    else:
                        pygame.draw.circle(self.screen, BLACK, center, GRID_SIZE//2 - 5)
                        pygame.draw.circle(self.screen, color, center, GRID_SIZE//2 - 7)
                        
                # Draw symbol
                txt = self.font.render(piece, True, WHITE)
                self.screen.blit(txt, (center[0]-8, center[1]-14))

        # Draw Exit Zone (Right side)
        exit_rect = pygame.Rect(SCREEN_WIDTH - 120, BOARD_OFFSET_Y + GRID_SIZE, 100, GRID_SIZE)
        pygame.draw.rect(self.screen, (50, 50, 50), exit_rect, border_radius=5)
        exit_txt = self.font.render("EXIT", True, WHITE)
        self.screen.blit(exit_txt, (SCREEN_WIDTH - 100, BOARD_OFFSET_Y + GRID_SIZE + 25))
        
        # Highlight Exit if it's a valid move
        if self.selected_piece_index is not None:
             for move in self.valid_moves:
                 if move[0] == self.selected_piece_index and move[1] == OFF_BOARD:
                     pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, exit_rect, 4, border_radius=5)

        # Draw Controls
        if self.turn_phase == "THROW" and not self.winner:
            # Hide throw button if it's AI turn
            if not (self.game_mode == 2 and self.current_player == PlayerType.OPPONENT):
                self.btn_throw.check_hover(mouse_pos)
                self.btn_throw.draw(self.screen, self.font)
        
        if self.winner:
            win_surf = self.title_font.render(f"{self.winner} WINS!", True, SELECTED_COLOR)
            self.screen.blit(win_surf, (SCREEN_WIDTH//2 - win_surf.get_width()//2, 600))

if __name__ == "__main__":
    gui = SenetGUI()
    gui.run()