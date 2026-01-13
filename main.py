# """Entry point for the Senet game."""

# from player import PlayerType
# from board import print_legend
# from player import Players
# from board import print_title
# from board import Colors
# from board import print_message
# from game import SenetGame

# from ai import AI

# def start_game():
#     c = Colors
#     print_title()

#     input(f"\n  {c.DIM}Press Enter to start...{c.RESET}")

#     print("\n  Choose type: \n    1- Human vs Human \n    2- Human vs AI\n")
#     choice = int(input('  Enter a number: '))
#     match choice:
#         case 1:
#             current_player=PlayerType.PLAYER
#             opponent=PlayerType.OPPONENT
#             print_legend(current_player, opponent)
#             game = SenetGame(current_player=current_player, opponent=opponent)
#             game.start_playing()
#         # case 2:
#         #     self.current_player = Players.PLAYER_2
#         case 2:
#             current_player = PlayerType.PLAYER
#             opponent = PlayerType.OPPONENT

#             ai = AI(
#                 player_symbol=opponent,
#                 depth=3
#             )

#             print_legend(current_player, opponent)

#             game = SenetGame(
#                 current_player=current_player,
#                 opponent=opponent,
#                 ai_player=ai
#             )

#             game.start_playing()

#         case _:
#             print_message(
#                 "Invalid choice. Defaulting to Human vs Human.", "warning")


# if __name__ == "__main__":
#     try:
#         start_game()
#     except KeyboardInterrupt:
#         print_message("Game interrupted by user.", "error")
#     except Exception as e:
#         print_message(f"An error occurred: {e}", "error")