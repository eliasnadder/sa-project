"""
Module for converting Senet board state to/from a persistence vector.
Enhanced for Expectiminimax algorithm - NO deep copying, pure vector operations.
"""

from board import OFF_BOARD, HOUSE_WATER, HOUSE_REBIRTH, HOUSE_THREE_TRUTHS, HOUSE_RE_ATUM, HOUSE_HORUS
from rules import get_valid_moves


class GameState:
    """
    Immutable game state using ONLY persistence vector.
    No board copying - everything is done through numerical vectors.
    """

    def __init__(self, vector, current_player):
        """
        Args:
            vector (tuple/list): 30 integers representing board state
                1 = 'X', -1 = 'O', 0 = Empty
            current_player (int): 1 for 'X', -1 for 'O'
        """
        # Store as immutable tuple for hashing
        if isinstance(vector, list):
            self._vector = tuple(vector)
        else:
            self._vector = vector

        self._current_player = current_player

        # Cache for hash
        self._hash = None

        # Cache for board reconstruction (only when needed)
        self._board_cache = None

    @classmethod
    def from_board(cls, board, current_player_symbol):
        """
        Create GameState from board list.

        Args:
            board (list): Board with None, 'X', 'O'
            current_player_symbol (str): 'X' or 'O'

        Returns:
            GameState: New state instance
        """
        vector = []
        for cell in board:
            if cell == 'X':
                vector.append(1)
            elif cell == 'O':
                vector.append(-1)
            else:
                vector.append(0)

        player_int = 1 if current_player_symbol == 'X' else -1

        return cls(tuple(vector), player_int)

    def get_vector(self):
        """Returns the immutable state vector."""
        return self._vector

    def get_current_player(self):
        """Returns current player as integer (1 or -1)."""
        return self._current_player

    def get_current_player_symbol(self):
        """Returns current player as symbol ('X' or 'O')."""
        return 'X' if self._current_player == 1 else 'O'

    def get_opponent_player(self):
        """Returns opponent player as integer."""
        return -self._current_player

    def get_opponent_symbol(self):
        """Returns opponent symbol."""
        return 'O' if self._current_player == 1 else 'X'

    def get_board(self):
        """
        Reconstruct board list from vector (cached).
        Only used when interacting with existing game logic.
        """
        if self._board_cache is None:
            board = []
            for val in self._vector:
                if val == 1:
                    board.append('X')
                elif val == -1:
                    board.append('O')
                else:
                    board.append(None)
            self._board_cache = board

        return self._board_cache

    def get_piece_positions(self, player=None):
        """
        Get positions of pieces directly from vector.

        Args:
            player (int/str): 1/'X' or -1/'O'. If None, uses current player.

        Returns:
            list[int]: Indices where pieces are located
        """
        if player is None:
            target_value = self._current_player
        elif isinstance(player, str):
            target_value = 1 if player == 'X' else -1
        else:
            target_value = player

        return [i for i, val in enumerate(self._vector) if val == target_value]

    def count_pieces(self, player=None):
        """
        Count pieces directly from vector.

        Args:
            player (int/str): Which player to count

        Returns:
            int: Number of pieces on board
        """
        if player is None:
            target = self._current_player
        elif isinstance(player, str):
            target = 1 if player == 'X' else -1
        else:
            target = player

        return sum(1 for val in self._vector if val == target)

    def get_pieces_off_board(self, player=None):
        """Calculate pieces that have been borne off."""
        initial_pieces = 7
        pieces_on_board = self.count_pieces(player)
        return initial_pieces - pieces_on_board

    def apply_move(self, from_pos, to_pos):
        """
        Apply move and return NEW GameState (pure function).
        Works directly on vector - NO board reconstruction needed.

        Args:
            from_pos (int): Starting position (0-29)
            to_pos (int): Target position (0-29 or OFF_BOARD=30)

        Returns:
            GameState: New state after move
        """

        # Convert tuple to list for modification
        new_vector = list(self._vector)

        piece = new_vector[from_pos]
        new_vector[from_pos] = 0  # Clear starting position

        # Handle bearing off
        if to_pos == OFF_BOARD:
            # Piece removed from board
            pass
        else:
            # Handle attack/swap
            if new_vector[to_pos] != 0:
                # Swap pieces
                opponent_piece = new_vector[to_pos]
                new_vector[from_pos] = opponent_piece

            # Place piece
            new_vector[to_pos] = piece

            # Handle House of Water
            if to_pos == HOUSE_WATER:
                new_vector = self._send_to_rebirth_vector(
                    new_vector, piece, to_pos)

            # Handle exit house failures
            special_houses = [HOUSE_THREE_TRUTHS, HOUSE_RE_ATUM, HOUSE_HORUS]

            for house_idx in special_houses:
                if new_vector[house_idx] == piece and house_idx != to_pos:
                    new_vector = self._send_to_rebirth_vector(
                        new_vector, piece, house_idx)

        # Next player (simplified - same player for now)
        next_player = -self._current_player

        return GameState(tuple(new_vector), next_player)

    def _send_to_rebirth_vector(self, vector, piece, from_pos):
        """
        Send piece to rebirth - pure vector operation.

        Args:
            vector (list): Current vector
            piece (int): Piece value (1 or -1)
            from_pos (int): Position to clear

        Returns:
            list: Modified vector
        """
        vector[from_pos] = 0  # Remove from current position

        # Find rebirth position
        rebirth_pos = HOUSE_REBIRTH
        while rebirth_pos >= 0 and vector[rebirth_pos] != 0:
            rebirth_pos -= 1

        if rebirth_pos >= 0:
            vector[rebirth_pos] = piece

        return vector

    def get_valid_moves(self, roll):
        """
        Get valid moves - requires board reconstruction.
        This is the ONLY place we need the board list.
        """
        board = self.get_board()
        player_symbol = self.get_current_player_symbol()
        return get_valid_moves(board, player_symbol, roll)

    def is_terminal(self):
        """Check if game is over - pure vector operation."""
        # Game over if either player has no pieces
        has_x = any(val == 1 for val in self._vector)
        has_o = any(val == -1 for val in self._vector)
        return not has_x or not has_o

    def get_winner(self):
        """
        Get winner if game is terminal.

        Returns:
            int: 1 for X wins, -1 for O wins, 0 for no winner yet
        """
        has_x = any(val == 1 for val in self._vector)
        has_o = any(val == -1 for val in self._vector)

        if not has_x:
            return 1  # X won (all pieces off)
        elif not has_o:
            return -1  # O won
        else:
            return 0  # Game not over

    def get_game_phase(self):
        """
        Determine game phase from vector statistics.

        Returns:
            str: 'opening', 'midgame', 'endgame'
        """
        # Find all occupied positions
        positions = [i for i, val in enumerate(self._vector) if val != 0]

        if not positions:
            return 'endgame'

        max_pos = max(positions)
        avg_pos = sum(positions) / len(positions)

        if max_pos < 15:
            return 'opening'
        elif avg_pos < 20:
            return 'midgame'
        else:
            return 'endgame'

    def get_flattened_vector(self):
        """
        Get complete state as flat array for neural networks.

        Returns:
            list[int]: [30 board positions, current_player, pieces_off_x, pieces_off_o]
        """
        return list(self._vector) + [
            self._current_player,
            self.get_pieces_off_board(1),   # X pieces off
            self.get_pieces_off_board(-1)   # O pieces off
        ]

    def __hash__(self):
        """Enable state as dictionary key - FAST hashing."""
        if self._hash is None:
            self._hash = hash((self._vector, self._current_player))
        return self._hash

    def __eq__(self, other):
        """Fast equality check using vectors."""
        if not isinstance(other, GameState):
            return False
        return (self._vector == other._vector and
                self._current_player == other._current_player)

    def __repr__(self):
        """Debug representation."""
        player_symbol = self.get_current_player_symbol()
        pieces_x = self.count_pieces(1)
        pieces_o = self.count_pieces(-1)
        return (f"GameState(player={player_symbol}, "
                f"X={pieces_x}, O={pieces_o}, "
                f"phase={self.get_game_phase()})")


# ============================================================================
# Utility Functions
# ============================================================================

def create_state_from_game(game):
    """
    Create GameState from SenetGame instance.

    Args:
        game (SenetGame): Active game

    Returns:
        GameState: Immutable state
    """
    return GameState.from_board(game.board, game.current_player)

def get_persistence_vector(board, current_player=None):
    """
    Legacy function - returns dict format.

    Args:
        board (list): Game board
        current_player (str): Current player symbol

    Returns:
        dict: State information
    """
    state = GameState.from_board(board, current_player or 'X')
    vec = state.get_flattened_vector()

    return {
        'board_vector': vec[:30],
        'current_player': vec[30],
        'pieces_off_x': vec[31],
        'pieces_off_o': vec[32]
    }

def get_board_from_vector(vector):
    """
    Reconstruct board from vector.

    Args:
        vector (list[int]): 30 integers

    Returns:
        list: Board with None, 'X', 'O'
    """
    board = []
    for val in vector:
        if val == 1:
            board.append('X')
        elif val == -1:
            board.append('O')
        else:
            board.append(None)
    return board


def get_flattened_vector(board, current_player=None):
    """
    Legacy function - returns flat vector.

    Returns:
        list[int]: Flattened state
    """
    state = GameState.from_board(board, current_player or 'X')
    return state.get_flattened_vector()
