"""Senet stick throwing mechanics."""
import random


def throw_sticks():
    """
    Simulates throwing 4 casting sticks.
    Calculates move value based on binary probability.
    - 1 flat side up = 1 move (Prob 25%)
    - 2 flat sides up = 2 moves (Prob 37.5%)
    - 3 flat sides up = 3 moves (Prob 25%)
    - 4 flat sides up = 4 moves (Prob 6.25%)
    - 0 flat sides up = 5 moves (Prob 6.25%)
    """
    sticks = [random.choice([0, 1]) for _ in range(4)]  # 0=Round, 1=Flat
    score = sum(sticks)

    if score == 0:
        return 5  # All round sides up = 5
    return score

#! Blocked until finish search
# def grants_extra_turn(roll):
#     """
#     Returns True if the roll grants an extra turn.
#     Kendall's rules: 1, 4, and 5 grant an extra turn.
#     """
#     return roll in [1, 4, 5]
