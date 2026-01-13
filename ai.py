import math 
from game_state_pyrsistent import GameState,get_all_possible_rolls
from evaluation import Evaluation

class AI:
    def __init__(self,player_symbol,depth):
        self.player=player_symbol
        self.depth=depth
        self.evaluator=Evaluation(player_symbol)

    def evaluation(self,state):
        board=state.get_board()
        return self.evaluator.evaluate_board(board)

    def choose_best_move(self, state,roll):
        best_value = -math.inf
        best_move = None

        for move in state.get_valid_moves(roll):
            value = self.expectiminimax(
                state.apply_move(move[0], move[1]),
                self.depth - 1,
                False
            )

            if value > best_value:
                best_value = value
                best_move = move

        return best_move
    def expectiminimax(self,state,depth,is_max):
        if depth == 0 or state.is_terminal():
            return self.evaluation(state)
        expected_value = 0.0
        rolls = get_all_possible_rolls()

        for roll, prob in rolls:
            moves = state.get_valid_moves(roll)

            if not moves:
                val = self.expectiminimax(
                    state, depth - 1, not is_max
                )
                expected_value += prob * val
                continue

            if is_max:
                best = -math.inf
                for move in moves:
                    child = state.apply_move(move[0], move[1])
                    best = max(
                        best,
                        self.expectiminimax(
                            child, depth - 1, False
                        )
                    )
                expected_value += prob * best

            else:
                best = math.inf
                for move in moves:
                    child = state.apply_move(move[0], move[1])
                    best = min(
                        best,
                        self.expectiminimax(
                            child, depth - 1, True
                        )
                    )
                expected_value += prob * best

        return expected_value

        