"""
MCTS starter code. This is the only file you'll need to modify, although
you can take a look at game1.py to get a sense of how the game is structured.

@author Bryce Wiedenbeck
@author Anna Rafferty (adapted from original in Jan 2017)
"""

# These imports are used by the starter code.
import random
import argparse
import game1
from math import sqrt, log, isnan
# random.seed(1)
# You will want to use this import in your code
import math

# Whether to display the UCB rankings at each turn.
DISPLAY_BOARDS = False 

# UCB_CONST value - you should experiment with different values
UCB_CONST = .5


class Node(object):
    """Node used in MCTS"""
    
    def __init__(self, state, parent_node):
        """Constructor for a new node representing game state
        state. parent_node is the Node that is the parent of this
        one in the MCTS tree. """
        self.state = state
        self.parent = parent_node
        self.children = {} # maps moves (keys) to Nodes (values); if you use it differently, you must also change addMove
        self.visits = 0
        self.value = float("nan")
        # Note: you may add additional fields if needed
        
    def addMove(self, move):
        """
        Adds a new node for the child resulting from move if one doesn't already exist.
        Returns true if a new node was added, false otherwise.
        """
        if move not in self.children:
            state = self.state.nextState(move)
            self.children[move] = Node(state, self)
            return True
        return False
    
    def getValue(self):
        """
        Gets the value estimate for the current node. Value estimates should correspond
        to the win percentage for the player at this node (accounting for draws as in 
        the project description).
        """
        return self.value

    def updateValue(self, outcome):
        """Updates the value estimate for the node's state.
        outcome: +1 for 1st player win, -1 for 2nd player win, 0 for draw."""
        "*** YOUR CODE HERE ***"
        # NOTE: which outcome is preferred depends on self.state.turn()
        if isnan(self.value):
            self.value = 0

        nextTotal = self.getValue() * self.visits
        if outcome != 0:
            if outcome == self.state.getTurn():
                # win
                nextTotal += 1.
                # TODO: CHECK WHICH PLAYER THAT IS
            else:
                # lose
                nextTotal += 0.
        else:
            # draw
            nextTotal += 0.5
        self.visits += 1
        self.value = nextTotal/self.visits

    def UCBWeight(self):
        """Weight from the UCB formula used by parent to select a child.
        This node will be selected by parent with probability proportional
        to its weight."""
        "*** YOUR CODE HERE ***"
        # for the node choosing the child; the value of the node should be the lose rate (which is what the
        # parent node want to maximize
        weight = 1 - self.getValue() + UCB_CONST * sqrt(log(self.parent.visits)/self.visits)
        return weight

def MCTS(root, rollouts):
    """Select a move by Monte Carlo tree search.
    Plays rollouts random games from the root node to a terminal state.
    In each rollout, play proceeds according to UCB while all children have
    been expanded. The first node with unexpanded children has a random child
    expanded. After expansion, play proceeds by selecting uniform random moves.
    Upon reaching a terminal state, values are propagated back along the
    expanded portion of the path. After all rollouts are completed, the move
    generating the highest value child of root is returned.
    Inputs:
        node: the node for which we want to find the optimal move
        rollouts: the number of root-leaf traversals to run
    Return:
        The legal move from node.state with the highest value estimate
    """
    "*** YOUR CODE HERE ***"
    if rollouts == 0:
        return randomMove(root)
    currentState = root
    for i in range(rollouts):
        # select & expand
        toSimulate = select(root)
        # print game1.print_board(toSimulate.state)
        # simulate and get the outcome
        outcome = simulate(toSimulate)
        # back-propagate
        backPropagate(toSimulate, outcome)

    # find the child node with lowest value(least likely to win for the opponent)
    nextMove = None
    # print game1.show_values(root)
    for move, child in root.children.items():
        if (nextMove is None) or (child.getValue() < root.children[nextMove].getValue()):
            nextMove = move
    # print nextMove
    return nextMove

def backPropagate(currentNode, outcome):
    while currentNode is not None:
        # updateValue() also updates count
        currentNode.updateValue(outcome)
        currentNode = currentNode.parent

def simulate(node):
    """
    Simulate a random game from a node.
    :param node: node to simulate
    :return: the outcome of the simulation
    """
    currentState = node.state
    while not currentState.isTerminal():
        moves = currentState.getMoves()
        nextInd = random.randint(0, len(moves)-1)
        currentState = currentState.nextState(moves[nextInd])
    return currentState.value()

def select(currentNode):
    """
    Recursive function to select and expand an unexpanded node in the tree.
    If a terminal node is encountered, it returns it.
    :param currentNode:
    :return: the node to simulate
    """
    # Base case 1: check terminal state
    if currentNode.state.isTerminal():
        return currentNode
    nextMove = getUnexpandedMove(currentNode)
    # Base case 2: has unexpanded child, expand and return the child for simulation
    if nextMove is not None:
        # find an unexpanded node, add it to the search tree
        assert currentNode.addMove(nextMove), 'move existed'
        return currentNode.children[nextMove]

    # node without unexpanded child, pick one child w.p. proportional to weight
    zConstant = 0.
    nodes = []
    weights = []
    for key, node in currentNode.children.items():
        nodes.append(node)
        weight = node.UCBWeight()
        weights.append(weight)
        zConstant += weight
    # print len(nodes), len(weights), zConstant
    # pick a child w.p. proportional to the weight
    randomNumber = random.random() * zConstant
    cumWeightSum = 0.
    for i, weight in enumerate(weights):
        cumWeightSum += weight
        if randomNumber <= cumWeightSum:
            return select(nodes[i])
    assert False, "should not get here"

def getUnexpandedMove(node):
    moves = node.state.getMoves()
    candidates = []
    for move in moves:
        if move not in node.children:
            candidates.append(move)
    if len(candidates)==0:
        # no unexpanded child
        return None
    # randomly choose a child
    return candidates[random.randint(0, len(candidates)-1)]


def parse_args():
    """
    Parse command line arguments.
    """
    p = argparse.ArgumentParser()
    p.add_argument("--rollouts", type=int, default=0, help="Number of root-to-leaf "+\
                    "play-throughs that MCTS should run). Default=0 (random moves)")
    p.add_argument("--numGames", type=int, default=0, help="Number of games "+\
                    "to play). Default=1")
    p.add_argument("--second", action="store_true", help="Set this flag to "+\
                    "make your agent move second.")
    p.add_argument("--displayBoard", action="store_true", help="Set this flag to "+\
                    "make display the board at each MCTS turn with MCTS's rankings of moves.")
    p.add_argument("--rolloutsSecondMCTSAgent", type=int, default=0, help="If non-0, other player "+\
                    "will also be an MCTS agent and will use the number of rollouts set with this "+\
                    "argument. Default=0 (other player is random)")   
    p.add_argument("--ucbConst", type=float, default=.5, help="Value for the UCB exploration"+\
                    "constant. Default=.5") 
    args = p.parse_args()
    if args.displayBoard:
        DISPLAY_BOARDS = True
    UCB_CONST = args.ucbConst
    return args


def randomMove(node):
    """
    Choose a valid move uniformly at random.
    """
    move = random.choice(node.state.getMoves())
    node.addMove(move)
    return move

def runMultipleGames(numGames, args):
    """
    Runs numGames games, with no printing except for a report on which game 
    number is currently being played, and reports final number
    of games won by player 1 and draws. args specifies whether player 1 or
    player 2 is MCTS and how many rollouts to use. For multiple games, you
    probably do not want to include the --displayBoard option in args, as
    this will do lots of printing and make running relatively slow.
    """
    player1GamesWon = 0
    draws = 0
    for i in range(numGames):
        print "Game " + str(i)
        node = playGame(args)
        winner = node.state.value()
        if winner == 1:
            player1GamesWon += 1
        elif winner == 0:
            draws += 1
    print "Player 1 games won: " + str(player1GamesWon) + "/" + str(numGames)
    print "Draws: " + str(draws) + "/" + str(numGames)

def playGame(args):
    """
    Play one game against another player.
    args specifies whether player 1 or player 2 is MCTS (
    or both if rolloutsSecondMCTSAgent is non-zero)
    and how many rollouts to use.
    Returns the final terminal node for the game.
    """
    # Make start state and root of MCTS tree
    start_state = game1.newGame()
    root1 = Node(start_state, None)
    if args.rolloutsSecondMCTSAgent != 0:
        root2 = Node(start_state, None)

    # Run MCTS
    node = root1
    if args.rolloutsSecondMCTSAgent != 0:
        node2 = root2
    while not node.state.isTerminal():
        if (not args.second and node.state.turn == 1) or \
                (args.second and node.state.turn == -1):
            move = MCTS(node, args.rollouts)
        else:
            if args.rolloutsSecondMCTSAgent == 0:
                move = randomMove(node)
            else:
                move = MCTS(node2, args.rolloutsSecondMCTSAgent)
        
        node.addMove(move)
        node = node.children[move]
        if args.rolloutsSecondMCTSAgent != 0:
            node2.addMove(move)
            node2 = node2.children[move]
    return node

            
    

def main():
    """
    Play a game of connect 4, using MCTS to choose the moves for one of the players.
    args on command line set properties; see parse_args() for details.
    """
    # Get commandline arguments
    args = parse_args()
    
    if args.numGames > 1:
        runMultipleGames(args.numGames, args)
    else:
        # Play the game
        node = playGame(args)
    
        # Print result
        winner = node.state.value()
        print game1.print_board(node.state)
        if winner == 1:
            print "Player 1 wins"
        elif winner == -1:
            print "Player 2 wins"
        else:
            print "It's a draw"
            
            
if __name__ == "__main__":
    main()
