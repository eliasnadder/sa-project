# evaluation.py
from board import (
    HOUSE_OF_HAPPINESS, HOUSE_WATER, HOUSE_THREE_TRUTHS,
    HOUSE_RE_ATUM, HOUSE_HORUS, HOUSE_REBIRTH, BOARD_SIZE, OFF_BOARD
)

# الإعدادات الافتراضية - سيتم استيرادها بواسطة trainer.py وتعديلها
SENET_AI_CONFIG = {
    'piece_off': 1200,
    'win_bonus': 20000,
    'progress_base': 40,
    'zone_multiplier': 1.8,
    'happiness_bonus': 150,
    'water_penalty': -300,
    'special_house': 100,
    'protection': 80,
    'block': 120,
    'attack': 30,
    'flexibility': 8
}

class Evaluation:
    def __init__(self, player, config=None):
        self.player = player
        self.opponent = 'O' if player == 'X' else 'X'
        # إذا لم يتم تمرير config، نستخدم الإعدادات الافتراضية أعلاه
        self.config = config if config else SENET_AI_CONFIG

    def evaluate_board(self, board, valid_moves=None):
        player_pos = [i for i, cell in enumerate(board) if cell == self.player]
        opp_pos = [i for i, cell in enumerate(board) if cell == self.opponent]

        if not player_pos: return self.config['win_bonus']
        if not opp_pos: return -self.config['win_bonus']

        score = 0
        
        # نقاط الخروج والتقدم
        score += (7 - len(player_pos)) * self.config['piece_off']
        score -= (7 - len(opp_pos)) * self.config['piece_off']

        for pos in player_pos:
            mult = self.config['zone_multiplier'] if pos >= 20 else 1.0
            score += (pos + 1) * self.config['progress_base'] * mult

            # الخانات الخاصة والتكتيك
            if pos == HOUSE_OF_HAPPINESS: score += self.config['happiness_bonus']
            elif pos == HOUSE_WATER: score += self.config['water_penalty']
            
            # الدفاع (وجود قطع بجانب بعضها)
            if (pos > 0 and board[pos-1] == self.player) or (pos < BOARD_SIZE-1 and board[pos+1] == self.player):
                score += self.config['protection']
                
            if pos + 1 < BOARD_SIZE and board[pos + 1] == self.opponent:
                score -= 40

        if valid_moves:
            score += len(valid_moves) * self.config['flexibility']
        
        return score

    def evaluate_move_priority(self, move):
        from_pos, to_pos = move
        if to_pos == OFF_BOARD: return 1000
        return 0