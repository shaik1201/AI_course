import json
import copy
import itertools
import time

state = {
    "optimal": True,
    "map": [['P', 'P'],
            ['P', 'G']],
    "taxis": {'taxi 1': {"location": (0, 0), "fuel": 10, "capacity": 1, "max_fuel": 10, "max_capacity": 1},
              'taxi 2': {"location": (0, 1), "fuel": 7, "capacity": 3, "max_fuel": 7, "max_capacity": 3}},
    "passengers": {'Dana': {"location": (1, 0), "destination": (0, 0),
                            "possible_goals": ((0, 0), (1, 1)), "prob_change_goal": 0.1},
                   'Max': {"location": (2, 2), "destination": (3, 4),
                           "possible_goals": ((0, 1), (1, 0), (1, 1)), "prob_change_goal": 0.1}
                   },

    "turns to go": 100,
    "number_taxis": 2,
    "number_passengers": 2}

destination_goals_passengers = []
for passenger_name in state['passengers'].keys():
    destination_goal_passenger = [state['passengers'][passenger_name]['possible_goals']]
    destination_goals_passengers += destination_goal_passenger
x = list(itertools.product(*destination_goals_passengers))
print(x)

s_primes = []
for i in range(len(x)):
    pass_counter = 0
    copy_state = copy.deepcopy(state)
    for passenger_name in (state['passengers'].keys()):
        copy_state['passengers'][passenger_name]['destination'] = x[i][pass_counter]
        pass_counter += 1
    s_primes.append(copy_state)

for i in s_primes:
    print(i)

#  actions_states = {('move', 'taxi1, (0,0)) : [state1, state2]}

