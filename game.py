"""Main Senet game class and game loop."""

from board import (
    create_initial_board, print_board, print_title, print_legend,
    print_roll, print_winner, print_message, OFF_BOARD, Colors
)
from sticks import throw_sticks
from rules import get_valid_moves, apply_move, check_win


class SenetGame:
    def __init__(self):
        self.board = create_initial_board()
        self.current_player = 'X'
        self.game_over = False

    def play(self):
        c = Colors
        print_title()
        print_legend()

        print_message("Player X vs Player O - Both Human Players", "info")
        input(f"\n  {c.DIM}Press Enter to start...{c.RESET}")

        while not self.game_over:
            print_board(self.board)
            player_color = c.CYAN if self.current_player == 'X' else c.MAGENTA
            print(
                f"\n  {c.BOLD}{player_color}▶ Player {self.current_player}'s turn{c.RESET}")
            input(f"  {c.DIM}Press Enter to throw sticks...{c.RESET}")

            # Turn loop (to handle extra turns)
            turn_active = True
            while turn_active:
                roll = throw_sticks()
                print_roll(roll)

                valid_moves = get_valid_moves(
                    self.board, self.current_player, roll)

                if not valid_moves:
                    print_message("No legal moves available.", "warning")
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
                    self.current_player = 'O' if self.current_player == 'X' else 'X'

                #! Blocked until finish search
                # Check for extra turn
                # if grants_extra_turn(roll):
                #     print_message(
                #         f"Roll of {roll} grants an extra turn! 🎯", "success")
                #     if not self.game_over:
                #         print_board(self.board)
                #         input(
                #             f"  {c.DIM}Player {self.current_player}, press Enter for extra turn...{c.RESET}")
                # else:
                #     turn_active = False

            # Switch Player
            # self.current_player = 'O' if self.current_player == 'X' else 'X'

    def _get_player_choice(self, valid_moves):
        """Get player's move choice from available moves."""
        c = Colors
        print(f"\n  {c.BOLD}Available moves:{c.RESET}")
        print(f"  {c.DIM}{'─' * 30}{c.RESET}")

        for idx, m in enumerate(valid_moves):
            dest = f"{c.GREEN}Off Board{c.RESET}" if m[1] == OFF_BOARD else f"Square {m[1] + 1}"
            print(f"    {c.YELLOW}[{idx}]{c.RESET} Square {m[0] + 1} → {dest}")

        print(f"  {c.DIM}{'─' * 30}{c.RESET}")

        choice = None
        while choice is None:
            try:
                user_input = int(input(f"  {c.BOLD}Select move index:{c.RESET} "))
                if 0 <= user_input < len(valid_moves):
                    choice = valid_moves[user_input]
                else:
                    print_message("Invalid index. Please try again.", "error")
            except ValueError:
                print_message("Please enter a number.", "error")

        return choice
