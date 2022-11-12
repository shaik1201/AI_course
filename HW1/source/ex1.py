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

        print("building a TaxiProblem")
        map_shape = (len(initial[map]), len(initial[map][0]))
        self.num_rows, self.num_cols = map_shape
        self.map = initial['map']
        self.number_of_taxis = len(initial['taxis'])
        self.number_of_passengers = len(initial['passengers'])
        self.taxis = list(initial['taxis'].keys())
        self.passengers = list(initial['passengers'].keys())

        self.taxis_locations = []
        for i in range(self.number_of_taxis):
            self.taxis_locations.append(initial['taxis'][self.taxis[i]]['location'])

        self.passengers_locations = []
        for i in range(self.number_of_passengers):
            self.passengers_locations.append(initial['passengers'][self.passengers[i]]['location'])

        # build new initial dictionary with new props
        search.Problem.__init__(self, initial)

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""

        # return tuple of tuples of actions for each taxi
        # loop over all taxis, check every action for each one and save all the possible
        # combinations (cartesian multiplication).

        # length of all_actions is the number of taxis

        # NOTE: check what the actions should look a like. i.e. is it ok to be a list
        # which each entry of it is a list contains tuples of actions of a taxi?
        taxis = [(k, v) for k, v in state['taxis'].items()]
        # i.e. taxis = [('taxi 1', {'location': (3, 3), 'fuel': 15, 'capacity': 2})]
        all_actions = []
        for taxi in taxis:
            taxi_name = taxi[0]
            taxi_location = taxi[1]['location']
            taxi_fuel = taxi[1]['fuel']
            taxi_capacity = taxi[1]['capacity']
            all_actions.append(self.check_actions(state, taxi_name, taxi_location, taxi_fuel,
                                                  taxi_capacity))

    def check_actions(self, state, taxi_name, taxi_location, taxi_fuel, taxi_capacity):
        '''
        return a list of tuples represents all possible actions for a taxi.
        i.e: [(“move”, “taxi 1”, (1, 2)), (“wait”, “taxi 1”), ("refuel", "taxi 1")]
        '''
        M = self.num_rows
        N = self.num_cols
        actions = []

        # following code doesn't check for drop off and refuel (each block needs to check these actions).
        # also, do we need to update
        # something in addition to adding to the actions list?
        # i.e. lowering the taxi fuel when making a move.

        # left up corner - can go R or D
        if taxi_location[0] == 0 and taxi_location[1] == 0:
            if state['map'][0][1] == 'P' and taxi_fuel > 0 and taxi_capacity > 0:
                actions.append(('move', taxi_name, (0, 1)))
            if state['map'][1][0] == 'P' and taxi_fuel > 0 and taxi_capacity > 0:
                actions.append(('move', taxi_name, (1, 0)))
            passenger_name_on_tile = self.check_passenger(state, (0, 0))
            if taxi_fuel > 0 and taxi_capacity > 0 and passenger_name_on_tile is not None:
                actions.append(('pick up', taxi_name, passenger_name_on_tile))

        # right down corner - can go U or L
        elif taxi_location[0] == M and taxi_location[1] == N:
            if state['map'][M - 1][N] == 'P' and taxi_fuel > 0 and taxi_capacity > 0:
                actions.append(('move', taxi_name, (M - 1, N)))
            if state['map'][M][N - 1] == 'P' and taxi_fuel > 0 and taxi_capacity > 0:
                actions.append(('move', taxi_name, (M, N - 1)))
            passenger_name_on_tile = self.check_passenger(state, (M, N))
            if taxi_fuel > 0 and taxi_capacity > 0 and passenger_name_on_tile is not None:
                actions.append(('pick up', taxi_name, passenger_name_on_tile))

        # right up corner - can go D or L
        elif taxi_location[0] == 0 and taxi_location[1] == N:
            if state['map'][M + 1][N] == 'P' and taxi_fuel > 0 and taxi_capacity > 0:
                actions.append(('move', taxi_name, (M + 1, N)))
            if state['map'][M][N - 1] == 'P' and taxi_fuel > 0 and taxi_capacity > 0:
                actions.append(('move', taxi_name, (M, N - 1)))
            passenger_name_on_tile = self.check_passenger(state, (0, N))
            if taxi_fuel > 0 and taxi_capacity > 0 and passenger_name_on_tile is not None:
                actions.append(('pick up', taxi_name, passenger_name_on_tile))

        # left down corner - can go U or R
        elif taxi_location[0] == M and taxi_location[1] == 0:
            if state['map'][M - 1][0] == 'P' and taxi_fuel > 0 and taxi_capacity > 0:
                actions.append(('move', taxi_name, (M - 1, 0)))
            if state['map'][M][N + 1] == 'P' and taxi_fuel > 0 and taxi_capacity > 0:
                actions.append(('move', taxi_name, (M, N + 1)))
            passenger_name_on_tile = self.check_passenger(state, (M, 0))
            if taxi_fuel > 0 and taxi_capacity > 0 and passenger_name_on_tile is not None:
                actions.append(('pick up', taxi_name, passenger_name_on_tile))

    def check_passenger(self, state, cords):
        '''
        check if there is a passenger on the specified cords
        '''
        passengers = self.passengers
        passengers_locations = []
        for i in range(self.number_of_passengers):
            passengers_locations.append(state['passengers'][passengers[i]]['location'])

        passengers_and_their_locations = zip(passengers, passengers_locations)
        # i.e. [('Yossi', (0, 0)), ('Moshe', (3, 1))]
        # so, passengers_and_their_locations[0] = ('Yossi', (0, 0))

        for passenger in passengers_and_their_locations:
            if cords in passenger:
                passenger_name = passenger[0]
                # return the first passenger on the tile
                return passenger_name
        return None

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        # i.e. if the action tells us to move taxi 1 to (1,2) we need to update
        # the state accordingly- decrease the taxi fuel and update its location in the state dict.

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
