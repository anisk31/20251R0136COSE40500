# converts column index to letters
def horizontal_label(index):
    return chr(ord('A') + index)

# converts string to tuple for board indexing
def coordinate_to_tuple(coord):
    try:
        row = ord(coord[0].upper()) - ord('A')
        col = int(coord[1:]) - 1
        if 0 <= row < 19 and 0 <= col < 19:
            return row, col
    except:
        return None

# converts tuple back to string for display
def tuple_to_coordinate(move):
    row, col = move
    return f"{chr(ord('A') + row)}{col + 1}"

# display the board according to colour and availability
def print_board(game):
    # print column headers (1 to 19) aligned
    print("   " + " ".join(f"{j+1:2}" for j in range(game.size)))

    # print each row with row label (A-S) and aligned cells
    for i in range(game.size):
        row_label = chr(ord('A') + i)
        row_cells = []
        for j in range(game.size):
            if game.board[i][j] == 1:
                row_cells.append("○")
            elif game.board[i][j] == 2:
                row_cells.append("●")
            else:
                row_cells.append(".")

        print(f"{row_label:2}  " + "  ".join(row_cells))
