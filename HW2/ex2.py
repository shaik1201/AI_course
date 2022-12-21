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
        # self.optimal_actions = self.value_iteration_algorithm()
        self.lst_states, self.lst_actions = self.value_iteration_algorithm()

    # check distance: print(self.distances.check_distances(self.distances.shortest_path_distances, (0,0), (1,2)))

    # For a given state we return the best policy (=action)
    def act(self, state):
        temp = state.pop('turns to go', None)
        idx_sol = self.lst_states.index(state)
        action_sol = self.lst_actions[idx_sol]
        state['turns to go'] = temp
        return action_sol




    def new_value_iteration_algorithm_old(self):
        states, rewards, values_t = self.value_state_initialization()
        values_t_1 = copy.deepcopy(values_t)
        print('starting value iteration')
        all_possible_actions = self.create_randoms_action()
        t = self.initial["turns to go"]
        lst_action = [None] * len(states)
        for i in range(10):
            print(time.time() - time1)
            print(f'round {i + 1}')
            counter_state = 0
            for state in states:
                actions = self.actions(state, all_possible_actions)
                actions_states = dict()
                for action in actions:
                    # for each action, compute all the states you can go to
                    number_of_possible_states = len(self.possible_destination)
                    copy_state = copy.deepcopy(state)
                    self.result(copy_state, action)
                    s_primes = []
                    for i in range(number_of_possible_states):
                        pass_counter = 0
                        copy_state_prime = copy.deepcopy(copy_state)
                        for passenger_name in (state['passengers'].keys()):
                            copy_state_prime['passengers'][passenger_name]['destination'] = self.possible_destination[i][pass_counter]
                            pass_counter += 1
                        s_primes.append(copy_state_prime)
                    actions_states[action] = s_primes
                # actions_states = { action1: [state1, state5, state66], action: [state155, state9, state57] }
                # probs_actions  = { action1: [0.5, 0.56, 1], action: [0, 0.98, 0.23] }
                # v_t_1_s_prime  = { action1: [455, 55, 1], action: [0, 56, 34] }
                # compute transition probs for each state and action
                max_sum = 0

                # if state == {'optimal': True, 'map': [['P', 'P', 'P'], ['P', 'G', 'P'], ['P', 'P', 'P']], 'taxis': {'taxi 1': {'location': (2, 2), 'fuel': 6, 'capacity': 0}}, 'passengers': {'Dana': {'location': 'taxi 1', 'destination': (0, 0), 'possible_goals': ((0, 0), (2, 2)), 'prob_change_goal': 0.1}}}:
                #     print(actions_states)
                for action in actions_states.keys():
                    sum_action = 0
                    counter_s_prime = 0
                    for s_prime in actions_states[action]:
                        pb = self.transition_function(state, action, s_prime)
                        idx_state = states.index(actions_states[action][counter_s_prime])
                        v_t_1_s_prime = values_t_1[idx_state]
                        sum_action += (pb * v_t_1_s_prime)
                        counter_s_prime += 1
                    if sum_action > max_sum:
                        max_sum = sum_action
                        max_action = action
                        lst_action[counter_state] = max_action

                reward_s = rewards[counter_state]
                values_t[counter_state] = reward_s + max_sum
                counter_state += 1
            values_t_1 = copy.deepcopy(values_t)
        print(values_t)
        print(max(values_t))
        return states, lst_action


    def value_iteration_algorithm(self):
        states, rewards, values_t = self.value_state_initialization()
        values_t_1 = copy.deepcopy(values_t)
        print('starting value iteration')
        all_possible_actions = self.create_randoms_action()
        t = self.initial["turns to go"]
        lst_action = [None] * len(states)
        for i in range(10):
            print(time.time() - time1)
            print(f'round {i + 1}')
            counter_state = 0
            rewards_to_update = []
            for state in states:
                actions = self.actions(state, all_possible_actions)
                actions_states = dict()
                for action in actions:
                    # for each action, compute all the states you can go to
                    number_of_possible_states = len(self.possible_destination)
                    copy_state = copy.deepcopy(state)
                    self.result(copy_state, action)
                    s_primes = []
                    for i in range(number_of_possible_states):
                        pass_counter = 0
                        copy_state_prime = copy.deepcopy(copy_state)
                        for passenger_name in (state['passengers'].keys()):
                            copy_state_prime['passengers'][passenger_name]['destination'] = self.possible_destination[i][pass_counter]
                            pass_counter += 1
                        s_primes.append(copy_state_prime)
                    actions_states[action] = s_primes
                # actions_states = { action1: [state1, state5, state66], action: [state155, state9, state57] }
                # probs_actions  = { action1: [0.5, 0.56, 1], action: [0, 0.98, 0.23] }
                # v_t_1_s_prime  = { action1: [455, 55, 1], action: [0, 56, 34] }
                # compute transition probs for each state and action

                if state == {'optimal': True, 'map': [['P', 'P', 'P'], ['P', 'G', 'P'], ['P', 'P', 'P']], 'taxis': {'taxi 1': {'location': (2, 2), 'fuel': 6, 'capacity': 1}}, 'passengers': {'Dana': {'location': (2, 2), 'destination': (0, 0), 'possible_goals': ((0, 0), (2, 2)), 'prob_change_goal': 0.1}}}:
                    print(actions_states)

                max_sum = 0
                for action in actions_states.keys():
                    sum_action = 0
                    counter_s_prime = 0
                    for s_prime in actions_states[action]:
                        pb = self.transition_function(state, action, s_prime)
                        idx_state_prime = states.index(actions_states[action][counter_s_prime])
                        rewards_to_update.append(self.rewards_function(action, idx_state_prime))
                        v_t_1_s_prime = values_t_1[idx_state_prime]
                        sum_action += (pb * v_t_1_s_prime)
                        counter_s_prime += 1
                    if sum_action >= max_sum:
                        max_sum = sum_action
                        max_action = action
                        lst_action[counter_state] = max_action
                reward_s = rewards[counter_state]
                values_t[counter_state] = reward_s + max_sum
                counter_state += 1
            values_t_1 = copy.deepcopy(values_t)
            for i, j in rewards_to_update:
                rewards[i] = j
        print(rewards)
        print(values_t)
        return states, lst_action


    def rewards_function(self, action, idx_state_prime):
        reward = 0
        if action[0][0] == 'drop off':
            reward = 100
        elif action[0][0] == 'refuel':
            reward = -10
        elif action == 'reset':
            reward = -50
        return idx_state_prime, reward


    # probability = [1, 0.56, 0.78,....] -> array of probability for each state
    def transition_function(self, state, action, state_prime):
        # turns_to_go_temp = state.pop('turns to go')
        pb = 1
        for passenger_name in state['passengers'].keys():
            if state['passengers'][passenger_name]['destination'] == state_prime['passengers'][passenger_name]['destination']:
                pb *= (1 - state['passengers'][passenger_name]['prob_change_goal'])
            else:
                pb *= state['passengers'][passenger_name]['prob_change_goal']
        return pb



    def value_state_initialization(self):
        state1 = self.initial_improved
        states = list()
        rewards = list()
        values = list()
        m = len(state1['map'])
        n = len(state1['map'][0])
        taxis_names = [taxi_name for taxi_name in state1['taxis'].keys()]
        number_taxis = state1['number_taxis']
        number_passengers = state1['number_passengers']
        fuel_taxis = []
        capacity_taxis = []
        possible_location_taxis = number_taxis * [
            [(i, j) for j in range(m) for i in range(n) if self.initial['map'][i][j] != 'I']]
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
                            # state_i['turns to go'] = self.initial['turns to go']
                            for taxi_name in state1['taxis'].keys():
                                state_i['taxis'][taxi_name] = {}
                                state_i['taxis'][taxi_name]['names_passengers_aboard'] = []
                                state_i['taxis'][taxi_name]["location"] = location_taxis[taxi_counter]
                                state_i['taxis'][taxi_name]["fuel"] = taxis_fuel[taxi_counter]
                                state_i['taxis'][taxi_name]["capacity"] = taxis_capacity[taxi_counter]

                                # the taxi refueled his fuel
                                # if state_i['taxis'][taxi_name]["fuel"] == state1['taxis'][taxi_name]["max_fuel"] and \
                                #         state1['map'][state_i['taxis'][taxi_name]["location"][0]][
                                #             state_i['taxis'][taxi_name]["location"][1]] == 'G':
                                #     reward -= 10

                                # if state_i['taxis'][taxi_name]["location"] == state1['taxis'][taxi_name]["location"] and \
                                #         state_i['taxis'][taxi_name]["fuel"] == state1['taxis'][taxi_name][
                                #     "max_fuel"] and \
                                #         state_i['taxis'][taxi_name]["capacity"] == state1['taxis'][taxi_name][
                                #     "max_capacity"]:
                                #     reset.append(True)

                                # else:
                                #     reset.append(False)

                                taxi_counter += 1

                            for passenger_name in state1['passengers'].keys():
                                state_i['passengers'][passenger_name] = {}
                                state_i['passengers'][passenger_name]["location"] = location_passengers[passenger_counter]
                                state_i['passengers'][passenger_name]["destination"] = destination_passengers[passenger_counter]
                                state_i['passengers'][passenger_name]["possible_goals"] = state1['passengers'][passenger_name]["possible_goals"]
                                state_i['passengers'][passenger_name]["prob_change_goal"] = state1['passengers'][passenger_name]["prob_change_goal"]

                                # if state_i['passengers'][passenger_name]["location"] == \
                                #         state_i['passengers'][passenger_name]["destination"] and \
                                #         state_i['passengers'][passenger_name]["location"] in location_taxis:
                                #     reward += 100

                                # if state_i['passengers'][passenger_name]["location"] == \
                                #         state1['passengers'][passenger_name]["location"] and \
                                #         state_i['passengers'][passenger_name]["destination"] == \
                                #         state1['passengers'][passenger_name]["destination"]:
                                #     reset.append(True)
                                #
                                # else:
                                #     reset.append(False)

                                if state_i['passengers'][passenger_name]['location'] in taxis_names:
                                    taxi_name_idx = taxis_names.index(state_i['passengers'][passenger_name]['location'])
                                    state_i['taxis'][taxis_names[taxi_name_idx]]['names_passengers_aboard'].append(passenger_name)

                                # for taxi_name in state_i['taxis'].keys():
                                #     if state_i['taxis'][taxi_name]['location'] == self.initial['passengers'][passenger_name]['location'] and \
                                #        state_i['passengers'][passenger_name]['location'] == taxi_name:
                                #         reward -= 50
                                #

                                passenger_counter += 1

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
                                states.append(state_i)
                                rewards.append(0)
                                values.append(0)
        self.possible_destination = self.possible_goals()
        return states, rewards, values




    # locations of taxis, fuel of taxis, capacity of taxis, location of passengers, destinations of passengers
    def value_state_initialization_old(self):
        state1 = self.initial_improved
        states = list()
        rewards = list()
        values = list()
        m = len(state1['map'])
        n = len(state1['map'][0])
        taxis_names = [taxi_name for taxi_name in state1['taxis'].keys()]
        number_taxis = state1['number_taxis']
        number_passengers = state1['number_passengers']
        fuel_taxis = []
        capacity_taxis = []
        possible_location_taxis = number_taxis * [[(i, j) for j in range(m) for i in range(n) if self.initial['map'][i][j] != 'I']]
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
                            state_i['optimal'] = state1['optimal']
                            state_i['map'] = state1['map']
                            state_i['taxis'] = {}
                            state_i['passengers'] = {}
                            # state_i['turns to go'] = self.initial['turns to go']
                            for taxi_name in state1['taxis'].keys():
                                state_i['taxis'][taxi_name] = {}
                                state_i['taxis'][taxi_name]['names_passengers_aboard'] = []
                                state_i['taxis'][taxi_name]["location"] = location_taxis[taxi_counter]
                                state_i['taxis'][taxi_name]["fuel"] = taxis_fuel[taxi_counter]
                                state_i['taxis'][taxi_name]["capacity"] = taxis_capacity[taxi_counter]


                                # the taxi refueled his fuel
                                if state_i['taxis'][taxi_name]["fuel"] == state1['taxis'][taxi_name]["max_fuel"] and \
                                   state1['map'][state_i['taxis'][taxi_name]["location"][0]][state_i['taxis'][taxi_name]["location"][1]] == 'G':
                                        reward -= 10

                                if state_i['taxis'][taxi_name]["location"] == state1['taxis'][taxi_name]["location"] and \
                                   state_i['taxis'][taxi_name]["fuel"] == state1['taxis'][taxi_name]["max_fuel"] and \
                                   state_i['taxis'][taxi_name]["capacity"] == state1['taxis'][taxi_name]["max_capacity"]:
                                        reset.append(True)

                                else:
                                    reset.append(False)

                                taxi_counter += 1

                            for passenger_name in state1['passengers'].keys():
                                state_i['passengers'][passenger_name] = {}
                                state_i['passengers'][passenger_name]["location"] = location_passengers[passenger_counter]
                                state_i['passengers'][passenger_name]["destination"] = destination_passengers[passenger_counter]
                                state_i['passengers'][passenger_name]["possible_goals"] = state1['passengers'][passenger_name]["possible_goals"]
                                state_i['passengers'][passenger_name]["prob_change_goal"] = state1['passengers'][passenger_name]["prob_change_goal"]

                                if state_i['passengers'][passenger_name]["location"] == state_i['passengers'][passenger_name]["destination"] and \
                                   state_i['passengers'][passenger_name]["location"] in location_taxis:
                                        reward += 100

                                if state_i['passengers'][passenger_name]["location"] == state1['passengers'][passenger_name]["location"] and \
                                   state_i['passengers'][passenger_name]["destination"] == state1['passengers'][passenger_name]["destination"]:
                                        reset.append(True)

                                else:
                                    reset.append(False)

                                if state_i['passengers'][passenger_name]['location'] in taxis_names:
                                    taxi_name_idx = taxis_names.index(state_i['passengers'][passenger_name]['location'])
                                    state_i['taxis'][taxis_names[taxi_name_idx]]['names_passengers_aboard'].append(passenger_name)

                                # for taxi_name in state_i['taxis'].keys():
                                #     if state_i['taxis'][taxi_name]['location'] == self.initial['passengers'][passenger_name]['location'] and \
                                #        state_i['passengers'][passenger_name]['location'] == taxi_name:
                                #         reward -= 50
                                #

                                passenger_counter += 1

                            flag_1 = False
                            flag_2 = False
                            flag_3 = False
                            for taxi_name in state_i['taxis'].keys():
                                if len(state_i['taxis'][taxi_name]['names_passengers_aboard']) > state1['taxis'][taxi_name]['max_capacity']:
                                    flag_1 = True
                                if len(state_i['taxis'][taxi_name]['names_passengers_aboard']) == 0 and state_i['taxis'][taxi_name]['capacity'] == 0:
                                    flag_2 = True
                                if len(state_i['taxis'][taxi_name]['names_passengers_aboard']) != 0 and state_i['taxis'][taxi_name]['capacity'] == state1['taxis'][taxi_name]['max_capacity']:
                                    flag_3 = True
                                del state_i['taxis'][taxi_name]['names_passengers_aboard']

                            if sum(reset) == len(reset):
                                reward -= 50

                            if not flag_1 and not flag_2 and not flag_3:
                                states.append(state_i)
                                rewards.append(reward)
                                values.append(reward)
        self.possible_destination = self.possible_goals()
        return states, rewards, values

    def possible_goals(self):
        destination_goals_passengers = []
        for passenger_name in self.initial['passengers'].keys():
            destination_goal_passenger = [self.initial['passengers'][passenger_name]['possible_goals']]
            destination_goals_passengers += destination_goal_passenger
        return list(itertools.product(*destination_goals_passengers))
    def create_randoms_action(self):
        m = len(self.initial['map'])
        n = len(self.initial['map'][0])
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

    def is_action_legal(self, state1, action):
        """
        check if the action is legal
        """
        def _is_move_action_legal(move_action):
            taxi_name = move_action[1]
            if taxi_name not in state1['taxis'].keys():
                return False
            if state1['taxis'][taxi_name]['fuel'] == 0:
                return False
            l1 = state1['taxis'][taxi_name]['location']
            l2 = move_action[2]
            return l2 in list(self.distances.graph.neighbors(l1))

        def _is_pick_up_action_legal(pick_up_action):
            taxi_name = pick_up_action[1]
            passenger_name = pick_up_action[2]
            # check same position
            if state1['taxis'][taxi_name]['location'] != state1['passengers'][passenger_name]['location']:
                return False
            # check taxi capacity
            if state1['taxis'][taxi_name]['capacity'] <= 0:
                return False
            # check passenger is not in his destination
            if state1['passengers'][passenger_name]['destination'] == state1['passengers'][passenger_name]['location']:
                return False
            return True

        def _is_drop_action_legal(drop_action):
            taxi_name = drop_action[1]
            passenger_name = drop_action[2]
            # check same position
            if state1['taxis'][taxi_name]['location'] == state1['passengers'][passenger_name]['destination'] and\
               state1['passengers'][passenger_name]['location'] == taxi_name:
                return True
            return False
            # if state1['taxis'][taxi_name]['location'] != state1['passengers'][passenger_name]['destination']:
            #     return False
            # return True

        def _is_refuel_action_legal(refuel_action):
            """
            check if taxi in gas location
            """
            taxi_name = refuel_action[1]
            i, j = state1['taxis'][taxi_name]['location']
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

        if len(action) != len(state1["taxis"].keys()):
            # logging.error(f"You had given {len(action)} atomic commands, while there are {len(state['taxis'])}"
            #               f" taxis in the problem!")
            return False

        for atomic_action in action:
            # illegal move action
            if atomic_action[0] == 'move' and not _is_move_action_legal(atomic_action):
                # logging.error(f"Move action {atomic_action} is illegal!")
                return False
            # illegal pick action
            elif atomic_action[0] == 'pick up' and not _is_pick_up_action_legal(atomic_action):
                # logging.error(f"Pick action {atomic_action} is illegal!")
                return False
            # illegal drop action
            elif atomic_action[0] == 'drop off' and not _is_drop_action_legal(atomic_action):
                # logging.error(f"Drop action {atomic_action} is illegal!")
                return False
            # illegal refuel action
            elif atomic_action[0] == 'refuel' and not _is_refuel_action_legal(atomic_action):
                # logging.error(f"Refuel action {atomic_action} is illegal!")
                return False
            elif atomic_action[0] == 'wait':
                return True
        # check mutex action
        if _is_action_mutex(action):
            # logging.error(f"Actions {action} are mutex!")
            return False
        return True

    def result(self, state1, action):
        """"
        update the state according to the action
        """
        self.apply(state1, action)
        if action != "reset":
            self.environment_step(state1)

    def apply(self, state1, action):
        """
        apply the action to the state
        """
        if action == "reset":
            self.reset_environment(state1)
            return
        if action == "terminate":
            self.terminate_execution(state1)
            return
        for atomic_action in action:
            self.apply_atomic_action(state1, atomic_action)
    def apply_atomic_action(self, state1, atomic_action):
        """
        apply an atomic action to the state
        """
        taxi_name = atomic_action[1]
        if atomic_action[0] == 'move':
            state1['taxis'][taxi_name]['location'] = atomic_action[2]
            state1['taxis'][taxi_name]['fuel'] -= 1
            return
        elif atomic_action[0] == 'pick up':
            passenger_name = atomic_action[2]
            state1['taxis'][taxi_name]['capacity'] -= 1
            state1['passengers'][passenger_name]['location'] = taxi_name
            return
        elif atomic_action[0] == 'drop off':
            passenger_name = atomic_action[2]
            state1['passengers'][passenger_name]['location'] = state1['taxis'][taxi_name]['location']
            #####################
            if state1['taxis'][taxi_name]['capacity'] < self.initial_improved['taxis'][taxi_name]['max_capacity']:
                state1['taxis'][taxi_name]['capacity'] += 1

            #####################

            return
        elif atomic_action[0] == 'refuel':
            state1['taxis'][taxi_name]['fuel'] = self.initial['taxis'][taxi_name]['fuel']
            return
        elif atomic_action[0] == 'wait':
            return
        else:
            raise NotImplemented

    def environment_step(self, state1):
        """
        update the state of environment randomly
        """
        for p in state1['passengers']:
            passenger_stats = state1['passengers'][p]
            if random.random() < passenger_stats['prob_change_goal']:
                # change destination
                passenger_stats['destination'] = random.choice(passenger_stats['possible_goals'])
        # state1["turns to go"] -= 1
        return

    def reset_environment(self, state1):
        """
        reset the state of the environment
        """
        state1["taxis"] = self.initial["taxis"]
        state1["passengers"] = self.initial["passengers"]
        # state1["turns to go"] -= 1
        return

    def terminate_execution(self, state1):
        """
        terminate the execution of the problem
        """
        # print(f"End of game")
        # print(f"-----------------------------------")
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


