"""
game1.py
This module represents the game of Connect 4.

@author Bryce Wiedenbeck
@author Anna Rafferty (adapted from original in Jan 2017)
"""


import numpy as np

HEIGHT = 6 # Height of the connect 4 board
WIDTH = 8 # Width of the connect 4 board
CONNECT = 4  # Number of items in a sequence necessary to win 

class State(object):
    """
    Represents a Connect 4 board.
    """
    
    def __init__(self, state=None, move=None):
        """
        Constructor. Makes a copy of state if a 
        state is passed in (i.e., non-destructive).
        """
        
        if state == None:
            self._board = np.zeros([HEIGHT, WIDTH], int)
            self._heights = np.zeros(WIDTH, int)
            self.turn = 1
        else:
            self._board = np.array(state._board)
            self._heights = np.array(state._heights)
            self.turn = -state.turn
        if move != None:
            self._board[HEIGHT - self._heights[move] - 1, move] = state.turn
            self._heights[move] += 1
        self.key = "".join(map(str, self._board.flat)) + str(self.turn)

    def getMoves(self):
        """
        Returns a vector of columns that one can place a piece in.
        """
        return np.nonzero(self._heights < HEIGHT)[0]

    def nextState(self, move):
        """
        Returns the State that would result from taking move in this state.
        """
        return State(self, move)

    def isTerminal(self):
        """
        Returns True if one player has won or if there are no more moves (a draw).
        Otherwise, returns False.
        """
        if len(self.getMoves()) == 0:
            return True
        return self._wins()
    
    def turn():
        """
        Returns +1 for the first player or -1 for the second player.
        This is the player whose turn it is to move in this state.
        """
        return self.turn
    
    def key():
        """
        Returns a string representing this state. 
        """
        return self.key
    

    def value(self):
        """
        Returns 0 if the state is a draw or hasn't been
        won by anyone, returns 1 if it's a win for the first
        player (i.e., the first player just made a move that resulted
        in this state, which is a win for the first player), and
        returns -1 if it's a win for the second player.
        """
        if self._wins():
            return -self.turn
        return 0

    def _wins(self):
        """
        Returns True if this state is a win for one of the players and False otherwise.
        """
        for j in range(WIDTH - CONNECT + 1):#start from left
            for i in range(HEIGHT-1, HEIGHT - CONNECT, -1):#start from bottom
                if self._board[i,j] == -self.turn:
                    for k in range(1,CONNECT):#go up
                        if self._board[i-k, j] != -self.turn:
                            break
                        if k == CONNECT - 1:
                            return True
                    for k in range(1,CONNECT):#go right
                        if self._board[i, j+k] != -self.turn:
                            break
                        if k == CONNECT - 1:
                            return True
                    for k in range(1,CONNECT):#go up-right
                        if self._board[i-k, j+k] != -self.turn:
                            break
                        if k == CONNECT - 1:
                            return True
            for i in range(HEIGHT - CONNECT, -1, -1):
                if self._board[i,j] == -self.turn:
                    for k in range(1,CONNECT):#go down-right
                        if self._board[i+k, j+k] != -self.turn:
                            break
                        if k == CONNECT - 1:
                            return True
        return False

def show_values(node):
    """
    Prints out the the board with a ranking of moves based on their values
    in MCTS. 1 is the move MCTS sees as the best move, and 8 is the worst
    move.
    """
    values = sorted(set([c.value for c in node.children.values()]))
    move_rank = {m:1+values.index(c.value) for m,c in node.children.items()}
    result = u"\n" + (" " + u"\u25a0")*WIDTH + u" \u25E9\n"
    for i in range(HEIGHT):
        result +=  u"\u25A1" + " "
        for j in range(WIDTH):
            move = j
            if i == (HEIGHT - node.state._heights[j] - 1) and move_rank.get(move, 10) < 10:
                c = str(move_rank[move])
            else:
                c = _print_char(node.state._board[i,j])
            result += c + " "
        result += u"\u25A1" + "\n"
    result += u"\u25EA" + (" " + u"\u25a0") * WIDTH
    return result

def print_board(state):
    """
    Print out the board in a human-readable form.
    """
    result = u"\n" + (" " + u"\u25a0")*WIDTH + u" \u25E9\n"
    for i in range(HEIGHT):
        result +=  u"\u25A1" + " "
        for j in range(WIDTH):
            c = _print_char(state._board[i,j])
            result += c + " "
        result += u"\u25A1" + "\n"
    result += u"\u25EA" + (" " + u"\u25a0") * WIDTH
    return result

def _print_char(i):
    """
    Get the unicode string to be printed for a piece of type i, or
    the character for an empty cell if i is 0. Note that 1 corresponds to a
    piece played by player 2 and -1 corresponds to a piece played by player 1
    (this is the opposite of how the turn instance variable works
    in state).
    """
    if i > 0:
        return u'\u25CB' # black piece
    if i < 0:
        return u'\u25CF' # white piece
    return u'\u00B7' # empty cell

def newGame():
    """
    Get a state representing a new game of Connect 4.
    """
    return State()
