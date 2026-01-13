# expectiminimax.py

from math import inf
from evaluation import Evaluation
from game_state_pyrsistent import GameState ,get_all_possible_rolls

def expectiminimax(state: GameState, depth: int, evaluator: Evaluation):
    score, move = _max_node(state, depth, evaluator)
    return score, move


def _max_node(state: GameState, depth: int, evaluator: Evaluation):
    if depth == 0 or state.is_terminal():
        return evaluator.evaluate_board(state.get_board()), None

    best_score = -inf
    best_move = None

    # Chance node: iterate over all possible rolls
    for roll, prob in get_all_possible_rolls():
        score, move = _chance_node(
            state=state,
            depth=depth,
            roll=roll,
            evaluator=evaluator,
            maximizing=True
        )

        expected_score += prob * score

        if expected_score > best_score:
            best_score = expected_score
            best_move = move

    return best_score, best_move


# ------------------------------------------------------------------
# MIN NODE (Opponent)
# ------------------------------------------------------------------

def _min_node(state: GameState, depth: int, evaluator: Evaluation):
    if depth == 0 or state.is_terminal():
        return evaluator.evaluate_board(state.get_board()), None

    worst_score = inf
    worst_move = None

    for roll, prob in get_all_possible_rolls():
        score, move = _chance_node(
            state=state,
            depth=depth,
            roll=roll,
            evaluator=evaluator,
            maximizing=False
        )

        expected_score += prob * score

        if expected_score < worst_score:
            worst_score = expected_score
            worst_move = move

    return worst_score, worst_move


# ------------------------------------------------------------------
# CHANCE NODE (Stick Throw)
# ------------------------------------------------------------------

def _chance_node(state: GameState, depth: int, roll: int,
                 evaluator: Evaluation, maximizing: bool):
    """
    Handles chance node (dice / stick roll).
    """

    valid_moves = state.get_valid_moves(roll)

    # No legal moves -> pass turn
    if not valid_moves:
        next_state = GameState(
            state.get_vector(),
            -state.get_current_player()
        )

        if maximizing:
            return _min_node(next_state, depth - 1, evaluator)[0], None
        else:
            return _max_node(next_state, depth - 1, evaluator)[0], None

    # Evaluate all possible moves
    if maximizing:
        best_score = -inf
        best_move = None

        for move in valid_moves:
            from_pos, to_pos = move
            new_state = state.apply_move(from_pos, to_pos)

            score, _ = _min_node(new_state, depth - 1, evaluator)

            if score > best_score:
                best_score = score
                best_move = move

        return best_score, best_move

    else:
        worst_score = inf
        worst_move = None

        for move in valid_moves:
            from_pos, to_pos = move
            new_state = state.apply_move(from_pos, to_pos)

            score, _ = _max_node(new_state, depth - 1, evaluator)

            if score < worst_score:
                worst_score = score
                worst_move = move

        return worst_score, worst_move