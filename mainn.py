import tkinter as tk
from tkinter import messagebox
from game import SenetGame
from player import PlayerType
from board import BOARD_SIZE

CELL_SIZE = 60

SPECIAL_CELLS = {
    14: "#f4e19c",  # بيت البعث
    25: "#9fe6a0",  # بيت السعادة
    26: "#87ceeb",  # بيت الماء
    27: "#f7b267",
    28: "#f7b267",
    29: "#f7b267"
}

class SenetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Senet - Antique Wood Style")
        self.root.geometry(f"{CELL_SIZE*10}x650")
        self.root.configure(bg="#8b5a2b")

        self.current_player = PlayerType.PLAYER
        self.opponent = PlayerType.OPPONENT
        self.game = SenetGame(current_player=self.current_player, opponent=self.opponent)

        self.message_box = tk.Text(root, height=5, width=70, state="disabled", bg="#f5deb3")
        self.message_box.pack(pady=10)

        self.roll_button = tk.Button(
            root, text="Throw Sticks", command=self.throw_sticks,
            state="disabled", bg="#deb887", font=("Arial", 12, "bold")
        )
        self.roll_button.pack(pady=5)

        self.canvas = tk.Canvas(
            root,
            width=CELL_SIZE*10,
            height=CELL_SIZE*3,
            bg="#c19a6b",
            highlightthickness=0
        )
        self.canvas.pack(pady=10)

        self.cells = []
        self.valid_moves = {}
        self.highlighted = []

        self.create_board()

        self.btn_frame = tk.Frame(root, bg="#8b5a2b")
        self.btn_frame.pack(pady=10)

        tk.Label(
            self.btn_frame,
            text="Choose Game Type:",
            font=("Arial", 12),
            bg="#8b5a2b",
            fg="white"
        ).pack(side="left", padx=5)

        tk.Button(self.btn_frame, text="Human vs Human", command=self.start_hvh, bg="#deb887").pack(side="left", padx=5)
        tk.Button(self.btn_frame, text="Human vs AI", command=self.start_hvai, bg="#deb887").pack(side="left", padx=5)

    def create_board(self):
        self.cells = []
        self.canvas.delete("all")

        # إطار خشبي
        self.canvas.create_rectangle(
            5, 5,
            CELL_SIZE*10 - 5,
            CELL_SIZE*3 - 5,
            outline="#5a3e1b",
            width=8
        )

        wood_colors = ["#deb887", "#d2b48c"]

        for i in range(BOARD_SIZE):
            row = i // 10
            col = i % 10
            x1, y1 = col * CELL_SIZE, row * CELL_SIZE
            x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE

            color = SPECIAL_CELLS.get(i, wood_colors[(row + col) % 2])

            rect = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline="#8b5a2b",
                width=2
            )

            self.cells.append(rect)

        self.update_board()

    def update_board(self):
        self.canvas.delete("piece")

        for i in range(BOARD_SIZE):
            cell_value = self.game.board[i]
            row = i // 10
            col = i % 10

            cx = col * CELL_SIZE + CELL_SIZE // 2
            cy = row * CELL_SIZE + CELL_SIZE // 2
            r = 20

            if cell_value == PlayerType.PLAYER:
                self.canvas.create_oval(
                    cx-r, cy-r, cx+r, cy+r,
                    fill="#1e90ff", outline="black", width=2, tags="piece"
                )
            elif cell_value == PlayerType.OPPONENT:
                self.canvas.create_oval(
                    cx-r, cy-r, cx+r, cy+r,
                    fill="#b22222", outline="black", width=2, tags="piece"
                )

    def start_hvh(self):
        self.show_message("Starting Human vs Human...")
        self.roll_button.config(state="normal")
        self.update_board()

    def start_hvai(self):
        self.show_message("Human vs AI is not implemented yet. Defaulting to Human vs Human.")
        self.start_hvh()

    def throw_sticks(self):
        roll = self.game.roll_sticks()
        self.show_message(f"{self.game.current_player} rolled: {roll}")

        self.valid_moves = self.game.get_valid_moves_for_gui(roll)

        if not self.valid_moves:
            self.show_message("No valid moves, turn passes.")
            self.game.next_turn()
            self.update_board()
        else:
            self.show_message("Click on a highlighted square.")
            self.highlight_valid_moves()
            self.canvas.bind("<Button-1>", self.select_piece)

    def highlight_valid_moves(self):
        self.clear_highlights()

        for from_pos, to_list in self.valid_moves.items():
            for to_pos in to_list:
                row = to_pos // 10
                col = to_pos % 10

                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline="green",
                    width=4,
                    tags="highlight"
                )
                self.highlighted.append(rect)

    def clear_highlights(self):
        self.canvas.delete("highlight")

    def select_piece(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        index = row * 10 + col

        for from_pos, to_list in self.valid_moves.items():
            if index in to_list:
                self.game.apply_gui_move(from_pos, index)
                self.show_message(f"Moved from {from_pos+1} to {index+1}")
                self.clear_highlights()
                self.canvas.unbind("<Button-1>")
                self.game.next_turn()
                self.update_board()
                return

    def show_message(self, msg):
        self.message_box.config(state="normal")
        self.message_box.insert(tk.END, msg + "\n")
        self.message_box.config(state="disabled")
        self.message_box.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    gui = SenetGUI(root)
    root.mainloop()
