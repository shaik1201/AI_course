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
        # self.lst_states, self.lst_actions = self.value_iteration_algorithm()
        # print(len(self.lst_states), len(self.lst_actions))
        # for i in range(len(self.lst_states)):
        #     print(self.lst_states[i])
        #     print(self.lst_actions[i])
        #     print()
        # print(self.lst_states)
        # print(self.lst_actions)
        # print()

        self.optimal_actions = self.value_iteration_shai()
        # x = {'optimal': True, 'map': [['P', 'P', 'P'], ['P', 'G', 'P'], ['P', 'P', 'P']], 'taxis': {'taxi 1': {'location': (0, 1), 'fuel': 3, 'capacity': 0}}, 'passengers': {'Dana': {'location': 'taxi 1', 'destination': (0, 0), 'possible_goals': ((0, 0), (2, 2)), 'prob_change_goal': 0.1}}}
        # print(self.optimal_actions[str(x)])
    # check distance: print(self.distances.check_distances(self.distances.shortest_path_distances, (0,0), (1,2)))

    # For a given state we return the best policy (=action)
    def act(self, state):
        temp = state.pop('turns to go', None)
        action = self.optimal_actions[str(state)]
        state['turns to go'] = temp
        return action




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
                    if sum_action >= max_sum:
                        max_sum = sum_action
                        max_action = action
                        lst_action[counter_state] = max_action

                reward_s = rewards[counter_state]
                values_t[counter_state] = reward_s + max_sum
                counter_state += 1
            values_t_1 = copy.deepcopy(values_t)
        return states, lst_action


    def value_iteration_algorithm(self):
        states, rewards, values_t = self.value_state_initialization()
        # values_t_1 = copy.deepcopy(values_t)
        values_t_1 = {}
        print('starting value iteration')
        all_possible_actions = self.create_randoms_action()
        t = self.initial["turns to go"]
        # lst_action = [None] * len(states)
        lst_action = []
        values_t_dict = {}

        ss = 0
        for i in range(2):
            print(time.time() - time1)
            print(f'round {i + 1}')
            counter_state = 0
            rewards_to_update = []

            for state in states:
                # if state['passengers']['Dana']['location'] != state['passengers']['Dana']['destination'] and \
                #         state['taxis']['taxi 1']['fuel'] > 0:
                #     print('hhh')
                actions = self.actions(state, all_possible_actions)
                # pickle.dump(actions, open('possible_action.pkl', 'wb'))
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
                    if action == 'terminate':
                        actions_states[action] = []
                # actions_states = { action1: [state1, state5, state66], action: [state155, state9, state57], 'terminate':[] }
                # probs_actions  = { action1: [0.5, 0.56, 1], action: [0, 0.98, 0.23] }
                # v_t_1_s_prime  = { action1: [455, 55, 1], action: [0, 56, 34] }
                # compute transition probs for each state and action

                # first update of values_t
                # given we are in state s:
                # value_t(s) = R(s) + max_actions(sigma_s_primes(T(s,a,s_prime) * value_t-1(s_prime)))
                # pickle.dump(actions_states, open('action_states.pkl','wb'))




                action_values = {}
                for action in actions_states.keys():
                    sum_action = 0
                    probs = []
                    for s_prime in actions_states[action]:
                        probs.append(self.transition_function(state, action, s_prime))
                    k = 0
                    for s_prime in actions_states[action]:
                        if ss == 0:
                            if action[0][0] == 'pick up':
                                values_t_1[str(s_prime)] = 50
                            elif action[0][0] == 'drop off':
                                values_t_1[str(s_prime)] = 100
                            elif action[0][0] == 'refuel':
                                values_t_1[str(s_prime)] = -10
                            elif action == 'reset':
                                values_t_1[str(s_prime)] = -50
                            elif action == 'terminate':
                                values_t_1[str(s_prime)] = 0
                            elif action[0][0] == 'wait':
                                values_t_1[str(s_prime)] = 0
                            elif action[0][0] == 'move':
                                values_t_1[str(s_prime)] = 0
                        sum_action += probs[k] * values_t_1[str(s_prime)]
                        k += 1
                    if action[0][0] == 'pick up':
                        action_values[action] = sum_action + 50
                    elif action[0][0] == 'drop off':
                        action_values[action] = sum_action + 100
                    elif action[0][0] == 'refuel':
                        action_values[action] = sum_action - 10
                    elif action == 'reset':
                        action_values[action] = sum_action - 50
                    elif action == 'terminate':
                        action_values[action] = sum_action
                    elif action[0][0] == 'wait':
                        action_values[action] = sum_action
                    elif action[0][0] == 'move':
                        action_values[action] = sum_action
                values_t_1[str(state)] = max(action_values.values())
                max_action = max(action_values, key=action_values.get)
                lst_action.append(max_action)
                # if max_action[0][0] == 'drop off':
                #     values_t_dict[str(state)] += 100
                # elif max_action[0][0] == 'refuel':
                #     values_t_dict[str(state)] -= 10
                # elif max_action[0][0] == 'pick up':
                #     values_t_dict[str(state)] += 70
                # elif max_action == 'reset':
                #     values_t_dict[str(state)] -= 50
            # values_t_1 = copy.deepcopy(values_t)
            ss += 1

        # for state in states:
        #     actions = self.actions(state, all_possible_actions)
        #     # pickle.dump(actions, open('possible_action.pkl', 'wb'))
        #     actions_states = dict()
        #     for action in actions:
        #         # for each action, compute all the states you can go to
        #         number_of_possible_states = len(self.possible_destination)
        #         copy_state = copy.deepcopy(state)
        #         self.result(copy_state, action)
        #         s_primes = []
        #         for i in range(number_of_possible_states):
        #             pass_counter = 0
        #             copy_state_prime = copy.deepcopy(copy_state)
        #             for passenger_name in (state['passengers'].keys()):
        #                 copy_state_prime['passengers'][passenger_name]['destination'] = self.possible_destination[i][pass_counter]
        #                 pass_counter += 1
        #                 s_primes.append(copy_state_prime)
        #         actions_states[action] = s_primes
        #     action_values = {}
        #     for action in actions_states.keys():
        #         sum_action = 0
        #         probs = []
        #         for s_prime in actions_states[action]:
        #             probs.append(self.transition_function(state, action, s_prime))
        #         k = 0
        #         for s_prime in actions_states[action]:
        #             sum_action += probs[k] * values_t_1[str(s_prime)]
        #             k += 1
        #         action_values[action] = sum_action
        #     values_t_dict[str(state)] = max(action_values.values())
        #     max_action = max(action_values, key=action_values.get)




            #     max_sum = 0
            #     for action in actions_states.keys():
            #         sum_action = 0
            #         counter_s_prime = 0
            #         for s_prime in actions_states[action]:
            #             pb = self.transition_function(state, action, s_prime)
            #             # idx_state_prime = states.index(actions_states[action][counter_s_prime])
            #             idx_state_prime = states.index(s_prime)
            #
            #             rewards_to_update.append(self.rewards_function(action, idx_state_prime))
            #
            #             v_t_1_s_prime = values_t_1[idx_state_prime]
            #             sum_action += (pb * v_t_1_s_prime)
            #             counter_s_prime += 1
            #         if sum_action >= max_sum:
            #             max_sum = sum_action
            #             max_action = action
            #             lst_action[counter_state] = max_action
            #     reward_s = rewards[counter_state]
            #     values_t[counter_state] = reward_s + max_sum
            #     counter_state += 1
            # values_t_1 = copy.deepcopy(values_t)
            # for i, j in rewards_to_update:
            #     rewards[i] = j
        return states, lst_action

    def value_iteration_shai(self):
        states, rewards, values_t = self.value_state_initialization()
        # x = {'optimal': True, 'map': [['P', 'P', 'P'], ['P', 'G', 'P'], ['P', 'P', 'P']], 'taxis': {'taxi 1': {'location': (0, 1), 'fuel': 0, 'capacity': 1, 'max_fuel': 10, 'max_capacity': 1}}, 'passengers': {'Dana': {'location': (0, 1), 'destination': (0, 0), 'possible_goals': ((0, 0), (2, 2)), 'prob_change_goal': 0.1}}}
        # print(x in states)
        values_t_past = self.update_initial_values(states)
        values_t_new = self.update_initial_values(states)
        rewards = self.initialize_rewards(states)
        all_possible_actions = self.create_randoms_action()

        for i in range(10):
            #############
            print(f"iteration: {i}")
            for state in states:
                # print(f"state idx: {states.index(state)}")
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

                # compute the reward for the best action
                # then update: v(s) = R(best_action) + sigma

                # reward_state = self.reward_shai(best_action)
                reward_state = self.reward_shai_new(state, i)

                # save the states_prime we can go to by applying best_action
                states_prime = actions_states[best_action]


                # compute transition probabilities to move to all states_prime by applying best_action
                # how it looks: {state_prime:prob, ...}
                transition_probs = self.compute_transition_probs(state, best_action, states_prime)

                # compute the sigma
                sigma = self.compute_sigma(states_prime, transition_probs, values_t_past)

                values_t_new[str(state)] = reward_state + sigma
                # values_t_new[str(state)] = rewards[(str(state), best_action)] + sigma

            # update values_t_past
            values_t_past = copy.deepcopy(values_t_new)

        # compute optimal action for each state
        optimal_actions = {}
        for state in states:
            optimal_action = self.compute_optimal_action(state, values_t_new)
            optimal_actions[str(state)] = optimal_action

        max_value = max(list(values_t_new.values()))
        print(max_value)
        return optimal_actions

    def initialize_rewards(self, states):
        rewards = {}
        all_possible_actions = self.create_randoms_action()
        for state in states:
            actions = self.actions(state, all_possible_actions)
            for action in actions:
                if not self.is_action_legal(state, action):
                    continue
                else:
                    rewards[(str(state), action)] = self.reward_shai(action)

        return rewards

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

    def update_initial_values(self, states):
        initial_values = {}
        for state in states:
            initial_values[str(state)] = 0
        return initial_values

    def compute_states_prime(self, state, action):
        # code for 1 passenger
        possible_destinations = []
        passengers = state['passengers'].keys()
        for passenger_name in passengers:
            possible_goals = state['passengers'][passenger_name]['possible_goals']
            for goal in possible_goals:
                possible_destinations.append(goal)

        assert len(possible_destinations) == 2, f"something went wrong, number of possible destinations is not 2 but: {len(possible_destinations)}"

        number_of_possible_states = len(possible_destinations)
        copy_state = copy.deepcopy(state)
        self.result(copy_state, action)
        s_primes = []
        for i in range(number_of_possible_states):
            copy_state_prime = copy.deepcopy(copy_state)
            for passenger_name in passengers:
                copy_state_prime['passengers'][passenger_name]['destination'] = possible_destinations[i]
                s_primes.append(copy_state_prime)

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

    def compute_best_action(self, state, actions_states, values_t_past):
        # first, for each action compute its value
        action_values = {}
        actions = actions_states.keys()
        for action in actions:
            s_primes = actions_states[action]
            action_value = self.compute_action_value(state, action, s_primes, values_t_past)
            action_values[action] = action_value

        # find the best action with the greatest action_value
        best_action = max(action_values, key=action_values.get)
        return best_action

    def compute_action_value(self, state, action, s_primes, values_t_past):
        probs = self.compute_transition_probs(state, action, s_primes)
        v = 0
        for s in s_primes:
            transition_prob = probs[str(s)]
            v_past = values_t_past[str(s)]
            v += transition_prob * v_past

        return v

    def compute_sigma(self, states_prime, transition_probs, values_t_past):
        v = 0
        for s in states_prime:
            transition_prob = transition_probs[str(s)]
            v_past = values_t_past[str(s)]
            v += transition_prob * v_past

        return v

    def compute_transition_probs(self, state, action, states_prime):
        # need to be compatability between states_prime and the probs returned.
        # returns dict - prob for each state_prime
        # code for 1 passenger
        probs = {}
        passengers = state['passengers'].keys()
        for passenger_name in passengers:
            prob_change_goal = state['passengers'][passenger_name]['prob_change_goal']
            for s_prime in states_prime:
                state_destination = state['passengers'][passenger_name]['destination']
                s_prime_destination = s_prime['passengers'][passenger_name]['destination']
                if s_prime_destination == state_destination:
                    probs[str(s_prime)] = 1 - prob_change_goal
                else:
                    probs[str(s_prime)] = prob_change_goal

        return probs



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
        if not state_prime:
            return 0
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
        self.n = len(self.initial_improved['map'])
        self.m = len(self.initial_improved['map'][0])

        taxis_names = [taxi_name for taxi_name in state1['taxis'].keys()]
        number_taxis = state1['number_taxis']
        number_passengers = state1['number_passengers']
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
                                ##### added by shai
                                # state_i['taxis'][taxi_name]["max_fuel"] = self.initial_improved['taxis'][taxi_name]['max_fuel']
                                # state_i['taxis'][taxi_name]["max_capacity"] = self.initial_improved['taxis'][taxi_name]['max_capacity']

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
                                #     if state_i['taxis'][taxi_name]['location'] == self.initial_improved['passengers'][passenger_name]['location'] and \
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
                x = {'optimal': True, 'map': [['P', 'P', 'P'], ['P', 'G', 'P'], ['P', 'P', 'P']], 'taxis': {'taxi 1': {'location': (0, 0), 'fuel': 0, 'capacity': 2}}, 'passengers': {'Dana': {'location': (0, 0), 'destination': (0, 0), 'possible_goals': ((0, 0), (2, 2)), 'prob_change_goal': 0.1}}}
                if state == x:
                    print()
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
        # state["turns to go"] -= 1
        return

    def reset_environment(self, state):
        """
        reset the state of the environment
        """
        state["taxis"] = copy.deepcopy(self.initial["taxis"])
        state["passengers"] = copy.deepcopy(self.initial["passengers"])
        # state["turns to go"] -= 1
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


