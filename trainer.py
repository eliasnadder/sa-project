# trainer.py
import random
import json
import matplotlib.pyplot as plt
from ai import AI
from evaluation_ai import SENET_AI_CONFIG, Evaluation
from game_state_pyrsistent import GameState
from board import create_initial_board
from rules import apply_move, check_win
from sticks import throw_sticks

# إعدادات التدريب
POP_SIZE = 10
GENS = 20


class Trainer:
    def __init__(self):
        self.population = [self._randomize_dna() for _ in range(POP_SIZE)]
        self.stats = []

    def _randomize_dna(self):
        dna = SENET_AI_CONFIG.copy()
        for k in dna:
            dna[k] *= random.uniform(0.7, 1.3)
        return dna

    def run(self):
        print("Starting Evolutionary Training...")
        for g in range(GENS):
            scores = []
            for dna in self.population:
                wins = sum(1 for _ in range(3) if self.play_match(dna) == 'X')
                scores.append((wins, dna))

            scores.sort(key=lambda x: x[0], reverse=True)
            self.stats.append(scores[0][0])
            print(f"Gen {g+1}: Best score {scores[0][0]}")

            # تكاثر الأقوياء
            best_dnas = [x[1] for x in scores[:POP_SIZE//2]]
            self.population = best_dnas + \
                [self._mutate(random.choice(best_dnas))
                 for _ in range(POP_SIZE//2)]

        # حفظ النتيجة
        with open("best_ai_weights.json", "w") as f:
            json.dump(scores[0][1], f, indent=4)

        plt.plot(self.stats)
        plt.title("Learning Curve")
        plt.savefig("evolution_plot.png")
        plt.show()

    def play_match(self, dna):
        board = create_initial_board()
        ai_x = AI('X', 1, weights=dna)
        ai_o = AI('O', 1)
        for _ in range(100):
            r = throw_sticks()
            m = ai_x.choose_best_move(GameState.from_board(board, 'X'), r)
            if m:
                board = apply_move(board, m[0], m[1])
                if check_win(board, 'X'):
                    return 'X'
        return 'O'

    def _mutate(self, dna):
        new_dna = dna.copy()
        k = random.choice(list(new_dna.keys()))
        new_dna[k] *= random.uniform(0.9, 1.1)
        return new_dna


if __name__ == "__main__":
    trainer = Trainer()
    trainer.run()