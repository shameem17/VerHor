import sys
import tkinter
import random
from turtle import color
import verhor_game


class Square(tkinter.Canvas):

    COLOR_EMPTY = "gray"
    COLOR_FILLED_R = "red"
    COLOR_FILLED_B = "blue"

    def __init__(self, master, size=50):
        tkinter.Canvas.__init__(self, master, height=size, width=size,
                                background=Square.COLOR_EMPTY, highlightthickness=2,
                                highlightbackground="black")

    # def set_state(self, state):
    #     color = Square.COLOR_FILLED if state else Square.COLOR_EMPTY
    #     self.configure(background=color)

    def set_state(self, state, vertical_color):
        if state:
            if vertical_color:
                color = Square.COLOR_FILLED_B
            else:
                color = Square.COLOR_FILLED_R
        else:
            color = Square.COLOR_EMPTY

        self.configure(background=color)


class Board(tkinter.Frame):

    def __init__(self, master, game, rows, cols):

        tkinter.Frame.__init__(self, master)

        self.two_player = False
        self.mode = "AI"
        self.toss = False
        self.game = game
        self.vertical = True        
        self.rows = rows
        self.cols = cols
        self.moved = False

    
        self.squares = []
        for row in range(rows):
            row_squares = []
            for col in range(cols):
                square = Square(self)
                square.grid(row=row, column=col, padx=1, pady=1)
                square.bind("<Button-1>",
                            lambda event, row=row, col=col: self.perform_move_2(row, col))
                row_squares.append(square)
            self.squares.append(row_squares)

    def perform_move(self, row, col):
        if self.game.is_legal_move(row, col, self.vertical) and self.toss:
            self.game.perform_move(row, col, self.vertical)
            self.vertical = not self.vertical
            self.update_squares()
            self.master.update_status()
            self.moved = True
        else:
            self.moved = False


    def perform_move_2(self, row, col):
        if self.two_player == False:
            self.perform_move(row, col)
            if self.moved == True:
                if not self.game.game_over(self.vertical):
                    (row, col), best_value, total_leaves = \
                        self.game.get_best_move(self.vertical, 1)
                    self.perform_move(row, col)

        elif self.two_player == True:
            self.perform_move(row, col)

    def update_squares(self):
        game_board = self.game.get_board()
        for row in range(self.rows):
            for col in range(self.cols):
                self.squares[row][col].set_state(game_board[row][col], self.vertical)


class VerHorGUI(tkinter.Frame):

    def __init__(self, master, rows, cols):

        tkinter.Frame.__init__(self, master)

        self.game = verhor_game.create_verhor_game(rows, cols)
        self.rows = rows
        self.cols = cols

        self.board = Board(self, self.game, rows, cols)
        self.board.pack(side=tkinter.LEFT, padx=1, pady=1)

        menu = tkinter.Frame(self)

        self.status_label = tkinter.Label(menu, font=("Arial", 16))
        self.status_label.pack(padx=1, pady=(1, 10))
        self.update_status()

        tkinter.Label(menu, text="Press 'r' to perform a random move.").pack(
            padx=1, pady=1, anchor=tkinter.W)

        tkinter.Label(menu, text="Press 'b' to perform a best move.").pack(
            padx=1, pady=1, anchor=tkinter.W)

        tkinter.Button(menu, text="Two Player",
                       command=self.two_player_move).pack(fill=tkinter.X, padx=1, pady=1)

        tkinter.Button(menu, text="Play with AI",
                       command=self.auto_move).pack(fill=tkinter.X, padx=1, pady=1)
        
        tkinter.Button(menu, text="Reset Game",
                       command=self.reset_click).pack(fill=tkinter.X, padx=1, pady=1)

        menu.pack(side=tkinter.RIGHT)

        self.focus_set()

        self.bind("t", lambda event: self.toss_move())

        self.bind("r", lambda event: self.perform_random_move())

        self.bind("b", lambda event: self.perform_best_move())

    def toss_move(self):
        if self.board.toss == False:
            self.board.toss = True
            toss_list = ['V', 'H']
            num = random.choice(toss_list)

            if num == 'V':
                self.change_to_v()
            elif num == 'H':
                self.change_to_h()

            self.update_status()
        
        

    def change_to_v(self):
        self.board.vertical = True
        self.update_status()

    def change_to_h(self):
        self.board.vertical = False
        self.update_status()

    def update_status(self):
        if self.board.toss == False:
            self.status_label.config(text=self.board.mode + "\n" + "Toss: press 't'")

        else:
            if self.game.game_over(self.board.vertical):
                winner = "Horizontal" if self.board.vertical else "Vertical"
                self.status_label.config(text=self.board.mode + "\n" + "Winner: " + winner)
            else:
                turn = "Vertical" if self.board.vertical else "Horizontal"
                self.status_label.config(text=self.board.mode + "\n" + "Turn: " + turn)

    def reset_click(self):
        self.game.reset()
        self.board.toss = False
        self.board.update_squares()
        self.update_status()

    def auto_move(self):
        self.reset_click()
        self.board.two_player = False
        self.board.mode = "AI"
        self.update_status()
        
        
    def two_player_move(self):
        self.reset_click()
        self.board.two_player = True
        self.board.mode = "Two Player"
        self.update_status()
        

    def perform_random_move(self):
        if not self.game.game_over(self.board.vertical):
            row, col = self.game.get_random_move(self.board.vertical)
            self.board.perform_move(row, col)
        
        if self.board.two_player == False:
            if not self.game.game_over(self.board.vertical):
                (row, col), best_value, total_leaves = \
                    self.game.get_best_move(self.board.vertical, 1)
                self.board.perform_move(row, col)

    def perform_best_move(self):
        if not self.game.game_over(self.board.vertical):
            (row, col), best_value, total_leaves = \
                self.game.get_best_move(self.board.vertical, 1)
            self.board.perform_move(row, col)

        if self.board.two_player == False:
            if not self.game.game_over(self.board.vertical):
                (row, col), best_value, total_leaves = \
                    self.game.get_best_move(self.board.vertical, 1)
                self.board.perform_move(row, col)


if __name__ == "__main__":
    root = tkinter.Tk()
    root.title("VerHor Game")
    print(sys.argv[1:])
    rows, cols = sys.argv[1:]
    VerHorGUI(root, int(rows), int(cols)).pack()
    root.resizable(height=False, width=False)
    root.mainloop()
