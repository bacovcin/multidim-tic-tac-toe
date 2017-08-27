from string import Template
from sys import exit
from pprint import pprint
from copy import copy

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
    def __init__(self, nDim, xes, oes, player):
        self.nDim = nDim
        self.xes = xes
        self.oes = oes
        self.player = player

# Impure IO functions below
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
def getNextPlayerMove(state, player):
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
                     player +
                     ' (give your move with 0,1,2 separated by commas)?\n')
    return [int(y) for y in move.split(',')]

# Figure out how many dimensions to use for the new game
def getNewGameDim():
    gameDim = ''
    while not isInt(gameDim):
        gameDim = input('How many dimensions will your next game be (q to quit)?\n').rstrip()
        if gameDim == 'q':
            exit()
    return int(gameDim)

# Pure functions remain

# We need a function to evaluate whether or not someone has won
def hasVictor(state):
    xcount = 0
    used_points = []
    for x1 in state.xes:
        for x2 in state.xes:
            for x3 in state.xes:
                if ((x1 != x2) and
                    (x1 != x3) and
                    (x2 != x3) and
                    (x1 not in used_points) and
                    (x2 not in used_points) and
                    (x3 not in used_points) and
                    False not in [(x1[i] == 0 and x2[i] == 1 and x3[i] == 2) or
                                  (x1[i] == x2[i] == x3[i])
                                  for i in range(state.nDim)]):
                    xcount += 1
                    used_points.append(x1)
                    used_points.append(x2)
                    used_points.append(x3)

    ocount = 0
    for o1 in state.oes:
        for o2 in state.oes:
            for o3 in state.oes:
                if ((o1 != o2) and
                    (o1 != o3) and
                    (o2 != o3) and
                    (o1 not in used_points) and
                    (o2 not in used_points) and
                    (o3 not in used_points) and
                    False not in [(o1[i] == 0 and o2[i] == 1 and o3[i] == 2) or
                                  (o1[i] == o2[i] == o3[i])
                                  for i in range(state.nDim)]):
                    ocount += 1
                    used_points.append(o1)
                    used_points.append(o2)
                    used_points.append(o3)
    if xcount >= state.nDim - 1:
        print('X just won the game!!!')
        return True
    elif ocount >= state.nDim - 1:
        print('O just won the game!!!')
        return True
    else:
        print('X has ' + str(xcount) + ' lines; ' + 
              str((state.nDim - 1) - xcount) + ' more to win.')
        print('O has ' + str(ocount) + ' lines; ' + 
              str((state.nDim - 1) - ocount) + ' more to win.')
        return False

# Actually, run the game
if __name__ == "__main__":
    while True:
        newDim = getNewGameDim()
        state = State(newDim,[],[],'X')
        printStateToScreen(state)
        while not hasVictor(state):
            newMove = getNextPlayerMove(state,state.player)
            if state.player == 'X':
                state = State(state.nDim,
                              state.xes+[newMove],
                              state.oes,
                              'O')
            else:
                state = State(state.nDim,
                              state.xes,
                              state.oes+[newMove],
                              'X')
            printStateToScreen(state)

