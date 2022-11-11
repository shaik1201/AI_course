import search
import random
import math


ids = ["206202384", "204864532"]


class TaxiProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""

        map_shape = (len(initial[map]), len(initial[map][0]))
        num_rows, num_cols = map_shape
        self.number_of_taxis = len(initial['taxis'])
        self.taxis_locations = []
        for i in range(self.number_of_taxis):
            self.taxis_locations.append(initial['taxis'][])


        search.Problem.__init__(self, initial)
        
    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""

        # return tuple of tuples of actions for each taxi
        # loop over all taxis, check every action for each one and save all the possible
        # combinations (cartesian multiplication).

        all_actions = []


        taxis_keys = list(state['taxis'].keys())
        for i in range(self.number_of_taxis):
            all_actions.append(check_possibility(state['taxis'][i]))

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return 0

    def h_1(self, node):
        """
        This is a simple heuristic
        """

    def h_2(self, node):
        """
        This is a slightly more sophisticated Manhattan heuristic
        """

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_taxi_problem(game):
    return TaxiProblem(game)

