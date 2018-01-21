"""Creates the structure of the state variable"""
from copy import copy


class State:
    """
     A state is defined by:
     (a) the number of dimensions
     (b) a list of places X has gone
     (c) a list of places O has gone
     (d) the current player
     flag if the x player is AI
     flag if the o player is AI
    """
    def __init__(self, ndim, places, player, aistatus):
        """Creates an initial state"""
        self.ndim = ndim
        self.xes = places[0]
        self.oes = places[1]
        self.player = player
        self.xai = aistatus[0]
        self.oai = aistatus[1]
        self.remaining_moves = (3**self.ndim) - (len(self.xes) + len(self.oes))

    def get_scores(self):
        """Calculates the current score for a state"""

        def check_three_moves(moves, move1, move2, used_points, score):
            """Checks if three moves are a winning triplet"""
            for move3 in moves:
                if 2 in move3:
                    for j in range(self.ndim):
                        if not ((move1[j] == move2[j] == move3[j]) or
                                (move1[j] == 0 and
                                 move2[j] == 1 and
                                 move3[j] == 2) or
                                (move1[j] == 2 and
                                 move2[j] == 1 and
                                 move3[j] == 0)):
                            break
                    else:
                        return score + 1, tuple(list(used_points) +
                                                [move1, move2, move3])
            return score, used_points

        def check_two_moves(moves, move1, used_points, score):
            """Create duplets of moves"""
            for i in range(len(moves)):
                newmoves = copy(moves)
                move2 = newmoves.pop(i)
                if move2 not in used_points and 1 in move2:
                    score, used_points = check_three_moves(newmoves,
                                                           move1,
                                                           move2,
                                                           used_points,
                                                           score)
            return score, used_points

        def search_moves(moves, used_points):
            """Search for unique three in a row"""
            score = 0
            for i in range(len(moves)):
                newmoves = copy(moves)
                move1 = newmoves.pop(i)
                if move1 not in used_points and 0 in move1:
                    score, used_points = check_two_moves(newmoves, move1,
                                                         used_points, score)
            return score

        xcount = search_moves(self.xes, ())
        ocount = search_moves(self.oes, ())

        return xcount, ocount

    def has_victor(self):
        """A function to evaluate whether or not someone has won"""
        xcount, ocount = self.get_scores()
        if xcount >= self.ndim - 1:
            print('X just won the game!!!')
            return True
        elif ocount >= self.ndim - 1:
            print('O just won the game!!!')
            return True
        else:
            if self.remaining_moves == 0:
                print('The game is a tie!!!')
                return True
            print('X has ' + str(xcount) + ' lines; ' +
                  str((self.ndim - 1) - xcount) + ' more to win.')
            print('O has ' + str(ocount) + ' lines; ' +
                  str((self.ndim - 1) - ocount) + ' more to win.')
            return False

    def generate_grid(self, curdimtrace):
        '''state = gameState
           curDimTrace is a identifying the current dimension
           Actually, create a row if you are at the first dimension'''
        if len(curdimtrace) == self.ndim - 1:
            newrow = ''
            for i in range(3):
                if [i]+curdimtrace in self.xes:
                    newrow += 'X|'
                elif [i]+curdimtrace in self.oes:
                    newrow += 'O|'
                else:
                    newrow += ' |'
            myoutput = newrow.rstrip('|')
        # We're going to be manipulating inherited material from recursive
        # calls
        else:
            # Get the recursive call output
            output1 = self.generate_grid([0]+curdimtrace)
            output2 = self.generate_grid([1]+curdimtrace)
            output3 = self.generate_grid([2]+curdimtrace)
            myoutput = []
            # We're at the second dimension (introduce the horizontal grid
            # lines)
            if isinstance(output1, str):
                myoutput.append(output1)
                myoutput.append('~.~.~')
                myoutput.append(output2)
                myoutput.append('~.~.~')
                myoutput.append(output3)
            # We're at an odd dimension
            # (extend the game board horizontally)
            elif not (self.ndim - len(curdimtrace)) % 2 == 0:
                output1 = [y for x in output1 for y in x.split('\n')]
                output2 = [y for x in output2 for y in x.split('\n')]
                output3 = [y for x in output3 for y in x.split('\n')]
                for k, out1str in enumerate(output1):
                    myoutput.append(out1str + ' ! ' +
                                    output2[k] + ' ! ' +
                                    output3[k] + ' ! ')
            # We're at an even dimension (extend the game board vertically)
            else:
                myoutput.append('\n'.join(output1)+'\n')
                myoutput.append('\n'.join(output2)+'\n')
                myoutput.append('\n'.join(output3)+'\n')
            # This is the final dimension (join everything with new lines
            # and send off for printing)
            if curdimtrace == []:
                myoutput = '\n'.join([x.rstrip('! ') for x in myoutput])
        return myoutput

    def print_to_screen(self):
        """Prints the state to the screen"""
        print(self.generate_grid([]))
