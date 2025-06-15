import time
from copy import deepcopy
from collections import defaultdict
from game import OmokGame  # if you use it inside

class OmokAI:
    # sets the AI player, time limit for moves and initializes helper structures
    def __init__(self, player, time_limit=10):
        self.player = player
        self.time_limit = time_limit
        self.heuristic_cache = {}
        self.transposition_table = {}
        self.killer_moves = defaultdict(list)
        self.initialize_opening_book()

    # sets initial known good moves for early-game positions
    def initialize_opening_book(self):
        self.opening_book = {
            tuple(): [(9, 9)],
        }

    # looks up current move history in the opening book
    def get_opening_move(self, game):
        key = tuple(sorted(game.move_history))
        return self.opening_book.get(key, None)

    # runs iterative deepening using alpha-beta pruning
    def iterative_deepening_search(self, game):
        start_time = time.time()
        best_move = None
        depth = 1

        # check opening book
        opening_move = self.get_opening_move(game)
        if opening_move:
            return opening_move[0]

        # urgent block/win check
        for move in self.get_possible_moves(game):
            temp = deepcopy(game)
            temp.make_move(*move)
            if temp.check_win(*move):
                return move

        while time.time() - start_time < self.time_limit:
            try:
                move, _ = self.alpha_beta_search(game, depth, start_time)
                if move:
                    best_move = move
                depth += 1
            except TimeoutError:
                break
        return best_move

    # recursive function for alpha-beta search
    def alpha_beta_search(self, game, depth, start_time):
        def recurse(state, depth, alpha, beta, maximizing, last_move, ply):
            alpha_orig = alpha
            # transposition table lookup - avoid re-searching previously seen positions
            key = tuple(map(tuple, state.board))
            if key in self.transposition_table:
                entry = self.transposition_table[key]
                if entry['depth'] >= depth:
                    # precise value for this position
                    if entry['flag'] == 'EXACT':
                        return entry['move'], entry['value']
                    # value at least this good - alpha
                    elif entry['flag'] == 'LOWER':
                        alpha = max(alpha, entry['value'])
                    # value at most this good - beta
                    elif entry['flag'] == 'UPPER':
                        beta = min(beta, entry['value'])
                    if alpha >= beta:
                        return entry['move'], entry['value']

            # ensures AI doesn't exceed time limit
            if time.time() - start_time > self.time_limit:
                raise TimeoutError()

            if depth == 0 or state.is_terminal():
                return None, self.evaluate(state)

            moves = self.get_possible_moves(state)
            if not moves:
                return None, self.evaluate(state)

            moves = self.order_moves(state, moves, maximizing, ply)
            best_move = moves[0]

            # maximizing player (AI)
            if maximizing:
                value = -float('inf')
                for move in moves:
                    new_state = deepcopy(state)
                    new_state.make_move(*move)
                    _, new_val = recurse(new_state, depth - 1, alpha, beta, False, move, ply + 1)
                    if new_val > value:
                        value = new_val
                        best_move = move
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        if move not in self.killer_moves[ply]:
                            self.killer_moves[ply].append(move)
                        break
                    
            # minimizing player (player 1)
            else:
                value = float('inf')
                for move in moves:
                    new_state = deepcopy(state)
                    new_state.make_move(*move)
                    _, new_val = recurse(new_state, depth - 1, alpha, beta, True, move, ply + 1)
                    if new_val < value:
                        value = new_val
                        best_move = move
                    beta = min(beta, value)
                    if alpha >= beta:
                        if move not in self.killer_moves[ply]:
                            self.killer_moves[ply].append(move)
                        break

            flag = 'EXACT'
            if value <= alpha_orig:
                flag = 'UPPER'
            elif value >= beta:
                flag = 'LOWER'
            self.transposition_table[key] = {
                'value': value,
                'move': best_move,
                'depth': depth,
                'flag': flag
            }
            return best_move, value

        return recurse(deepcopy(game), depth, -float('inf'), float('inf'), self.player == game.current_player, None, 0)

    # generates list of empty positions near existing stones
    def get_possible_moves(self, game):
        if not game.move_history:
            return [(game.size // 2, game.size // 2)]

        moves = set()
        for (r, c) in game.move_history:
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < game.size and 0 <= nc < game.size and game.board[nr][nc] == 0:
                        moves.add((nr, nc))
        return list(moves)

    # returns numeric score for all lines and patterns, and adds positive/negative score of pattern benefits the AI or player
    def evaluate(self, game):
        board = game.board
        if tuple(map(tuple, board)) in self.heuristic_cache:
            return self.heuristic_cache[tuple(map(tuple, board))]

        patterns = {
            (5, 0): 1000000,
            (4, 2): 100000,
            (4, 1): 50000,
            (3, 2): 10000,
            (3, 1): 2000,
            (2, 2): 1000,
            (2, 1): 100,
            (1, 2): 50,
            (1, 1): 10
        }

        score = 0
        center = game.size // 2
        for i in range(game.size):
            for j in range(game.size):
                if board[i][j] != 0:
                    player = board[i][j]
                    for dr, dc in game.directions:
                        length = 1
                        open_ends = 0
                        blocked = False

                        r, c = i + dr, j + dc
                        while 0 <= r < game.size and 0 <= c < game.size and board[r][c] == player:
                            length += 1
                            r += dr
                            c += dc
                        if 0 <= r < game.size and 0 <= c < game.size and board[r][c] == 0:
                            open_ends += 1

                        r, c = i - dr, j - dc
                        while 0 <= r < game.size and 0 <= c < game.size and board[r][c] == player:
                            length += 1
                            r -= dr
                            c -= dc
                        if 0 <= r < game.size and 0 <= c < game.size and board[r][c] == 0:
                            open_ends += 1

                        for (l, o), val in patterns.items():
                            if length >= l and open_ends >= o:
                                score += val if player == self.player else -val
                                break

        # uses heuristic_cache for speed
        self.heuristic_cache[tuple(map(tuple, board))] = score
        return score

    # looks for chain length and number of open ends
    def evaluate_move(self, game, row, col, player):
        score = 0
        center = game.size // 2
        dist = max(abs(row - center), abs(col - center))
        score += (game.size - dist)

        for dr, dc in game.directions:
            count = 1
            open_ends = 0

            for i in range(1, 5):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < game.size and 0 <= c < game.size:
                    if game.board[r][c] == player:
                        count += 1
                    elif game.board[r][c] == 0:
                        open_ends += 1
                        break
                    else:
                        break

            for i in range(1, 5):
                r, c = row - dr * i, col - dc * i
                if 0 <= r < game.size and 0 <= c < game.size:
                    if game.board[r][c] == player:
                        count += 1
                    elif game.board[r][c] == 0:
                        open_ends += 1
                        break
                    else:
                        break

            # quickly scores potential move
            if count >= 5:
                score += 1000000
            elif count == 4 and open_ends >= 1:
                score += 50000
            elif count == 3 and open_ends == 2:
                score += 10000
            else:
                score += count ** 2 * (open_ends + 1)

        return score

    # sorts moves by heuristic score - to improve alpha-beta efficiency
    def order_moves(self, game, moves, maximizing_player, ply):
        player = self.player if maximizing_player else 3 - self.player
        scored = []
        for move in moves:
            score = self.evaluate_move(game, move[0], move[1], player)
            # adds bonus to killer moves
            if move in self.killer_moves.get(ply, []):
                score += 10000
            scored.append((score, move))
        scored.sort(reverse=True)
        return [m for s, m in scored]