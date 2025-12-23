import numpy as np

# =========================
# Knucklebones Game Engine
# =========================

class KnucklebonesGame:
    def __init__(self):
        # board[player, column, row]
        # 0 = empty, 1–6 = dice
        self.board = np.zeros((2, 3, 3), dtype=int)
        self.current_player = 0
        self.done = False

    def reset(self):
        self.board[:] = 0
        self.current_player = 0
        self.done = False

    def roll_die(self):
        return np.random.randint(1, 7)

    def valid_moves(self, player):
        """Return columns that still have space"""
        return [c for c in range(3) if 0 in self.board[player, c]]

    def apply_move(self, player, column, value):
        """Place die and remove opponent dice"""
        if self.done:
            return

        # place die in first empty slot of chosen column
        col = self.board[player, column]
        row = np.where(col == 0)[0][0]
        col[row] = value

        # remove matching dice from opponent column
        opponent = 1 - player
        opp_col = self.board[opponent, column]
        opp_col[opp_col == value] = 0

        # check if this player filled their board
        if 0 not in self.board[player].flatten():
            self.done = True



    def score_player(self, player):
        """Calculate total score for a player"""
        total = 0
        for col in self.board[player]:
            for v in set(col):
                if v > 0:
                    count = np.sum(col == v)
                    total += v * count * count
        return total

    def get_winner(self):
        """Return winner: 0, 1, or None for tie"""
        s0 = self.score_player(0)
        s1 = self.score_player(1)

        if s0 > s1:
            return 0
        elif s1 > s0:
            return 1
        return None

    def print_board(self):
        """Print the boards cleanly with regular integers"""
        for p in [0, 1]:
            print(f"\nPlayer {p} board:")
            for r in range(2, -1, -1):
                # convert np.int64 to int for clean printing
                print([int(self.board[p, c, r]) for c in range(3)])
        print(
            f"\nScores -> P0: {self.score_player(0)} | "
            f"P1: {self.score_player(1)}"
        )



# =========================
# Environment Helpers
# =========================

def encode_state(game, rolled_value):
    """
    Encode the game state into a numeric vector
    Size: 18 board + 1 current player + 1 rolled die = 20
    """
    return np.concatenate([
        game.board.flatten(),
        [game.current_player],
        [rolled_value]
    ])


def compute_reward(game, player):
    """
    Sparse reward:
    +1 win
    -1 loss
    0 otherwise
    """
    if not game.done:
        return 0

    winner = game.get_winner()
    if winner == player:
        return 1
    elif winner is None:
        return 0
    else:
        return -1


# =========================
# Baseline Agent
# =========================

def random_agent(game):
    """Choose a random valid column"""
    return np.random.choice(game.valid_moves(game.current_player))


# =========================
# Simple Self-Play Test
# =========================

if __name__ == "__main__":
    game = KnucklebonesGame()
    turn = 1

    while not game.done:
        print("\n" + "=" * 30)
        print(f"TURN {turn}")
        print(f"Current Player: {game.current_player}")

        valid = game.valid_moves(game.current_player)

        if not valid:
            print("No valid moves. Skipping turn.")
            game.current_player = 1 - game.current_player
            turn += 1
            continue

        rolled = game.roll_die()
        print(f"Rolled Die: {rolled}")

        move = random_agent(game)
        print(f"Chosen Column: {move}")

        game.apply_move(game.current_player, move, rolled)

        game.print_board()

        game.current_player = 1 - game.current_player
        turn += 1

    print("\n" + "=" * 30)
    print("GAME OVER")
    game.print_board()
    print("Winner:", game.get_winner())
