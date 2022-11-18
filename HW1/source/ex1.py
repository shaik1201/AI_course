# import copy
# import itertools
#
# import search
# import random
# import math
# import json
# import utils
# import time
# ids = ["206202384", "204864532"]
#
#
# def manhattan(a, b):
#     return sum(abs(val1 - val2) for val1, val2 in zip(a, b))
#
# def euclidean(a, b):
#     return sum([(x - y) ** 2 for x, y in zip(a, b)]) ** 0.5
#
# class TaxiProblem(search.Problem):
#     """This class implements a medical problem according to problem description file"""
#
#     def __init__(self, initial):
#         """Don't forget to implement the goal test
#         You should change the initial to your own representation.
#         search.Problem.__init__(self, initial) creates the root node"""
#
#         # map_shape = (len(initial['map']), len(initial['map'][0]))
#         # self.num_rows, self.num_cols = map_shape
#         # self.map = initial['map']
#         # self.number_of_taxis = len(initial['taxis'])
#         # self.number_of_passengers = len(initial['passengers'])
#         # self.taxis = list(initial['taxis'].keys())
#         # self.passengers = list(initial['passengers'].keys())
#
#         # taxis_locations = []
#         # for i in range(self.number_of_taxis):
#         #     taxis_locations.append(initial['taxis'][self.taxis[i]]['location'])
#         #
#         # passengers_locations = []
#         # for i in range(self.number_of_passengers):
#         #     passengers_locations.append(initial['passengers'][self.passengers[i]]['location'])
#
#         for passenger in initial['passengers']:
#             x, y = initial['passengers'][passenger]['location']
#             w, z = initial['passengers'][passenger]['destination']
#             if initial['map'][x][y] == 'I' or initial['map'][w][z] == 'I':
#                 print('sleep')
#                 time.sleep(60)
#
#         for taxi in list(initial['taxis'].keys()):
#             initial['taxis'][taxi]['max_fuel'] = initial['taxis'][taxi]['fuel']
#             initial['taxis'][taxi]['passenger aboard'] = 0
#             initial['taxis'][taxi]['names_passengers_aboard'] = []
#
#         for passenger in list(initial['passengers'].keys()):
#             initial['passengers'][passenger]['taxi name'] = None
#             initial['passengers'][passenger]['picked_up'] = False
#             initial['passengers'][passenger]['arrived_goal'] = False
#             initial['passengers'][passenger]['ever_picked_up'] = False
#             initial['passengers'][passenger]['ever_dropped_off'] = False
#
#         state = {
#             'map': initial['map'],
#             'taxis': initial['taxis'],
#             'passengers': initial['passengers'],
#             'num_rows': len(initial['map']),
#             'num_cols': len(initial['map'][0]),
#             'number_of_taxis': len(initial['taxis']),
#             'number_of_passengers': len(initial['passengers']),
#             'taxis_names': list(initial['taxis'].keys()),
#             'passengers_names': list(initial['passengers'].keys()),
#             'goal_test_counter': 0,
#             'number_passengers_picked_up': 0,
#             'rounds': 0
#         }
#
#         state = json.dumps(state)
#         # build new initial dictionary with new props
#         search.Problem.__init__(self, state)
#
#     def actions(self, state):
#         """Returns all the actions that can be executed in the given
#         state. The result should be a tuple (or other iterable) of actions
#         as defined in the problem description file"""
#
#         # return tuple of tuples of actions for each taxi
#         # loop over all taxis, check every action for each one and save all the possible
#         # combinations (cartesian multiplication).
#
#         # length of all_actions is the number of taxis
#
#         # NOTE: check what the actions should look a like. i.e. is it ok to be a list
#         # which each entry of it is a list contains tuples of actions of a taxi?
#
#         state = copy.deepcopy(state)
#         state = json.loads(state)
#         taxis = [(k, v) for k, v in state['taxis'].items()]
#         # i.e. taxis = [('taxi 1', {'location': (3, 3), 'fuel': 15, 'capacity': 2})]
#         all_actions = []
#         taxis = utils.shuffled(state['taxis'].items())
#         for taxi in taxis:
#             taxi_name = taxi[0]
#             taxi_location = taxi[1]['location']
#             taxi_fuel = taxi[1]['fuel']
#             taxi_capacity = taxi[1]['capacity']
#             temp = self.check_actions(state, taxi_name, taxi_location, taxi_fuel, taxi_capacity)
#             all_actions.append(tuple(temp))
#
#         #all_actions = tuple(all_actions)
#         all_actions = list(itertools.product(*all_actions))
#         all_actions_copy = copy.deepcopy(all_actions)
#         for actions in all_actions:
#             for act in actions:
#                 if act[0] == 'move':
#                     for act2 in actions:
#                         #check if it's the same taxi
#                         if act[1] == act2[1]:
#                             continue
#                         # first case:
#                         # if taxi a and taxi b want to move to the same tile
#                         if (act2[0] == 'wait' or act2[0] == 'refuel' or act2[0] == 'pick uo' or act2[0] == 'drop off') and act[2] == state["taxis"][act2[1]]["location"]:
#                             all_actions = all_actions_copy.remove(actions)
#                             break
#                         if act2[0] == 'move':
#                             if act[2] == act2[2]:
#                                 all_actions = all_actions_copy.remove(actions)
#                                 break
#                 break
#         state = json.dumps(state)
#         for act in all_actions_copy:
#             yield act
#             # i.e. act = (('wait', 'taxi 1'),)
#
#     def check_actions(self, state, taxi_name, taxi_location, taxi_fuel, taxi_capacity):
#         '''
#         return a list of tuples represents all possible actions for a taxi.
#         i.e: [(“move”, “taxi 1”, (1, 2)), (“wait”, “taxi 1”), ("refuel", "taxi 1")]
#         '''
#         M = state['num_rows']
#         N = state['num_cols']
#         x, y = taxi_location
#         actions = []
#         taxis_locations = []
#         number_of_taxis = state['number_of_taxis']
#         for i in range(number_of_taxis):
#             taxis_locations.append(state['taxis'][state['taxis_names'][i]]['location'])
#
#         passengers_locations = []
#         number_of_passengers = state['number_of_passengers']
#         for i in range(number_of_passengers):
#             passengers_locations.append(state['passengers'][state['passengers_names'][i]]['location'])
#
#         # add the wait action
#         actions.append(('wait', taxi_name))
#
#         # check for refuel
#         if state['map'][x][y] == 'G':
#             actions.append(('refuel', taxi_name))
#
#         # check if out of fuel
#         if taxi_fuel <= 0:
#             return actions
#
#         # check for move actions
#         # can go up
#         if x - 1 >= 0 and state['map'][x - 1][y] != 'I' and (x - 1, y):
#             actions.append(('move', taxi_name, (x - 1, y)))
#
#         # can go down
#         if x + 1 < M and state['map'][x + 1][y] != 'I' and (x + 1, y):
#             actions.append(('move', taxi_name, (x + 1, y)))
#
#         # can go left
#         if y - 1 >= 0 and state['map'][x][y - 1] != 'I' and (x, y - 1):
#             actions.append(('move', taxi_name, (x, y - 1)))
#
#         # can go right
#         if y + 1 < N and state['map'][x][y + 1] != 'I' and (x, y + 1):
#             actions.append(('move', taxi_name, (x, y + 1)))
#
#         # check for pick-up actions
#         if taxi_location in passengers_locations and taxi_capacity > 0:
#             passenger_name = self.check_passenger_for_pickup(state,taxi_name, taxi_location)
#             if passenger_name is not None:
#                 actions.append(('pick up', taxi_name, passenger_name))
#
#         # check for drop-off actions
#         passenger_name_at_destination = self.check_passenger_for_dropoff(state, taxi_name, taxi_location)
#         if passenger_name_at_destination is not None:
#             actions.append(('drop off', taxi_name, passenger_name_at_destination))
#
#         return utils.shuffled(actions)
#
#     def check_passenger_for_pickup(self, state, taxi_name, cords):
#         '''
#         check if there is a passenger on the specified cords
#         '''
#         passengers = state['passengers_names']
#         passengers_locations = []
#         number_of_passengers = state['number_of_passengers']
#         for i in range(number_of_passengers):
#             passengers_locations.append(state['passengers'][passengers[i]]['location'])
#
#         passengers_and_their_locations = zip(passengers, passengers_locations)
#         # i.e. [('Yossi', (0, 0)), ('Moshe', (3, 1))]
#         # so, passengers_and_their_locations[0] = ('Yossi', (0, 0))
#
#         for passenger in passengers_and_their_locations:
#             if state['passengers'][passenger[0]]['ever_picked_up'] == True:
#                 continue
#             if cords in passenger:
#                 passenger_name = passenger[0]
#                 # return the first passenger on the tile
#
#                 if passenger_name in state["taxis"][taxi_name]["names_passengers_aboard"]:
#                     return None
#                 return passenger_name
#         return None
#
#     def check_passenger_for_dropoff(self, state, taxi_name, cords):
#         '''
#         return the passenger name if he is at his destination
#         '''
#         passengers = state['passengers_names']
#         passengers_locations = []
#         number_of_passengers = state['number_of_passengers']
#         for i in range(number_of_passengers):
#             passengers_locations.append(state['passengers'][passengers[i]]['location'])
#
#         passengers_destinations = []
#         for i in range(number_of_passengers):
#             passengers_destinations.append(state['passengers'][passengers[i]]['destination'])
#
#         passengers_and_their_locations = zip(passengers, passengers_locations)
#         # i.e. [('Yossi', (0, 0)), ('Moshe', (3, 1))]
#         # so, passengers_and_their_locations[0] = ('Yossi', (0, 0))
#         passengers_and_their_destinations = zip(passengers, passengers_destinations)
#
#
#         passenger_name1, passenger_name2 = None, None
#
#         for passenger in passengers_and_their_locations:
#             if cords in passenger:
#                 passenger_name1 = passenger[0]
#
#         for passenger in passengers_and_their_destinations:
#             if state['passengers'][passenger[0]]['ever_dropped_off'] == True:
#                 continue
#             if cords in passenger:
#                 passenger_name2 = passenger[0]
#
#         if passenger_name1 is not None and passenger_name2 is not None:
#             if passenger_name1 == passenger_name2 and state['passengers'][passenger_name1]['taxi name'] is not None:
#                 if passenger_name1 in state['taxis'][taxi_name]['names_passengers_aboard']:
#                     return passenger_name1
#
#
#
#         return None
#
#     def result(self, state, action):
#         """Return the state that results from executing the given
#         action in the given state. The action must be one of
#         self.actions(state)."""
#         # i.e. if the action tells us to move taxi 1 to (1,2) we need to update
#         # the state accordingly- decrease the taxi fuel and update its location in the state dict.
#         # when pick-up or drop-off update the capacity.
#
#         state = copy.deepcopy(state)
#         state = json.loads(state)
#         # check how it should look like if there is only 1 taxi
#         for act in action:
#             taxi_name = act[1]
#             taxi_action = act[0]
#             # if taxi_action == "wait":
#             #     print(f"{taxi_name} wait")
#             # if taxi_action == 'move':
#             #     print(f"{taxi_name} moved from {state['taxis'][taxi_name]['location']} to {act[2]}")
#             # if taxi_action == 'pick up':
#             #     print(f"{taxi_name} picked up: {state['taxis'][taxi_name]['names_passengers_aboard']}")
#             # if taxi_action == 'drop off':
#             #     print(f"{taxi_name} droped off: {state['taxis'][taxi_name]['names_passengers_aboard']}")
#             if len(act) == 2:
#                 if taxi_action == 'wait':
#                     continue
#                 elif taxi_action == 'refuel':
#                     state['taxis'][taxi_name]['fuel'] = state['taxis'][taxi_name]['max_fuel']
#             elif len(act) == 3:
#                 if taxi_action == 'move':
#                     cords = act[2]
#                     state['taxis'][taxi_name]['fuel'] -= 1
#                     # print(f"{taxi_name} moved from {state['taxis'][taxi_name]['location']} to {cords}")
#                     state['taxis'][taxi_name]['location'] = cords
#                     if state['taxis'][taxi_name]['passenger aboard'] > 0:
#                         for passenger in state['passengers']:
#                             if state['passengers'][passenger]['taxi name'] == taxi_name:
#                                 state['passengers'][passenger]['location'] = cords
#                 elif taxi_action == 'pick up':
#                     # print(state['taxis'][taxi_name]['location'])
#                     # print(act)
#                     passenger_name = act[2]
#                     state['taxis'][taxi_name]['passenger aboard'] += 1
#                     state['passengers'][passenger_name]['taxi name'] = taxi_name
#                     state['taxis'][taxi_name]['capacity'] -= 1
#                     state['number_passengers_picked_up'] += 1
#                     state['passengers'][passenger_name]['picked_up'] = True
#                     state['taxis'][taxi_name]['names_passengers_aboard'].append(passenger_name)
#                     state['passengers'][passenger_name]['ever_picked_up'] = True
#                     # print(f"{taxi_name} pick up: {state['taxis'][taxi_name]['names_passengers_aboard']}")
#                 elif taxi_action == 'drop off':
#                     passenger_name = act[2]
#                     state['taxis'][taxi_name]['passenger aboard'] -= 1
#                     state['passengers'][passenger_name]['location'] = state['passengers'][passenger_name]['destination']
#                     state['passengers'][passenger_name]['taxi name'] = None
#                     state['goal_test_counter'] += 1
#                     state['taxis'][taxi_name]['capacity'] += 1
#                     state['passengers'][passenger_name]['arrived_goal'] = True
#                     state['passengers'][passenger_name]['ever_dropped_off'] = True
#                     if passenger_name in state['taxis'][taxi_name]['names_passengers_aboard']:
#                         state['taxis'][taxi_name]['names_passengers_aboard'].remove(passenger_name)
#                     # print(f"{taxi_name} drop off: {state['taxis'][taxi_name]['names_passengers_aboard']}")
#
#
#         state['rounds'] += 1
#         return json.dumps(state)
#
#     def goal_test(self, state):
#         """ Given a state, checks if this is the goal state.
#          Returns True if it is, False otherwise."""
#         state = copy.deepcopy(state)
#         state = json.loads(state)
#
#         if state['goal_test_counter'] == state['number_of_passengers']:
#             state = json.dumps(state)
#             return True
#         state = json.dumps(state)
#         return False
#
#
#     def h(self, node):
#         """ This is the heuristic. It gets a node (not a state,
#         state can be accessed via node.state)
#         and returns a goal distance estimate"""
#
#         current_state = json.loads(node.state)
#
#         cycles_penalty = 0
#         if node.parent is not None:
#             # if there is 1 taxi
#             if len(node.action) == 1:
#                 if node.action[0] == 'wait':
#                     return 10
#                 if node.action[0] == 'drop off':
#                     return -10
#                 elif node.action[0] == 'move':
#                     parent = node.parent
#                     grand_parent = parent.parent
#                     if parent is not None and grand_parent is not None:
#                         grand_parent_state = json.loads(grand_parent.state)
#                         taxi_name = grand_parent_state['taxis'].keys()
#                         if grand_parent_state['taxis'][taxi_name]['location'] == current_state['taxis'][taxi_name]['location']:
#                             cycles_penalty += 10
#
#             else:
#                 # if there is more than 1 taxi
#                 for action in node.action:
#                     if action[0] == 'wait':
#                         return 10
#                     if action[0] == 'drop off':
#                         return -10
#                     elif node.action[0] == 'move':
#                         parent = node.parent
#                         grand_parent = parent.parent
#                         if parent is not None and grand_parent is not None:
#                             grand_parent_state = json.loads(grand_parent.state)
#                             taxi_name = action[1]
#                             if grand_parent_state['taxis'][taxi_name]['location'] == current_state['taxis'][taxi_name]['location']:
#                                 cycles_penalty += 10
#
#         number_of_passengers = current_state['number_of_passengers']
#         number_of_passengers_picked_up = 0
#         for taxi in current_state['taxis']:
#             # print(current_state['taxis'][taxi]['passenger aboard'])
#             number_of_passengers_picked_up += current_state['taxis'][taxi]['passenger aboard']
#
#         distances_to_destinations = 0
#         distances_to_locations = 0
#         # distance from taxi to destination of passenger
#         if number_of_passengers_picked_up > 0:
#             for taxi_name in current_state['taxis'].keys():
#                 taxi_location = current_state['taxis'][taxi_name]['location']
#                 for passenger_name in current_state['taxis'][taxi_name]['names_passengers_aboard']:
#                     destination = current_state['passengers'][passenger_name]['destination']
#                     # tmp = utils.turn_heading(destination, current_state['rounds'] + 1, destination)
#                     distances_to_destinations += manhattan(tuple(taxi_location), tuple(destination))
#
#         # distances from taxis to unpicked passengers locations
#         for taxi_name in current_state['taxis'].keys():
#             taxi_location = current_state['taxis'][taxi_name]['location']
#             for passenger_name in current_state['passengers'].keys():
#                 passenger_destination = current_state['passengers'][passenger_name]['destination']
#                 if passenger_destination == current_state['passengers'][passenger_name]['location']:
#                     continue
#                 else:
#                     location = current_state['passengers'][passenger_name]['location']
#                     # tmp = utils.turn_heading(location, current_state['rounds'] + 1, location)
#                     # print(f'taxi_location {taxi_location}, tmp {tmp}')
#                     distances_to_locations += manhattan(tuple(taxi_location), tuple(location))
#
#         penalty = distances_to_locations + (number_of_passengers_picked_up * 3.5) + (
#                 number_of_passengers * 7.2) + distances_to_destinations + cycles_penalty + node.path_cost
#
#         return penalty
#
#
#
#     def h_1(self, node):
#         """
#         This is a simple heuristic
#         """
#         state = json.loads(node.state)
#         number_unpicked = state['number_of_passengers'] - state['number_passengers_picked_up']
#         number_picked_undelivered = state['number_passengers_picked_up'] - state['goal_test_counter']
#         number_taxis_in_problem = state['number_of_taxis']
#         return ((2 * number_unpicked) + number_picked_undelivered) / number_taxis_in_problem
#
#
#
#     def h(self, node):
#         """
#         This is a slightly more sophisticated Manhattan heuristic
#         """
#         state = json.loads(node.state)
#         D = []
#         T = []
#
#         for passenger in state['passengers']:
#             if state['passengers'][passenger]['picked_up'] == False and state['passengers'][passenger]['arrived_goal'] == False:
#                 passenger_location = state['passengers'][passenger]['location']
#                 passenger_destination = state['passengers'][passenger]['destination']
#                 D.append(manhattan(passenger_location, passenger_destination))
#             if state['passengers'][passenger]['picked_up'] == True and state['passengers'][passenger]['arrived_goal'] == False:
#                 passenger_location = state['passengers'][passenger]['location']
#                 passenger_destination = state['passengers'][passenger]['destination']
#                 T.append(manhattan(passenger_location, passenger_destination))
#
#         return (sum(D) + sum(T)) / state['number_of_taxis']
#
#     def h9(self, node):
#         return 0
#     """Feel free to add your own functions
#     (-2, -2, None) means there was a timeout"""
#
#     def h_2_copy(self, node):
#         """
#         This is a slightly more sophisticated Manhattan heuristic
#         """
#         state = json.loads(node.state)
#         D = []
#         T = []
#
#         for passenger in state['passengers']:
#             if state['passengers'][passenger]['picked_up'] == False and state['passengers'][passenger]['arrived_goal'] == False:
#                 passenger_location = state['passengers'][passenger]['location']
#                 passenger_destination = state['passengers'][passenger]['destination']
#                 D.append(euclidean(passenger_location, passenger_destination))
#             if state['passengers'][passenger]['picked_up'] == True and state['passengers'][passenger]['arrived_goal'] == False:
#                 passenger_location = state['passengers'][passenger]['location']
#                 passenger_destination = state['passengers'][passenger]['destination']
#                 T.append(euclidean(passenger_location, passenger_destination))
#
#         return (sum(D) + sum(T)) / state['number_of_taxis']
#
#
# def create_taxi_problem(game):
#     return TaxiProblem(game)








import copy
import itertools

import search
import random
import math
import json
import utils
import time

ids = ["206202384", "204864532"]



def manhattan(a, b):
    return sum(abs(val1 - val2) for val1, val2 in zip(a, b))

def euclidean(a, b):
    return sum([(x - y) ** 2 for x, y in zip(a, b)]) ** 0.5

class TaxiProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""

        count_nb_passengers = 0
        for passenger_name in initial['passengers']:
            initial['passengers'][passenger_name]['picked_up'] = False
            initial['passengers'][passenger_name]['dropped_off'] = False
            count_nb_passengers += 1
        initial['total_number_passengers'] = count_nb_passengers
        initial['goal_test_counter'] = 0
        initial['num_rows'] = len(initial['map'])
        initial['num_cols'] = len(initial['map'][0])
        initial['rounds'] = 0
        initial['number_of_taxis'] = len(initial['taxis'])
        initial['number_passengers_picked_up'] = 0

        for taxi in list(initial['taxis'].keys()):
            initial['taxis'][taxi]['max_fuel'] = initial['taxis'][taxi]['fuel']
            initial['taxis'][taxi]['max_capacity'] = initial['taxis'][taxi]['capacity']
            initial['taxis'][taxi]['names_passengers_aboard'] = []


        # state = copy.deepcopy(initial)
        state = json.dumps(initial)
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

        #state = copy.deepcopy(state)
        state = json.loads(state)
        all_actions = []
        # i.e. taxis = [('taxi 1', {'location': (3, 3), 'fuel': 15, 'capacity': 2})]
        for taxi in state['taxis'].items():
            temp = self.check_actions(taxi, state)
            all_actions.append(tuple(temp))
            # all_actions = [(('Move', 'Taxi1', (1,2)), ('wait', 'Taxi1'), ('Move', 'Taxi1', (0,0))), (('Move', 'Taxi2', (0,0)), ('wait', 'Taxi2'))]

        all_actions = tuple(all_actions)
        # all_actions = ((('Move', 'Taxi1', (1,2)), ('wait', 'Taxi1'), ('Move', 'Taxi1', (0,0))), (('Move', 'Taxi2', (0,0)), ('wait', 'Taxi2')))


        all_actions = list(itertools.product(*all_actions))
        if state['number_of_taxis'] == 1:
            state = json.dumps(state)
            for act in all_actions:
                yield act
        else:
            all_actions_copy = copy.deepcopy(all_actions)
            for actions in all_actions:
                for act in actions:
                    if act[0] == 'move':
                        for act2 in actions:
                            # check if it's the same taxi
                            if act[1] == act2[1]:
                                continue
                            # first case:
                            # if taxi a and taxi b want to move to the same tile
                            if (act2[0] == 'wait' or act2[0] == 'refuel' or act2[0] == 'pick uo' or act2[
                                0] == 'drop off') and act[2] == state["taxis"][act2[1]]["location"]:
                                all_actions_copy.remove(actions)
                                break
                            if act2[0] == 'move':
                                if act[2] == act2[2]:
                                    all_actions_copy.remove(actions)
                                    break
                    break
            state = json.dumps(state)
            for act in all_actions_copy:
                yield act
            # i.e. act = (('wait', 'taxi 1'),)


    def check_actions(self, taxi, state):
        '''
        return a list of tuples represents all possible actions for a taxi.
        i.e: [(“move”, “taxi 1”, (1, 2)), (“wait”, “taxi 1”), ("refuel", "taxi 1")]
        '''
        M = state['num_rows']
        N = state['num_cols']
        taxi_name = taxi[0]
        taxi_location = taxi[1]['location']
        taxi_fuel = taxi[1]['fuel']
        taxi_capacity = taxi[1]['capacity']
        taxi_max_capacity = taxi[1]['max_capacity']
        x, y = taxi_location
        actions = []

        # passengers names on taxi[i] for checking drop off action
        passengers_aboard_taxi = taxi[1]['names_passengers_aboard']

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
        if x - 1 >= 0 and state['map'][x - 1][y] != 'I':
            actions.append(('move', taxi_name, (x - 1, y)))

        # can go down
        if x + 1 < M and state['map'][x + 1][y] != 'I':
            actions.append(('move', taxi_name, (x + 1, y)))

        # can go left
        if y - 1 >= 0 and state['map'][x][y - 1] != 'I':
            actions.append(('move', taxi_name, (x, y - 1)))

        # can go right
        if y + 1 < N and state['map'][x][y + 1] != 'I':
            actions.append(('move', taxi_name, (x, y + 1)))

        # check for pick-up actions
        # passengers_names_and_locations = [['Yossi', (0, 0)], ['Moshe', (3, 1)]]
        if taxi_capacity > 0:
            for passenger_name in state['passengers']:
                if (state['passengers'][passenger_name]['location'] == taxi_location) and (state['passengers'][passenger_name]['picked_up'] == False):
                    actions.append(('pick up', taxi_name, passenger_name))

        # check for drop_off actions
        if taxi_capacity < taxi_max_capacity:
            for passenger_name in passengers_aboard_taxi:
                if (state['passengers'][passenger_name]['destination'] == taxi_location) and (state['passengers'][passenger_name]['dropped_off'] == False):
                    actions.append(('drop off', taxi_name, passenger_name))

        return utils.shuffled(actions)


    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        # i.e. if the action tells us to move taxi 1 to (1,2) we need to update
        # the state accordingly- decrease the taxi fuel and update its location in the state dict.
        # when pick-up or drop-off update the capacity.

        #state = copy.deepcopy(state)
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
                if taxi_action == 'move':
                    cords = act[2]
                    state['taxis'][taxi_name]['fuel'] -= 1
                    state['taxis'][taxi_name]['location'] = cords
                    if state['taxis'][taxi_name]['capacity'] != state['taxis'][taxi_name]['max_capacity']:
                        for passenger_name in state['taxis'][taxi_name]['names_passengers_aboard']:
                            state['passengers'][passenger_name]['location'] = cords
                elif taxi_action == 'pick up':
                    passenger_name = act[2]
                    state['taxis'][taxi_name]['capacity'] -= 1
                    state['passengers'][passenger_name]['picked_up'] = True
                    state['number_passengers_picked_up'] += 1
                    state['taxis'][taxi_name]['names_passengers_aboard'].append(passenger_name)
                elif taxi_action == 'drop off':
                    passenger_name = act[2]
                    state['taxis'][taxi_name]['capacity'] += 1
                    state['passengers'][passenger_name]['dropped_off'] = True
                    state['goal_test_counter'] += 1
                    state['taxis'][taxi_name]['names_passengers_aboard'].remove(passenger_name)

        state['rounds'] += 1
        return json.dumps(state)


    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        state = json.loads(state)
        if state['goal_test_counter'] == state['total_number_passengers']:
            state = json.dumps(state)
            return True
        state = json.dumps(state)
        return False

    def h11(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""

        current_state = json.loads(node.state)

        cycles_penalty = 0
        if node.parent is not None:
            # if there is 1 taxi
            if len(node.action) == 1:
                if node.action[0] == 'wait':
                    return 10
                if node.action[0] == 'drop off':
                    return -10
                elif node.action[0] == 'move':
                    parent = node.parent
                    grand_parent = parent.parent
                    if parent is not None and grand_parent is not None:
                        grand_parent_state = json.loads(grand_parent.state)
                        taxi_name = grand_parent_state['taxis'].keys()
                        if grand_parent_state['taxis'][taxi_name]['location'] == current_state['taxis'][taxi_name]['location']:
                            cycles_penalty += 10

            else:
                # if there is more than 1 taxi
                for action in node.action:
                    if action[0] == 'wait':
                        return 10
                    if action[0] == 'drop off':
                        return -10
                    elif node.action[0] == 'move':
                        parent = node.parent
                        grand_parent = parent.parent
                        if parent is not None and grand_parent is not None:
                            grand_parent_state = json.loads(grand_parent.state)
                            taxi_name = action[1]
                            if grand_parent_state['taxis'][taxi_name]['location'] == current_state['taxis'][taxi_name]['location']:
                                cycles_penalty += 10

        number_of_passengers = current_state['number_of_passengers']
        number_of_passengers_picked_up = 0
        for taxi in current_state['taxis']:
            # print(current_state['taxis'][taxi]['passenger aboard'])
            number_of_passengers_picked_up += current_state['taxis'][taxi]['passenger aboard']

        distances_to_destinations = 0
        distances_to_locations = 0
        # distance from taxi to destination of passenger
        if number_of_passengers_picked_up > 0:
            for taxi_name in current_state['taxis'].keys():
                taxi_location = current_state['taxis'][taxi_name]['location']
                for passenger_name in current_state['taxis'][taxi_name]['names_passengers_aboard']:
                    destination = current_state['passengers'][passenger_name]['destination']
                    # tmp = utils.turn_heading(destination, current_state['rounds'] + 1, destination)
                    distances_to_destinations += manhattan(tuple(taxi_location), tuple(destination))

        # distances from taxis to unpicked passengers locations
        for taxi_name in current_state['taxis'].keys():
            taxi_location = current_state['taxis'][taxi_name]['location']
            for passenger_name in current_state['passengers'].keys():
                passenger_destination = current_state['passengers'][passenger_name]['destination']
                if passenger_destination == current_state['passengers'][passenger_name]['location']:
                    continue
                else:
                    location = current_state['passengers'][passenger_name]['location']
                    # tmp = utils.turn_heading(location, current_state['rounds'] + 1, location)
                    # print(f'taxi_location {taxi_location}, tmp {tmp}')
                    distances_to_locations += manhattan(tuple(taxi_location), tuple(location))

        penalty = distances_to_locations + (number_of_passengers_picked_up * 3.5) + (
                number_of_passengers * 7.2) + distances_to_destinations + cycles_penalty + node.path_cost

        return penalty

    def h_0(self, node):
        return 0

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

    def h_1(self, node):
        """
        This is a simple heuristic
        """
        state = json.loads(node.state)
        number_unpicked = state['total_number_passengers'] - state['number_passengers_picked_up']
        number_picked_undelivered = state['number_passengers_picked_up'] - state['goal_test_counter']
        number_taxis_in_problem = state['number_of_taxis']
        return ((2 * number_unpicked) + number_picked_undelivered) / number_taxis_in_problem



    def h(self, node):
        """
        This is a slightly more sophisticated Manhattan heuristic
        """
        state = json.loads(node.state)
        D = []
        T = []

        for passenger in state['passengers']:
            if state['passengers'][passenger]['picked_up'] == False and state['passengers'][passenger]['dropped_off'] == False:
                passenger_location = state['passengers'][passenger]['location']
                passenger_destination = state['passengers'][passenger]['destination']
                D.append(manhattan(passenger_location, passenger_destination))
            if state['passengers'][passenger]['picked_up'] == True and state['passengers'][passenger]['dropped_off'] == False:
                passenger_location = state['passengers'][passenger]['location']
                passenger_destination = state['passengers'][passenger]['destination']
                T.append(manhattan(passenger_location, passenger_destination))
        json.dumps(node.state)

        return (sum(D) + sum(T)) / state['number_of_taxis']


    def h_2_euclidean(self, node):
        """
        This is a slightly more sophisticated Manhattan heuristic
        """
        state = json.loads(node.state)
        D = []
        T = []

        for passenger in state['passengers']:
            if state['passengers'][passenger]['picked_up'] == False and state['passengers'][passenger]['dropped_off'] == False:
                passenger_location = state['passengers'][passenger]['location']
                passenger_destination = state['passengers'][passenger]['destination']
                D.append(euclidean(passenger_location, passenger_destination))
            if state['passengers'][passenger]['picked_up'] == True and state['passengers'][passenger]['dropped_off'] == False:
                passenger_location = state['passengers'][passenger]['location']
                passenger_destination = state['passengers'][passenger]['destination']
                T.append(euclidean(passenger_location, passenger_destination))

        return (sum(D) + sum(T)) / state['number_of_taxis']


def create_taxi_problem(game):
    return TaxiProblem(game)
