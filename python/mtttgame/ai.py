""" Determines what the AI does relies on randomness, so is impure """
from random import random, choices, sample
from copy import copy
import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
from state import State


def dumb_lookahead(state):
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


class RNN2(nn.Module):
    """Recurrent neural network for AI value generation"""
    def __init__(self, hiddensize=128, intermediatesize=128):
        """Initialize the network"""
        super(RNN2, self).__init__()

        self.hidden_size = hiddensize
        self.inter_size = intermediatesize
        self.i2h1 = nn.Linear(9 + self.hidden_size, self.inter_size)
        self.h12c = nn.Linear(self.inter_size, self.hidden_size)
        self.c2h2 = nn.Linear(self.hidden_size, self.inter_size)
        self.h22o = nn.Linear(self.inter_size, 9 + self.hidden_size)
        self.relu = nn.ReLU()

    def forward(self, myinput):
        """Define the forward progress through the network"""
        outputshape = myinput.shape
        hidden1s = [self.init_hidden()]
        for curspaces in torch.split(myinput, 9, 1):
            curinput = torch.cat((curspaces, hidden1s[-1]), 1)
            hidden1s.append(self.i2h1(curinput))
            hidden1s.append(self.relu(hidden1s[-1]))
            hidden1s.append(self.h12c(hidden1s[-1]))

        outputs = [Variable(torch.FloatTensor(0, 1))]
        hidden2s = [hidden1s[-1]]
        while outputs[-1].shape != outputshape:
            hidden2s.append(self.c2h2(hidden2s[-1]))
            hidden2s.append(self.relu(hidden2s[-1]))
            hidden2s.append(self.h22o(hidden2s[-1]))
            try:
                outputs[-1] = torch.cat((outputs[-1],
                                         hidden2s[-1][:,:9]))
            except RuntimeError:
                outputs[-1] = hidden2s[-1][:,:9]
            hidden2s.append(hidden2s[-1][:,9:])
        return outputs[-1]

    def init_hidden(self):
        return Variable(torch.zeros(1, self.hidden_size))


class RNN(nn.Module):
    """Recursive neural network for AI value generation"""
    def __init__(self, hiddensize=128):
        """Initialize the network"""
        super(RNN, self).__init__()

        self.hidden_size = hiddensize
        self.i2h1 = nn.Linear(9, self.hidden_size)
        self.h12c = nn.Linear(self.hidden_size, 3)
        self.c2h2 = nn.Linear(3, self.hidden_size)
        self.h22o = nn.Linear(self.hidden_size, 9)
        self.relu = nn.ReLU()

    def forward(self, myinput):
        """Define the forward progress through the network"""
        outputshape = myinput.shape
        inputs = [myinput]
        hidden1s = []
        while inputs[-1].shape != torch.Size([1, 3]):
            inputs.append(Variable(torch.FloatTensor(0)))
            for curinput in torch.split(inputs[-2], 9, 1):
                hidden1s.append(self.i2h1(curinput))
                hidden1s.append(self.relu(hidden1s[-1]))
                try:
                    inputs[-1] = torch.cat([inputs[-1],
                                            self.h12c(hidden1s[-1])],
                                           1)
                except RuntimeError:
                    inputs[-1] = self.h12c(hidden1s[-1])

        outputs = [inputs[-1]]
        hidden2s = []
        while outputs[-1].shape != outputshape:
            outputs.append(Variable(torch.FloatTensor(0)))
            for curinput in torch.split(outputs[-2], 3, 1):
                hidden2s.append(self.c2h2(curinput))
                hidden2s.append(self.relu(hidden2s[-1]))
                try:
                    outputs[-1] = torch.cat([outputs[-1],
                                             self.h22o(hidden2s[-1])],
                                            1)
                except RuntimeError as e:
                    outputs[-1] = self.h22o(hidden2s[-1])
        return outputs[-1]


class deep_learning_ai():
    """Code for using a deep neural network to generate
       value matrix"""
    def __init__(self, rnn_type=1):
        if rnn_type == 1:
            try:
                self.my_rnn = RNN()
                self.my_rnn.load_state_dict(torch.load('deepmodel.dic'))
            except FileNotFoundError:
                self.my_rnn = RNN()
                self.initial_train()
        elif rnn_type == 2:
            try:
                self.my_rnn = RNN2()
                self.my_rnn.load_state_dict(torch.load('deepmodel2.dic'))
            except FileNotFoundError:
                self.my_rnn = RNN2()
                self.initial_train()
        self.previous_moves = []
        self.rnn_type = rnn_type

    def get_input_vectors(self, state, curdimtrace):
        """Recursively create input vectors which take the form of a single
           vector that contains the results of walking through each dimension
           """

        if len(curdimtrace) == state.ndim - 1:
            if state.player == 'X':
                mymoves = state.xes
                enemymoves = state.oes
            else:
                mymoves = state.oes
                enemymoves = state.xes
            vector = []
            for i in (0, 1, 2):
                if [i] + curdimtrace in mymoves:
                    vector.append(1)
                elif [i] + curdimtrace in enemymoves:
                    vector.append(-1)
                else:
                    vector.append(0)
            return torch.Tensor([vector])
        return torch.cat([self.get_input_vectors(state,
                                                 [0] + curdimtrace),
                          self.get_input_vectors(state,
                                                 [1] + curdimtrace),
                          self.get_input_vectors(state,
                                                 [2] + curdimtrace)],
                         1)

    def get_values(self, state, inputs):
        """Use the RNN to get values for the current state"""
        def assign_values(curvalues, curdimtrace, ndim):
            """Create a list of space, value pairs"""
            if len(curdimtrace) == ndim:
                return [(curdimtrace, curvalues[0])]
            splitvalues = curvalues.chunk(3)
            return (assign_values(splitvalues[0],
                                  [0] + curdimtrace,
                                  ndim) +
                    assign_values(splitvalues[1],
                                  [1] + curdimtrace,
                                  ndim) +
                    assign_values(splitvalues[2],
                                  [2] + curdimtrace,
                                  ndim))
        values = self.my_rnn(inputs)
        return assign_values(values.data[0], [], state.ndim)

    def initial_train(self):
        """Generates exact values for 2d tic-tac-toe and
           fits model to those values"""
        def create_transmap(currentmap):
            """Convert a sequence of 9 into possible 3-in-a-rows"""
            return [currentmap[:3],
                    currentmap[3:6],
                    currentmap[6:9],
                    currentmap[6:9],
                    [currentmap[0],
                     currentmap[3],
                     currentmap[6]],
                    [currentmap[1],
                     currentmap[4],
                     currentmap[7]],
                    [currentmap[2],
                     currentmap[5],
                     currentmap[8]],
                    [currentmap[0],
                     currentmap[4],
                     currentmap[8]],
                    [currentmap[2],
                     currentmap[4],
                     currentmap[6]]]

        def iswin(currentmap):
            """Check if any possible 3-in-a-row is filled by the player"""
            transmap = create_transmap(currentmap)
            for curmap in transmap:
                if curmap == [1, 1, 1]:
                    return True
            return False

        def islose(currentmap):
            """Check if any possible 3-in-a-row is filled by the opponent"""
            transmap = create_transmap(currentmap)
            for curmap in transmap:
                if curmap == [-1, -1, -1]:
                    return True
            return False

        def create_state_value_maps(currentmap, curturn):
            """Recursively generate all possible values for 2d tic-tac-toe"""
            print(currentmap)
            outputs = []
            myvalue = []
            if iswin(currentmap):
                return [], 5.0
            elif islose(currentmap):
                return [], -10.0
            for i in range(9):
                if currentmap[i] not in (-1, 1):
                    newmap = list(currentmap)
                    newmap[i] = curturn
                    newmap = tuple(newmap)
                    output, newvalue = create_state_value_maps(newmap,
                                                               curturn *
                                                               -1)
                    outputs += output
                    myvalue.append(newvalue)
                else:
                    myvalue.append(0.0)
            outputs.append((currentmap, tuple(myvalue)))
            return outputs, sum(myvalue)/9

        def update(mysv):
            """Run a forward iteration through the current network"""
            self.my_rnn.zero_grad()
            inputs = mysv[0]
            outputs = self.my_rnn(inputs)
            loss = criterion(outputs, mysv[1])
            loss.backward()

            for parameter in self.my_rnn.parameters():
                parameter.data.add_(-0.005, parameter.grad.data)

            return outputs, loss[0]

        output1 = dict(create_state_value_maps((0, 0, 0,
                                                0, 0, 0,
                                                0, 0, 0), 1)[0])
        output2 = dict(create_state_value_maps((0, 0, 0,
                                                0, 0, 0,
                                                0, 0, 0), -1)[0])
        values = {}
        for key in set(list(output1) + list(output2)):
            try:
                o1 = output1[key]
                o2 = output2[key]
                values[key] = tuple([(o1[i] + o2[i])/2.0 for i in range(9)])
            except KeyError:
                try:
                    values[key] = output1[key]
                except KeyError:
                    values[key] = output2[key]
        values = [(Variable(torch.FloatTensor([key]), requires_grad=True),
                   Variable(torch.FloatTensor([values[key]])))
                  for key in values]

        criterion = nn.MSELoss()
        i = 0
        losses = []
        for sv in choices(values, k=1000000):
            i += 1
            output, loss = update(sv)
            losses.append(loss.data[0])
            if i % 500 == 0:
                print(str((i*100)/1000000.0) + '% done: Mean Current loss = '
                      + str(sum(losses)/500.0))
                losses = []
        if self.rnn_type == 1:
            torch.save(self.my_rnn.state_dict(), 'deepmodel.dic')
        elif self.rnn_type == 2:
            torch.save(self.my_rnn.state_dict(), 'deepmodel2.dic')

    def learning(self, remaining_moves, reward, ndim):
        def get_output_vectors(curtrace, curdimtrace, ndim):
            """Recursively create output vectors"""
            if len(curdimtrace) == ndim - 1:
                vector = []
                for i in (0, 1, 2):
                    if [i] + curdimtrace == curtrace:
                        vector.append(1)
                    else:
                        vector.append(0)
                return torch.Tensor([vector])
            return torch.cat([get_output_vectors(curtrace,
                                                 [0] + curdimtrace,
                                                 ndim),
                              get_output_vectors(curtrace,
                                                 [1] + curdimtrace,
                                                 ndim),
                              get_output_vectors(curtrace,
                                                 [2] + curdimtrace,
                                                 ndim)],
                             1)

        def update(mysv):
            """Run a forward iteration through the current network"""
            self.my_rnn.zero_grad()
            inputs = mysv[0]
            outputs = self.my_rnn(inputs)
            gold = Variable(torch.add(outputs.data, mysv[1]),
                            requires_grad=False)
            loss = criterion(outputs, gold)
            loss.backward()

            for parameter in self.my_rnn.parameters():
                parameter.data.add_(-0.001, parameter.grad.data)

            return outputs, loss[0]

        criterion = nn.MSELoss()
        if remaining_moves:
            nextmove = remaining_moves.pop(-1)
            newvalues = (get_output_vectors(nextmove[2],
                                            [], ndim) * reward)
            update((nextmove[1], newvalues))
            self.learning(remaining_moves, reward * 0.9, ndim)

    def check_for_reward(self, state):
        prev_state = self.previous_moves[-1][0]
        if state.player == 'X':
            myscore, theirscore = state.get_scores()
            myscore_prev, theirscore_prev = prev_state.get_scores()
        else:
            theirscore, myscore = state.get_scores()
            theirscore_prev, myscore_prev = prev_state.get_scores()
        if myscore > myscore_prev:
            self.learning(self.previous_moves, 2, state.ndim)
        if theirscore > theirscore_prev:
            self.learning(self.previous_moves, -4, state.ndim)

    def choose_move(self, state, greedye=0.1):
        """use the value matrix to select a move"""
        if self.previous_moves:
            self.check_for_reward(state)
        inputs = Variable(self.get_input_vectors(state, []))
        with open('debug.txt', 'a') as debugfile:
            debugfile.write(str(inputs) + '\n')
        values = self.get_values(state, inputs)
        values = sorted([tup for tup in values
                         if (tup[0] not in state.xes and
                             tup[0] not in state.oes)],
                        key=lambda x: -x[1])
        myq = random()
        if myq > greedye:
            choice = values[0][0]
        else:
            choice = sample(values, k=1)[0][0]
        self.previous_moves.append((state, inputs, choice))
        return choice
