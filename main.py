from engines.board import print_legend, print_title, Colors, print_message
from engines.game import SenetGame
from players.player import PlayerType

from players.game_modes import GAME_MODES


def start_game():
    c = Colors
    print_title()

    input(f"\n  {c.DIM}Press Enter to start...{c.RESET}")

    print("\n  Choose type: \n    1- Human vs Human \n    2- Human vs AI(SLOW) \n    3- Human vs AI(FAST) \n    4- Human vs AI(MEDIUM)")

    mode_mapping = {
        2: "HARD",
        3: "EASY",
        4: "MEDIUM",
        5: "Intelligent"
    }

    choice = int(input('  Enter a number: '))
    match choice:
        case 1:
            current_player = PlayerType.PLAYER
            opponent = PlayerType.OPPONENT
            print_legend(current_player, opponent)
            game = SenetGame(current_player=current_player, opponent=opponent)
            game.start_playing()

        case 2 | 3 | 4:
            current_player = PlayerType.PLAYER
            opponent = PlayerType.OPPONENT

            mode = mode_mapping[choice]
            ai_config = GAME_MODES[mode]
            ai_class = ai_config["ai_class"]
            depth = ai_config["depth"]

            print_legend(current_player, opponent)

            ai = ai_class(player_symbol=opponent, depth=depth)
            game = SenetGame(
                current_player=current_player,
                opponent=opponent,
                ai_player=ai
            )

            game.start_playing()

        case _:
            print_message(
                "Invalid choice. Defaulting to Human vs Human.", "warning")
            current_player = PlayerType.PLAYER
            opponent = PlayerType.OPPONENT
            print_legend(current_player, opponent)
            game = SenetGame(current_player=current_player, opponent=opponent)
            game.start_playing()


if __name__ == "__main__":
    try:
        start_game()
    except KeyboardInterrupt:
        print_message("Game interrupted by user.", "error")
    except Exception as e:
        print_message(f"An error occurred: {e}", "error")
