from engines.board import (
    HOUSE_OF_HAPPINESS, HOUSE_WATER,
    BOARD_SIZE, OFF_BOARD
)

SENET_AI_CONFIG = {
    'piece_off': 1200,
    'win_bonus': 20000,
    'progress_base': 85,
    'zone_multiplier': 1.8,
    'happiness_bonus': 150,
    'water_penalty': -300,
    'special_house': 100,
    'protection': 60,
    'block': 80,
    'attack': 60,
    'flexibility': 8,
    'isolated_penalty': 15
}

# Phase multipliers - THIS IS THE KEY ADDITION
PHASE_MULTIPLIERS = {
    'opening': {
        'progress_base': 0.9,       # قليل الأهمية في البداية
        'block': 1.5,               # مهم جداً للمنع
        'protection': 1.6,          # مهم للدفاع
        'attack': 0.4,
        'isolated_penalty': 0.8     # ليس مهم جداً
    },
    'midgame': {
        'progress_base': 1.8,       # متوازن
        'block': 1.0,
        'protection': 1.0,
        'attack': 1.0,              # فرص الهجوم
        'isolated_penalty': 1.2     # مهم في الوسط
    },
    'endgame': {
        'progress_base': 2.0,       # حاسم للفوز
        'piece_off': 1.5,           # أهم شيء
        'block': 0.4,               # قليل الأهمية
        'protection': 0.5,          # قليل الأهمية
        'attack': 0.6,
        'isolated_penalty': 0.5     # ليس مهم
    }
}

MAX_POSSIBLE_SCORE = 50000
MIN_POSSIBLE_SCORE = -50000


class Evaluation:
    def __init__(self, player, config=None):
        self.player = player
        self.opponent = 'O' if player == 'X' else 'X'
        self.base_config = config if config else SENET_AI_CONFIG
        self.config = self.base_config.copy()

        # للتتبع والتحليل
        self.phase_stats = {'opening': 0, 'midgame': 0, 'endgame': 0}
        self.debug = False  # اضبطه على True للتحليل

    def _get_game_phase(self, board):
        """تحديد مرحلة اللعبة بدقة أعلى"""
        my_indices = [i for i, cell in enumerate(board) if cell == self.player]
        opp_indices = [i for i, cell in enumerate(
            board) if cell == self.opponent]

        if not my_indices or not opp_indices:
            return 'endgame'

        # عدد القطع خارج اللوحة
        my_pieces_off = 7 - len(my_indices)
        opp_pieces_off = 7 - len(opp_indices)
        total_off = my_pieces_off + opp_pieces_off

        # متوسط مواقع القطع
        all_positions = my_indices + opp_indices
        avg_pos = sum(all_positions) / len(all_positions)
        max_pos = max(all_positions)

        # قواعد تحديد المرحلة (محسّنة)
        # Opening: لا قطع خارج اللوحة + معظم القطع قبل 15
        if total_off == 0 and max_pos < 15:
            return 'opening'

        # Endgame: 3+ قطع خارجة أو معظم القطع بعد 20
        if total_off >= 3 or avg_pos >= 22:
            return 'endgame'

        # Midgame: كل شيء بينهما
        return 'midgame'

    def _apply_phase_adjustments(self, phase):
        """Apply phase-specific weight multipliers"""
        multipliers = PHASE_MULTIPLIERS.get(phase, {})

        adjusted_config = self.base_config.copy()
        for key, multiplier in multipliers.items():
            if key in adjusted_config:
                adjusted_config[key] = self.base_config[key] * multiplier

        return adjusted_config

    def evaluate_board(self, board, valid_moves=None):
        my_indices = [i for i, cell in enumerate(board) if cell == self.player]
        opp_indices = [i for i, cell in enumerate(
            board) if cell == self.opponent]

        # Terminal states
        if not my_indices:
            return self.config['win_bonus']
        if not opp_indices:
            return -self.config['win_bonus']

        # Get phase and adjust weights
        phase = self._get_game_phase(board)
        self.config = self._apply_phase_adjustments(phase)

        # تتبع الإحصائيات
        self.phase_stats[phase] += 1

        score = 0

        # Pieces off board
        score += (7 - len(my_indices)) * self.config['piece_off']
        score -= (7 - len(opp_indices)) * self.config['piece_off']

        # Progress evaluation
        for pos in my_indices:
            mult = self.config['zone_multiplier'] if pos >= 20 else 1.0
            score += (pos + 1) * self.config['progress_base'] * mult

            # Special houses
            if pos == HOUSE_OF_HAPPINESS:
                score += self.config['happiness_bonus']
            elif pos == HOUSE_WATER:
                score += self.config['water_penalty']

            # Protection (adjacent allies)
            if (pos > 0 and board[pos-1] == self.player) or \
               (pos < BOARD_SIZE-1 and board[pos+1] == self.player):
                score += self.config['protection']

        # Opponent progress (negative)
        for pos in opp_indices:
            mult = self.config['zone_multiplier'] if pos >= 20 else 1.0
            score -= (pos + 1) * self.config['progress_base'] * mult
            if (pos > 0 and board[pos-1] == self.opponent) or \
               (pos < BOARD_SIZE-1 and board[pos+1] == self.opponent):
                score -= self.config['protection']

        # Blocking evaluation (ENHANCED)
        score += self._evaluate_blocking(board, my_indices, opp_indices)

        # Isolated pieces penalty
        score += self._evaluate_isolated_pieces(board)

        # Flexibility
        if valid_moves:
            score += len(valid_moves) * self.config['flexibility']

        # Debug logging
        if self.debug:
            print(f"  Phase: {phase}, Score: {score:.1f}, "
                  f"Progress weight: {self.config['progress_base']:.1f}, "
                  f"Block weight: {self.config['block']:.1f}")

        return max(MIN_POSSIBLE_SCORE + 1, min(score, MAX_POSSIBLE_SCORE - 1))

    def _evaluate_blocking(self, board, my_indices, opp_indices):
        """Enhanced blocking evaluation"""
        score = 0

        # Check each opponent piece
        for opp_pos in opp_indices:
            # Look ahead 1-3 squares
            for distance in range(1, 4):
                check_pos = opp_pos + distance
                if check_pos < BOARD_SIZE and board[check_pos] == self.player:
                    # We're blocking opponent's path
                    block_value = self.config['block'] / distance
                    score += block_value

                    # Bonus if we form a wall (2+ pieces)
                    if check_pos > 0 and board[check_pos-1] == self.player:
                        score += self.config['block'] * 0.5
                    if check_pos < BOARD_SIZE-1 and board[check_pos+1] == self.player:
                        score += self.config['block'] * 0.5

        return score

    def _evaluate_isolated_pieces(self, board):
        score = 0
        for i, c in enumerate(board):
            if c == self.player:
                left = i > 0 and board[i-1] == self.player
                right = i < BOARD_SIZE - 1 and board[i+1] == self.player
                if not left and not right:
                    score -= self.config['isolated_penalty']
        return score

    def evaluate_move_priority(self, move):
        from_pos, to_pos = move
        if to_pos == OFF_BOARD:
            return 10000
        return 0

    def get_phase_statistics(self):
        """إرجاع إحصائيات المراحل"""
        total = sum(self.phase_stats.values())
        if total == 0:
            return "No evaluations yet"

        return {
            'opening': f"{self.phase_stats['opening']/total*100:.1f}%",
            'midgame': f"{self.phase_stats['midgame']/total*100:.1f}%",
            'endgame': f"{self.phase_stats['endgame']/total*100:.1f}%",
            'total_evals': total
        }

    def print_statistics(self):
        """طباعة إحصائيات الاستخدام"""
        stats = self.get_phase_statistics()
        print(f"\nPhase Statistics:")
        print(f"  Opening:  {stats['opening']}")
        print(f"  Midgame:  {stats['midgame']}")
        print(f"  Endgame:  {stats['endgame']}")
        print(f"  Total evaluations: {stats['total_evals']}")

    def get_effective_weights(self, phase):
        """الحصول على الأوزان الفعلية لمرحلة معينة"""
        adjusted = self._apply_phase_adjustments(phase)
        return {
            'phase': phase,
            'progress_base': adjusted['progress_base'],
            'block': adjusted['block'],
            'protection': adjusted['protection'],
            'attack': adjusted['attack'],
            'ratio_progress_to_block': adjusted['progress_base'] / adjusted['block']
        }
