import numpy as np

class OmokGame:
    # initializes Omok game board
    def __init__(self, size=19):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.current_player = 1
        self.last_move = None
        self.winner = None
        self.directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        self.move_history = []

    # places stone for current player
    def make_move(self, row, col):
        if self.board[row][col] != 0:
            return False
        self.board[row][col] = self.current_player
        # updates last_move and appends to move_history
        self.last_move = (row, col)
        self.move_history.append((row, col))
        if self.check_win(row, col):
            self.winner = self.current_player
        # switches to next player
        self.current_player = 3 - self.current_player
        return True

    # checks all 4 directions for line of 5 or more
    def check_win(self, row, col):
        player = self.board[row][col]
        for dr, dc in self.directions:
            count = 1
            for i in range(1, 5):
                r, c = row + dr*i, col + dc*i
                if 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                    count += 1
                else:
                    break
            for i in range(1, 5):
                r, c = row - dr*i, col - dc*i
                if 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                    count += 1
                else:
                    break
            if count >= 5:
                return True
        return False

    def is_terminal(self):
        return self.winner is not None or np.all(self.board != 0)
