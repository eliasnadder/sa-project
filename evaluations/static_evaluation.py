from engines.board import (
    HOUSE_OF_HAPPINESS, HOUSE_WATER, HOUSE_THREE_TRUTHS,
    HOUSE_RE_ATUM, HOUSE_HORUS, HOUSE_REBIRTH, BOARD_SIZE, OFF_BOARD
)


class Evaluation:

    def __init__(self, player):

        self.player = player
        self.opponent = 'O' if player == 'X' else 'X'

        self.weights = {
            'piece_off': 1200,
            'progress': 85,
            'happiness': 100,
            'water': -200,
            'special_house': 60,
            'protection': 40,
            'block': 80,
            'attack': 60,
            'flexibility': 3
        }

        self.default_weights = self.weights.copy()

    def evaluate_board(self, board, valid_moves=None):
        self.weights = self.default_weights.copy()

        if self._is_terminal(board):
            return self._evaluate_terminal(board)

        game = self._get_game_phase(board)
        self._adjust_weights_for_phase(game)

        total_score = 0

        total_score += self._evaluate_pieces_off(board)
        total_score += self._evaluate_progress(board)
        total_score += self._evaluate_special_houses(board)
        total_score += self._evaluate_water_danger(board)
        total_score += self._evaluate_protection_block(board)
        total_score += self._evaluate_attack(board)
        total_score += self._evaluate_isolated_pieces(board)

        if valid_moves:
            total_score += self._evaluate_flexibility(valid_moves)

        return total_score

    def _evaluate_flexibility(self, valid_moves):
        if not valid_moves:
            return -100 * self.weights['flexibility']
        return len(valid_moves) * self.weights['flexibility']
# _______________________________________________

    def _is_terminal(self, board):
        has_player = any(cell == self.player for cell in board)
        has_opp = any(cell == self.opponent for cell in board)
        return not has_player or not has_opp

    def _evaluate_terminal(self, board):
        has_player = any(cell == self.player for cell in board)
        has_opp = any(cell == self.opponent for cell in board)

        if not has_player:
            return -10000
        elif not has_opp:
            return 10000
        return 0
# _________________________________________

    def _get_game_phase(self, board):

        player_pos = [i for i, cell in enumerate(board) if cell == self.player]
        opp_pos = [i for i, cell in enumerate(board) if cell == self.opponent]

        if not player_pos or not opp_pos:
            return 'endgame'

        max_pos = max(player_pos + opp_pos)

        if max_pos < 15:
            return 'opening'
        elif max_pos < 25:
            return 'midgame'
        else:
            return 'endgame'

    def _adjust_weights_for_phase(self, phase):

        if phase == 'opening':
            self.weights['protection'] = 25
            self.weights['block'] = 60
            self.weights['progress'] = 5

        elif phase == 'midgame':
            self.weights['protection'] = 20
            self.weights['block'] = 40
            self.weights['progress'] = 10
            self.weights['attack'] = 35

        else:
            self.weights['piece_off'] = 1500
            self.weights['progress'] = 15
            self.weights['protection'] = 10
            self.weights['block'] = 10
# ___________________________________________________

    def _evaluate_pieces_off(self, board):

        player_pieces_on = sum(1 for cell in board if cell == self.player)
        opp_pieces_on = sum(1 for cell in board if cell == self.opponent)

        player_pieces_off = 7 - player_pieces_on
        opp_pieces_off = 7 - opp_pieces_on

        return (player_pieces_off - opp_pieces_off) * self.weights['piece_off']

    def _evaluate_progress(self, board):

        player_score = 0
        opp_score = 0

        for i, cell in enumerate(board):
            if cell == self.player:
                player_score += (i + 1)
            elif cell == self.opponent:
                opp_score += (i + 1)

        return (player_score - opp_score) * self.weights['progress']

    def _evaluate_special_houses(self, board):

        score = 0

        if board[HOUSE_OF_HAPPINESS] == self.player:
            score += self.weights['happiness']

        elif board[HOUSE_WATER] == self.opponent:
            score += abs(self.weights['water'])

        elif board[HOUSE_REBIRTH] == self.player:
            score -= 100

        special_houses = [HOUSE_THREE_TRUTHS, HOUSE_RE_ATUM, HOUSE_HORUS]
        for house in special_houses:
            if board[house] == self.player:
                score += self.weights['special_house']

        return score

    def _evaluate_water_danger(self, board):
        score = 0
        player_pos = [i for i, cell in enumerate(board) if cell == self.player]

        if board[HOUSE_WATER] == self.player:
            score += self.weights['water'] * 2

        water_neighborns = [HOUSE_WATER - 1]
        for pos in player_pos:
            if pos in water_neighborns:
                danger = self.weights['water'] * 2
                score += danger

        return score

# ______________________________________

    def _evaluate_protection_block(self, board):
        score = 0

        for i in range(BOARD_SIZE - 1):
            if board[i] == self.player and board[i + 1] == self.player:
                score += self.weights['protection'] * 2

            if board[i] == self.opponent and board[i + 1] == self.opponent:
                score -= self.weights['protection']

        for i in range(BOARD_SIZE - 2):
            if (board[i] == self.player and
                board[i + 1] == self.player and
                    board[i + 2] == self.player):
                score += self.weights['block'] * 2

        return score

    def _evaluate_attack(self, board):
        score = 0

        for i, cell in enumerate(board):
            if cell == self.player:
                target = i + 1
                if target < BOARD_SIZE and board[target] == self.opponent:
                    if not self._is_protected(board, target):
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

        for i, cell in enumerate(board):
            if cell == self.player:
                left = i > 0 and board[i - 1] == self.player
                right = i < BOARD_SIZE - 1 and board[i + 1] == self.player
                if not left and not right:
                    score -= 15

        return score

# ______________________________________

    def evaluate_move(self, board, move, roll):

        from_pos, to_pos = move

        score = 0

        if to_pos == OFF_BOARD:
            score += self.weights['piece_off']

        else:
            if to_pos == HOUSE_OF_HAPPINESS - 1:
                score += 70

            elif from_pos == HOUSE_OF_HAPPINESS and roll in [2, 3]:
                score += 20

            elif from_pos == HOUSE_OF_HAPPINESS and roll == 1:
                score += -50

            elif from_pos == HOUSE_THREE_TRUTHS and roll == 3:
                score += 300
            elif from_pos == HOUSE_THREE_TRUTHS and roll == 3 and to_pos != OFF_BOARD:
                score -= 150

            elif from_pos == HOUSE_RE_ATUM and roll == 2:
                score += 200
            elif from_pos == HOUSE_RE_ATUM and roll == 2 and to_pos != OFF_BOARD:
                score -= 150

            elif from_pos == HOUSE_OF_HAPPINESS and roll == 4:
                score += 90
            elif from_pos == HOUSE_HORUS and roll in [1, 2, 3, 4, 5] and to_pos != OFF_BOARD:
                score -= 200

            elif from_pos == HOUSE_OF_HAPPINESS and roll == 5:
                score += 100

        if to_pos < BOARD_SIZE and board[to_pos] == self.opponent:
            if not self._is_protected(board, to_pos):
                score += self.weights['attack']

        return score
