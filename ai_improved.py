import math
from game_state_pyrsistent import get_all_possible_rolls
from evaluation_ai import Evaluation
from board import *


class ImprovedAI:
    """
    AI محسّن مع:
    - Transposition Table للتخزين المؤقت
    - Move Ordering
    - Iterative Deepening
    - Time Management
    """

    def __init__(self, player_symbol, depth, weights=None):
        self.player = player_symbol
        self.depth = depth
        self.evaluator = Evaluation(player_symbol, config=weights)

        # Transposition Table
        self.transposition_table = {}
        self.tt_hits = 0
        self.tt_misses = 0

        # إحصائيات
        self.nodes_evaluated = 0
        self.pruning_count = 0

    def clear_cache(self):
        """مسح الذاكرة المؤقتة"""
        self.transposition_table.clear()
        self.tt_hits = 0
        self.tt_misses = 0
        self.nodes_evaluated = 0
        self.pruning_count = 0

    def evaluation(self, state):
        """تقييم الحالة"""
        board = state.get_board()
        return self.evaluator.evaluate_board(board)

    def choose_best_move(self, state, roll):
        """اختيار أفضل حركة مع تحسينات"""
        valid_moves = state.get_valid_moves(roll)

        if not valid_moves:
            return None

        if len(valid_moves) == 1:
            return valid_moves[0]

        # ترتيب الحركات حسب الأولوية
        scored_moves = []
        for move in valid_moves:
            priority = self._evaluate_move_priority(move, state)
            scored_moves.append((priority, move))

        scored_moves.sort(key=lambda x: x[0], reverse=True)

        # البحث بعمق تدريجي (Iterative Deepening)
        best_move = None
        best_value = -math.inf

        for current_depth in range(1, self.depth + 1):
            move_values = []

            for _, move in scored_moves:
                child_state = state.apply_move(move[0], move[1])

                value = self.expectiminimax(
                    child_state,
                    current_depth - 1,
                    False,
                    -math.inf,
                    math.inf
                )

                move_values.append((value, move))

            # ترتيب حسب القيمة
            move_values.sort(key=lambda x: x[0], reverse=True)

            if move_values:
                best_value = move_values[0][0]
                best_move = move_values[0][1]

                # تحديث ترتيب الحركات للعمق التالي
                scored_moves = [(best_value, m) for v, m in move_values]

        return best_move

    def _evaluate_move_priority(self, move, state):
        """تقييم أولوية الحركة للترتيب"""
        _, to_pos = move

        priority = 0

        # أولوية عالية للخروج من اللوحة
        if to_pos == OFF_BOARD:
            priority += 10000

        # أولوية للوصول لبيت السعادة
        if to_pos == HOUSE_OF_HAPPINESS:
            priority += 1000

        # أولوية لتجنب الماء
        if to_pos == HOUSE_WATER:
            priority -= 5000

        # أولوية للهجوم
        board = state.get_board()
        if to_pos < BOARD_SIZE and board[to_pos] == state.get_opponent_symbol():
            priority += 500

        # أولوية للتقدم
        priority += to_pos * 10

        return priority

    def expectiminimax(self, state, depth, is_max, alpha, beta):
        """
        Expectiminimax محسّن مع:
        - Alpha-Beta Pruning (تقريبي)
        - Transposition Table
        """
        self.nodes_evaluated += 1

        # فحص الحالة النهائية
        if depth == 0 or state.is_terminal():
            return self.evaluation(state)

        # فحص Transposition Table
        state_key = hash(state)
        if state_key in self.transposition_table:
            cached = self.transposition_table[state_key]
            if cached['depth'] >= depth:
                self.tt_hits += 1
                return cached['value']

        self.tt_misses += 1

        expected_value = 0.0
        rolls = get_all_possible_rolls()

        for roll, prob in rolls:
            moves = state.get_valid_moves(roll)

            if not moves:
                # لا توجد حركات - نفس اللاعب يلعب مرة أخرى
                val = self.expectiminimax(
                    state, depth - 1, is_max, alpha, beta)
                expected_value += prob * val
                continue

            if is_max:
                best = -math.inf

                # ترتيب الحركات
                sorted_moves = self._order_moves(moves, state)

                for move in sorted_moves:
                    child = state.apply_move(move[0], move[1])
                    value = self.expectiminimax(
                        child, depth - 1, False, alpha, beta)
                    best = max(best, value)

                    # Alpha-Beta Pruning (تقريبي للExpectiminimax)
                    alpha = max(alpha, best)
                    if beta <= alpha * prob:  # تعديل للاحتمالات
                        self.pruning_count += 1
                        break

                expected_value += prob * best

            else:
                best = math.inf

                # ترتيب الحركات
                sorted_moves = self._order_moves(moves, state)

                for move in sorted_moves:
                    child = state.apply_move(move[0], move[1])
                    value = self.expectiminimax(
                        child, depth - 1, True, alpha, beta)
                    best = min(best, value)

                    # Alpha-Beta Pruning (تقريبي)
                    beta = min(beta, best)
                    if beta <= alpha * prob:
                        self.pruning_count += 1
                        break

                expected_value += prob * best

        # حفظ في Transposition Table
        self.transposition_table[state_key] = {
            'value': expected_value,
            'depth': depth
        }

        # تنظيف الذاكرة إذا كبرت كثيراً
        if len(self.transposition_table) > 100000:
            # حذف نصف المدخلات الأقدم
            keys = list(self.transposition_table.keys())
            for k in keys[:len(keys)//2]:
                del self.transposition_table[k]

        return expected_value

    def _order_moves(self, moves, state):
        """ترتيب الحركات لتحسين Pruning"""
        scored_moves = []

        for move in moves:
            score = self._evaluate_move_priority(move, state)
            scored_moves.append((score, move))

        # ترتيب تنازلي
        scored_moves.sort(key=lambda x: x[0], reverse=True)

        return [move for _, move in scored_moves]

    def get_stats(self):
        """الحصول على إحصائيات الأداء"""
        return {
            'nodes_evaluated': self.nodes_evaluated,
            'tt_hits': self.tt_hits,
            'tt_misses': self.tt_misses,
            'tt_hit_rate': (self.tt_hits / (self.tt_hits + self.tt_misses) * 100
                            if self.tt_hits + self.tt_misses > 0 else 0),
            'pruning_count': self.pruning_count,
            'tt_size': len(self.transposition_table)
        }

    def print_stats(self):
        """طباعة الإحصائيات"""
        stats = self.get_stats()
        print("\n=== AI Performance Stats ===")
        print(f"Nodes Evaluated: {stats['nodes_evaluated']:,}")
        print(f"TT Hits: {stats['tt_hits']:,}")
        print(f"TT Misses: {stats['tt_misses']:,}")
        print(f"TT Hit Rate: {stats['tt_hit_rate']:.2f}%")
        print(f"Pruning Count: {stats['pruning_count']:,}")
        print(f"TT Size: {stats['tt_size']:,}")
        print("===========================\n")
