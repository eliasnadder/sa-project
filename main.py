
import json
import os
from engines.board import print_legend, print_title, Colors, print_message
from engines.game import SenetGame
from players.player import PlayerType
from players.ai_pruning import AI 

from players.game_modes import GAME_MODES as M 


def choose_game_mode():
    print("choose game mode:")
    print("1 - Human vs Human")
    print("2 - Easy")
    print("3 - Medium")
    print("4 - Hard")
    
    mapping = {
        "1": "HUMAN",
        "2": "EASY",
        "3": "MEDIUM",
        "4": "HARD"
    }
    
    choice = input("Select: ")
    if choice not in mapping:
        print_message("Invaild choice, defaulting to Human va Human.", "warning")
        choice = "1"
    
    return M[mapping[choice]]

def start_game():
    c = Colors
    print_title()

    input(f"\n  {c.DIM}Press Enter to start...{c.RESET}")

    print("\n  Choose type: \n    1- Human vs Human \n    2- Human vs AI(SLOW)\n   3- Human vs AI(FAST)  4- Human vs AI(MEDIUM)  5- Human vs AI (Q-Learning)")
    
    AI_OPTIONS = {
        2: {"ai_class": M.SlowAI, "depth": 4, "label": "SLOW AI"},
        3: {"ai_class": M.FastAI, "depth": 2, "label": "FAST AI"},
        4: {"ai_class": M.AFastAI, "depth": 3, "label": "MEDIUM AI"}
    }
    
    choice = int(input('  Enter a number: '))
    match choice:
        case 1:
            current_player = PlayerType.PLAYER
            opponent = PlayerType.OPPONENT
            print_legend(current_player, opponent)
            game = SenetGame(current_player=current_player, opponent=opponent)
            game.start_playing()

        case c if c in AI_OPTIONS:
            current_player = PlayerType.PLAYER
            opponent = PlayerType.OPPONENT

            ai_config = AI_OPTIONS[c]
            ai_class = ai_config["ai_class"]
            depth = ai_config["depth"]
            label = ai_config['label']
            
            # Init weights
            ai_weights = None
            weights_file = "best_ai_weights.json"

            if os.path.exists(weights_file):
                try:
                    with open(weights_file, "r") as f:
                        ai_weights = json.load(f)
                    print_message(
                        "The training weights have been successfully loaded {label}! ​is now at its maximum power.", "info")
                except Exception as e:
                    print_message(
                        f"File upload error; default weights will be used.: {e}", "warning")
            else:
                print_message(
                    "The weights file does not exist, using default weights.", "warning")
            # ------------------------------------------

            ai = AI(player_symbol=opponent, depth=depth, weights=ai_weights)

            print_legend(current_player, opponent)

            game = SenetGame(
                current_player=current_player,
                opponent=opponent,
                ai_player=ai
            )

            game.start_playing()

        # case 5:
        #     current_player = PlayerType.PLAYER
        #     opponent = PlayerType.OPPONENT

        #     # تهيئة AI متعلم (QLearning)
        #     ai = QLearningAI(opponent)
        #     ai.load_latest_data()  # يحمله من training_logs/

        #     print_legend(current_player, opponent)

        #     game = SenetGame(
        #         current_player=current_player,
        #         opponent=opponent,
        #         ai_player=ai
        #     )
        #     game.start_playing()

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
