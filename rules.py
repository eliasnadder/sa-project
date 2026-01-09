"""Senet game rules - valid moves, blockades, protection, special houses."""

from board import (
    HOUSE_OF_HAPPINESS, HOUSE_WATER, HOUSE_REBIRTH,
    HOUSE_THREE_TRUTHS, HOUSE_RE_ATUM, HOUSE_HORUS,
    BOARD_SIZE, OFF_BOARD, print_message
)


def get_valid_moves(board, player, roll):
    """
    Determines all legal moves for the current player given a roll.
    Implements constraints like Blockades, Protection, and Special Houses.
    """
    opponent = 'O' if player == 'X' else 'X'
    valid_moves = []

    # Find all pieces for the current player
    piece_indices = [i for i, x in enumerate(board) if x == player]

    for start_pos in piece_indices:
        target_pos = start_pos + roll

        # --- RULE: Bearing Off (Exiting the Board) ---
        if target_pos >= BOARD_SIZE:
            if not _can_bear_off(start_pos, roll, target_pos):
                continue
            valid_moves.append((start_pos, OFF_BOARD))
            continue

        # --- RULE: House of happiness ---
        if not _can_pass_happiness(start_pos, target_pos, roll):
            continue

        # --- RULE: Occupancy and Capturing ---
        if not _can_land_on(board, target_pos, player, opponent):
            continue

        # --- RULE: Blockades ---
        if _is_path_blocked(board, start_pos, target_pos, roll, opponent):
            continue

        # If we passed all checks, it's a valid move
        valid_moves.append((start_pos, target_pos))

    return valid_moves


def _can_bear_off(start_pos, roll, target_pos):
    """Check if a piece can bear off the board."""
    # Can only bear off if already at position 25 or beyond
    if start_pos < HOUSE_OF_HAPPINESS:
        return False

    # Special exit house rules for positions 27, 28, 29
    if start_pos == HOUSE_THREE_TRUTHS and roll != 3:
        return False  # House of Three Truths needs roll of 3
    if start_pos == HOUSE_RE_ATUM and roll != 2:
        return False  # House of Re-Atum needs roll of 2
    if start_pos == HOUSE_HORUS and roll != 1:
        return False  # House of Horus needs roll of 1

    # For other positions (25, 26), any roll that reaches 30+ is valid
    return target_pos == OFF_BOARD or (start_pos <= HOUSE_WATER and target_pos > OFF_BOARD)


def _can_pass_happiness(start_pos, target_pos, roll):
    """Check if move respects House of Happiness rules."""
    # Must land exactly on House of Happiness when passing through it
    if start_pos < HOUSE_OF_HAPPINESS and target_pos > HOUSE_OF_HAPPINESS:
        # Cannot jump over House of Happiness
        if start_pos + roll != HOUSE_OF_HAPPINESS:
            return False
    return True


def _can_land_on(board, target_pos, player, opponent):
    """Check if a piece can land on the target position."""
    target_content = board[target_pos]

    # Cannot land on own piece
    if target_content == player:
        return False

    if target_content == opponent:
        # --- RULE: Protection ---
        if _is_protected(board, target_pos, opponent):
            return False

    return True


def _is_protected(board, pos, player):
    """Check if a piece at pos is protected by adjacent friendly pieces."""
    # Check previous neighbor
    if pos > 0 and board[pos - 1] == player:
        return True
    # Check next neighbor
    if pos < BOARD_SIZE - 1 and board[pos + 1] == player:
        return True
    return False


def _is_path_blocked(board, start_pos, target_pos, roll, opponent):
    """Check if the path is blocked by a blockade (3+ consecutive opponent pieces)."""
    if roll <= 1:
        return False

    # Check squares between start and target
    for i in range(start_pos + 1, target_pos):
        if board[i] == opponent:
            # Check left neighbors
            left_count = 0
            idx = i - 1
            while idx >= 0 and board[idx] == opponent:
                left_count += 1
                idx -= 1

            # Check right neighbors
            right_count = 0
            idx = i + 1
            while idx < BOARD_SIZE and board[idx] == opponent:
                right_count += 1
                idx += 1

            # If total consecutive group >= 3
            if (left_count + 1 + right_count) >= 3:
                return True

    return False


def apply_move(board, start_pos, target_pos):
    """
    Executes the move on the board.
    Handles swapping (Attack) and House of Water.
    Returns the updated board.
    """
    piece = board[start_pos]
    board[start_pos] = None  # Remove from old spot

    # Handle Bearing Off
    if target_pos == OFF_BOARD:
        print_message(f"Player {piece} bears off a piece! 🏆", "success")
        return board

    # Handle Attack (Swap)
    if board[target_pos] is not None:
        opponent = board[target_pos]
        print_message(f"Attack! {piece} swaps with {opponent}.", "attack")
        board[start_pos] = opponent  # Opponent sent back

    # Place piece in new spot
    board[target_pos] = piece

    # --- RULE: House of Water ---
    if target_pos == HOUSE_WATER:
        board = _handle_house_of_water(board, piece, target_pos)

    return board


def _handle_house_of_water(board, piece, target_pos):
    """Handle landing on House of Water - piece goes back to rebirth."""
    print_message(f"Oh no! {piece} fell into the House of Water!", "water")
    board[target_pos] = None  # Remove from Water

    # Check House of Rebirth
    rebirth_pos = HOUSE_REBIRTH

    # If Rebirth is occupied, search backwards for first empty slot
    while rebirth_pos >= 0 and board[rebirth_pos] is not None:
        rebirth_pos -= 1

    if rebirth_pos >= 0:
        print_message(
            f"{piece} is reborn at square {rebirth_pos + 1}.", "rebirth")
        board[rebirth_pos] = piece
    else:
        # Extreme edge case fallback
        print_message(
            f"{piece} was lost in the waters (No empty squares).", "error")

    return board


def check_win(board, player):
    """Checks if the player has no pieces left on the board (won)."""
    return board.count(player) == 0
