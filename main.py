from game import OmokGame
from ai import OmokAI
from utils import coordinate_to_tuple, tuple_to_coordinate, print_board

def main():
    print("Omok Game - Iterative Deepening Heuristic Alpha-Beta Search")
    print("Black (○) moves first. White (●) is the AI.")

    game = OmokGame()
    ai = OmokAI(player=2, time_limit=10)  

    # when game is not end yet
    while not game.is_terminal():
        print_board(game)

        if game.current_player == 1:
            while True:
                move_input = input("Your move (e.g., J10): ").strip()
                move = coordinate_to_tuple(move_input)
                if move and game.board[move[0]][move[1]] == 0:
                    print("")
                    break
                print("Invalid move. Try again.\n")
        else:
            print("AI is thinking...")
            move = ai.iterative_deepening_search(game)
            print(f"AI plays: {tuple_to_coordinate(move)}\n")

        game.make_move(*move)

    print_board(game)
    if game.winner:
        winner = "Black (You)" if game.winner == 1 else "White (AI)"
        print(f"Game over! {winner} wins!")
    else:
        print("Game over! It's a draw!")

if __name__ == "__main__":
    main()
