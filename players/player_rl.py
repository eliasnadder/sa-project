import random
import json
import os
import csv  # إضافة للحفظ في CSV
from datetime import datetime
import glob
from engines.game_state_pyrsistent import GameState
from evaluations.evaluation_ai_star1 import Evaluation, SENET_AI_CONFIG


class QLearningAI:
    def __init__(self, opponent, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.1, weights_update_rate=0.05):
        self.opponent = opponent
        self.q_table = {}  # {state_hash: {action_tuple: q_value}}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.weights_update_rate = weights_update_rate
        self.weights = SENET_AI_CONFIG.copy()
        self.actions_taken = []
        self.evaluator = Evaluation(opponent, config=self.weights)

    def choose_best_move(self, state: GameState, roll):
        valid_moves = state.get_valid_moves(roll)

        valid_moves.sort(
            key=lambda m: self.evaluator.evaluate_move_priority(m), reverse=True)

        board = state.get_board()
        valid_moves.sort(key=lambda m: self.evaluator.evaluate_board(
            board, valid_moves=valid_moves), reverse=True)

        if not valid_moves:
            return None

        state_hash = hash(tuple(state.get_board()))

        if random.random() < self.exploration_rate:
            move = random.choice(valid_moves)
        else:
            best_value = -float('inf')
            best_move = None
            for move in valid_moves:
                child_state = state.apply_move(move[0], move[1])
                eval_score = self.evaluator.evaluate_board(
                    child_state.get_board(), self.weights)
                action_hash = hash(move)
                q_value = self.q_table.get(state_hash, {}).get(
                    action_hash, 0) + eval_score
                if q_value > best_value:
                    best_value = q_value
                    best_move = move
            move = best_move or random.choice(valid_moves)

        self.actions_taken.append((state_hash, hash(move), 0))
        return move

    def update_from_game(self, reward):
        for i in range(len(self.actions_taken) - 1):
            state_hash, action_hash, _ = self.actions_taken[i]
            next_state_hash, _, _ = self.actions_taken[i+1]
            current_q = self.q_table.get(state_hash, {}).get(action_hash, 0)
            max_next_q = max(self.q_table.get(
                next_state_hash, {}).values(), default=0)
            new_q = current_q + self.learning_rate * \
                (0 + self.discount_factor * max_next_q - current_q)
            self.q_table.setdefault(state_hash, {})[action_hash] = new_q

        if self.actions_taken:
            state_hash, action_hash, _ = self.actions_taken[-1]
            current_q = self.q_table.get(state_hash, {}).get(action_hash, 0)
            new_q = current_q + self.learning_rate * (reward - current_q)
            self.q_table.setdefault(state_hash, {})[action_hash] = new_q

        adjustment = self.weights_update_rate if reward > 0 else -self.weights_update_rate
        for key in self.weights:
            self.weights[key] *= (1 + adjustment * random.uniform(-0.5, 0.5))

        self.actions_taken = []

    def save_data(self, folder="training_logs"):
        os.makedirs(folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_json = os.path.join(folder, f"ai_data_{timestamp}.json")
        filename_csv = os.path.join(folder, f"q_table_{timestamp}.csv")

        # حفظ JSON
        data = {
            "q_table": self.q_table,
            "weights": self.weights
        }
        with open(filename_json, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"AI data saved to {filename_json}")

        # حفظ Q-table في CSV لمشاهدة سهلة
        with open(filename_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ['State Hash', 'Action Hash', 'Q-Value'])  # رأس الجدول
            for state_hash, actions in self.q_table.items():
                for action_hash, q_value in actions.items():
                    writer.writerow([state_hash, action_hash, q_value])
        print(
            f"Q-table saved as CSV table to {filename_csv} (open in Excel to view records)")

    def load_latest_data(self, folder="training_logs"):
        files = glob.glob(os.path.join(folder, "ai_data_*.json"))
        if files:
            latest_file = max(files, key=os.path.getmtime)
            with open(latest_file, 'r') as f:
                data = json.load(f)
            self.q_table = data.get("q_table", {})
            self.weights = data.get("weights", SENET_AI_CONFIG.copy())
            print(f"Loaded latest AI data from {latest_file}")
        else:
            print("No previous AI data found. Starting fresh.")
