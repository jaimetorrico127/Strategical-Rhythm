import random
import math
import sys
import copy
import numpy as np
# SpencerLepine - Connect Four command-line game made w/ Python

# Hard-coded board size
BOARD_COLS = 7
BOARD_ROWS = 6


# Game board object
class Board():
    def __init__(self):
        players1 = ['X', 'O']
        players2 = ['O','X']
        coin = random.randint(0,1)
        if coin == 0:
          self.players = players1
        else:
          self.players = players2
        self.board = [[' ' for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.turns = 0
        self.last_move = [-1, -1] # [r, c]

    def print_board(self):
        print("\n")
        # Number the columns seperately to keep it cleaner
        for r in range(BOARD_COLS):
            print(f"  ({r+1}) ", end="")
        print("\n")

        # Print the slots of the game board
        for r in range(BOARD_ROWS):
            print('|', end="")
            for c in range(BOARD_COLS):
                print(f"  {self.board[r][c]}  |", end="")
            print("\n")

        print(f"{'-' * 42}\n")

    def which_turn(self):
        
        return self.players[self.turns % 2]
    
    def in_bounds(self, r, c):
        return (r >= 0 and r < BOARD_ROWS and c >= 0 and c < BOARD_COLS)

    def turn(self, column):
        # Search bottom up for an open slot
        for i in range(BOARD_ROWS-1, -1, -1):
            if self.board[i][column] == ' ':
                self.board[i][column] = self.which_turn()
                self.last_move = [i, column]

                self.turns += 1
                return True

        return False

    def check_winner(self,liveGamePlay):
        last_row = self.last_move[0]
        last_col = self.last_move[1]
        last_letter = self.board[last_row][last_col]

        # [r, c] direction, matching letter count, locked bool
        directions = [[[-1, 0], 0, True], 
                      [[1, 0], 0, True], 
                      [[0, -1], 0, True],
                      [[0, 1], 0, True],
                      [[-1, -1], 0, True],
                      [[1, 1], 0, True],
                      [[-1, 1], 0, True],
                      [[1, -1], 0, True]]
        
        # Search outwards looking for matching pieces
        for a in range(4):
            for d in directions:
                r = last_row + (d[0][0] * (a+1))
                c = last_col + (d[0][1] * (a+1))

                if d[2] and self.in_bounds(r, c) and self.board[r][c] == last_letter:
                    d[1] += 1
                else:
                    # Stop searching in this direction
                    d[2] = False

        # Check possible direction pairs for '4 pieces in a row'
        for i in range(0, 7, 2):
            if (directions[i][1] + directions[i+1][1] >= 3):
                if liveGamePlay:
                    self.print_board()
                    print(f"{last_letter} is the winner!")
                    return last_letter
                else: # heuristic test
                    return last_letter
                #self.print_board()
                #print(f"{last_letter} is the winner!")
                #return last_letter # we need to figure out how to pass this out to identify a desirable direction  

        # Did not find any winners
        return False
#-----------------------------------------------AI PROGRAMMING-------------------------------------------------------
AI_PIECE = 'O'
PLAYER_PIECE = 'X'
EMPTY = ' '

GAME_LENGTH = 4

def get_next_available_row(B, col):
    for r in range(BOARD_ROWS):
        if B.board[r][col] == EMPTY:
            return r

def evaluate_heuristic(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4
    return score

def heuristic_score(B, piece):
    board = np.array(B.board)
    score = 0
    center_array = [i for i in list(board[:, BOARD_COLS//2])]
    center_count = center_array.count(piece)
    score += center_count * 3
    # Checking the horizontals
    # the horizontals logically check out: either way we take them row by row and evaluate each row
    for r in range(BOARD_ROWS):
        row_array = [i for i in list(board[r,:])]
        for c in range(BOARD_COLS-3):
            window = row_array[c:c+GAME_LENGTH]
            score += evaluate_heuristic(window, piece)
    # Checking the verticals
    for c in range(BOARD_COLS):
        col_array = [i for i in list(board[:,c])]
        for r in range(BOARD_ROWS-3):
            window = col_array[r:r+GAME_LENGTH]
            score += evaluate_heuristic(window, piece)
    # Checking positively sloped diagonals
    for r in range(BOARD_ROWS-3):
        for c in range(BOARD_COLS-3):
            window = [B.board[r+i][c+i] for i in range(GAME_LENGTH)]
            score += evaluate_heuristic(window, piece)
    # Checking negatively sloped diagonals
    for r in range(BOARD_ROWS-3): # O(r)  => total T(n) = O(rcg)
            # T(cloop) = O(c)
        for c in range(BOARD_COLS-3):
            # T(window) = O(connect i)
            window = [B.board[r+3-i][c+i] for i in range(GAME_LENGTH)]
            score += evaluate_heuristic(window, piece)
    return score
def is_terminal_position(B):
    return B.check_winner(False) == AI_PIECE or B.check_winner(False) == PLAYER_PIECE or len(get_valid_positions(B)) == 0
def is_valid_position(B, col):
    return B.board[0][col] == EMPTY

def get_valid_positions(B):
    valid_positions = []
    for col in range(BOARD_COLS):
        if is_valid_position(B, col):
            valid_positions.append(col)
    return valid_positions

def minimax(B, depth, alpha, beta, maxPlayer):
    valid_positions = get_valid_positions(B)
    is_terminal = is_terminal_position(B)
    if depth == 0 or is_terminal:
        if is_terminal:
            
            if B.check_winner(False) == AI_PIECE: # AI piece
                
                return (None, 100000000000000)
                             
            elif B.check_winner(False) == PLAYER_PIECE: # Player Piece
                return (None, -100000000000000)
            else: # game over, no more moves
                return (None, 0)
        else: # Depth is zero
            return (None, heuristic_score(B, AI_PIECE))
    if maxPlayer:
        value = -math.inf
        column = random.choice(valid_positions)
        for col in valid_positions:
            row = get_next_available_row(B, col)
            b_copy = copy.deepcopy(B)
            #drop_piece(b_copy, row, col, PLAYER_PIECE)
            b_copy.turn(col)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
              break
        return column, value
    else: # minPlayer
        value = math.inf
        column = random.choice(valid_positions)
        for col in valid_positions:
            row = get_next_available_row(B, col)
            b_copy = copy.deepcopy(B)
            b_copy.turn(col)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
              break
        return column, value
        
#--------------------------------------------------------------------------------------------------------------------
def play():
    # Initialize the game board
    game = Board()

    game_over = False
    while not game_over:
        game.print_board()
        print(game.which_turn())
        
          
        # Ask the user for input, but only accept valid turns
        valid_move = False
        while not valid_move:
            if game.which_turn() == PLAYER_PIECE:
                user_move = input(f"{game.which_turn()}'s Turn - pick a column (1-{BOARD_COLS}): ")
                try:
                    valid_move = game.turn(int(user_move)-1)
                except:
                    print(f"Please choose a number between 1 and {BOARD_COLS}")
            else : # AI turn
                valid_move = True
                AI_move, points = minimax(game,5, -math.inf, math.inf, True)
                #print(points)
                valid_move = game.turn(int(AI_move))
        
        #if game.which_turn() == AI_PIECE:
          #print(is_terminal_position(game))
          #AI_move = minimax(game,5, -math.inf, math.inf, True)[0]
          
          #valid_move = game.turn(int(AI_move))  
          #print(points)
        # End the game if there is a winner
        game_over = game.check_winner(True)
        
        # End the game if there is a tie
        if not any(' ' in x for x in game.board):
            print("The game is a draw..")
            return


if __name__ == '__main__':
    play()  