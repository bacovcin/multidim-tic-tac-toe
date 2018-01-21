""" Determines what the AI does relies on randomness, so is impure """
from random import sample
from state import State


def get_ai_move(state):
    """ Currently implementing a standard (dumb) look ahead AI """
    def build_possible_moves(state, curdimtrace):
        """Figure out where possible moves are"""
        if len(curdimtrace) == state.ndim - 1:
            output = {}
            for i in range(3):
                newdim = [i] + curdimtrace
                if newdim in state.xes or newdim in state.oes:
                    continue
                else:
                    if state.player == 'X':
                        newstate = State(state.ndim,
                                         [[*state.xes, newdim], state.oes],
                                         'O', [state.xai, state.oai])
                    else:
                        newstate = State(state.ndim,
                                         [state.xes, [*state.oes, newdim]],
                                         'X', [state.xai, state.oai])
                    output[(tuple(newdim), newstate)] = {}
        else:
            output1 = build_possible_moves(state, [0] + curdimtrace)
            output2 = build_possible_moves(state, [1] + curdimtrace)
            output3 = build_possible_moves(state, [2] + curdimtrace)
            output = {**output1, **output2, **output3}
        return output

    def update_scores(scores, choice, scoretype, newscore):
        """Calculate score based on moves"""
        try:
            scores[choice][scoretype] += newscore
        except KeyError:
            try:
                scores[choice][scoretype] = newscore
            except KeyError:
                scores[choice] = {}
                scores[choice][scoretype] = newscore
        return scores

    choices = build_possible_moves(state, [])
    scores = {}
    for choice in choices:
        if state.remaining_moves >= 2:
            choices[choice] = build_possible_moves(choice[1], [])
            for choice2 in choices[choice]:
                if state.remaining_moves >= 3:
                    choices[choice][choice2] = build_possible_moves(choice2[1],
                                                                    [])
                    for choice3 in choices[choice][choice2]:
                        newscores = choice3[1].get_scores()
                        scores = update_scores(scores, choice,
                                               'XScore', newscores[0])
                        scores = update_scores(scores, choice,
                                               'OScore', newscores[0])
                else:
                    newscores = choice2[1].get_scores()
                    scores = update_scores(scores, choice,
                                           'XScore', newscores[0])
                    scores = update_scores(scores, choice,
                                           'OScore', newscores[0])
        else:
            newscores = choice[1].get_scores()
            scores = update_scores(scores, choice,
                                   'XScore', newscores[0])
            scores = update_scores(scores, choice,
                                   'OScore', newscores[0])

    for choice in scores:
        if state.player == 'X':
            scores[choice] = (scores[choice]['XScore'] -
                              scores[choice]['OScore'])
        else:
            scores[choice] = (scores[choice]['OScore'] -
                              scores[choice]['XScore'])
    best_choices = [list(x[0]) for x in scores
                    if scores[x] == max(scores.values())]
    return sample(best_choices, 1)[0]
