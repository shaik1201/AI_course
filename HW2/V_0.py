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
possible_destination_passengers = [state['passengers'][passenger_name]["possible_goals"] for passenger_name in
                                   state['passengers'].keys()]

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

# initial: { "optimal": True,
#           "map": [['P', 'P', 'P'],
#                   ['P', 'G', 'P'],
#                   ['P', 'P', 'P']],
#           "taxis": {'taxi 1': {"location": (0, 0), "fuel": 10, "capacity": 1, 'max}},
#           "passengers": {'Dana': {"location": (2, 2), "destination": (0, 0),
#                   "possible_goals": ((0, 0), (2, 2)), "prob_change_goal": 0.1}},
#           "turns to go": 100
#           "number_taxis" : 1
#           "number_passengers" : 1}


k = 0
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
                    state_i["turns to go"] = state["turns to go"]
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
                        state_i['passengers'][passenger_name]["possible_goals"] = state['passengers'][passenger_name][
                            "possible_goals"]
                        state_i['passengers'][passenger_name]["prob_change_goal"] = state['passengers'][passenger_name][
                            "prob_change_goal"]

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

                    v_0['state' + str(k)] = [state_i, reward]
                    v_1['state' + str(k)] = [state_i, reward]
                    reward1['state' + str(k)] = [state_i, reward]

                    k += 1
