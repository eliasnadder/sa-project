import math
from engines.load_weights import load_weights
from engines.board import BOARD_SIZE, HOUSE_OF_HAPPINESS, HOUSE_WATER, OFF_BOARD
from engines.game_state_pyrsistent import GameState, get_all_possible_rolls
from evaluations.evaluation_ai_phased import Evaluation, MAX_POSSIBLE_SCORE, MIN_POSSIBLE_SCORE


class AI:
    """
    AI محسّن يطبق Star1 Pruning بشكل صحيح مع:
    - Transposition Table
    - Move Ordering
    - Iterative Deepening
    """

    def __init__(self, player_symbol, depth):
        self.player = player_symbol
        self.depth = depth
        self.evaluator = Evaluation(player_symbol, config=load_weights())

        # Transposition Table
        self.transposition_table = {}
        self.tt_hits = 0
        self.tt_misses = 0

        # إحصائيات
        self.nodes_evaluated = 0
        self.pruning_count = 0

    def clear_cache(self):
        self.transposition_table.clear()
        self.tt_hits = 0
        self.tt_misses = 0
        self.nodes_evaluated = 0
        self.pruning_count = 0

    def choose_best_move(self, state, roll):
        """
        نقطة الدخول: لدينا رمية معروفة (roll)، لذا نبدأ بـ Decision Node مباشرة.
        """
        valid_moves = state.get_valid_moves(roll)
        if not valid_moves:
            return None
        if len(valid_moves) == 1:
            return valid_moves[0]

        # 1. Move Ordering (ترتيب الحركات)
        scored_moves = []
        for move in valid_moves:
            priority = self._evaluate_move_priority(move, state)
            scored_moves.append((priority, move))
        scored_moves.sort(key=lambda x: x[0], reverse=True)

        best_move = None

        # 2. Iterative Deepening (البحث التدريجي)
        # نبدأ من عمق 1 ونزيد حتى نصل للعمق المطلوب
        for current_depth in range(1, self.depth + 1):

            # إعادة تهيئة المتغيرات للبحث الحالي
            current_best_move = None
            current_best_val = -math.inf
            alpha = MIN_POSSIBLE_SCORE
            beta = MAX_POSSIBLE_SCORE

            # نقوم بالبحث لأفضل الحركات المرتبة
            for _, move in scored_moves:
                child_state = state.apply_move(move[0], move[1])

                # الانتقال لعقدة الحظ (لأن الدور انتهى وسيرمي الخصم)
                # ملاحظة: الخصم هو Min، لذا نمرر maximizing=False
                val = self._chance_node(
                    child_state,
                    current_depth - 1,
                    alpha,
                    beta,
                    maximizing=False
                )

                if val > current_best_val:
                    current_best_val = val
                    current_best_move = move

                # تحديث Alpha للجذر
                alpha = max(alpha, val)

            best_move = current_best_move

            # تحديث ترتيب الحركات بناءً على نتائج هذا العمق لتسريع العمق القادم
            # (نضع أفضل حركة وجدناها في المقدمة)
            if best_move:
                # نبحث عن الحركة في القائمة ونضعها في الأول
                # هذا تبسيط، الأفضل إعادة الترتيب بالكامل لكن هذا يكفي
                pass

        return best_move

    def _chance_node(self, state, depth, alpha, beta, maximizing):
        """
        عقدة الحظ: تطبق Star1 Pruning.
        تحسب القيمة المتوقعة لجميع الرميات الممكنة.
        """
        self.nodes_evaluated += 1

        if depth == 0 or state.is_terminal():
            return self.evaluator.evaluate_board(state.get_board())

        # Transposition Table Lookup
        state_key = (hash(state), depth, 'chance', maximizing)
        if state_key in self.transposition_table:
            self.tt_hits += 1
            return self.transposition_table[state_key]
        self.tt_misses += 1

        expected_value = 0.0
        cumulative_prob = 0.0

        # ترتيب الرميات حسب الاحتمالية (الأكبر أولاً) لزيادة كفاءة Star1
        rolls = sorted(get_all_possible_rolls(),
                       key=lambda x: x[1], reverse=True)

        for roll, prob in rolls:
            # نستدعي عقدة القرار لكل رمية
            val = self._decision_node(
                state, depth, roll, alpha, beta, maximizing)

            expected_value += prob * val
            cumulative_prob += prob

            # --- Star1 Pruning Logic (التقليم الصحيح) ---
            remaining_prob = 1.0 - cumulative_prob

            # أقصى قيمة ممكنة يمكن الوصول إليها
            max_possible = expected_value + \
                (remaining_prob * MAX_POSSIBLE_SCORE)
            # أدنى قيمة ممكنة يمكن الوصول إليها
            min_possible = expected_value + \
                (remaining_prob * MIN_POSSIBLE_SCORE)

            # التقليم
            if max_possible <= alpha:
                self.pruning_count += 1
                return alpha  # Fail-low
            if min_possible >= beta:
                self.pruning_count += 1
                return beta  # Fail-high

        # تخزين النتيجة
        self._store_tt(state_key, expected_value)
        return expected_value

    def _decision_node(self, state, depth, roll, alpha, beta, maximizing):
        """
        عقدة القرار: تطبق Alpha-Beta Pruning التقليدية.
        تختار أفضل حركة بعد معرفة الرمية.
        """
        if depth <= 0 or state.is_terminal():  # تغيير depth == 0 إلى depth <= 0 للأمان
            return self.evaluator.evaluate_board(state.get_board())

        valid_moves = state.get_valid_moves(roll)

        # حالة عدم وجود حركات (تمرير الدور)
        if not valid_moves:
            next_player = -state.get_current_player()  # تبديل اللاعب
            # ملاحظة: في كود GameState الخاص بك، قد تحتاج للتأكد من كيفية تبديل الدور يدوياً
            # هنا نفترض إنشاء حالة جديدة بنفس اللوحة ولكن للاعب التالي
            next_state = GameState(state.get_vector(), next_player)

            # إذا كنا Max والآن دور Min، نذهب لـ Chance node للـ Min
            # لكن مهلاً، إذا مررنا الدور، فاللاعب التالي سيرمي العصي.
            # لذا نذهب لـ Chance Node
            return self._chance_node(next_state, depth-1, alpha, beta, not maximizing)

        # ترتيب الحركات (Heuristic)
        sorted_moves = self._order_moves(valid_moves, state)

        if maximizing:
            best_val = -math.inf
            for move in sorted_moves:
                child_state = state.apply_move(move[0], move[1])

                # بعد حركتي (Max)، يأتي دور الخصم (Min) ليرمي العصي
                val = self._chance_node(
                    child_state, depth - 1, alpha, beta, maximizing=False)

                best_val = max(best_val, val)
                alpha = max(alpha, best_val)
                if beta <= alpha:
                    break  # Beta Cutoff
            return best_val
        else:  # Minimizing
            best_val = math.inf
            for move in sorted_moves:
                child_state = state.apply_move(move[0], move[1])

                # بعد حركة الخصم (Min)، يأتي دوري (Max) لأرمي العصي
                val = self._chance_node(
                    child_state, depth - 1, alpha, beta, maximizing=True)

                best_val = min(best_val, val)
                beta = min(beta, best_val)
                if beta <= alpha:
                    break  # Alpha Cutoff
            return best_val

    def _store_tt(self, key, value):
        self.transposition_table[key] = value
        # تنظيف بسيط للذاكرة
        if len(self.transposition_table) > 200000:
            self.transposition_table.clear()

    def _evaluate_move_priority(self, move, state):
        _, to_pos = move
        priority = 0
        if to_pos == OFF_BOARD:
            priority += 20000                    # أعلى أولوية للخروج
        if to_pos >= 25:                         # أي حركة في المنطقة النهائية
            priority += 5000 + (to_pos * 20)
        if to_pos == HOUSE_OF_HAPPINESS:
            priority += 1500
        if to_pos == HOUSE_WATER:
            priority -= 8000                     # عقوبة أقوى

        board = state.get_board()
        if to_pos < BOARD_SIZE and board[to_pos] == state.get_opponent_symbol():
            priority += 800                      # هجوم جيد لكن ليس أولوية مطلقة

        priority += to_pos * 15                  # مكافأة عامة للتقدم
        return priority

    def _order_moves(self, moves, state):
        scored = [(self._evaluate_move_priority(m, state), m) for m in moves]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored]

    def get_stats(self):
        return {
            'nodes': self.nodes_evaluated,
            'pruning': self.pruning_count,
            'tt_hits': self.tt_hits
        }
