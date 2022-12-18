import copy
import itertools
import random

import networkx as nx
import logging

ids = ["204864532", "206202384"]


# Successful delivery of a passenger : +100
# Resetting the environment: -50
# Refuel: -10


# initial: { "optimal": True,
#           "map": [['P', 'P', 'P'],
#                   ['P', 'G', 'P'],
#                   ['P', 'P', 'P']],
#           "taxis": {'taxi 1': {"location": (0, 0), "fuel": 10, "capacity": 1}},
#           "passengers": {'Dana': {"location": (2, 2), "destination": (0, 0),
#                   "possible_goals": ((0, 0), (2, 2)), "prob_change_goal": 0.1}},
#           "turns to go": 100 }


# initial_improved: { "optimal": True,
#           "map": [['P', 'P', 'P'],
#                   ['P', 'G', 'P'],
#                   ['P', 'P', 'P']],
#           "taxis": {'taxi 1': {"location": (0, 0), "fuel": 10, "capacity": 1, 'max_fuel': 10, 'max_capacity": 1}},
#           "passengers": {'Dana': {"location": (2, 2), "destination": (0, 0),
#                   "possible_goals": ((0, 0), (2, 2)), "prob_change_goal": 0.1}},
#           "turns to go": 100
#           "number_taxis" : 1
#           "number_passengers" : 1}


class OptimalTaxiAgent:
    def __init__(self, initial):
        self.initial = initial
        self.initial_improved = copy.deepcopy(initial)
        self.initial_improved['number_taxis'] = len(initial['taxis'].keys())
        self.initial_improved['number_passengers'] = len(initial['passengers'].keys())
        for taxi in initial['taxis'].keys():
            self.initial_improved['taxis'][taxi]['max_fuel'] = initial['taxis'][taxi]['fuel']
            self.initial_improved['taxis'][taxi]['max_capacity'] = initial['taxis'][taxi]['capacity']
        self.distances = Distances(initial)

    # check distance: print(self.distances.check_distances(self.distances.shortest_path_distances, (0,0), (1,2)))

    # For a given state we return the best policy (=action)
    def act(self, state):
        return 'wait'


    def value_iteration_algorithm(self):
        v_t_1, v_t, reward = self.value_state_initialization()
        all_possible_actions = self.create_randoms_action()
        t = self.initial["turns to go"]
        for i in range(1, t+1):
            for state in reward.keys():
                actions = self.actions(state, all_possible_actions)
                actions_states = dict()
                for action in actions:
                    copy_state = copy.deepcopy(state)
                    self.result(copy_state, action)
                    actions_states[action] = copy_state
                    # probability_s_s1 = self.transition_function(state, action, copy_state)
                probability_s_s1 = 1
                value_for_each_state = dict()
                for action_state in actions_states.keys():
                    value_for_each_state[action_state] = v_t_1[actions_states[action_state]][1] * probability_s_s1
                max_value = max(value_for_each_state.values())

                # We need the max action for the policy
                # max_action = max(value_for_each_state, key=value_for_each_state.get)

                # We are Here !

                # PROBLEM !!!! : HOW TO
                # v_t[state][1] = reward[state] + max_value
                # v_t[state][0] -= 1
                # v_t_1[state][1] = v_t[state][1]
                # v_t_1[state][0] = v_t[state][0]

            # v_t_1 = copy.deepcopy(v_t)


### IMPORTANT:  AS WE HAVE SEEN THE STATES DON'T CHANGE OVER ITERATIONS, JUST REWARD AND TURNS TO GO DO
###             SO MAYBE WE WILL SAVE JUST ONE DICT OF STATES (THAT DOESN'T CHANGE OVER ITERATIONS) AND
###             TWO LISTS VT_1 AND V_T WITH TURNS TO GO AND REWARDS AS VALUES





    # locations of taxis, fuel of taxis, capacity of taxis, location of passengers, destinations of passengers
    def value_state_initialization(self):
        state = self.initial_improved
        v_0 = dict()
        v_1 = dict()
        reward1 = dict()
        m = len(state['map'])
        n = len(state['map'][0])
        number_taxis = state['number_taxis']
        number_passengers = state['number_passengers']
        fuel_taxis = []
        capacity_taxis = []
        possible_location_taxis = number_taxis * [[(i, j) for j in range(m) for i in range(n)]]
        possible_location_passengers = [(i, j) for j in range(m) for i in range(n)]
        possible_destination_passengers = [state['passengers'][passenger_name]["possible_goals"] for passenger_name in state['passengers'].keys()]

        for taxi_name in state['taxis'].keys():
            fuel_taxis += [[i for i in range(state['taxis'][taxi_name]['max_fuel'] + 1)]]
            capacity_taxis += [[i for i in range(state['taxis'][taxi_name]['max_capacity'] + 1)]]
            possible_location_passengers.append(taxi_name)

        possible_location_passengers = number_passengers * [possible_location_passengers]

        all_possible_location_taxis = list(itertools.product(*possible_location_taxis))
        all_possible_location_passengers = list(itertools.product(*possible_location_passengers))
        all_possible_destination_passengers = list(itertools.product(*possible_destination_passengers))
        all_fuels = list(itertools.product(*fuel_taxis))
        all_capacity = list((itertools.product(*capacity_taxis)))

        k = 0
        turns_to_go = state['turns to go']
        for location_taxis in all_possible_location_taxis:
            for location_passengers in all_possible_location_passengers:
                for destination_passengers in all_possible_destination_passengers:
                    for taxis_fuel in all_fuels:
                        for taxis_capacity in all_capacity:
                            # Fill the state
                            reset = []
                            reward = 0
                            taxi_counter = 0
                            passenger_counter = 0
                            state_i = dict()
                            state_i['optimal'] = state['optimal']
                            state_i['map'] = state['map']
                            # state_i["turns to go"] = state["turns to go"]
                            state_i['taxis'] = {}
                            state_i['passengers'] = {}

                            for taxi_name in state['taxis'].keys():
                                state_i['taxis'][taxi_name] = {}
                                state_i['taxis'][taxi_name]["location"] = location_taxis[taxi_counter]
                                state_i['taxis'][taxi_name]["fuel"] = taxis_fuel[taxi_counter]
                                state_i['taxis'][taxi_name]["capacity"] = taxis_capacity[taxi_counter]

                                if state_i['taxis'][taxi_name]["fuel"] == state['taxis'][taxi_name]["max_fuel"] and \
                                   state_i['taxis'][taxi_name]["location"] != state['taxis'][taxi_name]["location"]:
                                        reward -= 10

                                if state_i['taxis'][taxi_name]["location"] == state['taxis'][taxi_name]["location"] and \
                                   state_i['taxis'][taxi_name]["fuel"] == state['taxis'][taxi_name]["max_fuel"] and \
                                   state_i['taxis'][taxi_name]["capacity"] == state['taxis'][taxi_name]["max_capacity"]:
                                        reset.append(True)

                                else:
                                    reset.append(False)
                                taxi_counter += 1

                            for passenger_name in state['passengers'].keys():
                                state_i['passengers'][passenger_name] = {}
                                state_i['passengers'][passenger_name]["location"] = location_passengers[passenger_counter]
                                state_i['passengers'][passenger_name]["destination"] = destination_passengers[passenger_counter]
                                state_i['passengers'][passenger_name]["possible_goals"] = state['passengers'][passenger_name]["possible_goals"]
                                state_i['passengers'][passenger_name]["prob_change_goal"] = state['passengers'][passenger_name]["prob_change_goal"]

                                if state_i['passengers'][passenger_name]["location"] == \
                                   state_i['passengers'][passenger_name]["destination"]:
                                        reward += 100

                                if state_i['passengers'][passenger_name]["location"] == \
                                   state['passengers'][passenger_name]["location"] and \
                                   state_i['passengers'][passenger_name]["destination"] == \
                                   state['passengers'][passenger_name]["destination"]:
                                        reset.append(True)

                                else:
                                    reset.append(False)
                                passenger_counter += 1

                            if sum(reset) == len(reset):
                                reward -= 50

                            str_state_i = str(sorted(state_i.items()))
                            v_0[str_state_i] = [turns_to_go, reward]
                            v_1[str_state_i] = [turns_to_go, reward]
                            reward1[str_state_i] = [turns_to_go, reward]

                            k += 1
        return v_0, v_1, reward1

    def transition_function(self, state, action, state1):
        return 0

    def create_randoms_action(self):
        m = len(self.initial_improved['map'])
        n = len(self.initial_improved['map'][0])
        actions = []

        for taxi_name in self.initial_improved['taxis'].keys():
            taxis_actions = []
            for i in range(m):
                for j in range(n):
                    taxis_actions.append(('move', taxi_name, (i, j)))
            for passenger_name in self.initial_improved['passengers'].keys():
                taxis_actions.append(('pick up', taxi_name, passenger_name))
                taxis_actions.append(('drop off', taxi_name, passenger_name))
            taxis_actions.append(('refuel', taxi_name))
            taxis_actions.append(('wait', taxi_name))
            actions.append(taxis_actions)

        all_possible_actions = list(itertools.product(*actions))
        all_possible_actions.append('reset')
        all_possible_actions.append('terminate')
        return all_possible_actions

    def actions(self, state, all_possible_actions):
        all_actions = []
        for possible_action in all_possible_actions:
            if self.is_action_legal(state, possible_action):
                all_actions.append(possible_action)
        return all_actions

    def is_action_legal(self, state, action):
        """
        check if the action is legal
        """
        def _is_move_action_legal(move_action):
            taxi_name = move_action[1]
            if taxi_name not in state['taxis'].keys():
                return False
            if state['taxis'][taxi_name]['fuel'] == 0:
                return False
            l1 = state['taxis'][taxi_name]['location']
            l2 = move_action[2]
            return l2 in list(self.distances.graph.neighbors(l1))

        def _is_pick_up_action_legal(pick_up_action):
            taxi_name = pick_up_action[1]
            passenger_name = pick_up_action[2]
            # check same position
            if state['taxis'][taxi_name]['location'] != state['passengers'][passenger_name]['location']:
                return False
            # check taxi capacity
            if state['taxis'][taxi_name]['capacity'] <= 0:
                return False
            # check passenger is not in his destination
            if state['passengers'][passenger_name]['destination'] == state['passengers'][passenger_name]['location']:
                return False
            return True

        def _is_drop_action_legal(drop_action):
            taxi_name = drop_action[1]
            passenger_name = drop_action[2]
            # check same position
            if state['taxis'][taxi_name]['location'] != state['passengers'][passenger_name]['destination']:
                return False
            return True

        def _is_refuel_action_legal(refuel_action):
            """
            check if taxi in gas location
            """
            taxi_name = refuel_action[1]
            i, j = state['taxis'][taxi_name]['location']
            if self.initial_improved['map'][i][j] == 'G':
                return True
            else:
                return False

        def _is_action_mutex(global_action):
            assert type(global_action) == tuple, "global action must be a tuple"
            # one action per taxi
            if len(set([a[1] for a in global_action])) != len(global_action):
                return True
            # pick up the same person
            pick_actions = [a for a in global_action if a[0] == 'pick up']
            if len(pick_actions) > 1:
                passengers_to_pick = set([a[2] for a in pick_actions])
                if len(passengers_to_pick) != len(pick_actions):
                    return True
            return False

        if action == "reset":
            return True
        if action == "terminate":
            return True

        if len(action) != len(state["taxis"].keys()):
            logging.error(f"You had given {len(action)} atomic commands, while there are {len(state['taxis'])}"
                          f" taxis in the problem!")
            return False

        for atomic_action in action:
            # illegal move action
            if atomic_action[0] == 'move' and not _is_move_action_legal(atomic_action):
                logging.error(f"Move action {atomic_action} is illegal!")
                return False
            # illegal pick action
            elif atomic_action[0] == 'pick up' and not _is_pick_up_action_legal(atomic_action):
                logging.error(f"Pick action {atomic_action} is illegal!")
                return False
            # illegal drop action
            elif atomic_action[0] == 'drop off' and not _is_drop_action_legal(atomic_action):
                logging.error(f"Drop action {atomic_action} is illegal!")
                return False
            # illegal refuel action
            elif atomic_action[0] == 'refuel' and not _is_refuel_action_legal(atomic_action):
                logging.error(f"Refuel action {atomic_action} is illegal!")
                return False
            elif atomic_action[0] == 'wait':
                return True
        # check mutex action
        if _is_action_mutex(action):
            logging.error(f"Actions {action} are mutex!")
            return False
        return True

    def result(self, state, action):
        """"
        update the state according to the action
        """
        self.apply(state, action)
        if action != "reset":
            self.environment_step(state)

    def apply(self, state, action):
        """
        apply the action to the state
        """
        if action == "reset":
            self.reset_environment(state)
        if action == "terminate":
            self.terminate_execution(state)
        for atomic_action in action:
            self.apply_atomic_action(state, atomic_action)
    def apply_atomic_action(self, state, atomic_action):
        """
        apply an atomic action to the state
        """
        taxi_name = atomic_action[1]
        if atomic_action[0] == 'move':
            state['taxis'][taxi_name]['location'] = atomic_action[2]
            state['taxis'][taxi_name]['fuel'] -= 1
            return
        elif atomic_action[0] == 'pick up':
            passenger_name = atomic_action[2]
            state['taxis'][taxi_name]['capacity'] -= 1
            state['passengers'][passenger_name]['location'] = taxi_name
            return
        elif atomic_action[0] == 'drop off':
            passenger_name = atomic_action[2]
            state['passengers'][passenger_name]['location'] = state['taxis'][taxi_name]['location']
            state['taxis'][taxi_name]['capacity'] += 1
            return
        elif atomic_action[0] == 'refuel':
            state['taxis'][taxi_name]['fuel'] = self.initial['taxis'][taxi_name]['fuel']
            return
        elif atomic_action[0] == 'wait':
            return
        else:
            raise NotImplemented

    def environment_step(self, state):
        """
        update the state of environment randomly
        """
        for p in state['passengers']:
            passenger_stats = state['passengers'][p]
            if random.random() < passenger_stats['prob_change_goal']:
                # change destination
                passenger_stats['destination'] = random.choice(passenger_stats['possible_goals'])
        state["turns to go"] -= 1
        return

    def reset_environment(self, state):
        """
        reset the state of the environment
        """
        state["taxis"] = self.initial["taxis"]
        state["passengers"] = self.initial["passengers"]
        state["turns to go"] -= 1
        return

    def terminate_execution(self, state):
        """
        terminate the execution of the problem
        """
        print(f"End of game")
        print(f"-----------------------------------")
        return
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


