"""Python code to implement multidimensional tic-tac-toe"""
import curses
from ai import dumb_lookahead as get_ai_move
from state import State


def is_int(string):
    """Checks if a string can be converted into an integer"""
    try:
        int(string)
        return True
    except ValueError:
        return False


def get_next_player_move(state, gui):
    """Uses input to get the next move by a human"""
    def is_valid_move(state, x):
        if x == '':
            return False, '\n'
        s = x.split(',')

        if len(s) != state.ndim:
            return False, 'Not the correct number of dimensions.\n'
        s2 = [int(y) for y in s]
        if s2 in state.xes:
            return False, 'This space already has an X in it.\n'
        elif s2 in state.oes:
            return False, 'This space already has an O in it\n'
        return True, ''

    move = ''
    querystr = ('Where would you like to go Player ' +
                state.player +
                ' (give your move with 0,1,2 separated by commas)?')
    errorstr = '\n'
    curstr = ''
    is_valid = False
    while not is_valid:
        gui['inputbar'].clear()
        gui['inputbar'].addstr(querystr + '\t' + errorstr + curstr)
        gui['inputbar'].refresh()
        nextchr = gui['inputbar'].getkey()
        if nextchr in ('\n', '\r', curses.KEY_ENTER):
            move = curstr
        elif nextchr == 'q':
            exit()
        elif nextchr in ['0', '1', '2', ',']:
            curstr += nextchr
        elif nextchr in ['\b', '\x7f',
                         curses.KEY_DC, curses.KEY_BACKSPACE]:
            curstr = curstr[:-1]
        is_valid, errorstr = is_valid_move(state, move)
    return [int(y) for y in move.split(',')]


def get_new_game(gui):
    """Initializes a game"""
    def get_ai(player):
        """Gets an AI value"""
        querystr = 'Is ' + player + ' player an AI (y, n, q to quit)?\n'
        gui['inputbar'].clear()
        gui['inputbar'].addstr(querystr)
        gui['inputbar'].refresh()
        while True:
            nextchr = gui['inputbar'].getkey()
            if nextchr == 'q':
                exit()
            elif nextchr == 'y':
                return True
            elif nextchr == 'n':
                return False
        return False
    querystr = 'How many dimensions will your next game be (q to quit)?\n'
    gui['inputbar'].clear()
    gui['inputbar'].addstr(querystr)
    gui['inputbar'].refresh()
    curstr = ''
    gamedim = ''
    while not is_int(gamedim):
        nextchr = gui['inputbar'].getkey()
        if nextchr in ('\n', '\r', curses.KEY_ENTER):
            gamedim = curstr
        elif nextchr == 'q':
            exit()
        elif nextchr in ['1', '2', '3', '4', '5',
                         '6', '7', '8', '9', '0']:
            curstr += nextchr
        elif nextchr in ['\b', '\x7f',
                         curses.KEY_DC, curses.KEY_BACKSPACE]:
            curstr = curstr[:-1]
        gui['inputbar'].clear()
        gui['inputbar'].addstr(querystr+curstr)
        gui['inputbar'].refresh()
    gamedim = int(gamedim)
    xai = get_ai('X')
    oai = get_ai('O')
    return (gamedim, xai, oai), gui


def create_windows(stdscr):
    """Create the gamepad and input bar"""
    maxpadx = 1000
    maxpady = 1000
    gamepad = curses.newpad(maxpady, maxpadx)
    inputbar = curses.newwin(2, curses.COLS - 1,
                             curses.LINES - 3, 0)
    inputbar.leaveok(True)
    mainheight = curses.LINES - 3
    mainwidth = curses.COLS - 1
    return {'gamepad': gamepad,
            'inputbar': inputbar,
            'mainheight': mainheight - 1,
            'mainwidth': mainwidth - 1,
            'maxpadx': maxpadx,
            'maxpady': maxpady,
            'curpadx': 0,
            'curpady': 0,
            'cornerx': 0,
            'cornery': 0,
            'stdscr': stdscr,
            'inputmessage': '',
            'moves': {}}


def move_main_window(gui, key):
    """Move the pad view around"""
    curwinx = gui['curpadx'] - gui['cornerx']
    curwiny = gui['curpady'] - gui['cornery']
    if key in (curses.ACS_RARROW, 'C'):
        if curwinx == gui['mainwidth'] and (gui['cornerx'] +
                                            gui['mainwidth'] <
                                            gui['maxpadx']):
            gui['cornerx'] += 1
        elif curwinx < gui['mainwidth']:
            gui['curpadx'] += 1
    elif key in (curses.ACS_LARROW, 'D'):
        if curwinx == 0 and gui['cornerx'] > 0:
            gui['cornerx'] -= 1
        elif curwinx > 0:
            gui['curpadx'] -= 1
    elif key in (curses.ACS_DARROW, 'B'):
        if curwiny == gui['mainheight'] and (gui['cornery'] +
                                             gui['mainheight'] <
                                             gui['maxpady']):
            gui['cornery'] += 1
        elif curwiny < gui['mainheight']:
            gui['curpady'] += 1
    elif key in (curses.ACS_UARROW, 'A'):
        if curwiny == 0 and gui['cornery'] > 0:
            gui['cornery'] -= 1
        elif curwiny > 0:
            gui['curpady'] -= 1
    gui['gamepad'].refresh(gui['cornery'], gui['cornerx'],
                           0, 0,
                           gui['mainheight'], gui['mainwidth'])
    gui['gamepad'].move(gui['curpady'], gui['curpadx'])
    curses.setsyx(gui['curpady'], gui['curpadx'])
    gui['gamepad'].syncup()
    gui['gamepad'].refresh(gui['cornery'], gui['cornerx'],
                           0, 0,
                           gui['mainheight'], gui['mainwidth'])
    return gui


def take_move(state, gui):
    """Get the next move"""
    if state.player == 'X':
        if state.xai:
            newmove = get_ai_move(state)
        else:
            newmove = get_next_player_move(state, gui)
        state = State(state.ndim,
                      (state.xes+[newmove], state.oes),
                      'O',
                      (state.xai, state.oai))
    else:
        if state.oai:
            newmove = get_ai_move(state)
        else:
            newmove = get_next_player_move(state, gui)
        state = State(state.ndim,
                      (state.xes, state.oes+[newmove]),
                      'X',
                      (state.xai, state.oai))
    state.print_to_screen(gui)
    return state


def display_input(instring, gui):
    """Display message in input bar and wait for return to continue"""
    gui['inputbar'].clear()
    gui['inputbar'].addstr(instring + '\nPress ENTER to take next move' +
                           '("q" to quit). You will not be able to move ' +
                           'around board while taking your move...')
    gui['inputbar'].refresh()
    nextchr = ''
    while nextchr not in ('\n', '\r', curses.KEY_ENTER):
        nextchr = gui['inputbar'].getkey()
        if nextchr in (curses.ACS_LARROW,
                       curses.ACS_RARROW,
                       curses.ACS_UARROW,
                       curses.ACS_DARROW, 'B', 'C', 'D', 'A'):
            gui = move_main_window(gui, nextchr)
        elif nextchr == 'q':
            exit()
        gui = move_main_window(gui, '')
    return gui


def next_move(state, gui, printstr):
    """Manipulate the GUI between moves"""
    gui = display_input(printstr, gui)
    return take_move(state, gui)


def main(stdscr):
    """Actually run the game"""
    gui = create_windows(stdscr)
    while True:
        # Clear screen
        newrules, gui = get_new_game(gui)
        state = State(newrules[0],
                      ([], []),
                      'X',
                      (newrules[1], newrules[2]))
        state.print_to_screen(gui)
        while True:
            printstr, victor = state.has_victor()
            if victor:
                gui = display_input(printstr, gui)
                break
            state = next_move(state, gui, printstr)


if __name__ == "__main__":
    curses.wrapper(main)
