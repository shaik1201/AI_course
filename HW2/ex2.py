import itertools

import networkx as nx
import numpy as np

ids = ["204864532", "206202384"]


# Successful delivery of a passenger : +100
# Resetting the environment: -50
# Refuel: -10

class OptimalTaxiAgent:
    def __init__(self, initial):
        initial['number_taxis'] = len(initial['taxis'].keys())
        initial['number_passengers'] = len(initial['passengers'].keys())
        for taxi in initial['taxis'].keys():
            initial['taxis'][taxi]['max_fuel'] = initial['taxis'][taxi]['fuel']
            initial['taxis'][taxi]['max_capacity'] = initial['taxis'][taxi]['capacity']
        self.initial = initial
        self.distances = Distances(initial)


    # check distance: print(self.distances.check_distances(self.distances.shortest_path_distances, (0,0), (1,2)))

    # For a given state we return the best policy (=action)
    def act(self, state):
        return 'wait'

    # initial: { "optimal": True,
    #           "map": [['P', 'P', 'P'],
    #                   ['P', 'G', 'P'],
    #                   ['P', 'P', 'P']],
    #           "taxis": {'taxi 1': {"location": (0, 0), "fuel": 10, "capacity": 1, "max_fuel" = 10, "max_capacity" = 1}},
    #           "passengers": {'Dana': {"location": (2, 2), "destination": (0, 0),
    #                   "possible_goals": ((0, 0), (2, 2)), "prob_change_goal": 0.1}},
    #           "turns to go": 100
    #           "number_taxis" : 1
    #           "number_passengers" : 1}

    def value_iteration_algorithm(self,state):
        v_0 = self.value_state_initialization()
        converge = False
        epsilon = 0.1
        value = [0,0]
        while not converge:
            value[1] = value[0]
            value[0] = self.value_state(state)
            if np.absolute(value[1] - value[0]) <= epsilon:
                converge = True
        return


    # locations of taxis, fuel of taxis, capacity of taxis, location of passengers, destinations of passengers
    def value_state_initialization(self):
        state = self.initial
        v_0 = {}
        m = len(state['map'])
        n = len(state['map'][0])
        number_taxis = state['number_taxis']
        number_passengers = state['number_passengers']
        fuel_taxis = []
        capacity_taxis = []
        # [(0,0), (1,0), ... ,(m-1,n-1)]
        possible_location_taxis = number_taxis * [[(i, j) for j in range(m) for i in range(n)]]
        possible_location_passengers = [(i, j) for j in range(m) for i in range(n)]
        possible_destination_passengers = [state['passengers'][passenger_name]["possible_goals"] for passenger_name in state['passengers'].keys()]

        for taxi_name in state['taxis'].keys():
            fuel_taxis += [[i for i in range(state['taxis'][taxi_name]['max_fuel'])]]
            capacity_taxis += [[i for i in range(state['taxis'][taxi_name]['max_capacity'])]]
            possible_location_passengers.append(taxi_name)

        possible_location_passengers = number_passengers * [possible_location_passengers]

        # [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (2, 11), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10), (4, 11), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (5, 10), (5, 11), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (6, 11), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9), (7, 10), (7, 11), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8), (8, 9), (8, 10), (8, 11), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8), (9, 9), (9, 10), (9, 11), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7), (10, 8), (10, 9), (10, 10), (10, 11), (11, 0), (11, 1), (11, 2), (11, 3), (11, 4), (11, 5), (11, 6), (11, 7), (11, 8), (11, 9), (11, 10), (11, 11)]
        all_possible_location_taxis = list(itertools.product(*possible_location_taxis))
        all_possible_location_passengers = list(itertools.product(*possible_location_passengers))
        all_possible_destination_passengers = list(itertools.product(*possible_destination_passengers))
        all_fuels = list(itertools.product(*fuel_taxis))
        all_capacity = list((itertools.product(*capacity_taxis)))

        # initial: { "optimal": True,
        #           "map": [['P', 'P', 'P'],
        #                   ['P', 'G', 'P'],
        #                   ['P', 'P', 'P']],
        #           "taxis": {'taxi 1': {"location": (0, 0), "fuel": 10, "capacity": 1, "max_fuel" = 10, "max_capacity" = 1}},
        #           "passengers": {'Dana': {"location": (2, 2), "destination": (0, 0),
        #                   "possible_goals": ((0, 0), (2, 2)), "prob_change_goal": 0.1}},
        #           "turns to go": 100
        #           "number_taxis" : 1
        #           "number_passengers" : 1}


        # for number_of_taxis in range(number_taxis):
        k = 0
        for location_taxis in all_possible_location_taxis:
            state = self.initial
            for location_passengers in all_possible_location_passengers:
                for destination_passengers in all_possible_destination_passengers:
                    for taxis_fuel in all_fuels:
                        for taxis_capacity in all_capacity:
                            # Fill the state
                            taxi_counter = 0
                            passenger_counter = 0
                            for taxi_name in state['taxis'].keys():
                                state['taxis'][taxi_name]["location"] = location_taxis[taxi_counter] # √
                                state['taxis'][taxi_name]["fuel"] = taxis_fuel[taxi_counter] # √
                                state['taxis'][taxi_name]["capacity"] = taxis_capacity[taxi_counter] # √
                                taxi_counter += 1
                            for passenger_name in state['passengers'].keys():
                                state['passengers'][passenger_name]["location"] = location_passengers[passenger_counter] # √
                                state['passengers'][passenger_name]["destination"] = destination_passengers[passenger_counter]
                                passenger_counter += 1
                            v_0['state' + str(k)] = state
                            k += 1
    def value_state(self, state):
        return 0

    def reward_state(self, state):
        reward = 0
        for taxi in self.initial['taxis'].keys():
            fuel_conservation = state['taxis'][taxi]['fuel'] / state['taxis'][taxi]['max_fuel']
            reward += state['taxis'][taxi]['max_capacity'] - state['taxis'][taxi]['capacity']
            for passenger in self.initial['passengers'].keys():
                # If the passenger is on the taxi
                # The location of the passenger is the taxi's name
                if self.initial['passengers'][passenger]['location'] == taxi:
                    reward += fuel_conservation * (self.distances.diameter - self.distances.check_distances(self.distances.graph, state['taxis'][taxi]['location'], self.initial['passengers'][passenger]['destination']))

                # If the passenger is not on the taxis:
                # The location of the passenger is his location
                else:
                    reward += fuel_conservation * (self.distances.diameter - self.distances.check_distances(self.distances.graph, state['taxis'][taxi]['location'], state['passengers'][passenger]['location']))
        return reward

    def transition_function(self):
        return 0




class TaxiAgent:
    def __init__(self, initial):
        self.initial = initial
        self.distances = Distances(initial)

    def act(self, state):
        return 'wait'

    def reward_state(self, state):
        reward = 0
        for taxi in self.initial['taxis'].keys():
            fuel_conservation = state['taxis'][taxi]['fuel'] / state['taxis'][taxi]['max_fuel']
            reward += state['taxis'][taxi]['max_capacity'] - state['taxis'][taxi]['capacity']
            for passenger in self.initial['passengers'].keys():
                # If the passenger is on the taxi
                # The location of the passenger is the taxi's name
                if self.initial['passengers'][passenger]['location'] == taxi:
                    reward += fuel_conservation * (self.distances.diameter - self.distances.check_distances(self.distances.graph, state['taxis'][taxi]['location'], self.initial['passengers'][passenger]['destination']))

                # If the passenger is not on the taxis:
                # The location of the passenger is his location
                else:
                    reward += fuel_conservation * (self.distances.diameter - self.distances.check_distances(self.distances.graph, state['taxis'][taxi]['location'], state['passengers'][passenger]['location']))
        return reward

class Distances:
    #initial: { "optimal": True,
    #           "map": [['P', 'P', 'P'],
    #                   ['P', 'G', 'P'],
    #                   ['P', 'P', 'P']],
    #           "taxis": {'taxi 1': {"location": (0, 0), "fuel": 10, "capacity": 1}},
    #           "passengers": {'Dana': {"location": (2, 2), "destination": (0, 0),
    #                   "possible_goals": ((0, 0), (2, 2)), "prob_change_goal": 0.1}},
    #           "turns to go": 100},
    def __init__(self, initial):
        self.state = initial
        self.graph = self.build_graph(initial)
        self.shortest_path_distances = self.create_shortest_path_distances(self.graph)
        self.diameter = nx.diameter(self.graph)
    def build_graph(self, initial):
        """
        build the graph of the problem
        """
        n, m = len(initial['map']), len(initial['map'][0])
        g = nx.grid_graph((m, n))
        nodes_to_remove = []
        for node in g:
            if initial['map'][node[0]][node[1]] == 'I':
                nodes_to_remove.append(node)
        for node in nodes_to_remove:
            g.remove_node(node)
        return g

    def create_shortest_path_distances(self, graph):
        d = {}
        for n1 in graph.nodes:
            for n2 in graph.nodes:
                if n1 == n2:
                    continue
                d[(n1, n2)] = len(nx.shortest_path(graph, n1, n2)) - 1
        return d

    def check_distances(self, graph, node1, node2):
        return graph[(node1,node2)]


