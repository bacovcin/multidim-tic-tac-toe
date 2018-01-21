"""Python code to implement multidimensional tic-tac-toe"""
from ai import get_ai_move
from state import State


def is_int(string):
    """Checks if a string can be converted into an integer"""
    try:
        int(string)
        return True
    except ValueError:
        return False


def get_next_player_move(state):
    """Uses input to get the next move by a human"""
    def is_valid_move(state, move):
        """Checks if the user's input is a valid move"""
        if move == '':
            return False
        smove = move.split(',')

        if len(smove) != state.ndim:
            print('Not the correct number of dimensions.\n')
            return False
        elif False in [y in ['0', '1', '2'] for y in smove]:
            print('One of your dimensions was not an acceptable number' +
                  '(0,1,2).\n')
            return False
        smove2 = [int(y) for y in smove]
        if smove2 in state.xes:
            print('This space already has an X in it.\n')
            return False
        elif smove2 in state.oes:
            print('This space already has an O in it.\n')
            return False
        return True
    move = ''
    while not is_valid_move(state, move):
        move = input('Where would you like to go Player ' +
                     state.player +
                     ' (give your move with 0,1,2 separated by commas)?\n')
    return [int(y) for y in move.split(',')]


def get_new_game():
    """Initializes a game"""
    def get_ai(player):
        """Gets an AI value"""
        myai = ''
        while not isinstance(myai, bool):
            myai = input('Is ' + player +
                         ' player an AI (y, n, q to quit)?\n').rstrip().lower()
            if myai == 'q':
                exit()
            elif myai == 'y':
                myai = True
            elif myai == 'n':
                myai = False
        return myai
    gamedim = ''
    while not is_int(gamedim):
        gamedim = input('How many dimensions will your next game be' +
                        '(q to quit)?\n').rstrip().lower()
        if gamedim == 'q':
            exit()
    gamedim = int(gamedim)
    xai = get_ai('X')
    oai = get_ai('O')
    return gamedim, xai, oai


def main():
    """Actually run the game"""
    while True:
        newrules = get_new_game()
        state = State(newrules[0],
                      ([], []),
                      'X',
                      (newrules[1], newrules[2]))
        state.print_to_screen()
        while not state.has_victor():
            if state.player == 'X':
                if state.xai:
                    newmove = get_ai_move(state)
                else:
                    newmove = get_next_player_move(state)
                state = State(state.ndim,
                              (state.xes+[newmove], state.oes),
                              'O',
                              (state.xai, state.oai))
            else:
                if state.oai:
                    newmove = get_ai_move(state)
                else:
                    newmove = get_next_player_move(state)
                state = State(state.ndim,
                              (state.xes, state.oes+[newmove]),
                              'X',
                              (state.xai, state.oai))
            state.print_to_screen()
            print(state.__dict__)


if __name__ == "__main__":
    main()
