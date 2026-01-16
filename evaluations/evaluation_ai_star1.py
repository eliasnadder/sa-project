from engines.board import (
    HOUSE_OF_HAPPINESS, HOUSE_WATER,
    BOARD_SIZE, OFF_BOARD
)

# الإعدادات الافتراضية
SENET_AI_CONFIG = {
    'piece_off': 1200,          # نقاط الخروج
    'win_bonus': 20000,         # مكافأة الفوز
    'progress_base': 85,        # أساس التقدم
    'zone_multiplier': 1.8,     # مضاعف المنطقة
    'happiness_bonus': 150,     # مكافأة خانة السعادة
    'water_penalty': -300,      # عقوبة خانة الماء
    'special_house': 100,       # مكافأة الخانات الخاصة
    'protection': 60,           # نقاط الحماية
    'block': 80,                # نقاط التكتل
    'attack': 60,               # نقاط الهجوم
    'flexibility': 8,           # نقاط المرونة
    'isolated_penalty': 15      # عقوبة القطع المعزولة
}

# تحديد الحدود القصوى والدنيا للنقاط لغرض التقليم (Star1 Pruning)
# القيمة يجب أن تكون أكبر من أي تقييم فعلي ممكن للوح
MAX_POSSIBLE_SCORE = 50000
MIN_POSSIBLE_SCORE = -50000


class Evaluation:
    def __init__(self, player, config=None):
        self.player = player
        self.opponent = 'O' if player == 'X' else 'X'
        self.config = config if config else SENET_AI_CONFIG

    def evaluate_board(self, board, valid_moves=None):
        my_indices = [i for i, cell in enumerate(board) if cell == self.player]
        opp_indices = [i for i, cell in enumerate(
            board) if cell == self.opponent]

        # شروط الفوز والخسارة النهائية
        if not my_indices:
            return self.config['win_bonus']
        if not opp_indices:
            return -self.config['win_bonus']

        score = 0

        # نقاط الخروج والتقدم
        score += (7 - len(my_indices)) * self.config['piece_off']
        score -= (7 - len(opp_indices)) * self.config['piece_off']

        for pos in my_indices:
            mult = self.config['zone_multiplier'] if pos >= 20 else 1.0
            score += (pos + 1) * self.config['progress_base'] * mult

            # الخانات الخاصة والتكتيك
            if pos == HOUSE_OF_HAPPINESS:
                score += self.config['happiness_bonus']
            elif pos == HOUSE_WATER:
                score += self.config['water_penalty']

            # الدفاع (وجود قطع بجانب بعضها)
            if (pos > 0 and board[pos-1] == self.player) or (pos < BOARD_SIZE-1 and board[pos+1] == self.player):
                score += self.config['protection']

        # خصم نقاط الخصم (لجعل التقييم متوازناً Zero-sum)
        for pos in opp_indices:
            mult = self.config['zone_multiplier'] if pos >= 20 else 1.0
            score -= (pos + 1) * self.config['progress_base'] * mult
            if (pos > 0 and board[pos-1] == self.opponent) or (pos < BOARD_SIZE-1 and board[pos+1] == self.opponent):
                score -= self.config['protection']

        # تقييم القطع المعزولة
        score += self._evaluate_isolated_pieces(board)
        
        # مكافأة المرونة (عدد الحركات الممكنة)
        if valid_moves:
            score += len(valid_moves) * self.config['flexibility']

        # التأكد من أن النتيجة ضمن الحدود (Clamping)
        return max(MIN_POSSIBLE_SCORE + 1, min(score, MAX_POSSIBLE_SCORE - 1))

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
            return 1000
        return 0
