import numpy as np
from copy import copy

# Set the dimensions of the Tic-Tac-Toe board
rows = 3
cols = 3

# Initialize the game board as a 3x3 array filled with zeros
board = np.zeros((rows, cols))

# Define the mapping of values on the board
# 0 -> blank
# 1 -> 'X'
# 2 -> 'O'

# Constants for alpha-beta pruning
inf = 9999999999
neg_inf = -9999999999

def printBoard():
    # Iterate over each row and column in the board
    for i in range(0, rows):
        for j in range(0, cols):
            # Print the corresponding symbol based on the value in the board
            if board[i, j] == 0:
                print(' _ ', end='')

            elif board[i, j] == 1:
                print(' X ', end='')

            else:
                print(' O ', end='')

        # Move to the next line to print the next row
        print()
# Initialize the heuristic table to evaluate board positions for each winning position
heuristicTable = np.zeros((rows + 1, cols + 1))

# Calculate the number of winning positions
numberOfWinningPositions = rows + cols + 2

# Populate the heuristic table with values for each position
# The index represents the number of X's or O's in a winning position
for index in range(0, rows + 1):
    heuristicTable[index, 0] = 10 ** index  # Positive value for X's
    heuristicTable[0, index] = -10 ** index  # Negative value for O's

# Define the array of winning positions
winningArray = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]])

def utilityOfState(state):
    # Create a copy of the flattened state array
    stateCopy = copy(state.ravel())

    # Initialize the heuristic value
    heuristic = 0

    # Iterate over each winning position
    for i in range(0, numberOfWinningPositions):
        maxp = 0
        minp = 0

        # Check the cells in the current winning position
        for j in range(0, rows):
            # Count the number of 'O's (maxp) and 'X's (minp) in the winning position
            if stateCopy[winningArray[i, j]] == 2:
                maxp += 1
            elif stateCopy[winningArray[i, j]] == 1:
                minp += 1

        # Calculate the heuristic value for the current winning position
        heuristic += heuristicTable[maxp][minp]

    # Return the accumulated heuristic value for the state
    return heuristic
def minimax(state, alpha, beta, maximizing, depth, maxp, minp):
    # Base case: if depth reaches 0, return the utility of the current state
    if depth == 0:
        return utilityOfState(state), state

    # Find the available positions in the state where a move can be made
    rowsLeft, columnsLeft = np.where(state == 0)

    # Create a copy of the state to be returned
    returnState = copy(state)

    # If there are no more available positions or the game is over, return the utility of the current state
    if rowsLeft.shape[0] == 0:
        return utilityOfState(state), returnState

    if maximizing:
        utility = neg_inf
        for i in range(0, rowsLeft.shape[0]):
            # Make a move in the next available position
            nextState = copy(state)
            nextState[rowsLeft[i], columnsLeft[i]] = maxp

            # Recursively call minimax on the next state with maximizing turned off
            Nutility, Nstate = minimax(nextState, alpha, beta, False, depth - 1, maxp, minp)

            # Update the utility and return state if a better move is found
            if Nutility > utility:
                utility = Nutility
                returnState = copy(nextState)

            # Update alpha if the utility is greater
            if utility > alpha:
                alpha = utility

            # Perform alpha-beta pruning if alpha is greater than or equal to beta
            if alpha >= beta:
                break

        return utility, returnState

    else:
        utility = inf
        for i in range(0, rowsLeft.shape[0]):
            # Make a move in the next available position
            nextState = copy(state)
            nextState[rowsLeft[i], columnsLeft[i]] = minp

            # Recursively call minimax on the next state with maximizing turned on
            Nutility, Nstate = minimax(nextState, alpha, beta, True, depth - 1, maxp, minp)

            # Update the utility and return state if a better move is found
            if Nutility < utility:
                utility = Nutility
                returnState = copy(nextState)

            # Update beta if the utility is smaller
            if utility < beta:
                beta = utility

            # Perform alpha-beta pruning if alpha is greater than or equal to beta
            if alpha >= beta:
                break

        return utility, returnState
def checkGameOver(state):
    # Create a copy of the state to avoid modifying the original state
    stateCopy = copy(state)

    # Calculate the utility value of the state using the utilityOfState function
    value = utilityOfState(stateCopy)

    # If the value is greater than or equal to 1000, it indicates a win for the current player
    if value >= 1000:
        return 1  # Return 1 to indicate a win

    # If the value is not greater than 1000, it indicates the game is not over or it's a draw
    return -1  # Return -1 to indicate the game is not over or it's a draw
def isMoveValid(row, col):
    # Check if the given row and column are within the valid range of the board
    if row < 0 or row >= rows or col < 0 or col >= cols:
        return False

    # Check if the cell at the given row and column is already occupied
    if board[row, col] != 0:
        return False

    # Return True if the move is valid (within range and not occupied), False otherwise
    return True
def HumanagainstAI():
    num = int(input('Enter player num (1st or 2nd): '))
    value = 0
    global board
    for turn in range(0, rows * cols):
        if (turn + num) % 2 == 1:  # Make the player go first, and assign 'X' to the human player
            print('Your turn')
            validMove = False
            while not validMove:
                try:
                    r, c = [int(x) for x in input('Enter your move (row column): ').split(' ')]
                except:
                    validMove = False
                if isMoveValid(r - 1, c - 1):  # Check if the move is valid
                    board[r - 1, c - 1] = 1  # Assign 'X' to the chosen cell
                    validMove = True
                else:
                    print('Invalid move! Try again.')

            printBoard()  # Print the updated board
            value = checkGameOver(board)  # Check if the game is over
            if value == 1:
                print('You win. Game Over')
                board = np.zeros((rows, cols))  # Reset the board
                return
            print('\n')
        else:  # It's the computer's turn, make the AI always put a circle ('O')
            print('AI turn')
            state = np.copy(board)
            value, nextState = minimax(state, neg_inf, inf, True, 2, 2, 1)  # Use minimax algorithm to choose the AI's move
            board = np.copy(nextState)
            printBoard()
            print('\n')
            value = checkGameOver(board)
            if value == 1:
                print('PC wins. Game Over')
                board = np.zeros((rows, cols))
                return
    board = np.zeros((rows, cols))
    print('It\'s a draw')

def AIagainstAI():
    value = 0
    global board
    for turn in range(0, rows * cols):
        if turn % 2 == 0:  # AI 1's turn
            print('AI1 turn')
            state = np.copy(board)
            value, nextState = minimax(state, neg_inf, inf, True, 2, 2, 2)  # Use minimax algorithm to choose AI 1's move
            board = np.copy(nextState)
            printBoard()
            print('\n')
            value = checkGameOver(board)
            if value == 1:
                print('AI 1 wins. Game Over')
                board = np.zeros((rows, cols))
                return
        else:  # AI 2's turn
            print('AI2 turn')
            state = np.copy(board)
            value, nextState = minimax(state, neg_inf, inf, False, 2, 2, 1)  # Use minimax algorithm to choose AI 2's move
            board = np.copy(nextState)
            printBoard()
            print('\n')
            value = checkGameOver(board)
            if value == 1:
                print('AI 2 wins. Game Over')
                board = np.zeros((rows, cols))
                return
    board = np.zeros((rows, cols))
    print('It\'s a draw')

# This is what I added
def main():
    print("Welcome to Tic-Tac-Toe!")
    while True:
        print("\nChoose a game mode:")
        print("1. Human vs AI")
        print("2. AI vs AI")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            print("\nStarting Human vs AI game...")
            printBoard()
            print()
            HumanagainstAI()
        elif choice == '2':
            print("\nStarting AI vs AI game...")
            printBoard()
            print()
            AIagainstAI()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()