import copy
import itertools

import search
import random
import math
import json

ids = ["206202384", "204864532"]


class TaxiProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""

        # map_shape = (len(initial['map']), len(initial['map'][0]))
        # self.num_rows, self.num_cols = map_shape
        # self.map = initial['map']
        # self.number_of_taxis = len(initial['taxis'])
        # self.number_of_passengers = len(initial['passengers'])
        # self.taxis = list(initial['taxis'].keys())
        # self.passengers = list(initial['passengers'].keys())

        # taxis_locations = []
        # for i in range(self.number_of_taxis):
        #     taxis_locations.append(initial['taxis'][self.taxis[i]]['location'])
        #
        # passengers_locations = []
        # for i in range(self.number_of_passengers):
        #     passengers_locations.append(initial['passengers'][self.passengers[i]]['location'])

        for taxi in list(initial['taxis'].keys()):
            initial['taxis'][taxi]['max_fuel'] = initial['taxis'][taxi]['fuel']
            initial['taxis'][taxi]['passenger aboard'] = 0

        for passenger in list(initial['passengers'].keys()):
            initial['passengers'][passenger]['taxi name'] = None

        state = {
            'map': initial['map'],
            'taxis': initial['taxis'],
            'passengers': initial['passengers'],
            'num_rows': len(initial['map']),
            'num_cols': len(initial['map'][0]),
            'number_of_taxis': len(initial['taxis']),
            'number_of_passengers': len(initial['passengers']),
            'taxis_names': list(initial['taxis'].keys()),
            'passengers_names': list(initial['passengers'].keys()),
            'goal_test_counter': 0
        }

        state = json.dumps(state)
        # build new initial dictionary with new props
        search.Problem.__init__(self, state)

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

        state = copy.deepcopy(state)
        state = json.loads(state)
        taxis = [(k, v) for k, v in state['taxis'].items()]
        # i.e. taxis = [('taxi 1', {'location': (3, 3), 'fuel': 15, 'capacity': 2})]
        all_actions = []
        for taxi in taxis:
            taxi_name = taxi[0]
            taxi_location = taxi[1]['location']
            taxi_fuel = taxi[1]['fuel']
            taxi_capacity = taxi[1]['capacity']
            temp = self.check_actions(state, taxi_name, taxi_location, taxi_fuel, taxi_capacity)
            all_actions.append(tuple(temp))

        all_actions = all_actions
        all_actions = tuple(itertools.product(*all_actions))
        # print(all_actions)
        state = json.dumps(state)
        for act in all_actions:
            yield act
            # i.e. act = (('wait', 'taxi 1'),)

    def check_actions(self, state, taxi_name, taxi_location, taxi_fuel, taxi_capacity):
        '''
        return a list of tuples represents all possible actions for a taxi.
        i.e: [(“move”, “taxi 1”, (1, 2)), (“wait”, “taxi 1”), ("refuel", "taxi 1")]
        '''
        M = state['num_rows']
        N = state['num_cols']
        x, y = taxi_location
        actions = []
        taxis_locations = []
        number_of_taxis = state['number_of_taxis']
        for i in range(number_of_taxis):
            taxis_locations.append(state['taxis'][state['taxis_names'][i]]['location'])

        passengers_locations = []
        number_of_passengers = state['number_of_passengers']
        for i in range(number_of_passengers):
            passengers_locations.append(state['passengers'][state['passengers_names'][i]]['location'])

        # add the wait action
        actions.append(('wait', taxi_name))

        # check for refuel
        if state['map'][x][y] == 'G':
            actions.append(('refuel', taxi_name))

        # check if out of fuel
        if taxi_fuel <= 0:
            return actions

        # check for move actions
        # can go up
        if x - 1 >= 0 and state['map'][x - 1][y] != 'I' and (x - 1, y) not in taxis_locations:
            actions.append(('move', taxi_name, (x - 1, y)))

        # can go down
        if x + 1 < M and state['map'][x + 1][y] != 'I' and (x + 1, y) not in taxis_locations:
            actions.append(('move', taxi_name, (x + 1, y)))

        # can go left
        if y - 1 >= 0 and state['map'][x][y - 1] != 'I' and (x, y - 1) not in taxis_locations:
            actions.append(('move', taxi_name, (x, y - 1)))

        # can go right
        if y + 1 < N and state['map'][x][y + 1] != 'I' and (x, y + 1) not in taxis_locations:
            actions.append(('move', taxi_name, (x, y + 1)))

        # check for pick-up actions
        if taxi_location in passengers_locations and taxi_capacity > 0:
            passenger_name = self.check_passenger_for_pickup(state, taxi_location)
            actions.append(('pick up', taxi_name, passenger_name))

        # check for drop-off actions
        passenger_name_at_destination = self.check_passenger_for_dropoff(state, taxi_location)
        if passenger_name_at_destination is not None:
            actions.append(('drop off', taxi_name, passenger_name_at_destination))

        return actions

    def check_passenger_for_pickup(self, state, cords):
        '''
        check if there is a passenger on the specified cords
        '''
        passengers = state['passengers_names']
        passengers_locations = []
        number_of_passengers = state['number_of_passengers']
        for i in range(number_of_passengers):
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

    def check_passenger_for_dropoff(self, state, cords):
        '''
        return the passenger name if he is at his destination
        '''
        passengers = state['passengers_names']
        passengers_locations = []
        number_of_passengers = state['number_of_passengers']
        for i in range(number_of_passengers):
            passengers_locations.append(state['passengers'][passengers[i]]['location'])

        passengers_destinations = []
        for i in range(number_of_passengers):
            passengers_destinations.append(state['passengers'][passengers[i]]['destination'])

        passengers_and_their_locations = zip(passengers, passengers_locations)
        passengers_and_their_destinations = zip(passengers, passengers_destinations)
        # i.e. [('Yossi', (0, 0)), ('Moshe', (3, 1))]
        # so, passengers_and_their_locations[0] = ('Yossi', (0, 0))

        passenger_name1, passenger_name2 = None, None

        for passenger in passengers_and_their_locations:
            if cords in passenger:
                passenger_name1 = passenger[0]

        for passenger in passengers_and_their_destinations:
            if cords in passenger:
                passenger_name2 = passenger[0]

        if passenger_name1 is not None and passenger_name2 is not None:
            if passenger_name1 == passenger_name2 and state['passengers'][passenger_name1]['taxi name'] is not None:
                return passenger_name1

        return None

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        # i.e. if the action tells us to move taxi 1 to (1,2) we need to update
        # the state accordingly- decrease the taxi fuel and update its location in the state dict.
        # when pick-up or drop-off update the capacity.

        state = copy.deepcopy(state)
        state = json.loads(state)
        # check how it should look like if there is only 1 taxi
        for act in action:
            taxi_name = act[1]
            taxi_action = act[0]
            if len(act) == 2:
                if taxi_action == 'wait':
                    continue
                elif taxi_action == 'refuel':
                    state['taxis'][taxi_name]['fuel'] = state['taxis'][taxi_name]['max_fuel']
            elif len(act) == 3:
                passenger_name = act[2]
                if taxi_action == 'move':
                    cords = act[2]
                    state['taxis'][taxi_name]['fuel'] -= 1
                    state['taxis'][taxi_name]['location'] = cords
                    if state['taxis'][taxi_name]['passenger aboard'] > 0:
                        for passenger in state['passengers']:
                            if state['passengers'][passenger]['taxi name'] == taxi_name:
                                state['passengers'][passenger]['location'] = cords
                elif taxi_action == 'pick up':
                    state['taxis'][taxi_name]['passenger aboard'] += 1
                    state['passengers'][passenger_name]['taxi name'] = taxi_name
                    state['taxis'][taxi_name]['capacity'] -= 1
                elif taxi_action == 'drop off':
                    state['taxis'][taxi_name]['passenger aboard'] -= 1
                    state['passengers'][passenger_name]['location'] = state['passengers'][passenger_name]['destination']
                    state['passengers'][passenger_name]['taxi name'] = None
                    state['goal_test_counter'] += 1
                    state['taxis'][taxi_name]['capacity'] += 1

        return json.dumps(state)

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        state = copy.deepcopy(state)
        state = json.loads(state)

        if state['goal_test_counter'] == state['number_of_passengers']:
            state = json.dumps(state)
            return True
        state = json.dumps(state)
        return False

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
