# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from search import aStarSearch, depthFirstSearch
from searchAgents import ClosestDotSearchAgent, _manhattanDistance

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.
    """


    def getAction(self, gameState):
        """
        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        This evaluation function is not particularly good; using information
        from the game state would allow it to be much better, although still
        not as good as an agent that plans. You may find the information listed
        below helpful in later parts of the project (e.g., when designing
        an evaluation function for your planning agent).
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        return successorGameState.getScore()

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 1)
    """
    # def __init__(self):
    #     super(MinimaxAgent, self).__init__(evalFn='scoreEvaluationFunction', depth='2')
    #     self.currentDepth = 0

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        action, score = self.minMax(gameState, 0, self.index)
        return action

    #pass in currentDepth
    #return action, score
    def minMax(self, gameState, currentDepth, currentAgent):
        """
        Recursive function to calculate out the min when the opponent player is playing, max when pacman is playing
        :param gameState:
        :param currentDepth:
        :param currentAgent:
        :return: tuple of action and score
        """
        # Base case at the terminal states
        if gameState.isWin() or gameState.isLose():
            return None, self.evaluationFunction(gameState)
        if currentDepth==self.depth and currentAgent==0:
            return None, self.evaluationFunction(gameState)

        # Recursive case
        legalActions = gameState.getLegalActions(currentAgent)
        successors = [gameState.generateSuccessor(currentAgent, action) for action in legalActions]
        nextDepth = currentDepth
        nextAgent = currentAgent + 1
        if currentAgent == gameState.getNumAgents()-1:
            nextDepth += 1
            nextAgent = 0

        successorScores = [self.minMax(successor, nextDepth, nextAgent)[1] for successor in successors]
        if currentAgent == 0:
            index = maxIndex(successorScores)
        else:
            index = minIndex(successorScores)

        return legalActions[index], successorScores[index]

def minIndex(scores):
    """
    Helper function to find the min score index.
    :param scores: a list of scores
    :return: index of the min score in scores
    """
    minIndex = 0
    minScore = scores[0]
    for i, score in enumerate(scores):
        if score < minScore:
            minScore = score
            minIndex = i
    return minIndex

def maxIndex(scores):
    """
    Helper function to find the max score index.
    :param scores: a list of scores
    :return: index of the max score i6n scores
    """
    maxIndex = 0
    maxScore = scores[0]
    for i, score in enumerate(scores):
        if score > maxScore:
            maxScore = score
            maxIndex = i
    return maxIndex

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Initialize the alpha, beta values for pruning.
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        alpha = float("-inf")
        beta = float("inf")
        action, score = self.alphaBetaPrune(alpha, beta, gameState, 0, self.index)
        return action

        # pass in currentDepth
        # return action, score

    def alphaBetaPrune(self, alpha, beta, gameState, currentDepth, currentAgent):
        """
        Helper function: Minimax agent with alphaBeta pruning.
        :param alpha:
        :param beta:
        :param gameState:
        :param currentDepth:
        :param currentAgent:
        :return: a tuple of action and score
        """

        # Base case at terminal states
        if gameState.isWin() or gameState.isLose():
            return None, self.evaluationFunction(gameState)
        if currentDepth == self.depth and currentAgent == 0:
            return None, self.evaluationFunction(gameState)

        inMax = False
        currentValue = float("inf")
        if currentAgent == 0:
            inMax = True
            currentValue = float("-inf")

        # Recursive case
        legalActions = gameState.getLegalActions(currentAgent)
        nextDepth = currentDepth
        nextAgent = currentAgent + 1

        if currentAgent == gameState.getNumAgents()-1:
            nextAgent = 0
            nextDepth += 1
        scores = []
        for i, action in enumerate(legalActions):
            successor = gameState.generateSuccessor(currentAgent,action)
            _, returnedValue = self.alphaBetaPrune(alpha, beta, successor, nextDepth, nextAgent)
            scores.append(returnedValue)
            # max node
            if inMax:
                currentValue = max(currentValue,returnedValue)
                if currentValue > beta:
                    return legalActions[i], currentValue
                alpha = max(alpha, currentValue)
            # min node
            else:
                currentValue = min(currentValue, returnedValue)
                if currentValue < alpha:
                    return legalActions[i],currentValue
                beta = min(beta, currentValue)
        if inMax:
            index = maxIndex(scores)
        else:
            index = minIndex(scores)
        return legalActions[index], scores[index]

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """

          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        action, score = self.expectiMax(gameState, 0, self.index)
        return action

    def expectiMax(self, gameState, currentDepth, currentAgent):
        """
        Hepler Function: use probability to calculate out the utility for expectation and max agents.
        :param gameState:
        :param currentDepth:
        :param currentAgent:
        :return: a tuple of action and utility
        """
        # Base case
        # Use evaluation function to evaluate the utility for the current node
        if gameState.isWin() or gameState.isLose():
            return None, self.evaluationFunction(gameState)
        if currentDepth == self.depth and currentAgent == 0:
            return None, self.evaluationFunction(gameState)

        # Recursive case
        legalActions = gameState.getLegalActions(currentAgent)
        successors = [gameState.generateSuccessor(currentAgent, action) for action in legalActions]
        nextDepth = currentDepth
        nextAgent = currentAgent + 1
        if currentAgent == gameState.getNumAgents() - 1:
            nextDepth += 1
            nextAgent = 0
        successorScores = [self.expectiMax(successor, nextDepth, nextAgent)[1] for successor in successors]

        if currentAgent == 0:
            #pacman - max agent
            index = maxIndex(successorScores)
            return legalActions[index], successorScores[index]
        else:
            # ghost - expectation agent
            return None, average(successorScores)

def average(scores):
    """
    Helper function: find the average score from the input.
    :param scores:
    :return: average score
    """
    count = 0
    sum = 0.
    for s in scores:
        sum += s
        count += 1
    return sum/float(count)

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION:
    The evaluation function here deals with 2 situations: when ghost is close (within 3 steps) or far
    1.when ghost is far away, the evaluation doesn't care about where the ghost is but only evaluates the closest food
    (subtracting the distance from the closest food. The further the closest food is, the smaller evaluation is.)
    2.when ghost is close, the evaluation considers both the ghost distance and also the closest food.
    (substracting both distances from closest food and closest ghost from terminal utility, therefore, the further
    the closest food is, or the closer the closest ghost is, the smaller evaluation is)
    """
    "*** YOUR CODE HERE ***"
    ghostPositions = currentGameState.getGhostPositions()
    pacmanPosition = currentGameState.getPacmanPosition()
    foodGrid = currentGameState.getFood()
    foodList = foodGrid.asList()

    foodDifferences = [_manhattanDistance(foodPosition, pacmanPosition) for foodPosition in foodList]
    positionDifferences = [_manhattanDistance(ghostPosition, pacmanPosition) for ghostPosition in ghostPositions]
    mini = minIndex(positionDifferences)
    if foodDifferences == []:
        foodEval = 0
    else:
        mini2 = minIndex(foodDifferences)
        foodEval = foodDifferences[mini2]

    if positionDifferences[mini] <= 3:
        evalFunc = currentGameState.getScore() - positionDifferences[mini] - foodEval
    else:
        evalFunc = currentGameState.getScore() - foodEval

    return evalFunc

# Abbreviation
better = betterEvaluationFunction

