# @SpencerLepine - Connect Four command-line game made w/ Python
import random
import math
import sys
import copy
import numpy as np
# Hard-coded board size
BOARD_COLS = 7
BOARD_ROWS = 6

#board variable
#Initialize board
board = [[' ' for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]

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
        self.board = board
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
 
        # Did not find any winners
        return False


#Start Rule-Based Implementation
#------------------------------------Rule-Based AI class------------------------------------
#Programmer: Jaime Torrico
#Everything related to the Rule-Based AI playing is in the RuleBasedAI() clasa
class RuleBasedAI():
    #qTable that holds the points for each column in in the board
    qTable = [None]*BOARD_COLS

    #Points system
    AIPointsTable = {0: 0, 1: 1.1, 2: 2.3, 3: 100, 4: 102}
    OpponentPointsTable = {0: 0, 1: 1, 2: 2.1, 3: 20, 4:21}

#--------------------------------------------------
    #Updates the Q table by calculating the points for all of the possible state spaces of the board
    #Programmer: Jaime Torrico
    def updateQ():
        #Calculated points for every column
        for c in range(BOARD_COLS):
            #Finds first open slot in each row and calculates points accordingly
            RuleBasedAI.findTopOpen(c)
        #prints the qTable
        print('Q-Table:',RuleBasedAI.qTable) 

#--------------------------------------------------
    #Finds the first open spot in each column where a piece would fall(to gravity) and fills and calculates its points
    #Programmer: Jaime Torrico
    def findTopOpen(column):
        #initialies value of zero to disregard any outdated valued that could possibly be saved
        RuleBasedAI.qTable[column] = 0

        #checks to see if a column is already full, if it puts a very large negative number in the table to prevent the AI from choosing 
        #a column that is already full
        if board[0][column] != ' ':
            RuleBasedAI.qTable[column] = -100
            return

        #If the bottom row is empty it will pass down the bottom row 
        #Checks the bottom row first to see if it does not have to check all of the other rows
        if board[5][column] == ' ':
            #Calls method to tally points passing down the according row and column as paramaters
            RuleBasedAI.tallyPoints(5, column)
            return

        #If the bottom row is not empty it will search through all of the rows in the column untill it finds the first empty row
        #It does this by finding the first occupied row and subtracing 1 from it, therefore returning where the new piece would fall due to gravity
        for r in range(BOARD_ROWS):
            if board[r][column] != ' ':
                #Calls method to tally points passing down the according row and column as paramaters
                RuleBasedAI.tallyPoints(r-1, column)
                return  

#--------------------------------------------------
    #Programmer: Jaime Torrico
    #Tallies points for opposite sides of the passed down row and column
    # Two complimentary methods are passed down in the paramaters (EX: countLeftPieces, countRightPieces) 
    # along with the current first open row and column
    # This method is to have the AI recognize pieces on opposite sides of the same spot to be counted as consecutive 
    def tallyOppositeSides(leftMethod, rightMethod,row, column):
        #how many of which piece there are on the left side
        #calls method that returns the pieces for the left side
        leftPieces = leftMethod(row, column)

        #how many of which piece there are to the right side
        #calls method that returns the pieces for the right side
        rightPieces = rightMethod(row, column)

        #If the pieces are empty / 0 or are different than the opposite side the points will be calculated independently
        if leftPieces == 0 or rightPieces == 0 or leftPieces[0] != rightPieces[0]:
            #left points calcualted
            leftPoints =  RuleBasedAI.returnPoints(leftPieces)
            #left points put in qTable
            RuleBasedAI.qTable[column] += leftPoints
            #right points calculated
            rightPoints =  RuleBasedAI.returnPoints(rightPieces)
            #right points put in qTable
            RuleBasedAI.qTable[column] += rightPoints
        #If the pieces have the same string than their number will be combined and points will be calculated together
        else:
            #String of the pieces
            string = leftPieces[0]
            #Numer of pieces
            number = leftPieces[1]+rightPieces[1]
            #pieces put together
            totalPieces = string, number
            #points calculated
            points = RuleBasedAI.returnPoints(totalPieces)
            #Points added to the qTable
            RuleBasedAI.qTable[column] += points

#--------------------------------------------------
    #Tallies the points for the row, and column passed down
    #Programmer: Jaime Torrico
    def tallyPoints(row, column):
    
        #Tallies pionts for pieces in opposite directions
        #After calling each method, the points are calculated and added to the qTable

        #Tallies points to the left and right horizontal (-)
        RuleBasedAI.tallyOppositeSides(RuleBasedAI.countLeftPieces, RuleBasedAI.countRightPieces,row, column)

        #Tallies points of the left and right of the left diagonal (\)
        RuleBasedAI.tallyOppositeSides(RuleBasedAI.countLeftUpDiagonalPieces, RuleBasedAI.countLeftDownDiagonalPieces, row, column)

        #Tallies points of the left and right of the right diagonal (/)
        RuleBasedAI.tallyOppositeSides(RuleBasedAI.countBottomRightDiagonal, RuleBasedAI.countTopRightDiagonalPieces, row, column)
        
        #Tallies points of the bottom (|) 
        #Pieces are counted with the countDownMethod
        pieces = RuleBasedAI.countDownPieces(row, column)
        #Points are calculated calling the dictionaries with the pieces
        points = RuleBasedAI.returnPoints(pieces)
        #Q-Table is updated with according points
        RuleBasedAI.qTable[column] += points

#--------------------------------------------------
    #Checks how many consecutive pieces of the same piece are to the left of the current open spot (-)
    #Programmer: Jaime Torrico
    #Counts how many pieces are to the left of the passed down row and column on the board
    def countLeftPieces(row, column):
        #The current piece to the left of the first open column
        piece = board[row][column-1]
        #Count variable starts at 0
        count = 0;
        #if there is no piece or out of bounds returns 0
        if piece == ' ':
            return 0
        #if there is a piece it counts and returns the piece
        else:
            for i in range(column, 0, -1):
                #Increments if the piece equals the privous
                if board[row][i-1] == piece and i-1 != 7:
                    count += 1
                #breaks if the pieces are different or if there is no piece
                else:
                    break
        #Returns the pieces and the count of the pieces
        return piece, count 

#--------------------------------------------------
    #Checks how many consecutive pieces of the same piece are to the right of the current the current open spot (-)
    #Programmer: Jaime Torrico
    def countRightPieces(row,column):
        #The current piece to the right of the first open column
        #Variable used to check if the column is out of bounds
        currColumn = column + 1
        if currColumn == 7:
            return 0
        #Initialized the piece    
        piece = board[row][column + 1]
        #Count starts at 0
        count = 0
        #if there is no piece or out of bounds returns 0
        if piece == ' ':
            return 0
        #otherwise it counts the pieces
        else:
            for i in range(column, 6, 1):
                #if the current board position is equal to the piece it will increment the count
                if board[row][i+1] == piece and i != 7:
                    count += 1
                #breaks if the pieces are different or if there is no piece
                else:
                    break
        return piece, count

#--------------------------------------------------
    #Checks how many consecutive pieces are to the top left diagonal of the current open spot (Top \)
    #Programmer: Jaime Torrico
    def countLeftUpDiagonalPieces(row, column):
        #If there is no left diagonal becuase it is out of bounds
        if row == 0 or column == 0:
            return 0
        #Set the piece to the current left diagonal
        piece = board[row-1][column-1]
        count = 0;
        #if there is no piece or out of bounds returns 0
        if piece == ' ':
            return 0
        else:
            #start at current column
            i = column
            #inc starts at 1 and increases by one each time to go to the left diagonal
            inc = 1
            #while the column is greater than 0
            while i > 0 and row-inc >= 0 and column-inc >= 0:
                #curr is set to the current location of the board
                curr = board[row-inc][column-inc]
                #If curr is the same piece at the piece than it will increment the count and the location of the location
                if curr == piece:
                    count += 1
                    inc += 1
                    i -= 1
                #Otherwise it will exit the loop
                else:
                    break
        #Returns the pieces and the count of the pieces
        return piece, count    

#--------------------------------------------------
    #Counts consecutive bottom right diagonal pieces (Bottom \)
    #Programmer: Jaime Torrico
    def countLeftDownDiagonalPieces(row, column):
        #If there is no diagonal becuase it is out of bounds it returns 0
        if row == 5 or column == 6:
            return 0

        #Set the piece to the current bottom right diagonal
        piece = board[row+1][column+1]
        count = 0;
        #if there is no piece or out of bounds returns 0
        if piece == ' ':
            return 0
        #If there is a piece
        else:
            #start at current column
            i = column
            #Inc starts at 1 and increases by one each time to go to the left diagonal
            inc = 1
            #while the row and column + inc are in bound
            while row + inc < 6 and column + inc < 7:
                #Cur is equal to the current location on the board
                curr = board[row+inc][column+inc]
                #if pieces are equal it increments the count
                if curr == piece:
                    count += 1
                    inc += 1
                    i += 1
                #Otherwise it exits the loop
                else:
                    break
        #Returns the pieces and the count of the pieces
        return piece, count

#--------------------------------------------------
    #Counts how many consecutive pieces are to the top right of the current open spot (Top /)
    #Programmer: Jaime Torrico
    def countTopRightDiagonalPieces(row, column):
        #If there is no right diagonal becuase it is out of bounds
        if row == 0 or column == 6:
            return 0
        #Set the piece to the current left diagonal
        piece = board[row-1][column+1]
        count = 0;
        #if there is no piece or out of bounds returns 0
        if piece == ' ':
            return 0
        
        else:
            #inc starts at 1 and increases by one each time to go to the left diagonal
            i = 1
            #while the top right diagonal is in bounds
            while row-i > 0 and column+i < 6:
                #Cur is set to the current position on the board
                curr = board[row-i][column+i]
                #If curr is equal to the piece the count is incremented
                if curr == piece:
                    count += 1
                    i += 1
                #Otherwise it exits the loop
                else:
                    break
        #Returns the pieces and the count of the pieces
        return piece, count

#--------------------------------------------------
    #Counts how many consecutive pieces are to the bottom left of the current open spot (Bottom /)
    #Programmer: Jaime Torrico
    def countBottomRightDiagonal(row, column):
        #If there is no diagonal becuase it is out of bounds
        if row == 5 or column == 0:
            return 0
        #Set the piece to the current left diagonal
        piece = board[row+1][column-1]
        count = 0;
        #if there is no piece or out of bounds returns 0
        if piece == ' ':
            return 0
        #otherwise is counts how many pieces there are
        else:
            #inc starts at 1 and increases by one each time to go to the left diagonal
            i = 1
            #while the top right diagonal is in bounds
            while row+i < 6 and column-i >= 0:
                #Curr is the current position on the board
                curr = board[row+i][column-i]
                #If curr and piece are the same piece the count is incremented
                if curr == piece:
                    count += 1
                    i += 1
                #otherwise the loop is terminated
                else:
                    break
        #Returns the pieces and the count of the pieces
        return piece, count

#--------------------------------------------------
    #Counts how many consecutive pieces are under the current open spot
    #Programmer: Jaime Torrico
    def countDownPieces(row, column):
        #if down is out of bounds
        if row == 5:
            return 0
        #Piece variable is initialized to the current location on the board
        piece = board[row + 1][column]
        count = 0
        #If the piece is empty it returns 0
        if piece == ' ':
            return 0
        #Otherwise it counts the pieces
        else:
            #While the row is in bounds
            while row < 5:
                #If the new location on the board is equl to the piece the count is incremented
                if board[row+1][column] == piece:
                    count += 1
                    row+=1
                #Otherwise the loop is termineated
                else:
                    break
        return piece, count

#--------------------------------------------------
    #Method that takes the type of piece and the number of pieces and returns the according points based on the point system
    #Programmer: Jaime Torrico
    def returnPoints(pieces):
        #Pieces is (string piece, int num)
        #EX: ('X',2) or ('O',2)
        #It holds how many of what piece are passed down

        #If there are no pieces it returns 0
        if pieces == 0: 
            return 0
        #Otherwise it retrieves the accordint points from the points tabe
        else:
            #Checks which character the piece is to call the correct dictionary
            if pieces[0] == 'O':
                #Rule-Based AI piece
                return RuleBasedAI.AIPointsTable[pieces[1]]
            else:
                #Opponent piece
                return RuleBasedAI.OpponentPointsTable[pieces[1]] 

#--------------------------------------------------
    #Chooses best move based on what is in the QTable
    #Programmer: Jaime Torrico
    def AIMove():
        #Updates Q-Table values
        RuleBasedAI.updateQ()

        #Retrieves the maximum from the qTable
        maxPoints = (max(RuleBasedAI.qTable))

        #If the table is empty the AI chooses randomly between columns 2 through 6 for its first move
        #This was done in order to diversify the gameplay
        if all ( points==0 for points in RuleBasedAI.qTable):
            firstMove = random.randint(1,6)
            print('First piece choose:', firstMove+1)
            return firstMove
        else:
            #Otherwise it returns the index of the maximum from the qTable
            return RuleBasedAI.qTable.index(maxPoints)
        
#-------------------------------------------------------------------------------------------
#End Rule-Based AI

#Variables that indicate which is the AI piece and which is the opponent piece
AI_PIECE = 'O'
PLAYER_PIECE = 'X'

def play():
    # Initialize the game board
    game = Board()

    game_over = False
    while not game_over:
        game.print_board()
        print(game.which_turn(), 'turn')
          
        # Ask the user for input, but only accept valid turns
        valid_move = False
        while not valid_move:
            #If it is the AI's turn
            if game.which_turn() == AI_PIECE:
                #Retrieves the AI's move
                ai_move = RuleBasedAI.AIMove()
                #Submits it move to the board
                #Does not subtract a 1 to make up for the index starting at 0 of the array therefore already being a -1
                valid_move = game.turn(int(ai_move))
                #ai_move +1 to make up for the array starting at 0 bt the board columns starting at 1
                print("RuleBased choose:",ai_move+1)
            #If it is not the AI's turn
            else : 
                user_move = input(f"{game.which_turn()}'s Turn - pick a column (1-{BOARD_COLS}): ")
                try:
                    valid_move = game.turn(int(user_move)-1)
                except:
                    print(f"Please choose a number between 1 and {BOARD_COLS}")
                    
        game_over = game.check_winner(True)
        # End the game if there is a tie
        if not any(' ' in x for x in game.board):
            print("The game is a draw..")
            return


if __name__ == '__main__':
    play()  
