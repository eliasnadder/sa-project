"""Senet board state and display logic with enhanced terminal output."""

# ANSI color codes


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Background colors
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_RED = "\033[41m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"


# Special house indices
HOUSE_REBIRTH = 14      # Square 15
HOUSE_OF_HAPPINESS = 25       # Square 26
HOUSE_WATER = 26        # Square 27
HOUSE_THREE_TRUTHS = 27  # Square 28
HOUSE_RE_ATUM = 28      # Square 29
HOUSE_HORUS = 29        # Square 30

BOARD_SIZE = 30
OFF_BOARD = 30


def create_initial_board():
    """
    Creates the initial board state.
    The board has 30 squares (0-29 index).
    None = Empty, 'X' = Player 1, 'O' = Player 2
    Setup: Alternating on squares 1-10 (Indices 0-9)
    """

    board = [None] * BOARD_SIZE
    for i in range(0, 14):
        if i % 2 == 0:
            board[i] = 'X'
        else:
            board[i] = 'O'
    return board


def print_title():
    """Print a fancy game title."""
    c = Colors
    title = f"""
{c.YELLOW}{c.BOLD}
    ╔═══════════════════════════════════════════════════════════╗
    ║   ███████╗███████╗███╗   ██╗███████╗████████╗             ║
    ║   ██╔════╝██╔════╝████╗  ██║██╔════╝╚══██╔══╝             ║
    ║   ███████╗█████╗  ██╔██╗ ██║█████╗     ██║                ║
    ║   ╚════██║██╔══╝  ██║╚██╗██║██╔══╝     ██║                ║
    ║   ███████║███████╗██║ ╚████║███████╗   ██║                ║
    ║   ╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝   ╚═╝                ║
    ║                 {c.CYAN}Ancient Egyptian Board Game{c.YELLOW}               ║
    ╚═══════════════════════════════════════════════════════════╝
{c.RESET}"""
    print(title)


def print_legend(player, opponent):
    """Print the board legend."""
    c = Colors
    print(f"\n{c.BOLD}  ╔══════════════════ LEGEND ═══════════════════╗{c.RESET}")
    print(f"  ║   {c.CYAN}{c.BOLD}{player}{c.RESET} = Player 1    {c.MAGENTA}{c.BOLD}{opponent}{c.RESET} = Player 2              ║")
    print(
        f"  ║  {c.GREEN}(R){c.RESET} Rebirth     {c.YELLOW}(H){c.RESET} Happiness              ║")
    print(
        f"  ║  {c.BLUE}(W){c.RESET} Water       {c.RED}(3)(2)(1){c.RESET} Exit Houses      ║")
    print(f"  {c.BOLD}╚═════════════════════════════════════════════╝{c.RESET}\n")


def _get_cell_display(val, idx):
    """Get the display string for a cell with colors."""
    c = Colors

    # Determine special house marker and color
    special = ""

    if idx == HOUSE_REBIRTH:
        special = f"{c.GREEN}R{c.RESET}"
    elif idx == HOUSE_OF_HAPPINESS:
        special = f"{c.YELLOW}H{c.RESET}"
    elif idx == HOUSE_WATER:
        special = f"{c.BLUE}W{c.RESET}"
    elif idx == HOUSE_THREE_TRUTHS:
        special = f"{c.RED}3{c.RESET}"
    elif idx == HOUSE_RE_ATUM:
        special = f"{c.RED}2{c.RESET}"
    elif idx == HOUSE_HORUS:
        special = f"{c.RED}1{c.RESET}"

    # Determine piece display
    if val == 'X':
        piece = f"{c.CYAN}{c.BOLD}X{c.RESET}"
    elif val == 'O':
        piece = f"{c.MAGENTA}{c.BOLD}O{c.RESET}"
    else:
        piece = f"{c.DIM}·{c.RESET}"

    if special:
        return f"{piece}{special}"
    return f"{piece} "


def print_board(board, current_player_symbol=None):
    """
    Prints the board in the correct Boustrophedon (S-shape) layout with colors.
    Row 1: 1 -> 10 (Indices 0-9)
    Row 2: 20 <- 11 (Indices 19-10)
    Row 3: 21 -> 30 (Indices 20-29)
    """
    c = Colors

    # حساب عدد القطع على اللوحة
    pieces_x_on_board = sum(1 for cell in board if cell == 'X')
    pieces_o_on_board = sum(1 for cell in board if cell == 'O')

    # عدد القطع المخرجة (كل لاعب يبدأ بـ 7 قطع)
    pieces_x_off = 7 - pieces_x_on_board
    pieces_o_off = 7 - pieces_o_on_board

    # تحديد لون اللاعب الحالي (إذا مررت current_player_symbol)
    current_color = c.CYAN if current_player_symbol == 'X' else c.MAGENTA if current_player_symbol == 'O' else c.WHITE

    print(
        f"\n{c.BOLD}{c.YELLOW}═══════════════════ SENET BOARD ═══════════════════{c.RESET}")

    # Row 1 Header
    header1 = "  "
    for i in range(10):
        header1 += f"{c.DIM}{i+1:^5}{c.RESET}"
    print(header1)

    # Row 1 Top border
    print(f"  {c.WHITE}╔════╦════╦════╦════╦════╦════╦════╦════╦════╦════╗{c.RESET}")

    # Row 1 Cells (0-9)
    row1 = f"  {c.WHITE}║{c.RESET}"
    for i in range(10):
        cell = _get_cell_display(board[i], i)
        row1 += f" {cell} {c.WHITE}║{c.RESET}"
    print(row1)

    # Row 1-2 separator
    print(f"  {c.WHITE}╠════╬════╬════╬════╬════╬════╬════╬════╬════╬════╣{c.RESET}")

    # Row 2 Cells (19-10) - Reversed direction
    row2 = f"  {c.WHITE}║{c.RESET}"
    for i in range(19, 9, -1):
        cell = _get_cell_display(board[i], i)
        row2 += f" {cell} {c.WHITE}║{c.RESET}"
    print(row2)

    # Row 2 Header
    header2 = "  "
    for i in range(19, 9, -1):
        header2 += f"{c.DIM}{i+1:^5}{c.RESET}"
    print(header2)

    # Row 2-3 separator
    print(f"  {c.WHITE}╠════╬════╬════╬════╬════╬════╬════╬════╬════╬════╣{c.RESET}")

    # Row 3 Cells (20-29)
    row3 = f"  {c.WHITE}║{c.RESET}"
    for i in range(20, 30):
        cell = _get_cell_display(board[i], i)
        row3 += f" {cell} {c.WHITE}║{c.RESET}"
    print(row3)

    # Row 3 Bottom border
    print(f"  {c.WHITE}╚════╩════╩════╩════╩════╩════╩════╩════╩════╩════╝{c.RESET}")

    # Row 3 Header
    header3 = "  "
    for i in range(20, 30):
        header3 += f"{c.DIM}{i+1:^5}{c.RESET}"
    print(header3)

    # ══════════ الإضافة الجديدة: إحصائيات القطع ══════════
    print(f"{c.BOLD}{c.YELLOW}═════════════════ PIECES STATUS ═════════════════{c.RESET}")
    print(f" {c.CYAN}{c.BOLD}Player X:{c.RESET} {pieces_x_on_board} pieces on board ─ {c.GREEN}{pieces_x_off} pieces off (borne off){c.RESET}")
    print(f" {c.MAGENTA}{c.BOLD}Player O:{c.RESET} {pieces_o_on_board} pieces on board ─ {c.GREEN}{pieces_o_off} pieces off (borne off){c.RESET}")

    # إذا كان اللاعب الحالي معروف، نبرز دوره
    if current_player_symbol:
        print(
            f"\n {current_color}{c.BOLD}▶ Current turn: Player {current_player_symbol}{c.RESET}")

    print(f"{c.BOLD}{c.YELLOW}════════════════════════════════════════════════════{c.RESET}\n")


def print_roll(roll):
    """Print the dice roll in a fancy way."""
    c = Colors
    print(f"\n  {c.BOLD}🎲 THROWING STICKS...{c.RESET}")
    print(f"  {c.BOLD}{c.GREEN}Roll: {roll}{c.RESET}")


def print_winner(player):
    """Print winner announcement."""
    c = Colors
    color = c.CYAN if player == 'X' else c.MAGENTA
    print(f"""
{c.BOLD}{color}
    ╔═══════════════════════════════════════════════╗
    ║                                               ║
    ║      🎉  PLAYER {player} WINS!  🎉               ║
    ║                                               ║
    ║         Congratulations, Champion!            ║
    ║                                               ║
    ╚═══════════════════════════════════════════════╝
{c.RESET}""")


def print_message(msg, msg_type="info"):
    """Print a formatted message."""
    c = Colors
    icons = {
        "info": f"{c.CYAN}ℹ{c.RESET}",
        "warning": f"{c.YELLOW}⚠{c.RESET}",
        "error": f"{c.RED}✗{c.RESET}",
        "success": f"{c.GREEN}✓{c.RESET}",
        "attack": f"{c.RED}⚔{c.RESET}",
        "water": f"{c.BLUE}🌊{c.RESET}",
        "rebirth": f"{c.GREEN}♻{c.RESET}",
    }
    icon = icons.get(msg_type, icons["info"])
    print(f"\n  {icon} {msg}")
