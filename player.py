"""
This program adopts some amended part of sample solution of project 1
Author: Luoming Zhang 898306
"""

import copy
from .pq_max import PriorityQueue

_STARTING_HEXES = {
    'r': {(-3, 3), (-3, 2), (-3, 1), (-3, 0)},
    'g': {(0, -3), (1, -3), (2, -3), (3, -3)},
    'b': {(3, 0), (2, 1), (1, 2), (0, 3)},
}

_NEXT_COLOUR = {
    'red': 'green',
    'green': 'blue',
    'blue': 'red'
}

_PREV_COLOUR = {
    'red': 'blue',
    'green': 'red',
    'blue': 'green'
}

_INIT_P = {'red': 0,
           'green': 0,
           'blue': 0}

PLAYERS = 3

# The max point can get in each round
MAXP = 4


class ExamplePlayer:
    def __init__(self, colour):
        """
        This method is called once at the beginning of the game to initialise
        your player. You should use this opportunity to set up your own internal
        representation of the game state, and any other information about the
        game state you would like to maintain for the duration of the game.

        The parameter colour will be a string representing the player your
        program will play as (Red, Green or Blue). The value will be one of the
        strings "red", "green", or "blue" correspondingly.
        """
        # TODO: Set up state representation.

        self.colour = colour
        self.board = Board(colour)

    def action(self):
        """
        This method is called at the beginning of each of your turns to request
        a choice of action from your program.

        Based on the current state of the game, your player should select and
        return an allowed action to play on this turn. If there are no allowed
        actions, your player must return a pass instead. The action (or pass)
        must be represented based on the above instructions for representing
        actions.
        """
        # TODO: Decide what action to take.

        state = State(self.colour, self.board, None, None, _INIT_P)
        return max_n(state)
        # return ("PASS", None)

    def update(self, colour, action):
        """
        This method is called at the end of every turn (including your player’s
        turns) to inform your player about the most recent action. You should
        use this opportunity to maintain your internal representation of the
        game state and any other information about the game you are storing.

        The parameter colour will be a string representing the player whose turn
        it is (Red, Green or Blue). The value will be one of the strings "red",
        "green", or "blue" correspondingly.

        The parameter action is a representation of the most recent action (or
        pass) conforming to the above in- structions for representing actions.

        You may assume that action will always correspond to an allowed action
        (or pass) for the player colour (your method does not need to validate
        the action/pass against the game rules).
        """
        # TODO: Update state representation in response to action.

        self.board.update(colour, action)


def max_n(initial_state):
    """
    use depth-first exploration and amended shallow pruning
    """
    queue = PriorityQueue()

    for state1 in initial_state.actions_successors():
        # the point of initial state's successor after actions
        p = state1.point[initial_state.colour]
        for state2 in state1.actions_successors():
            for state3 in state2.actions_successors():
                state2.queue.update(state3, state3.point[state2.colour])

            max_state3 = state2.queue.extract_max()
            state2.point = max_state3.point
            state1.queue.update(state2, state2.point[state1.colour])

        max_state2 = state1.queue.extract_max()
        state1.point = max_state2.point
        # if initial state's successor's point is max point
        # and the updated after other players' action is still max point
        # player can't get any better than this action, return this action
        if state1.point[initial_state.colour] == MAXP and p == MAXP:
            return state1.action
        queue.update(state1, state1.point[initial_state.colour])

    max_move = queue.extract_max()

    return max_move.action


def exit_dist(qr, colour):
    """the Manhattan distance of a coordinate to the nearest exiting hex"""
    q, r = qr
    if colour == 'red':
        return 3 - q
    if colour == 'green':
        return 3 - r
    if colour == 'blue':
        return 3 - (-q - r)


class Board:

    def __init__(self, colour):

        self.colour = colour

        if colour == 'red':
            self.exit_hexes = {(3, -3), (3, -2), (3, -1), (3, 0)}

        if colour == 'green':
            self.exit_hexes = {(-3, 3), (-2, 3), (-1, 3), (0, 3)}

        if colour == 'blue':
            self.exit_hexes = {(-3, 0), (-2, -1), (-1, -2), (0, -3)}

        self.board_dict = {'red': frozenset(_STARTING_HEXES['r']),
                           'green': frozenset(_STARTING_HEXES['g']),
                           'blue': frozenset(_STARTING_HEXES['b'])}

        ran = range(-3, +3 + 1)
        self.all_hexes = {(q, r) for q in ran for r in ran if -q - r in ran}

    def can_exit_from(self, qr):
        """can a piece exit the board from this hex?"""
        return qr in self.exit_hexes

    def is_blocked(self, qr):
        """is this hex occupied by a block?"""
        for key in self.board_dict:
            if qr in self.board_dict[key]:
                return True
        return False

    def __contains__(self, qr):
        return qr in self.all_hexes

    def update(self, colour, action):
        atype, aargs = action
        if atype == 'PASS':
            return
        elif atype == 'EXIT':
            self.board_dict[colour] = self.board_dict[colour] - {aargs}

        else:  # if atype == 'MOVE' or atype == 'JUMP':
            self.board_dict[colour] = self.board_dict[colour] - {aargs[0]} | {aargs[1]}
            if atype == 'JUMP':
                middle = tuple(map(lambda x, y: int((x + y) / 2), aargs[0], aargs[1]))
                for key, val in self.board_dict.items():
                    self.board_dict[key] = self.board_dict[key] - {middle}
                self.board_dict[colour] = self.board_dict[colour] | {middle}


# These are the directions in which moves/jumps are allowed in the game:
HEX_STEPS = [(-1, +0), (+0, -1), (+1, -1), (+1, +0), (+0, +1), (-1, +1)]


class State:

    def __init__(self, colour, board, action, prev_state, point):
        self.board = board
        self.colour = colour
        self.next_colour = _NEXT_COLOUR[colour]
        self.prev_colour = _PREV_COLOUR[colour]
        self.piece_hexes = board.board_dict[colour]
        self.action = action
        self.prev_state = prev_state

        self.point = point
        self.queue = PriorityQueue()

    def actions_successors(self):
        """
        construct and return a list of all actions available from this state
        (and their resulting successor states)
        """
        actions_successors_list = []
        for action in self._actions():
            actions_successors_list.append(self._apply(action))
        return actions_successors_list

    def _actions(self):
        """
        construct and return a list of all actions available from this state
        """
        available_actions_list = []
        for qr in self.piece_hexes:
            # consider possible exit action:
            if self.board.can_exit_from(qr):
                available_actions_list.append(('EXIT', qr))

            q, r = qr
            for step_q, step_r in HEX_STEPS:
                for atype, dist in [('MOVE', 1), ('JUMP', 2)]:
                    qr_t = q + step_q * dist, r + step_r * dist  # qr_t = 'target' hex
                    if qr_t in self.board:
                        if not self.board.is_blocked(qr_t):
                            available_actions_list.append((atype, (qr, qr_t)))
                            break  # only try to jump if the move IS blocked
                    else:
                        break  # if a move goes off the board, a jump would too
        if not available_actions_list:
            # Note that this shouldn't happen in Part A, but:
            available_actions_list.append(('PASS', None))
        return available_actions_list

    def _apply(self, action):
        """
        compute and return the state resulting from taking a particular action
        in this state
        """
        new_board = Board(self.next_colour)
        new_board.board_dict = copy.deepcopy(self.board.board_dict)
        new_board.update(self.colour, action)

        return State(self.next_colour, new_board, action, self, point_cal(self, action))

    def is_goal(self):
        """Goal test: The game is won when all pieces have exited."""
        return not self.piece_hexes

    # we need to store states in sets and dictionaries, so we had better make
    # them behave well with hashing and equality checking:
    def __eq__(self, other):
        """
        states should compare equal if they have the same pieces
        (all states should share an underlying board in our program, so
        there's no need to check that)
        """
        return self.board.board_dict == other.board.board_dict

    def __hash__(self):
        """
        likewise, we should only consider the set of pieces relevant when
        computing a hash value for a state
        """
        return hash(self.piece_hexes)


def point_cal(state, action):
    """
    This function is similar to Board.update, but it works for update point in class state
    """
    point = copy.deepcopy(state.point)
    colour = state.colour
    board_dict = state.board.board_dict
    atype, aargs = action
    if atype == 'PASS':
        point[colour] -= 1
    elif atype == 'EXIT':
        point[colour] += 2
    else:
        point[colour] += (exit_dist(aargs[0], colour) - exit_dist(aargs[1], colour))
        if atype == 'JUMP':
            middle = tuple(map(lambda x, y: int((x + y) / 2), aargs[0], aargs[1]))
            for key in board_dict:
                if middle in board_dict[key]:
                    if key != colour:
                        point[colour] += 2
    return point
