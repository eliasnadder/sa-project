"""Entry point for the Senet game."""

import json
import os
from engines.board import print_legend, print_title, Colors, print_message
from engines.game import SenetGame
# from engines.game_ql import SenetGame
from players.player import PlayerType
from players.ai_pruning import AI
from players.player_rl import QLearningAI


def start_game():
    c = Colors
    print_title()

    input(f"\n  {c.DIM}Press Enter to start...{c.RESET}")

    print("\n  Choose type: \n    1- Human vs Human \n    2- Human vs AI\n    3- Human vs AI (Q-Learning)")
    choice = int(input('  Enter a number: '))
    match choice:
        case 1:
            current_player = PlayerType.PLAYER
            opponent = PlayerType.OPPONENT
            print_legend(current_player, opponent)
            game = SenetGame(current_player=current_player, opponent=opponent)
            game.start_playing()

        case 2:
            current_player = PlayerType.PLAYER
            opponent = PlayerType.OPPONENT

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

            ai = AI(
                player_symbol=opponent,
                depth=3,
                weights=ai_weights
            )

            print_legend(current_player, opponent)

            game = SenetGame(
                current_player=current_player,
                opponent=opponent,
                ai_player=ai
            )

            game.start_playing()

        case 3:
            current_player = PlayerType.PLAYER
            opponent = PlayerType.OPPONENT

            # تهيئة AI متعلم (QLearning)
            ai = QLearningAI(opponent)
            ai.load_latest_data()  # يحمله من training_logs/

            print_legend(current_player, opponent)

            game = SenetGame(
                current_player=current_player,
                opponent=opponent,
                ai_player=ai
            )
            game.start_playing()

        case _:
            print_message(
                "Invalid choice. Defaulting to Human vs Human.", "warning")


if __name__ == "__main__":
    try:
        start_game()
    except KeyboardInterrupt:
        print_message("Game interrupted by user.", "error")
    except Exception as e:
        print_message(f"An error occurred: {e}", "error")
