"""Main Senet game class and game loop."""

from players.player import PlayerType
from board import *
from sticks import throw_sticks
from rules import get_valid_moves, apply_move, check_win
from players.ai_pruning import AI
from game_state_pyrsistent import *
from sticks import throw_sticks


class SenetGame:
    def __init__(self, current_player, opponent, ai_player=None):
        self.board = create_initial_board()
        self.current_player = current_player
        self.opponent = opponent
        self.game_over = False

        self.ai_player = ai_player

    def get_state_vector(self):
        """Returns the current board state as a persistence vector."""
        return get_persistence_vector(self.board)

    def get_flattened_state(self):
        """Returns a flattened state vector for AI input."""
        return get_flattened_vector(self.board, self.current_player)

    def start_playing(self):
        c = Colors
        while not self.game_over:
            print_board(self.board)
            player_color = c.CYAN if self.current_player == PlayerType.PLAYER else c.MAGENTA
            print(
                f"\n  {c.BOLD}{player_color}▶ Player {self.current_player}'s turn{c.RESET}")
            input(f"  {c.DIM}Press Enter to throw sticks...{c.RESET}")

            # Main loop
            turn_active = True
            while turn_active:
                roll = throw_sticks()
                print_roll(roll)

                valid_moves = get_valid_moves(
                    self.board, self.current_player, roll)

                if not valid_moves:
                    print_message("No legal moves available.", "warning")
                else:
                    # choice = self._get_player_choice(valid_moves)
                    if self.ai_player and self.current_player == PlayerType.OPPONENT:
                        choice = self._get_ai_choice(roll)
                    else:
                        choice = self._get_player_choice(valid_moves)

                    self.board = apply_move(self.board, choice[0], choice[1])

                    # Check Win
                    if check_win(self.board, self.current_player):
                        print_board(self.board)
                        print_winner(self.current_player)
                        self.game_over = True
                        return

                    turn_active = False  # End turn after a valid move
                    self.current_player = PlayerType.OPPONENT if self.current_player == PlayerType.PLAYER else PlayerType.PLAYER

    def _get_player_choice(self, valid_moves):
        """Get player's move choice from available moves."""
        c = Colors
        print(f"\n  {c.BOLD}Available moves:{c.RESET}")
        print(f"  {c.DIM}{'─' * 30}{c.RESET}")

        for idx, m in enumerate(valid_moves):
            dest = f"{c.GREEN}Off Board{c.RESET}" if m[1] == OFF_BOARD else "HOUSE OF HAPPINESS" if m[1] == HOUSE_OF_HAPPINESS else "HOUSE WATER" if m[1] == HOUSE_WATER else "HOUSE THREE TRUTHS" if m[
                1] == HOUSE_THREE_TRUTHS else "HOUSE RE ATUM" if m[1] == HOUSE_RE_ATUM else "HOUSE HORUS" if m[1] == HOUSE_HORUS else f"Square {m[1] + 1}"
            print(f"    {c.YELLOW}[{idx}]{c.RESET} Square {m[0] + 1} → {dest}")

        print(f"  {c.DIM}{'─' * 30}{c.RESET}")

        choice = None
        while choice is None:
            try:
                user_input = int(
                    input(f"  {c.BOLD}Select move index:{c.RESET} "))
                if 0 <= user_input < len(valid_moves):
                    choice = valid_moves[user_input]
                else:
                    print_message("Invalid index. Please try again.", "error")
            except ValueError:
                print_message("Please enter a number.", "error")

        return choice

    def _get_ai_choice(self, roll):
        c = Colors
        print(f"\n  {c.BOLD}{c.MAGENTA}AI is thinking...{c.RESET}")

        # تحويل board الحالي إلى GameState
        state = GameState.from_board(
            board=self.board, current_player_symbol=self.current_player)
        move = self.ai_player.choose_best_move(state, roll)

        print(
            f"  {c.MAGENTA}AI chose:{c.RESET} "
            f"Square {move[0] + 1} → "
            f"{'Off Board' if move[1] == OFF_BOARD else f'Square {move[1] + 1}'}"
        )

        return move
