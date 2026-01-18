import random

def throw_sticks():
    sticks = [random.choice([0, 1]) for _ in range(4)]  # 0=Round, 1=Flat
    score = sum(sticks)

    if score == 0:
        return 5  # All round sides up = 5
    return score

