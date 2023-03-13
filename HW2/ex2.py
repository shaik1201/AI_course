import copy
import itertools
import random
import time
import pickle
import networkx as nx
import logging
import json

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

time1 = time.time()

class OptimalTaxiAgent:

    def __init__(self, initial):
        global time1
        self.initial = initial
        self.initial_improved = copy.deepcopy(initial)
        self.initial_improved['number_taxis'] = len(initial['taxis'].keys())
        self.initial_improved['number_passengers'] = len(initial['passengers'].keys())
        for taxi in initial['taxis'].keys():
            self.initial_improved['taxis'][taxi]['max_fuel'] = initial['taxis'][taxi]['fuel']
            self.initial_improved['taxis'][taxi]['max_capacity'] = initial['taxis'][taxi]['capacity']
        self.distances = Distances(initial)
        print('starting value initialization')
        print(time.time() - time1)
        print()
        self.possible_destination = None
        self.best_actions = {}
        self.value_iteration_shai()
    def act(self, state):
        new_state = {key: state[key] for key in self.order}
        action = self.best_actions[json.dumps(new_state)]
        return action




    def value_iteration_shai(self):
        states = self.value_state_initialization()
        values_t_new = self.initialization_initial_values(states)
        all_possible_actions = self.create_randoms_action()
        turns_to_go = self.initial['turns to go']

        y = self.initial

        for i in range(0, turns_to_go):
            print(f"iteration: {i}")
            values_t_past = copy.deepcopy(values_t_new)
            values_t_new = dict()
            for state in states[i]:

                # possible actions for the state
                actions = self.actions(state, all_possible_actions)

                # for each action compute all states prime we can go to, given the current state
                actions_states = dict()
                for action in actions:
                    actions_states[action] = self.compute_states_prime(state, action)
                    if action == 'terminate':
                        actions_states[action] = []

                # compute the best action for the given state
                best_action = self.compute_best_action(state, actions_states, values_t_past)

                # save the states_prime we can go to by applying best_action
                states_prime = actions_states[best_action]

                # compute transition probabilities to move to all states_prime by applying best_action
                # how it looks: {state_prime:prob, ...}
                transition_probs = self.compute_transition_probs(state, best_action, states_prime)

                # compute the sigma
                sigma = self.compute_sigma(states_prime, transition_probs, values_t_past)

                reward_state = self.reward_shai(best_action)

                key_state = json.dumps(state)
                new_value = reward_state + sigma
                temp = {key_state: new_value}
                temp2 = {key_state: best_action}
                values_t_new.update(temp)
                self.best_actions.update(temp2)
                # print(values_t_new[str(state)])


        # value = values_t_new[json.dumps(y)]
        # print(f'final value: {value}')


    def reward_shai_new(self, state, iteration):
        passengers = state['passengers'].keys()
        taxis = state['taxis'].keys()
        taxis_num = len(list(taxis))
        for passenger_name in passengers:
            r = random.random()
            if state['passengers'][passenger_name]['location'] == state['passengers'][passenger_name]['destination'] and r <= 7/8:
                return 100
        if iteration != 0:
            # check if was reset
            count = 0
            for taxi_name in taxis:
                if state['taxis'][taxi_name]['location'] == self.initial_improved['taxis'][taxi_name]['location'] and \
                        state['taxis'][taxi_name]['fuel'] == self.initial_improved['taxis'][taxi_name]['max_fuel'] and \
                        state['taxis'][taxi_name]['capacity'] == self.initial_improved['taxis'][taxi_name]['max_capacity']:
                    count += 1
                if count == taxis_num:
                    return -50
            # check if any taxi refueled
            for taxi_name in taxis:
                if state['taxis'][taxi_name]['fuel'] == self.initial_improved['taxis'][taxi_name]['max_fuel']:
                    return -10
        return 0

    def initialization_initial_values(self, states):
        initial_values = {}
        for state in states[0]:
            initial_values[json.dumps(state)] = 0
        return initial_values

    def compute_states_prime(self, state, action):
        # code for 1 passenger
        # possible_destinations = []
        passengers = state['passengers'].keys()
        # for passenger_name in passengers:
        #     possible_goals = state['passengers'][passenger_name]['possible_goals']
        #     for goal in possible_goals:
        #         possible_destinations.append(goal)

        possible_destinations = self.possible_destination

        number_of_possible_states = len(possible_destinations)
        copy_state = copy.deepcopy(state)
        self.result(copy_state, action)
        s_primes = []
        for i in range(number_of_possible_states):
            counter_passenger = 0
            copy_state_prime = copy.deepcopy(copy_state)
            for passenger_name in passengers:
                copy_state_prime['passengers'][passenger_name]['destination'] = possible_destinations[i][counter_passenger]
                counter_passenger += 1
                if copy_state_prime not in s_primes:
                    s_primes.append(copy_state_prime)


        if action == 'reset':
            for s in s_primes:
                flag = False
                for passenger_name in passengers:
                    if s['passengers'][passenger_name]['destination'] != self.initial['passengers'][passenger_name]['destination']:
                        flag = True
                if flag:
                    s_primes.remove(s)
        return s_primes

    def compute_optimal_action(self, state, values_t_new):

        # compute all actions given the state
        all_possible_actions = self.create_randoms_action()
        actions = self.actions(state, all_possible_actions)

        # for each action compute all states prime we can go to, given the current state
        actions_states = dict()
        for action in actions:
            actions_states[action] = self.compute_states_prime(state, action)
            if action == 'terminate':
                actions_states[action] = []

        # compute the best action for the given state
        best_action = self.compute_best_action(state, actions_states, values_t_new)

        return best_action

    def reward_shai(self, action):
        if action[0][0] == 'pick up':
            return 0
        elif action[0][0] == 'drop off':
            return 100
        elif action[0][0] == 'refuel':
            return -10
        elif action == 'reset':
            return -50
        elif action == 'terminate':
            return 0
        elif action[0][0] == 'wait':
            return 0
        elif action[0][0] == 'move':
            return 0

    def compute_best_action(self, state, actions_states, values_t):
        # first, for each action compute its value
        action_values = {}
        actions = actions_states.keys()
        for action in actions:
            s_primes = actions_states[action]
            action_value = self.compute_action_value(state, action, s_primes, values_t) + self.reward_shai(action)
            action_values[action] = action_value

        # find the best action with the greatest action_value
        best_action = max(action_values, key=action_values.get)
        return best_action

    def compute_action_value(self, state, action, s_primes, values_t):
        probs = self.compute_transition_probs(state, action, s_primes)
        v = 0

        for s in s_primes:
            transition_prob = probs[json.dumps(s)]
            if s['turns to go'] == 0:
                v_past = 0
            else:
                v_past = values_t[json.dumps(s)]
            v += transition_prob * v_past

        return v

    def compute_sigma(self, states_prime, transition_probs, values_t_past):
        v = 0
        for s in states_prime:
            transition_prob = transition_probs[json.dumps(s)]
            if s['turns to go'] == 0:
                v_past = 0
            else:
                v_past = values_t_past[json.dumps(s)]
            v += transition_prob * v_past

        return v

    def compute_transition_probs(self, state, action, states_prime):
        # need to be compatability between states_prime and the probs returned.
        # returns dict - prob for each state_prime
        # code for 1 passenger
        probs = {}
        p = 1
        passengers = state['passengers'].keys()
        for passenger_name in passengers:
            n = len(self.initial['passengers'][passenger_name]['possible_goals'])
            prob_change_goal = state['passengers'][passenger_name]['prob_change_goal']
            prob_transition = prob_change_goal / n
            if state['passengers'][passenger_name]['destination'] in state['passengers'][passenger_name]['possible_goals']:
                for s_prime in states_prime:
                    state_destination = state['passengers'][passenger_name]['destination']
                    s_prime_destination = s_prime['passengers'][passenger_name]['destination']
                    if s_prime_destination == state_destination:
                        probs[json.dumps(s_prime)] = 1 - prob_change_goal + prob_transition
                    else:
                        probs[json.dumps(s_prime)] = prob_transition
                    if action == 'reset':
                        probs[json.dumps(s_prime)] = 1
            else:
                for s_prime in states_prime:
                    state_destination = state['passengers'][passenger_name]['destination']
                    s_prime_destination = s_prime['passengers'][passenger_name]['destination']
                    if s_prime_destination == state_destination:
                        probs[json.dumps(s_prime)] = 1 - prob_change_goal
                    else:
                        probs[json.dumps(s_prime)] = prob_transition
                    if action == 'reset':
                        probs[json.dumps(s_prime)] = 1
        return probs




    # states[i] = turns to go i + 1

    def value_state_initialization(self):
        state1 = self.initial_improved
        states = list()
        self.n = len(self.initial_improved['map'])
        self.m = len(self.initial_improved['map'][0])
        turns_to_go = list(range(1,self.initial['turns to go'] + 1))
        taxis_names = [taxi_name for taxi_name in state1['taxis'].keys()]
        number_taxis = state1['number_taxis']
        fuel_taxis = []
        capacity_taxis = []
        possible_location_taxis = number_taxis * [[(i, j) for i in range(self.n) for j in range(self.m) if self.initial_improved['map'][i][j] != 'I']]

        possible_location_passengers = []
        possible_destination_passengers = []
        for passenger_name in state1['passengers'].keys():
            poss_location = list()
            poss_destination = list()
            for possible_destination in state1['passengers'][passenger_name]['possible_goals']:
                poss_location.append(possible_destination)
                poss_destination.append(possible_destination)
            poss_location += taxis_names
            if state1['passengers'][passenger_name]['location'] not in poss_location:
                poss_location.append(state1['passengers'][passenger_name]['location'])
            if state1['passengers'][passenger_name]['destination'] not in poss_destination:
                poss_location.append(state1['passengers'][passenger_name]['destination'])
                poss_destination.append(state1['passengers'][passenger_name]['destination'])
            possible_location_passengers.append(poss_location)
            possible_destination_passengers.append(poss_destination)

        for taxi_name in state1['taxis'].keys():
            fuel_taxis += [[i for i in range(state1['taxis'][taxi_name]['max_fuel'] + 1)]]
            capacity_taxis += [[i for i in range(state1['taxis'][taxi_name]['max_capacity'] + 1)]]

        all_possible_location_taxis = list(itertools.product(*possible_location_taxis))
        all_possible_location_passengers = list(itertools.product(*possible_location_passengers))
        all_possible_destination_passengers = list(itertools.product(*possible_destination_passengers))
        all_fuels = list(itertools.product(*fuel_taxis))
        all_capacity = list(itertools.product(*capacity_taxis))


        if number_taxis > 1:
            for taxis_locations in all_possible_location_taxis:
                taxi_loc = taxis_locations[0]
                for i in range(1, len(taxis_locations)):
                    if taxis_locations[i] == taxi_loc:
                        all_possible_location_taxis.remove(taxis_locations)

        for turn in turns_to_go:
            turn_to_go_i = []
            for location_taxis in all_possible_location_taxis:
                for location_passengers in all_possible_location_passengers:
                    for destination_passengers in all_possible_destination_passengers:
                        for taxis_fuel in all_fuels:
                            for taxis_capacity in all_capacity:
                                # Fill the state
                                taxi_counter = 0
                                passenger_counter = 0
                                state_i = dict()
                                state_i['optimal'] = state1['optimal']
                                state_i['map'] = state1['map']
                                state_i['taxis'] = {}
                                state_i['passengers'] = {}
                                # state_i['turns to go'] = self.initial_improved['turns to go']
                                for taxi_name in state1['taxis'].keys():
                                    state_i['taxis'][taxi_name] = {}
                                    state_i['taxis'][taxi_name]['names_passengers_aboard'] = []
                                    state_i['taxis'][taxi_name]["location"] = location_taxis[taxi_counter]
                                    state_i['taxis'][taxi_name]["fuel"] = taxis_fuel[taxi_counter]
                                    state_i['taxis'][taxi_name]["capacity"] = taxis_capacity[taxi_counter]

                                    taxi_counter += 1

                                for passenger_name in state1['passengers'].keys():
                                    state_i['passengers'][passenger_name] = {}
                                    state_i['passengers'][passenger_name]["location"] = location_passengers[passenger_counter]
                                    state_i['passengers'][passenger_name]["destination"] = destination_passengers[passenger_counter]
                                    state_i['passengers'][passenger_name]["possible_goals"] = state1['passengers'][passenger_name]["possible_goals"]
                                    state_i['passengers'][passenger_name]["prob_change_goal"] = state1['passengers'][passenger_name]["prob_change_goal"]


                                    if state_i['passengers'][passenger_name]['location'] in taxis_names:
                                        taxi_name_idx = taxis_names.index(state_i['passengers'][passenger_name]['location'])
                                        state_i['taxis'][taxis_names[taxi_name_idx]]['names_passengers_aboard'].append(passenger_name)

                                    passenger_counter += 1
                                state_i['turns to go'] = turn
                                flag_1 = False
                                flag_2 = False
                                flag_3 = False
                                for taxi_name in state_i['taxis'].keys():
                                    if len(state_i['taxis'][taxi_name]['names_passengers_aboard']) > \
                                            state1['taxis'][taxi_name]['max_capacity']:
                                        flag_1 = True
                                    if len(state_i['taxis'][taxi_name]['names_passengers_aboard']) == 0 and \
                                            state_i['taxis'][taxi_name]['capacity'] == 0:
                                        flag_2 = True
                                    if len(state_i['taxis'][taxi_name]['names_passengers_aboard']) != 0 and \
                                            state_i['taxis'][taxi_name]['capacity'] == state1['taxis'][taxi_name][
                                        'max_capacity']:
                                        flag_3 = True
                                    del state_i['taxis'][taxi_name]['names_passengers_aboard']

                                # if sum(reset) == len(reset):
                                #     reward -= 50

                                if not flag_1 and not flag_2 and not flag_3:
                                    turn_to_go_i.append(state_i)
            states.append(turn_to_go_i)
        self.possible_destination = self.possible_goals()
        self.order = list(states[0][0].keys())
        return states




    # locations of taxis, fuel of taxis, capacity of taxis, location of passengers, destinations of passengers


    def possible_goals(self):
        destination_goals_passengers = []
        for passenger_name in self.initial_improved['passengers'].keys():
            destination_goal_passenger = [self.initial_improved['passengers'][passenger_name]['possible_goals']]
            destination_goals_passengers += destination_goal_passenger
        return list(itertools.product(*destination_goals_passengers))
    def create_randoms_action(self):
        m = len(self.initial_improved['map'])
        n = len(self.initial_improved['map'][0])
        actions = []

        for taxi_name in self.initial['taxis'].keys():
            taxis_actions = []
            for i in range(m):
                for j in range(n):
                    taxis_actions.append(('move', taxi_name, (i, j)))
            for passenger_name in self.initial['passengers'].keys():
                taxis_actions.append(('pick up', taxi_name, passenger_name))
                taxis_actions.append(('drop off', taxi_name, passenger_name))
            taxis_actions.append(('refuel', taxi_name))
            taxis_actions.append(('wait', taxi_name))
            actions.append(taxis_actions)

        all_possible_actions = list(itertools.product(*actions))
        all_possible_actions.append('reset')
        all_possible_actions.append('terminate')
        return all_possible_actions

    def actions(self, state1, all_possible_actions):
        all_actions = []
        for possible_action in all_possible_actions:
            if self.is_action_legal(state1, possible_action):
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
            # check passenger not on taxi already
            if state['passengers'][passenger_name]['location'] == taxi_name:
                return False
            return True

        def _is_drop_action_legal(drop_action):
            taxi_name = drop_action[1]
            passenger_name = drop_action[2]
            # check same position
            if state['taxis'][taxi_name]['location'] == state['passengers'][passenger_name]['destination'] and \
                    state['passengers'][passenger_name]['location'] == taxi_name and \
                    state['taxis'][taxi_name]['capacity'] < self.initial_improved['taxis'][taxi_name]['max_capacity']:
                return True
            return False


        def _is_refuel_action_legal(refuel_action):
            """
            check if taxi in gas location
            """
            taxi_name = refuel_action[1]
            i, j = state['taxis'][taxi_name]['location']
            if self.initial['map'][i][j] == 'G':
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
            # logging.error(f"You had given {len(action)} atomic commands, while there are {len(state['taxis'])}"
            #               f" taxis in the problem!")
            return False
        for atomic_action in action:
            # illegal move action
            if atomic_action[0] == 'move':
                if not _is_move_action_legal(atomic_action):
                    # logging.error(f"Move action {atomic_action} is illegal!")
                    return False
            # illegal pick action
            elif atomic_action[0] == 'pick up':
                if not _is_pick_up_action_legal(atomic_action):
                    # logging.error(f"Pick action {atomic_action} is illegal!")
                    return False
            # illegal drop action
            elif atomic_action[0] == 'drop off':
                if not _is_drop_action_legal(atomic_action):
                    # logging.error(f"Drop action {atomic_action} is illegal!")
                    return False
            # illegal refuel action
            elif atomic_action[0] == 'refuel':
                if not _is_refuel_action_legal(atomic_action):
                    # logging.error(f"Refuel action {atomic_action} is illegal!")
                    return False
            elif atomic_action[0] != 'wait':
                return False
        # check mutex action
        if _is_action_mutex(action):
            # logging.error(f"Actions {action} are mutex!")
            return False
        # check taxis collision
        if len(state['taxis']) > 1:
            taxis_location_dict = dict([(t, state['taxis'][t]['location']) for t in state['taxis'].keys()])
            move_actions = [a for a in action if a[0] == 'move']
            for move_action in move_actions:
                taxis_location_dict[move_action[1]] = move_action[2]
            if len(set(taxis_location_dict.values())) != len(taxis_location_dict):
                # logging.error(f"Actions {action} cause collision!")
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
            return
        if action == "terminate":
            self.terminate_execution()
            return
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
            if state['taxis'][taxi_name]['capacity'] < self.initial_improved['taxis'][taxi_name]['max_capacity']:
                passenger_name = atomic_action[2]
                state['passengers'][passenger_name]['location'] = state['taxis'][taxi_name]['location']
                state['taxis'][taxi_name]['capacity'] += 1
            return
        elif atomic_action[0] == 'refuel':
            state['taxis'][taxi_name]['fuel'] = self.initial_improved['taxis'][taxi_name]['fuel']
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
        state["taxis"] = copy.deepcopy(self.initial["taxis"])
        state["passengers"] = copy.deepcopy(self.initial["passengers"])
        state["turns to go"] -= 1
        return

    def terminate_execution(self):
        """
        terminate the execution of the problem
        """
        # print(f"End of game, your score is {self.score}!")
        # print(f"-----------------------------------")
        # # raise EndOfGame
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


