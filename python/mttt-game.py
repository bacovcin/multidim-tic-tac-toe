from random import sample
from sys import exit

def isInt(x):
    try:
        int(x)
        return True
    except ValueError:
        return False

class State:
    # A state is defined by:
    # (a) the number of dimensions
    # (b) a list of places X has gone
    # (c) a list of places O has gone
    # (d) the current player
    # flag if the x player is AI
    # flag if the o player is AI
    def __init__(self, nDim, xes, oes, player, xai, oai):
        self.nDim = nDim
        self.xes = xes
        self.oes = oes
        self.player = player
        self.xAI = xai
        self.oAI = oai
        self.remainingMoves = (3**self.nDim) - (len(self.xes) + len(self.oes))

# Impure functions below

# Determines what the AI does
# relies on randomness, so is impure
def getAImove(state):
    # Currently implementing a standard (dumb) look ahead AI
    def buildPossibleMoves(state,curDimTrace):
        if len(curDimTrace) == state.nDim - 1:
            output = {}
            for i in range(3):
                newDim = [i] + curDimTrace
                if newDim in state.xes or newDim in state.oes:
                    continue
                else:
                    if state.player == 'X':
                        newState = State(state.nDim,
                                         [*state.xes,newDim],
                                         state.oes,
                                         'O', state.xAI, state.oAI)
                    else:
                        newState = State(state.nDim,
                                         state.xes,
                                         [*state.oes,newDim],
                                         'X', state.xAI, state.oAI)
                    output[(tuple(newDim), newState)] = {}
        else:
            output1 = buildPossibleMoves(state, [0] + curDimTrace)
            output2 = buildPossibleMoves(state, [1] + curDimTrace)
            output3 = buildPossibleMoves(state, [2] + curDimTrace)
            output = {**output1, **output2, **output3}
        return output
    def updateScores(scores,choice,scoreType,newScore):
        try:
            scores[choice][scoreType] += newScore
        except:
            try:
                scores[choice][scoreType] = newScore
            except:
                scores[choice] = {}
                scores[choice][scoreType] = newScore
        return scores
    # Let's start 3 levels deep
    choices = buildPossibleMoves(state,[])
    scores = {}
    for choice in choices:
        if state.remainingMoves >= 2:
            choices[choice] = buildPossibleMoves(choice[1],[])
            for choice2 in choices[choice]:
                if state.remainingMoves >= 3:
                    choices[choice][choice2] = buildPossibleMoves(choice2[1],[])
                    for choice3 in choices[choice][choice2]:
                        newScores = getScores(choice3[1])
                        scores = updateScores(scores,choice,'XScore',newScores[0])
                        scores = updateScores(scores,choice,'OScore',newScores[0])
                else:
                    newScores = getScores(choice2[1])
                    scores = updateScores(scores,choice,'XScore',newScores[0])
                    scores = updateScores(scores,choice,'OScore',newScores[0])
        else:
            newScores = getScores(choice[1])
            scores = updateScores(scores,choice,'XScore',newScores[0])
            scores = updateScores(scores,choice,'OScore',newScores[0])

    for choice in scores:
        if state.player == 'X':
            scores[choice] = scores[choice]['XScore'] - scores[choice]['OScore']
        else:
            scores[choice] = scores[choice]['OScore'] - scores[choice]['XScore']
    best_choices = [list(x[0]) for x in scores 
                    if scores[x] == max(scores.values())]
    return sample(best_choices,1)[0]

# Update the screen with the current state
def printStateToScreen(state):
    def generateGrid(state,curDimTrace):
        #state = gameState
        #curDimTrace is a identifying the current dimension

        # Actually, create a row if you are at the first dimension
        if len(curDimTrace) == state.nDim - 1:
            newRow = ''
            for i in range(3):
                if [i]+curDimTrace in state.xes:
                    newRow+= 'X|'
                elif [i]+curDimTrace in state.oes:
                    newRow+= 'O|'
                else:
                    newRow+= ' |'
            myOutput = newRow.rstrip('|')
        # We're going to be manipulating inherited material from recursive
        # calls
        else:
            # Get the recursive call output
            output1 = generateGrid(state,[0]+curDimTrace)
            output2 = generateGrid(state,[1]+curDimTrace)
            output3 = generateGrid(state,[2]+curDimTrace)
            myOutput = []
            # We're at the second dimension (introduce the horizontal grid
            # lines)
            if isinstance(output1,str):
                myOutput.append(output1)
                myOutput.append('~.~.~')
                myOutput.append(output2)
                myOutput.append('~.~.~')
                myOutput.append(output3)
            # We're at an odd dimension (extend the game board horizontally)
            elif not (state.nDim - len(curDimTrace)) % 2 == 0:
                output1 = [y for x in output1 for y in x.split('\n')]
                output2 = [y for x in output2 for y in x.split('\n')]
                output3 = [y for x in output3 for y in x.split('\n')]
                for k in range(len(output1)):
                    myOutput.append(output1[k]+' ! '+
                                    output2[k]+' ! '+
                                    output3[k]+' ! ')
            # We're at an even dimension (extend the game board vertically)
            else:
                myOutput.append('\n'.join(output1)+'\n')
                myOutput.append('\n'.join(output2)+'\n')
                myOutput.append('\n'.join(output3)+'\n')
            # This is the final dimension (join everything with new lines and
            # send off for printing)
            if curDimTrace == []:
                myOutput = '\n'.join([x.rstrip('! ') for x in myOutput])
        return myOutput
    print(generateGrid(state,[]))

# Get the next player's move
def getNextPlayerMove(state):
    def isValidMove(state,x):
        if x == '':
            return False
        s = x.split(',')

        if len(s) != state.nDim:
            print('Not the correct number of dimensions.\n')
            return False
        elif False in [y in ['0','1','2'] for y in s]:
            print('One of your dimensions was not an acceptable number (0,1,2).\n')
            return False
        s2 = [int(y) for y in s]
        if s2 in state.xes:
            print('This space already has an X in it.\n')
            return False
        elif s2 in state.oes:
            print('This space already has an O in it.\n')
            return False
        else:
            return True
    move = ''
    while not isValidMove(state, move):
        move = input('Where would you like to go Player ' +
                     state.player +
                     ' (give your move with 0,1,2 separated by commas)?\n')
    return [int(y) for y in move.split(',')]

# Figure out how many dimensions to use for the new game
def getNewGame():
    gameDim = ''
    while not isInt(gameDim):
        gameDim = input('How many dimensions will your next game be (q to quit)?\n').rstrip().lower()
        if gameDim == 'q':
            exit()
    gameDim = int(gameDim)
    xAI = ''
    while not isinstance(xAI, bool):
        xAI = input('Is X player an AI (y, n, q to quit)?\n').rstrip().lower()
        if xAI == 'q':
            exit()
        elif xAI == 'y':
            xAI = True
        elif xAI == 'n':
            xAI = False
    oAI = ''
    while not isinstance(oAI, bool):
        oAI = input('Is O player an AI (y, n, q to quit)?\n').rstrip().lower()
        if oAI == 'q':
            exit()
        elif oAI == 'y':
            oAI = True
        elif oAI == 'n':
            oAI = False
    return gameDim, xAI, oAI

# Pure functions remain
def getScores(state):
    xcount = 0
    used_points = []
    for x1 in state.xes:
        if x1 not in used_points and (0 in x1 or 2 in x1):
            for x2 in state.xes:
                if (x2 not in used_points and
                    x2 != x1 and
                    1 in x2):
                    for x3 in state.xes:
                        if ((x3 not in used_points) and
                             x1 != x3 and
                             x2 != x3 and
                             (2 in x3 or 0 in x3) and
                             False not in [(x1[j] == 0 and
                                            x2[j] == 1 and
                                            x3[j] == 2) or
                                           (x1[j] == 2 and
                                            x2[j] == 1 and
                                            x3[j] == 0) or
                                            (x1[j] == x2[j] == x3[j])
                                            for j in range(state.nDim)]):
                            print(x1)
                            print(x2)
                            print(x3)
                            print('\n')
                            xcount += 1
                            used_points.append(x1)
                            used_points.append(x2)
                            used_points.append(x3)

    ocount = 0
    used_points = []
    for o1 in state.oes:
        if o1 not in used_points and 0 in o1:
            for o2 in state.oes:
                if (o2 not in used_points and
                    o2 != o1 and
                    1 in o2):
                    for o3 in state.oes:
                        if ((o3 not in used_points) and
                             o3 != o1 and
                             o3 != o2 and
                             2 in o3 and
                             False not in [(o1[j] == 0 and
                                            o2[j] == 1 and
                                            o3[j] == 2) or
                                           (o1[j] == 2 and
                                            o2[j] == 1 and
                                            o3[j] == 0) or
                                            (o1[j] == o2[j] == o3[j])
                                            for j in range(state.nDim)]):
                            print(o1)
                            print(o2)
                            print(o3)
                            ocount += 1
                            used_points.append(o1)
                            used_points.append(o2)
                            used_points.append(o3)
    return xcount, ocount

# We need a function to evaluate whether or not someone has won
def hasVictor(state):
    xcount, ocount = getScores(state)
    if xcount >= state.nDim - 1:
        print('X just won the game!!!')
        return True
    elif ocount >= state.nDim - 1:
        print('O just won the game!!!')
        return True
    else:
        if state.remainingMoves == 0:
            print('The game is a tie!!!')
            return True
        print('X has ' + str(xcount) + ' lines; ' + 
              str((state.nDim - 1) - xcount) + ' more to win.')
        print('O has ' + str(ocount) + ' lines; ' + 
              str((state.nDim - 1) - ocount) + ' more to win.')
        return False

# Actually, run the game
if __name__ == "__main__":
    while True:
        newRules = getNewGame()
        state = State(newRules[0],[],[],'X',newRules[1],newRules[2])
        printStateToScreen(state)
        while not hasVictor(state):
            if state.player == 'X':
                if state.xAI:
                    newMove = getAImove(state)
                else:
                    newMove = getNextPlayerMove(state)
                state = State(state.nDim,
                              state.xes+[newMove],
                              state.oes,
                              'O',
                              state.xAI,
                              state.oAI)
            else:
                if state.oAI:
                    newMove = getAImove(state)
                else:
                    newMove = getNextPlayerMove(state)
                state = State(state.nDim,
                              state.xes,
                              state.oes+[newMove],
                              'X',
                              state.xAI,
                              state.oAI)
            printStateToScreen(state)
            print(state.__dict__)

