from engines.board import (
    HOUSE_OF_HAPPINESS, HOUSE_WATER, HOUSE_THREE_TRUTHS,
    HOUSE_RE_ATUM, HOUSE_HORUS, HOUSE_REBIRTH, BOARD_SIZE, OFF_BOARD
)

# هذه هي الأوزان التي سيتم تدريبها
SENET_AI_CONFIG = {
    'piece_off': 1200,
    'progress': 85,
    'happiness': 100,
    'water': -200,
    'special_house': 60,
    'protection': 40,
    'block': 80,
    'attack': 60,
    'flexibility': 3,
    'isolated_penalty': 15
}

class Evaluation:
    def __init__(self, player, config=None):
        self.player = player
        self.opponent = 'O' if player == 'X' else 'X'
        self.base_weights = config.copy() if config else SENET_AI_CONFIG.copy()
        self.weights = self.base_weights.copy()

    # =====================================================

    def evaluate_board(self, board, valid_moves=None):
        self.weights = self.base_weights.copy()

        if self._is_terminal(board):
            return self._evaluate_terminal(board)

        phase = self._get_game_phase(board)
        self._adjust_weights_for_phase(phase)

        score = 0
        score += self._evaluate_pieces_off(board)
        score += self._evaluate_progress(board)
        score += self._evaluate_special_houses(board)
        score += self._evaluate_water_danger(board)
        score += self._evaluate_protection_block(board)
        score += self._evaluate_attack(board)
        score += self._evaluate_isolated_pieces(board)

        if valid_moves:
            score += len(valid_moves) * self.weights['flexibility']

        return score

    # =====================================================

    def _is_terminal(self, board):
        return not any(c == self.player for c in board) or \
            not any(c == self.opponent for c in board)

    def _evaluate_terminal(self, board):
        if not any(c == self.player for c in board):
            return -10000
        if not any(c == self.opponent for c in board):
            return 10000
        return 0

    # =====================================================

    def _get_game_phase(self, board):
        positions = [i for i, c in enumerate(board) if c]
        if not positions:
            return 'endgame'
        max_pos = max(positions)
        if max_pos < 15:
            return 'opening'
        elif max_pos < 25:
            return 'midgame'
        return 'endgame'

    def _adjust_weights_for_phase(self, phase):
        if phase == 'opening':
            self.weights['progress'] *= 0.1
            self.weights['protection'] *= 0.6
            self.weights['block'] *= 0.7

        elif phase == 'midgame':
            self.weights['attack'] *= 0.7

        else:  # endgame
            self.weights['piece_off'] *= 1.3
            self.weights['progress'] *= 0.2
            self.weights['block'] *= 0.3

    # =====================================================

    def _evaluate_pieces_off(self, board):
        p_on = sum(1 for c in board if c == self.player)
        o_on = sum(1 for c in board if c == self.opponent)
        return (7 - p_on - (7 - o_on)) * self.weights['piece_off']

    def _evaluate_progress(self, board):
        score = 0
        for i, c in enumerate(board):
            if c == self.player:
                score += (i + 1)
            elif c == self.opponent:
                score -= (i + 1)
        return score * self.weights['progress']

    def _evaluate_special_houses(self, board):
        score = 0
        if board[HOUSE_OF_HAPPINESS] == self.player:
            score += self.weights['happiness']

        for h in [HOUSE_THREE_TRUTHS, HOUSE_RE_ATUM, HOUSE_HORUS]:
            if board[h] == self.player:
                score += self.weights['special_house']

        if board[HOUSE_REBIRTH] == self.player:
            score -= 100

        return score

    def _evaluate_water_danger(self, board):
        score = 0
        if board[HOUSE_WATER] == self.player:
            score += self.weights['water'] * 2
        if board[HOUSE_WATER - 1] == self.player:
            score += self.weights['water']
        return score

    def _evaluate_protection_block(self, board):
        score = 0
        for i in range(BOARD_SIZE - 1):
            if board[i] == board[i + 1] == self.player:
                score += self.weights['protection']
            if board[i] == board[i + 1] == self.opponent:
                score -= self.weights['protection']

        for i in range(BOARD_SIZE - 2):
            if board[i] == board[i+1] == board[i+2] == self.player:
                score += self.weights['block']
        return score

    def _evaluate_attack(self, board):
        score = 0
        for i, c in enumerate(board):
            if c == self.player:
                t = i + 1
                if t < BOARD_SIZE and board[t] == self.opponent:
                    if not self._is_protected(board, t):
                        score += self.weights['attack']
        return score

    def _is_protected(self, board, pos):
        if pos > 0 and board[pos - 1] == board[pos]:
            return True
        if pos < BOARD_SIZE - 1 and board[pos + 1] == board[pos]:
            return True
        return False

    def _evaluate_isolated_pieces(self, board):
        score = 0
        for i, c in enumerate(board):
            if c == self.player:
                left = i > 0 and board[i-1] == self.player
                right = i < BOARD_SIZE - 1 and board[i+1] == self.player
                if not left and not right:
                    score -= self.weights['isolated_penalty']
        return score

    # =====================================================

    def evaluate_move_priority(self, move):
        _, to_pos = move
        if to_pos == OFF_BOARD:
            return 1000
        return 0
